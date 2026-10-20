//! Export bathymetry and sound-speed profiles along WGS84 geodesics, for hydroacoustics' propagation
//! engine (KRAKEN / RAM). One implementation in Rust; the module reads the CSV files.
//!
//! cargo run -p mh370-ocean --release --example ocean_paths -- <request.json> <out-dir>
//!
//! request.json:
//! { "bathymetry": ["/…/gebco/grid/gebco_2026.json"],
//!   "soundspeed_dir": "/…/woa23/soundspeed",
//!   "paths": [ { "name": "air9-H01W", "a": [98.8821, -27.5612], "b": [114.142637, -34.890303],
//!                "time_unix": 1002499200, "spacing_m": 250, "half_width_m": 2000, "profile_every_m": 25000 } ] }
//!
//! Writes `<name>_bathymetry.csv` (s_m, lon, lat, depth_m, source, tid, corridor_max_elevation_m,
//! corridor_max_offset_m, corridor_max_tid, corridor_max_source) and `<name>_soundspeed.csv` (node, s_m,
//! lon, lat, depth_m, pressure_dbar, c_mean_m_s, c_sd_m_s, sa_g_kg, ct_c), plus `<name>_meta.json` with the
//! geodesic length, the WOA23 decade and month used, and the inputs.

use geographiclib_rs::{DirectGeodesic, Geodesic};
use mh370_ocean::bathy::{path_extent, Bathymetry};
use mh370_ocean::soundspeed::{woa23_period, SoundSpeedClimatology};
use serde::Deserialize;
use std::fmt::Write as _;
use std::path::{Path, PathBuf};

#[derive(Deserialize)]
struct PathReq {
    name: String,
    a: [f64; 2],
    b: [f64; 2],
    time_unix: f64,
    spacing_m: f64,
    half_width_m: f64,
    profile_every_m: f64,
}

#[derive(Deserialize)]
struct Request {
    bathymetry: Vec<PathBuf>,
    soundspeed_dir: PathBuf,
    paths: Vec<PathReq>,
}

fn opt<T: std::fmt::Display>(v: Option<T>) -> String {
    v.map(|x| x.to_string()).unwrap_or_default()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let req: Request = serde_json::from_str(&std::fs::read_to_string(&args[1]).expect("request")).expect("parse");
    let out = Path::new(&args[2]);
    std::fs::create_dir_all(out).unwrap();
    let layers: Vec<&Path> = req.bathymetry.iter().map(|p| p.as_path()).collect();
    for p in &req.paths {
        // The window comes from the geodesic itself (sampled every 10 km, padded by the corridor and
        // 0.1 deg), never from the endpoints: long paths bow poleward of both ends.
        let window = path_extent(p.a, p.b, p.half_width_m, 10_000.0, 0.1);
        let bathy = Bathymetry::load(&layers, Some(window)).expect("bathymetry");
        let (len, azi) = bathy.inverse(p.a, p.b);
        let samples = bathy.path(p.a, p.b, p.spacing_m, p.half_width_m);
        // Fail loudly on any sample off every layer: a gap is never dropped silently.
        let gaps: Vec<usize> = samples.iter().enumerate().filter(|(_, x)| x.is_none()).map(|(k, _)| k).collect();
        if let Some(&k) = gaps.first() {
            eprintln!("{}: {} of {} samples are off every bathymetry layer, the first at s = {:.1} km; window {window:?}", p.name, gaps.len(), samples.len(), (k as f64 * p.spacing_m).min(len) / 1e3);
            std::process::exit(2);
        }
        let mut csv = String::from("s_m,lon,lat,depth_m,source,tid,corridor_max_elevation_m,corridor_max_offset_m,corridor_max_tid,corridor_max_source\n");
        for s in samples.into_iter().flatten() {
            let t = &s.track;
            let c = &s.corridor_max;
            writeln!(csv, "{:.1},{:.6},{:.6},{},{:?},{},{},{:.1},{},{:?}", s.s_m, t.point[0], t.point[1], t.depth_m, t.source, opt(t.tid), c.elevation_m, s.corridor_max_offset_m, opt(c.tid), c.source).unwrap();
        }
        std::fs::write(out.join(format!("{}_bathymetry.csv", p.name)), csv).unwrap();

        let (decade, month) = woa23_period(p.time_unix);
        let clim = SoundSpeedClimatology::load(&req.soundspeed_dir.join(format!("woa23_{decade}_m{month:02}.json"))).expect("woa23");
        let g = Geodesic::wgs84();
        let n = (len / p.profile_every_m).ceil() as usize;
        let mut csv = String::from("node,s_m,lon,lat,depth_m,pressure_dbar,c_mean_m_s,c_sd_m_s,sa_g_kg,ct_c\n");
        for k in 0..=n {
            let s = (k as f64 * p.profile_every_m).min(len);
            let (la, lo): (f64, f64) = g.direct(p.a[1], p.a[0], azi, s);
            if let Some(pr) = clim.profile([lo, la]) {
                for i in 0..pr.depth_m.len() {
                    writeln!(csv, "{k},{s:.1},{lo:.6},{la:.6},{},{:.3},{:.4},{:.4},{:.5},{:.5}", pr.depth_m[i], pr.pressure_dbar[i], pr.c_mean_m_s[i], pr.c_sd_m_s[i], pr.absolute_salinity_g_kg[i], pr.conservative_temperature_c[i]).unwrap();
                }
            }
        }
        std::fs::write(out.join(format!("{}_soundspeed.csv", p.name)), csv).unwrap();
        let meta = serde_json::json!({
            "name": p.name, "a": p.a, "b": p.b, "geodesic_length_m": len, "initial_azimuth_deg": azi,
            "spacing_m": p.spacing_m, "half_width_m": p.half_width_m, "profile_every_m": p.profile_every_m,
            "time_unix": p.time_unix, "woa23_decade": decade, "woa23_month": month,
            "bathymetry_layers": req.bathymetry, "load_window": window, "soundspeed_dir": req.soundspeed_dir,
            "crate": "mh370-ocean", "spread": "decav t_sdo/s_sdo, linearised, T and S independent"
        });
        std::fs::write(out.join(format!("{}_meta.json", p.name)), serde_json::to_string_pretty(&meta).unwrap()).unwrap();
        println!("{}: {:.1} km, WOA23 {decade} month {month}", p.name, len / 1000.0);
    }
}
