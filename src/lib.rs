//! Cyberpunk ASCII City — Rust core.
//!
//! 3D ASCII city city running on Rust + WASM + WebGL. Substrate cells
//! become buildings. FNV-1a 64-bit prev_hash chain integrity.
//!
//! # Architecture
//!
//! ```text
//! [ CityGrid (32×32 cells) ]
//!           ↓
//! [ Raycaster::cast(camera, grid) ]
//!           ↓
//! [ Vec<PackedCell> of 160×60 cells ]
//!           ↓
//! [ Zero-copy WebGL upload via shared buffer ]
//!           ↓
//! [ GPU fragment shader → font atlas → screen ]
//! ```

#![cfg_attr(feature = "wasm", no_std)]
#[cfg(feature = "wasm")]
#[macro_use]
extern crate alloc;

#[cfg(not(feature = "wasm"))]
extern crate alloc;

mod cell;
mod engine;
mod jepa_predict;
mod lore;
mod scoring;
mod types;

pub use cell::{CityCell, CityGrid};
pub use engine::{Camera, Raycaster};
pub use jepa_predict::{JepaPredictor, Velocity};
pub use scoring::{CellScore, score_grid};
pub use lore::{LoreKind, LoreSlot};
pub use types::{
    fnv1a_64, pack_cell, verify_canary,
    BUFFER_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH,
    Glyph, PackedCell,
};

/// Top-level engine that ties grid + raycaster together.
pub struct CityEngine {
    pub grid: CityGrid,
    pub raycaster: Raycaster,
    pub frame_count: u32,
}

impl CityEngine {
    /// Create a new city engine with a procedural city layout.
    pub fn new(seed: u32) -> Self {
        Self {
            grid: CityGrid::generate_city(seed),
            raycaster: Raycaster::new(),
            frame_count: 0,
        }
    }

    /// Create with an empty grid.
    pub fn empty(width: u8, height: u8) -> Self {
        Self {
            grid: CityGrid::new(width, height),
            raycaster: Raycaster::new(),
            frame_count: 0,
        }
    }

    /// Cast rays for the current camera position and update the buffer.
    pub fn step(&mut self) {
        self.raycaster.cast(&self.grid);
        self.frame_count += 1;
    }

    /// Move camera forward in its facing direction.
    pub fn move_forward(&mut self, distance: f32) {
        self.raycaster.camera.x += f32::sin(self.raycaster.camera.angle) * distance;
        self.raycaster.camera.y += f32::cos(self.raycaster.camera.angle) * distance;
    }

    /// Rotate camera by delta radians.
    pub fn rotate(&mut self, delta: f32) {
        self.raycaster.camera.angle += delta;
    }

    /// Get a raw pointer to the screen buffer (for WASM).
    pub fn buffer_ptr(&self) -> *const u32 {
        self.raycaster.buffer_ptr() as *const u32
    }

    /// Get buffer as raw bytes (for WebGL upload).
    pub fn buffer_bytes(&self) -> &[u8] {
        self.raycaster.buffer_bytes()
    }

    /// Get camera state as floats.
    pub fn camera_state(&self) -> (f32, f32, f32) {
        (
            self.raycaster.camera.x,
            self.raycaster.camera.y,
            self.raycaster.camera.angle,
        )
    }

    /// Set camera position.
    pub fn set_camera(&mut self, x: f32, y: f32, angle: f32) {
        self.raycaster.camera.x = x;
        self.raycaster.camera.y = y;
        self.raycaster.camera.angle = angle;
    }

    /// Get grid dimensions.
    pub fn grid_dims(&self) -> (u8, u8) {
        (self.grid.width, self.grid.height)
    }

    /// Set a cell (height + type) at (x, y).
    pub fn set_cell(&mut self, x: usize, y: usize, height: u8, cell_type: u8) {
        self.grid.set(x, y, height, cell_type);
    }

    /// Verify the substrate chain integrity.
    pub fn verify_chain(&self) -> bool {
        self.grid.verify_chain()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_canary() {
        assert!(verify_canary());
    }

    #[test]
    fn test_engine_creation() {
        let engine = CityEngine::new(42);
        assert_eq!(engine.grid.width, 32);
        assert_eq!(engine.frame_count, 0);
    }

    #[test]
    fn test_step() {
        let mut engine = CityEngine::new(42);
        engine.step();
        assert_eq!(engine.frame_count, 1);
        assert!(!engine.buffer_ptr().is_null());
    }

    #[test]
    fn test_movement() {
        let mut engine = CityEngine::new(42);
        let (x0, y0, _) = engine.camera_state();
        engine.rotate(0.5);
        engine.move_forward(2.0);
        let (x1, y1, _) = engine.camera_state();
        assert_ne!(x0, x1);
        assert_ne!(y0, y1);
    }

    #[test]
    fn test_chain_integrity() {
        let engine = CityEngine::new(42);
        assert!(engine.verify_chain());
    }
}

// WASM bindings (only compiled with wasm-bindgen)
#[cfg(feature = "wasm")]
#[cfg(feature = "wasm")]
mod wasm_api {
    use super::*;
    use wasm_bindgen::prelude::*;

