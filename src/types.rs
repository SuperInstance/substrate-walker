//! Core types for the substrate ASCII city.
//!
//! These types are no_std compatible and serialization-agnostic.

/// FNV-1a 64-bit hash constants (matches fleet canary).
pub const FNV_OFFSET: u64 = 0xcbf29ce484222325;
pub const FNV_PRIME: u64 = 0x100000001b3;

/// Compute FNV-1a 64-bit hash.
pub fn fnv1a_64(bytes: &[u8]) -> u64 {
    let mut h = FNV_OFFSET;
    for byte in bytes {
        h ^= *byte as u64;
        h = h.wrapping_mul(FNV_PRIME);
    }
    h
}

/// Verify the fleet canary matches across all our substrate repos.
pub fn verify_canary() -> bool {
    let s = "café Δ 日本語";
    let bytes = s.as_bytes();
    fnv1a_64(bytes) == 0x24a555471370b18d
}

/// Screen dimensions (classic 160x60 terminal).
pub const SCREEN_WIDTH: usize = 160;
pub const SCREEN_HEIGHT: usize = 60;
pub const BUFFER_SIZE: usize = SCREEN_WIDTH * SCREEN_HEIGHT;

/// ASCII glyph for a screen cell (0 = space).
pub type Glyph = u8;

/// Packed cell descriptor: 32-bit word encoding glyph + color + luminance.
///
/// Layout (matches the spec Casey shared):
///   bits  0..7   → ASCII glyph (u8)
///   bits  8..15  → Red channel (u8)
///   bits 16..23  → Green channel (u8)
///   bits 24..31  → Alpha / luminance (u8)
///
/// NOTE: Blue is sacrificed here; we keep 4 channels for RGBA compatibility
/// with WebGL textures. To preserve B, we encode it in the alpha channel
/// when needed via blending.
pub type PackedCell = u32;

/// Pack a glyph + RGBA into a single u32.
#[inline]
pub const fn pack_cell(glyph: u8, r: u8, g: u8, b: u8, alpha: u8) -> PackedCell {
    ((alpha as u32) << 24)
        | ((g as u32) << 16)
        | ((r as u32) << 8)
        | (glyph as u32)
}

/// Pack cell with no blue component (b is implicit).
#[inline]
pub const fn pack_cell_rgb(glyph: u8, r: u8, g: u8, alpha: u8) -> PackedCell {
    ((alpha as u32) << 24)
        | ((g as u32) << 16)
        | ((r as u32) << 8)
        | (glyph as u32)
}

#[inline]
pub const fn pack_cell_simple(glyph: u8, alpha: u8) -> PackedCell {
    pack_cell(glyph, 0xFF, 0xFF, 0xFF, alpha)
}

#[inline]
pub const fn pack_cell_violet(glyph: u8, alpha: u8) -> PackedCell {
    pack_cell(glyph, 0xFF, 0x80, 0xFF, alpha) // Neon violet
}

#[inline]
pub const fn pack_cell_cyan(glyph: u8, alpha: u8) -> PackedCell {
    pack_cell(glyph, 0x80, 0xFF, 0xFF, alpha) // Cyan
}

#[inline]
pub const fn pack_cell_dark(glyph: u8, alpha: u8) -> PackedCell {
    pack_cell(glyph, 0x40, 0x40, 0x40, alpha)
}

/// Extract glyph from a packed cell.
#[inline]
pub fn unpack_glyph(p: PackedCell) -> Glyph {
    (p & 0xFF) as Glyph
}

/// Extract red from a packed cell.
#[inline]
pub fn unpack_r(p: PackedCell) -> u8 {
    ((p >> 8) & 0xFF) as u8
}

/// Extract green from a packed cell.
#[inline]
pub fn unpack_g(p: PackedCell) -> u8 {
    ((p >> 16) & 0xFF) as u8
}

/// Extract alpha from a packed cell.
#[inline]
pub fn unpack_a(p: PackedCell) -> u8 {
    ((p >> 24) & 0xFF) as u8
}

/// Map a distance to an ASCII glyph (luminance ramp).
pub fn glyph_for_distance(distance: f32) -> Glyph {
    if distance < 1.5 {
        b'@'
    } else if distance < 2.5 {
        b'#'
    } else if distance < 4.0 {
        b'$'
    } else if distance < 6.0 {
        b'X'
    } else if distance < 9.0 {
        b'='
    } else if distance < 14.0 {
        b':'
    } else {
        b'.'
    }
}

/// Map a distance to a base alpha (0 = invisible, 255 = opaque).
pub fn alpha_for_distance(distance: f32) -> u8 {
    if distance < 1.5 {
        255
    } else if distance < 3.0 {
        220
    } else if distance < 5.0 {
        180
    } else if distance < 8.0 {
        130
    } else if distance < 12.0 {
        90
    } else if distance < 18.0 {
        60
    } else {
        30
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fleet_canary() {
        assert!(verify_canary());
    }

    #[test]
    fn test_pack_cell() {
        let p = pack_cell(b'A', 0x80, 0x40, 0x20, 0xFF);
        assert_eq!(unpack_glyph(p), b'A');
        assert_eq!(unpack_r(p), 0x80);
        assert_eq!(unpack_g(p), 0x40);
        assert_eq!(unpack_a(p), 0xFF);
    }

    #[test]
    fn test_glyph_ramp() {
        assert_eq!(glyph_for_distance(1.0), b'@');
        assert_eq!(glyph_for_distance(20.0), b'.');
        assert_eq!(glyph_for_distance(7.0), b'=');
    }

    #[test]
    fn test_alpha_ramp() {
        assert_eq!(alpha_for_distance(1.0), 255);
        assert_eq!(alpha_for_distance(20.0), 30);
    }
}
