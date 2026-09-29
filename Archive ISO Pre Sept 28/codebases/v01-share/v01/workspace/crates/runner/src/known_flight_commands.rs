use std::{
    collections::BTreeMap,
    fs,
    path::{Path, PathBuf},
    time::{Instant, SystemTime, UNIX_EPOCH},
};

use anyhow::{bail, Context, Result};
use mh370_antenna::{DirectionalGainGrid, DirectionalPatternBasis};
use mh370_controls::{
    parse_known_flight_antenna_power, parse_known_flight_inference, parse_known_flight_truth_csv,
    run_known_flight_inference, score_known_flight, KnownFlightAntennaInputs,
    KnownFlightInferenceConfig, KnownFlightInferenceRun, KnownFlightScoreSummary,
    KnownFlightScoringConfig, KnownFlightTruthRow,
};
use mh370_dynamics::{Era5Grid, IgrfGrid};
use mh370_reporting::{
    build_known_flight_panel_png, build_known_flight_pdf, KnownFlightArcReport,
    KnownFlightControlReport, ReportPoint,
};
use rayon::ThreadPoolBuilder;
use serde::{de::DeserializeOwned, Serialize};

use crate::{
    atomic_write, executable_sha256, prepare_output, sha256_bytes, sha256_file, write_json,
};

#[derive(Debug, Serialize)]
struct InferenceManifest {
    schema_version: u32,
    engine_version: &'static str,
    executable_sha256: String,
    command: &'static str,
    status: &'static str,
    experiment_name: String,
    config_path: String,
    config_sha256: String,
    inference_path: String,
    inference_sha256: String,
    weather_path: String,
    weather_sha256: String,
    magnetic_path: String,
    magnetic_sha256: String,
    antenna_observations_path: Option<String>,
    antenna_observations_sha256: Option<String>,
    antenna_surface_path: Option<String>,
    antenna_surface_sha256: Option<String>,
    algorithm: String,
    particles_per_seed: usize,
    seeds: Vec<u64>,
    outputs: BTreeMap<String, String>,
    limitations: Vec<String>,
}

#[derive(Debug, Serialize)]
struct ScoringManifest {
    schema_version: u32,
    engine_version: &'static str,
    executable_sha256: String,
    command: &'static str,
    status: String,
    config_path: String,
    config_sha256: String,
    truth_path: String,
    truth_sha256: String,
    run_inputs: BTreeMap<String, String>,
    outputs: BTreeMap<String, String>,
    limitations: Vec<String>,
}

#[derive(Debug, Serialize)]
struct RuntimeReceipt {
    schema_version: u32,
    unix_time_s: u64,
    elapsed_seconds: f64,
    threads: usize,
}

#[derive(Debug, Serialize)]
struct SeedSummary {
    seed: u64,
    particles: usize,
    checkpoints: usize,
    final_particle_ess: f64,
    final_root_ess: f64,
    log_evidence: f64,
    artifact: String,
    artifact_sha256: String,
}

#[derive(Debug, Serialize)]
struct InferenceSummary {
    schema_version: &'static str,
    status: &'static str,
    experiment_name: String,
    inference_sha256: String,
    inference_config_sha256: String,
    seeds: Vec<SeedSummary>,
    elapsed_seconds: f64,
    threads: usize,
}

fn load_toml<T: DeserializeOwned>(path: &Path) -> Result<(T, Vec<u8>)> {
    let bytes = fs::read(path).with_context(|| format!("cannot read config {}", path.display()))?;
    let text = std::str::from_utf8(&bytes).context("configuration is not UTF-8")?;
    let configuration = toml::from_str(text)
        .with_context(|| format!("cannot parse TOML configuration {}", path.display()))?;
    Ok((configuration, bytes))
}

fn write_json_compact(path: &Path, value: &impl Serialize) -> Result<()> {
    let mut bytes = serde_json::to_vec(value)?;
    bytes.push(b'\n');
    atomic_write(path, &bytes)
}

