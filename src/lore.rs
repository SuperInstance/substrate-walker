//! Lore metadata attached to substrate cells.
//!
//! When the player visits a cell for the first time, the JEV frontal-cortex
//! fires to generate a brief description. The lore is cached on the cell's
//! metadata field, so re-visits are free (no API call).

extern crate alloc;
use alloc::string::String;

use crate::types::fnv1a_64;

/// Type of lore attached to a cell.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
pub enum LoreKind {
    None = 0,
    BuildingName = 1,
    DistrictName = 2,
    WitnessNote = 3,
    CanonQuote = 4,
    Perception = 5,
}

impl LoreKind {
    pub fn from_u8(v: u8) -> Self {
        match v {
            1 => LoreKind::BuildingName,
            2 => LoreKind::DistrictName,
            3 => LoreKind::WitnessNote,
            4 => LoreKind::CanonQuote,
            5 => LoreKind::Perception,
            _ => LoreKind::None,
        }
    }
}

/// A small lore snippet attached to a cell.
///
/// We keep the lore inline in the cell to avoid an extra allocation. The
/// snippet is a fixed-size byte array of up to 64 bytes plus a 4-byte hash
/// of the full description (for the chain).
#[derive(Debug, Clone, Copy)]
pub struct LoreSlot {
    pub kind: LoreKind,
    pub hash: u32,         // FNV-1a 32 of full description (truncated)
    pub snippet: [u8; 64], // Inline snippet (null-padded)
    pub len: u8,           // Actual length of snippet
}

impl LoreSlot {
    pub const EMPTY: LoreSlot = LoreSlot {
        kind: LoreKind::None,
        hash: 0,
        snippet: [0u8; 64],
        len: 0,
    };

    pub fn is_empty(&self) -> bool {
        self.kind == LoreKind::None
    }

    /// Set lore from a string. Returns the FNV-1a 32-bit hash.
    pub fn set(&mut self, kind: LoreKind, text: &str) -> u32 {
        self.kind = kind;
        self.snippet = [0u8; 64];
        let bytes = text.as_bytes();
        let len = bytes.len().min(64);
        self.snippet[..len].copy_from_slice(&bytes[..len]);
        self.len = len as u8;
        // Compute 32-bit FNV-1a of full text
        let h64 = fnv1a_64(bytes);
        self.hash = (h64 & 0xFFFFFFFF) as u32;
        self.hash
    }

    /// Get the lore snippet as a string (if non-empty).
    pub fn get(&self) -> Option<String> {
        if self.is_empty() {
            return None;
        }
        // Use alloc::string::String for no_std
        Some(String::from_utf8_lossy(&self.snippet[..self.len as usize]).into_owned())
    }
}

impl Default for LoreSlot {
    fn default() -> Self {
        Self::EMPTY
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_empty_lore() {
        let lore = LoreSlot::EMPTY;
        assert!(lore.is_empty());
        assert_eq!(lore.get(), None);
    }

    #[test]
    fn test_set_lore() {
        let mut lore = LoreSlot::EMPTY;
        lore.set(LoreKind::BuildingName, "Tower of Memory");
        assert!(!lore.is_empty());
        assert_eq!(lore.get().as_deref(), Some("Tower of Memory"));
        assert!(lore.hash != 0);
    }

    #[test]
    fn test_long_lore_truncates() {
        let mut lore = LoreSlot::EMPTY;
        let long = "This is a very long building description that exceeds sixty-four bytes";
        lore.set(LoreKind::DistrictName, long);
        let stored = lore.get().unwrap();
        assert_eq!(stored.len(), 64);
    }
}
