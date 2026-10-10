//! Runner (hub): configuration, hypotheses, deterministic seeding and run artifacts.
//!
//! Usage: `mh370 <config.toml> [<override.toml>...] <output-dir>`
//!        `mh370 serve [--port <n>] [--root <dir>]`   local app (see `ui/index.html`)
//!        `mh370 describe [--root <dir>]`             model, inputs and controls as JSON
//!        `mh370 summarise <run-dir>`                 rebuild a finished run's summary.json
//!        `mh370 evaluate <config.toml> [<override.toml>...] <samples> <out-dir>`
//!                                                    impact modules on a samples file (impacts.rs)
//!        `mh370 terminal <run-dir> <config.toml> [<override.toml>...] <out-dir>`
//!                                                    the end-of-flight stage again, from a run's hand-off
//!
//! The core estimate is the Davey et al. (2016) model with no hypotheses enabled.
//! A config may enable hypotheses (`[hypotheses.<name>]`); each acts only through the
//! hooks in `crates/hypothesis`, and the manifest records which were enabled.

mod config;
mod describe;
mod filter;
mod handoff;
mod impacts;
mod observations;
mod output;
mod serve;
mod summary;
mod terminal;

use filter::{Context, Step, FINAL_COLUMNS, MAX_ROUTE_POINTS};
use flight::{environment::Gridded, Parameters, Prior};
use hypothesis::{Hypothesis, PriorSpec, Terminal, MODES};
use output::{code_revision, peak_memory_mib, write_json};
use std::collections::BTreeSet;
use std::path::{Path, PathBuf};
use std::time::Instant;

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let result = match args.first().map(String::as_str) {
        Some("serve") => serve::main(&args[1..]),
        Some("describe") => describe::main(&args[1..]),
        Some("summarise") => summarise(&args[1..]),
        Some("evaluate") => impacts::evaluate(&args[1..]),
        Some("terminal") => rerun_terminal(&args[1..]),
        _ if args.len() >= 2 => {
            let paths: Vec<PathBuf> = args.iter().map(PathBuf::from).collect();
            let (configs, out) = paths.split_at(paths.len() - 1);
            run(configs, &out[0], None).map(|_| ())
        }
        _ => {
            eprintln!("usage: mh370 <config.toml> [<override.toml>...] <output-dir>");
            eprintln!("       mh370 serve [--port <n>] [--root <dir>]");
            eprintln!("       mh370 describe [--root <dir>]");
            eprintln!("       mh370 summarise <run-dir>");
            eprintln!("       mh370 evaluate <config.toml> [<override.toml>...] <samples> <out-dir>");
            eprintln!("       mh370 terminal <run-dir> <config.toml> [<override.toml>...] <out-dir>");
            std::process::exit(2);
        }
    };
    if let Err(e) = result {
        eprintln!("error: {e}");
        std::process::exit(1);
    }
}

