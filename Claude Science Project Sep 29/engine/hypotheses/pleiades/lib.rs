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
//! (prepare/twoepoch.py) and is not yet in this hook. PROVISIONAL throughout. `ocean-model` has two
//! options (GLORYS12V1, Copernicus-GlobCurrent; one release table each) and the spread is the measured
//! per-component OU fit of ocean transport's GDP replay (run.toml).
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
    /// One entry per `ocean-model` option, in option order, at equal prior weight. When present it
    /// replaces release_grid / sigma_e_ms / t_e_days (and k_*, if given per product).
    #[serde(default)]
    products: Vec<Product>,
    /// COSMO-SkyMed contacts (F1-F4), for the conditional-branch prediction columns only.
    #[serde(default = "default_cosmo")]
    cosmo_contacts: String,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Product {
    release_grid: String,
    /// [east, north], m/s and days: the OU fit of the GDP replay for this product.
    sigma_e_ms: [f64; 2],
    t_e_days: [f64; 2],
    k_min_m2_s: Option<f64>,
    k_max_m2_s: Option<f64>,
    /// Where sigma_e / T_e come from (recorded, not used).
    #[serde(default)]
    source: String,
}

fn default_targets() -> String { "data/targets-3km.csv".into() }
fn default_cosmo() -> String { "data/cosmo-contacts.csv".into() }

/// COSMO-SkyMed contact sets and passes of the conditional branch, in prediction-column order.
const COSMO_SETS: [(&str, usize); 2] = [("C3", 3), ("C4", 4)];
const COSMO_PASSES: [(&str, f64); 2] = [("dawn-20Mar", 1_395_359_760.0), ("dusk-21Mar", 1_395_402_960.0)];

