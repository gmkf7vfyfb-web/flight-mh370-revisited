//! AUDIT HARNESS (untracked, not committed): deterministic tracks through one current product.
//! args: <current manifest> <releases.json> <out.csv> [wind manifest c_wind]
use mh370_ocean::*;
use serde::Deserialize;
#[derive(Deserialize)]
struct Rel { lon: f64, lat: f64, t0: f64 }
#[derive(Deserialize)]
struct Req { step_s: f64, output_times: Vec<f64>, releases: Vec<Rel> }
fn main() {
    let a: Vec<String> = std::env::args().collect();
    let req: Req = serde_json::from_str(&std::fs::read_to_string(&a[2]).unwrap()).unwrap();
    let t0 = req.releases.iter().map(|r| r.t0).fold(f64::INFINITY, f64::min) - 3.0 * 86400.0;
    let t1 = *req.output_times.last().unwrap() + 3.0 * 86400.0;
    let w = LoadWindow::new([15.0, 120.0, -50.0, 0.0], [t0, t1]);
    let open = |p: &str| GridField::load_window(std::path::Path::new(p), &w).expect("load");
    let current = open(&a[1]);
    let wind = (a.len() > 5).then(|| open(&a[4]));
    let c_wind: f64 = if a.len() > 5 { a[5].parse().unwrap() } else { 0.0 };
    let parts: Vec<Particle> = req.releases.iter().map(|r| Particle::new([r.lon, r.lat], r.t0, ObjectResponse::new(0.0, c_wind))).collect();
    let spec = RunSpec {
        forcing: Forcing { current: &current, stokes: None, wind10: wind.as_ref().map(|w| w as &dyn VectorField) },
        coast: &NoCoast,
        domain: Domain { lon_min: 15.0, lon_max: 120.0, lat_min: -50.0, lat_max: 0.0 },
        step_s: req.step_s, output_times: req.output_times.clone(), diffusion: Diffusion::None,
        ocean_error: OceanErrorModel::none(), refloat: Refloat::Off, seed: 1, leeway_absorbs_stokes: true,
        accept_partial_stokes_overlap: false, explicit_residual: false, threads: 2,
    };
    let out = integrate(&spec, &parts).expect("integrate");
    let mut s = String::from("particle,k,t,lon,lat\n");
    for (i, tr) in out.tracks.iter().enumerate() {
        for (k, sn) in tr.snapshots.iter().enumerate() {
            if let Snapshot::Afloat(p) = sn { s += &format!("{i},{k},{},{:.9},{:.9}\n", req.output_times[k], p[0], p[1]); }
        }
    }
    std::fs::write(&a[3], s).unwrap();
    eprintln!("{} {:?}", out.provenance.ocean_model, out.tracks.iter().map(|t| format!("{:?}", t.fate)).collect::<Vec<_>>());
}