/// One run: load the configuration, filter every case and seed, and write the artifacts.
/// `hooks` is `None` on the command line and `Some` when the app drives the run.
pub fn run(config_paths: &[PathBuf], out: &Path, hooks: Option<&Hooks>) -> Result<serde_json::Value, String> {
    let started = Instant::now();
    let config = config::load_with(config_paths, hooks.and_then(|h| h.overrides.clone()))?;
    // Trajectory modules act in the filter; the terminal and impact modules act after it.
    let roles = config.roles()?;
    if !config.compose.is_empty() {
        return Err("[[compose]] acts in the composer, which is not built yet; run impact modules on a \
                    samples file with `mh370 evaluate` meanwhile"
            .into());
    }
    let mut epochs = satcom::load_epochs(&config.inputs.observations, &config.inputs.ephemeris)?;
    let known: BTreeSet<String> = epochs.iter().flat_map(satcom::Epoch::observations).collect();
    for id in &config.exclude_epochs {
        if !epochs.iter().any(|e| &e.id == id) {
            return Err(format!("exclude_epochs: unknown epoch {id}"));
        }
    }
    // Excluded bursts after the filter's stop go to the end-of-flight stage when there is one.
    let excluded: Vec<satcom::Epoch> = epochs.iter().filter(|e| config.exclude_epochs.contains(&e.id)).cloned().collect();
    epochs.retain(|e| !config.exclude_epochs.contains(&e.id));
    let mut environment = Gridded::load(&config.inputs.era5, &config.inputs.igrf)?;
    environment.wind_scale = config.environment.wind_scale;
    environment.declination_scale = config.environment.declination_scale;

    let hypotheses: Vec<Box<dyn Hypothesis>> = roles
        .trajectory
        .iter()
        .map(|name| hypotheses::construct(name, &config.hypotheses[name]))
        .collect::<Result<_, _>>()?;
    if let Some((name, _)) = roles.trajectory.iter().zip(&hypotheses).find(|(_, h)| !h.alternatives().is_empty()) {
        return Err(format!("{name} declares alternatives, but trajectory strata are not built yet"));
    }
    let terminal_module = roles.terminal.as_ref().map(|name| hypotheses::construct(name, &config.hypotheses[name])).transpose()?;

    let mut params = config.dynamics.apply(Parameters::default());
    params.fuel = load_fuel(&config, &epochs)?;
    params.early = config.dynamics.early.as_ref().map(|e| e.resolve()).transpose()?;
    let mut spec = PriorSpec {
        unix_s: satcom::parse_utc(&config.prior.time_utc)?,
        latitude_deg: config.prior.latitude_deg,
        longitude_deg: config.prior.longitude_deg,
        position_sd_nm: config.prior.position_sd_nm,
        track_deg: config.prior.track_deg,
        track_sd_deg: config.prior.track_sd_deg,
        mach_range: params.mach_range,
        mach_gaussian: None,
        altitude_levels: Prior::uniform_altitude_levels(&params),
        mode_weights: [1.0; 5],
    };
    for h in &hypotheses {
        h.adjust_prior(&mut spec);
    }
    validate_prior(&spec)?;
    let prior = Prior {
        unix_s: spec.unix_s,
        lat: spec.latitude_deg,
        lon: spec.longitude_deg,
        position_sd_nm: spec.position_sd_nm,
        track_deg: spec.track_deg,
        track_sd_deg: spec.track_sd_deg,
        mach_range: spec.mach_range,
        mach_gaussian: spec.mach_gaussian,
        altitude_levels: spec.altitude_levels.clone(),
    };

    let steps = build_steps(&epochs, &hypotheses, prior.unix_s)?;
    let last = steps.last().unwrap();
    let stop = handoff::Stop { epoch: last.id.clone(), step: steps.len() - 1, unix_s: last.unix_s };
    let stage = match (&config.terminal, &terminal_module) {
        (Some(t), Some(module)) => {
            let later = excluded.iter().filter(|e| e.unix_s > stop.unix_s).cloned().collect();
            let mut stage = terminal::Stage::new(t, &params, &environment, Some(environment.era5_span()), terminal_model(module.as_ref(), &t.module)?, later)?;
            stage.bfo_drift_hz2_per_s = config.bfo_bias.drift_hz2_per_s;
            Some(stage)
        }
        _ => None,
    };
    // Which stage uses each observation, per case (and 00:19 data option); any datum used
    // twice stops the run here.
    let mut assignments = Vec::new();
    for case in &config.cases {
        let options: Vec<Option<&config::DataOption>> = match &config.terminal {
            Some(t) => t.options.iter().map(Some).collect(),
            None => vec![None],
        };
        for option in options {
            let mut assignment = observations::Assignment::new(&known);
            for epoch in steps.iter().filter_map(|s| s.satcom.as_ref()) {
                for id in epoch.cruise_observations(case.use_bfo) {
                    assignment.claim(&id, "cruise filter")?;
                }
            }
            for (name, h) in roles.trajectory.iter().zip(&hypotheses) {
                for id in h.observations() {
                    assignment.claim(&id, name)?;
                }
            }
            if let Some(option) = option {
                for id in &option.observations {
                    assignment.claim(id, &format!("terminal option {}", option.id))?;
                }
            }
            assignments.push(serde_json::json!({"case": case.id, "option": option.map(|o| &o.id), "assignment": assignment.into_map()}));
        }
    }
    let route_points = ((steps.last().unwrap().unix_s - prior.unix_s) / config.output.route_interval_s) as usize + 1;
    if route_points > MAX_ROUTE_POINTS {
        return Err("route_interval_s is too small for the flight duration".into());
    }
    std::fs::create_dir_all(out).map_err(|e| e.to_string())?;
    eprintln!("loaded inputs in {:.1} s", started.elapsed().as_secs_f64());

    let ctx = Context {
        config: &config,
        params: &params,
        prior: &prior,
        mode_weights: spec.mode_weights,
        steps: &steps,
        environment: &environment,
        hypotheses: &hypotheses,
        route_points,
        progress: hooks.map(|h| h.progress),
        cancel: hooks.map(|h| h.cancel),
        handoff: config.terminal.as_ref().map_or(0, |t| t.handoff),
        handoff_floor: config.terminal.as_ref().map_or(0, |t| t.handoff_floor),
    };
    let mut replicates = Vec::new();
    for case in &config.cases {
        for &seed in case.seeds.as_ref().unwrap_or(&config.seeds) {
            let dir = out.join(&case.id).join(format!("seed-{seed}"));
            std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
            let (replicate, handed_off) = filter::run_case(&ctx, case, seed, &dir)?;
            write_json(&dir.join("diagnostics.json"), &replicate)?;
            if let Some(stage) = &stage {
                let started = Instant::now();
                let diagnostics = stage.run(seed, &stop, &handed_off, &dir)?;
                write_json(&dir.join("terminal.json"), &diagnostics)?;
                eprintln!("{} seed {seed}: end of flight in {:.1} s", case.id, started.elapsed().as_secs_f64());
            }
            replicates.push(replicate);
        }
    }

    // Reference BTO arcs at 35,000 ft for plotting (each particle carries its own altitude).
    let arcs: Vec<_> = epochs
        .iter()
        .filter_map(|e| {
            let bto = e.bto_us?;
            let points: Vec<[f64; 2]> = (0..=320)
                .map(|i| -50.0 + 0.25 * f64::from(i))
                .filter_map(|lat| satcom::arc_longitude(e.satellite_km, lat, 35_000.0, bto).map(|lon| [lat, lon]))
                .collect();
            Some(serde_json::json!({"epoch": e.id, "bto_us": bto, "altitude_ft": 35_000.0, "lat_lon": points}))
        })
        .collect();

    let manifest = serde_json::json!({
        "config": config,
        "config_paths": config_paths,
        "code_revision": code_revision(),
        "model": "Davey et al. (2016) dynamics and measurement model; see README",
        "assumptions": describe::assumptions(&config, &params, &spec),
        "hypotheses": config.hypotheses.iter().map(|(name, params)| serde_json::json!({
            "name": name, "parameters": params, "metadata": hypotheses::metadata(name),
            "role": if roles.terminal.as_ref() == Some(name) { "terminal" }
                    else if roles.impact.contains(name) { "impact" } else { "trajectory" }})).collect::<Vec<_>>(),
        "prior": {
            "unix_s": spec.unix_s, "latitude_deg": spec.latitude_deg, "longitude_deg": spec.longitude_deg,
            "position_sd_nm": spec.position_sd_nm, "track_deg": spec.track_deg, "track_sd_deg": spec.track_sd_deg,
            "mach_range": spec.mach_range, "mach_gaussian": spec.mach_gaussian, "altitude_levels": spec.altitude_levels,
            "mode_weights": MODES.iter().zip(spec.mode_weights).collect::<Vec<_>>(),
        },
        "epochs": steps.iter().map(|s| match &s.satcom {
            Some(e) => serde_json::json!({"id": s.id, "unix_s": s.unix_s, "bto_us": e.bto_us,
                "bto_sd_us": e.bto_sd_us, "bfo_hz": e.bfo_hz, "bfo_sd_hz": e.bfo_sd_hz}),
            None => serde_json::json!({"id": s.id, "unix_s": s.unix_s, "requested_by_hypothesis": true}),
        }).collect::<Vec<_>>(),
        "observations": assignments,
        "stop": stop,
        "handoff_columns": stage.as_ref().map(|_| handoff::COLUMNS),
        "impact_columns": stage.as_ref().map(terminal::Stage::impact_columns),
        "terminal": stage.as_ref().map(|s| s.manifest()),
        "prior_unix_s": prior.unix_s,
        "final_columns": FINAL_COLUMNS,
        "tank_columns": config.fuel.as_ref().and_then(|f| f.tanks).filter(|&t| t == 2).map(|_| filter::TANK_COLUMNS),
        "residual_columns": filter::RESIDUAL_COLUMNS,
        "route_interval_s": config.output.route_interval_s,
        "reference_arcs": arcs,
        "replicates": replicates,
        "threads": rayon::current_num_threads(),
        "runtime_s": started.elapsed().as_secs_f64(),
        "peak_memory_mib": peak_memory_mib(),
    });
    write_json(&out.join("run.json"), &manifest)?;
    // Display statistics (latitude density, pooled weights, agreement) are computed once,
    // here, and read by both the report and the app. See summary.rs.
    summary::write(out, &config, &replicates)?;
    Ok(manifest)
}

