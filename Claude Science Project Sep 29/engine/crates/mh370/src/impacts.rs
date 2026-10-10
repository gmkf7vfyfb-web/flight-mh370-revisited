//! Impact samples: the layout of impacts.npy, the views impact modules see, and
//! `mh370 evaluate`.
//!
//! `mh370 evaluate <config.toml> [<override.toml>...] <samples> <out-dir>` runs the impact
//! modules of a configuration (those named in its `[[compose]]` sets and `[terminal]`) on a
//! samples file: each module's log-likelihood under every combination of its alternatives,
//! and its predictions. There is no filter and no composition, so any module can test against
//! a fixture in seconds.
//!
//! Samples are impacts.npy (column names from the run's run.json) or a plain CSV (no quoted
//! commas) whose header names `ImpactView` fields. A float field the samples lack reads as NaN,
//! an integer field as `usize::MAX` ("not given"). CSV rows pass through to the output with the
//! new columns appended; npy samples give a row-aligned evaluate.npy that starts with their
//! weight. Output columns are `<module>:loglik` (or `<module>:loglik:<option>/<option>...` under
//! alternatives) and `<module>:<prediction>`.

use crate::config::Config;
use crate::output::{code_revision, read_npy_rows, write_json, write_npy64};
use hypothesis::{Alternatives, Hypothesis, ImpactView};
use rayon::prelude::*;
use serde_json::json;
use std::path::{Path, PathBuf};

/// Leading columns of impacts.npy, in order. After them come `bto_residual_us:<epoch>` and
/// `bfo_innovation_hz:<epoch>` per terminal epoch, `latent:<name>` per latent of the terminal
/// module, and `loglik:<option>` (or `loglik:<option>/<bfo model>`) per data option.
pub const IMPACT_COLUMNS: [&str; 21] = [
    "weight", "parent", "mode", "alternative", "family", "unix_s", "latitude_deg", "longitude_deg",
    "velocity_east_mps", "velocity_north_mps", "velocity_up_mps", "flight_path_angle_deg", "mass_kg",
    "kinetic_energy_j", "vertical_kinetic_energy_j", "takeover_unix_s", "takeover_latitude_deg",
    "takeover_longitude_deg", "takeover_altitude_ft", "arc_distance_nm", "log_q_correction",
];

/// `ImpactView` fields read from sample columns of the same name: integers first.
const INTEGER_FIELDS: [&str; 4] = ["parent", "family", "mode", "alternative"];
const FLOAT_FIELDS: [&str; 14] = [
    "unix_s", "latitude_deg", "longitude_deg", "velocity_east_mps", "velocity_north_mps", "velocity_up_mps",
    "flight_path_angle_deg", "mass_kg", "kinetic_energy_j", "vertical_kinetic_energy_j", "takeover_unix_s",
    "takeover_latitude_deg", "takeover_longitude_deg", "takeover_altitude_ft",
];

/// Where each `ImpactView` field sits in a sample row, if the samples carry it.
pub struct Fields {
    integers: [Option<usize>; 4],
    floats: [Option<usize>; 14],
}

impl Fields {
    pub fn new(columns: &[String]) -> Self {
        let find = |name: &str| columns.iter().position(|c| c == name);
        Fields { integers: INTEGER_FIELDS.map(find), floats: FLOAT_FIELDS.map(find) }
    }

