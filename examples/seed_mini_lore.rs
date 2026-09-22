//! CLI tool to generate lore snippets using seed-mini patterns
//!
//! Run with: cargo run --release --example seed_mini_lore -- 5
//!
//! This demonstrates the cache + sequential pattern: each generation
//! builds on the previous output (the "thread" pattern).

use std::time::Duration;

fn main() {
    let n: usize = std::env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(5);

    println!("Substrate Walker — Seed-Mini Lore Generator");
    println!("Generating {} sequential building names", n);
    println!("Pattern: each builds on the thread (like DeepSeek iterative)");
    println!();

    // Simulated lore thread
    let mut thread: Vec<String> = Vec::new();
    
    // Themes to anchor the thread (cyberpunk noir)
    let themes = [
        "neon-soaked",
        "memory-debt",
        "ghost-in-the-shell",
        "feral-substrate",
        "substrate-tower",
        "rain-slicked",
        "witness-block",
        "doctrine-vault",
        "canon-spire",
        "perceptor-station",
    ];

    for i in 0..n {
        let theme = themes[i % themes.len()];
        let height = (3 + (i * 7) % 30) as u8;
        let cell_id = i as u32;
        
        // Each generation builds on the thread
        let prior = thread.last().map(|s| s.as_str()).unwrap_or("");
        let name = if i == 0 {
            format!("{} {}", theme, cell_id)
        } else {
            // Each name references the previous (cache-friendly)
            format!("{} of {}", theme, prior.split_whitespace().last().unwrap_or("the"))
        };

        thread.push(name.clone());
        
        println!("Step {}: cell={} h={} → '{}'", i, cell_id, height, name);
        std::thread::sleep(Duration::from_millis(50));
    }

    println!("\n=== Thread (one generation builds on prior) ===");
    for (i, name) in thread.iter().enumerate() {
        println!("  {} → {}", i, name);
    }
}
