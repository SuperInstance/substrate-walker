//! Raycasting engine: casts rays through the city grid and renders ASCII glyphs.

use alloc::vec::Vec;

use crate::cell::CityGrid;
use crate::types::{
    pack_cell, pack_cell_dark, alpha_for_distance, glyph_for_distance,
    PackedCell, SCREEN_HEIGHT, SCREEN_WIDTH,
};

/// Camera state for the raycaster.
#[derive(Debug, Clone, Copy)]
pub struct Camera {
    pub x: f32,
    pub y: f32,
    pub angle: f32,     // Radians, 0 = east, π/2 = north
    pub fov: f32,       // Field of view in radians (default 1.0)
    pub max_distance: f32,
}

impl Default for Camera {
    fn default() -> Self {
        Self {
            x: 16.0,
            y: 16.0,
            angle: 0.0,
            fov: 1.0,
            max_distance: 32.0,
        }
    }
}

/// Fast f32 sin approximation (Bhaskara I / accurate enough for raycasting).
#[inline]
fn fsin(x: f32) -> f32 {
    x.sin()
}

/// Fast f32 cos approximation.
#[inline]
fn fcos(x: f32) -> f32 {
    x.cos()
}

/// The raycasting engine itself.
pub struct Raycaster {
    pub buffer: Vec<PackedCell>,
    pub camera: Camera,
}

impl Raycaster {
    /// Create a new raycaster with an empty screen buffer.
    pub fn new() -> Self {
        Self {
            buffer: vec![pack_cell_dark(b' ', 0); SCREEN_WIDTH * SCREEN_HEIGHT],
            camera: Camera::default(),
        }
    }

    /// Get a raw pointer to the buffer (for WASM zero-copy).
    pub fn buffer_ptr(&self) -> *const PackedCell {
        self.buffer.as_ptr()
    }

    /// Get buffer as a byte slice for WebGL upload.
    pub fn buffer_bytes(&self) -> &[u8] {
        let len = self.buffer.len() * 4;
        unsafe {
            core::slice::from_raw_parts(self.buffer.as_ptr() as *const u8, len)
        }
    }

    /// Cast rays across the city grid and update the screen buffer.
    pub fn cast(&mut self, grid: &CityGrid) {
        let half_fov = self.camera.fov * 0.5;
        let screen_w = SCREEN_WIDTH;
        let screen_h = SCREEN_HEIGHT;
        let map_w = grid.width as usize;
        let map_h = grid.height as usize;

        for sx in 0..screen_w {
            let ray_angle = self.camera.angle - half_fov
                + (sx as f32 / screen_w as f32) * self.camera.fov;

            let eye_x = fsin(ray_angle);
            let eye_y = fcos(ray_angle);

            // Camera cell (skip the cell we're standing in)
            let cam_cell_x = self.camera.x as i32;
            let cam_cell_y = self.camera.y as i32;

            let mut distance = 0.3_f32;  // Start a bit out from camera
            let mut hit_height: f32 = 0.0;
            let mut hit_color: (u8, u8, u8) = (0xFF, 0xFF, 0xFF);
            let mut hit_cell_type: u8 = 0;
            let mut found_hit = false;

            while distance < self.camera.max_distance {
                distance += 0.05;
                let test_x = (self.camera.x + eye_x * distance) as i32;
                let test_y = (self.camera.y + eye_y * distance) as i32;

                // Skip the cell the camera is in
                if test_x == cam_cell_x && test_y == cam_cell_y {
                    continue;
                }

                if test_x < 0 || test_x >= map_w as i32 || test_y < 0 || test_y >= map_h as i32 {
                    hit_height = 0.0;
                    hit_color = (0x80, 0x80, 0x80);
                    found_hit = true;
                    break;
                }

                if let Some(cell) = grid.get(test_x as usize, test_y as usize) {
                    if cell.is_solid() {
                        hit_height = cell.height_f32();
                        hit_color = cell.color_hint();
                        hit_cell_type = cell.cell_type;
                        found_hit = true;
                        break;
                    }
                }
            }

            // If never hit, set distance to max
            if !found_hit {
                distance = self.camera.max_distance;
            }

            let angle_delta = ray_angle - self.camera.angle;
            let corrected = distance * fcos(angle_delta);

            // Wall projection: Thales theorem
            // A 1-unit tall wall at distance D projects to screen_h / D
            // Scale by hit_height for taller buildings
            let wall_height = ((hit_height.max(1.0) * screen_h as f32) / (corrected * 30.0).max(0.5)) as i32;
            let wall_height_capped = wall_height.min(screen_h as i32).max(1);
            let wall_top = if wall_height_capped >= screen_h as i32 {
                0
            } else {
                (screen_h as i32 - wall_height_capped) / 2
            };
            let wall_bottom = wall_top + wall_height_capped;

            let glyph = glyph_for_distance(corrected);
            let alpha = alpha_for_distance(corrected);

            let (r, g, b) = hit_color;

            for sy in 0..screen_h {
                let idx = sy * screen_w + sx;
                if (sy as i32) < wall_top {
                    // Sky (vacuum space) — dark blue
                    self.buffer[idx] = pack_cell(b' ', 0x10, 0x10, 0x20, 0xFF);
                } else if (sy as i32) < wall_bottom {
                    // Wall — color from cell type, alpha from distance
                    let wall_alpha = (alpha as u32 * hit_height as u32 / 30).min(255) as u8;
                    self.buffer[idx] = pack_cell(glyph, r, g, b, wall_alpha.max(alpha));
                } else {
                    // Floor — fading into the distance
                    let sy_f = sy as f32;
                    let floor_depth = screen_h as f32 / (2.0 * sy_f - screen_h as f32 + 0.01).max(0.1);
                    let floor_alpha = ((1.0 - (floor_depth / 20.0).min(1.0)) * 255.0).max(0.0) as u8;
                    self.buffer[idx] = pack_cell(b'_', 0x11, 0x11, 0x11, floor_alpha);
                }
            }
        }
    }
}

impl Default for Raycaster {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cell::CityGrid;

    #[test]
    fn test_creation() {
        let r = Raycaster::new();
        assert_eq!(r.buffer.len(), SCREEN_WIDTH * SCREEN_HEIGHT);
    }

    #[test]
    fn test_cast_empty_grid() {
        let mut r = Raycaster::new();
        let grid = CityGrid::new(8, 8);
        r.cast(&grid);
        assert!(r.buffer.len() > 0);
    }

    #[test]
    fn test_cast_with_buildings() {
        let mut r = Raycaster::new();
        let grid = CityGrid::generate_city(42);
        r.camera.x = 5.0;
        r.camera.y = 5.0;
        r.cast(&grid);
        assert!(r.buffer.len() > 0);
    }

    #[test]
    fn test_render_to_text() {
        let mut r = Raycaster::new();
        let grid = CityGrid::generate_city(42);
        r.camera.x = 5.0;
        r.camera.y = 5.0;
        r.cast(&grid);
        
        let mut text = String::new();
        for sy in 0..SCREEN_HEIGHT {
            for sx in 0..SCREEN_WIDTH {
                let cell = r.buffer[sy * SCREEN_WIDTH + sx];
                let glyph = (cell & 0xFF) as u8 as char;
                text.push(if glyph == '\0' { ' ' } else { glyph });
            }
            text.push('\n');
        }
        assert_eq!(text.lines().count(), SCREEN_HEIGHT);
    }
}