fn thread_count(requested: Option<usize>) -> Result<usize> {
    let threads = requested.unwrap_or_else(|| {
        std::thread::available_parallelism()
            .map(usize::from)
            .unwrap_or(1)
    });
    if threads == 0 {
        bail!("thread count must be positive");
    }
    Ok(threads)
}

fn runtime_receipt(elapsed_seconds: f64, threads: usize) -> Result<RuntimeReceipt> {
    Ok(RuntimeReceipt {
        schema_version: 1,
        unix_time_s: SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .context("system clock predates Unix epoch")?
            .as_secs(),
        elapsed_seconds,
        threads,
    })
}

fn root_ess(run: &KnownFlightInferenceRun) -> Result<f64> {
    if run.filter.root_ids.len() != run.filter.log_weights.len() {
        bail!("final root and weight arrays differ in length");
    }
    let mut mass = BTreeMap::<usize, f64>::new();
    for (root, log_weight) in run.filter.root_ids.iter().zip(&run.filter.log_weights) {
        *mass.entry(*root).or_default() += log_weight.exp();
    }
    let total = mass.values().sum::<f64>();
    if !total.is_finite() || total <= 0.0 {
        bail!("final root mass is invalid");
    }
    Ok(1.0
        / mass
            .values()
            .map(|value| {
                let normalized = value / total;
                normalized * normalized
            })
            .sum::<f64>())
}

