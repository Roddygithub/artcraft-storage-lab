//! The `postMessage` bridge to a same-origin parent page (`?host=parent`), for pages that embed
//! PhotoCraft in an `<iframe>` and keep its files (a file server's web UI, a Nextcloud app). The
//! same messages as WordCraft's, GridCraft's, PdfCraft's and CADCraft's bridges; each is a plain
//! object with a `type`:
//!
//! - `photocraft:ready` (to the parent): `{ version }`, sent once the app is running and
//!   listening; send a file now.
//! - `photocraft:open` (from the parent): `{ name, bytes }`, bytes an `ArrayBuffer` or
//!   `Uint8Array`. It opens like a image dropped on the window.
//! - `photocraft:save` (to the parent): `{ name, saveAs, bytes }` (a transferred `ArrayBuffer`) for
//!   every file PhotoCraft would otherwise download. `saveAs` is false when `name` is the file the
//!   parent sent (Save), true for any other name (Save As, exports).
//! - `photocraft:dirty` (to the parent): `{ dirty }` whenever unsaved changes appear or go away.
//! - `photocraft:failed` (to the parent): `{ error }` when the app couldn't start.
//!
//! Only the parent window on the page's own origin is heard or answered.

use std::cell::RefCell;
use std::rc::Rc;

use photocraft_ui_egui::Services;

/// Files to open, shared with the shell: `(name, bytes)`.
pub type Inbox = std::sync::Arc<std::sync::Mutex<Vec<(String, Vec<u8>)>>>;
use wasm_bindgen::JsCast as _;
use wasm_bindgen::JsValue;
use wasm_bindgen::closure::Closure;

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
    /// image showed as saved.
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
    /// files it sends (pushed into the app's own open inbox).
    pub fn connect(&self, services: &mut Services, inbox: Inbox, ctx: egui::Context) {
        self.listen(inbox, ctx);
        let bridge = self.clone();
        services.write = Some(Box::new(move |name: &str, bytes: &[u8]| bridge.post_save(name, bytes)));
        // The parent stores the file synchronously from the app's point of view; a download that
        // might be cancelled is not involved.
        services.write_unconfirmed = false;
    }

    pub fn post_dirty(&self, dirty: bool) {
        self.send(&[("type", "photocraft:dirty".into()), ("dirty", dirty.into())]);
    }

    pub fn post_ready(&self) {
        self.send(&[("type", "photocraft:ready".into()), ("version", env!("CARGO_PKG_VERSION").into())]);
    }

    /// The app couldn't start (no WebGPU or WebGL2, for example): let the parent say so.
    pub fn post_failed(&self, error: &str) {
        self.send(&[("type", "photocraft:failed".into()), ("error", error.into())]);
    }

    fn post_save(&self, path: &str, bytes: &[u8]) -> Result<(), String> {
        let name = std::path::Path::new(path).file_name().map(|n| n.to_string_lossy().to_string()).unwrap_or_else(|| path.to_string());
        let save_as = self.opened.borrow().as_deref() != Some(name.as_str());
        let buffer = js_sys::Uint8Array::from(bytes).buffer();
        let message = message(&[
            ("type", "photocraft:save".into()),
            ("name", name.as_str().into()),
            ("saveAs", save_as.into()),
            ("bytes", buffer.clone().into()),
        ])
        .ok_or_else(|| "couldn't build the message".to_string())?;
        self.parent
            .post_message_with_transfer(&message, &self.origin, &js_sys::Array::of1(&buffer))
            .map_err(|e| e.as_string().unwrap_or_else(|| format!("{e:?}")))
    }

    /// Hear `photocraft:open` from the parent and queue the file like a dropped one.
    fn listen(&self, inbox: Inbox, ctx: egui::Context) {
        let parent = self.parent.clone();
        let origin = self.origin.clone();
        let opened = self.opened.clone();
        let on_message = Closure::<dyn FnMut(web_sys::MessageEvent)>::new(move |event: web_sys::MessageEvent| {
            if event.origin() != origin || !event.source().is_some_and(|s| js_sys::Object::is(&s, &parent)) {
                return;
            }
            let data = event.data();
            if string(&data, "type").as_deref() != Some("photocraft:open") {
                return;
            }
            let name = string(&data, "name").filter(|n| !n.trim().is_empty()).unwrap_or_else(|| "Image.png".to_string());
            let Some(bytes) = bytes(&data) else { return };
            *opened.borrow_mut() = Some(name.clone());
            inbox.lock().unwrap_or_else(|e| e.into_inner()).push((name, bytes));
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
