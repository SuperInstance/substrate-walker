//! Integration tests for substrate-walker.
//!
//! These tests verify the full pipeline: cell → grid → raycaster → buffer.

use substrate_walker::{verify_canary, CityEngine, CityGrid, LoreSlot, LoreKind};

#[test]
fn test_canary_matches_fleet() {
    assert!(verify_canary());
}

#[test]
fn test_engine_lifecycle() {
    let mut engine = CityEngine::new(42);
    assert_eq!(engine.grid.width, 32);
    assert!(engine.verify_chain());

    // Step multiple times
    for _ in 0..10 {
        engine.step();
    }
    assert_eq!(engine.frame_count, 10);
}

#[test]
fn test_camera_movement() {
    let mut engine = CityEngine::new(42);
    let (x0, y0, a0) = engine.camera_state();

    engine.rotate(std::f32::consts::PI / 4.0);
    engine.move_forward(5.0);

    let (x1, y1, a1) = engine.camera_state();
    assert_ne!(x0, x1);
    assert_ne!(y0, y1);
    assert!((a1 - a0 - std::f32::consts::PI / 4.0).abs() < 0.01);
}

#[test]
fn test_chain_integrity_after_moves() {
    let mut engine = CityEngine::new(42);
    assert!(engine.verify_chain());

    // Move around
    for _ in 0..100 {
        engine.move_forward(0.1);
    }
    assert!(engine.verify_chain());
}

#[test]
fn test_chain_integrity_after_cell_edits() {
    let mut engine = CityEngine::new(42);
    let initial_chain = engine.verify_chain();

    // Edit several cells
    engine.set_cell(5, 5, 20, 0);
    engine.set_cell(10, 10, 15, 1);
    engine.set_cell(15, 15, 10, 2);
    engine.set_cell(20, 20, 25, 3);

    assert_eq!(initial_chain, true);
    assert!(engine.verify_chain());
}

#[test]
fn test_lore_slot_basic() {
    let mut slot = LoreSlot::default();
    assert!(slot.is_empty());

    slot.set(LoreKind::BuildingName, "Tower of Memory");
    assert!(!slot.is_empty());
    assert_eq!(slot.kind, LoreKind::BuildingName);
    assert_eq!(slot.get().as_deref(), Some("Tower of Memory"));
}

#[test]
fn test_lore_slot_truncation() {
    let mut slot = LoreSlot::default();
    let long = "This is a very long building description that exceeds sixty-four bytes in total length";
    slot.set(LoreKind::DistrictName, long);
    let stored = slot.get().unwrap();
    assert_eq!(stored.len(), 64);
}

#[test]
fn test_lore_slot_kind_variants() {
    let mut slot = LoreSlot::default();
    let kinds = [
        (LoreKind::BuildingName, "Tower"),
        (LoreKind::DistrictName, "District"),
        (LoreKind::WitnessNote, "Note"),
        (LoreKind::CanonQuote, "Quote"),
        (LoreKind::Perception, "Percept"),
    ];

    for (kind, text) in &kinds {
        slot.set(*kind, text);
        assert_eq!(slot.kind, *kind);
        assert_eq!(slot.get().as_deref(), Some(*text));
    }
}

#[test]
fn test_grid_get_out_of_bounds() {
    let grid = CityGrid::new(8, 8);
    assert!(grid.get(7, 7).is_some());
    assert!(grid.get(8, 7).is_none());
    assert!(grid.get(7, 8).is_none());
    assert!(grid.get(0, 0).is_some());
}

#[test]
fn test_grid_set_out_of_bounds_is_safe() {
    let mut grid = CityGrid::new(8, 8);
    grid.set(10, 10, 5, 0); // Should not panic
    assert!(grid.get(8, 8).is_none());
    assert!(grid.verify_chain()); // Chain should still be valid
}

#[test]
fn test_cyberpunk_seed_determinism() {
    let grid1 = CityGrid::generate_city(42);
    let grid2 = CityGrid::generate_city(42);

    assert_eq!(grid1.width, grid2.width);
    assert_eq!(grid1.height, grid2.height);
    assert_eq!(grid1.cells.len(), grid2.cells.len());

    for (c1, c2) in grid1.cells.iter().zip(grid2.cells.iter()) {
        assert_eq!(c1.height, c2.height);
        assert_eq!(c1.cell_type, c2.cell_type);
        assert_eq!(c1.hash, c2.hash);
    }
}

#[test]
fn test_different_seeds_different_cities() {
    let grid1 = CityGrid::generate_city(42);
    let grid2 = CityGrid::generate_city(99);

    // At least one cell should differ
    let differs = grid1.cells.iter()
        .zip(grid2.cells.iter())
        .any(|(c1, c2)| c1.height != c2.height || c1.cell_type != c2.cell_type);
    assert!(differs, "Different seeds should produce different cities");
}