/// The terminal model of the module named in `[terminal]`.

/// Load the performance tables and build the shared fuel model, or `None` when `[fuel]` is absent.
///
/// Fails loudly when `[fuel]` is set without `inputs.fuel_tables`: a run that asked for fuel and
/// silently got none would report a fuel-constrained posterior that was never constrained.
fn load_fuel(
    config: &config::Config,
    epochs: &[satcom::Epoch],
) -> Result<Option<std::sync::Arc<flight::FuelModel>>, String> {
    let Some(f) = &config.fuel else { return Ok(None) };
    let path = config
        .inputs
        .fuel_tables
        .as_ref()
        .ok_or("[fuel] is set but inputs.fuel_tables is missing")?;
    let text = std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let tables = flight::fuel::FuelTables::from_json(&text)?;
    let mut model = flight::FuelModel::new(
        tables,
        flight::fuel::FuelPrior {
            initial_kg: f.initial_kg,
            zfw_kg: f.zfw_kg,
            factor_mean: f.factor_mean,
            factor_sd: f.factor_sd,
        },
    );
    match f.model.as_deref() {
        None | Some("tables") => {
            if f.ceiling == Some(true) {
                return Err("[fuel] ceiling = true needs model = \"internal-v1\" (the ceiling table is in that model)".into());
            }
        }
        Some("internal-v1") => {
            let path = config.inputs.fuel_model.as_ref().ok_or("[fuel] model = \"internal-v1\" needs inputs.fuel_model")?;
            let text = std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
            let grid = flight::fuel::InternalGrid::from_json(&text)?;
            if grid.version != "internal-v1" {
                return Err(format!("{}: model version {} is not internal-v1", path.display(), grid.version));
            }
            model.internal = Some(grid);
        }
        Some(other) => return Err(format!("[fuel] model = \"{other}\" is not tables or internal-v1")),
    }
    model.temperature = f.temperature.unwrap_or(false);
    model.initial_from_factor = f.initial_from_factor.map(|[a, b]| (a, b));
    model.ceiling = f.ceiling.unwrap_or(false);
    match f.tanks.unwrap_or(1) {
        1 => {}
        2 => {
            if model.internal.as_ref().and_then(|g| g.inop.as_ref()).is_none() {
                return Err("[fuel] tanks = 2 needs model = \"internal-v1\" with its grid_inop".into());
            }
            let [im, isd] = f.tank_imbalance_kg.unwrap_or([221.0, 120.0]);
            let [rm, rsd] = f.tank_flow_ratio.unwrap_or([1.021, 0.008]);
            model.tanks = Some(flight::fuel::TankPrior { imbalance_mean_kg: im, imbalance_sd_kg: isd, ratio_mean: rm, ratio_sd: rsd });
        }
        n => return Err(format!("[fuel] tanks = {n}: must be 1 or 2")),
    }
    if f.single_engine == Some(true) {
        if model.tanks.is_none() {
            return Err("[fuel] single_engine = true needs tanks = 2".into());
        }
        // Probe well inside the one-engine envelope (FL150, 200 t): at FL250 and 200 t the LRC INOP
        // table is already filler (above the one-engine ceiling), which is not a missing table.
        if model.internal.as_ref().and_then(|g| g.inop_mach(150.0, 200.0)).is_none() {
            return Err("[fuel] single_engine = true needs internal-v1's lrc_inop_mach table".into());
        }
        let [lo, hi] = f.single_engine_descent_fpm.unwrap_or([300.0, 1000.0]);
        if !(lo > 0.0 && hi >= lo) {
            return Err("[fuel] single_engine_descent_fpm must be 0 < lo <= hi".into());
        }
        model.single_engine = Some(flight::SingleEngine { descent_fpm: (lo, hi), mach_band: f.single_engine_mach_band.unwrap_or(0.02) });
    }
    match f.proposal.as_deref() {
        None | Some("reject") => {}
        Some("endurance") => {
            // The proposal is built around the same deadline the evidence uses, so the paths
            // it stops proposing are exactly the ones the requirement would have rejected.
            let id = f
                .require_power_until
                .as_ref()
                .ok_or("[fuel] proposal = \"endurance\" needs require_power_until to aim at")?;
            let deadline = epochs
                .iter()
                .find(|e| e.id == *id)
                .map(|e| e.unix_s)
                .ok_or_else(|| format!("[fuel] require_power_until = \"{id}\" is not an epoch"))?;
            let prior_mix = f.proposal_prior_mix.unwrap_or(0.15);
            if !(prior_mix > 0.0 && prior_mix < 1.0) {
                return Err("[fuel] proposal_prior_mix must lie strictly between 0 and 1, so the \
                            proposal keeps the prior's support".into());
            }
            model.endurance = Some(flight::EnduranceProposal {
                deadline_unix_s: deadline,
                prior_mix,
                cells: f.proposal_cells.unwrap_or(16).max(2),
            });
        }
        Some(other) => return Err(format!("[fuel] proposal = \"{other}\" is not reject or endurance")),
    }
    Ok(Some(std::sync::Arc::new(model)))
}

