//! Load the GSHHG full-resolution coastline over the default box and report what a consumer needs
//! to trust it: load time, cell census, named-segment runs, the line and chainage of each point
//! given on the command line (lon,lat pairs, e.g. debris finds), and a timing of `first_crossing`
//! and `is_land` on random short steps in the drift domain.
//!
//! `cargo run --release -p mh370-ocean --example coast_check -- <gshhs_f.b> [lon,lat[,label]] ...`

use mh370_ocean::{g1_segments, Coastline, PolygonCoast, PolygonCoastOptions};
use rand::{Rng, SeedableRng};
use std::time::Instant;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let path = std::path::Path::new(&args[1]);
    let t0 = Instant::now();
    let c = PolygonCoast::from_gshhg(path, g1_segments(), PolygonCoastOptions::default()).expect("load");
    let load_s = t0.elapsed().as_secs_f64();
    let census = c.cell_census();
    let segs = c.segments();
    let named: Vec<_> = segs.iter().filter(|s| s.segment < 100).collect();
    let n_vertices: usize = c.ring_infos().iter().map(|r| r.vertices).sum();
    println!("{{\"label\": {:?}, \"load_s\": {load_s:.2}, \"rings\": {}, \"vertices\": {n_vertices}, \"cells_coastal_land_sea\": {census:?}, \"segments\": {}, \"unnamed_max_id\": {}}}",
        c.label(), c.ring_infos().len(), segs.len(), segs.iter().map(|s| s.segment).max().unwrap_or(0));
    for s in &named {
        let ri = c.ring_index(s.line).unwrap();
        let r = &c.ring_infos()[ri];
        println!("named segment {} line {} (ring {} vertices, {:.1} km): {:.1}-{:.1} km ({:.1} km)", s.segment, s.line, r.vertices, r.length_m / 1e3, s.start_m / 1e3, s.end_m / 1e3, (s.end_m - s.start_m) / 1e3);
    }
    for a in &args[2..] {
        let v: Vec<&str> = a.split(',').collect();
        let p = [v[0].parse::<f64>().unwrap(), v[1].parse::<f64>().unwrap()];
        let land = c.is_land(p);
        match c.locate(p, 50_000.0) {
            Some(h) => println!("{:<40} {:>10.5} {:>10.5} land={land} segment={} line={} chainage_km={:.3} dist_m={:.0}", v.get(2).unwrap_or(&""), p[0], p[1], h.segment, h.line, h.chainage_m / 1e3, h.snapped_m),
            None => println!("{:<40} {:>10.5} {:>10.5} land={land} no shore within 50 km", v.get(2).unwrap_or(&""), p[0], p[1]),
        }
    }
    // Timing: 1e6 random 3 km steps in 15-120 E, 50-0 S.
    let mut g = rand_chacha::ChaCha8Rng::seed_from_u64(1);
    let steps: Vec<([f64; 2], [f64; 2])> = (0..1_000_000)
        .map(|_| {
            let p = [g.gen_range(15.0..120.0), g.gen_range(-50.0..0.0)];
            let a: f64 = g.gen_range(0.0..std::f64::consts::TAU);
            (p, [p[0] + 0.027 * a.cos() / (p[1] as f64).to_radians().cos(), p[1] + 0.027 * a.sin()])
        })
        .collect();
    let t1 = Instant::now();
    let land = steps.iter().filter(|s| c.is_land(s.0)).count();
    let t_land = t1.elapsed().as_secs_f64();
    let t2 = Instant::now();
    let hits = steps.iter().filter(|s| c.first_crossing(s.0, s.1).is_some()).count();
    let t_cross = t2.elapsed().as_secs_f64();
    println!("random points: land fraction {:.4}; is_land {:.0} ns/call; first_crossing {:.0} ns/call, {} hits", land as f64 / 1e6, t_land * 1e3, t_cross * 1e3, hits);
}
