//! Same-origin iframe transport for the common Craft host protocol.
use js_sys::{Array, Object, Reflect, Uint8Array};
use std::{cell::RefCell, collections::HashMap, rc::Rc};
use wasm_bindgen::{JsCast, JsValue, closure::Closure};
use web_sys::{EventTarget, MessageEvent, Window};

use crate::host_protocol::{OpenAdmission, SaveTicket, accepts_parent_message};

const MAX_OPEN_BYTES: usize = 256 * 1024 * 1024;
const MAX_TYPE_UTF16_UNITS: u32 = 128;
const MAX_NAME_UTF16_UNITS: u32 = 1024;
const MAX_TICKET_UTF16_UNITS: u32 = 256;
const MAX_ERROR_UTF16_UNITS: u32 = 4096;

thread_local! {
    static OPEN_ADMISSIONS: RefCell<HashMap<(String, String), Rc<RefCell<OpenAdmission>>>> =
        RefCell::new(HashMap::new());
}

/// Messages received from the parent host.
pub enum HostMessage {
    Open {
        name: String,
        bytes: Vec<u8>,
    },
    SaveResult {
        ticket: SaveTicket,
        ok: bool,
        error: Option<String>,
    },
}

/// Same-origin parent window transport for one named Craft app.
#[derive(Clone)]
pub struct HostTransport {
    parent: Window,
    origin: String,
    app: String,
    open_admission: Rc<RefCell<OpenAdmission>>,
}

impl HostTransport {
    /// Return a transport only when this page is framed by a same-origin parent.
    pub fn current(app: &str) -> Result<Option<Self>, JsValue> {
        let Some(window) = web_sys::window() else {
            return Ok(None);
        };
        let Some(parent) = window.parent()? else {
            return Ok(None);
        };
        if Object::is(parent.as_ref(), window.as_ref()) {
            return Ok(None);
        }
        let origin = window.location().origin()?;
        if origin.is_empty() || app.trim().is_empty() || parent.location().origin()? != origin {
            return Ok(None);
        }
        let open_admission = shared_open_admission(&origin, app);
        Ok(Some(Self {
            parent,
            origin,
            app: app.to_owned(),
            open_admission,
        }))
    }

    /// Listen for parent messages. Exact origin and `event.source` are both checked.
    /// Open bytes are admitted within a cumulative per-app runtime budget before copying.
    pub fn listen(
        &self,
        mut callback: impl FnMut(HostMessage) + 'static,
    ) -> Result<HostListener, JsValue> {
        let window = web_sys::window().ok_or_else(|| JsValue::from_str("no browser window"))?;
        let parent: JsValue = self.parent.clone().into();
        let origin = self.origin.clone();
        let app = self.app.clone();
        let open_admission = self.open_admission.clone();
        let handler = Closure::<dyn FnMut(MessageEvent)>::new(move |event: MessageEvent| {
            let source_is_parent = event
                .source()
                .is_some_and(|source| Object::is(source.as_ref(), &parent));
            if !accepts_parent_message(&event.origin(), &origin, source_is_parent) {
                return;
            }
            let data = event.data();
            let Ok(kind) = string_field(&data, "type", MAX_TYPE_UTF16_UNITS) else {
                return;
            };
            if kind == format!("{app}:open") {
                let Ok(name) = string_field(&data, "name", MAX_NAME_UTF16_UNITS) else {
                    return;
                };
                let Ok(value) = Reflect::get(&data, &JsValue::from_str("bytes")) else {
                    return;
                };
                let Some(length) = bytes_len(&value).filter(|length| *length <= MAX_OPEN_BYTES)
                else {
                    return;
                };
                if !open_admission.borrow_mut().admit(length, MAX_OPEN_BYTES) {
                    return;
                }
                let Some(bytes) = read_bytes(&value, MAX_OPEN_BYTES) else {
                    return;
                };
                callback(HostMessage::Open { name, bytes });
            } else if kind == format!("{app}:saveResult") {
                let Ok(ticket_value) = string_field(&data, "ticket", MAX_TICKET_UTF16_UNITS) else {
                    return;
                };
                let Some(ticket) = SaveTicket::new(ticket_value) else {
                    return;
                };
                let Ok(ok) = Reflect::get(&data, &JsValue::from_str("ok")) else {
                    return;
                };
                let error = string_field(&data, "error", MAX_ERROR_UTF16_UNITS).ok();
                callback(HostMessage::SaveResult {
                    ticket,
                    ok: ok.as_bool().unwrap_or(false),
                    error,
                });
            }
        });
        window.add_event_listener_with_callback("message", handler.as_ref().unchecked_ref())?;
        Ok(HostListener {
            target: window.unchecked_into(),
            handler: Some(handler),
        })
    }

    /// Notify the parent that the editor bridge is ready.
    pub fn post_ready(&self, version: &str) -> Result<(), JsValue> {
        self.post(
            &format!("{}:ready", self.app),
            &[(&"version", &JsValue::from_str(version))],
        )
    }

    /// Report editor dirty state.
    pub fn post_dirty(&self, dirty: bool) -> Result<(), JsValue> {
        self.post(
            &format!("{}:dirty", self.app),
            &[(&"dirty", &JsValue::from_bool(dirty))],
        )
    }

    /// Send a failure that is not tied to a save ticket.
    pub fn post_failed(&self, error: &str) -> Result<(), JsValue> {
        self.post(
            &format!("{}:failed", self.app),
            &[(&"error", &JsValue::from_str(error))],
        )
    }

