//! Smoke test of the GSHHG coastline with real forcing: how often a product's land mask strands a
//! particle before the shoreline is reached, how far from the shore, and how many of those the
//! declared snap distance converts to beachings.
//!
//! Particles on a regular grid of GSHHG sea points over 32-60 E, 30-8 S (Mozambique Channel,
//! Madagascar, Mascarenes), released 12:00 UTC 8 March 2014, 1 h steps for 120 days, K = 248 m^2/s.
//! Configuration `leeway`: GLORYS12 current + c_wind 0.02 x ERA5 U10. Configuration `stokes`:
//! GLORYS12 + 1.0 x WAVERYS Stokes + 0.01 x ERA5 U10.
//!
//! cargo run --release -p mh370-ocean --example coast_smoke -- <gshhs_f.b> <current> <stokes> <wind> <threads> <n>

use mh370_ocean::*;
use std::time::Instant;

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let open = |p: &str| if p.ends_with(".series.json") { GridField::load_series(std::path::Path::new(p)) } else { GridField::load(std::path::Path::new(p)) }.expect("load");
    let coast = PolygonCoast::from_gshhg(std::path::Path::new(&a[1]), g1_segments(), PolygonCoastOptions::default()).unwrap();
    let (cur, sto, win) = (open(&a[2]), open(&a[3]), open(&a[4]));
    let threads: usize = a[5].parse().unwrap();
    let n: usize = a[6].parse().unwrap();
    let t0 = 1_394_280_000.0;
    let t1 = t0 + 120.0 * SECONDS_PER_DAY;
    let side = (n as f64).sqrt().ceil() as usize;
    let grid: Vec<LonLat> = (0..side * side)
        .map(|i| [32.0 + 28.0 * ((i % side) as f64 + 0.5) / side as f64, -30.0 + 22.0 * ((i / side) as f64 + 0.5) / side as f64])
        .filter(|&p| !coast.is_land(p))
        .collect();
    for (name, a_s, c_w) in [("leeway", 0.0, 0.02), ("stokes", 1.0, 0.01)] {
        let particles: Vec<Particle> = grid.iter().map(|&p| Particle::new(p, t0, ObjectResponse::new(a_s, c_w))).collect();
        let spec = RunSpec {
            forcing: Forcing { current: &cur, stokes: (a_s > 0.0).then_some(&sto as &dyn VectorField), wind10: Some(&win) },
            coast: &coast,
            domain: Domain { lon_min: 15.0, lon_max: 120.0, lat_min: -50.0, lat_max: 0.0 },
            step_s: 3600.0,
            output_times: vec![t1],
            diffusion: Diffusion::Diffusivity { k_m2_s: 248.0 },
            ocean_error: OceanErrorModel::none(),
            refloat: Refloat::Off,
            seed: 11,
            leeway_absorbs_stokes: false,
            accept_partial_stokes_overlap: false,
            explicit_residual: false,
            threads,
        };
        let s = Instant::now();
        let out = integrate(&spec, &particles).unwrap();
        let wall = s.elapsed().as_secs_f64();
        let (mut crossed, mut snapped, mut afloat, mut left) = (0, Vec::new(), 0, 0);
        let mut other: std::collections::BTreeMap<String, usize> = Default::default();
        let mut land_gaps: Vec<(String, f64)> = Vec::new();
        let mut named = [0usize; 7];
        for tr in &out.tracks {
            match tr.events.first() {
                Some(Event::Beached { snapped_m, segment, .. }) => {
                    if *snapped_m > 0.0 { snapped.push(*snapped_m) } else { crossed += 1 }
                    if *segment < 7 { named[*segment as usize] += 1 }
                }
                Some(Event::FieldGap { at, component, gap: FieldGap::Land, .. }) => {
                    land_gaps.push((format!("{component:?}"), coast.locate(*at, 300_000.0).map_or(f64::INFINITY, |h| h.snapped_m)))
                }
                Some(Event::LeftDomain { .. }) => left += 1,
                None => afloat += 1,
                Some(Event::FieldGap { component, gap, .. }) => *other.entry(format!("FieldGap:{component:?}:{gap:?}")).or_default() += 1,
                Some(e) => *other.entry(format!("{e:?}").split([' ', '{']).next().unwrap().to_string()).or_default() += 1,
            }
        }
        snapped.sort_by(|x, y| x.partial_cmp(y).unwrap());
        let q = |v: &[f64], f: f64| if v.is_empty() { f64::NAN } else { v[((v.len() - 1) as f64 * f).round() as usize] / 1e3 };
        let mut gd: Vec<f64> = land_gaps.iter().map(|g| g.1).collect();
        gd.sort_by(|x, y| x.partial_cmp(y).unwrap());
        let mut comps: Vec<String> = land_gaps.iter().map(|g| g.0.clone()).collect();
        comps.sort();
        comps.dedup();
        let by: Vec<String> = comps.iter().map(|c| format!("{c}:{}", land_gaps.iter().filter(|g| &g.0 == c).count())).collect();
        println!(
            "{{\"config\":\"{name}\",\"particles\":{},\"wall_s\":{wall:.1},\"afloat\":{afloat},\"beached_crossing\":{crossed},\"beached_snapped\":{},\"snapped_km_p50_p90_p99_max\":[{:.2},{:.2},{:.2},{:.2}],\"land_gap_beyond_snap\":{},\"land_gap_by_component\":{:?},\"land_gap_shore_km_p50_max\":[{:.1},{:.1}],\"left_domain\":{left},\"other\":{other:?},\"named_S1_S6\":{:?}}}",
            particles.len(), snapped.len(), q(&snapped, 0.5), q(&snapped, 0.9), q(&snapped, 0.99), q(&snapped, 1.0), land_gaps.len(), by, q(&gd, 0.5), q(&gd, 1.0), &named[1..]
        );
    }
}
