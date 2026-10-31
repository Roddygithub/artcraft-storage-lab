//! The `postMessage` bridge to a same-origin parent page (`?host=parent`), for pages that embed
//! DesignCraft in an `<iframe>` and keep its files (a file server's web UI, a Nextcloud app). The
//! same messages as WordCraft's, GridCraft's, PdfCraft's and CADCraft's bridges; each is a plain
//! object with a `type`:
//!
//! - `designcraft:ready` (to the parent): `{ version }`, sent once the app is running and
//!   listening; send a file now.
//! - `designcraft:open` (from the parent): `{ name, bytes }`, bytes an `ArrayBuffer` or
//!   `Uint8Array`. It opens like a document dropped on the window.
//! - `designcraft:save` (to the parent): `{ name, saveAs, bytes }` (a transferred `ArrayBuffer`) for
//!   every file DesignCraft would otherwise download. `saveAs` is false when `name` is the file the
//!   parent sent (Save), true for any other name (Save As, exports).
//! - `designcraft:failed` (to the parent): `{ error }` when the app couldn't start.
//!
//! Only the parent window on the page's own origin is heard or answered.

use std::cell::RefCell;
use std::rc::Rc;

use designcraft_ui_egui::Services;
use wasm_bindgen::JsCast as _;
use wasm_bindgen::JsValue;
use wasm_bindgen::closure::Closure;

/// Files the parent sent, read by the shell on the UI thread (`WebShell::logic`).
pub type HostFiles = Rc<RefCell<Vec<(String, Vec<u8>)>>>;

#[derive(Clone)]
pub struct Bridge {
    window: web_sys::Window,
    parent: web_sys::Window,
    origin: String,
    /// The name the parent sent; a save under it is a Save, anything else a Save As.
    opened: Rc<RefCell<Option<String>>>,
}

impl Bridge {
    /// `None` when the page isn't framed, or when the parent is on another origin: messages only
    /// go to this origin, so the browser would drop every save without an error while the
    /// document showed as saved.
    pub fn new() -> Option<Self> {
        let window = web_sys::window()?;
        let parent = window.parent().ok().flatten()?;
        if js_sys::Object::is(&parent, &window) {
            return None;
        }
        let origin = window.location().origin().ok()?;
        if origin == "null" {
            return None;
        }
        if parent.location().origin().ok()? != origin {
            return None;
        }
        Some(Self { window, parent, origin, opened: Rc::default() })
    }

    /// Hand saved and exported files to the parent instead of downloading them, and hear the
    /// files it sends (queued in `files`; the shell opens them on the UI thread).
    pub fn connect(&self, services: &mut Services, files: HostFiles, ctx: egui::Context) {
        self.listen(files, ctx);
        let bridge = self.clone();
        services.write = Some(Box::new(move |name: &str, bytes: &[u8]| bridge.post_save(name, bytes)));
        let bridge = self.clone();
        services.download = Some(Box::new(move |name: &str, bytes: &[u8]| {
            if let Err(e) = bridge.post_save(name, bytes) {
                log::error!("couldn't hand {name} to the host page: {e}");
            }
        }));
    }

    pub fn post_ready(&self) {
        self.send(&[("type", "designcraft:ready".into()), ("version", env!("CARGO_PKG_VERSION").into())]);
    }

    /// The app couldn't start (no WebGPU or WebGL2, for example): let the parent say so.
    pub fn post_failed(&self, error: &str) {
        self.send(&[("type", "designcraft:failed".into()), ("error", error.into())]);
    }

    fn post_save(&self, path: &str, bytes: &[u8]) -> Result<(), String> {
        let name = std::path::Path::new(path).file_name().map(|n| n.to_string_lossy().to_string()).unwrap_or_else(|| path.to_string());
        let save_as = self.opened.borrow().as_deref() != Some(name.as_str());
        let buffer = js_sys::Uint8Array::from(bytes).buffer();
        let message = message(&[
            ("type", "designcraft:save".into()),
            ("name", name.as_str().into()),
            ("saveAs", save_as.into()),
            ("bytes", buffer.clone().into()),
        ])
        .ok_or_else(|| "couldn't build the message".to_string())?;
        self.parent
            .post_message_with_transfer(&message, &self.origin, &js_sys::Array::of1(&buffer))
            .map_err(|e| e.as_string().unwrap_or_else(|| format!("{e:?}")))
    }

    /// Hear `designcraft:open` from the parent and queue the file for the shell.
    fn listen(&self, files: HostFiles, ctx: egui::Context) {
        let parent = self.parent.clone();
        let origin = self.origin.clone();
        let opened = self.opened.clone();
        let on_message = Closure::<dyn FnMut(web_sys::MessageEvent)>::new(move |event: web_sys::MessageEvent| {
            if event.origin() != origin || !event.source().is_some_and(|s| js_sys::Object::is(&s, &parent)) {
                return;
            }
            let data = event.data();
            if string(&data, "type").as_deref() != Some("designcraft:open") {
                return;
            }
            let name = string(&data, "name").filter(|n| !n.trim().is_empty()).unwrap_or_else(|| "Document.designcraft".to_string());
            let Some(bytes) = bytes(&data) else { return };
            *opened.borrow_mut() = Some(name.clone());
            files.borrow_mut().push((name, bytes));
            ctx.request_repaint();
        });
        if self.window.add_event_listener_with_callback("message", on_message.as_ref().unchecked_ref()).is_ok() {
            on_message.forget();
        }
    }

    fn send(&self, fields: &[(&str, JsValue)]) -> bool {
        message(fields).is_some_and(|m| self.parent.post_message(&m, &self.origin).is_ok())
    }
}

fn message(fields: &[(&str, JsValue)]) -> Option<js_sys::Object> {
    let m = js_sys::Object::new();
    for (key, value) in fields {
        js_sys::Reflect::set(&m, &JsValue::from_str(key), value).ok()?;
    }
    Some(m)
}

fn string(data: &JsValue, key: &str) -> Option<String> {
    js_sys::Reflect::get(data, &JsValue::from_str(key)).ok()?.as_string()
}

/// `bytes` as an `ArrayBuffer` or `Uint8Array`.
fn bytes(data: &JsValue) -> Option<Vec<u8>> {
    let bytes = js_sys::Reflect::get(data, &JsValue::from_str("bytes")).ok()?;
    if let Some(array) = bytes.dyn_ref::<js_sys::Uint8Array>() {
        Some(array.to_vec())
    } else if bytes.is_instance_of::<js_sys::ArrayBuffer>() {
        Some(js_sys::Uint8Array::new(&bytes).to_vec())
    } else {
        None
    }
}
