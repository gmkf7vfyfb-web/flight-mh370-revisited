use std::{
    collections::BTreeMap,
    fs,
    path::{Path, PathBuf},
    time::Instant,
};

use anyhow::{bail, Context, Result};
use mh370_antenna::{
    evaluate_conditional_power, target_eirp_prediction, AircraftAttitude, AntennaError,
    ConditionalPowerObservation, DirectionalGainGrid, DirectionalPatternBasis, TargetEirpLinkModel,
};
use mh370_domain::{great_circle_distance_nm, AircraftState, LatLon, Seconds, Vec3};
use mh370_dynamics::{propagate_constant_track, LateralMode};
use mh370_estimator::{
    parse_satcom_observations, EvidenceComponent, EvidenceIdentity, EvidenceLedger,
    PosteriorHandoff, PosteriorHandoffParticle, PosteriorRunMetadata,
};
use mh370_reporting::{
    build_accident_panel_png, build_pdf, build_posterior_svg, ReportDocument, ReportMapBounds,
    ReportMapContext, ReportMapRoute, ReportPoint,
};
use mh370_satcom::{bto, normal_log_density, SatcomModelConfig};
use serde::{Deserialize, Serialize};

use crate::{
    atomic_write, executable_sha256, prepare_output, sha256_bytes, sha256_file, write_json,
};

#[derive(Debug, Clone, Deserialize)]
struct ContinuationInputs {
    observations: PathBuf,
    satellite_ephemeris: PathBuf,
    ground_station_position_km: Vec3,
    source_epoch_id: String,
    target_epoch_id: String,
    target_channel: String,
}

#[derive(Debug, Clone, Deserialize)]
struct ContinuationConfig {
    schema_version: u32,
    name: String,
    source_handoffs: Vec<PathBuf>,
    inputs: ContinuationInputs,
    satcom: SatcomModelConfig,
    selection: ContinuationSelection,
    #[serde(default = "default_plotted_paths")]
    plotted_paths: usize,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
enum ContinuationSelection {
    Bto,
    ConditionalPower {
        surface: PathBuf,
        observed_dbm: f64,
        observation_adjustment_db: f64,
        observation_sd_db: f64,
        reference_gain_dbic: f64,
        directional_departure_scale: f64,
        permit_unverified_reconstruction: bool,
        link: TargetEirpLinkModel,
    },
}

fn default_plotted_paths() -> usize {
    400
}

#[derive(Debug, Clone)]
struct SourcePopulation {
    source_index: usize,
    handoff: PosteriorHandoff,
}

#[derive(Debug, Clone)]
struct SourceParticle {
    source_index: usize,
    handoff: PosteriorHandoffParticle,
}

#[derive(Debug, Clone)]
struct ContinuedParticle {
    source_index: usize,
    source: PosteriorHandoffParticle,
    prior_weight: f64,
    log_likelihood: f64,
    weight: f64,
    predicted_observable: f64,
    observable_residual: f64,
    end: AircraftState,
}

#[derive(Debug, Clone, PartialEq)]
struct ContinuationWeightSummary {
    seed_posterior_ess: BTreeMap<u64, f64>,
    seed_log_evidence_increments: BTreeMap<u64, f64>,
    log_evidence_increment: f64,
    posterior_ess: f64,
}

#[derive(Debug, Serialize)]
struct ContinuationSummary {
    schema_version: u32,
    name: String,
    status: String,
    model_scope: String,
    selection: String,
    source_epoch_id: String,
    target_epoch_id: String,
    target_time_utc: String,
    propagation_duration_s: f64,
    source_handoffs: usize,
    particles: usize,
    posterior_ess: f64,
    seed_posterior_ess: BTreeMap<u64, f64>,
    log_evidence_increment: f64,
    seed_log_evidence_increments: BTreeMap<u64, f64>,
    endpoint_mean: LatLon,
    endpoint_latitude_90_deg: [f64; 2],
    endpoint_longitude_90_deg: [f64; 2],
    maximum_source_mean_separation_nm: f64,
    elapsed_seconds: f64,
    limitations: Vec<String>,
}

#[derive(Debug, Serialize)]
struct ContinuationManifest {
    schema_version: u32,
    engine_version: &'static str,
    executable_sha256: String,
    command: &'static str,
    config_path: String,
    config_sha256: String,
    input_sha256: BTreeMap<String, String>,
    outputs: BTreeMap<String, String>,
    scientific_scope: Vec<String>,
}

#[derive(Debug, Serialize)]
struct ContinuationRunIdentityPreimage<'a> {
    domain: &'static str,
    engine_version: &'static str,
    executable_sha256: &'a str,
    config_sha256: &'a str,
    input_sha256: &'a BTreeMap<String, String>,
    model_family: &'a str,
    seed: u64,
    source_run_identity_sha256: &'a str,
}

fn resolve(config_path: &Path, value: &Path) -> PathBuf {
    if value.is_absolute() {
        value.to_path_buf()
    } else {
        config_path
            .parent()
            .unwrap_or_else(|| Path::new("."))
            .join(value)
    }
}

fn parse_source_handoff(bytes: &[u8], source_index: usize) -> Result<SourcePopulation> {
    let handoff: PosteriorHandoff =
        serde_json::from_slice(bytes).context("source handoff is not valid JSON")?;
    handoff
        .validate()
        .map_err(anyhow::Error::new)
        .context("source posterior handoff is invalid")?;
    if handoff
        .particles
        .iter()
        .any(|particle| particle.lateral_mode != LateralMode::ConstantTrueTrack)
    {
        bail!("typed continuation currently supports constant-true-track handoffs only");
    }
    Ok(SourcePopulation {
        source_index,
        handoff,
    })
}

fn validate_source_populations(populations: &[SourcePopulation]) -> Result<()> {
    let first = populations
        .first()
        .context("at least one source handoff is required")?;
    let family = &first.handoff.run.model_family;
    let config_sha256 = &first.handoff.run.config_sha256;
    let input_sha256 = &first.handoff.run.input_sha256;
    let evidence = &first.handoff.evidence;
    let first_particle = first
        .handoff
        .particles
        .first()
        .context("source handoff contains no particles")?;
    let checkpoint_time = first_particle.aircraft.time;
    let lateral_mode = first_particle.lateral_mode;
    let mut seeds = BTreeMap::new();
    for population in populations {
        if population.handoff.run.model_family != *family {
            bail!("implicit mixing of posterior model families is not permitted");
        }
        if population.handoff.run.config_sha256 != *config_sha256
            || population.handoff.run.input_sha256 != *input_sha256
            || population.handoff.evidence != *evidence
        {
            bail!("numerical replicate handoffs must share configuration, inputs, and evidence");
        }
        if population.handoff.particles.iter().any(|particle| {
            particle.aircraft.time != checkpoint_time || particle.lateral_mode != lateral_mode
        }) {
            bail!("numerical replicate handoffs must share checkpoint time and lateral mode");
        }
        if seeds
            .insert(population.handoff.run.seed, population.source_index)
            .is_some()
        {
            bail!("source handoff seeds must be unique numerical replicates");
        }
    }
    Ok(())
}

