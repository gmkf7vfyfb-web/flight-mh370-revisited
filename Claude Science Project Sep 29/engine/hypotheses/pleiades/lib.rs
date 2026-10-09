//! Pléiades / COSMO-SkyMed: conditional hypothesis H that at least one object imaged by Pléiades on
//! 23 March 2014 (GA Record 2017/13) or detected by COSMO-SkyMed on 21 March 2014 came from 9M-MRO
//! (brief: threads/master-prompts/pleiades.md).
//!
//! The module enters ONLY as an impact log-likelihood from positional compatibility under forward
//! transport (likelihood.rs), with H carried by the alternative `pleiades-origin` = {not-H, H} whose
//! prior the composer sweeps. There is NO identity likelihood: shape and size give none (brief
//! section 3). It must never pre-select or filter impact samples (composition rule 2).
//!
//! Status: deliverable 3 (Pléiades positions only). COSMO-SkyMed enters through deliverables 4-5
//! (prepare/twoepoch.py) and is not yet in this hook. PROVISIONAL throughout: the release-grid table
//! is one ocean-model option, and the spread parameters are declared, not yet measured.
//!
//! Notes, results and provenance live outside the engine tree (engine/AGENTS.md: three markdown
//! files only, generated output never committed): `Claude Science Project Sep 29/results/pleiades/`,
//! `results/pleiades-references.md` and `.bib`. The GA Record 2017/13 object crops are (c) CNES and are
//! never committed anywhere; the PDF is read by path.

mod export;
mod likelihood;

use hypothesis::{Alternatives, Hypothesis, ImpactView};
use likelihood::{PositionLikelihood, Spread, Table, Target};
use serde::Deserialize;
use std::path::{Path, PathBuf};

/// Labels of `object-rating`, in order: rating-4 weight rho4 (rho4 = 0 is the rating-5 arm).
const RATING_OPTIONS: [(&str, &str, f64); 4] =
    [("rho4-0", "rating5", 0.0), ("rho4-0.25", "rating45", 0.25), ("rho4-0.5", "rating45", 0.5), ("rho4-1", "rating45", 1.0)];

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Params {
    /// release-grid.toml from export.rs; relative paths are relative to this module's directory.
    /// Absent: the module returns NaN ("not computed") for every sample.
    release_grid: Option<String>,
    #[serde(default = "default_targets")]
    targets: String,
    #[serde(default = "default_sigma_e")]
    sigma_e_ms: f64,
    #[serde(default = "default_t_e")]
    t_e_days: f64,
    #[serde(default = "default_sd_target")]
    sd_target_km: f64,
    #[serde(default = "default_k_min")]
    k_min_m2_s: f64,
    #[serde(default = "default_k_max")]
    k_max_m2_s: f64,
    #[serde(default = "default_k_nodes")]
    k_nodes: usize,
    /// Prior P(H) for `pleiades-origin`; the composer sweeps it.
    #[serde(default = "default_prior_h")]
    prior_h: f64,
}

fn default_targets() -> String { "data/targets-3km.csv".into() }
fn default_sigma_e() -> f64 { 0.05 }
fn default_t_e() -> f64 { 2.0 }
fn default_sd_target() -> f64 { 0.5 }
fn default_k_min() -> f64 { 30.0 }
fn default_k_max() -> f64 { 1000.0 }
fn default_k_nodes() -> usize { 8 }
fn default_prior_h() -> f64 { 0.5 }

fn resolve(p: &str) -> PathBuf {
    let p = Path::new(p);
    if p.is_absolute() { p.to_path_buf() } else { Path::new(env!("CARGO_MANIFEST_DIR")).join("pleiades").join(p) }
}

struct Pleiades {
    prior_h: f64,
    ocean_model: String,
    lik: Option<PositionLikelihood>,
}

/// Scene acquisition times (data/acquisition-times.csv).
fn scene_time(scene: &str) -> Result<f64, String> {
    match scene {
        "PHR_4" | "PHR_2" => Ok(1_395_548_640.0),
        "PHR_1" | "PHR_3" => Ok(1_395_548_880.0),
        other => Err(format!("pleiades: unknown scene {other}")),
    }
}

