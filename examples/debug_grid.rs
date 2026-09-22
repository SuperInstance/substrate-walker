use substrate_walker::{CityEngine, CityGrid};

fn main() {
    let grid = CityGrid::generate_city(42);
    println!("Grid at (15..18, 15..18):");
    for y in 15..18 {
        for x in 15..18 {
            if let Some(cell) = grid.get(x as usize, y as usize) {
                print!("({},{}): h={} type={} ", x, y, cell.height, cell.cell_type);
            }
        }
        println!();
    }
    println!("\nGrid at (16, 16):");
    if let Some(cell) = grid.get(16, 16) {
        println!("height={} is_solid={}", cell.height, cell.is_solid());
    }
    
    // Center cell (16,16)
    let mut engine = CityEngine::empty(32, 32);
    // Set just a few buildings around
    engine.set_cell(15, 15, 20, 0);
    engine.set_cell(17, 15, 20, 1);
    engine.set_cell(15, 17, 20, 2);
    engine.set_cell(17, 17, 20, 3);
    engine.set_cell(20, 16, 5, 0);
    
    engine.set_camera(16.0, 16.0, 0.0);
    engine.step();
    
    println!("\nTest render with sparse buildings:");
    let ptr = engine.buffer_ptr();
    let buffer = unsafe {
        std::slice::from_raw_parts(ptr as *const u32, 160 * 60)
    };
    for sy in 0..60 {
        let mut line = String::new();
        for sx in 0..160 {
            let cell = buffer[sy * 160 + sx];
            let glyph = (cell & 0xFF) as u8;
            line.push(if glyph == 0 { ' ' } else { glyph as char });
        }
        println!("{}", line);
    }
}
