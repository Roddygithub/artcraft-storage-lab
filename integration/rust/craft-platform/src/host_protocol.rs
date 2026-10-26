//! Small, app-agnostic pieces of the parent-frame save protocol.
use std::collections::HashMap;

/// Opaque host correlation token. It is deliberately a string so it is safe across JS runtimes.
#[derive(Clone, Debug, Eq, Hash, PartialEq)]
pub struct SaveTicket(String);

impl SaveTicket {
    /// Construct a non-empty ticket.
    pub fn new(value: impl Into<String>) -> Option<Self> {
        let value = value.into();
        (!value.trim().is_empty() && value.len() <= 256).then_some(Self(value))
    }

    /// Borrow the wire representation.
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Tracks pending host saves and consumes each acknowledgement at most once.
#[derive(Debug)]
pub struct PendingSaves<T> {
    pending: HashMap<SaveTicket, T>,
}

impl<T> Default for PendingSaves<T> {
    fn default() -> Self {
        Self {
            pending: HashMap::new(),
        }
    }
}

const MAX_PENDING_SAVES: usize = 64;

/// Bounds total parent-provided document copies in one editor runtime.
#[derive(Debug, Default)]
pub struct OpenAdmission {
    messages: usize,
    bytes: usize,
}

const MAX_OPEN_MESSAGES: usize = 64;

impl<T> PendingSaves<T> {
    pub fn insert(&mut self, ticket: SaveTicket, value: T) -> Result<(), T> {
        if self.pending.contains_key(&ticket) || self.pending.len() >= MAX_PENDING_SAVES {
            return Err(value);
        }
        self.pending.insert(ticket, value);
        Ok(())
    }
    pub fn complete(&mut self, ticket: &SaveTicket) -> Option<T> {
        self.pending.remove(ticket)
    }
    pub fn len(&self) -> usize {
        self.pending.len()
    }
    pub fn is_empty(&self) -> bool {
        self.pending.is_empty()
    }
    /// Whether any outstanding save carries a matching snapshot or revision.
    pub fn any(&self, predicate: impl FnMut(&T) -> bool) -> bool {
        self.pending.values().any(predicate)
    }
}

impl OpenAdmission {
    /// Admit multiple opens within a cumulative byte and message budget.
    pub fn admit(&mut self, byte_len: usize, max_bytes: usize) -> bool {
        if self.messages >= MAX_OPEN_MESSAGES || byte_len > max_bytes.saturating_sub(self.bytes) {
            return false;
        }
        self.messages += 1;
        self.bytes += byte_len;
        true
    }
}

/// True only for a message from the expected origin and actual parent frame.
pub fn accepts_parent_message(origin: &str, expected_origin: &str, source_is_parent: bool) -> bool {
    source_is_parent && origin == expected_origin
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tickets_are_opaque_strings_and_can_exceed_js_safe_integer_range() {
        let ticket = SaveTicket::new("wordcraft:9007199254740993").expect("non-empty");
        assert_eq!(ticket.as_str(), "wordcraft:9007199254740993");
    }

    #[test]
    fn pending_save_acknowledgement_is_consumed_once() {
        let ticket = SaveTicket::new("gridcraft:1").expect("non-empty");
        let mut pending = PendingSaves::default();
        assert_eq!(pending.insert(ticket.clone(), 42), Ok(()));
        assert_eq!(pending.complete(&ticket), Some(42));
        assert_eq!(pending.complete(&ticket), None);
    }

    #[test]
    fn pending_saves_are_bounded() {
        let mut pending = PendingSaves::default();
        for id in 0..MAX_PENDING_SAVES {
            let ticket = SaveTicket::new(format!("app:{id}")).expect("non-empty");
            assert!(pending.insert(ticket, id).is_ok());
        }
        let overflow = SaveTicket::new("app:overflow").expect("non-empty");
        assert!(pending.insert(overflow, 0).is_err());
    }

    #[test]
    fn parent_messages_require_exact_origin_and_parent_source() {
        assert!(accepts_parent_message(
            "https://host.test",
            "https://host.test",
            true
        ));
        assert!(!accepts_parent_message(
            "https://evil.test",
            "https://host.test",
            true
        ));
        assert!(!accepts_parent_message(
            "https://host.test",
            "https://host.test",
            false
        ));
    }

    #[test]
    fn open_admission_bounds_cumulative_bytes_and_message_count() {
        let mut admission = OpenAdmission::default();
        assert!(!admission.admit(9, 8));
        assert!(admission.admit(4, 8));
        assert!(admission.admit(4, 8));
        assert!(!admission.admit(1, 8));

        let mut empty_opens = OpenAdmission::default();
        for _ in 0..MAX_OPEN_MESSAGES {
            assert!(empty_opens.admit(0, 8));
        }
        assert!(!empty_opens.admit(0, 8));
    }
}