    /// The view of one sample row. `latents` is empty except for the terminal module's own hook.
    pub fn view<'a>(&self, row: &[f64], latents: &'a [f64]) -> ImpactView<'a> {
        let i = |k: usize| self.integers[k].map_or(usize::MAX, |c| row[c] as usize);
        let f = |k: usize| self.floats[k].map_or(f64::NAN, |c| row[c]);
        ImpactView {
            parent: i(0),
            family: i(1),
            mode: i(2),
            alternative: i(3),
            unix_s: f(0),
            latitude_deg: f(1),
            longitude_deg: f(2),
            velocity_east_mps: f(3),
            velocity_north_mps: f(4),
            velocity_up_mps: f(5),
            flight_path_angle_deg: f(6),
            mass_kg: f(7),
            kinetic_energy_j: f(8),
            vertical_kinetic_energy_j: f(9),
            takeover_unix_s: f(10),
            takeover_latitude_deg: f(11),
            takeover_longitude_deg: f(12),
            takeover_altitude_ft: f(13),
            latents,
        }
    }

    /// Integer fields must hold non-negative whole numbers wherever the samples carry them.
    fn check(&self, rows: &[f64], width: usize) -> Result<(), String> {
        for (k, column) in self.integers.iter().enumerate() {
            let Some(c) = column else { continue };
            if let Some(r) = rows.chunks_exact(width).position(|row| !(row[*c] >= 0.0 && row[*c].fract() == 0.0)) {
                return Err(format!("sample row {r}: {} must be a non-negative integer", INTEGER_FIELDS[k]));
            }
        }
        Ok(())
    }
}

/// A name that becomes part of a column name: not empty, and free of the separators.
pub fn check_name(what: &str, name: &str) -> Result<(), String> {
    if name.is_empty() || name.contains([',', '/', ':', '\n', '\r']) {
        return Err(format!("{what} {name:?}: names must be non-empty, without , / : or line breaks"));
    }
    Ok(())
}

/// Validate a module's declared alternatives: names and labels usable in columns, options
/// present and unique, priors positive and summing to one, a sweep label only on two options.
pub fn check_alternatives(module: &str, alternatives: &[Alternatives]) -> Result<(), String> {
    for (k, a) in alternatives.iter().enumerate() {
        check_name(&format!("{module}: alternative"), &a.name)?;
        for (label, _) in &a.options {
            check_name(&format!("{module}: option of {}", a.name), label)?;
        }
        let problem = if a.options.is_empty() {
            Some("has no options".to_string())
        } else if a.sweep_label.is_some() && a.options.len() != 2 {
            Some("has a sweep label but not two options".to_string())
        } else if alternatives[..k].iter().any(|b| b.name == a.name) {
            Some("is declared twice".to_string())
        } else if a.options.iter().enumerate().any(|(j, o)| a.options[..j].iter().any(|p| p.0 == o.0)) {
            Some("repeats an option label".to_string())
        } else if !a.options.iter().all(|o| o.1.is_finite() && o.1 > 0.0) {
            Some("has a prior that is not positive".to_string())
        } else {
            let total: f64 = a.options.iter().map(|o| o.1).sum();
            ((total - 1.0).abs() > 1e-6).then(|| format!("has priors summing to {total}, not 1"))
        };
        if let Some(problem) = problem {
            return Err(format!("{module}: alternative {} {problem}", a.name));
        }
    }
    Ok(())
}

/// Every combination of one option per alternative, first alternative varying slowest,
/// with its label: option labels joined by '/'. One empty combination if there are none.
pub fn combinations(alternatives: &[Alternatives]) -> Result<Vec<(Vec<usize>, String)>, String> {
    let count = alternatives.iter().try_fold(1usize, |n, a| n.checked_mul(a.options.len())).filter(|&n| n <= 4096);
    let count = count.ok_or("more than 4096 combinations of alternatives")?;
    Ok((0..count)
        .map(|mut k| {
            let mut choice = vec![0; alternatives.len()];
            for (d, a) in alternatives.iter().enumerate().rev() {
                choice[d] = k % a.options.len();
                k /= a.options.len();
            }
            let label = choice.iter().zip(alternatives).map(|(&c, a)| a.options[c].0.as_str()).collect::<Vec<_>>().join("/");
            (choice, label)
        })
        .collect())
}

/// Sample rows with named columns.
struct Samples {
    columns: Vec<String>,
    /// Row-major values, `columns.len()` per row.
    values: Vec<f64>,
    /// CSV samples: the header line and each row's text, passed through to the output.
    text: Option<(String, Vec<String>)>,
}

