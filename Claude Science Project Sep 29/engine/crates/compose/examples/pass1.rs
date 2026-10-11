//! Composer pass 1 on core run C: the pass-0 driver (`pass0.rs`) adapted to run C's compact inputs.
//!
//! run C NOT CONVERGED; EoF physics provisional, no structural limit (G13); hydro predictive, not calibrated;
//! drift GLORYS12 only, current nodes; GlobCurrent excluded (F1). Architecture stand-in; the composer module reviews it.
//!
//! Differences from pass0.rs (declared in results/composer-pass1-run-c.md): inputs are float32 (`seed-<k>.f32` +
//! `seed-<k>.json` from results/composer-pass1-run-c/prep_inputs_c.py); any number of seeds; the source split-half floor is
//! an argument (0.924 for 8 replicates); ONE terminal option per invocation, so that only its column is held in memory
//! (peak RAM); no not-H Pleiades columns (ruling 8 / merge 960b3147: a column excluded by `given` may be absent); the
//! refusal cases R1-R7 of pass 0 are not repeated; products added: G and H without hydro, the rho correlated-error
//! Pleiades sensitivities.
//!
//! Usage: pass1 <stratum input dir> <out dir> <n seeds> <option column, e.g. r600-bto+unpowered> <observations, comma
//!        separated> <source split-half statistic> <floor> <description>

use compose::{compose, Declaration, Mode, Product, Replicate, Set, SplitHalfCheck, Status, MODE_COUNT};
use hypothesis::Alternatives;
use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::fs;
use std::io::{Read, Write};
use std::path::{Path, PathBuf};

const GLORYS: &str = "glorys12v1+era5-wind10";
/// Pass-0 tolerance on not-computed weight for sets with drift (the default 1e-3 refuses them; recorded).
const PASS0_TOLERANCE: f64 = 0.5;

fn json_str_list(s: &str, key: &str) -> Vec<String> {
    let k = s.find(&format!("\"{key}\"")).expect("key");
    let a = k + s[k..].find('[').unwrap();
    let b = a + s[a..].find(']').unwrap();
    s[a + 1..b].split(',').map(|x| x.trim().trim_matches(|c| c == '"' || c == '\n' || c == ' ').to_string()).filter(|x| !x.is_empty()).collect()
}

fn json_num(s: &str, key: &str) -> f64 {
    let k = s.find(&format!("\"{key}\"")).expect("key");
    let a = k + s[k..].find(':').unwrap() + 1;
    let t: String = s[a..].trim_start().chars().take_while(|c| !matches!(c, ',' | '}' | '\n')).collect();
    let t = t.trim();
    if t == "null" { f64::NEG_INFINITY } else { t.parse().expect("number") }
}

/// The header's five modes (prior_weight, log_evidence, posterior_probability), in order.
fn json_modes(s: &str) -> [Mode; MODE_COUNT] {
    let k = s.find("\"modes\"").unwrap();
    let body = &s[k..];
    let mut out = Vec::new();
    let mut at = 0;
    for _ in 0..MODE_COUNT {
        let a = at + body[at..].find('{').unwrap();
        let b = a + body[a..].find('}').unwrap();
        let o = &body[a..=b];
        out.push(Mode { prior_weight: json_num(o, "prior_weight"), log_evidence: json_num(o, "log_evidence"), posterior_probability: json_num(o, "posterior_probability") });
        at = b + 1;
    }
    out.try_into().unwrap()
}