fn consume_evidence_atomically(
    populations: &mut [SourcePopulation],
    identity: EvidenceIdentity,
) -> Result<()> {
    let mut ledgers = populations
        .iter()
        .map(|population| population.handoff.evidence.clone())
        .collect::<Vec<EvidenceLedger>>();
    for ledger in &mut ledgers {
        ledger.consume(identity.clone())?;
    }
    for (population, ledger) in populations.iter_mut().zip(ledgers) {
        population.handoff.evidence = ledger;
    }
    Ok(())
}

fn source_particles(populations: &[SourcePopulation]) -> Vec<SourceParticle> {
    populations
        .iter()
        .flat_map(|population| {
            population
                .handoff
                .particles
                .iter()
                .cloned()
                .map(|handoff| SourceParticle {
                    source_index: population.source_index,
                    handoff,
                })
        })
        .collect()
}

fn continuation_elapsed_s(
    source: &mh370_estimator::FlightObservation,
    target: &mh370_estimator::FlightObservation,
) -> Result<f64> {
    let elapsed = target.measurement.time.0 - source.measurement.time.0;
    if !elapsed.is_finite() || elapsed <= 0.0 {
        bail!("target epoch must follow the declared source epoch");
    }
    Ok(elapsed)
}

fn continue_bto_particle(
    source: SourceParticle,
    propagation_duration_s: f64,
    target: &mh370_estimator::FlightObservation,
    observed_us: f64,
    standard_deviation_us: f64,
    satcom: SatcomModelConfig,
) -> Result<ContinuedParticle> {
    let end = propagate_constant_track(source.handoff.aircraft, Seconds(propagation_duration_s))?;
    let predicted_observable = bto(
        end.position,
        end.altitude.0,
        target.measurement.satellite_position_km,
        target.measurement.ground_station_position_km,
        satcom.bto,
    )
    .0;
    let observable_residual = observed_us - predicted_observable;
    let log_likelihood = normal_log_density(observable_residual, standard_deviation_us)?;
    Ok(ContinuedParticle {
        source_index: source.source_index,
        prior_weight: source.handoff.normalized_log_weight.exp(),
        source: source.handoff,
        log_likelihood,
        weight: 0.0,
        predicted_observable,
        observable_residual,
        end,
    })
}

fn normalize_continued_particles(
    populations: &[SourcePopulation],
    particles: &mut [ContinuedParticle],
) -> Result<ContinuationWeightSummary> {
    let source_count = populations.len();
    let mut seed_posterior_ess = BTreeMap::new();
    let mut seed_log_evidence_increments = BTreeMap::new();
    for population in populations {
        let indices = particles
            .iter()
            .enumerate()
            .filter_map(|(index, particle)| {
                (particle.source_index == population.source_index).then_some(index)
            })
            .collect::<Vec<_>>();
        let maximum_log_weight = indices
            .iter()
            .map(|index| {
                particles[*index].source.normalized_log_weight + particles[*index].log_likelihood
            })
            .fold(f64::NEG_INFINITY, f64::max);
        if !maximum_log_weight.is_finite() {
            bail!(
                "continuation selection has zero posterior probability for seed {}",
                population.handoff.run.seed
            );
        }
        let weight_sum = indices
            .iter()
            .map(|index| {
                (particles[*index].source.normalized_log_weight + particles[*index].log_likelihood
                    - maximum_log_weight)
                    .exp()
            })
            .sum::<f64>();
        if !weight_sum.is_finite() || weight_sum <= 0.0 {
            bail!(
                "continuation selection has zero posterior probability for seed {}",
                population.handoff.run.seed
            );
        }
        let source_scale = 1.0 / source_count as f64;
        for index in &indices {
            particles[*index].weight = (particles[*index].source.normalized_log_weight
                + particles[*index].log_likelihood
                - maximum_log_weight)
                .exp()
                / weight_sum
                * source_scale;
        }
        let seed = population.handoff.run.seed;
        seed_log_evidence_increments.insert(seed, maximum_log_weight + weight_sum.ln());
        let within_seed_ess = 1.0
            / indices
                .iter()
                .map(|index| (particles[*index].weight / source_scale).powi(2))
                .sum::<f64>();
        seed_posterior_ess.insert(seed, within_seed_ess);
    }
    let maximum_log_evidence = seed_log_evidence_increments
        .values()
        .copied()
        .fold(f64::NEG_INFINITY, f64::max);
    let log_evidence_increment = maximum_log_evidence
        + seed_log_evidence_increments
            .values()
            .map(|value| (value - maximum_log_evidence).exp())
            .sum::<f64>()
            .ln()
        - (seed_log_evidence_increments.len() as f64).ln();
    let posterior_ess = 1.0
        / particles
            .iter()
            .map(|particle| particle.weight.powi(2))
            .sum::<f64>();
    Ok(ContinuationWeightSummary {
        seed_posterior_ess,
        seed_log_evidence_increments,
        log_evidence_increment,
        posterior_ess,
    })
}
fn weighted_quantile(particles: &[ContinuedParticle], latitude: bool, probability: f64) -> f64 {
    let mut values = particles
        .iter()
        .map(|particle| {
            (
                if latitude {
                    particle.end.position.latitude.0
                } else {
                    particle.end.position.longitude.0
                },
                particle.weight,
            )
        })
        .collect::<Vec<_>>();
    values.sort_by(|first, second| first.0.total_cmp(&second.0));
    let mut cumulative = 0.0;
    for (value, weight) in values {
        cumulative += weight;
        if cumulative >= probability {
            return value;
        }
    }
    f64::NAN
}

