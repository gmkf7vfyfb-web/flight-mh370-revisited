//! Load a gridded forcing (part or series manifest) and print its axes, time gaps and a few samples,
//! as a check that a prepared product is what its manifest says.
//!
//! cargo run -p mh370-ocean --release --example forcing_check -- <manifest>

use mh370_ocean::*;

fn main() {
    let path = std::path::PathBuf::from(std::env::args().nth(1).expect("manifest"));
    let g = if path.to_string_lossy().ends_with(".series.json") { GridField::load_series(&path) } else { GridField::load(&path) }.expect("load");
    let (t, lon, lat) = g.axes();
    let max_gap = t.windows(2).map(|w| w[1] - w[0]).fold(0.0, f64::max) / 3600.0;
    let min_gap = t.windows(2).map(|w| w[1] - w[0]).fold(f64::INFINITY, f64::min) / 3600.0;
    println!("product {} component {:?} times {} first {} last {} step_h [{min_gap}, {max_gap}] lon [{}, {}] x{} lat [{}, {}] x{}",
        g.meta().product, g.meta().component, t.len(), t[0], t[t.len() - 1], lon[0], lon[lon.len() - 1], lon.len(), lat[0], lat[lat.len() - 1], lat.len());
    let when = 1_435_752_000.0; // 2015-07-01T12:00Z
    for (name, p) in [("MH370 arc 35S 95E", [95.0, -35.0]), ("off Reunion 21.5S 55E", [55.0, -21.5]), ("Agulhas 37S 30E", [30.0, -37.0]), ("inland Madagascar", [46.5, -19.0])] {
        println!("{name}: {:?}", g.sample(when, p));
    }
}
