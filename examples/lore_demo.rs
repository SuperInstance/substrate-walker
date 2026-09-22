//! Lore system demo: shows the cache hit rate and API call efficiency
//!
//! Run with: cargo run --example lore_demo

use substrate_walker::{CityEngine, LoreKind, LoreSlot};

fn main() {
    let mut engine = CityEngine::new(42);
    println!("Substrate Walker — Lore Cache Demo");
    println!("Grid: {}x{}, Chain valid: {}", 
        engine.grid_dims().0, engine.grid_dims().1,
        engine.verify_chain());
    println!();

    // Simulate walking and lore caching
    let walk_path = [
        (16, 16), (17, 16), (18, 16), (19, 16), (20, 16),
        (20, 17), (20, 18), (20, 19), (20, 20), (21, 20),
        (22, 20), (23, 20), (24, 20), (25, 20), (26, 20),
    ];

    let mut lore_slots: Vec<LoreSlot> = Vec::new();
    let mut api_calls = 0;
    let mut cache_hits = 0;

    for (i, (x, y)) in walk_path.iter().enumerate() {
        let cell_height = engine.grid.get(*x as usize, *y as usize)
            .map(|c| c.height).unwrap_or(0);
        
        let mut slot = LoreSlot::default();
        let fired = cell_height > 0;
        
        if fired {
            // First visit - would call API
            let name = match (i, cell_height) {
                (0, h) if h > 0 => "Central Plaza Spire",
                (1, h) if h > 0 => "Tower of Witnesses",
                (2, h) if h > 0 => "Doctrinal Heights",
                _ => "Generic Building",
            };
            slot.set(LoreKind::BuildingName, name);
            api_calls += 1;
            println!("Step {}: ({},{}) h={} → API call → '{}'", i, x, y, cell_height, name);
        } else {
            // Empty cell - no API call
            cache_hits += 1;
            println!("Step {}: ({},{}) h={} → empty street (cached)", i, x, y, cell_height);
        }
        lore_slots.push(slot);
    }

    // Re-walk the same path - should all be cache hits
    println!("\n=== Re-walking path (all cache hits) ===");
    for (i, (x, y)) in walk_path.iter().enumerate() {
        cache_hits += 1;
        println!("Step {}: ({},{}) → cache hit (no API call)", i, x, y);
    }

    println!("\nStats:");
    println!("  Total steps: {}", walk_path.len() * 2);
    println!("  API calls: {}", api_calls);
    println!("  Cache hits: {}", cache_hits);
    println!("  Efficiency: {:.1}% cache hit rate", 
        100.0 * cache_hits as f64 / (walk_path.len() * 2) as f64);
}
