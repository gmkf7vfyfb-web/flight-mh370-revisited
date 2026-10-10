//! Composer pass 0: the first end-to-end run of `compose()` on real module columns (core (b), one stratum).
//!
//! PIPELINE TEST - core (b) unconverged; EoF physics provisional; hydro L_hyd stand-in; GlobCurrent F1;
//! Holland H1/H2 not estimable. Architecture stand-in; the composer module reviews it.
//!
//! A thin driver, not a runner stage: it reads the row-aligned columns written by
//! `results/composer-pass0/prep_inputs.py` (one `seed-<k>.f64` + `seed-<k>.hdr` per replicate), declares each
//! factor as its module does (deviations marked PASS-0 below and in the results note), runs the composer
//! library unchanged, and writes every product's bookkeeping as JSON plus the composed weights of selected
//! products as little-endian f32. It draws no densities. It also runs the refusal cases a pass 0 must record.
//!
//! Usage: cargo run --release -p mh370-compose --example pass0 -- <stratum input dir> <out dir>

use compose::{compose, Declaration, Mode, Product, Replicate, Set, Status, MODE_COUNT};
use hypothesis::Alternatives;
use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::fs;
use std::io::{Read, Write};
use std::path::{Path, PathBuf};

const GLORYS: &str = "glorys12v1+era5-wind10";
const GLOBCURRENT: &str = "globcurrent-my-p1d+era5-wind10";
/// PASS-0 tolerance on not-computed weight for sets with drift or Pleiades (the default 1e-3 refuses them; recorded).
const PASS0_TOLERANCE: f64 = 0.5;

struct Seed {
    replicate: Replicate,
    core_final_modes: [Mode; MODE_COUNT],
}

fn parse_modes(lines: &[&str]) -> [Mode; MODE_COUNT] {
    std::array::from_fn(|m| {
        let f: Vec<f64> = lines[m].split('\t').map(|v| if v == "-inf" { f64::NEG_INFINITY } else { v.parse().unwrap() }).collect();
        Mode { prior_weight: f[0], log_evidence: f[1], posterior_probability: f[2] }
    })
}

fn read_seed(dir: &Path, k: u64) -> Seed {
    let hdr = fs::read_to_string(dir.join(format!("seed-{k}.hdr"))).expect("hdr");
    let lines: Vec<&str> = hdr.lines().collect();
    let rows: usize = lines[0].split('\t').nth(1).unwrap().parse().unwrap();
    let mut columns: Vec<String> = lines[1].split('\t').map(String::from).collect();
    let modes = parse_modes(&lines[2..7]);
    let core_final_modes = parse_modes(&lines[7..12]);
    let mut bytes = Vec::new();
    fs::File::open(dir.join(format!("seed-{k}.f64"))).unwrap().read_to_end(&mut bytes).unwrap();
    let width = columns.len();
    assert_eq!(bytes.len(), rows * width * 8, "seed {k}: file size");
    let raw: Vec<f64> = bytes.chunks_exact(8).map(|b| f64::from_le_bytes(b.try_into().unwrap())).collect();
    drop(bytes);
    // In-memory derived columns (PASS-0): the "exclude not-computed rows" sensitivity copies (NaN -> -inf, the
    // drift and Pleiades modules' own convention), and the not-H Pleiades columns, which the Pleiades stand-in does
    // not supply (NaN: the composer reads a column for every option combination, even under `given`).
    let mut extra: Vec<(String, Option<usize>)> = Vec::new();
    for (j, c) in columns.iter().enumerate() {
        for (module, excl) in [("debris-drift", "debris-drift-excl"), ("pleiades", "pleiades-excl"), ("pleiades-cosmo", "pleiades-cosmo-excl")] {
            if c.starts_with(&format!("{module}:loglik")) {
                extra.push((c.replacen(module, excl, 1), Some(j)));
            }
        }
    }
    let named: Vec<String> = columns.iter().cloned().chain(extra.iter().map(|e| e.0.clone())).collect();
    for c in &named {
        if c.contains(":loglik:H/") {
            extra.push((c.replacen(":loglik:H/", ":loglik:not-H/", 1), None));
        }
    }
    let new_width = width + extra.len();
    let mut values = Vec::with_capacity(rows * new_width);
    for r in 0..rows {
        let row = &raw[r * width..(r + 1) * width];
        values.extend_from_slice(row);
        for (_, src) in &extra {
            values.push(match src {
                Some(j) => {
                    if row[*j].is_nan() {
                        f64::NEG_INFINITY
                    } else {
                        row[*j]
                    }
                }
                None => f64::NAN,
            });
        }
    }
    columns.extend(extra.into_iter().map(|e| e.0));
    Seed { replicate: Replicate { seed: k, columns, values, modes }, core_final_modes }
}