fn weighted_position<'a>(particles: impl Iterator<Item = &'a ContinuedParticle>) -> Result<LatLon> {
    let values = particles.collect::<Vec<_>>();
    let total = values.iter().map(|particle| particle.weight).sum::<f64>();
    let latitude = values
        .iter()
        .map(|particle| particle.end.position.latitude.0 * particle.weight)
        .sum::<f64>()
        / total;
    let sine = values
        .iter()
        .map(|particle| particle.end.position.longitude.to_radians().sin() * particle.weight)
        .sum::<f64>()
        / total;
    let cosine = values
        .iter()
        .map(|particle| particle.end.position.longitude.to_radians().cos() * particle.weight)
        .sum::<f64>()
        / total;
    LatLon::new(latitude, sine.atan2(cosine).to_degrees())
        .context("continued posterior mean is invalid")
}

fn maximum_source_separation(particles: &[ContinuedParticle], source_count: usize) -> Result<f64> {
    let mut means = Vec::with_capacity(source_count);
    for source in 0..source_count {
        means.push(weighted_position(
            particles
                .iter()
                .filter(|particle| particle.source_index == source),
        )?);
    }
    let mut maximum: f64 = 0.0;
    for first in 0..means.len() {
        for second in (first + 1)..means.len() {
            maximum = maximum.max(great_circle_distance_nm(means[first], means[second]).0);
        }
    }
    Ok(maximum)
}

fn posterior_csv(particles: &[ContinuedParticle]) -> Vec<u8> {
    let mut output = String::from(
        "source,model_family,seed,particle,prior_weight,log_selection_likelihood,weight,start_time_s,start_latitude_deg,start_longitude_deg,end_time_s,end_latitude_deg,end_longitude_deg,altitude_ft,track_true_deg,heading_true_deg,ground_speed_kt,mach,bfo_bias_hz,bfo_bias_variance_hz2,predicted_observable,observable_residual,turn_time_s,post_turn_track_true_deg\n",
    );
    for particle in particles {
        let source = &particle.source;
        let _ = std::fmt::Write::write_fmt(
            &mut output,
            format_args!(
                "{},{},{},{},{:.17e},{:.12},{:.17e},{:.6},{:.12},{:.12},{:.6},{:.12},{:.12},{:.3},{:.9},{:.9},{:.9},{:.9},{:.9},{:.9},{:.9},{:.9},{:.6},{:.9}\n",
                particle.source_index,
                source.identity.model_family,
                source.identity.seed,
                source.identity.particle,
                particle.prior_weight,
                particle.log_likelihood,
                particle.weight,
                source.aircraft.time.0,
                source.aircraft.position.latitude.0,
                source.aircraft.position.longitude.0,
                particle.end.time.0,
                particle.end.position.latitude.0,
                particle.end.position.longitude.0,
                particle.end.altitude.0,
                particle.end.track_true.0,
                source.heading_true.0,
                particle.end.ground_speed.0,
                source.mach,
                particle.end.bfo_bias.0,
                source.bfo_bias.variance_hz2,
                particle.predicted_observable,
                particle.observable_residual,
                source.turn.turn_time.0,
                source.turn.post_turn_track_true.0,
            ),
        );
    }
    output.into_bytes()
}
fn build_continued_handoffs(
    populations: &[SourcePopulation],
    particles: &[ContinuedParticle],
    source_count: usize,
    executable_digest: &str,
    config_digest: &str,
    input_sha256: &BTreeMap<String, String>,
) -> Result<Vec<PosteriorHandoff>> {
    let mut output = Vec::with_capacity(populations.len());
    for population in populations {
        let preimage = ContinuationRunIdentityPreimage {
            domain: "mh370-continue-to-contact-run-v1",
            engine_version: env!("CARGO_PKG_VERSION"),
            executable_sha256: executable_digest,
            config_sha256: config_digest,
            input_sha256,
            model_family: &population.handoff.run.model_family,
            seed: population.handoff.run.seed,
            source_run_identity_sha256: &population.handoff.run.run_identity_sha256,
        };
        let run_identity_sha256 = sha256_bytes(&serde_json::to_vec(&preimage)?);
        let continued = particles
            .iter()
            .filter(|particle| {
                particle.source_index == population.source_index
                    && particle.weight.is_finite()
                    && particle.weight > 0.0
                    && particle.log_likelihood.is_finite()
            })
            .map(|particle| {
                let mut source = particle.source.clone();
                source.normalized_log_weight = (particle.weight * source_count as f64).ln();
                source.source_log_likelihood += particle.log_likelihood;
                source.aircraft = particle.end;
                source
            })
            .collect::<Vec<_>>();
        if continued.is_empty() {
            bail!(
                "continued handoff has no finite-weight particles for seed {}",
                population.handoff.run.seed
            );
        }
        let handoff = PosteriorHandoff {
            schema_version: population.handoff.schema_version,
            run: PosteriorRunMetadata {
                model_family: population.handoff.run.model_family.clone(),
                seed: population.handoff.run.seed,
                lateral_mode: population.handoff.run.lateral_mode,
                run_identity_sha256,
                config_sha256: config_digest.to_string(),
                input_sha256: input_sha256.clone(),
                fixed_waypoint: population.handoff.run.fixed_waypoint.clone(),
            },
            evidence: population.handoff.evidence.clone(),
            particles: continued,
        };
        handoff
            .validate()
            .map_err(anyhow::Error::new)
            .context("generated continued handoff is invalid")?;
        output.push(handoff);
    }
    Ok(output)
}

fn bto_arc(
    latitude_min: f64,
    latitude_max: f64,
    reference_longitude: f64,
    altitude_ft: f64,
    target_bto_us: f64,
    satellite_position_km: Vec3,
    ground_station_position_km: Vec3,
    satcom: SatcomModelConfig,
) -> Vec<[f64; 2]> {
    let residual = |latitude: f64, longitude: f64| {
        let position = LatLon::new(latitude, longitude).expect("arc grid coordinate is valid");
        bto(
            position,
            altitude_ft,
            satellite_position_km,
            ground_station_position_km,
            satcom.bto,
        )
        .0 - target_bto_us
    };
    let mut arc = Vec::new();
    for index in 0..=120 {
        let latitude = latitude_min + (latitude_max - latitude_min) * index as f64 / 120.0;
        let mut roots = Vec::new();
        let mut left = 55.0;
        let mut left_value = residual(latitude, left);
        for step in 1..=280 {
            let right = 55.0 + 70.0 * step as f64 / 280.0;
            let right_value = residual(latitude, right);
            if left_value == 0.0 || (left_value < 0.0) != (right_value < 0.0) {
                let mut low = left;
                let mut high = right;
                let mut low_value = left_value;
                for _ in 0..48 {
                    let midpoint = 0.5 * (low + high);
                    let midpoint_value = residual(latitude, midpoint);
                    if (low_value < 0.0) != (midpoint_value < 0.0) {
                        high = midpoint;
                    } else {
                        low = midpoint;
                        low_value = midpoint_value;
                    }
                }
                roots.push(0.5 * (low + high));
            }
            left = right;
            left_value = right_value;
        }
        if let Some(longitude) = roots.into_iter().min_by(|first, second| {
            (first - reference_longitude)
                .abs()
                .total_cmp(&(second - reference_longitude).abs())
        }) {
            arc.push([latitude, longitude]);
        }
    }
    arc
}

