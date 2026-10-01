//! What the app needs to know about this estimate, as JSON: the engines it can run, the
//! model constants in force, the controls it may change and the data behind them.
//!
//! Everything here is read from the code and the repository rather than restated, so a
//! panel cannot drift from the run it describes: model constants come from
//! `flight::Parameters` and `crates/satcom`, engines from the config files, hypotheses
//! from their own `hypothesis.toml`, and provenance from README.md.

use crate::config::Config;
use flight::Parameters;
use hypothesis::{PriorSpec, MODES};
use serde_json::{json, Value};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

pub fn main(args: &[String]) -> Result<(), String> {
    let root = root_from(args)?;
    println!("{}", serde_json::to_string_pretty(&describe(&root)?).map_err(|e| e.to_string())?);
    Ok(())
}

/// `--root <dir>`, else the first ancestor of the working directory holding `config/davey2016.toml`.
pub fn root_from(args: &[String]) -> Result<PathBuf, String> {
    if let Some(i) = args.iter().position(|a| a == "--root") {
        return args.get(i + 1).map(PathBuf::from).ok_or_else(|| "--root needs a directory".into());
    }
    let here = std::env::current_dir().map_err(|e| e.to_string())?;
    here.ancestors()
        .find(|dir| dir.join("config/davey2016.toml").is_file())
        .map(Path::to_path_buf)
        .ok_or_else(|| "no config/davey2016.toml above the working directory; pass --root".into())
}

pub fn describe(root: &Path) -> Result<Value, String> {
    let base_path = root.join("config/davey2016.toml");
    let base = crate::config::load(&[base_path.clone()])?;
    let params = base.dynamics.apply(Parameters::default());
    Ok(json!({
        "root": root,
        "code_revision": crate::output::code_revision(),
        "model": "Davey et al. (2016), Bayesian Methods in the Search for MH370: ch. 5-8 model, Fig. 10.3 result",
        "threads": rayon::current_num_threads(),
        "engines": engines(root)?,
        "hypotheses": hypothesis_directories(root)?,
        "hypothesis_api": {
            "hooks": doc_comment(&root.join("crates/hypothesis/src/lib.rs")),
            "new": "make new-hypothesis H=<name>, then rebuild the app to enable it",
        },
        "controls": controls(&base, &params),
        "constants": constants(&params),
        "data": data_sources(root, &base),
        "departures": readme_section(root, "Departures from the paper"),
        "runs": existing_runs(root),
        "grid": {"latitude_step_deg": crate::summary::GRID_STEP, "smoothing_deg": crate::summary::SMOOTH_DEG,
                 "shoulder": [crate::summary::SHOULDER.0, crate::summary::SHOULDER.1]},
    }))
}

/// The model constants a run used, recorded in its own manifest.
pub fn assumptions(config: &Config, params: &Parameters, spec: &PriorSpec) -> Value {
    json!({
        "dynamics": constants(params)["dynamics"],
        "measurement": constants(params)["measurement"],
        "prior": {
            "time_utc": config.prior.time_utc, "latitude_deg": spec.latitude_deg, "longitude_deg": spec.longitude_deg,
            "position_sd_nm": spec.position_sd_nm, "track_deg": spec.track_deg, "track_sd_deg": spec.track_sd_deg,
            "mach_range": spec.mach_range, "mach_gaussian": spec.mach_gaussian,
            "altitude_levels": spec.altitude_levels.len(),
            "mode_weights": MODES.iter().zip(spec.mode_weights).collect::<Vec<_>>(),
            "bfo_bias_mean_hz": config.bfo_bias.mean_hz, "bfo_bias_sd_hz": config.bfo_bias.sd_hz,
            "bfo_bias_drift_hz2_per_s": config.bfo_bias.drift_hz2_per_s.unwrap_or(0.0),
        },
        "environment": {"wind_scale": config.environment.wind_scale},
        "sampler": {
            "particles_per_mode": config.particles_per_mode,
            "seeds": config.seeds,
            "resample_ess_fraction": config.resample_ess_fraction,
            "scheme": "one filter per autopilot mode combined by evidence; systematic resampling; \
                       Gibbs refresh of the manoeuvre time constant after each resampling",
        },
        "dynamics_overrides": config.dynamics,
    })
}

