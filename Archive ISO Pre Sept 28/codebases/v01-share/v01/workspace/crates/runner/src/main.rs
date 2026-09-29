mod accident_antenna;
mod accident_commands;
mod broad_flight_commands;
#[allow(dead_code)]
mod broad_impact_handoff;
mod broad_terminal_cli;
mod broad_terminal_commands;
mod conditional_spatial_commands;
mod continuation_commands;
mod final_bfo_commands;
mod impact_commands;
mod impact_handoff;
mod known_flight_commands;
mod ocean_drift_application;
mod ocean_drift_commands;

use std::{
    collections::BTreeMap,
    fs::{self, OpenOptions},
    io::Write,
    path::{Path, PathBuf},
    time::{Instant, SystemTime, UNIX_EPOCH},
};

use anyhow::{bail, Context, Result};
use clap::{Parser, Subcommand};
use mh370_controls::{run_synthetic, simulate_synthetic, ExperimentConfig, SyntheticRun};
use rayon::ThreadPoolBuilder;
use serde::Serialize;
use sha2::{Digest, Sha256};

#[derive(Debug, Parser)]
#[command(
    name = "mh370",
    version,
    about = "Lean modular MH370 Bayesian estimator"
)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Debug, Subcommand)]
enum Command {
    /// Run the canonical MH370 accident-flight estimator and publish reports.
    Estimate {
        #[arg(long)]
        config: PathBuf,
        #[arg(long)]
        output: PathBuf,
        #[arg(long)]
        threads: Option<usize>,
    },
    /// Run broad marked-jump powered-flight inference through a declared checkpoint.
    EstimateBroadFlight {
        #[arg(long)]
        config: PathBuf,
        #[arg(long)]
        output: PathBuf,
        #[arg(long)]
        threads: Option<usize>,
    },
    /// Continue one broad 00:11 handoff through exact R600 and a mirrored terminal family.
    InferBroadTerminal {
        #[arg(long)]
        config: PathBuf,
        #[arg(long)]
        output: PathBuf,
    },
    /// Estimate a family-specific ocean-drift source area.
    EstimateOceanDrift {
        #[arg(long)]
        config: PathBuf,
        #[arg(long)]
        output: PathBuf,
    },
    /// Continue completed posterior particles to a later SATCOM contact.
    ContinueToContact {
        #[arg(long)]
        config: PathBuf,
        #[arg(long)]
        output: PathBuf,
    },
    /// Analyze whether the two raw final BFOs can be matched by local dynamics.
    AnalyzeFinalBfo {
        #[arg(long)]
        config: PathBuf,
        #[arg(long)]
        output: PathBuf,
    },
    /// Propagate one typed 00:11 posterior seed through one conditional end-of-flight scenario.
    InferImpact {
        #[arg(long)]
        config: PathBuf,
        #[arg(long)]
        output: PathBuf,
    },
    /// Apply one named provisional spatial surface as a separate sensitivity branch.
    ApplyConditionalSurface {
        #[arg(long)]
        config: PathBuf,
        #[arg(long)]
        output: PathBuf,
    },
    /// Generate deterministic synthetic truth and SATCOM observations.
    Simulate {
        #[arg(long)]
        config: PathBuf,
        #[arg(long)]
        output: PathBuf,
    },
    /// Run the synthetic particle-filter validation suite.
    Validate {
        #[arg(long)]
        config: PathBuf,
        #[arg(long)]
        output: PathBuf,
        #[arg(long)]
        threads: Option<usize>,
    },
    /// Run all frozen truth-blind MH371 inference seeds.
    InferKnownFlight {
        #[arg(long)]
        config: PathBuf,
        #[arg(long)]
        inference: PathBuf,
        #[arg(long)]
        weather: PathBuf,
        #[arg(long)]
        magnetic: PathBuf,
        #[arg(long, requires = "antenna_surface")]
        antenna_observations: Option<PathBuf>,
        #[arg(long, requires = "antenna_observations")]
        antenna_surface: Option<PathBuf>,
        #[arg(long)]
        output: PathBuf,
        #[arg(long)]
        threads: Option<usize>,
    },
    /// Score completed MH371 inference artifacts against scorer-only truth.
    ScoreKnownFlight {
        #[arg(long)]
        config: PathBuf,
        #[arg(long)]
        truth: PathBuf,
        #[arg(long = "run", required = true)]
        runs: Vec<PathBuf>,
        #[arg(long)]
        output: PathBuf,
    },
}