    #[wasm_bindgen(start)]
    pub fn start() {
        // Initialization hook
    }

    #[wasm_bindgen]
    pub struct WasmCity {
        engine: CityEngine,
    }

    #[wasm_bindgen]
    impl WasmCity {
        #[wasm_bindgen(constructor)]
        pub fn new(seed: u32) -> Self {
            Self {
                engine: CityEngine::new(seed),
            }
        }

        #[wasm_bindgen]
        pub fn step(&mut self) {
            self.engine.step();
        }

        #[wasm_bindgen]
        pub fn buffer_ptr(&self) -> *const u32 {
            self.engine.buffer_ptr()
        }

        #[wasm_bindgen]
        pub fn buffer_size(&self) -> usize {
            BUFFER_SIZE * 4 // bytes
        }

        #[wasm_bindgen]
        pub fn move_forward(&mut self, distance: f32) {
            self.engine.move_forward(distance);
        }

        #[wasm_bindgen]
        pub fn rotate(&mut self, delta: f32) {
            self.engine.rotate(delta);
        }

        #[wasm_bindgen]
        pub fn set_camera(&mut self, x: f32, y: f32, angle: f32) {
            self.engine.set_camera(x, y, angle);
        }

        #[wasm_bindgen]
        pub fn camera_x(&self) -> f32 { self.engine.raycaster.camera.x }
        #[wasm_bindgen]
        pub fn camera_y(&self) -> f32 { self.engine.raycaster.camera.y }
        #[wasm_bindgen]
        pub fn camera_angle(&self) -> f32 { self.engine.raycaster.camera.angle }
        #[wasm_bindgen]
        pub fn frame_count(&self) -> u32 { self.engine.frame_count }
        #[wasm_bindgen]
        pub fn grid_width(&self) -> u8 { self.engine.grid.width }
        #[wasm_bindgen]
        pub fn grid_height(&self) -> u8 { self.engine.grid.height }

        #[wasm_bindgen]
        pub fn set_cell(&mut self, x: usize, y: usize, height: u8, cell_type: u8) {
            self.engine.set_cell(x, y, height, cell_type);
        }

        #[wasm_bindgen]
        pub fn verify_chain(&self) -> bool {
            self.engine.verify_chain()
        }

        #[wasm_bindgen]
        pub fn get_cell_height(&self, x: usize, y: usize) -> u8 {
            self.engine.grid.get(x, y).map(|c| c.height).unwrap_or(0)
        }

        #[wasm_bindgen]
        pub fn get_cell_type(&self, x: usize, y: usize) -> u8 {
            self.engine.grid.get(x, y).map(|c| c.cell_type).unwrap_or(0)
        }

        #[wasm_bindgen]
        pub fn cell_count(&self) -> usize {
            self.engine.grid.cells.len()
        }

        #[wasm_bindgen]
        pub fn grid_hash_first(&self) -> u64 {
            self.engine.grid.cells.first().map(|c| c.hash).unwrap_or(0)
        }

        #[wasm_bindgen]
        pub fn grid_hash_last(&self) -> u64 {
            self.engine.grid.cells.last().map(|c| c.hash).unwrap_or(0)
        }

        /// Get the average composite tournament score across the grid.
        #[wasm_bindgen]
        pub fn avg_tournament_score(&self) -> f32 {
            use crate::scoring::score_grid;
            let scores = score_grid(&self.engine.grid);
            if scores.is_empty() { return 0.0; }
            scores.iter().map(|s| s.composite).sum::<f32>() / scores.len() as f32
        }

        /// Get the composite score at a specific cell.
        /// Returns 0.0 if out of bounds.
        #[wasm_bindgen]
        pub fn cell_score(&self, x: usize, y: usize) -> f32 {
            use crate::scoring::score_grid;
            let scores = score_grid(&self.engine.grid);
            let idx = y * self.engine.grid.width as usize + x;
            scores.get(idx).map(|s| s.composite).unwrap_or(0.0)
        }

        /// Predict next cells the player will visit given velocity (vx, vy).
        /// Returns the cell height at the predicted position (0 = no building).
        /// -1 means invalid prediction.
        #[wasm_bindgen]
        pub fn predict_height(&self, x: f32, y: f32, vx: f32, vy: f32, steps_out: u32) -> i32 {
            use crate::jepa_predict::{JepaPredictor, Velocity};
            let predictor = JepaPredictor {
                look_ahead: steps_out.max(1) as usize,
                prediction_threshold: 0.0,
            };
            let velocity = Velocity { vx, vy };
            let preds = predictor.predict(&self.engine.grid, x, y, velocity);
            if let Some((px, py, _)) = preds.first() {
                self.engine.grid.get(*px, *py).map(|c| c.height as i32).unwrap_or(-1)
            } else {
                -1
            }
        }
    }
}