/// Model constants in force, with where each comes from.
fn constants(p: &Parameters) -> Value {
    json!({
        "dynamics": {
            "mach_reversion_per_s": p.mach_reversion_per_s,
            "mach_noise_per_s": p.mach_noise_per_s,
            "angle_reversion_per_s": p.angle_reversion_per_s,
            "angle_noise_rad2_per_s": p.angle_noise_rad2_per_s,
            "wind_reversion_per_s": p.wind_reversion_per_s,
            "wind_noise_kt2_per_s": p.wind_noise_kt2_per_s,
            "tau_range_h": p.tau_range_h,
            "mach_range": p.mach_range,
            "altitude_range_ft": p.altitude_range_ft,
            "altitude_step_ft": p.altitude_step_ft,
            "bank_angle_deg": p.bank_angle_deg,
            "mach_rate_per_s": p.mach_rate_per_s,
            "climb_rate_ft_per_s": p.climb_rate_ft_per_s,
            "lnav_switch_mean_s": p.lnav_switch_mean_s,
            "cruise_step_s": p.cruise_step_s,
            "manoeuvre_step_s": p.manoeuvre_step_s,
            "bfo_vertical_rate": p.bfo_vertical_rate,
            "fuel": p.fuel.as_ref().map(|f| serde_json::json!({
                "initial_kg": f.initial_kg, "zfw_kg": f.zfw_kg,
                "factor_mean": f.factor_mean, "factor_sd": f.factor_sd,
                "proposal": match &f.endurance {
                    None => "reject".to_string(),
                    Some(e) => format!(
                        "endurance (deadline unix {}, prior mix {}, {} cells)",                        e.deadline_unix_s, e.prior_mix, e.cells),
                },
            })),
            "source": "Davey et al. (2016) Table 8.2 and ch. 6-7, compiled into crates/flight",
        },
        "measurement": {
            "bto_fixed_offset_us": satcom::BTO_FIXED_OFFSET_US,
            "uplink_hz": satcom::UPLINK_HZ,
            "downlink_hz": satcom::DOWNLINK_HZ,
            "perth_ges_km": [satcom::PERTH_GES_KM.x, satcom::PERTH_GES_KM.y, satcom::PERTH_GES_KM.z],
            "nominal_satellite_lon_deg": satcom::NOMINAL_SATELLITE_LON_DEG,
            "nominal_satellite_height_km": satcom::NOMINAL_SATELLITE_HEIGHT_KM,
            "speed_of_light_km_s": satcom::SPEED_OF_LIGHT_KM_S,
            "bfo_bias": "constant per trajectory, Kalman-marginalised (Davey sec. 5.3 / 8.1)",
            "source": "Davey et al. (2016) ch. 5; BTO offset reconciled with Ashton et al. (2015), see README",
        },
        "modes": MODES,
    })
}

/// Configurations that can be run: the base estimate, core overrides, and hypothesis runs.
fn engines(root: &Path) -> Result<Vec<Value>, String> {
    let mut out = vec![engine(root, &root.join("config/davey2016.toml"), "base", None)?];
    for (dir, kind) in [("config/sensitivity", "sensitivity"), ("config", "override")] {
        let mut paths = list_toml(&root.join(dir));
        paths.sort();
        for path in paths {
            let name = path.file_name().unwrap_or_default().to_string_lossy().to_string();
            if name == "davey2016.toml" {
                continue;
            }
            out.push(engine(root, &path, kind, Some("config/davey2016.toml"))?);
        }
    }
    let mut hypotheses = list_dirs(&root.join("hypotheses"));
    hypotheses.sort();
    for dir in hypotheses {
        let run = dir.join("run.toml");
        if run.is_file() && !dir.ends_with("_template") {
            out.push(engine(root, &run, "hypothesis", None)?);
        }
    }
    Ok(out)
}