fn terminal_model<'a>(module: &'a dyn Hypothesis, name: &str) -> Result<&'a dyn Terminal, String> {
    module.terminal().ok_or_else(|| format!("{name} is named in [terminal] but has no terminal model"))
}

/// The end-of-flight stage again, from a finished run's hand-off: every `<case>/seed-<s>/`
/// holding a handoff.toml gets new impacts in `<out>`. Pass the configuration the run was made
/// with (the powered flight uses its dynamics and weather), with overrides for `[terminal]`
/// or the terminal module's parameters.
fn rerun_terminal(args: &[String]) -> Result<(), String> {
    if args.len() < 3 {
        return Err("usage: mh370 terminal <run-dir> <config.toml> [<override.toml>...] <out-dir>".into());
    }
    let started = Instant::now();
    let run_dir = PathBuf::from(&args[0]);
    let out = PathBuf::from(&args[args.len() - 1]);
    let config_paths: Vec<PathBuf> = args[1..args.len() - 1].iter().map(PathBuf::from).collect();
    let config = config::load(&config_paths)?;
    let roles = config.roles()?;
    let (Some(t), Some(name)) = (&config.terminal, &roles.terminal) else {
        return Err("the configuration has no [terminal]".into());
    };
    let module = hypotheses::construct(name, &config.hypotheses[name])?;
    let epochs = satcom::load_epochs(&config.inputs.observations, &config.inputs.ephemeris)?;
    let mut environment = Gridded::load(&config.inputs.era5, &config.inputs.igrf)?;
    environment.wind_scale = config.environment.wind_scale;
    environment.declination_scale = config.environment.declination_scale;
    let mut params = config.dynamics.apply(Parameters::default());
    params.fuel = load_fuel(&config, &epochs)?;
    params.early = config.dynamics.early.as_ref().map(|e| e.resolve()).transpose()?;

    let mut handoffs = Vec::new();
    for case in &config.cases {
        for &seed in case.seeds.as_ref().unwrap_or(&config.seeds) {
            let dir = run_dir.join(&case.id).join(format!("seed-{seed}"));
            if dir.join("handoff.toml").is_file() {
                handoffs.push((case.id.clone(), seed, handoff::read(&dir)?));
            }
        }
    }
    let stop = match handoffs.first() {
        Some((.., (stop, _))) => stop.clone(),
        None => return Err(format!("{}: no handoff.toml for the configuration's cases and seeds", run_dir.display())),
    };
    let later = epochs.iter().filter(|e| config.exclude_epochs.contains(&e.id) && e.unix_s > stop.unix_s).cloned().collect();
    let mut stage = terminal::Stage::new(t, &params, &environment, Some(environment.era5_span()), terminal_model(module.as_ref(), name)?, later)?;
    stage.bfo_drift_hz2_per_s = config.bfo_bias.drift_hz2_per_s;
    let mut replicates = Vec::new();
    for (case, seed, (s, rows)) in handoffs {
        if s != stop {
            return Err(format!("{case} seed {seed}: its hand-off stops at {} rather than {}", s.epoch, stop.epoch));
        }
        let dir = out.join(&case).join(format!("seed-{seed}"));
        std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
        let diagnostics = stage.run(seed, &stop, &rows, &dir)?;
        write_json(&dir.join("terminal.json"), &diagnostics)?;
        replicates.push(serde_json::json!({"case": case, "seed": seed, "terminal": diagnostics}));
    }
    write_json(
        &out.join("run.json"),
        &serde_json::json!({
            "source_run": run_dir,
            "config": config,
            "config_paths": config_paths,
            "code_revision": code_revision(),
            "stop": stop,
            "impact_columns": stage.impact_columns(),
            "terminal": stage.manifest(),
            "replicates": replicates,
            "runtime_s": started.elapsed().as_secs_f64(),
        }),
    )?;
    eprintln!("wrote {} ({:.1} s)", out.display(), started.elapsed().as_secs_f64());
    Ok(())
}

