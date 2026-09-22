use substrate_walker::{CityEngine, CityGrid, SCREEN_WIDTH, SCREEN_HEIGHT};

fn main() {
    let grid = CityGrid::generate_city(42);
    let mut engine = CityEngine::new(42);
    engine.set_camera(16.0, 16.0, 0.0);
    
    // Manually trace one column
    let half_fov = engine.raycaster.camera.fov * 0.5;
    let sx = 80;
    let ray_angle = engine.raycaster.camera.angle - half_fov
        + (sx as f32 / SCREEN_WIDTH as f32) * engine.raycaster.camera.fov;
    
    println!("Camera at ({}, {}) facing angle={}, ray_angle={}",
        engine.raycaster.camera.x,
        engine.raycaster.camera.y,
        engine.raycaster.camera.angle,
        ray_angle);
    
    let eye_x = ray_angle.sin();
    let eye_y = ray_angle.cos();
    
    println!("eye=({}, {})", eye_x, eye_y);
    
    let mut distance = 0.05_f32;
    let mut hit_height = 0.0;
    while distance < engine.raycaster.camera.max_distance {
        distance += 0.05;
        let test_x = (engine.raycaster.camera.x + eye_x * distance) as i32;
        let test_y = (engine.raycaster.camera.y + eye_y * distance) as i32;
        if let Some(cell) = grid.get(test_x as usize, test_y as usize) {
            if cell.is_solid() {
                hit_height = cell.height_f32();
                println!("HIT at distance {} at ({}, {}), height={}", distance, test_x, test_y, hit_height);
                break;
            }
        }
    }
    
    let angle_delta = ray_angle - engine.raycaster.camera.angle;
    let corrected = distance * angle_delta.cos();
    println!("corrected distance: {}", corrected);
    
    let effective_height = hit_height.max(1.0) * 2.0;
    let wall_height = ((effective_height * SCREEN_HEIGHT as f32) / (corrected * 8.0).max(0.5)) as i32;
    let wall_top = if wall_height >= SCREEN_HEIGHT as i32 {
        0
    } else {
        (SCREEN_HEIGHT as i32 - wall_height) / 2
    };
    let wall_bottom = SCREEN_HEIGHT as i32 - wall_top;
    
    println!("wall_height={}, wall_top={}, wall_bottom={}", wall_height, wall_top, wall_bottom);
}