fn engine(root: &Path, path: &Path, kind: &str, applies_over: Option<&str>) -> Result<Value, String> {
    let relative = path.strip_prefix(root).unwrap_or(path).to_string_lossy().to_string();
    let text = std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
    // A config's leading comment block is its description.
    let description: String = text
        .lines()
        .take_while(|l| l.starts_with('#'))
        .map(|l| l.trim_start_matches('#').trim())
        .collect::<Vec<_>>()
        .join(" ");
    let id = match kind {
        "hypothesis" => path.parent().and_then(Path::file_name).unwrap_or_default().to_string_lossy().to_string(),
        _ => path.file_stem().unwrap_or_default().to_string_lossy().to_string(),
    };
    // Overrides are merged over the base; full configs stand alone.
    let full = applies_over.is_none();
    let config = full.then(|| crate::config::load(&[path.to_path_buf()])).transpose()?;
    Ok(json!({
        "id": id,
        "kind": kind,
        "path": relative,
        "applies_over": applies_over,
        "description": description,
        "name": config.as_ref().map(|c| c.name.clone()),
        "particles": config.as_ref().map(|c| c.particles_per_mode.iter().sum::<usize>()),
        "seeds": config.as_ref().map(|c| c.seeds.len()),
        "cases": config.as_ref().map(|c| c.cases.iter().map(|case| case.id.clone()).collect::<Vec<_>>()),
    }))
}

/// Hypotheses on disk, with the status each records for itself.
fn hypothesis_directories(root: &Path) -> Result<Vec<Value>, String> {
    let mut dirs = list_dirs(&root.join("hypotheses"));
    dirs.sort();
    let mut out = Vec::new();
    for dir in dirs {
        let name = dir.file_name().unwrap_or_default().to_string_lossy().to_string();
        if name.starts_with('_') {
            continue;
        }
        let Ok(text) = std::fs::read_to_string(dir.join("hypothesis.toml")) else {
            continue;
        };
        let meta: toml::Table = toml::from_str(&text).map_err(|e| format!("{name}/hypothesis.toml: {e}"))?;
        // The parameters a run uses, from its own run.toml, with the TOML type of each so
        // that the app writes `1` or `1.0` as the hypothesis declared it.
        let parameters = std::fs::read_to_string(dir.join("run.toml"))
            .ok()
            .and_then(|t| t.parse::<toml::Table>().ok())
            .and_then(|t| t.get("hypotheses")?.get(&name).cloned());
        let parameter_types: BTreeMap<String, &str> = parameters
            .as_ref()
            .and_then(toml::Value::as_table)
            .map(|t| t.iter().map(|(k, v)| (k.clone(), v.type_str())).collect())
            .unwrap_or_default();
        out.push(json!({
            "name": name,
            "question": meta.get("question").and_then(|v| v.as_str()),
            "status": meta.get("status").and_then(|v| v.as_str()),
            "summary": meta.get("summary").and_then(|v| v.as_str()),
            // A directory added since the last build is listed, but cannot be enabled until
            // the binary is rebuilt: the registry is generated by hypotheses/build.rs.
            "built": hypotheses::NAMES.contains(&name.as_str()),
            "core_requests": meta.get("core_requests").cloned().map(|v| v.to_string()),
            "parameters": parameters,
            "parameter_types": parameter_types,
            "doc": doc_comment(&dir.join("lib.rs")),
        }));
    }
    Ok(out)
}

/// The `//!` block at the top of a hypothesis: its assumption, source, and how it enters.
fn doc_comment(path: &Path) -> Option<String> {
    let text = std::fs::read_to_string(path).ok()?;
    let doc: Vec<&str> = text.lines().take_while(|l| l.starts_with("//!")).map(|l| l.trim_start_matches("//!").trim()).collect();
    (!doc.is_empty()).then(|| doc.join("\n"))
}