pub(crate) fn continue_to_contact(config_path: &Path, output: &Path) -> Result<()> {
    let started = Instant::now();
    let config_bytes =
        fs::read(config_path).with_context(|| format!("cannot read {}", config_path.display()))?;
    let config_text =
        std::str::from_utf8(&config_bytes).context("continuation config is not UTF-8")?;
    let config: ContinuationConfig =
        toml::from_str(config_text).context("cannot parse continuation TOML")?;
    let config_digest = sha256_bytes(&config_bytes);
    let executable_digest = executable_sha256()?;
    if config.schema_version != 2
        || config.name.trim().is_empty()
        || config.source_handoffs.is_empty()
        || config.inputs.source_epoch_id.trim().is_empty()
        || config.inputs.target_epoch_id.trim().is_empty()
        || config.inputs.target_channel.trim().is_empty()
        || config.plotted_paths == 0
    {
        bail!("continuation configuration is incomplete");
    }
    config.satcom.validate()?;
    prepare_output(output)?;

    let observation_path = resolve(config_path, &config.inputs.observations);
    let ephemeris_path = resolve(config_path, &config.inputs.satellite_ephemeris);
    let observation_bytes = fs::read(&observation_path)
        .with_context(|| format!("cannot read {}", observation_path.display()))?;
    let ephemeris_bytes = fs::read(&ephemeris_path)
        .with_context(|| format!("cannot read {}", ephemeris_path.display()))?;
    let observations = parse_satcom_observations(
        std::str::from_utf8(&observation_bytes).context("observation CSV is not UTF-8")?,
        std::str::from_utf8(&ephemeris_bytes).context("ephemeris CSV is not UTF-8")?,
        config.inputs.ground_station_position_km,
        None,
    )?;
    let target = observations
        .iter()
        .find(|observation| observation.id == config.inputs.target_epoch_id)
        .context("target epoch is absent from the SATCOM input")?;
    let source_epoch = observations
        .iter()
        .find(|observation| observation.id == config.inputs.source_epoch_id)
        .context("source epoch is absent from the SATCOM input")?;
    let propagation_duration_s = continuation_elapsed_s(source_epoch, target)?;
    let target_bto = if matches!(&config.selection, ContinuationSelection::Bto) {
        Some(
            target
                .measurement
                .bto
                .zip(target.measurement.bto_sd)
                .context("target epoch lacks a complete BTO observation")?,
        )
    } else {
        None
    };

    let mut input_sha256 = BTreeMap::from([
        (
            observation_path.display().to_string(),
            sha256_bytes(&observation_bytes),
        ),
        (
            ephemeris_path.display().to_string(),
            sha256_bytes(&ephemeris_bytes),
        ),
    ]);
    let mut handoff_input_sha256 = BTreeMap::from([
        (
            "satcom_observations".to_string(),
            sha256_bytes(&observation_bytes),
        ),
        (
            "satellite_ephemeris".to_string(),
            sha256_bytes(&ephemeris_bytes),
        ),
    ]);
    let power_grid = match &config.selection {
        ContinuationSelection::Bto => None,
        ContinuationSelection::ConditionalPower {
            surface,
            observed_dbm,
            observation_adjustment_db,
            observation_sd_db,
            reference_gain_dbic,
            directional_departure_scale,
            ..
        } => {
            if ![
                *observed_dbm,
                *observation_adjustment_db,
                *observation_sd_db,
                *reference_gain_dbic,
                *directional_departure_scale,
            ]
            .iter()
            .all(|value| value.is_finite())
                || *observation_sd_db <= 0.0
                || !(0.0..=1.0).contains(directional_departure_scale)
            {
                bail!("conditional startup-power selection is invalid");
            }
            let path = resolve(config_path, surface);
            let bytes = fs::read(&path)
                .with_context(|| format!("cannot read antenna surface {}", path.display()))?;
            input_sha256.insert(path.display().to_string(), sha256_bytes(&bytes));
            handoff_input_sha256.insert("antenna_surface".to_string(), sha256_bytes(&bytes));
            Some(DirectionalGainGrid::parse(
                &bytes,
                DirectionalPatternBasis::UnverifiedReconstruction,
            )?)
        }
    };
    let mut populations = Vec::new();
    for (source_index, configured_path) in config.source_handoffs.iter().enumerate() {
        let path = resolve(config_path, configured_path);
        let bytes = fs::read(&path)
            .with_context(|| format!("cannot read source handoff {}", path.display()))?;
        let population = parse_source_handoff(&bytes, source_index)?;
        let seed = population.handoff.run.seed;
        let digest = sha256_bytes(&bytes);
        handoff_input_sha256.insert(format!("source_handoff_seed_{seed}"), digest.clone());
        populations.push(population);
        input_sha256.insert(path.display().to_string(), digest);
    }
    validate_source_populations(&populations)?;
    let target_component = match &config.selection {
        ContinuationSelection::Bto => EvidenceComponent::Bto,
        ContinuationSelection::ConditionalPower { .. } => EvidenceComponent::ReceivedPower,
    };
    consume_evidence_atomically(
        &mut populations,
        EvidenceIdentity {
            epoch_id: target.id.clone(),
            channel: Some(config.inputs.target_channel.clone()),
            component: target_component,
        },
    )?;

    let source_count = populations.len();
    let sources = source_particles(&populations);
    let mut particles = Vec::with_capacity(sources.len());
    for source in sources {
        if let ContinuationSelection::Bto = &config.selection {
            let (observed, standard_deviation) =
                target_bto.expect("BTO selection was validated before propagation");
            particles.push(continue_bto_particle(
                source,
                propagation_duration_s,
                target,
                observed.0,
                standard_deviation.0,
                config.satcom,
            )?);
            continue;
        }
        let start = source.handoff.aircraft;
        let end = propagate_constant_track(start, Seconds(propagation_duration_s))?;
        let (predicted_observable, observable_residual, log_likelihood) = match &config.selection {
            ContinuationSelection::Bto => unreachable!("BTO continuation returned above"),
            ContinuationSelection::ConditionalPower {
                observed_dbm,
                observation_adjustment_db,
                observation_sd_db,
                reference_gain_dbic,
                directional_departure_scale,
                permit_unverified_reconstruction,
                link,
                ..
            } => {
                let adjusted_observed = observed_dbm + observation_adjustment_db;
                let prediction = target_eirp_prediction(
                    end,
                    target.measurement.satellite_position_km,
                    target.measurement.ground_station_position_km,
                    *link,
                )?;
                let score = evaluate_conditional_power(
                    end,
                    AircraftAttitude::level(source.handoff.heading_true),
                    target.measurement.satellite_position_km,
                    power_grid.as_ref().expect("power surface was loaded"),
                    ConditionalPowerObservation {
                        observed_dbm: adjusted_observed,
                        full_precompensation_prediction_dbm: prediction
                            .full_precompensation_prediction_dbm,
                        standard_deviation_db: *observation_sd_db,
                        reference_gain_dbic: *reference_gain_dbic,
                        directional_departure_scale: *directional_departure_scale,
                        permit_unverified_reconstruction: *permit_unverified_reconstruction,
                    },
                );
                match score {
                    Ok(score) => (
                        score.predicted_dbm,
                        adjusted_observed - score.predicted_dbm,
                        score.log_likelihood.context(
                            "unverified antenna likelihood was not explicitly permitted",
                        )?,
                    ),
                    Err(AntennaError::BelowHorizon) => (f64::NAN, f64::NAN, f64::NEG_INFINITY),
                    Err(error) => return Err(error.into()),
                }
            }
        };
        particles.push(ContinuedParticle {
            source_index: source.source_index,
            prior_weight: source.handoff.normalized_log_weight.exp(),
            source: source.handoff,
            log_likelihood,
            weight: 0.0,
            predicted_observable,
            observable_residual,
            end,
        });
    }

    let weight_summary = normalize_continued_particles(&populations, &mut particles)?;
    let seed_posterior_ess = weight_summary.seed_posterior_ess;
    let seed_log_evidence_increments = weight_summary.seed_log_evidence_increments;
    let log_evidence_increment = weight_summary.log_evidence_increment;
    let posterior_ess = weight_summary.posterior_ess;
    let endpoint_mean = weighted_position(particles.iter())?;
    let latitude_90 = [
        weighted_quantile(&particles, true, 0.05),
        weighted_quantile(&particles, true, 0.95),
    ];
    let longitude_90 = [
        weighted_quantile(&particles, false, 0.05),
        weighted_quantile(&particles, false, 0.95),
    ];
    let maximum_source_mean_separation_nm = maximum_source_separation(&particles, source_count)?;

    let continued_handoffs = build_continued_handoffs(
        &populations,
        &particles,
        source_count,
        &executable_digest,
        &config_digest,
        &handoff_input_sha256,
    )?;
    let mut handoff_paths = Vec::with_capacity(continued_handoffs.len());
    for handoff in &continued_handoffs {
        let relative = PathBuf::from(format!("seed-{}/posterior-handoff.json", handoff.run.seed));
        let path = output.join(&relative);
        write_json(&path, handoff)?;
        handoff_paths.push((relative, path));
    }

    let posterior_path = output.join("posterior.csv");
    atomic_write(&posterior_path, &posterior_csv(&particles))?;

    let report_points = particles
        .iter()
        .map(|particle| ReportPoint {
            latitude_deg: particle.end.position.latitude.0,
            longitude_deg: particle.end.position.longitude.0,
            weight: particle.weight,
        })
        .collect::<Vec<_>>();
    let start_latitude_min = particles
        .iter()
        .map(|particle| particle.source.aircraft.position.latitude.0)
        .fold(f64::INFINITY, f64::min);
    let start_latitude_max = particles
        .iter()
        .map(|particle| particle.source.aircraft.position.latitude.0)
        .fold(f64::NEG_INFINITY, f64::max);
    let start_longitude_min = particles
        .iter()
        .map(|particle| particle.source.aircraft.position.longitude.0)
        .fold(f64::INFINITY, f64::min);
    let start_longitude_max = particles
        .iter()
        .map(|particle| particle.source.aircraft.position.longitude.0)
        .fold(f64::NEG_INFINITY, f64::max);
    let bounds = ReportMapBounds {
        longitude_min_deg: start_longitude_min.min(longitude_90[0]) - 0.8,
        longitude_max_deg: start_longitude_max.max(longitude_90[1]) + 0.8,
        latitude_min_deg: start_latitude_min.min(latitude_90[0]) - 0.8,
        latitude_max_deg: start_latitude_max.max(latitude_90[1]) + 0.8,
    };
    let mut ranked = particles.iter().collect::<Vec<_>>();
    ranked.sort_by(|first, second| second.weight.total_cmp(&first.weight));
    let mut routes = ranked
        .into_iter()
        .take(config.plotted_paths.min(particles.len()))
        .map(|particle| ReportMapRoute {
            label: String::new(),
            style: "candidate".to_string(),
            coordinates_deg: vec![
                [
                    particle.source.aircraft.position.latitude.0,
                    particle.source.aircraft.position.longitude.0,
                ],
                [
                    particle.end.position.latitude.0,
                    particle.end.position.longitude.0,
                ],
            ],
        })
        .collect::<Vec<_>>();
    let (
        title,
        subtitle_suffix,
        selection_label,
        selection_summary,
        evidence_condition,
        limitations,
        selection_scope,
    ) = match &config.selection {
        ContinuationSelection::Bto => {
            let (observed, standard_deviation) =
                target_bto.expect("BTO selection was validated before reporting");
            let altitude_mean = particles
                .iter()
                .map(|particle| particle.end.altitude.0 * particle.weight)
                .sum::<f64>();
            routes.push(ReportMapRoute {
                label: "7th BTO arc".to_string(),
                style: "arc".to_string(),
                coordinates_deg: bto_arc(
                    bounds.latitude_min_deg,
                    bounds.latitude_max_deg,
                    endpoint_mean.longitude.0,
                    altitude_mean,
                    observed.0,
                    target.measurement.satellite_position_km,
                    target.measurement.ground_station_position_km,
                    config.satcom,
                ),
            });
            (
                    "MH370 00:11 to 00:19 constant-true-track control".to_string(),
                    "BTO-only selection".to_string(),
                    "00:19 R600 BTO only".to_string(),
                    format!(
                        "{} BTO {:.0} +/- {:.0} us",
                        target.time_utc, observed.0, standard_deviation.0
                    ),
                    "00:11 posterior propagated to 00:19:29; selection uses time and seventh-arc BTO distance only.".to_string(),
                    vec![
                        "The 00:19:29 R600 BTO is the only new selection observable.".to_string(),
                        "No 00:19 BFO, startup received power, end-of-flight displacement, drift, hydroacoustics, or antenna likelihood is applied.".to_string(),
                        "Control model: short continuation paths preserve each 00:11 particle's final constant true track, ground speed, and altitude.".to_string(),
                        "The interval is conditional on the one-turn and frozen-continuation model; it is not full MH370 path uncertainty.".to_string(),
                    ],
                    vec![
                        "Only the target epoch's BTO likelihood updates particle probability.".to_string(),
                        "The report overlays a calculated equal-BTO arc at posterior-weighted mean altitude.".to_string(),
                    ],
                )
        }
        ContinuationSelection::ConditionalPower {
            observed_dbm,
            observation_adjustment_db,
            observation_sd_db,
            directional_departure_scale,
            ..
        } => {
            let adjusted = observed_dbm + observation_adjustment_db;
            (
                    "MH370 00:11 to 00:19 conditional startup-power control".to_string(),
                    "startup power only; no 00:19 BTO".to_string(),
                    "00:19 R600 startup power only (conditional)".to_string(),
                    format!(
                        "{} Rx power {:.2} dBm (adjusted), SD {:.1} dB",
                        target.time_utc, adjusted, observation_sd_db
                    ),
                    "00:11 posterior propagated to 00:19:29; only conditionally modelled startup received power updates the weights.".to_string(),
                    vec![
                        "The 00:19:29 R600 received power is the only new selection observable; its BTO and BFO are not applied.".to_string(),
                        format!(
                            "The raw R600 observation is adjusted by {:+.1} dB to the regular R1200 reference chain.",
                            observation_adjustment_db
                        ),
                        format!(
                            "The antenna surface is an unverified reconstruction and the directional-departure endpoint is {:.2}; this is a conditional sensitivity and is not applied to the core posterior.",
                            directional_departure_scale
                        ),
                        "Each particle's stored 00:11 true heading is held fixed for antenna attitude during this frozen constant-track continuation.".to_string(),
                        "Control model: short continuation paths preserve each 00:11 particle's final constant true track, ground speed, and altitude.".to_string(),
                        "The interval is conditional on the one-turn and frozen-continuation model; it is not full MH370 path uncertainty.".to_string(),
                    ],
                    vec![
                        "Only the adjusted target epoch startup-power likelihood updates particle probability.".to_string(),
                        "No equal-BTO arc is plotted because the target epoch BTO is deliberately held out.".to_string(),
                    ],
                )
        }
    };

    let document = ReportDocument {
        title: title.clone(),
        subtitle: format!(
            "{} | {} typed source handoffs | {}",
            config.name, source_count, subtitle_suffix
        ),
        summary: vec![
            ("Particles".to_string(), particles.len().to_string()),
            (
                "Pooled numerical ESS".to_string(),
                format!("{posterior_ess:.0}"),
            ),
            (
                "Minimum seed ESS".to_string(),
                format!(
                    "{:.0}",
                    seed_posterior_ess
                        .values()
                        .copied()
                        .fold(f64::INFINITY, f64::min)
                ),
            ),
            (
                "Endpoint mean".to_string(),
                format!(
                    "{:.3} deg, {:.3} deg E",
                    endpoint_mean.latitude.0, endpoint_mean.longitude.0
                ),
            ),
            (
                "90% latitude".to_string(),
                format!("{:.2} to {:.2} deg", latitude_90[0], latitude_90[1]),
            ),
            (
                "90% longitude".to_string(),
                format!("{:.2} to {:.2} deg E", longitude_90[0], longitude_90[1]),
            ),
            (
                "Source mean separation".to_string(),
                format!("{maximum_source_mean_separation_nm:.1} NM"),
            ),
            ("Selection".to_string(), selection_summary),
        ],
        points: report_points,
        diagnostics: Vec::new(),
        evidence_conditions: vec![evidence_condition],
        limitations: limitations.clone(),
        map_context: Some(ReportMapContext {
            bounds,
            references: Vec::new(),
            routes,
        }),
    };
    let pdf_path = output.join("report.pdf");
    let svg_path = output.join("posterior.svg");
    let png_path = output.join("posterior.png");
    atomic_write(&pdf_path, &build_pdf(&document)?)?;
    atomic_write(&svg_path, &build_posterior_svg(&document)?)?;
    atomic_write(&png_path, &build_accident_panel_png(&document)?)?;

    let summary = ContinuationSummary {
        schema_version: 2,
        name: config.name,
        status: "complete".to_string(),
        model_scope: "short-horizon frozen constant-true-track control; not the physical end-of-flight transition kernel".to_string(),
        selection: selection_label.clone(),
        source_epoch_id: source_epoch.id.clone(),
        target_epoch_id: target.id.clone(),
        target_time_utc: target.time_utc.clone(),
        propagation_duration_s,
        source_handoffs: source_count,
        particles: particles.len(),
        posterior_ess,
        seed_posterior_ess,
        log_evidence_increment,
        seed_log_evidence_increments,
        endpoint_mean,
        endpoint_latitude_90_deg: latitude_90,
        endpoint_longitude_90_deg: longitude_90,
        maximum_source_mean_separation_nm,
        elapsed_seconds: started.elapsed().as_secs_f64(),
        limitations,
    };
    let summary_path = output.join("summary.json");
    write_json(&summary_path, &summary)?;

    let mut outputs = BTreeMap::new();
    for path in [
        &summary_path,
        &posterior_path,
        &pdf_path,
        &svg_path,
        &png_path,
    ] {
        outputs.insert(
            path.file_name().unwrap().to_string_lossy().to_string(),
            sha256_file(path)?,
        );
    }
    for (relative, path) in &handoff_paths {
        outputs.insert(relative.display().to_string(), sha256_file(path)?);
    }
    let mut scientific_scope = vec![
        "This is a typed conditional continuation of completed 00:11 posterior handoffs, not a fresh fit.".to_string(),
        "The frozen constant-true-track propagation is a short-horizon control and is not the physical end-of-flight transition model.".to_string(),
        "Each numerical seed is updated and normalized independently; the report gives every seed equal mixture weight.".to_string(),
        "Only the explicitly selected target evidence is consumed atomically from each source evidence ledger.".to_string(),
    ];
    scientific_scope.extend(selection_scope);
    let manifest = ContinuationManifest {
        schema_version: 1,
        engine_version: env!("CARGO_PKG_VERSION"),
        executable_sha256: executable_digest,
        command: "continue-to-contact",
        config_path: config_path.display().to_string(),
        config_sha256: config_digest,
        input_sha256,
        outputs,
        scientific_scope,
    };
    write_json(&output.join("run-manifest.json"), &manifest)?;

    println!(
        "status=complete particles={} ess={:.1} mean=({:.4},{:.4}) source_separation_nm={:.2} summary={}",
        summary.particles,
        summary.posterior_ess,
        summary.endpoint_mean.latitude.0,
        summary.endpoint_mean.longitude.0,
        summary.maximum_source_mean_separation_nm,
        summary_path.display()
    );
    Ok(())
}

