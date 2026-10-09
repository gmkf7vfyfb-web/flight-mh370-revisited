//! Load a field cut to a window and report its size and load time; with `compare`, also load the
//! full manifest and check that 20,000 random queries inside the window agree exactly.
//!
//! cargo run --release -p mh370-ocean --example window_load -- <manifest> <lon_min> <lon_max> <lat_min> <lat_max> <t_start> <t_end> [compare]

use mh370_ocean::*;
use rand::{Rng, SeedableRng};
use std::time::Instant;

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let f = |i: usize| a[i].parse::<f64>().unwrap();
    let path = std::path::Path::new(&a[1]);
    let w = LoadWindow::new([f(2), f(3), f(4), f(5)], [f(6), f(7)]);
    let s = Instant::now();
    let win = GridField::load_window(path, &w).expect("window");
    let tw = s.elapsed().as_secs_f64();
    let (t, lo, la) = win.axes();
    print!("{{\"window_bytes\":{},\"load_s\":{tw:.2},\"slices\":{},\"nlon\":{},\"nlat\":{}", win.data_bytes(), t.len(), lo.len(), la.len());
    if a.len() > 8 {
        let s = Instant::now();
        let full = GridField::load_window(path, &LoadWindow::all()).expect("full");
        let tf = s.elapsed().as_secs_f64();
        let mut g = rand_chacha::ChaCha8Rng::seed_from_u64(3);
        let mut mismatch = 0;
        for _ in 0..20_000 {
            let p = [g.gen_range(f(2)..f(3)), g.gen_range(f(4)..f(5))];
            let tt = g.gen_range(f(6)..f(7));
            mismatch += (win.sample(tt, p) != full.sample(tt, p)) as usize;
        }
        print!(",\"full_bytes\":{},\"full_load_s\":{tf:.2},\"mismatches_of_20000\":{mismatch}", full.data_bytes());
    }
    println!("}}");
}
