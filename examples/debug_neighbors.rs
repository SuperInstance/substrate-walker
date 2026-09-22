use substrate_walker::{CityGrid};

fn main() {
    let grid = CityGrid::generate_city(42);
    println!("Cells around (16, 16):");
    for y in 14..20 {
        for x in 14..20 {
            if let Some(cell) = grid.get(x as usize, y as usize) {
                print!("({:2},{:2}):h={:2} ", x, y, cell.height);
            } else {
                print!("(???)     ");
            }
        }
        println!();
    }
}
