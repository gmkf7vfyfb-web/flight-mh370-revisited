#![cfg_attr(not(test), allow(dead_code, unused_imports))]
//! Deterministic transport tables for the Pléiades module, computed through the shared
//! `mh370-ocean` integrator (no advection here: brief section 8 and the shared-ocean rule).
//!
//! The module's likelihood uses an ANALYTIC spread around a deterministic track (brief section 9),
//! so every track here is integrated with diffusion and ocean error switched off. The spread is
//! added afterwards, in closed form, by `likelihood.rs` and by `prepare/`. That makes the
//! likelihood normalised and seed-free by construction.
//!
//! Velocity system (declared): GLORYS12 surface current + c_wind * ERA5 10 m wind, leeway angle 0,
//! a_stokes = 0, no WAVERYS. The windage c_wind ABSORBS Stokes drift (the CSIRO-style system), so
//! Stokes is not added on top (brief section 7: never count Stokes twice).
//!
//! Two tables, both run from `cargo test -p mh370-hypotheses -- --ignored pleiades_export`, with
//! `PLEIADES_OCEAN_DIR` (the ocean-data root) and `PLEIADES_EXPORT_DIR` (where to write; normally
//! the gitignored `engine/runs/pleiades/`):
//! - `cosmo-tracks.csv`: each COSMO-SkyMed contact released at each pass time and offset, for each
//!   windage on the grid, positions at the Pléiades scene times.
//! - `release-grid.f32` + `.json`: a regular release grid at the impact time, for each windage,
//!   positions at the COSMO pass times and the Pléiades scene times.

use ocean::{Diffusion, Domain, Forcing, GridField, NoCoast, ObjectResponse, OceanErrorModel, Particle, Refloat, RunSpec, Snapshot};
use std::path::Path;

/// Windage grid: c_wind = 0 .. 5 % in 0.25 % steps (prior work's uniform 0-5 %).
pub const WINDAGE_STEP: f64 = 0.0025;
pub const WINDAGE_N: usize = 21;
/// Integration step, s. ERA5 is 3-hourly instantaneous; 1 h resolves the 40-53 h COSMO interval.
pub const STEP_S: f64 = 3600.0;
/// Release time of the impact table: 8 Mar 2014 00:20:00 UTC (impacts fall 00:19-00:40; the
/// 20-minute spread moves an object < 1 km against a spread of tens of km).
pub const IMPACT_RELEASE_UNIX_S: f64 = 1_394_238_000.0;
/// Pléiades scene times (data/acquisition-times.csv): 04:24 UTC (PHR_4, PHR_2) and 04:28 UTC
/// (PHR_1, PHR_3), 23 March 2014.
pub const PLEIADES_UNIX_S: [f64; 2] = [1_395_548_640.0, 1_395_548_880.0];
/// COSMO pass mid-times: dawn 23:56 UTC 20 Mar, dusk 11:56 UTC 21 Mar.
pub const COSMO_PASS_UNIX_S: [f64; 2] = [1_395_359_760.0, 1_395_402_960.0];
pub const COSMO_PASS_LABEL: [&str; 2] = ["dawn-20Mar", "dusk-21Mar"];
/// Quadrature offsets on the COSMO pass time, s (+-25 min declared uncertainty).
pub const PASS_OFFSETS_S: [f64; 3] = [-1500.0, 0.0, 1500.0];

pub fn windage(k: usize) -> f64 {
    k as f64 * WINDAGE_STEP
}

pub struct Ocean {
    pub current: GridField,
    pub wind: GridField,
}

impl Ocean {
    /// Current product from `PLEIADES_CURRENT` (path under the ocean-data root; a `.series.json`
    /// is loaded as a series), default GLORYS12V1 surface, March-April 2014. Wind is ERA5.
    pub fn load(root: &Path) -> Result<Self, String> {
        let cur = std::env::var("PLEIADES_CURRENT").unwrap_or_else(|_| "glorys12/glorys12v1_uo_vo_surface_20140307-20140430.json".into());
        let p = root.join(&cur);
        let current = if cur.ends_with(".series.json") { GridField::load_series(&p)? } else { GridField::load(&p)? };
        Ok(Ocean { current, wind: GridField::load(&root.join("era5/era5_u10_v10_3h_15-120E_50-0S_20140307-20141231.json"))? })
    }
}

/// Suffix for the output files of one product (`PLEIADES_EXPORT_TAG`, default empty = GLORYS12).
pub fn tag() -> String {
    std::env::var("PLEIADES_EXPORT_TAG").unwrap_or_default()
}

/// Integration domain: default 75-110 E, 48-22 S (unchanged); env `PLEIADES_INTEGRATE_DOMAIN` = "lon_min,lon_max,lat_min,lat_max"
/// widens it for the coverage export (composer ruling 1), inside the ocean data (15-120 E, 50-0 S).
fn integrate_domain() -> Domain {
    match std::env::var("PLEIADES_INTEGRATE_DOMAIN") {
        Ok(s) => {
            let f: Vec<f64> = s.split(',').map(|x| x.trim().parse().expect("PLEIADES_INTEGRATE_DOMAIN: four numbers")).collect();
            assert_eq!(f.len(), 4, "PLEIADES_INTEGRATE_DOMAIN must be lon_min,lon_max,lat_min,lat_max");
            Domain { lon_min: f[0], lon_max: f[1], lat_min: f[2], lat_max: f[3] }
        }
        Err(_) => Domain { lon_min: 75.0, lon_max: 110.0, lat_min: -48.0, lat_max: -22.0 },
    }
}