impl Samples {
    fn read(path: &Path) -> Result<Self, String> {
        if path.extension().is_some_and(|e| e == "npy") {
            let columns = impact_columns_for(path)?;
            let mut values = Vec::new();
            let mut width = None;
            read_npy_rows(path, |row| {
                width.get_or_insert(row.len());
                values.extend_from_slice(row);
            })?;
            if width.is_some_and(|w| w != columns.len()) {
                return Err(format!("{}: {} columns, but run.json names {}", path.display(), width.unwrap(), columns.len()));
            }
            return Ok(Samples { columns, values, text: None });
        }
        let text = std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
        let text = text.strip_prefix('\u{feff}').unwrap_or(&text);
        // (file line number, text) of each non-blank line.
        let mut lines = text.lines().enumerate().map(|(n, l)| (n + 1, l)).filter(|(_, l)| !l.trim().is_empty());
        let header = lines.next().ok_or_else(|| format!("{}: empty", path.display()))?.1.to_string();
        let columns: Vec<String> = header.split(',').map(|c| c.trim().to_string()).collect();
        if let Some(c) = columns.iter().enumerate().find(|(i, c)| columns[..*i].contains(c)) {
            return Err(format!("{}: column {} appears twice in the header", path.display(), c.1));
        }
        let known = |c: &String| c == "weight" || INTEGER_FIELDS.contains(&c.as_str()) || FLOAT_FIELDS.contains(&c.as_str()) || c.starts_with("latent:");
        let mut values = Vec::new();
        let mut rows = Vec::new();
        for (n, line) in lines {
            let cells: Vec<&str> = line.split(',').collect();
            if cells.len() != columns.len() {
                return Err(format!("{}:{n}: {} fields, the header has {}", path.display(), cells.len(), columns.len()));
            }
            for (cell, column) in cells.iter().zip(&columns) {
                // Columns the modules read must be numbers (empty = NaN); others pass through as text.
                let cell = cell.trim();
                let value = match cell.parse::<f64>() {
                    Ok(v) => v,
                    Err(_) if cell.is_empty() || !known(column) => f64::NAN,
                    Err(_) => return Err(format!("{}:{n}: {column}: not a number: {cell}", path.display())),
                };
                values.push(value);
            }
            rows.push(line.to_string());
        }
        Ok(Samples { columns, values, text: Some((header, rows)) })
    }
}

/// Column names of an impacts.npy: from the nearest run.json above it.
fn impact_columns_for(path: &Path) -> Result<Vec<String>, String> {
    let absolute = path.canonicalize().map_err(|e| format!("{}: {e}", path.display()))?;
    for dir in absolute.ancestors().skip(1) {
        let Ok(text) = std::fs::read_to_string(dir.join("run.json")) else { continue };
        let manifest: serde_json::Value = serde_json::from_str(&text).map_err(|e| format!("{}: {e}", dir.display()))?;
        if let Some(columns) = manifest["impact_columns"].as_array() {
            let columns: Vec<String> = columns.iter().filter_map(|c| c.as_str().map(str::to_string)).collect();
            if !columns.iter().zip(IMPACT_COLUMNS).all(|(c, expected)| c == expected) || columns.len() < IMPACT_COLUMNS.len() {
                return Err(format!("{}: impacts.npy has an older column layout; rerun the terminal stage", dir.display()));
            }
            return Ok(columns);
        }
    }
    Err(format!("{}: no run.json with impact_columns above it; use a CSV with named columns instead", path.display()))
}

/// One impact module, constructed, with what it declared.
struct Module {
    name: String,
    hypothesis: Box<dyn Hypothesis>,
    combinations: Vec<(Vec<usize>, String)>,
    predictions: Vec<String>,
    /// Sample columns holding the latents this module reads: the terminal module's own
    /// `latent_columns`, or for an impact module the names in `latents_read` (core request 4).
    latents: Vec<Option<usize>>,
    /// Those of them the samples lack (read as NaN), for the manifest.
    latents_missing: Vec<String>,
}