/// Rebuild `summary.json` for a run made before it was written, or after a display change.
fn summarise(args: &[String]) -> Result<(), String> {
    let dir = Path::new(args.first().ok_or("usage: mh370 summarise <run-dir>")?);
    // The published curve comes from the base config, found from --root, the working
    // directory, or the run directory itself.
    let root = describe::root_from(args).or_else(|_| {
        dir.canonicalize()
            .map_err(|e| e.to_string())?
            .ancestors()
            .find(|d| d.join("config/davey2016.toml").is_file())
            .map(Path::to_path_buf)
            .ok_or_else(|| "no config/davey2016.toml above the run directory; pass --root".to_string())
    });
    let reference = root
        .ok()
        .and_then(|root| config::load(&[root.join("config/davey2016.toml")]).ok())
        .and_then(|base| base.inputs.reference_curve);
    summary::rebuild(dir, reference)?;
    eprintln!("wrote {}/summary.json", dir.display());
    Ok(())
}

/// How the app observes and steers a run. The command line passes none of these.
pub struct Hooks<'a> {
    pub overrides: Option<toml::Table>,
    pub progress: &'a (dyn Fn(&filter::Progress) + Sync),
    pub cancel: &'a std::sync::atomic::AtomicBool,
}

/// SATCOM epochs plus epochs requested by hypotheses, in time order (SATCOM first on ties).
fn build_steps(epochs: &[satcom::Epoch], hypotheses: &[Box<dyn Hypothesis>], start_unix_s: f64) -> Result<Vec<Step>, String> {
    let mut steps: Vec<Step> =
        epochs.iter().map(|e| Step { id: e.id.clone(), unix_s: e.unix_s, satcom: Some(e.clone()) }).collect();
    let end = epochs.last().ok_or("no SATCOM epochs")?.unix_s;
    for h in hypotheses {
        for (id, unix_s) in h.extra_epochs() {
            if !(unix_s > start_unix_s && unix_s <= end) {
                return Err(format!("hypothesis epoch {id} lies outside the filtered interval"));
            }
            steps.push(Step { id, unix_s, satcom: None });
        }
    }
    steps.sort_by(|a, b| a.unix_s.total_cmp(&b.unix_s).then(b.satcom.is_some().cmp(&a.satcom.is_some())));
    Ok(steps)
}

fn validate_prior(spec: &PriorSpec) -> Result<(), String> {
    let ok = |w: &f64| w.is_finite() && *w >= 0.0;
    if !spec.altitude_levels.iter().all(|(_, w)| ok(w)) || spec.altitude_levels.iter().all(|(_, w)| *w == 0.0) {
        return Err("prior altitude weights must be non-negative and not all zero".into());
    }
    if !spec.mode_weights.iter().all(ok) || spec.mode_weights.iter().all(|w| *w == 0.0) {
        return Err("prior mode weights must be non-negative and not all zero".into());
    }
    if spec.mach_gaussian.is_some_and(|(m, sd)| !(m.is_finite() && sd > 0.0)) {
        return Err("prior Gaussian Mach needs a finite mean and positive s.d.".into());
    }
    if !(spec.mach_range.0 < spec.mach_range.1) {
        return Err("prior Mach range is empty".into());
    }
    Ok(())
}