fn load_targets(path: &Path, table: &Table) -> Result<Vec<Vec<Target>>, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let mut lines = text.lines();
    let head: Vec<&str> = lines.next().ok_or("empty targets file")?.split(',').collect();
    let col = |n: &str| head.iter().position(|h| *h == n).ok_or(format!("targets: no column {n}"));
    let (ca, cr, cs, cx, cy, ce, cc) = (col("arm")?, col("rho4")?, col("scene")?, col("lon")?, col("lat")?, col("w_equal")?, col("w_count")?);
    let mut arms = vec![Vec::new(); RATING_OPTIONS.len()];
    for l in lines {
        let f: Vec<&str> = l.split(',').collect();
        let rho: f64 = f[cr].parse().map_err(|e| format!("targets rho4: {e}"))?;
        for (o, (_, arm, r)) in RATING_OPTIONS.iter().enumerate() {
            if f[ca] == *arm && (rho - r).abs() < 1e-9 {
                let t = scene_time(f[cs])?;
                arms[o].push(Target {
                    scene: f[cs].to_string(),
                    lon: f[cx].parse().map_err(|e| format!("{e}"))?,
                    lat: f[cy].parse().map_err(|e| format!("{e}"))?,
                    w_equal: f[ce].parse().map_err(|e| format!("{e}"))?,
                    w_count: f[cc].parse().map_err(|e| format!("{e}"))?,
                    time_index: table.time_index(t).ok_or(format!("release grid has no output at scene time {t}"))?,
                    dt_ref_unix_s: t,
                });
            }
        }
    }
    for (o, a) in arms.iter_mut().enumerate() {
        if a.is_empty() {
            return Err(format!("targets: no rows for object-rating option {}", RATING_OPTIONS[o].0));
        }
        // the file carries 6 decimals; renormalise so each weight form sums to one exactly
        let (se, sc): (f64, f64) = (a.iter().map(|t| t.w_equal).sum(), a.iter().map(|t| t.w_count).sum());
        if (se - 1.0).abs() > 1e-4 || (sc - 1.0).abs() > 1e-4 {
            return Err(format!("targets: weights for {} sum to {se}, {sc}", RATING_OPTIONS[o].0));
        }
        for t in a.iter_mut() {
            t.w_equal /= se;
            t.w_count /= sc;
        }
    }
    Ok(arms)
}

pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String> {
    let p: Params = params.clone().try_into().map_err(|e| format!("pleiades: {e}"))?;
    if !(p.prior_h > 0.0 && p.prior_h < 1.0) {
        return Err("pleiades: prior_h must lie in (0, 1)".into());
    }
    let (lik, ocean_model) = match &p.release_grid {
        None => (None, "glorys12v1+era5-wind10".to_string()),
        Some(g) => {
            let table = Table::load(&resolve(g))?;
            let arms = load_targets(&resolve(&p.targets), &table)?;
            let spread = Spread::new(p.sigma_e_ms, p.t_e_days * 86_400.0, p.sd_target_km, p.k_min_m2_s, p.k_max_m2_s, p.k_nodes);
            let om = table.ocean_model.clone();
            (Some(PositionLikelihood { table, spread, arms }), om)
        }
    };
    Ok(Box::new(Pleiades { prior_h: p.prior_h, ocean_model, lik }))
}

impl Hypothesis for Pleiades {
    fn observations(&self) -> Vec<String> {
        vec!["ga-rec2017-13:pleiades-objects".into()]
    }

    fn alternatives(&self) -> Vec<Alternatives> {
        let mut origin = Alternatives::new("pleiades-origin", &[("not-H", 1.0 - self.prior_h), ("H", self.prior_h)]);
        origin.sweep_label = Some("prior P(H): at least one imaged object came from 9M-MRO".into());
        let q = 1.0 / RATING_OPTIONS.len() as f64;
        let rating: Vec<(&str, f64)> = RATING_OPTIONS.iter().map(|(l, _, _)| (*l, q)).collect();
        vec![
            origin,
            Alternatives::new("object-rating", &rating),
            Alternatives::new("cluster-weight", &[("equal", 0.5), ("count", 0.5)]),
            Alternatives::new(ocean::OCEAN_MODEL_ALTERNATIVE, &[(self.ocean_model.as_str(), 1.0)]),
        ]
    }

    fn absolute_scale(&self) -> bool {
        true
    }