#[cfg(test)]
mod tests {
    use mh370_domain::{
        Degrees, Feet, FeetPerMinute, Hertz, Knots, Microseconds, SatcomObservation,
    };
    use mh370_estimator::{
        EvidenceDisposition, FlightObservation, PosteriorParticleIdentity, TurnMetadata,
        POSTERIOR_HANDOFF_SCHEMA_VERSION,
    };
    use mh370_satcom::{BfoBiasState, BfoConstants, BtoConstants};

    use super::*;

    fn target_bto_identity() -> EvidenceIdentity {
        EvidenceIdentity {
            epoch_id: "m0019a".to_string(),
            channel: Some("R600".to_string()),
            component: EvidenceComponent::Bto,
        }
    }

    fn particle(
        family: &str,
        seed: u64,
        index: usize,
        normalized_weight: f64,
    ) -> PosteriorHandoffParticle {
        let bias = BfoBiasState {
            mean_hz: 150.0 + index as f64,
            variance_hz2: 4.0 + index as f64,
        };
        PosteriorHandoffParticle {
            identity: PosteriorParticleIdentity {
                model_family: family.to_string(),
                seed,
                particle: index,
            },
            normalized_log_weight: normalized_weight.ln(),
            source_log_likelihood: -20.0 - index as f64,
            aircraft: AircraftState {
                time: Seconds(20_927.0),
                position: LatLon::new(-36.0 - index as f64 * 0.01, 89.0).unwrap(),
                altitude: Feet(35_000.0),
                track_true: Degrees(180.0),
                ground_speed: Knots(480.0),
                vertical_speed: FeetPerMinute(0.0),
                bfo_bias: Hertz(bias.mean_hz),
            },
            heading_true: Degrees(182.0),
            lateral_mode: LateralMode::ConstantTrueTrack,
            mach: 0.82,
            turn: TurnMetadata {
                initial_position: LatLon::new(6.0, 96.0).unwrap(),
                initial_track_true: Degrees(295.0),
                turn_time: Seconds(1_700.0),
                post_turn_track_true: Degrees(180.0),
                turn_count: 1,
            },
            bfo_bias: bias,
        }
    }