    /// Ask the parent for a file after the user invokes the app's Open command.
    pub fn post_open_request(&self, purpose: &str) -> Result<(), JsValue> {
        self.post(
            &format!("{}:openRequest", self.app),
            &[("purpose", &JsValue::from_str(purpose))],
        )
    }

    /// Ask the parent to open a file. App-specific name and byte policy stays with the app.
    pub fn post_open(&self, name: &str, bytes: &[u8]) -> Result<(), JsValue> {
        let object = self.message(&format!("{}:open", self.app));
        Reflect::set(&object, &"name".into(), &name.into())?;
        let buffer = Uint8Array::from(bytes).buffer();
        Reflect::set(&object, &"bytes".into(), &buffer)?;
        self.parent
            .post_message_with_transfer(&object, &self.origin, &Array::of1(&buffer))
    }

    /// Send serialized bytes with an opaque ticket. This means delivered to the parent only;
    /// the host must send a later `saveResult` after durable storage confirms the write.
    pub fn post_save(
        &self,
        ticket: &SaveTicket,
        name: &str,
        bytes: &[u8],
        save_as: bool,
    ) -> Result<(), JsValue> {
        let object = self.message(&format!("{}:save", self.app));
        Reflect::set(&object, &"ticket".into(), &ticket.as_str().into())?;
        Reflect::set(&object, &"name".into(), &name.into())?;
        let buffer = Uint8Array::from(bytes).buffer();
        Reflect::set(&object, &"bytes".into(), &buffer)?;
        Reflect::set(&object, &"saveAs".into(), &save_as.into())?;
        self.parent
            .post_message_with_transfer(&object, &self.origin, &Array::of1(&buffer))
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

fn shared_open_admission(origin: &str, app: &str) -> Rc<RefCell<OpenAdmission>> {
    OPEN_ADMISSIONS.with(|admissions| {
        let mut admissions = admissions.borrow_mut();
        let key = (origin.to_owned(), app.to_owned());
        Rc::clone(
            admissions
                .entry(key)
                .or_insert_with(|| Rc::new(RefCell::new(OpenAdmission::default()))),
        )
    })
}

/// Owns and removes the global message listener on drop.
pub struct HostListener {
    target: EventTarget,
    handler: Option<Closure<dyn FnMut(MessageEvent)>>,
}
impl Drop for HostListener {
    fn drop(&mut self) {
        if let Some(handler) = self.handler.take() {
            let _ = self
                .target
                .remove_event_listener_with_callback("message", handler.as_ref().unchecked_ref());
        }
    }
}

fn string_field(value: &JsValue, key: &str, max_utf16_units: u32) -> Result<String, JsValue> {
    let field = Reflect::get(value, &JsValue::from_str(key))?;
    let Some(field) = field.dyn_ref::<js_sys::JsString>() else {
        return Err(JsValue::from_str("expected string field"));
    };
    if field.length() > max_utf16_units {
        return Err(JsValue::from_str("string field exceeds size limit"));
    }
    field
        .as_string()
        .ok_or_else(|| JsValue::from_str("expected string field"))
}

fn bytes_len(value: &JsValue) -> Option<usize> {
    if let Some(array) = value.dyn_ref::<Uint8Array>() {
        Some(array.length() as usize)
    } else if let Some(buffer) = value.dyn_ref::<js_sys::ArrayBuffer>() {
        Some(buffer.byte_length() as usize)
    } else {
        None
    }
}

fn read_bytes(value: &JsValue, max_bytes: usize) -> Option<Vec<u8>> {
    let length = bytes_len(value)?;
    if length > max_bytes {
        return None;
    }
    if let Some(array) = value.dyn_ref::<Uint8Array>() {
        Some(array.to_vec())
    } else if value.is_instance_of::<js_sys::ArrayBuffer>() {
        Some(Uint8Array::new(value).to_vec())
    } else {
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use wasm_bindgen_test::wasm_bindgen_test;

    #[wasm_bindgen_test]
    fn separate_transports_share_open_budget_for_same_app_and_origin() {
        let first = shared_open_admission("https://host.test", "wordcraft");
        let second = shared_open_admission("https://host.test", "wordcraft");
        assert!(Rc::ptr_eq(&first, &second));
        assert!(first.borrow_mut().admit(4, 8));
        assert!(second.borrow_mut().admit(4, 8));
        assert!(!first.borrow_mut().admit(1, 8));

        let other_app = shared_open_admission("https://host.test", "gridcraft");
        assert!(!Rc::ptr_eq(&first, &other_app));
        assert!(other_app.borrow_mut().admit(8, 8));
    }

    #[wasm_bindgen_test]
    fn oversized_arraybuffer_and_typed_array_are_rejected_before_copy() {
        let buffer = js_sys::ArrayBuffer::new(8);
        assert!(read_bytes(buffer.as_ref(), 4).is_none());

        let array = Uint8Array::new_with_length(8);
        assert!(read_bytes(array.as_ref(), 4).is_none());
        assert_eq!(
            read_bytes(array.as_ref(), 8).map(|bytes| bytes.len()),
            Some(8)
        );
    }

    #[wasm_bindgen_test]
    fn oversized_metadata_strings_are_rejected_before_conversion() {
        let object = Object::new();
        let long = JsValue::from_str("0123456789");
        assert!(Reflect::set(&object, &"field".into(), &long).is_ok());
        assert!(string_field(object.as_ref(), "field", 4).is_err());
        assert_eq!(
            string_field(object.as_ref(), "field", 10).ok().as_deref(),
            Some("0123456789")
        );
    }
}
