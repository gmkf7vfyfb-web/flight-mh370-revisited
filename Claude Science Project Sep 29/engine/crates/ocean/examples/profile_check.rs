//! Print a GLORYS12 `GridProfile` column (and its TEOS-10 density and sound speed) at one point and
//! time, as JSON, for cross-checks against the netCDF and for settling.
//!
//! cargo run --release -p mh370-ocean --example profile_check -- <profile.json> <unix_s> <lon> <lat>

use mh370_ocean::*;

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let g = GridProfile::load(std::path::Path::new(&a[1])).expect("load");
    let (t, lon, lat): (f64, f64, f64) = (a[2].parse().unwrap(), a[3].parse().unwrap(), a[4].parse().unwrap());
    let p = g.profile(t, [lon, lat]).expect("profile");
    let te = p.teos10().expect("teos10");
    println!("{}", serde_json::json!({"profile": p, "rho": te.in_situ_density_kg_m3, "c": te.sound_speed_m_s}));
}