    fn handoff(family: &str, seed: u64, disposition: EvidenceDisposition) -> PosteriorHandoff {
        let mut evidence = EvidenceLedger::new();
        evidence.record(target_bto_identity(), disposition).unwrap();
        PosteriorHandoff {
            schema_version: POSTERIOR_HANDOFF_SCHEMA_VERSION,
            run: PosteriorRunMetadata {
                model_family: family.to_string(),
                seed,
                lateral_mode: Some(LateralMode::ConstantTrueTrack),
                run_identity_sha256: "a".repeat(64),
                config_sha256: "b".repeat(64),
                input_sha256: BTreeMap::from([("satcom".to_string(), "c".repeat(64))]),
                fixed_waypoint: None,
            },
            evidence,
            particles: vec![
                particle(family, seed, 0, 0.5),
                particle(family, seed, 1, 0.5),
            ],
        }
    }

    fn observation(id: &str, time_s: f64) -> FlightObservation {
        FlightObservation {
            id: id.to_string(),
            time_utc: "2014-03-08T00:11:00Z".to_string(),
            satellite_afc_hz: 0.0,
            measurement: SatcomObservation {
                time: Seconds(time_s),
                satellite_position_km: Vec3::new(1.0, 2.0, 3.0),
                satellite_velocity_km_s: Vec3::new(0.0, 0.0, 0.0),
                ground_station_position_km: Vec3::new(4.0, 5.0, 6.0),
                bto: Some(Microseconds(18_000.0)),
                bto_sd: Some(Microseconds(50.0)),
                bfo: None,
                bfo_sd: None,
            },
        }
    }

