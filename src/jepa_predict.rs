//! JEPA-style next-cell prediction.
//!
//! Like the human visual cortex predicts what you'll see before you turn your
//! head, this module predicts the next cell(s) the player will encounter and
//! pre-generates their lore.
//!
//! The prediction is simple: based on velocity vector, look ahead 1-3 cells
//! in the player's direction of motion and pre-fetch lore.

use alloc::vec::Vec;

use crate::cell::CityGrid;

#[derive(Debug, Clone, Copy)]
pub struct Velocity {
    pub vx: f32,
    pub vy: f32,
}

impl Velocity {
    pub fn zero() -> Self {
        Self { vx: 0.0, vy: 0.0 }
    }

    pub fn is_moving(&self) -> bool {
        self.vx.abs() > 0.01 || self.vy.abs() > 0.01
    }

    /// Normalized direction vector
    pub fn direction(&self) -> (f32, f32) {
        let mag = (self.vx * self.vx + self.vy * self.vy).sqrt();
        if mag < 0.001 {
            (0.0, 0.0)
        } else {
            (self.vx / mag, self.vy / mag)
        }
    }
}

/// Predictor that estimates the next cells the player will visit.
pub struct JepaPredictor {
    pub look_ahead: usize,
    pub prediction_threshold: f32,
}

impl Default for JepaPredictor {
    fn default() -> Self {
        Self {
            look_ahead: 3,
            prediction_threshold: 0.5,
        }
    }
}

impl JepaPredictor {
    /// Predict the next N cells the player will visit.
    pub fn predict(
        &self,
        grid: &CityGrid,
        x: f32,
        y: f32,
        velocity: Velocity,
    ) -> Vec<(usize, usize, f32)> {
        if !velocity.is_moving() {
            return Vec::new();
        }

        let (dx, dy) = velocity.direction();
        let mut predictions = Vec::with_capacity(self.look_ahead);

        for i in 1..=self.look_ahead {
            let distance = i as f32;
            let pred_x = x + dx * distance;
            let pred_y = y + dy * distance;

            let confidence = 1.0 - (i as f32 / self.look_ahead as f32) * 0.5;

            if confidence < self.prediction_threshold {
                break;
            }

            let px = pred_x.round() as usize;
            let py = pred_y.round() as usize;

            if let Some(cell) = grid.get(px, py) {
                if cell.is_solid() {
                    predictions.push((px, py, confidence));
                }
            }
        }

        predictions
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_velocity_zero() {
        let v = Velocity::zero();
        assert!(!v.is_moving());
    }

    #[test]
    fn test_velocity_moving() {
        let v = Velocity { vx: 1.0, vy: 0.0 };
        assert!(v.is_moving());
    }

    #[test]
    fn test_velocity_direction() {
        let v = Velocity { vx: 3.0, vy: 4.0 };
        let (dx, dy) = v.direction();
        assert!((dx - 0.6).abs() < 0.01);
        assert!((dy - 0.8).abs() < 0.01);
    }

    #[test]
    fn test_predictor_idle() {
        let grid = CityGrid::new(32, 32);
        let predictor = JepaPredictor::default();
        let preds = predictor.predict(&grid, 16.0, 16.0, Velocity::zero());
        assert_eq!(preds.len(), 0);
    }

    #[test]
    fn test_predictor_moving() {
        let mut grid = CityGrid::new(32, 32);
        for x in 18..22 {
            grid.set(x, 16, 5, 0);
        }

        let predictor = JepaPredictor::default();
        let velocity = Velocity { vx: 1.0, vy: 0.0 };
        let preds = predictor.predict(&grid, 16.0, 16.0, velocity);

        assert!(preds.len() > 0);
        if let Some((x, y, _)) = preds.first() {
            assert_eq!(*x, 18);
            assert_eq!(*y, 16);
        }
    }
}