/// Settings the app may change, with the range each control offers. Every key is a path in
/// the run configuration, so a change here is the same as an override file on the command line.
fn controls(base: &Config, p: &Parameters) -> Vec<Value> {
    let published = Parameters::default();
    let mut out = vec![
        control("particles_per_mode", "Particles per mode", "integer5", json!(base.particles_per_mode), json!(1_000), json!(20_000_000),
            "One filter per autopilot mode, in the order true heading, magnetic heading, true track, magnetic track, lateral navigation.",
            "Run size"),
        control("seeds", "Seeds", "integers", json!(base.seeds), json!(1), json!(u32::MAX),
            "Independent replicates. A result whose replicates disagree is unconverged.", "Run size"),
        control("resample_ess_fraction", "Resample below ESS fraction", "number", json!(base.resample_ess_fraction), json!(0.05), json!(1.0),
            "Systematic resampling fires when the effective sample size falls below this fraction of the particle count.", "Run size"),
        control("environment.wind_scale", "Nominal wind scale", "number", json!(base.environment.wind_scale), json!(0.0), json!(2.0),
            "Multiplier on the ERA5 wind field. 1.0 is the estimate; 0.0 turns the nominal wind off and keeps the wind-error process.",
            "Environment"),
        control("prior.latitude_deg", "Prior latitude", "number", json!(base.prior.latitude_deg), json!(-10.0), json!(20.0),
            "18:01:49 UTC radar point, reconstructed from Davey ch. 4 figures.", "Prior"),
        control("prior.longitude_deg", "Prior longitude", "number", json!(base.prior.longitude_deg), json!(90.0), json!(110.0),
            "18:01:49 UTC radar point, reconstructed from Davey ch. 4 figures.", "Prior"),
        control("prior.position_sd_nm", "Prior position s.d.", "number", json!(base.prior.position_sd_nm), json!(0.05), json!(20.0),
            "Standard deviation of the radar position, in nautical miles.", "Prior"),
        control("prior.track_deg", "Prior track", "number", json!(base.prior.track_deg), json!(180.0), json!(360.0),
            "Mean control angle at the radar point, degrees true.", "Prior"),
        control("prior.track_sd_deg", "Prior track s.d.", "number", json!(base.prior.track_sd_deg), json!(0.1), json!(30.0),
            "Standard deviation of the initial control angle, degrees.", "Prior"),
        control("bfo_bias.mean_hz", "BFO bias prior mean", "number", json!(base.bfo_bias.mean_hz), json!(0.0), json!(300.0),
            "Prior mean of the per-trajectory constant BFO bias (Davey sec. 5.3).", "Measurement"),
        control("bfo_bias.sd_hz", "BFO bias prior s.d.", "number", json!(base.bfo_bias.sd_hz), json!(1.0), json!(100.0),
            "Prior standard deviation of the BFO bias, marginalised per particle.", "Measurement"),
        control("output.route_interval_s", "Route sample interval", "number", json!(base.output.route_interval_s), json!(300.0), json!(3600.0),
            "Seconds between stored route points; display only.", "Output"),
        control("output.route_samples", "Routes kept", "integer", json!(base.output.route_samples), json!(0), json!(20_000),
            "Number of weighted routes written for plotting; display only.", "Output"),
    ];
    // Dynamics constants: sliders span a fifth to five times the published value.
    let mut dynamics = |key: &str, label: &str, value: f64, published: f64, unit: &str| {
        let (lo, hi) = if published > 0.0 { (published / 5.0, published * 5.0) } else { (-1.0, 1.0) };
        out.push(json!({
            "key": format!("dynamics.{key}"), "label": label, "kind": "number", "group": "Dynamics",
            "value": value, "published": published, "min": lo, "max": hi, "unit": unit,
            "note": "Published value; the slider spans a fifth to five times it. Any value may be typed.",
        }));
    };
    dynamics("mach_reversion_per_s", "Mach reversion rate", p.mach_reversion_per_s, published.mach_reversion_per_s, "1/s");
    dynamics("mach_noise_per_s", "Mach noise strength", p.mach_noise_per_s, published.mach_noise_per_s, "1/s");
    dynamics("angle_reversion_per_s", "Control-angle reversion rate", p.angle_reversion_per_s, published.angle_reversion_per_s, "1/s");
    dynamics("angle_noise_rad2_per_s", "Control-angle noise strength", p.angle_noise_rad2_per_s, published.angle_noise_rad2_per_s, "rad^2/s");
    dynamics("wind_reversion_per_s", "Wind-error reversion rate", p.wind_reversion_per_s, published.wind_reversion_per_s, "1/s");
    dynamics("wind_noise_kt2_per_s", "Wind-error noise strength", p.wind_noise_kt2_per_s, published.wind_noise_kt2_per_s, "kt^2/s");
    dynamics("bank_angle_deg", "Turn bank angle", p.bank_angle_deg, published.bank_angle_deg, "deg");
    dynamics("mach_rate_per_s", "Mach change rate", p.mach_rate_per_s, published.mach_rate_per_s, "1/s");
    dynamics("climb_rate_ft_per_s", "Climb rate", p.climb_rate_ft_per_s, published.climb_rate_ft_per_s, "ft/s");
    dynamics("lnav_switch_mean_s", "LNAV hold-reversion mean", p.lnav_switch_mean_s, published.lnav_switch_mean_s, "s");
    dynamics("cruise_step_s", "Cruise integration step", p.cruise_step_s, published.cruise_step_s, "s");
    dynamics("manoeuvre_step_s", "Manoeuvre integration step", p.manoeuvre_step_s, published.manoeuvre_step_s, "s");
    for (key, label, value, published, unit) in [
        ("tau_range_h", "Manoeuvre time constant range", p.tau_range_h, published.tau_range_h, "h"),
        ("mach_range", "Mach range", p.mach_range, published.mach_range, ""),
        ("altitude_range_ft", "Altitude range", p.altitude_range_ft, published.altitude_range_ft, "ft"),
    ] {
        out.push(json!({
            "key": format!("dynamics.{key}"), "label": label, "kind": "range", "group": "Dynamics",
            "value": [value.0, value.1], "published": [published.0, published.1], "unit": unit,
            "note": "Jeffreys prior over the range for the time constant; uniform for Mach and altitude.",
        }));
    }
    out
}