pub fn spec<'a>(ocean: &'a Ocean, coast: &'a NoCoast, output_times: Vec<f64>, threads: usize) -> RunSpec<'a> {
    RunSpec {
        forcing: Forcing { current: &ocean.current, stokes: None, wind10: Some(&ocean.wind) },
        coast,
        domain: integrate_domain(),
        step_s: STEP_S,
        output_times,
        diffusion: Diffusion::None,
        ocean_error: OceanErrorModel::none(),
        refloat: Refloat::Off,
        seed: 0,
        leeway_absorbs_stokes: true,
        accept_partial_stokes_overlap: false,
        explicit_residual: false,
        threads,
    }
}

pub fn response(c_wind: f64) -> ObjectResponse {
    ObjectResponse { a_stokes: 0.0, c_wind, wind_angle_deg: 0.0, leeway_angle_deg: 0.0, leeway_speed_mps: 0.0 }
}

/// Afloat position or NaN: anything else (left domain, field gap) is flagged by NaN and counted.
pub fn position(s: &Snapshot) -> [f64; 2] {
    match s {
        Snapshot::Afloat(p) => *p,
        _ => [f64::NAN, f64::NAN],
    }
}

#[cfg(test)]
mod run {
    use super::*;
    use std::fmt::Write as _;
    use std::io::Write as _;

    fn dirs() -> (std::path::PathBuf, std::path::PathBuf) {
        let o = std::env::var("PLEIADES_OCEAN_DIR").expect("set PLEIADES_OCEAN_DIR");
        let e = std::env::var("PLEIADES_EXPORT_DIR").expect("set PLEIADES_EXPORT_DIR");
        std::fs::create_dir_all(&e).unwrap();
        (o.into(), e.into())
    }

    fn threads() -> usize {
        std::env::var("RAYON_NUM_THREADS").ok().and_then(|s| s.parse().ok()).unwrap_or(2)
    }

    #[test]
    #[ignore]
    fn pleiades_export_cosmo_tracks() {
        let (o, e) = dirs();
        let ocean = Ocean::load(&o).unwrap();
        let coast = NoCoast;
        let contacts = std::fs::read_to_string(Path::new(env!("CARGO_MANIFEST_DIR")).join("pleiades/data/cosmo-contacts.csv")).unwrap();
        let contacts: Vec<(String, f64, f64)> = contacts
            .lines()
            .skip(1)
            .map(|l| {
                let f: Vec<&str> = l.split(',').collect();
                (f[0].to_string(), f[1].parse().unwrap(), f[2].parse().unwrap())
            })
            .collect();
        // Output at the two scene times and +-25 min around them, to measure that sensitivity.
        let mut outs: Vec<f64> = PLEIADES_UNIX_S.iter().flat_map(|t| [t - 1500.0, *t, t + 1500.0]).collect();
        outs.sort_by(|a, b| a.partial_cmp(b).unwrap());
        outs.dedup();
        let mut particles = Vec::new();
        let mut keys = Vec::new();
        for (id, lat, lon) in &contacts {
            for (p, t0) in COSMO_PASS_UNIX_S.iter().enumerate() {
                for off in PASS_OFFSETS_S {
                    for k in 0..WINDAGE_N {
                        particles.push(Particle { release: [*lon, *lat], release_time: t0 + off, response: response(windage(k)), end_time: None });
                        keys.push((id.clone(), COSMO_PASS_LABEL[p], off, windage(k)));
                    }
                }
            }
        }
        let run = ocean::integrate(&spec(&ocean, &coast, outs.clone(), threads()), &particles).unwrap();
        let mut csv = String::from("contact,pass,offset_s,c_wind,out_unix_s,longitude,latitude\n");
        let mut bad = 0;
        for (key, track) in keys.iter().zip(&run.tracks) {
            for (t, s) in outs.iter().zip(&track.snapshots) {
                let p = position(s);
                bad += usize::from(!p[0].is_finite());
                writeln!(csv, "{},{},{},{:.4},{},{:.6},{:.6}", key.0, key.1, key.2, key.3, t, p[0], p[1]).unwrap();
            }
        }
        assert_eq!(bad, 0, "every COSMO track must stay afloat in the domain");
        std::fs::write(e.join(format!("cosmo-tracks{}.csv", tag())), csv).unwrap();
        std::fs::write(e.join(format!("cosmo-tracks{}-provenance.json", tag())), serde_json_like(&run.provenance)).unwrap();
    }