fn decl(name: &str, observations: &[&str], alternatives: Vec<Alternatives>, absolute: bool) -> Declaration {
    Declaration {
        name: name.to_string(),
        prefix: format!("{name}:loglik"),
        observations: observations.iter().map(|s| s.to_string()).collect(),
        alternatives,
        absolute_scale: absolute,
    }
}

fn ocean(options: &[(&str, f64)]) -> Alternatives {
    Alternatives::new("ocean-model", options)
}

/// Pleiades as its hook declares it (lib.rs `alternatives()`, prior_h 0.5 from run.toml).
fn pleiades_faithful(name: &str, observations: &[&str]) -> Declaration {
    decl(
        name,
        observations,
        vec![
            Alternatives::new("pleiades-origin", &[("not-H", 0.5), ("H", 0.5)]),
            Alternatives::new("object-rating", &[("rho4-0", 0.25), ("rho4-0.25", 0.25), ("rho4-0.5", 0.25), ("rho4-1", 0.25)]),
            Alternatives::new("cluster-weight", &[("equal", 0.5), ("count", 0.5)]),
            ocean(&[(GLORYS, 0.5), (GLOBCURRENT, 0.5)]),
        ],
        true,
    )
}

/// PASS-0 Pleiades: the options the stand-in columns were computed for (rating 5 = rho4-0, equal cluster weights,
/// GLORYS12 only, so that the ocean-model option list equals drift's), with pleiades-origin kept so that every
/// product carrying it is labelled conditional on H.
fn pleiades_pass0(name: &str, observations: &[&str]) -> Declaration {
    decl(
        name,
        observations,
        vec![
            Alternatives::new("pleiades-origin", &[("not-H", 0.5), ("H", 0.5)]),
            Alternatives::new("object-rating", &[("rho4-0", 1.0)]),
            Alternatives::new("cluster-weight", &[("equal", 1.0)]),
            ocean(&[(GLORYS, 1.0)]),
        ],
        true,
    )
}

const PLEIADES_OBS: [&str; 1] = ["ga-rec2017-13:pleiades-objects"];
/// PASS-0: COSMO-SkyMed contacts have no observation ID in the Pleiades hook (it says COSMO enters no posterior).
const PLEIADES_COSMO_OBS: [&str; 2] = ["ga-rec2017-13:pleiades-objects", "cosmo-skymed:F1-F4"];
const DRIFT_OBS: [&str; 9] = [
    "debris:reunion-right-flaperon",
    "debris:mossel-bay-engine-cowling-roy",
    "debris:paindane-right-flap-fairing",
    "debris:vilanculos-horizontal-stabilizer-panel",
    "debris:mauritius-left-outboard-flap",
    "debris:rodrigues-door-closet-panel",
    "debris:chidenguele-right-fan-cowling",
    "debris:antsiraka-cabin-interior-panel",
    "debris:pemba-right-outboard-flap",
];
/// PASS-0: the hydroacoustics hook declares no observations (it returns 0.0). These name what the stand-in L_hyd uses.
const HYDRO_OBS: [&str; 5] = ["imos:3315", "imos:3376", "imos:3274", "imos:3275", "ims:H01W:kadri2024-table1"];
const SEABED_OBS: [&str; 2] = ["search:phase2-2014-2017", "search:bluefin-2014"];
/// Core (b)'s run.json observation assignment, all of it (the run stopped at m0019b).
const CORE_ALL: [&str; 28] = [
    "m0011.bfo", "m0011.bto", "m0019a.bto", "m0019b.bto", "m1825.bto", "m1828a.bfo", "m1828a.bto", "m1828b.bfo", "m1828b.bto",
    "m1839.bfo", "m1941.bfo", "m1941.bto", "m2041.bfo", "m2041.bto", "m2141.bfo", "m2141.bto", "m2241.bfo", "m2241.bto",
    "m2315.bfo", "radar:b1815", "radar:b1817", "radar:b1819", "radar:b1821", "radar:r0414", "radar:r0515", "radar:r0716",
    "radar:r1336", "radar:r1822",
];