pub(crate) fn infer(
    config_path: &Path,
    inference_path: &Path,
    weather_path: &Path,
    magnetic_path: &Path,
    antenna_observations_path: Option<&Path>,
    antenna_surface_path: Option<&Path>,
    output: &Path,
    requested_threads: Option<usize>,
) -> Result<()> {
    let (configuration, config_bytes): (KnownFlightInferenceConfig, Vec<u8>) =
        load_toml(config_path)?;
    configuration
        .validate()
        .map_err(anyhow::Error::msg)
        .context("invalid known-flight inference configuration")?;
    let inference_bytes = fs::read(inference_path)
        .with_context(|| format!("cannot read inference {}", inference_path.display()))?;
    let inference_sha256 = sha256_bytes(&inference_bytes);
    if inference_sha256 != configuration.expected_inference_sha256 {
        bail!("inference SHA-256 differs from the frozen configuration");
    }
    let package = parse_known_flight_inference(&inference_bytes)?;
    let weather_bytes = fs::read(weather_path)
        .with_context(|| format!("cannot read weather grid {}", weather_path.display()))?;
    let weather_sha256 = sha256_bytes(&weather_bytes);
    if weather_sha256 != configuration.expected_weather_sha256 {
        bail!("weather grid SHA-256 differs from configuration");
    }
    let weather = Era5Grid::parse(&weather_bytes).context("cannot parse ERA5 weather grid")?;
    let magnetic_bytes = fs::read(magnetic_path)
        .with_context(|| format!("cannot read magnetic grid {}", magnetic_path.display()))?;
    let magnetic_sha256 = sha256_bytes(&magnetic_bytes);
    if magnetic_sha256 != configuration.expected_magnetic_sha256 {
        bail!("magnetic grid SHA-256 differs from configuration");
    }
    let magnetic = IgrfGrid::parse(&magnetic_bytes).context("cannot parse IGRF magnetic grid")?;
    let antenna_data = match (antenna_observations_path, antenna_surface_path) {
        (Some(observations_path), Some(surface_path)) => {
            let observation_bytes = fs::read(observations_path).with_context(|| {
                format!(
                    "cannot read antenna observations {}",
                    observations_path.display()
                )
            })?;
            let observations_sha256 = sha256_bytes(&observation_bytes);
            let antenna_package = parse_known_flight_antenna_power(&observation_bytes)?;
            let surface_bytes = fs::read(surface_path).with_context(|| {
                format!("cannot read antenna surface {}", surface_path.display())
            })?;
            let surface_sha256 = sha256_bytes(&surface_bytes);
            let surface = DirectionalGainGrid::parse(
                &surface_bytes,
                DirectionalPatternBasis::UnverifiedReconstruction,
            )
            .context("cannot parse directional antenna surface")?;
            Some((
                antenna_package,
                observations_sha256,
                surface,
                surface_sha256,
            ))
        }
        (None, None) => None,
        _ => bail!("antenna observations and surface paths must be supplied together"),
    };
    if configuration.model.antenna.is_some() != antenna_data.is_some() {
        bail!("antenna inputs must be supplied exactly when the configuration enables them");
    }
    let config_sha256 = sha256_bytes(&config_bytes);
    let threads = thread_count(requested_threads)?;
    prepare_output(output)?;

    let pool = ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .context("cannot build deterministic worker pool")?;
    let started = Instant::now();
    let mut outputs = BTreeMap::new();
    let mut seed_summaries = Vec::with_capacity(configuration.seeds.len());

    for seed in &configuration.seeds {
        let run = pool.install(|| {
            let antenna = antenna_data.as_ref().map(
                |(package, observations_sha256, surface, surface_sha256)| {
                    KnownFlightAntennaInputs {
                        package,
                        observations_sha256,
                        surface,
                        surface_sha256,
                    }
                },
            );
            run_known_flight_inference(
                &configuration,
                &package,
                &inference_sha256,
                &config_sha256,
                &weather,
                &weather_sha256,
                &magnetic,
                &magnetic_sha256,
                antenna,
                *seed,
            )
        })?;
        let artifact_name = format!("inference-seed-{seed}.json");
        let artifact_path = output.join(&artifact_name);
        write_json_compact(&artifact_path, &run)?;
        let artifact_sha256 = sha256_file(&artifact_path)?;
        outputs.insert(artifact_name.clone(), artifact_sha256.clone());
        seed_summaries.push(SeedSummary {
            seed: *seed,
            particles: run.particle_count,
            checkpoints: run.filter.snapshots.len(),
            final_particle_ess: run.filter.effective_sample_size()?,
            final_root_ess: root_ess(&run)?,
            log_evidence: run.filter.log_evidence,
            artifact: artifact_name,
            artifact_sha256,
        });
    }

    let elapsed_seconds = started.elapsed().as_secs_f64();
    let status = if antenna_data.is_some() {
        "complete_truth_separated_conditional_antenna_control"
    } else {
        "complete_truth_separated_bto_bfo_control"
    };
    let summary = InferenceSummary {
        schema_version: "mh370-known-flight-inference-summary-v2",
        status,
        experiment_name: configuration.name.clone(),
        inference_sha256: inference_sha256.clone(),
        inference_config_sha256: config_sha256.clone(),
        seeds: seed_summaries,
        elapsed_seconds,
        threads,
    };
    let summary_path = output.join("inference-summary.json");
    write_json(&summary_path, &summary)?;
    outputs.insert(
        "inference-summary.json".to_string(),
        sha256_file(&summary_path)?,
    );

    let manifest = InferenceManifest {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION"),
        executable_sha256: executable_sha256()?,
        command: "infer-known-flight",
        status,
        experiment_name: configuration.name.clone(),
        config_path: config_path.display().to_string(),
        config_sha256,
        inference_path: inference_path.display().to_string(),
        inference_sha256,
        weather_path: weather_path.display().to_string(),
        weather_sha256,
        magnetic_path: magnetic_path.display().to_string(),
        magnetic_sha256,
        antenna_observations_path: antenna_observations_path
            .map(|path| path.display().to_string()),
        antenna_observations_sha256: antenna_data
            .as_ref()
            .map(|(_, sha256, _, _)| sha256.clone()),
        antenna_surface_path: antenna_surface_path.map(|path| path.display().to_string()),
        antenna_surface_sha256: antenna_data
            .as_ref()
            .map(|(_, _, _, sha256)| sha256.clone()),
        algorithm: format!("{:?}", configuration.algorithm).to_lowercase(),
        particles_per_seed: configuration.particles,
        seeds: configuration.seeds.clone(),
        outputs,
        limitations: vec![
            "known-flight control; not an MH370 accident-flight posterior".to_string(),
            "inference command has no scorer-truth argument".to_string(),
            "constant-magnetic-heading control uses ERA5 winds, ERA5 temperature, and IGRF14 declination"
                .to_string(),
        ],
    };
    write_json(&output.join("run-manifest.json"), &manifest)?;
    write_json(
        &output.join("runtime-receipt.json"),
        &runtime_receipt(elapsed_seconds, threads)?,
    )?;

    println!(
        "status={} seeds={} particles_per_seed={} elapsed_s={:.3} threads={} summary={}",
        summary.status,
        summary.seeds.len(),
        configuration.particles,
        elapsed_seconds,
        threads,
        summary_path.display()
    );
    for seed in &summary.seeds {
        println!(
            "seed={} particle_ess={:.1} root_ess={:.1} log_evidence={:.3}",
            seed.seed, seed.final_particle_ess, seed.final_root_ess, seed.log_evidence
        );
    }
    Ok(())
}

