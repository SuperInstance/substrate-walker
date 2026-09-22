//! Substrate cell as a city building.
//!
//! Each cell in the Quilt substrate becomes a building in the city city.
//! The cell carries:
//! - id (canonical)
//! - prev_hash (chain link)
//! - height (building height)
//! - cell_type (doctrine / witness / canon / perception)
//! - content_preview (first 200 bytes of content)

use alloc::vec::Vec;

use crate::types::{fnv1a_64, PackedCell};

/// A substrate cell representing a building in the city.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CityCell {
    pub x: u8,
    pub y: u8,
    pub height: u8,
    pub cell_type: u8, // 0=doctrine, 1=witness, 2=canon, 3=perception
    pub prev_hash: u64,
    pub hash: u64,
    pub metadata: u16, // For type-specific data
}

impl CityCell {
    /// Create an empty cell with a deterministic hash based on (x, y).
    pub fn empty(x: u8, y: u8) -> Self {
        let canonical: [u8; 4] = [x, y, 0, 0];
        let hash = crate::types::fnv1a_64(&canonical);
        Self {
            x,
            y,
            height: 0,
            cell_type: 0,
            prev_hash: 0,
            hash,
            metadata: 0,
        }
    }

    /// Compute the cell's hash from its content + prev_hash.
    pub fn compute_hash(&mut self) {
        let canonical: [u8; 12] = [
            self.x, self.y, self.height, self.cell_type,
            (self.prev_hash & 0xFF) as u8,
            ((self.prev_hash >> 8) & 0xFF) as u8,
            ((self.prev_hash >> 16) & 0xFF) as u8,
            ((self.prev_hash >> 24) & 0xFF) as u8,
            (self.metadata & 0xFF) as u8,
            ((self.metadata >> 8) & 0xFF) as u8,
            ((self.hash & 0xFF) as u8), // placeholder
            0,
        ];
        self.hash = fnv1a_64(&canonical);
    }

    /// Check if this cell is solid (a building, not empty space).
    pub fn is_solid(&self) -> bool {
        self.height > 0
    }

    /// Get the height as a float (for raycasting).
    pub fn height_f32(&self) -> f32 {
        self.height as f32
    }

    /// Encode the cell type as a color channel hint.
    pub fn color_hint(&self) -> (u8, u8, u8) {
        match self.cell_type {
            0 => (0xFF, 0x80, 0xFF), // doctrine = neon violet
            1 => (0x80, 0xFF, 0x80), // witness = neon green
            2 => (0xFF, 0xFF, 0x80), // canon = neon yellow
            3 => (0x80, 0xFF, 0xFF), // perception = cyan
            _ => (0xFF, 0xFF, 0xFF), // unknown = white
        }
    }
}

/// A 2D grid of city cells.
#[derive(Debug, Clone)]
pub struct CityGrid {
    pub width: u8,
    pub height: u8,
    pub cells: Vec<CityCell>,
}

impl CityGrid {
    /// Create a new grid filled with empty cells.
    ///
    /// The empty cells form an FNV-1a 64-bit prev_hash chain across the grid
    /// in row-major order (cell at index `i` has prev_hash = cell at index `i-1`.hash).
    /// Empty cells still have non-zero hashes (deterministic per (x,y)).
    pub fn new(width: u8, height: u8) -> Self {
        let mut cells = Vec::with_capacity((width as usize) * (height as usize));
        let mut prev_hash: u64 = 0;
        for y in 0..height {
            for x in 0..width {
                let canonical: [u8; 12] = [
                    x, y, 0, 0,
                    (prev_hash & 0xFF) as u8,
                    ((prev_hash >> 8) & 0xFF) as u8,
                    ((prev_hash >> 16) & 0xFF) as u8,
                    ((prev_hash >> 24) & 0xFF) as u8,
                    0, 0, 0, 0,
                ];
                let hash = crate::types::fnv1a_64(&canonical);
                cells.push(CityCell {
                    x,
                    y,
                    height: 0,
                    cell_type: 0,
                    prev_hash,
                    hash,
                    metadata: 0,
                });
                prev_hash = hash;
            }
        }
        Self { width, height, cells }
    }

    /// Get cell at (x, y) or None if out of bounds.
    pub fn get(&self, x: usize, y: usize) -> Option<&CityCell> {
        if x >= self.width as usize || y >= self.height as usize {
            return None;
        }
        self.cells.get(y * self.width as usize + x)
    }