fn control(key: &str, label: &str, kind: &str, value: Value, min: Value, max: Value, note: &str, group: &str) -> Value {
    json!({"key": key, "label": label, "kind": kind, "value": value, "min": min, "max": max, "note": note, "group": group})
}

/// Measured inputs a run reads, with size on disk and the provenance table from README.md.
fn data_sources(root: &Path, base: &Config) -> Vec<Value> {
    let table = readme_data_table(root);
    let mut entries = vec![
        ("observations", base.inputs.observations.clone()),
        ("ephemeris", base.inputs.ephemeris.clone()),
        ("era5", base.inputs.era5.clone()),
        ("igrf", base.inputs.igrf.clone()),
    ];
    if let Some(curve) = &base.inputs.reference_curve {
        entries.push(("reference_curve", curve.clone()));
    }
    entries
        .into_iter()
        .map(|(key, path)| {
            let full = if path.is_absolute() { path.clone() } else { root.join(&path) };
            let name = full.file_name().unwrap_or_default().to_string_lossy().to_string();
            let meta = std::fs::metadata(&full).ok();
            let row = table.iter().find(|(file, _, _)| file.contains(&name) || name.contains(file.trim_matches('`')));
            json!({
                "key": key,
                "path": path,
                "present": meta.is_some(),
                "bytes": meta.as_ref().map(|m| m.len()),
                "content": row.map(|r| r.1.clone()),
                "source": row.map(|r| r.2.clone()),
            })
        })
        .collect()
}

/// The `| File | Content | Source |` table in README.md, as (file, content, source) rows.
fn readme_data_table(root: &Path) -> Vec<(String, String, String)> {
    let Ok(text) = std::fs::read_to_string(root.join("README.md")) else {
        return Vec::new();
    };
    text.lines()
        .filter(|l| l.starts_with('|') && l.matches('|').count() >= 4 && !l.contains("---"))
        .filter_map(|l| {
            let cells: Vec<&str> = l.trim_matches('|').split('|').map(str::trim).collect();
            (cells.len() >= 3 && cells[0] != "File").then(|| {
                (cells[0].trim_matches('`').to_string(), cells[1].to_string(), cells[2].to_string())
            })
        })
        .collect()
}

/// A `## ` section of README.md, so the app quotes the record rather than repeating it.
fn readme_section(root: &Path, heading: &str) -> Option<String> {
    let text = std::fs::read_to_string(root.join("README.md")).ok()?;
    let start = text.find(&format!("## {heading}"))?;
    let rest = &text[start..];
    let end = rest[3..].find("\n## ").map(|i| i + 3).unwrap_or(rest.len());
    Some(rest[..end].trim().to_string())
}

/// Finished runs under `runs/`, for comparison against a new one.
fn existing_runs(root: &Path) -> Vec<Value> {
    let mut dirs = list_dirs(&root.join("runs"));
    dirs.sort();
    dirs.iter()
        .filter(|dir| dir.join("run.json").is_file())
        .map(|dir| {
            let name = dir.file_name().unwrap_or_default().to_string_lossy().to_string();
            let summary = dir.join("summary.json").is_file();
            json!({"name": name, "path": format!("runs/{name}"), "has_summary": summary})
        })
        .collect()
}

fn list_toml(dir: &Path) -> Vec<PathBuf> {
    std::fs::read_dir(dir)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .filter(|p| p.extension().is_some_and(|e| e == "toml"))
        .collect()
}

fn list_dirs(dir: &Path) -> Vec<PathBuf> {
    std::fs::read_dir(dir).into_iter().flatten().flatten().map(|e| e.path()).filter(|p| p.is_dir()).collect()
}