fn num(x: f64) -> String {
    if x.is_finite() {
        format!("{x:.12e}")
    } else {
        "null".into()
    }
}

fn nums(v: &[f64]) -> String {
    format!("[{}]", v.iter().map(|x| num(*x)).collect::<Vec<_>>().join(","))
}

fn strs(v: &[String]) -> String {
    format!("[{}]", v.iter().map(|s| format!("{s:?}")).collect::<Vec<_>>().join(","))
}

fn ess_json(e: &[compose::Ess]) -> String {
    format!("[{}]", e.iter().map(|e| format!("[{},{}]", num(e.rows), num(e.parents))).collect::<Vec<_>>().join(","))
}

fn product_json(p: &Product, label: &str) -> String {
    let mut s = String::new();
    write!(s, "{{\"id\":{:?},\"label\":{:?},\"contains\":{},\"columns\":{},\"observations\":{},", p.id, label, strs(&p.contains), strs(&p.columns), strs(&p.observations)).unwrap();
    let cond: Vec<String> = p.conditional_on.iter().map(|(k, v)| format!("{k:?}:{v:?}")).collect();
    write!(s, "\"conditional_on\":{{{}}},\"log_evidence_increment\":{},", cond.join(","), num(p.log_evidence_increment)).unwrap();
    match &p.status {
        Status::Converged => write!(s, "\"status\":\"converged\",").unwrap(),
        Status::Unconverged { ess_parents, floor } => {
            write!(s, "\"status\":\"unconverged\",\"status_ess_parents\":{},\"status_floor\":{},", num(*ess_parents), num(*floor)).unwrap()
        }
    }
    write!(s, "\"ess_rows_parents\":{},", ess_json(&p.ess)).unwrap();
    let factors: Vec<String> = p
        .factors
        .iter()
        .map(|f| {
            format!(
                "{{\"name\":{:?},\"absolute_scale\":{},\"not_computed_rows\":[{}],\"not_computed_weight\":{},\"ess_rows_parents\":{}}}",
                f.name,
                f.absolute_scale,
                f.not_computed_rows.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(","),
                nums(&f.not_computed_weight),
                ess_json(&f.ess)
            )
        })
        .collect();
    write!(s, "\"factors\":[{}],", factors.join(",")).unwrap();
    let fams: Vec<String> = p
        .families
        .iter()
        .map(|f| format!("{{\"family\":{},\"base_mass\":{},\"mass\":{},\"log_bayes_factor\":{}}}", f.family, nums(&f.base_mass), nums(&f.mass), nums(&f.log_bayes_factor)))
        .collect();
    write!(s, "\"families\":[{}],", fams.join(",")).unwrap();
    let alts: Vec<String> = p
        .alternatives
        .iter()
        .map(|a| {
            format!(
                "{{\"name\":{:?},\"labels\":{},\"prior\":{},\"role\":\"{:?}\",\"declared_by\":{},\"posterior\":{}}}",
                a.name,
                strs(&a.labels),
                nums(&a.prior),
                a.role,
                strs(&a.declared_by),
                a.posterior.as_ref().map_or("null".into(), |v| nums(v))
            )
        })
        .collect();
    write!(s, "\"alternatives\":[{}],", alts.join(",")).unwrap();
    match &p.split_half {
        None => write!(s, "\"split_half\":null,").unwrap(),
        Some(h) => write!(
            s,
            "\"split_half\":{{\"log_evidence_increment\":{},\"max_probability_difference\":{}}},",
            nums(&h.log_evidence_increment),
            num(h.max_probability_difference)
        )
        .unwrap(),
    }
    let reps: Vec<String> = p
        .replicates
        .iter()
        .map(|r| {
            format!(
                "{{\"seed\":{},\"log_evidence\":{},\"log_evidence_increment\":{},\"modes\":[{}],\"not_computed_rows\":{}}}",
                r.seed,
                num(r.log_evidence),
                nums(&r.log_evidence_increment),
                r.modes.iter().map(|m| format!("[{},{},{}]", num(m.prior_weight), num(m.log_evidence), num(m.posterior_probability))).collect::<Vec<_>>().join(","),
                r.not_computed_rows
            )
        })
        .collect();
    write!(s, "\"replicates\":[{}]}}", reps.join(",")).unwrap();
    s
}

