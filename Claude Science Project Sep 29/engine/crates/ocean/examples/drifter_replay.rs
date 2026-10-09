//! Replay GDP drifter segments (`prepare/gdp_segments.py`) through one ocean configuration and write
//! the model-minus-drifter separation at every 6 h lead to 15 days: the transport-model error with
//! no diffusion and no ocean-error draw, so the separation is the deterministic model error.
//!
//! cargo run --release -p mh370-ocean --example drifter_replay -- <segments.json> <gshhs_f.b> <out.f32> \
//!     <current manifest> [<wind manifest> <c_wind>]
//!
//! Output: little-endian f32 `[segment][lead 1..=60][east_km, north_km]`, NaN after the model track
//! ends (beached on GSHHG, left the domain, or a field gap). Separation is measured in the local
//! tangent plane at the mean latitude of the two points. The segment order is the input order.

use mh370_ocean::*;
use serde::Deserialize;
use std::collections::BTreeMap;

#[derive(Deserialize)]
struct Seg {
    t0: f64,
    lon: Vec<f64>,
    lat: Vec<f64>,
}
#[derive(Deserialize)]
struct Segs {
    step_s: f64,
    fixes: usize,
    segments: Vec<Seg>,
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let s: Segs = serde_json::from_str(&std::fs::read_to_string(&a[1]).unwrap()).unwrap();
    let coast = PolygonCoast::from_gshhg(std::path::Path::new(&a[2]), vec![], PolygonCoastOptions::default()).unwrap();
    let open = |p: &str| if p.ends_with(".series.json") { GridField::load_series(std::path::Path::new(p)) } else { GridField::load(std::path::Path::new(p)) }.expect("load");
    let current = open(&a[4]);
    let wind = (a.len() > 6).then(|| open(&a[5]));
    let c_wind: f64 = if a.len() > 6 { a[6].parse().unwrap() } else { 0.0 };
    let leads = s.fixes - 1;
    let mut out = vec![f32::NAN; s.segments.len() * leads * 2];
    let mut groups: BTreeMap<i64, Vec<usize>> = BTreeMap::new();
    for (k, g) in s.segments.iter().enumerate() {
        groups.entry(g.t0 as i64).or_default().push(k);
    }
    let start = std::time::Instant::now();
    let (mut ended, mut released_on_land) = (0usize, 0usize);
    for (&t0, members) in &groups {
        let t0 = t0 as f64;
        let particles: Vec<Particle> = members
            .iter()
            .map(|&k| Particle::new([s.segments[k].lon[0], s.segments[k].lat[0]], t0, ObjectResponse::new(0.0, c_wind)))
            .collect();
        let spec = RunSpec {
            forcing: Forcing { current: &current, stokes: None, wind10: wind.as_ref().map(|w| w as &dyn VectorField) },
            coast: &coast,
            domain: Domain { lon_min: 15.0, lon_max: 120.0, lat_min: -50.0, lat_max: 0.0 },
            step_s: 3600.0,
            output_times: (1..=leads).map(|l| t0 + l as f64 * s.step_s).collect(),
            diffusion: Diffusion::None,
            ocean_error: OceanErrorModel::none(),
            refloat: Refloat::Off,
            seed: 1,
            leeway_absorbs_stokes: true,
            accept_partial_stokes_overlap: false,
            explicit_residual: false,
            threads: 2,
        };
        let run = integrate(&spec, &particles).expect("integrate");
        for (tr, &k) in run.tracks.iter().zip(members) {
            if matches!(tr.events.first(), Some(Event::ReleasedOnLand { .. })) {
                released_on_land += 1;
            } else if !tr.events.is_empty() {
                ended += 1;
            }
            let g = &s.segments[k];
            for (l, snap) in tr.snapshots.iter().enumerate() {
                if let Snapshot::Afloat(m) = snap {
                    let (dl, la) = (g.lon[l + 1], g.lat[l + 1]);
                    let cos = (0.5 * (m[1] + la)).to_radians().cos();
                    let e = (m[0] - dl).to_radians() * EARTH_RADIUS_M * cos / 1e3;
                    let n = (m[1] - la).to_radians() * EARTH_RADIUS_M / 1e3;
                    out[(k * leads + l) * 2] = e as f32;
                    out[(k * leads + l) * 2 + 1] = n as f32;
                }
            }
        }
    }
    let bytes: Vec<u8> = out.iter().flat_map(|x| x.to_le_bytes()).collect();
    std::fs::write(&a[3], bytes).unwrap();
    println!(
        "{{\"segments\":{},\"start_groups\":{},\"ended_early\":{ended},\"released_on_land\":{released_on_land},\"wall_s\":{:.1},\"ocean_model\":{:?},\"c_wind\":{c_wind}}}",
        s.segments.len(),
        groups.len(),
        start.elapsed().as_secs_f64(),
        Forcing { current: &current, stokes: None, wind10: wind.as_ref().map(|w| w as &dyn VectorField) }.ocean_model()
    );
}