fn known_flight_report(
    runs: &[KnownFlightInferenceRun],
    truth: &[KnownFlightTruthRow],
    summary: &KnownFlightScoreSummary,
) -> Result<KnownFlightControlReport> {
    if runs.is_empty() || truth.len() < 2 {
        bail!("known-flight report lacks runs or observation truth");
    }
    let terminal_index = truth.len() - 1;
    let terminal = summary
        .checkpoints
        .iter()
        .filter(|item| item.checkpoint_index == terminal_index)
        .collect::<Vec<_>>();
    let range = |values: Vec<f64>, decimals: usize| {
        let minimum = values.iter().copied().fold(f64::INFINITY, f64::min);
        let maximum = values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
        format!("{minimum:.decimals$} to {maximum:.decimals$}")
    };
    let implied_bias = summary
        .bfo_truth_closure
        .iter()
        .map(|item| item.implied_aircraft_bias_hz)
        .collect::<Vec<_>>();
    let mut arcs = Vec::with_capacity(truth.len() - 1);
    for (checkpoint_index, truth_row) in truth.iter().enumerate().skip(1) {
        let mut points = Vec::with_capacity(
            runs.iter()
                .map(|run| run.filter.snapshots[checkpoint_index].particles.len())
                .sum(),
        );
        for run in runs {
            let snapshot = &run.filter.snapshots[checkpoint_index];
            let total = snapshot
                .log_weights
                .iter()
                .map(|value| value.exp())
                .sum::<f64>();
            if !total.is_finite() || total <= 0.0 {
                bail!("invalid snapshot weights while building known-flight report");
            }
            for (particle, log_weight) in snapshot.particles.iter().zip(&snapshot.log_weights) {
                points.push(ReportPoint {
                    latitude_deg: particle.aircraft.position.latitude.0,
                    longitude_deg: particle.aircraft.position.longitude.0,
                    weight: log_weight.exp() / total / runs.len() as f64,
                });
            }
        }
        let assessments = summary
            .checkpoints
            .iter()
            .filter(|item| item.checkpoint_index == checkpoint_index)
            .collect::<Vec<_>>();
        let average = |field: fn(&mh370_controls::KnownFlightCheckpointScore) -> f64| {
            assessments.iter().map(|item| field(item)).sum::<f64>() / assessments.len() as f64
        };
        let closure = summary
            .bfo_truth_closure
            .iter()
            .find(|item| item.checkpoint_index == checkpoint_index)
            .context("BFO closure row is absent")?;
        arcs.push(KnownFlightArcReport {
            label: format!("{} SATCOM arc", truth_row.epoch_id),
            time_utc: truth_row.time_utc.clone(),
            truth_latitude_deg: truth_row.latitude_deg,
            truth_longitude_deg: truth_row.longitude_deg,
            truth_heading_true_deg: truth_row.heading_true_deg,
            points,
            metrics: vec![
                (
                    "Mean position error".to_string(),
                    format!("{:.1} NM", average(|item| item.posterior_mean_error_nm)),
                ),
                (
                    "Posterior within 100 NM".to_string(),
                    format!("{:.1}%", 100.0 * average(|item| item.mass_within_100_nm)),
                ),
                (
                    "Mach: posterior / truth".to_string(),
                    format!(
                        "{:.3} / {:.3}",
                        average(|item| item.posterior_mean_mach),
                        truth_row.mach
                    ),
                ),
                (
                    "Altitude: posterior / truth".to_string(),
                    format!(
                        "{:.0} / {:.0} ft",
                        average(|item| item.posterior_mean_altitude_ft),
                        truth_row.altitude_ft
                    ),
                ),
                (
                    "Ground speed: posterior / truth".to_string(),
                    format!(
                        "{:.0} / {:.0} kt",
                        average(|item| item.posterior_mean_ground_speed_kt),
                        truth_row.ground_speed_kt
                    ),
                ),
                (
                    "Latent BFO bias".to_string(),
                    format!("{:.1} Hz", average(|item| item.posterior_mean_bfo_bias_hz)),
                ),
                (
                    "Truth-implied BFO bias".to_string(),
                    format!("{:.1} Hz", closure.implied_aircraft_bias_hz),
                ),
                (
                    "Particle / root ESS".to_string(),
                    format!(
                        "{:.0} / {:.1}",
                        average(|item| item.particle_ess),
                        average(|item| item.root_ess)
                    ),
                ),
            ],
        });
    }

    let bfo_sd = runs[0].observations[0]
        .satcom
        .bfo_sd
        .context("known-flight report observation lacks BFO SD")?
        .0;
    let mut evidence_conditions = vec![
        "Cruise only: 01:48 UTC initial state through the selected 06:48:33 UTC SATCOM observation."
            .to_string(),
        "Later ACARS positions, trajectory, Mach, altitude, and headings were excluded from inference and loaded only here."
            .to_string(),
        "ERA5 temperature and wind plus IGRF-14 east-positive magnetic declination drive every propagation step."
            .to_string(),
        "Satellite oscillator and Perth GES AFC terms remain separate inputs; aircraft BFO bias is analytically estimated."
            .to_string(),
        "Each map combines deterministic seed replicates with equal replicate weight.".to_string(),
    ];
    let mut limitations = summary.limitations.clone();
    if let Some(antenna) = runs[0]
        .observations
        .iter()
        .find_map(|observation| observation.antenna.as_ref())
    {
        let endpoint = if antenna.power.directional_departure_scale == 0.0 {
            "full target-EIRP precompensation"
        } else {
            "no precompensation"
        };
        let maximum_time_offset_s = runs[0]
            .observations
            .iter()
            .filter_map(|observation| observation.antenna.as_ref())
            .map(|observation| observation.power_time_offset_s.abs())
            .fold(0.0, f64::max);
        evidence_conditions.push(format!(
            "Conditional RxGain endpoint: {endpoint}; event-level SD {:.2} dB; reference gain {:.2} dBic.",
            antenna.power.standard_deviation_db, antenna.power.reference_gain_dbic
        ));
        evidence_conditions.push(format!(
            "Power rows use the selected event/channel aggregation; maximum absolute offset from its SATCOM arc is {maximum_time_offset_s:.3} s."
        ));
        limitations.extend(runs[0].limitations.iter().skip(4).cloned());
    }
    Ok(KnownFlightControlReport {
        title: "MH371 truth-blind cruise control".to_string(),
        subtitle: format!(
            "{} | {} deterministic seeds | generated from run artifacts",
            summary.model_family,
            summary.seeds.len()
        ),
        summary: vec![
            ("Model family".to_string(), summary.model_family.clone()),
            (
                "Particles".to_string(),
                format!(
                    "{} x {} seeds",
                    summary.particle_count_per_seed,
                    summary.seeds.len()
                ),
            ),
            (
                "Terminal mean error".to_string(),
                format!(
                    "{} NM",
                    range(
                        terminal
                            .iter()
                            .map(|item| item.posterior_mean_error_nm)
                            .collect(),
                        1
                    )
                ),
            ),
            (
                "Terminal mass within 100 NM".to_string(),
                format!(
                    "{}%",
                    range(
                        terminal
                            .iter()
                            .map(|item| 100.0 * item.mass_within_100_nm)
                            .collect(),
                        1
                    )
                ),
            ),
            (
                "Terminal root ESS".to_string(),
                range(terminal.iter().map(|item| item.root_ess).collect(), 1),
            ),
            ("BFO observation SD".to_string(), format!("{bfo_sd:.1} Hz")),
            (
                "Truth-implied BFO bias".to_string(),
                format!("{} Hz", range(implied_bias, 1)),
            ),
            (
                "BTO equation closure".to_string(),
                format!("{:.3e} us max", summary.maximum_bto_closure_abs_error_us),
            ),
        ],
        arcs,
        evidence_conditions,
        limitations,
    })
}