    fn impact_log_likelihood(&self, impact: &ImpactView, choice: &[usize]) -> f64 {
        if choice[0] == 0 {
            return 0.0; // not-H: the background against which H is measured
        }
        match &self.lik {
            None => f64::NAN,
            Some(l) => l.ln_l_h(impact.longitude_deg, impact.latitude_deg, impact.unix_s, choice[1], choice[2] == 1),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn constructs_without_data_and_reports_not_computed() {
        let h = new(&toml::Value::Table(Default::default())).unwrap();
        let names: Vec<String> = h.alternatives().iter().map(|a| a.name.clone()).collect();
        assert_eq!(names, ["pleiades-origin", "object-rating", "cluster-weight", "ocean-model"]);
        assert!(h.absolute_scale());
        for a in h.alternatives() {
            assert!((a.options.iter().map(|o| o.1).sum::<f64>() - 1.0).abs() < 1e-12, "{}", a.name);
        }
    }

    #[test]
    fn targets_file_has_every_rating_option_and_weights_sum_to_one() {
        let text = std::fs::read_to_string(resolve("data/targets-3km.csv")).unwrap();
        let mut sums = std::collections::BTreeMap::<(String, String), (f64, f64)>::new();
        for l in text.lines().skip(1) {
            let f: Vec<&str> = l.split(',').collect();
            let e = sums.entry((f[0].into(), f[1].into())).or_default();
            e.0 += f[5].parse::<f64>().unwrap();
            e.1 += f[6].parse::<f64>().unwrap();
        }
        assert_eq!(sums.len(), 5);
        for (k, (a, b)) in sums {
            assert!((a - 1.0).abs() < 1e-5 && (b - 1.0).abs() < 1e-5, "{k:?} {a} {b}");
        }
    }

    /// Export the module's own ln L(s | H) on a regular impact grid, for every object-rating and
    /// cluster-weight option, so that analyses outside the engine (prepare/rerun_reference.py) use
    /// exactly this hook's numbers. Writes PLEIADES_EXPORT_DIR/likelihood-surface.{f32,toml}.
    #[test]
    #[ignore]
    fn pleiades_export_likelihood_surface() {
        use std::io::Write as _;
        let out = std::path::PathBuf::from(std::env::var("PLEIADES_EXPORT_DIR").expect("set PLEIADES_EXPORT_DIR"));
        let mut t = toml::map::Map::new();
        t.insert("release_grid".into(), toml::Value::String("../../runs/pleiades/release-grid.toml".into()));
        let h = new(&toml::Value::Table(t)).unwrap();
        let (lon0, lat0, step, nlon, nlat) = (87.025, -40.975, 0.05, 199usize, 199usize);
        let unix_s = 1_394_238_300.0; // 00:25 UTC 8 Mar: within the impact window
        let mut buf = Vec::with_capacity(4 * 2 * nlat * nlon * 4);
        let mut nan = 0usize;
        for r in 0..RATING_OPTIONS.len() {
            for w in 0..2 {
                for j in 0..nlat {
                    for i in 0..nlon {
                        let view = ImpactView {
                            parent: 0, unix_s, latitude_deg: lat0 + j as f64 * step, longitude_deg: lon0 + i as f64 * step,
                            velocity_east_mps: 0.0, velocity_north_mps: 0.0, velocity_up_mps: 0.0, flight_path_angle_deg: 0.0, mass_kg: 0.0,
                            kinetic_energy_j: 0.0, vertical_kinetic_energy_j: 0.0, family: 0, takeover_unix_s: 0.0, takeover_latitude_deg: 0.0,
                            takeover_longitude_deg: 0.0, takeover_altitude_ft: 0.0, mode: 0, alternative: 0, latents: &[],
                        };
                        let v = h.impact_log_likelihood(&view, &[1, r, w, 0]);
                        nan += usize::from(!v.is_finite());
                        buf.extend_from_slice(&(v as f32).to_le_bytes());
                    }
                }
            }
        }
        std::fs::File::create(out.join("likelihood-surface.f32")).unwrap().write_all(&buf).unwrap();
        let labels: Vec<&str> = RATING_OPTIONS.iter().map(|o| o.0).collect();
        let meta = format!(
            "layout = \"[object-rating][cluster-weight][lat][lon] ln L(s|H) little-endian float32\"\nlon0 = {lon0}\nlat0 = {lat0}\nstep_deg = {step}\nnlon = {nlon}\nnlat = {nlat}\nimpact_unix_s = {unix_s:.1}\nobject_rating = {labels:?}\ncluster_weight = [\"equal\", \"count\"]\nnot_computed = {nan}\nocean_model = \"glorys12v1+era5-wind10\"\n"
        );
        std::fs::write(out.join("likelihood-surface.toml"), meta).unwrap();
        assert_eq!(nan, 0, "every grid point inside the release table must be computed");
    }

    /// Against the real table (gitignored runs/pleiades); run with --ignored after export.rs.
    #[test]
    #[ignore]
    fn real_table_column_is_finite_on_the_grid_and_seed_free() {
        let mut t = toml::map::Map::new();
        t.insert("release_grid".into(), toml::Value::String("../../runs/pleiades/release-grid.toml".into()));
        let h = new(&toml::Value::Table(t.clone())).unwrap();
        let h2 = new(&toml::Value::Table(t)).unwrap();
        let mut n = 0;
        for i in 0..40 {
            let view = ImpactView {
                parent: 0, unix_s: 1_394_238_300.0, latitude_deg: -37.5 + 0.08 * i as f64, longitude_deg: 89.0 + 0.1 * i as f64,
                velocity_east_mps: 0.0, velocity_north_mps: 0.0, velocity_up_mps: 0.0, flight_path_angle_deg: 0.0, mass_kg: 0.0,
                kinetic_energy_j: 0.0, vertical_kinetic_energy_j: 0.0, family: 0, takeover_unix_s: 0.0, takeover_latitude_deg: 0.0,
                takeover_longitude_deg: 0.0, takeover_altitude_ft: 0.0, mode: 0, alternative: 0, latents: &[],
            };
            for r in 0..4 {
                for w in 0..2 {
                    let a = h.impact_log_likelihood(&view, &[1, r, w, 0]);
                    let b = h2.impact_log_likelihood(&view, &[1, r, w, 0]);
                    assert!(a.is_finite(), "{a} at {i}");
                    assert_eq!(a.to_bits(), b.to_bits());
                    n += 1;
                }
            }
            assert_eq!(h.impact_log_likelihood(&view, &[0, 0, 0, 0]), 0.0);
        }
        assert_eq!(n, 320);
    }
}
