//! AUDIT HARNESS (untracked, not committed): fates of particles through one composition, with the
//! production coast (GSHHG f, g1 segments, snap 25 km), Fickian diffusion K, per-particle c_wind.
//! args: <current manifest> <wind manifest> <gshhs_f.b> <releases.json> <out.csv>
use mh370_ocean::*;
use serde::Deserialize;
#[derive(Deserialize)]
struct Rel { lon: f64, lat: f64, t0: f64, c_wind: f64 }
#[derive(Deserialize)]
struct Req { step_s: f64, end_time: f64, k_m2_s: f64, seed: u64, threads: usize, releases: Vec<Rel> }
fn main() {
    let a: Vec<String> = std::env::args().collect();
    let req: Req = serde_json::from_str(&std::fs::read_to_string(&a[4]).unwrap()).unwrap();
    let t0 = req.releases.iter().map(|r| r.t0).fold(f64::INFINITY, f64::min) - 3.0 * 86400.0;
    let w = LoadWindow::new([15.0, 120.0, -50.0, 0.0], [t0, req.end_time + 3.0 * 86400.0]);
    let open = |p: &str| GridField::load_window(std::path::Path::new(p), &w).expect("load");
    let current = open(&a[1]);
    let wind = open(&a[2]);
    let opts = PolygonCoastOptions { snap_max_m: 25_000.0, ..Default::default() };
    let coast = PolygonCoast::from_gshhg(std::path::Path::new(&a[3]), g1_segments(), opts).unwrap();
    let parts: Vec<Particle> = req.releases.iter().map(|r| Particle::new([r.lon, r.lat], r.t0, ObjectResponse::new(0.0, r.c_wind))).collect();
    let spec = RunSpec {
        forcing: Forcing { current: &current, stokes: None, wind10: Some(&wind) },
        coast: &coast,
        domain: Domain { lon_min: 15.0, lon_max: 120.0, lat_min: -50.0, lat_max: 0.0 },
        step_s: req.step_s, output_times: vec![req.end_time],
        diffusion: if req.k_m2_s > 0.0 { Diffusion::Diffusivity { k_m2_s: req.k_m2_s } } else { Diffusion::None },
        ocean_error: OceanErrorModel::none(), refloat: Refloat::Off, seed: req.seed, leeway_absorbs_stokes: true,
        accept_partial_stokes_overlap: false, explicit_residual: false, threads: req.threads,
    };
    let out = integrate(&spec, &parts).expect("integrate");
    let mut s = String::from("particle,fate,t,lon,lat,segment,snapped_m\n");
    for (i, tr) in out.tracks.iter().enumerate() {
        let mut row = format!("{i},{:?},,,,,\n", tr.fate);
        for ev in &tr.events {
            match *ev {
                Event::Beached { t, at, segment, snapped_m, .. } => { row = format!("{i},Beached,{t},{:.5},{:.5},{segment},{snapped_m:.0}\n", at[0], at[1]); break; }
                Event::LeftDomain { t, at } => { row = format!("{i},LeftDomain,{t},{:.5},{:.5},,\n", at[0], at[1]); break; }
                Event::FieldGap { t, at, gap, .. } => { row = format!("{i},FieldGap-{gap:?},{t},{:.5},{:.5},,\n", at[0], at[1]); break; }
                _ => {}
            }
        }
        s += &row;
    }
    std::fs::write(&a[5], s).unwrap();
    eprintln!("{} {}", out.provenance.ocean_model, out.provenance.coast);
}