pub fn evaluate(args: &[String]) -> Result<(), String> {
    if args.len() < 3 {
        return Err("usage: mh370 evaluate <config.toml> [<override.toml>...] <samples> <out-dir>".into());
    }
    let paths: Vec<PathBuf> = args.iter().map(PathBuf::from).collect();
    let (configs, rest) = paths.split_at(paths.len() - 2);
    let (samples_path, out) = (&rest[0], &rest[1]);
    let config = crate::config::load(configs)?;
    let roles = config.roles()?;
    let names: Vec<String> = roles.terminal.iter().chain(&roles.impact).cloned().collect();
    if names.is_empty() {
        return Err("no impact modules: name them in a [[compose]] set (or [terminal])".into());
    }
    let samples = Samples::read(samples_path)?;
    let width = samples.columns.len();
    let modules = names.iter().map(|name| module(&config, name, roles.terminal.as_ref() == Some(name), &samples.columns)).collect::<Result<Vec<_>, _>>()?;

    let (columns, results) = run_modules(&modules, &samples)?;
    write_outputs(&samples, &columns, &results, out)?;
    let rows = samples.values.len() / width;
    write_json(
        &out.join("evaluate.json"),
        &json!({
            "samples": samples_path,
            "rows": rows,
            "columns": output_columns(&samples, &columns),
            "config_paths": configs,
            "code_revision": code_revision(),
            "modules": modules.iter().map(|m| json!({
                "name": m.name,
                "parameters": config.hypotheses[&m.name],
                "observations": m.hypothesis.observations(),
                "alternatives": m.hypothesis.alternatives().iter().map(|a| json!({"name": a.name, "options": a.options, "sweep_label": a.sweep_label})).collect::<Vec<_>>(),
                "absolute_scale": m.hypothesis.absolute_scale(),
                "prediction_columns": m.predictions,
                "latents_read": m.hypothesis.latents_read(),
                "latents_missing": m.latents_missing,
            })).collect::<Vec<_>>(),
        }),
    )?;
    eprintln!("evaluated {} modules on {rows} samples: {}", modules.len(), out.display());
    Ok(())
}

/// Every module on every sample: the module columns' names, and per sample one row of values
/// (npy samples: their weight first).
fn run_modules(modules: &[Module], samples: &Samples) -> Result<(Vec<String>, Vec<f64>), String> {
    let width = samples.columns.len();
    let fields = Fields::new(&samples.columns);
    fields.check(&samples.values, width)?;
    let mut columns = Vec::new();
    for m in modules {
        for (_, label) in &m.combinations {
            columns.push(if label.is_empty() { format!("{}:loglik", m.name) } else { format!("{}:loglik:{label}", m.name) });
        }
        columns.extend(m.predictions.iter().map(|p| format!("{}:{p}", m.name)));
    }
    let weight = npy_weight(samples);
    let (lead, stride) = (usize::from(weight.is_some()), columns.len() + usize::from(weight.is_some()));
    let mut results = vec![f64::NAN; samples.values.len() / width * stride];
    let latents_needed = modules.iter().map(|m| m.latents.len()).max().unwrap_or(0);
    results.par_chunks_mut(stride).zip(samples.values.par_chunks_exact(width)).enumerate().try_for_each_init(
        || Vec::with_capacity(latents_needed),
        |latents, (r, (out, row))| {
            if let Some(w) = weight {
                out[0] = row[w];
            }
            let mut k = lead;
            for m in modules {
                latents.clear();
                latents.extend(m.latents.iter().map(|c| c.map_or(f64::NAN, |c| row[c])));
                let view = fields.view(row, latents);
                for (choice, label) in &m.combinations {
                    out[k] = m.hypothesis.impact_log_likelihood(&view, choice);
                    if out[k] == f64::INFINITY {
                        return Err(format!("{} returned +inf at sample row {r} ({label})", m.name));
                    }
                    k += 1;
                }
                m.hypothesis.predict(&view, &mut out[k..k + m.predictions.len()]);
                k += m.predictions.len();
            }
            Ok(())
        },
    )?;
    Ok((columns, results))
}