#[derive(Debug, Serialize)]
struct RunManifest {
    schema_version: u32,
    engine_version: &'static str,
    executable_sha256: String,
    command: &'static str,
    experiment_name: String,
    status: String,
    config_path: String,
    config_sha256: String,
    algorithm: String,
    particles: usize,
    filter_seed: u64,
    truth_seed: u64,
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

fn sha256_bytes(value: &[u8]) -> String {
    hex::encode(Sha256::digest(value))
}

fn sha256_file(path: &Path) -> Result<String> {
    let bytes = fs::read(path)
        .with_context(|| format!("cannot read artifact for hashing: {}", path.display()))?;
    Ok(sha256_bytes(&bytes))
}

fn executable_sha256() -> Result<String> {
    let path = std::env::current_exe().context("cannot resolve running executable for hashing")?;
    sha256_file(&path)
}

fn atomic_write(path: &Path, value: &[u8]) -> Result<()> {
    let parent = path
        .parent()
        .context("artifact path has no parent directory")?;
    fs::create_dir_all(parent).with_context(|| format!("cannot create {}", parent.display()))?;
    let temporary = parent.join(format!(
        ".{}.tmp-{}",
        path.file_name()
            .and_then(|name| name.to_str())
            .unwrap_or("artifact"),
        std::process::id()
    ));
    let mut stream = OpenOptions::new()
        .create_new(true)
        .write(true)
        .open(&temporary)
        .with_context(|| format!("cannot create temporary artifact {}", temporary.display()))?;
    stream.write_all(value)?;
    stream.sync_all()?;
    drop(stream);
    fs::rename(&temporary, path).with_context(|| {
        format!(
            "cannot atomically publish {} as {}",
            temporary.display(),
            path.display()
        )
    })?;
    Ok(())
}

fn write_json(path: &Path, value: &impl Serialize) -> Result<()> {
    let mut bytes = serde_json::to_vec_pretty(value)?;
    bytes.push(b'\n');
    atomic_write(path, &bytes)
}

fn prepare_output(path: &Path) -> Result<()> {
    if path.exists() {
        let mut entries = fs::read_dir(path)
            .with_context(|| format!("cannot inspect output {}", path.display()))?;
        if entries.next().is_some() {
            bail!(
                "output directory is not empty; refusing to overwrite: {}",
                path.display()
            );
        }
    } else {
        fs::create_dir_all(path)
            .with_context(|| format!("cannot create output {}", path.display()))?;
    }
    Ok(())
}

fn load_config(path: &Path) -> Result<(ExperimentConfig, Vec<u8>)> {
    let bytes = fs::read(path).with_context(|| format!("cannot read config {}", path.display()))?;
    let text = std::str::from_utf8(&bytes).context("experiment config is not UTF-8")?;
    let configuration: ExperimentConfig =
        toml::from_str(text).context("cannot parse experiment TOML")?;
    configuration
        .validate()
        .map_err(anyhow::Error::msg)
        .context("invalid experiment configuration")?;
    Ok((configuration, bytes))
}

fn posterior_csv(run: &SyntheticRun) -> Vec<u8> {
    let mut output = String::from(
        "particle,weight,time_s,latitude_deg,longitude_deg,altitude_ft,track_true_deg,ground_speed_kt,vertical_speed_fpm,bfo_bias_hz\n",
    );
    for (index, (state, log_weight)) in run
        .filter
        .particles
        .iter()
        .zip(&run.filter.log_weights)
        .enumerate()
    {
        output.push_str(&format!(
            "{index},{:.17e},{:.9},{:.12},{:.12},{:.6},{:.9},{:.9},{:.9},{:.9}\n",
            log_weight.exp(),
            state.time.0,
            state.position.latitude.0,
            state.position.longitude.0,
            state.altitude.0,
            state.track_true.0,
            state.ground_speed.0,
            state.vertical_speed.0,
            state.bfo_bias.0,
        ));
    }
    output.into_bytes()
}

fn manifest(
    command: &'static str,
    configuration: &ExperimentConfig,
    config_path: &Path,
    config_bytes: &[u8],
    status: String,
    outputs: BTreeMap<String, String>,
) -> Result<RunManifest> {
    Ok(RunManifest {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION"),
        executable_sha256: executable_sha256()?,
        command,
        experiment_name: configuration.name.clone(),
        status,
        config_path: config_path.display().to_string(),
        config_sha256: sha256_bytes(config_bytes),
        algorithm: format!("{:?}", configuration.filter.algorithm).to_lowercase(),
        particles: configuration.filter.particles,
        filter_seed: configuration.filter.seed,
        truth_seed: configuration.truth_seed,
        outputs,
        limitations: vec![
            "synthetic model-closure test; not an observation".to_string(),
            "does not load MH370 data or emit MH370 geography".to_string(),
            "constant-track process is intentionally simpler than the accident-flight model"
                .to_string(),
        ],
    })
}

fn simulate(config_path: &Path, output: &Path) -> Result<()> {
    prepare_output(output)?;
    let (configuration, config_bytes) = load_config(config_path)?;
    let dataset = simulate_synthetic(&configuration)?;
    let dataset_path = output.join("synthetic-dataset.json");
    write_json(&dataset_path, &dataset)?;

    let outputs = BTreeMap::from([(
        "synthetic-dataset.json".to_string(),
        sha256_file(&dataset_path)?,
    )]);
    let manifest = manifest(
        "simulate",
        &configuration,
        config_path,
        &config_bytes,
        "simulated".to_string(),
        outputs,
    )?;
    write_json(&output.join("run-manifest.json"), &manifest)?;
    println!(
        "status=simulated dataset={} manifest={}",
        dataset_path.display(),
        output.join("run-manifest.json").display()
    );
    Ok(())
}

fn validate(config_path: &Path, output: &Path, requested_threads: Option<usize>) -> Result<()> {
    prepare_output(output)?;
    let (configuration, config_bytes) = load_config(config_path)?;
    let threads = requested_threads.unwrap_or_else(|| {
        std::thread::available_parallelism()
            .map(usize::from)
            .unwrap_or(1)
    });
    if threads == 0 {
        bail!("thread count must be positive");
    }

    let started = Instant::now();
    let pool = ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .context("cannot build deterministic worker pool")?;
    let run = pool.install(|| run_synthetic(&configuration))?;
    let elapsed_seconds = started.elapsed().as_secs_f64();

    let dataset_path = output.join("synthetic-dataset.json");
    let summary_path = output.join("summary.json");
    let checkpoints_path = output.join("checkpoints.json");
    let posterior_path = output.join("posterior.csv");
    write_json(&dataset_path, &run.dataset)?;
    write_json(&summary_path, &run.summary)?;
    write_json(&checkpoints_path, &run.filter.checkpoints)?;
    atomic_write(&posterior_path, &posterior_csv(&run))?;

    let mut outputs = BTreeMap::new();
    for name in [
        "synthetic-dataset.json",
        "summary.json",
        "checkpoints.json",
        "posterior.csv",
    ] {
        outputs.insert(name.to_string(), sha256_file(&output.join(name))?);
    }
    let manifest = manifest(
        "validate",
        &configuration,
        config_path,
        &config_bytes,
        run.summary.status.clone(),
        outputs,
    )?;
    write_json(&output.join("run-manifest.json"), &manifest)?;
    let receipt = RuntimeReceipt {
        schema_version: 1,
        unix_time_s: SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .context("system clock predates Unix epoch")?
            .as_secs(),
        elapsed_seconds,
        threads,
    };
    write_json(&output.join("runtime-receipt.json"), &receipt)?;

    println!(
        "status={} passed={} particles={} elapsed_s={:.3} threads={} mean_error_nm={:.2} mass_100nm={:.4} ess={:.1} summary={}",
        run.summary.status,
        run.summary.passed,
        configuration.filter.particles,
        elapsed_seconds,
        threads,
        run.summary.final_mean_error_nm,
        run.summary.mass_within_100_nm,
        run.summary.final_ess,
        summary_path.display()
    );
    if !run.summary.passed {
        bail!("synthetic validation failed; artifacts were preserved");
    }
    Ok(())
}

fn main() -> Result<()> {
    match Cli::parse().command {
        Command::Estimate {
            config,
            output,
            threads,
        } => accident_commands::estimate(&config, &output, threads),
        Command::EstimateBroadFlight {
            config,
            output,
            threads,
        } => broad_flight_commands::estimate(&config, &output, threads),
        Command::InferBroadTerminal { config, output } => {
            broad_terminal_cli::infer(&config, &output)
        }
        Command::EstimateOceanDrift { config, output } => {
            ocean_drift_commands::estimate(&config, &output)
        }
        Command::ContinueToContact { config, output } => {
            continuation_commands::continue_to_contact(&config, &output)
        }
        Command::AnalyzeFinalBfo { config, output } => {
            final_bfo_commands::analyze(&config, &output)
        }
        Command::InferImpact { config, output } => impact_commands::infer_impact(&config, &output),
        Command::ApplyConditionalSurface { config, output } => {
            conditional_spatial_commands::apply(&config, &output)
        }
        Command::Simulate { config, output } => simulate(&config, &output),
        Command::Validate {
            config,
            output,
            threads,
        } => validate(&config, &output, threads),
        Command::InferKnownFlight {
            config,
            inference,
            weather,
            magnetic,
            antenna_observations,
            antenna_surface,
            output,
            threads,
        } => known_flight_commands::infer(
            &config,
            &inference,
            &weather,
            &magnetic,
            antenna_observations.as_deref(),
            antenna_surface.as_deref(),
            &output,
            threads,
        ),
        Command::ScoreKnownFlight {
            config,
            truth,
            runs,
            output,
        } => known_flight_commands::score(&config, &truth, &runs, &output),
    }
}