pub(crate) fn score(
    config_path: &Path,
    truth_path: &Path,
    run_paths: &[PathBuf],
    output: &Path,
) -> Result<()> {
    let (configuration, config_bytes): (KnownFlightScoringConfig, Vec<u8>) =
        load_toml(config_path)?;
    configuration
        .validate()
        .map_err(anyhow::Error::msg)
        .context("invalid known-flight scoring configuration")?;
    let truth_bytes = fs::read(truth_path)
        .with_context(|| format!("cannot read scorer truth {}", truth_path.display()))?;
    let truth_sha256 = sha256_bytes(&truth_bytes);
    let truth = parse_known_flight_truth_csv(&truth_bytes)?;

    let mut runs = Vec::with_capacity(run_paths.len());
    let mut run_inputs = BTreeMap::new();
    for path in run_paths {
        let bytes =
            fs::read(path).with_context(|| format!("cannot read run {}", path.display()))?;
        let run: KnownFlightInferenceRun = serde_json::from_slice(&bytes)
            .with_context(|| format!("cannot parse run {}", path.display()))?;
        run_inputs.insert(path.display().to_string(), sha256_bytes(&bytes));
        runs.push(run);
    }

    let started = Instant::now();
    let summary = score_known_flight(&configuration, &runs, &truth, &truth_sha256)?;
    let report = known_flight_report(&runs, &truth, &summary)?;
    let pdf_bytes = build_known_flight_pdf(&report).context("cannot build MH371 control PDF")?;
    let panel_png = build_known_flight_panel_png(&report)
        .context("cannot build MH371 posterior-density panel PNG")?;
    let elapsed_seconds = started.elapsed().as_secs_f64();
    prepare_output(output)?;
    let summary_path = output.join("score-summary.json");
    write_json(&summary_path, &summary)?;
    let mut outputs = BTreeMap::from([(
        "score-summary.json".to_string(),
        sha256_file(&summary_path)?,
    )]);
    let pdf_path = output.join("mh371-control.pdf");
    atomic_write(&pdf_path, &pdf_bytes)?;
    outputs.insert("mh371-control.pdf".to_string(), sha256_file(&pdf_path)?);
    let panel_png_path = output.join("mh371-posterior-panels.png");
    atomic_write(&panel_png_path, &panel_png)?;
    outputs.insert(
        "mh371-posterior-panels.png".to_string(),
        sha256_file(&panel_png_path)?,
    );
    let manifest = ScoringManifest {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION"),
        executable_sha256: executable_sha256()?,
        command: "score-known-flight",
        status: summary.status.clone(),
        config_path: config_path.display().to_string(),
        config_sha256: sha256_bytes(&config_bytes),
        truth_path: truth_path.display().to_string(),
        truth_sha256,
        run_inputs,
        outputs,
        limitations: summary.limitations.clone(),
    };
    write_json(&output.join("score-manifest.json"), &manifest)?;
    write_json(
        &output.join("runtime-receipt.json"),
        &runtime_receipt(elapsed_seconds, 1)?,
    )?;

    println!(
        "status={} numerical_valid={} min_final_mass_100nm={:.4} min_overlap={:.4} max_js_nats={:.6} score={} pdf={} png={}",
        summary.status,
        summary.numerically_valid,
        summary.minimum_final_mass_within_100_nm,
        summary.minimum_pairwise_overlap,
        summary.maximum_pairwise_js_nats,
        summary_path.display(),
        pdf_path.display(),
        panel_png_path.display()
    );
    Ok(())
}