    #[test]
    #[ignore]
    fn pleiades_export_release_grid() {
        let (o, e) = dirs();
        let ocean = Ocean::load(&o).unwrap();
        let coast = NoCoast;
        // 0.1 deg grid over 87-97 E, 41-31 S: covers the impact samples' reach around the arc.
        // 85-103 E, 43-25 S: covers the reference-289 impacts north to 25 S (was 87-97 E, 41-31 S)
        let (lon0, lat0, step, nlon, nlat) = super::grid_box("PLEIADES_RELEASE_BOX", (85.0, -43.0, 0.1, 181usize, 181usize));
        let mut outs: Vec<f64> = COSMO_PASS_UNIX_S.iter().chain(PLEIADES_UNIX_S.iter()).copied().collect();
        outs.sort_by(|a, b| a.partial_cmp(b).unwrap());
        let mut particles = Vec::with_capacity(nlon * nlat * WINDAGE_N);
        for j in 0..nlat {
            for i in 0..nlon {
                for k in 0..WINDAGE_N {
                    let p = [lon0 + i as f64 * step, lat0 + j as f64 * step];
                    particles.push(Particle { release: p, release_time: IMPACT_RELEASE_UNIX_S, response: response(windage(k)), end_time: None });
                }
            }
        }
        let run = ocean::integrate(&spec(&ocean, &coast, outs.clone(), threads()), &particles).unwrap();
        let mut buf: Vec<u8> = Vec::with_capacity(particles.len() * outs.len() * 8);
        let mut ended = 0usize;
        for track in &run.tracks {
            for s in &track.snapshots {
                let p = position(s);
                ended += usize::from(!p[0].is_finite());
                buf.extend_from_slice(&(p[0] as f32).to_le_bytes());
                buf.extend_from_slice(&(p[1] as f32).to_le_bytes());
            }
        }
        std::fs::File::create(e.join(format!("release-grid{}.f32", tag()))).unwrap().write_all(&buf).unwrap();
        let meta = format!(
            "{{\"layout\": \"[lat][lon][windage][out_time][lon_deg, lat_deg] little-endian float32\",\n \"lon0\": {lon0}, \"lat0\": {lat0}, \"step_deg\": {step}, \"nlon\": {nlon}, \"nlat\": {nlat},\n \"windage_step\": {WINDAGE_STEP}, \"windage_n\": {WINDAGE_N},\n \"release_unix_s\": {IMPACT_RELEASE_UNIX_S}, \"out_unix_s\": {outs:?},\n \"non_afloat_snapshots\": {ended},\n \"provenance\": {}}}\n",
            serde_json_like(&run.provenance)
        );
        std::fs::write(e.join(format!("release-grid{}.json", tag())), meta).unwrap();
        let toml = format!(
            "layout = \"[lat][lon][windage][out_time][lon_deg, lat_deg] little-endian float32\"\nlon0 = {lon0}\nlat0 = {lat0}\nstep_deg = {step}\nnlon = {nlon}\nnlat = {nlat}\nwindage_step = {WINDAGE_STEP}\nwindage_n = {WINDAGE_N}\nrelease_unix_s = {IMPACT_RELEASE_UNIX_S:.1}\nout_unix_s = {outs:?}\nnon_afloat_snapshots = {ended}\nocean_model = \"{}\"\ndata_file = \"release-grid{}.f32\"\n",
            run.provenance.ocean_model, tag()
        );
        std::fs::write(e.join(format!("release-grid{}.toml", tag())), toml).unwrap();
    }

    /// Minimal JSON for the provenance record (serde_json is not a permitted hypothesis dependency).
    fn serde_json_like(p: &ocean::integrate::Provenance) -> String {
        let q = |s: &str| s.replace('\\', "\\\\").replace('"', "\\\"");
        format!(
            "{{\"alternative\": \"{}\", \"ocean_model\": \"{}\", \"current\": \"{}\", \"wind10\": \"{}\", \"stokes\": \"{}\", \"step_s\": {}, \"diffusion\": \"{}\", \"ocean_error\": \"{}\", \"integrator\": \"{}\", \"leeway_calm_wind_mps\": {}}}",
            p.alternative, q(&p.ocean_model), q(&p.current), q(p.wind10.as_deref().unwrap_or("none")), q(p.stokes.as_deref().unwrap_or("none")),
            p.step_s, q(&format!("{:?}", p.diffusion)), q(&format!("{:?}", p.ocean_error)), q(p.integrator), p.leeway_calm_wind_mps
        )
    }
}

/// Export grid box, overridable for coverage runs: env `var` = "lon0,lat0,step,nlon,nlat" (default unchanged).
/// Composer ruling 1 (10 Oct 16:25 -0600): impacts outside this box are not computed, so the box must cover them.
#[cfg(test)]
pub(crate) fn grid_box(var: &str, default: (f64, f64, f64, usize, usize)) -> (f64, f64, f64, usize, usize) {
    match std::env::var(var) {
        Ok(s) => {
            let f: Vec<&str> = s.split(',').map(str::trim).collect();
            assert_eq!(f.len(), 5, "{var} must be lon0,lat0,step,nlon,nlat");
            (f[0].parse().unwrap(), f[1].parse().unwrap(), f[2].parse().unwrap(), f[3].parse().unwrap(), f[4].parse().unwrap())
        }
        Err(_) => default,
    }
}
