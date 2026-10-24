//! Same-origin iframe transport for the common Craft host protocol.
use js_sys::{Array, Object, Reflect, Uint8Array};
use wasm_bindgen::{JsCast, JsValue, closure::Closure};
use web_sys::{EventTarget, MessageEvent, Window};

use crate::host_protocol::{SaveTicket, accepts_parent_message};

/// Messages received from the parent host.
pub enum HostMessage {
    Open { name: String, bytes: Vec<u8> },
    SaveResult { ticket: SaveTicket, ok: bool, error: Option<String> },
}

/// Same-origin parent window transport for one named Craft app.
#[derive(Clone)]
pub struct HostTransport {
    parent: Window,
    origin: String,
    app: String,
}

impl HostTransport {
    /// Return a transport only when this page is framed by a same-origin parent.
    pub fn current(app: &str) -> Result<Option<Self>, JsValue> {
        let Some(window) = web_sys::window() else {
            return Ok(None);
        };
        let Some(parent) = window.parent()? else { return Ok(None) };
        if Object::is(parent.as_ref(), window.as_ref()) {
            return Ok(None);
        }
        let origin = window.location().origin()?;
        if origin.is_empty() || app.trim().is_empty() || parent.location().origin()? != origin {
            return Ok(None);
        }
        Ok(Some(Self { parent, origin, app: app.to_owned() }))
    }

    /// Listen for parent messages. Exact origin and `event.source` are both checked.
    pub fn listen(&self, mut callback: impl FnMut(HostMessage) + 'static) -> Result<HostListener, JsValue> {
        let window = web_sys::window().ok_or_else(|| JsValue::from_str("no browser window"))?;
        let parent: JsValue = self.parent.clone().into();
        let origin = self.origin.clone();
        let app = self.app.clone();
        let handler = Closure::<dyn FnMut(MessageEvent)>::new(move |event: MessageEvent| {
            let source_is_parent = event.source().is_some_and(|source| Object::is(source.as_ref(), &parent));
            if !accepts_parent_message(&event.origin(), &origin, source_is_parent) {
                return;
            }
            let data = event.data();
            let Ok(kind) = string_field(&data, "type") else {
                return;
            };
            if kind == format!("{app}:open") {
                let Ok(name) = string_field(&data, "name") else {
                    return;
                };
                let Ok(value) = Reflect::get(&data, &JsValue::from_str("bytes")) else {
                    return;
                };
                let Some(bytes) = read_bytes(&value) else { return };
                callback(HostMessage::Open { name, bytes });
            } else if kind == format!("{app}:saveResult") {
                let Ok(ticket_value) = string_field(&data, "ticket") else {
                    return;
                };
                let Some(ticket) = SaveTicket::new(ticket_value) else {
                    return;
                };
                let Ok(ok) = Reflect::get(&data, &JsValue::from_str("ok")) else {
                    return;
                };
                let error = string_field(&data, "error").ok();
                callback(HostMessage::SaveResult { ticket, ok: ok.as_bool().unwrap_or(false), error });
            }
        });
        window.add_event_listener_with_callback("message", handler.as_ref().unchecked_ref())?;
        Ok(HostListener { target: window.unchecked_into(), handler: Some(handler) })
    }

    /// Notify the parent that the editor bridge is ready.
    pub fn post_ready(&self, version: &str) -> Result<(), JsValue> {
        self.post(&format!("{}:ready", self.app), &[(&"version", &JsValue::from_str(version))])
    }

    /// Report editor dirty state.
    pub fn post_dirty(&self, dirty: bool) -> Result<(), JsValue> {
        self.post(&format!("{}:dirty", self.app), &[(&"dirty", &JsValue::from_bool(dirty))])
    }

    /// Send a failure that is not tied to a save ticket.
    pub fn post_failed(&self, error: &str) -> Result<(), JsValue> {
        self.post(&format!("{}:failed", self.app), &[(&"error", &JsValue::from_str(error))])
    }

    /// Ask the parent for a file after the user invokes the app's Open command.
    pub fn post_open_request(&self, purpose: &str) -> Result<(), JsValue> {
        self.post(&format!("{}:openRequest", self.app), &[("purpose", &JsValue::from_str(purpose))])
    }

    /// Ask the parent to open a file. App-specific name and byte policy stays with the app.
    pub fn post_open(&self, name: &str, bytes: &[u8]) -> Result<(), JsValue> {
        let object = self.message(&format!("{}:open", self.app));
        Reflect::set(&object, &"name".into(), &name.into())?;
        let buffer = Uint8Array::from(bytes).buffer();
        Reflect::set(&object, &"bytes".into(), &buffer)?;
        self.parent.post_message_with_transfer(&object, &self.origin, &Array::of1(&buffer))
    }

    /// Send serialized bytes with an opaque ticket. This means delivered to the parent only;
    /// the host must send a later `saveResult` after durable storage confirms the write.
    pub fn post_save(&self, ticket: &SaveTicket, name: &str, bytes: &[u8], save_as: bool) -> Result<(), JsValue> {
        let object = self.message(&format!("{}:save", self.app));
        Reflect::set(&object, &"ticket".into(), &ticket.as_str().into())?;
        Reflect::set(&object, &"name".into(), &name.into())?;
        let buffer = Uint8Array::from(bytes).buffer();
        Reflect::set(&object, &"bytes".into(), &buffer)?;
        Reflect::set(&object, &"saveAs".into(), &save_as.into())?;
        self.parent.post_message_with_transfer(&object, &self.origin, &Array::of1(&buffer))
    }

    fn post(&self, kind: &str, fields: &[(&str, &JsValue)]) -> Result<(), JsValue> {
        let object = self.message(kind);
        for (key, value) in fields {
            Reflect::set(&object, &JsValue::from_str(key), value)?;
        }
        self.parent.post_message(&object, &self.origin)
    }

    fn message(&self, kind: &str) -> Object {
        let object = Object::new();
        let _ = Reflect::set(&object, &"type".into(), &kind.into());
        object
    }
}

/// Owns and removes the global message listener on drop.
pub struct HostListener {
    target: EventTarget,
    handler: Option<Closure<dyn FnMut(MessageEvent)>>,
}
impl Drop for HostListener {
    fn drop(&mut self) {
        if let Some(handler) = self.handler.take() {
            let _ = self.target.remove_event_listener_with_callback("message", handler.as_ref().unchecked_ref());
        }
    }
}

fn string_field(value: &JsValue, key: &str) -> Result<String, JsValue> {
    Reflect::get(value, &JsValue::from_str(key))?.as_string().ok_or_else(|| JsValue::from_str("expected string field"))
}

fn read_bytes(value: &JsValue) -> Option<Vec<u8>> {
    if let Some(array) = value.dyn_ref::<Uint8Array>() {
        Some(array.to_vec())
    } else if value.is_instance_of::<js_sys::ArrayBuffer>() {
        Some(Uint8Array::new(value).to_vec())
    } else {
        None
    }
}