    fn bto_continuation_regression(
        population: SourcePopulation,
    ) -> (Vec<u8>, Vec<u8>, ContinuationWeightSummary) {
        let mut populations = vec![population];
        consume_evidence_atomically(&mut populations, target_bto_identity()).unwrap();
        let target = FlightObservation {
            id: "m0019a".to_string(),
            time_utc: "2014-03-08T00:19:29Z".to_string(),
            satellite_afc_hz: 0.0,
            measurement: SatcomObservation {
                time: Seconds(22_660.0),
                satellite_position_km: Vec3::new(17_921.0, -38_150.0, 211.0),
                satellite_velocity_km_s: Vec3::new(0.0, 0.0, 0.0),
                ground_station_position_km: Vec3::new(-2_368.8, 4_881.1, -3_342.0),
                bto: Some(Microseconds(18_400.0)),
                bto_sd: Some(Microseconds(63.0)),
                bfo: None,
                bfo_sd: None,
            },
        };
        let satcom = SatcomModelConfig {
            bto: BtoConstants {
                speed_of_light_km_s: 299_792.458,
                nominal_delay_us: 499_962.0,
                channel_term_us: 4_283.0,
            },
            bfo: BfoConstants {
                satellite_afc_hz: 0.0,
                uplink_hz: 1_646_652_500.0,
                downlink_hz: 3_615_152_500.0,
                speed_of_light_km_s: 299_792.458,
                nominal_satellite_longitude_deg: 64.5,
                nominal_satellite_altitude_km: 36_210.12,
            },
            bfo_bias_prior_mean_hz: 150.0,
            bfo_bias_prior_sd_hz: 25.0,
        };
        let mut particles = source_particles(&populations)
            .into_iter()
            .map(|source| {
                continue_bto_particle(source, 510.0, &target, 18_400.0, 63.0, satcom).unwrap()
            })
            .collect::<Vec<_>>();
        let summary = normalize_continued_particles(&populations, &mut particles).unwrap();
        let output = build_continued_handoffs(
            &populations,
            &particles,
            populations.len(),
            &"d".repeat(64),
            &"e".repeat(64),
            &BTreeMap::from([("fixture".to_string(), "f".repeat(64))]),
        )
        .unwrap();
        (
            posterior_csv(&particles),
            serde_json::to_vec(&output).unwrap(),
            summary,
        )
    }

