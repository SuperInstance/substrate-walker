//! Tournament scoring demo.
//!
//! Inspired by kev-substrate-competition: each cell gets a composite score
//! based on chain integrity, type diversity, and walkability.
//! 
//! The composite metric: integrity × diversity × accessibility
//! Higher = better district for the player to visit.

use substrate_walker::{CityEngine, score_grid};

fn main() {
    let engine = CityEngine::new(42);
    
    println!("Substrate Walker — Tournament Scoring");
    println!("City: {}x{}, chain valid: {}", 
        engine.grid.width, engine.grid.height, 
        engine.verify_chain());
    println!();

    let scores = score_grid(&engine.grid);
    let total = scores.len();
    
    // Compute aggregate stats
    let avg_integrity: f32 = scores.iter().map(|s| s.integrity).sum::<f32>() / total as f32;
    let avg_diversity: f32 = scores.iter().map(|s| s.diversity).sum::<f32>() / total as f32;
    let avg_accessibility: f32 = scores.iter().map(|s| s.accessibility).sum::<f32>() / total as f32;
    let avg_composite: f32 = scores.iter().map(|s| s.composite).sum::<f32>() / total as f32;

    println!("=== Aggregate Stats ===");
    println!("Cells: {}", total);
    println!("Avg integrity:     {:.3}", avg_integrity);
    println!("Avg diversity:     {:.3}", avg_diversity);
    println!("Avg accessibility: {:.3}", avg_accessibility);
    println!("Avg composite:     {:.3}", avg_composite);
    println!();

    // Top 10 cells by composite score
    let mut indexed: Vec<(usize, f32)> = scores.iter().enumerate().map(|(i, s)| (i, s.composite)).collect();
    indexed.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());

    println!("=== Top 10 Districts (by composite score) ===");
    for (rank, (idx, score)) in indexed.iter().take(10).enumerate() {
        let cell = &engine.grid.cells[*idx];
        let s = &scores[*idx];
        println!("{:2}. ({:2},{:2}) h={:2} type={} comp={:.3} int={:.2} div={:.2} acc={:.2}",
            rank + 1, cell.x, cell.y, cell.height, cell.cell_type,
            score, s.integrity, s.diversity, s.accessibility);
    }
    
    println!();
    
    // Bottom 10
    println!("=== Bottom 10 Districts ===");
    for (rank, (idx, score)) in indexed.iter().rev().take(10).enumerate() {
        let cell = &engine.grid.cells[*idx];
        let s = &scores[*idx];
        println!("{:2}. ({:2},{:2}) h={:2} type={} comp={:.3} int={:.2} div={:.2} acc={:.2}",
            rank + 1, cell.x, cell.y, cell.height, cell.cell_type,
            score, s.integrity, s.diversity, s.accessibility);
    }
}