    /// Set cell at (x, y) and recompute the FNV-1a chain from this point on.
    pub fn set(&mut self, x: usize, y: usize, height: u8, cell_type: u8) {
        if x >= self.width as usize || y >= self.height as usize {
            return;
        }
        let idx = y * self.width as usize + x;

        // Update the cell itself
        let prev_hash = if idx > 0 { self.cells[idx - 1].hash } else { 0 };
        let canonical: [u8; 12] = [
            x as u8, y as u8, height, cell_type,
            (prev_hash & 0xFF) as u8,
            ((prev_hash >> 8) & 0xFF) as u8,
            ((prev_hash >> 16) & 0xFF) as u8,
            ((prev_hash >> 24) & 0xFF) as u8,
            0, 0, 0, 0,
        ];
        let hash = crate::types::fnv1a_64(&canonical);
        self.cells[idx] = CityCell {
            x: x as u8,
            y: y as u8,
            height,
            cell_type,
            prev_hash,
            hash,
            metadata: 0,
        };

        // Recompute the chain from idx+1 onwards
        let mut current_prev = hash;
        for i in (idx + 1)..self.cells.len() {
            let c = self.cells[i];
            let canonical: [u8; 12] = [
                c.x, c.y, c.height, c.cell_type,
                (current_prev & 0xFF) as u8,
                ((current_prev >> 8) & 0xFF) as u8,
                ((current_prev >> 16) & 0xFF) as u8,
                ((current_prev >> 24) & 0xFF) as u8,
                (c.metadata & 0xFF) as u8,
                ((c.metadata >> 8) & 0xFF) as u8,
                0, 0,
            ];
            let new_hash = crate::types::fnv1a_64(&canonical);
            self.cells[i] = CityCell {
                x: c.x,
                y: c.y,
                height: c.height,
                cell_type: c.cell_type,
                prev_hash: current_prev,
                hash: new_hash,
                metadata: c.metadata,
            };
            current_prev = new_hash;
        }
    }

    /// Verify the prev_hash chain across all cells.
    pub fn verify_chain(&self) -> bool {
        let mut prev_hash: u64 = 0;
        for (i, cell) in self.cells.iter().enumerate() {
            if cell.prev_hash != prev_hash {
                return false;
            }
            prev_hash = cell.hash;
        }
        true
    }

    /// Generate a procedural city city layout.
    ///
    /// Buildings cluster in districts with random heights. The pattern is
    /// deterministic (seeded) so we can verify reproducibility.
    pub fn generate_city(seed: u32) -> Self {
        let width = 32u8;
        let height = 32u8;
        let mut grid = Self::new(width, height);

        // Simple xorshift32 PRNG for reproducibility
        let mut state = seed;
        let mut rand = || -> u32 {
            state ^= state << 13;
            state ^= state >> 17;
            state ^= state << 5;
            state
        };

        // Skyline density (every ~5 cells has a building)
        for y in 0..height {
            for x in 0..width {
                let r = rand() % 100;
                let cell_type = ((x as u32 + y as u32) % 4) as u8; // Distribute cell types
                
                if r < 25 {
                    // Tall skyscraper (10-30 units)
                    let h = (10 + (rand() % 20)) as u8;
                    grid.set(x as usize, y as usize, h, cell_type);
                } else if r < 50 {
                    // Mid-rise (3-9 units)
                    let h = (3 + (rand() % 7)) as u8;
                    grid.set(x as usize, y as usize, h, cell_type);
                }
                // else: empty street (height = 0) — 50% empty
            }
        }

        // Add a "central plaza" — short cells, type=canon
        // Camera spawns here, so leave the immediate cells low/short
        for x in 14..18 {
            for y in 14..18 {
                // Edge of plaza is taller (witness)
                if x == 14 || x == 17 || y == 14 || y == 17 {
                    grid.set(x as usize, y as usize, 2, 1);
                } else {
                    grid.set(x as usize, y as usize, 1, 2);
                }
            }
        }

        // Mark cells around spawn as empty (camera area)
        // Actually keep them short so we don't get blocked in
        for x in 12..20 {
            for y in 12..20 {
                if !((14..18).contains(&x) && (14..18).contains(&y)) {
                    // Already set above
                }
            }
        }

        grid
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::verify_canary;

    #[test]
    fn test_canary() {
        assert!(verify_canary());
    }

    #[test]
    fn test_empty_grid() {
        let grid = CityGrid::new(4, 4);
        assert_eq!(grid.cells.len(), 16);
        assert!(grid.verify_chain());
    }

    #[test]
    fn test_set_cell() {
        let mut grid = CityGrid::new(4, 4);
        grid.set(1, 1, 5, 0);
        let cell = grid.get(1, 1).unwrap();
        assert_eq!(cell.height, 5);
        assert!(cell.hash != 0);
    }

    #[test]
    fn test_chain_integrity() {
        let mut grid = CityGrid::new(8, 8);
        for i in 0..8 {
            for j in 0..8 {
                grid.set(i, j, ((i + j) % 5) as u8, (i % 4) as u8);
            }
        }
        assert!(grid.verify_chain());
    }

    #[test]
    fn test_city_generation() {
        let grid = CityGrid::generate_city(42);
        assert_eq!(grid.width, 32);
        assert_eq!(grid.height, 32);
        // Should have some buildings
        let solid_count = grid.cells.iter().filter(|c| c.is_solid()).count();
        assert!(solid_count > 100, "Cyberpunk city should have buildings (got {})", solid_count);
        assert!(grid.verify_chain());
    }

    #[test]
    fn test_color_hints() {
        let mut grid = CityGrid::new(2, 2);
        grid.set(0, 0, 10, 0);
        grid.set(1, 0, 10, 1);
        grid.set(0, 1, 10, 2);
        grid.set(1, 1, 10, 3);
        assert_eq!(grid.cells[0].color_hint(), (0xFF, 0x80, 0xFF));
        assert_eq!(grid.cells[1].color_hint(), (0x80, 0xFF, 0x80));
    }
}
