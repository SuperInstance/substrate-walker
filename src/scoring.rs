//! Tournament scoring for substrate cells.
//!
//! Inspired by kev-substrate-competition:
//! - Each cell has a "calibration" score
//! - Composite metric: prev_hash_integrity × cell_type_balance / cost
//! - Cells with higher scores are "better districts"

use crate::cell::CityGrid;

#[derive(Debug, Clone, Copy)]
pub struct CellScore {
    pub integrity: f32,    // 0..1, hash chain integrity
    pub diversity: f32,    // 0..1, cell type mix
    pub accessibility: f32, // 0..1, walkable from camera
    pub composite: f32,    // Combined score
}

impl CellScore {
    pub fn neutral() -> Self {
        Self {
            integrity: 0.5,
            diversity: 0.5,
            accessibility: 0.5,
            composite: 0.5,
        }
    }
}

/// Score the entire city grid.
pub fn score_grid(grid: &CityGrid) -> Vec<CellScore> {
    grid.cells.iter().enumerate().map(|(idx, cell)| {
        // Integrity: prev_hash matches previous cell's hash
        let prev_hash = if idx > 0 { grid.cells[idx - 1].hash } else { 0 };
        let integrity = if cell.prev_hash == prev_hash { 1.0 } else { 0.0 };

        // Diversity: cell_type contributes to mix
        let diversity = match cell.cell_type {
            0 | 1 | 2 | 3 => 1.0, // Known type
            _ => 0.0,            // Unknown
        };

        // Accessibility: cells with neighbors that are empty are more walkable
        let x = cell.x as usize;
        let y = cell.y as usize;
        let accessible_neighbors = [
            grid.get(x.wrapping_sub(1), y),
            grid.get(x + 1, y),
            grid.get(x, y.wrapping_sub(1)),
            grid.get(x, y + 1),
        ].iter().filter(|c| {
            c.map(|c| !c.is_solid()).unwrap_or(false)
        }).count() as f32 / 4.0;

        // Composite: integrity * diversity * accessibility
        let composite = (integrity + diversity + accessible_neighbors) / 3.0;

        CellScore {
            integrity,
            diversity,
            accessibility: accessible_neighbors,
            composite,
        }
    }).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_neutral_score() {
        let s = CellScore::neutral();
        assert_eq!(s.composite, 0.5);
    }

    #[test]
    fn test_score_grid() {
        let mut grid = CityGrid::new(8, 8);
        for x in 0..8 {
            for y in 0..8 {
                grid.set(x, y, ((x + y) % 5) as u8, (x % 4) as u8);
            }
        }
        let scores = score_grid(&grid);
        assert_eq!(scores.len(), 64);
        // All scores should have full integrity (chain was just built)
        for s in &scores {
            assert_eq!(s.integrity, 1.0);
        }
    }

    #[test]
    fn test_corner_cell_score() {
        let mut grid = CityGrid::new(4, 4);
        // All corners are buildings
        grid.set(0, 0, 5, 0);
        grid.set(3, 0, 5, 0);
        grid.set(0, 3, 5, 0);
        grid.set(3, 3, 5, 0);
        // Center is empty
        grid.set(1, 1, 0, 0);
        grid.set(2, 1, 0, 0);
        grid.set(1, 2, 0, 0);
        grid.set(2, 2, 0, 0);

        let scores = score_grid(&grid);
        // Center cells should have high accessibility (4 empty neighbors)
        let center_score = scores[1 * 4 + 1]; // (1, 1)
        assert!(center_score.accessibility > 0.5, "Center should be accessible: {}", center_score.accessibility);
    }
}