/// npy samples carry their weight into evaluate.npy; CSV samples pass every column through.
fn npy_weight(samples: &Samples) -> Option<usize> {
    samples.columns.iter().position(|c| c == "weight").filter(|_| samples.text.is_none())
}

fn output_columns(samples: &Samples, columns: &[String]) -> Vec<String> {
    npy_weight(samples).map(|_| "weight".to_string()).into_iter().chain(columns.iter().cloned()).collect()
}

/// evaluate.csv (CSV samples, their rows passed through) or evaluate.npy (float64).
fn write_outputs(samples: &Samples, columns: &[String], results: &[f64], out: &Path) -> Result<(), String> {
    std::fs::create_dir_all(out).map_err(|e| format!("{}: {e}", out.display()))?;
    let names = output_columns(samples, columns);
    let stride = names.len();
    match &samples.text {
        Some((header, lines)) => {
            let mut text = format!("{header},{}\n", names.join(","));
            for (line, values) in lines.iter().zip(results.chunks_exact(stride)) {
                text += line;
                for v in values {
                    text += &format!(",{v}");
                }
                text.push('\n');
            }
            let path = out.join("evaluate.csv");
            std::fs::write(&path, text).map_err(|e| format!("{}: {e}", path.display()))
        }
        None => write_npy64(&out.join("evaluate.npy"), &[results.len() / stride, stride], results),
    }
}

fn module(config: &Config, name: &str, terminal: bool, columns: &[String]) -> Result<Module, String> {
    let hypothesis = hypotheses::construct(name, &config.hypotheses[name])?;
    let alternatives = hypothesis.alternatives();
    check_alternatives(name, &alternatives)?;
    let latent_names = match (terminal, hypothesis.terminal()) {
        (true, Some(t)) => t.latent_columns(),
        (true, None) => return Err(format!("{name} is named in [terminal] but has no terminal model")),
        (false, _) => hypothesis.latents_read(),
    };
    let (latents, latents_missing) = latent_map(name, &latent_names, columns)?;
    if !latents_missing.is_empty() {
        eprintln!("{name}: the samples carry no column for latent(s) {}; they read as NaN", latents_missing.join(", "));
    }
    let predictions = hypothesis.prediction_columns();
    for (i, p) in predictions.iter().enumerate() {
        check_name(&format!("{name}: prediction"), p)?;
        if p == "loglik" || predictions[..i].contains(p) {
            return Err(format!("{name}: prediction {p} is reserved or declared twice"));
        }
    }
    Ok(Module { name: name.to_string(), combinations: combinations(&alternatives)?, predictions, latents, latents_missing, hypothesis })
}

