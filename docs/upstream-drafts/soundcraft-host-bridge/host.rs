//! The `postMessage` bridge to a same-origin parent page (`?host=parent`), for pages that embed
//! SoundCraft in an `<iframe>` and keep its files. The same messages as WordCraft's, GridCraft's,
//! PdfCraft's and CADCraft's bridges; each is a plain object with a `type`:
//!
//! - `soundcraft:ready` (to the parent): `{ version }`, sent once the app is running.
//! - `soundcraft:open` (from the parent): `{ name, bytes }`; a session opens, audio and MIDI
//!   import, exactly as a dropped file would.
//! - `soundcraft:save` (to the parent): `{ name, saveAs, bytes }` (a transferred `ArrayBuffer`)
//!   for every file SoundCraft would otherwise download (the engine's delivery hook). `saveAs` is
//!   false when `name` is the file the parent sent, true otherwise (Save As, exports, bounces).
//! - `soundcraft:failed` (to the parent): `{ error }` when the app couldn't start.
//!
//! Only the parent window on the page's own origin is heard or answered. The engine's delivery
//! hook is a plain `fn`, so the bridge lives in a thread-local and `deliver` forwards to it.

use std::cell::RefCell;
use std::rc::Rc;

use wasm_bindgen::JsCast as _;
use wasm_bindgen::JsValue;
use wasm_bindgen::closure::Closure;

/// Files the parent sent, read by the shell on the UI thread (`WebShell::logic`).
pub type HostFiles = Rc<RefCell<Vec<(String, Vec<u8>)>>>;

thread_local! {
    static BRIDGE: RefCell<Option<Bridge>> = const { RefCell::new(None) };
}

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
    /// go to this origin, so the browser would drop every save without an error.
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

    /// Install this bridge as the engine's file delivery and hear the files the parent sends
    /// (queued in `files`; the shell opens them on the UI thread).
    pub fn connect(&self, files: HostFiles, ctx: egui::Context) {
        self.listen(files, ctx);
        BRIDGE.with(|b| *b.borrow_mut() = Some(self.clone()));
    }

    pub fn post_ready(&self) {
        self.send(&[("type", "soundcraft:ready".into()), ("version", env!("CARGO_PKG_VERSION").into())]);
    }

    /// The app couldn't start (no WebGPU or WebGL2, for example): let the parent say so.
    pub fn post_failed(&self, error: &str) {
        self.send(&[("type", "soundcraft:failed".into()), ("error", error.into())]);
    }

    fn post_save(&self, path: &str, bytes: &[u8]) -> Result<(), String> {
        let name = std::path::Path::new(path).file_name().map(|n| n.to_string_lossy().to_string()).unwrap_or_else(|| path.to_string());
        let save_as = self.opened.borrow().as_deref() != Some(name.as_str());
        let buffer = js_sys::Uint8Array::from(bytes).buffer();
        let message = message(&[
            ("type", "soundcraft:save".into()),
            ("name", name.as_str().into()),
            ("saveAs", save_as.into()),
            ("bytes", buffer.clone().into()),
        ])
        .ok_or_else(|| "couldn't build the message".to_string())?;
        self.parent
            .post_message_with_transfer(&message, &self.origin, &js_sys::Array::of1(&buffer))
            .map_err(|e| e.as_string().unwrap_or_else(|| format!("{e:?}")))
    }

    /// Hear `soundcraft:open` from the parent and queue the file for the shell.
    fn listen(&self, files: HostFiles, ctx: egui::Context) {
        let parent = self.parent.clone();
        let origin = self.origin.clone();
        let opened = self.opened.clone();
        let on_message = Closure::<dyn FnMut(web_sys::MessageEvent)>::new(move |event: web_sys::MessageEvent| {
            if event.origin() != origin || !event.source().is_some_and(|s| js_sys::Object::is(&s, &parent)) {
                return;
            }
            let data = event.data();
            if string(&data, "type").as_deref() != Some("soundcraft:open") {
                return;
            }
            let name = string(&data, "name").filter(|n| !n.trim().is_empty()).unwrap_or_else(|| "Session.soundcraft".to_string());
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

/// The engine's delivery hook in host mode: the parent page stores the file. `Err` when there is
/// no bridge (the shell then installs the download hook instead).
pub fn deliver(name: &str, bytes: &[u8]) -> Result<(), String> {
    BRIDGE.with(|b| match b.borrow().as_ref() {
        Some(bridge) => bridge.post_save(name, bytes),
        None => Err("no host page".to_string()),
    })
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