/// Read one seed, keeping the common columns, the chosen terminal column, and every module column; adding the
/// "not-computed excluded" copies (NaN -> -inf) for drift and the Pleiades column sets.
fn read_seed(dir: &Path, k: u64, terminal_col: &str) -> Replicate {
    let hdr = fs::read_to_string(dir.join(format!("seed-{k}.json"))).expect("json");
    let rows = json_num(&hdr, "rows") as usize;
    let all = json_str_list(&hdr, "columns");
    let keep: Vec<usize> = (0..all.len()).filter(|&j| !all[j].starts_with("loglik:") || all[j] == terminal_col).collect();
    assert!(keep.iter().any(|&j| all[j] == terminal_col), "seed {k}: no column {terminal_col}");
    let mut columns: Vec<String> = keep.iter().map(|&j| all[j].clone()).collect();
    let mut extra: Vec<(String, usize)> = Vec::new();
    for (i, c) in columns.iter().enumerate() {
        for (module, excl) in [("debris-drift", "debris-drift-excl"), ("pleiades", "pleiades-excl"), ("pleiades-cosmo", "pleiades-cosmo-excl")] {
            if c.starts_with(&format!("{module}:loglik")) {
                extra.push((c.replacen(module, excl, 1), i));
            }
        }
    }
    let mut bytes = Vec::new();
    fs::File::open(dir.join(format!("seed-{k}.f32"))).unwrap().read_to_end(&mut bytes).unwrap();
    let width = all.len();
    assert_eq!(bytes.len(), rows * width * 4, "seed {k}: file size");
    let new_width = keep.len() + extra.len();
    let mut values = Vec::with_capacity(rows * new_width);
    let mut row = vec![0f64; keep.len()];
    for r in 0..rows {
        let b = &bytes[r * width * 4..(r + 1) * width * 4];
        for (i, &j) in keep.iter().enumerate() {
            row[i] = f32::from_le_bytes(b[j * 4..j * 4 + 4].try_into().unwrap()) as f64;
        }
        values.extend_from_slice(&row);
        for (_, src) in &extra {
            values.push(if row[*src].is_nan() { f64::NEG_INFINITY } else { row[*src] });
        }
    }
    drop(bytes);
    columns.extend(extra.into_iter().map(|e| e.0));
    Replicate { seed: k, columns, values, modes: json_modes(&hdr) }
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
        Status::Unconverged { ess_parents, floor, reasons } => write!(
            s,
            "\"status\":\"unconverged\",\"status_ess_parents\":{},\"status_floor\":{},\"status_reasons\":{},",
            num(*ess_parents),
            num(*floor),
            strs(reasons)
        )
        .unwrap(),
    }
    let chk = |c: &SplitHalfCheck| format!("{{\"what\":{:?},\"statistic\":{},\"threshold\":{},\"at_least\":{},\"passed\":{}}}", c.what, num(c.statistic), num(c.threshold), c.at_least, c.passed);
    write!(s, "\"source_split_half\":{},", p.source_split_half.as_ref().map_or("null".into(), chk)).unwrap();
    write!(s, "\"factor_split_half\":[{}],", p.factor_split_half.iter().map(chk).collect::<Vec<_>>().join(",")).unwrap();
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
    let a: Vec<String> = std::env::args().collect();
    let (input, out) = (PathBuf::from(&a[1]), PathBuf::from(&a[2]));
    let nseeds: u64 = a[3].parse().unwrap();
    let opt = a[4].clone();
    let term_obs: Vec<String> = a[5].split(',').map(String::from).collect();
    let source = SplitHalfCheck::overlap(&a[8], a[6].parse().unwrap(), a[7].parse().unwrap());
    fs::create_dir_all(&out).unwrap();
    let terminal_col = format!("loglik:{opt}");
    let samples: Vec<Replicate> = (1..=nseeds).map(|k| read_seed(&input, k, &terminal_col)).collect();
    eprintln!("read {} seeds", samples.len());

    let declarations = vec![
        Declaration::terminal(&opt, &[], term_obs),
        decl("debris-drift", &DRIFT_OBS, vec![ocean(&[(GLORYS, 1.0)])], true),
        decl("debris-drift-excl", &DRIFT_OBS, vec![ocean(&[(GLORYS, 1.0)])], true),
        decl("hydroacoustics", &HYDRO_OBS, vec![], true),
        decl("seabed-search", &SEABED_OBS, vec![], true),
        pleiades_pass0("pleiades", &PLEIADES_OBS),
        pleiades_pass0("pleiades-excl", &PLEIADES_OBS),
        pleiades_pass0("pleiades-cosmo", &PLEIADES_COSMO_OBS),
        pleiades_pass0("pleiades-cosmo-excl", &PLEIADES_COSMO_OBS),
        pleiades_pass0("pleiades-rho0", &PLEIADES_COSMO_OBS),
        pleiades_pass0("pleiades-rho05", &PLEIADES_COSMO_OBS),
    ];
    let mut cx = Ctx { samples: &samples, declarations: &declarations, out: &out, products: Vec::new(), refusals: Vec::new() };
    // Base: the filter posterior on the impact samples; observations restricted to epochs at or before the m0011 hand-off.
    let base_obs: Vec<String> = CORE_ALL.iter().filter(|o| !o.starts_with("m0019")).map(|s| s.to_string()).collect();
    let p0 = Product::filter(&samples, base_obs).expect("filter product").with_source_split_half(source);
    cx.products.push(product_json(&p0, "flight (filter hand-off weights)"));
    let h = [("pleiades-origin", "H")];
    let tag = "o";
    let term = format!("terminal:{opt}");
    let Some(p1) = cx.product("flight + end of flight (00:19 option)", &p0, &format!("{tag}-P1"), &[&term], &[], 1e-3, true) else {
        panic!("P1 refused: {:?}", cx.refusals)
    };
    if let Some(g) = cx.product("general: flight + EoF + drift + hydro", &p1, &format!("{tag}-G"), &["debris-drift", "hydroacoustics"], &[], PASS0_TOLERANCE, true) {
        cx.product("general, after searches", &g, &format!("{tag}-Ga"), &["seabed-search"], &[], 1e-3, true);
    }
    if let Some(d) = cx.product("general without hydro: flight + EoF + drift", &p1, &format!("{tag}-D"), &["debris-drift"], &[], PASS0_TOLERANCE, true) {
        cx.product("general without hydro, after searches", &d, &format!("{tag}-Da"), &["seabed-search"], &[], 1e-3, true);
    }
    if let Some(hp) = cx.product("Pleiades hypothesis: G + Pleiades, ocean model joint", &p1, &format!("{tag}-H"), &["debris-drift", "hydroacoustics", "pleiades"], &h, PASS0_TOLERANCE, true) {
        cx.product("Pleiades hypothesis, after searches", &hp, &format!("{tag}-Ha"), &["seabed-search"], &[], 1e-3, true);
    }
    if let Some(hn) = cx.product("Pleiades hypothesis without hydro", &p1, &format!("{tag}-Hn"), &["debris-drift", "pleiades"], &h, PASS0_TOLERANCE, true) {
        cx.product("Pleiades hypothesis without hydro, after searches", &hn, &format!("{tag}-Hna"), &["seabed-search"], &[], 1e-3, true);
    }
    cx.product("flight + EoF + Pleiades (evidence-ratio denominator)", &p1, &format!("{tag}-PE"), &["pleiades"], &h, PASS0_TOLERANCE, false);
    cx.product("general, not-computed rows excluded", &p1, &format!("{tag}-Gx"), &["debris-drift-excl", "hydroacoustics"], &[], 1e-3, true);
    cx.product("Pleiades hypothesis, not-computed rows excluded", &p1, &format!("{tag}-Hx"), &["debris-drift-excl", "hydroacoustics", "pleiades-excl"], &h, 1e-3, true);
    cx.product("flight + EoF + Pleiades, not-computed excluded", &p1, &format!("{tag}-PEx"), &["pleiades-excl"], &h, 1e-3, false);
    cx.product("Pleiades + COSMO hypothesis", &p1, &format!("{tag}-Hc"), &["debris-drift", "hydroacoustics", "pleiades-cosmo"], &h, PASS0_TOLERANCE, false);
    cx.product("flight + EoF + Pleiades + COSMO", &p1, &format!("{tag}-PEc"), &["pleiades-cosmo"], &h, PASS0_TOLERANCE, false);
    cx.product("Pleiades + COSMO, correlated errors rho 0 (surface)", &p1, &format!("{tag}-Hr0"), &["debris-drift", "hydroacoustics", "pleiades-rho0"], &h, PASS0_TOLERANCE, true);
    cx.product("flight + EoF + Pleiades + COSMO rho 0", &p1, &format!("{tag}-PEr0"), &["pleiades-rho0"], &h, PASS0_TOLERANCE, false);
    cx.product("Pleiades + COSMO, correlated errors rho 0.5", &p1, &format!("{tag}-Hr5"), &["debris-drift", "hydroacoustics", "pleiades-rho05"], &h, PASS0_TOLERANCE, true);
    cx.product("flight + EoF + Pleiades + COSMO rho 0.5", &p1, &format!("{tag}-PEr5"), &["pleiades-rho05"], &h, PASS0_TOLERANCE, false);
    cx.product("flight + EoF + hydro", &p1, &format!("{tag}-Y"), &["hydroacoustics"], &[], 1e-3, false);
    cx.product("flight + EoF + searched areas", &p1, &format!("{tag}-S"), &["seabed-search"], &[], 1e-3, false);
    let mut f = fs::File::create(out.join("products.json")).unwrap();
    write!(f, "{{\"stratum_input\":{:?},\"option\":{:?},\"products\":[{}],\n\"refusals\":[{}]}}", input.display().to_string(), opt, cx.products.join(",\n"), cx.refusals.join(",\n")).unwrap();
    eprintln!("{} products, {} refusal/info records", cx.products.len(), cx.refusals.len());
}