/// Arms [set][pass] of equally weighted COSMO contacts at their pass time (data/cosmo-contacts.csv,
/// first three rows = F1-F3, fourth = F4).
fn cosmo_arms(path: &Path, table: &Table) -> Result<Vec<Vec<Target>>, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let mut contacts = Vec::new();
    for l in text.lines().skip(1) {
        let f: Vec<&str> = l.split(',').collect();
        let num = |i: usize| f[i].parse::<f64>().map_err(|e| format!("cosmo contacts: {e}"));
        contacts.push((f[0].to_string(), num(2)?, num(1)?));
    }
    if contacts.len() != 4 {
        return Err(format!("cosmo contacts: expected F1-F4, got {} rows", contacts.len()));
    }
    let mut arms = Vec::new();
    for (_, n) in COSMO_SETS {
        for (_, t) in COSMO_PASSES {
            let ti = table.time_index(t).ok_or(format!("release grid has no output at COSMO pass {t}"))?;
            arms.push(
                contacts[..n]
                    .iter()
                    .map(|(id, lon, lat)| Target {
                        scene: id.clone(),
                        lon: *lon,
                        lat: *lat,
                        w_equal: 1.0 / n as f64,
                        w_count: 1.0 / n as f64,
                        time_index: ti,
                        dt_ref_unix_s: t,
                    })
                    .collect(),
            );
        }
    }
    Ok(arms)
}
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
    /// Per `ocean-model` option: label and likelihood (None: not computed, NaN).
    models: Vec<(String, Option<PositionLikelihood>)>,
    /// Per `ocean-model` option: COSMO positional likelihood, arms [set][pass] (prediction columns only;
    /// COSMO is not in the impact likelihood, P2/P1: no background or footprint term).
    cosmo: Vec<Option<PositionLikelihood>>,
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
    let mut cosmo = Vec::new();
    let mut build = |grid: &str, spread: Spread| -> Result<(String, Option<PositionLikelihood>), String> {
        let table = Table::load(&resolve(grid))?;
        let arms = load_targets(&resolve(&p.targets), &table)?;
        let carms = cosmo_arms(&resolve(&p.cosmo_contacts), &table)?;
        cosmo.push(Some(PositionLikelihood { table: Table::load(&resolve(grid))?, spread: spread.clone(), arms: carms }));
        Ok((table.ocean_model.clone(), Some(PositionLikelihood { table, spread, arms })))
    };
    let models = if !p.products.is_empty() {
        let mut m = Vec::new();
        for q in &p.products {
            let _ = &q.source;
            let spread = Spread::anisotropic(
                q.sigma_e_ms, [q.t_e_days[0] * 86_400.0, q.t_e_days[1] * 86_400.0], p.sd_target_km,
                q.k_min_m2_s.unwrap_or(p.k_min_m2_s), q.k_max_m2_s.unwrap_or(p.k_max_m2_s), p.k_nodes,
            );
            m.push(build(&q.release_grid, spread)?);
        }
        let mut labels: Vec<&str> = m.iter().map(|x| x.0.as_str()).collect();
        labels.sort();
        labels.dedup();
        if labels.len() != m.len() {
            return Err("pleiades: two products carry the same ocean_model label".into());
        }
        m
    } else {
        match &p.release_grid {
            None => {
                cosmo.push(None);
                vec![("glorys12v1+era5-wind10".to_string(), None)]
            }
            Some(g) => vec![build(g, Spread::new(p.sigma_e_ms, p.t_e_days * 86_400.0, p.sd_target_km, p.k_min_m2_s, p.k_max_m2_s, p.k_nodes))?],
        }
    };
    Ok(Box::new(Pleiades { prior_h: p.prior_h, models, cosmo }))
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
            {
                let qm = 1.0 / self.models.len() as f64;
                let om: Vec<(&str, f64)> = self.models.iter().map(|(l, _)| (l.as_str(), qm)).collect();
                Alternatives::new(ocean::OCEAN_MODEL_ALTERNATIVE, &om)
            },
        ]
    }

    fn absolute_scale(&self) -> bool {
        true
    }

    /// The conditional branch (architecture ~18:30 UTC 9 Oct): ln L(s | C, H) for each ocean model and
    /// COSMO contact set, per pass and pass-marginalised (equal weight on dawn-20Mar and dusk-21Mar).
    /// A reported quantity, not a likelihood term: COSMO enters no composed posterior.
    fn prediction_columns(&self) -> Vec<String> {
        let mut c = Vec::new();
        for (m, _) in &self.models {
            for (set, _) in COSMO_SETS {
                c.push(format!("cosmo-lnl-{set}-pass-marginal-{m}"));
                for (pass, _) in COSMO_PASSES {
                    c.push(format!("cosmo-lnl-{set}-{pass}-{m}"));
                }
            }
        }
        c
    }

    fn predict(&self, impact: &ImpactView, out: &mut [f64]) {
        let mut k = 0;
        for l in &self.cosmo {
            for si in 0..COSMO_SETS.len() {
                let v: Vec<f64> = (0..COSMO_PASSES.len())
                    .map(|pi| match l {
                        None => f64::NAN,
                        Some(l) => l.ln_l_h(impact.longitude_deg, impact.latitude_deg, impact.unix_s, si * COSMO_PASSES.len() + pi, false),
                    })
                    .collect();
                let mx = v.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
                out[k] = if mx.is_finite() { mx + (v.iter().map(|x| (x - mx).exp()).sum::<f64>() / v.len() as f64).ln() } else { mx };
                if v.iter().any(|x| x.is_nan()) {
                    out[k] = f64::NAN;
                }
                out[k + 1..k + 1 + v.len()].copy_from_slice(&v);
                k += 1 + v.len();
            }
        }
    }

    fn impact_log_likelihood(&self, impact: &ImpactView, choice: &[usize]) -> f64 {
        if choice[0] == 0 {
            return 0.0; // not-H: the background against which H is measured
        }
        match &self.models[choice[3]].1 {
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
    fn run_toml_parses_with_two_measured_products() {
        let run: toml::Value = toml::from_str(&std::fs::read_to_string(resolve("run.toml")).unwrap()).unwrap();
        let p: Params = run["hypotheses"]["pleiades"].clone().try_into().unwrap();
        assert_eq!(p.products.len(), 2);
        for q in &p.products {
            assert!(q.sigma_e_ms.iter().all(|s| *s > 0.05 && *s < 0.2), "measured sigma_e out of the replay range");
            assert!(q.t_e_days.iter().all(|t| *t > 2.0 && *t < 20.0));
            assert_eq!((q.k_min_m2_s, q.k_max_m2_s), (Some(0.0), Some(0.0)));
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
        // The module's own run.toml parameters, so the surface is the configured hook exactly.
        // PLEIADES_RUN_TOML selects a sensitivity configuration (default: run.toml).
        let cfg = std::env::var("PLEIADES_RUN_TOML").unwrap_or_else(|_| "run.toml".into());
        let run: toml::Value = toml::from_str(&std::fs::read_to_string(resolve(&cfg)).unwrap()).unwrap();
        let params = run["hypotheses"]["pleiades"].clone();
        let h = new(&params).unwrap();
        let models: Vec<String> = h.alternatives()[3].options.iter().map(|o| o.0.clone()).collect();
        let (lon0, lat0, step, nlon, nlat) = (85.025, -42.975, 0.05, 360usize, 360usize);
        let unix_s = 1_394_238_300.0; // 00:25 UTC 8 Mar: within the impact window
        let mut buf = Vec::with_capacity(models.len() * 4 * 2 * nlat * nlon * 4);
        let mut nan = 0usize;
        for m in 0..models.len() {
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
                        let v = h.impact_log_likelihood(&view, &[1, r, w, m]);
                        nan += usize::from(!v.is_finite());
                        buf.extend_from_slice(&(v as f32).to_le_bytes());
                    }
                }
            }
        }
        }
        std::fs::File::create(out.join("likelihood-surface.f32")).unwrap().write_all(&buf).unwrap();
        let labels: Vec<&str> = RATING_OPTIONS.iter().map(|o| o.0).collect();
        let meta = format!(
            "layout = \"[ocean-model][object-rating][cluster-weight][lat][lon] ln L(s|H) little-endian float32\"\nlon0 = {lon0}\nlat0 = {lat0}\nstep_deg = {step}\nnlon = {nlon}\nnlat = {nlat}\nimpact_unix_s = {unix_s:.1}\nobject_rating = {labels:?}\ncluster_weight = [\"equal\", \"count\"]\nnot_computed = {nan}\nocean_model = {models:?}\nparams = \"{cfg} [hypotheses.pleiades]\"\n"
        );
        std::fs::write(out.join("likelihood-surface.toml"), meta).unwrap();
        // A few points can be not computed (a track leaves a forcing field, at the 25 S edge); counted in
        // not_computed and treated as zero likelihood by the analysis scripts, which report their mass.
        assert!(nan * 100 < buf.len() / 4, "more than 1% of the grid not computed: {nan}");
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

    /// The conditional branch (architecture ~18:30 UTC 9 Oct): COSMO-SkyMed positional likelihood
    /// ln L(s | C, H) on the same impact grid as `pleiades_export_likelihood_surface`, for every ocean
    /// model in run.toml, contact set (C3 = F1-F3, C4 = F1-F4) and pass (dawn-20Mar, dusk-21Mar), with
    /// the measured spread and equal contact weights. A_scene scales it and cancels in every conditional
    /// PDF; no footprint or background term is implied (P1). Writes PLEIADES_EXPORT_DIR/cosmo-surface.{f32,toml}.
    #[test]
    #[ignore]
    fn pleiades_export_cosmo_surface() {
        use std::io::Write as _;
        let out = std::path::PathBuf::from(std::env::var("PLEIADES_EXPORT_DIR").expect("set PLEIADES_EXPORT_DIR"));
        let run: toml::Value = toml::from_str(&std::fs::read_to_string(resolve("run.toml")).unwrap()).unwrap();
        let p: Params = run["hypotheses"]["pleiades"].clone().try_into().unwrap();
        let (lon0, lat0, step, nlon, nlat) = (85.025, -42.975, 0.05, 360usize, 360usize);
        let unix_s = 1_394_238_300.0;
        let mut buf = Vec::new();
        let mut labels = Vec::new();
        let mut nan = 0usize;
        for q in &p.products {
            let table = Table::load(&resolve(&q.release_grid)).unwrap();
            labels.push(table.ocean_model.clone());
            let spread = Spread::anisotropic(
                q.sigma_e_ms,
                [q.t_e_days[0] * 86_400.0, q.t_e_days[1] * 86_400.0],
                p.sd_target_km,
                q.k_min_m2_s.unwrap_or(p.k_min_m2_s),
                q.k_max_m2_s.unwrap_or(p.k_max_m2_s),
                p.k_nodes,
            );
            let arms = cosmo_arms(&resolve(&p.cosmo_contacts), &table).unwrap();
            let lik = PositionLikelihood { table, spread, arms };
            for a in 0..lik.arms.len() {
                for j in 0..nlat {
                    for i in 0..nlon {
                        let v = lik.ln_l_h(lon0 + i as f64 * step, lat0 + j as f64 * step, unix_s, a, false);
                        nan += usize::from(!v.is_finite());
                        buf.extend_from_slice(&(v as f32).to_le_bytes());
                    }
                }
            }
        }
        std::fs::File::create(out.join("cosmo-surface.f32")).unwrap().write_all(&buf).unwrap();
        std::fs::write(
            out.join("cosmo-surface.toml"),
            format!(
                "layout = \"[ocean-model][contact-set][pass][lat][lon] ln L(s|C,H) little-endian float32\"\nlon0 = {lon0}\nlat0 = {lat0}\nstep_deg = {step}\nnlon = {nlon}\nnlat = {nlat}\nimpact_unix_s = {unix_s:.1}\nocean_model = {labels:?}\ncontact_set = [\"C3\", \"C4\"]\npass = [\"dawn-20Mar\", \"dusk-21Mar\"]\nnot_computed = {nan}\nparams = \"run.toml [hypotheses.pleiades]; data/cosmo-contacts.csv; equal contact weights\"\n"
            ),
        )
        .unwrap();
        assert!(nan * 100 < buf.len() / 4, "more than 1% of the grid not computed: {nan}");
    }
}
