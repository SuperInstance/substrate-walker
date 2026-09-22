//! Native example: renders the city to text.
//!
//! Run with: cargo run --example text_render

use substrate_walker::{CityEngine, SCREEN_HEIGHT, SCREEN_WIDTH};

fn main() {
    let mut engine = CityEngine::new(42);
    println!("Substrate Walker — Substrate Walker");
    println!("Grid: {}x{}, Screen: {}x{}", 
        engine.grid_dims().0, engine.grid_dims().1,
        SCREEN_WIDTH, SCREEN_HEIGHT);
    println!("Chain valid: {}", engine.verify_chain());
    println!();

    // Sample views
    let views: [(f32, f32, f32, &str); 4] = [
        (16.0, 16.0, 0.0, "Central Plaza, facing East"),
        (16.0, 16.0, std::f32::consts::PI / 2.0, "Central Plaza, facing North"),
        (5.0, 5.0, 0.0, "Skyscraper Alley, facing East"),
        (20.0, 20.0, std::f32::consts::PI * 0.75, "Wide open, facing SW"),
    ];

    for (x, y, angle, label) in views.iter() {
        engine.set_camera(*x, *y, *angle);
        engine.step();
        println!("=== {} ===", label);
        let ptr = engine.buffer_ptr();
        let buffer = unsafe {
            std::slice::from_raw_parts(ptr as *const u32, SCREEN_WIDTH * SCREEN_HEIGHT)
        };
        for sy in 0..SCREEN_HEIGHT {
            let mut line = String::new();
            for sx in 0..SCREEN_WIDTH {
                let cell = buffer[sy * SCREEN_WIDTH + sx];
                let glyph = (cell & 0xFF) as u8;
                line.push(if glyph == 0 { ' ' } else { glyph as char });
            }
            println!("{}", line);
        }
        println!();
    }
}