/// Sample columns for latents named without the `latent:` prefix, and the names the samples
/// lack (core request 4).
fn latent_map(module: &str, names: &[String], columns: &[String]) -> Result<(Vec<Option<usize>>, Vec<String>), String> {
    for (i, l) in names.iter().enumerate() {
        if l.is_empty() || l.starts_with("latent:") || names[..i].contains(l) {
            return Err(format!("{module}: latent {l:?} is empty, carries the latent: prefix, or is named twice"));
        }
    }
    let at: Vec<Option<usize>> = names.iter().map(|l| columns.iter().position(|c| *c == format!("latent:{l}"))).collect();
    let missing = names.iter().zip(&at).filter(|(_, c)| c.is_none()).map(|(l, _)| l.clone()).collect();
    Ok((at, missing))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::output::read_npy_rows;

    /// A module with one alternative whose log-likelihood depends on the choice, the latitude
    /// and whether the family was given, and one prediction.
    struct Probe;

    impl Hypothesis for Probe {
        fn alternatives(&self) -> Vec<Alternatives> {
            vec![Alternatives::new("offset", &[("low", 0.5), ("high", 0.5)])]
        }
        fn prediction_columns(&self) -> Vec<String> {
            vec!["doubled latitude (deg)".into()]
        }
        fn impact_log_likelihood(&self, impact: &ImpactView, choice: &[usize]) -> f64 {
            let given = if impact.family == usize::MAX { 0.0 } else { 100.0 };
            impact.latitude_deg + 10.0 * choice[0] as f64 + given
        }
        fn predict(&self, impact: &ImpactView, out: &mut [f64]) {
            out[0] = 2.0 * impact.latitude_deg;
        }
    }

    fn probe() -> Module {
        let alternatives = Probe.alternatives();
        Module { name: "probe".into(), combinations: combinations(&alternatives).unwrap(), predictions: Probe.prediction_columns(), latents: Vec::new(), latents_missing: Vec::new(), hypothesis: Box::new(Probe) }
    }

    #[test]
    fn combinations_run_first_alternative_slowest_and_names_are_checked() {
        let a = Alternatives::new("a", &[("a1", 0.5), ("a2", 0.5)]);
        let b = Alternatives::new("b", &[("b1", 0.2), ("b2", 0.3), ("b3", 0.5)]);
        let labels: Vec<String> = combinations(&[a.clone(), b.clone()]).unwrap().into_iter().map(|(c, l)| format!("{c:?}{l}")).collect();
        assert_eq!(labels[..4], ["[0, 0]a1/b1", "[0, 1]a1/b2", "[0, 2]a1/b3", "[1, 0]a2/b1"]);
        assert_eq!(combinations(&[]).unwrap(), vec![(vec![], String::new())]);
        assert!(check_alternatives("m", &[a.clone(), b]).is_ok());
        let bad = |options: &[(&str, f64)]| check_alternatives("m", &[Alternatives::new("x", options)]).is_err();
        assert!(bad(&[("p", 0.5), ("q", 0.6)]), "priors must sum to one");
        assert!(bad(&[("p", 0.5), ("p", 0.5)]), "labels must be unique");
        assert!(bad(&[("p,q", 0.5), ("r", 0.5)]) && bad(&[("p/q", 0.5), ("r", 0.5)]) && bad(&[("", 1.0)]));
        let swept = Alternatives { sweep_label: Some("odds".into()), ..Alternatives::new("x", &[("p", 0.2), ("q", 0.3), ("r", 0.5)]) };
        assert!(check_alternatives("m", &[swept]).is_err(), "a sweep needs two options");
        assert!(check_alternatives("m", &[a.clone(), a]).is_err(), "names must be unique");
    }

    /// Core request 4: an impact module reads the terminal module's latents by name, in the
    /// order it asked for them, NaN for one the samples lack, and bad names are refused.
    #[test]
    fn impact_modules_read_terminal_latents_by_name() {
        struct Reader;
        impl Hypothesis for Reader {
            fn latents_read(&self) -> Vec<String> {
                vec!["debris_class".into(), "not_emitted".into(), "impact_bank_deg".into()]
            }
            fn prediction_columns(&self) -> Vec<String> {
                vec!["first".into(), "second".into(), "third".into()]
            }
            fn predict(&self, impact: &ImpactView, out: &mut [f64]) {
                out.copy_from_slice(impact.latents);
            }
        }
        let columns: Vec<String> = ["weight", "latitude_deg", "latent:impact_bank_deg", "latent:spiral_divergent", "latent:debris_class"].iter().map(|c| c.to_string()).collect();
        let (at, missing) = latent_map("reader", &Reader.latents_read(), &columns).unwrap();
        assert_eq!(at, [Some(4), None, Some(2)]);
        assert_eq!(missing, ["not_emitted"]);
        for bad in [vec!["latent:debris_class".to_string()], vec!["a".into(), "a".into()], vec![String::new()]] {
            assert!(latent_map("reader", &bad, &columns).is_err(), "{bad:?}");
        }
        let dir = std::env::temp_dir().join(format!("latents-test-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let csv = dir.join("samples.csv");
        std::fs::write(&csv, format!("{}\n0.5,-35.0,12.5,1,2\n", columns.join(","))).unwrap();
        let samples = Samples::read(&csv).unwrap();
        std::fs::remove_dir_all(&dir).unwrap();
        let m = Module { name: "reader".into(), combinations: combinations(&[]).unwrap(), predictions: Reader.prediction_columns(), latents: at, latents_missing: missing, hypothesis: Box::new(Reader) };
        let (_, results) = run_modules(&[m], &samples).unwrap();
        // CSV samples: no weight column is led; the row is loglik (NaN default) then predictions.
        let tail = &results[results.len() - 3..];
        assert_eq!((tail[0], tail[2]), (2.0, 12.5));
        assert!(tail[1].is_nan(), "a latent the samples lack must read as NaN");
    }

    /// CSV samples pass through with their text columns; npy samples lead with their weight.
    /// A family the samples lack reads as "not given" (usize::MAX), never as family 0.
    #[test]
    fn evaluate_round_trips_csv_and_npy_samples() {
        let dir = std::env::temp_dir().join(format!("evaluate-test-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let csv = dir.join("samples.csv");
        std::fs::write(&csv, "\u{feff}weight,latitude_deg,label\n0.25,-30.5,north\n\n0.75,-40.0,south\n").unwrap();
        let samples = Samples::read(&csv).unwrap();
        let (columns, results) = run_modules(&[probe()], &samples).unwrap();
        assert_eq!(columns, ["probe:loglik:low", "probe:loglik:high", "probe:doubled latitude (deg)"]);
        write_outputs(&samples, &columns, &results, &dir.join("csv")).unwrap();
        let text = std::fs::read_to_string(dir.join("csv/evaluate.csv")).unwrap();
        let lines: Vec<&str> = text.lines().collect();
        assert_eq!(lines, [
            "weight,latitude_deg,label,probe:loglik:low,probe:loglik:high,probe:doubled latitude (deg)",
            "0.25,-30.5,north,-30.5,-20.5,-61",
            "0.75,-40.0,south,-40,-30,-80",
        ]);

        // impacts.npy samples: the column names come from the run.json above them.
        let mut names: Vec<String> = IMPACT_COLUMNS.iter().map(|c| c.to_string()).collect();
        names.push("loglik:none".into());
        std::fs::write(dir.join("run.json"), json!({"impact_columns": names}).to_string()).unwrap();
        let (width, lat, family) = (names.len(), IMPACT_COLUMNS.iter().position(|c| *c == "latitude_deg").unwrap(), 4);
        let mut values = vec![0.0; 2 * width];
        values[0] = 0.4;
        values[width] = 0.6;
        values[lat] = -35.0;
        values[width + lat] = -36.0;
        values[width + family] = 3.0;
        std::fs::create_dir_all(dir.join("seed-1")).unwrap();
        write_npy64(&dir.join("seed-1/impacts.npy"), &[2, width], &values).unwrap();
        let samples = Samples::read(&dir.join("seed-1/impacts.npy")).unwrap();
        let (columns, results) = run_modules(&[probe()], &samples).unwrap();
        write_outputs(&samples, &columns, &results, &dir.join("npy")).unwrap();
        let mut back = Vec::new();
        read_npy_rows(&dir.join("npy/evaluate.npy"), |row| back.push(row.to_vec())).unwrap();
        std::fs::remove_dir_all(&dir).unwrap();
        assert_eq!(output_columns(&samples, &columns)[0], "weight");
        assert_eq!(back, [vec![0.4, 65.0, 75.0, -70.0], vec![0.6, 64.0, 74.0, -72.0]]);
    }
}