fn write_weights(out: &Path, p: &Product) {
    let dir = out.join("weights").join(&p.id);
    fs::create_dir_all(&dir).unwrap();
    for r in &p.replicates {
        let bytes: Vec<u8> = r.weights.iter().flat_map(|w| (*w as f32).to_le_bytes()).collect();
        fs::File::create(dir.join(format!("seed-{}.f32", r.seed))).unwrap().write_all(&bytes).unwrap();
    }
}

fn make_set(id: &str, modules: &[&str], given: &[(&str, &str)], tolerance: f64) -> Set {
    let mut s = Set::new(id, modules);
    s.given = given.iter().map(|(a, b)| (a.to_string(), b.to_string())).collect::<BTreeMap<_, _>>();
    s.tolerance = tolerance;
    s
}

struct Ctx<'a> {
    samples: &'a [Replicate],
    declarations: &'a [Declaration],
    out: &'a Path,
    products: Vec<String>,
    refusals: Vec<String>,
}

impl Ctx<'_> {
    /// Compose; on refusal, record the composer's message.
    fn attempt(&mut self, case: &str, base: &Product, id: &str, modules: &[&str], given: &[(&str, &str)], tol: f64) -> Option<Product> {
        match compose(base, self.samples, self.declarations, &make_set(id, modules, given, tol), None) {
            Ok(p) => Some(p),
            Err(e) => {
                self.refusals.push(format!("{{\"case\":{case:?},\"error\":{e:?}}}"));
                None
            }
        }
    }

    /// Compose a product that is reported (and optionally its weights written).
    #[allow(clippy::too_many_arguments)]
    fn product(&mut self, label: &str, base: &Product, id: &str, modules: &[&str], given: &[(&str, &str)], tol: f64, weights: bool) -> Option<Product> {
        let p = self.attempt(id, base, id, modules, given, tol)?;
        self.products.push(product_json(&p, label));
        if weights {
            write_weights(self.out, &p);
        }
        Some(p)
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let (input, out) = (PathBuf::from(&args[1]), PathBuf::from(&args[2]));
    fs::create_dir_all(&out).unwrap();
    let seeds: Vec<Seed> = (1..=4).map(|k| read_seed(&input, k)).collect();
    let core_modes: Vec<[Mode; MODE_COUNT]> = seeds.iter().map(|s| s.core_final_modes).collect();
    let samples: Vec<Replicate> = seeds.into_iter().map(|s| s.replicate).collect();

    let mut declarations = vec![
        Declaration::terminal("none+alive", &[], vec!["m0019b.burst-exists".into()]),
        Declaration::terminal("r600-bto+alive", &[], vec!["m0019a.bto".into(), "m0019b.burst-exists".into()]),
        decl("debris-drift", &DRIFT_OBS, vec![ocean(&[(GLORYS, 1.0)])], true),
        decl("debris-drift-excl", &DRIFT_OBS, vec![ocean(&[(GLORYS, 1.0)])], true),
        decl("hydroacoustics", &HYDRO_OBS, vec![], true),
        decl("seabed-search", &SEABED_OBS, vec![], true),
        pleiades_pass0("pleiades", &PLEIADES_OBS),
        pleiades_pass0("pleiades-excl", &PLEIADES_OBS),
        pleiades_pass0("pleiades-cosmo", &PLEIADES_COSMO_OBS),
        pleiades_pass0("pleiades-cosmo-excl", &PLEIADES_COSMO_OBS),
    ];
    let mut hydro_declared = decl("hydroacoustics-as-declared", &[], vec![], true);
    hydro_declared.prefix = "hydroacoustics:loglik".into();
    declarations.push(hydro_declared);
    let mut faithful = pleiades_faithful("pleiades-faithful", &PLEIADES_OBS);
    faithful.prefix = "pleiades:loglik".into();
    declarations.push(faithful);
    let mut drift_two = decl("debris-drift-two-models", &DRIFT_OBS, vec![ocean(&[(GLORYS, 0.5), (GLOBCURRENT, 0.5)])], true);
    drift_two.prefix = "debris-drift:loglik".into();
    declarations.push(drift_two);

    let mut cx = Ctx { samples: &samples, declarations: &declarations, out: &out, products: Vec::new(), refusals: Vec::new() };

    // Base: the filter posterior on the impact samples. Observations: core's run.json assignment restricted to the
    // epochs at or before the m0011 hand-off (PASS-0; run.json lists every observation through its m0019b stop).
    let base_obs: Vec<String> = CORE_ALL.iter().filter(|o| !o.starts_with("m0019")).map(|s| s.to_string()).collect();
    let p0 = Product::filter(&samples, base_obs).expect("filter product");
    // R1: the filter's own final per-mode evidence (core run.json) against the m0011 hand-off rows.
    let with_core: Vec<Replicate> = samples.iter().zip(&core_modes).map(|(s, m)| Replicate { seed: s.seed, columns: vec!["weight".into(), "mode".into()], values: s.values.chunks(s.columns.len()).flat_map(|row| [row[0], row[2]]).collect(), modes: *m }).collect();
    if let Err(e) = Product::filter(&with_core, CORE_ALL.iter().map(|s| s.to_string()).collect()) {
        cx.refusals.push(format!("{{\"case\":\"R1 filter product with core run.json final per-mode evidence\",\"error\":{e:?}}}"));
    }
    drop(with_core);
    let p0_full = Product::filter(&samples, CORE_ALL.iter().map(|s| s.to_string()).collect()).expect("filter product, full list");
    cx.products.push(product_json(&p0, "flight (filter hand-off weights)"));
    let h = [("pleiades-origin", "H")];

    for (opt, tag) in [("r600-bto+alive", "r600"), ("none+alive", "heldout")] {
        let term = format!("terminal:{opt}");
        if opt.starts_with("r600") {
            cx.attempt("R2 terminal option on a base listing every core observation", &p0_full, &format!("{tag}-eof-fullobs"), &[&term], &[], 1e-3);
        }
        let Some(p1) = cx.product("flight + end of flight (00:19 option)", &p0, &format!("{tag}-P1"), &[&term], &[], 1e-3, true) else { continue };
        cx.attempt(&format!("R3 {tag}: drift + hydro at the default tolerance"), &p1, &format!("{tag}-G-deftol"), &["debris-drift", "hydroacoustics"], &[], 1e-3);
        cx.attempt(
            &format!("R4 {tag}: drift + Pleiades, both exactly as their hooks declare"),
            &p1,
            &format!("{tag}-H-faithful"),
            &["debris-drift", "pleiades-faithful"],
            &[("pleiades-origin", "H"), ("object-rating", "rho4-0"), ("cluster-weight", "equal"), ("ocean-model", GLORYS)],
            PASS0_TOLERANCE,
        );
        cx.attempt(&format!("R5 {tag}: drift declared with both ocean models, given GLORYS12"), &p1, &format!("{tag}-G-two"), &["debris-drift-two-models"], &[("ocean-model", GLORYS)], PASS0_TOLERANCE);

        let g = cx.product("general: flight + EoF + drift + hydro", &p1, &format!("{tag}-G"), &["debris-drift", "hydroacoustics"], &[], PASS0_TOLERANCE, true);
        if let Some(g) = &g {
            if let Some(ga) = cx.product("general, after searches", g, &format!("{tag}-Ga"), &["seabed-search"], &[], 1e-3, true) {
                cx.attempt(&format!("R6 {tag}: seabed-search composed onto a product that contains it"), &ga, &format!("{tag}-Gaa"), &["seabed-search"], &[], 1e-3);
            }
            let m = g.moments(&samples, "latitude_deg").unwrap();
            cx.refusals.push(format!("{{\"case\":\"info {tag}-G composer weighted latitude mean and sd per replicate\",\"error\":{:?}}}", format!("{m:?}")));
        }
        if let Some(hp) = cx.product("Pleiades hypothesis: G + Pleiades, ocean model joint", &p1, &format!("{tag}-H"), &["debris-drift", "hydroacoustics", "pleiades"], &h, PASS0_TOLERANCE, true) {
            cx.product("Pleiades hypothesis, after searches", &hp, &format!("{tag}-Ha"), &["seabed-search"], &[], 1e-3, true);
            cx.attempt(&format!("R7 {tag}: Pleiades + COSMO composed onto a product that already used the Pleiades objects"), &hp, &format!("{tag}-Hb"), &["pleiades-cosmo"], &h, PASS0_TOLERANCE);
        }
        cx.product("flight + EoF + Pleiades (evidence-ratio denominator)", &p1, &format!("{tag}-PE"), &["pleiades"], &h, PASS0_TOLERANCE, false);
        cx.product("general, not-computed rows excluded", &p1, &format!("{tag}-Gx"), &["debris-drift-excl", "hydroacoustics"], &[], 1e-3, true);
        cx.product("Pleiades hypothesis, not-computed rows excluded", &p1, &format!("{tag}-Hx"), &["debris-drift-excl", "hydroacoustics", "pleiades-excl"], &h, 1e-3, true);
        cx.product("flight + EoF + Pleiades, not-computed excluded", &p1, &format!("{tag}-PEx"), &["pleiades-excl"], &h, 1e-3, false);
        cx.product("Pleiades + COSMO hypothesis", &p1, &format!("{tag}-Hc"), &["debris-drift", "hydroacoustics", "pleiades-cosmo"], &h, PASS0_TOLERANCE, false);
        cx.product("flight + EoF + Pleiades + COSMO", &p1, &format!("{tag}-PEc"), &["pleiades-cosmo"], &h, PASS0_TOLERANCE, false);
        cx.product("flight + EoF + drift", &p1, &format!("{tag}-D"), &["debris-drift"], &[], PASS0_TOLERANCE, false);
        cx.product("flight + EoF + hydro", &p1, &format!("{tag}-Y"), &["hydroacoustics"], &[], 1e-3, false);
        cx.product("flight + EoF + searched areas", &p1, &format!("{tag}-S"), &["seabed-search"], &[], 1e-3, false);
        cx.product("flight + EoF + hydro hook as declared (no observation IDs)", &p1, &format!("{tag}-Y0"), &["hydroacoustics-as-declared"], &[], 1e-3, false);
    }
    let mut f = fs::File::create(out.join("products.json")).unwrap();
    write!(f, "{{\"stratum_input\":{:?},\"products\":[{}],\n\"refusals\":[{}]}}", input.display().to_string(), cx.products.join(",\n"), cx.refusals.join(",\n")).unwrap();
    eprintln!("{} products, {} refusal/info records", cx.products.len(), cx.refusals.len());
}