    #[test]
    fn typed_handoff_round_trip_and_mode_rejection() {
        let source = handoff("medium-bfo", 370_023, EvidenceDisposition::HeldOut);
        let bytes = serde_json::to_vec(&source).unwrap();
        let parsed = parse_source_handoff(&bytes, 2).unwrap();
        assert_eq!(parsed.source_index, 2);
        assert_eq!(parsed.handoff, source);

        let mut unsupported = source;
        unsupported.particles[0].lateral_mode = LateralMode::ConstantTrueHeading;
        let bytes = serde_json::to_vec(&unsupported).unwrap();
        assert!(parse_source_handoff(&bytes, 0).is_err());
    }

    #[test]
    fn serialized_typed_handoff_continuation_is_numerically_exact() {
        let in_memory = SourcePopulation {
            source_index: 0,
            handoff: handoff("medium-bfo", 370_023, EvidenceDisposition::HeldOut),
        };
        let encoded = serde_json::to_vec(&in_memory.handoff).unwrap();
        let decoded = parse_source_handoff(&encoded, 0).unwrap();

        let direct = bto_continuation_regression(in_memory);
        let serialized = bto_continuation_regression(decoded);
        assert_eq!(direct, serialized);
    }

    #[test]
    fn shifted_origin_uses_declared_epoch_interval() {
        let source = observation("m0011", 22_150.0);
        let target = observation("m0019a", 22_660.0);
        assert_eq!(continuation_elapsed_s(&source, &target).unwrap(), 510.0);
        assert_eq!(
            20_927.0 + continuation_elapsed_s(&source, &target).unwrap(),
            21_437.0
        );
        assert_eq!(target.measurement.time.0 - 20_927.0, 1_733.0);
        assert!(continuation_elapsed_s(&source, &source).is_err());
    }

    #[test]
    fn evidence_consumption_is_atomic_across_seeds() {
        let mut populations = vec![
            SourcePopulation {
                source_index: 0,
                handoff: handoff("medium-bfo", 370_023, EvidenceDisposition::HeldOut),
            },
            SourcePopulation {
                source_index: 1,
                handoff: handoff("medium-bfo", 370_024, EvidenceDisposition::Consumed),
            },
        ];
        let before = populations
            .iter()
            .map(|population| population.handoff.evidence.clone())
            .collect::<Vec<_>>();
        assert!(consume_evidence_atomically(&mut populations, target_bto_identity()).is_err());
        for (population, expected) in populations.iter().zip(before) {
            assert_eq!(population.handoff.evidence, expected);
        }
    }

    #[test]
    fn numerical_replicates_must_share_family_and_have_unique_seeds() {
        let valid = vec![
            SourcePopulation {
                source_index: 0,
                handoff: handoff("medium-bfo", 370_023, EvidenceDisposition::HeldOut),
            },
            SourcePopulation {
                source_index: 1,
                handoff: handoff("medium-bfo", 370_024, EvidenceDisposition::HeldOut),
            },
        ];
        validate_source_populations(&valid).unwrap();

        let mut incompatible = valid.clone();
        incompatible[1].handoff.run.config_sha256 = "d".repeat(64);
        assert!(validate_source_populations(&incompatible).is_err());

        let mixed = vec![
            valid[0].clone(),
            SourcePopulation {
                source_index: 1,
                handoff: handoff("conditional-gain", 370_024, EvidenceDisposition::HeldOut),
            },
        ];
        assert!(validate_source_populations(&mixed).is_err());

        let duplicate_seed = vec![valid[0].clone(), valid[0].clone()];
        assert!(validate_source_populations(&duplicate_seed).is_err());
    }

    #[test]
    fn continued_handoffs_are_normalized_within_each_seed() {
        let populations = vec![
            SourcePopulation {
                source_index: 0,
                handoff: handoff("medium-bfo", 370_023, EvidenceDisposition::Consumed),
            },
            SourcePopulation {
                source_index: 1,
                handoff: handoff("medium-bfo", 370_024, EvidenceDisposition::Consumed),
            },
        ];
        let weights = [[0.4, 0.1], [0.05, 0.45]];
        let particles = populations
            .iter()
            .flat_map(|population| {
                population
                    .handoff
                    .particles
                    .iter()
                    .enumerate()
                    .map(|(index, source)| ContinuedParticle {
                        source_index: population.source_index,
                        source: source.clone(),
                        prior_weight: 0.25,
                        log_likelihood: -1.0,
                        weight: weights[population.source_index][index],
                        predicted_observable: 0.0,
                        observable_residual: 0.0,
                        end: source.aircraft,
                    })
                    .collect::<Vec<_>>()
            })
            .collect::<Vec<_>>();
        let input_sha256 = BTreeMap::from([("handoff".to_string(), "d".repeat(64))]);
        let output = build_continued_handoffs(
            &populations,
            &particles,
            populations.len(),
            &"e".repeat(64),
            &"f".repeat(64),
            &input_sha256,
        )
        .unwrap();
        assert_eq!(output.len(), 2);
        for handoff in &output {
            handoff.validate().unwrap();
            let sum = handoff
                .particles
                .iter()
                .map(|particle| particle.normalized_log_weight.exp())
                .sum::<f64>();
            assert!((sum - 1.0).abs() < 1e-12);
        }
        assert!((output[0].particles[0].normalized_log_weight.exp() - 0.8).abs() < 1e-12);
        assert!((output[1].particles[1].normalized_log_weight.exp() - 0.9).abs() < 1e-12);
        assert_eq!(output[0].particles[0].identity.particle, 0);
        assert_eq!(output[0].particles[0].bfo_bias.variance_hz2, 4.0);
    }
}
