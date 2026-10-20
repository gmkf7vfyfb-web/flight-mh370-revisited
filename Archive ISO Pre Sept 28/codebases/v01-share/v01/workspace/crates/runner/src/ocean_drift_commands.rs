use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    io::{BufReader, Read},
    path::{Path, PathBuf},
    time::{Instant, SystemTime, UNIX_EPOCH},
};

use anyhow::{bail, Context, Result};
use mh370_ocean_drift::{
    evaluate_source_area, ArrivalSamplingConfig, BarnacleChronology, BarnacleIsotopeModel,
    BarnacleRecord, DebrisEvidence, DebrisMotionFamily, DriftEnvironment, GriddedField,
    MotionConfig, SourceAreaCell, SourceAreaConfig, SourceAreaResult,
};
use mh370_reporting::{
    build_accident_panel_png, build_pdf, build_posterior_svg, DiagnosticPoint, ReportDocument,
    ReportMapContext, ReportPoint,
};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};

use crate::{
    atomic_write, executable_sha256, prepare_output, sha256_bytes, sha256_file, write_json,
};

#[derive(Debug, Clone, Deserialize)]
struct FieldInput {
    binary: PathBuf,
    metadata: PathBuf,
    /// Optional hard support rule; interpolation across a larger timestamp
    /// gap terminates as outside-time support.
    maximum_interpolation_gap_hours: Option<f64>,
    /// For schema-3 fields with an independently audited persistent-land
    /// sentinel, use finite corners of the containing cell rather than
    /// rejecting the whole coastal cell. Intermittent missing values still
    /// fail, and no value is ever replaced by zero.
    #[serde(default)]
    renormalize_finite_spatial_corners: bool,
}

#[derive(Debug, Clone, Deserialize)]
struct IsotopeRunConfig {
    records: PathBuf,
    sst: FieldInput,
    chronologies: Vec<BarnacleChronology>,
    seawater_delta18o_per_mil: f64,
    seawater_delta18o_sd_per_mil: f64,
    calibration_sd_c: f64,
    residual_sd_c: f64,
    sst_field_sd_c: f64,
    shell_smoothing_days: f64,
    correlation_days: f64,
    compatible_simultaneous_confidence: f64,
    rejection_simultaneous_confidence: f64,
    maximum_marginal_log_penalty: f64,
    maximum_rejection_log_penalty: f64,
}

#[derive(Debug, Clone, Deserialize)]
struct OceanDriftRunConfig {
    schema_version: u32,
    name: String,
    /// Exactly one incompatible current family is selected per run.
    family: String,
    currents: FieldInput,
    wind: Option<FieldInput>,
    stokes: Option<FieldInput>,
    coast: Option<FieldInput>,
    source_cells: PathBuf,
    seed: u64,
    particles_per_cell: usize,
    release_unix_seconds: f64,
    sampling: ArrivalSamplingConfig,
    /// Schema-2 single-object compatibility input. It is normalized into the
    /// same canonical motion-family implementation used by schema 3.
    motion: Option<MotionConfig>,
    debris: Option<DebrisEvidence>,
    #[serde(default)]
    motion_families: Vec<DebrisMotionFamily>,
    isotope: Option<IsotopeRunConfig>,
    map_context: Option<ReportMapContext>,
}

#[derive(Debug, Deserialize)]
struct SourceCellFile {
    schema: String,
    cells: Vec<SourceAreaCell>,
}

#[derive(Debug, Deserialize)]
struct IsotopeRecordFile {
    schema: String,
    record_count: usize,
    terminal_anchor: String,
    records: Vec<BarnacleRecord>,
}

#[derive(Debug)]
struct LoadedField {
    field: GriddedField,
    binary_sha256: String,
    metadata_sha256: String,
    metadata: Value,
}

struct HashingReader<R> {
    input: R,
    digest: Sha256,
}

impl<R> HashingReader<R> {
    fn new(input: R) -> Self {
        Self {
            input,
            digest: Sha256::new(),
        }
    }

    fn finish(self) -> String {
        format!("{:x}", self.digest.finalize())
    }
}

impl<R: Read> Read for HashingReader<R> {
    fn read(&mut self, buffer: &mut [u8]) -> std::io::Result<usize> {
        let count = self.input.read(buffer)?;
        self.digest.update(&buffer[..count]);
        Ok(count)
    }
}

#[derive(Debug, Serialize)]
struct OceanRunManifest {
    schema_version: u32,
    engine_version: &'static str,
    executable_sha256: String,
    command: &'static str,
    config_path: String,
    config_sha256: String,
    family: String,
    isotope_enabled: bool,
    seed: u64,
    particles_per_cell: usize,
    sampling: ArrivalSamplingConfig,
    coast_enabled: bool,
    current_maximum_interpolation_gap_hours: Option<f64>,
    current_renormalizes_persistent_land_corners: bool,
    motion_family_ids: Vec<String>,
    stokes_velocity_scales: BTreeMap<String, f64>,
    stokes_renormalizes_finite_spatial_corners: bool,
    input_sha256: BTreeMap<String, String>,
    input_metadata: BTreeMap<String, Value>,
    outputs: BTreeMap<String, String>,
    limitations: Vec<String>,
}

#[derive(Debug, Serialize)]
struct RuntimeReceipt {
    schema_version: u32,
    unix_time_s: u64,
    elapsed_seconds: f64,
    source_cells: usize,
    simulated_paths: usize,
    propagated_segments: usize,
    peak_memory_kib: Option<u64>,
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

fn load_field(config_path: &Path, input: &FieldInput, label: &str) -> Result<LoadedField> {
    let binary_path = resolve(config_path, &input.binary);
    let metadata_path = resolve(config_path, &input.metadata);
    let metadata_bytes = fs::read(&metadata_path)
        .with_context(|| format!("cannot read {label} metadata {}", metadata_path.display()))?;
    let metadata_sha256 = sha256_bytes(&metadata_bytes);
    let metadata: Value = serde_json::from_slice(&metadata_bytes)
        .with_context(|| format!("cannot parse {label} metadata"))?;
    if input.renormalize_finite_spatial_corners
        && metadata
            .pointer("/packing/persistent_land_mask_value")
            .and_then(Value::as_i64)
            .is_none()
    {
        bail!("{label} finite-corner renormalization requires a distinct persistent-land sentinel");
    }
    let recorded_hash = metadata
        .get("binary_sha256")
        .and_then(Value::as_str)
        .context("field metadata lacks binary_sha256")?;
    let binary = fs::File::open(&binary_path)
        .with_context(|| format!("cannot open {label} field {}", binary_path.display()))?;
    let mut stream = HashingReader::new(BufReader::with_capacity(1024 * 1024, binary));
    let mut field = GriddedField::from_reader(label, &mut stream)
        .with_context(|| format!("cannot parse {label} field"))?;
    let actual_hash = stream.finish();
    if recorded_hash != actual_hash {
        bail!("{label} field hash mismatch: metadata={recorded_hash}, actual={actual_hash}");
    }
    let maximum_gap_seconds = input
        .maximum_interpolation_gap_hours
        .map(|hours| hours * 3_600.0);
    field
        .set_maximum_time_interpolation_gap_seconds(maximum_gap_seconds)
        .with_context(|| format!("invalid {label} maximum interpolation gap"))?;
    field.set_renormalize_finite_spatial_corners(input.renormalize_finite_spatial_corners);
    Ok(LoadedField {
        field,
        binary_sha256: actual_hash,
        metadata_sha256,
        metadata,
    })
}

fn read_json<T: for<'de> Deserialize<'de>>(path: &Path, label: &str) -> Result<T> {
    let bytes =
        fs::read(path).with_context(|| format!("cannot read {label} {}", path.display()))?;
    serde_json::from_slice(&bytes).with_context(|| format!("cannot parse {label}"))
}

fn resolved_motion_families(config: &OceanDriftRunConfig) -> Result<Vec<DebrisMotionFamily>> {
    match config.schema_version {
        2 if config.motion_families.is_empty() => {
            let motion = config
                .motion
                .context("schema-2 ocean-drift config lacks motion")?;
            let debris = config
                .debris
                .clone()
                .context("schema-2 ocean-drift config lacks debris")?;
            Ok(vec![DebrisMotionFamily {
                id: "configured-object-motion".to_string(),
                motion,
                debris,
            }])
        }
        3 if config.motion.is_none()
            && config.debris.is_none()
            && !config.motion_families.is_empty() =>
        {
            Ok(config.motion_families.clone())
        }
        _ => bail!(
            "schema 2 requires one motion/debris pair; schema 3 requires only motion_families"
        ),
    }
}

fn source_csv(result: &SourceAreaResult) -> Vec<u8> {
    let mut output = String::from(
        "cell_id,latitude_deg,longitude_deg,prior_weight,debris_log_compatibility,conditional_isotope_log_compatibility,combined_log_weight,normalized_weight,importance_weighted_terminated_fraction,proposal_terminated_fraction,status,flaperon_arrival_ess,minimum_recovery_ess,non_recovery_landfall_probability,non_recovery_unresolved_probability,non_recovery_log_compatibility,isotope_compatible_paths,isotope_marginal_paths,isotope_rejected_paths,isotope_missing_coverage_paths,correction_weight_ess,mean_correction_weight\n",
    );
    for cell in &result.cells {
        let isotope = cell
            .conditional_isotope_log_compatibility
            .map(|value| format!("{value:.17e}"))
            .unwrap_or_default();
        let combined = cell
            .combined_log_weight
            .map(|value| format!("{value:.17e}"))
            .unwrap_or_default();
        let arrival_ess = cell
            .recoveries
            .iter()
            .find(|recovery| recovery.is_flaperon)
            .map(|recovery| recovery.effective_sample_size)
            .unwrap_or(0.0);
        let isotope_counts = cell
            .isotope
            .as_ref()
            .map(|evaluation| {
                (
                    evaluation.compatible_paths,
                    evaluation.marginal_paths,
                    evaluation.rejected_paths,
                    evaluation.missing_coverage_paths,
                )
            })
            .unwrap_or((0, 0, 0, 0));
        let minimum_recovery_ess = cell
            .recoveries
            .iter()
            .map(|recovery| recovery.effective_sample_size)
            .fold(f64::INFINITY, f64::min);
        let minimum_recovery_ess = if minimum_recovery_ess.is_finite() {
            minimum_recovery_ess
        } else {
            0.0
        };
        let non_recovery_landfall = cell
            .non_recoveries
            .iter()
            .map(|observation| observation.estimated_landfall_probability)
            .sum::<f64>();
        let non_recovery_unresolved = cell
            .non_recoveries
            .iter()
            .map(|observation| observation.unresolved_path_probability)
            .sum::<f64>();
        let non_recovery_log = cell
            .non_recoveries
            .iter()
            .map(|observation| observation.log_compatibility)
            .sum::<f64>();
        output.push_str(&format!(
            "{},{:.12},{:.12},{:.17e},{:.17e},{},{},{:.17e},{:.9},{:.9},{:?},{:.9},{:.9},{:.9},{:.9},{:.9},{},{},{},{},{:.9},{:.9}\n",
            cell.id,
            cell.position.latitude.0,
            cell.position.longitude.0,
            cell.prior_weight,
            cell.debris_log_compatibility,
            isotope,
            combined,
            cell.normalized_weight,
            cell.terminated_fraction,
            cell.proposal_terminated_fraction,
            cell.status,
            arrival_ess,
            minimum_recovery_ess,
            non_recovery_landfall,
            non_recovery_unresolved,
            non_recovery_log,
            isotope_counts.0,
            isotope_counts.1,
            isotope_counts.2,
            isotope_counts.3,
            cell.sampling.correction_weight_effective_sample_size,
            cell.sampling.mean_correction_weight,
        ));
    }
    output.into_bytes()
}

fn coast_evidence_condition(
    coast_configured: bool,
    coast_metadata: Option<&Value>,
) -> &'static str {
    if !coast_configured {
        "coastal interaction disabled; no land or beaching field was supplied"
    } else if coast_metadata
        .and_then(|metadata| metadata.pointer("/component_units/beaching_rate"))
        .is_some()
    {
        "explicit land fraction and supplied beaching-rate field enabled"
    } else {
        "explicit land mask enabled; coastal beaching disabled because no beaching-rate field was supplied"
    }
}

fn report_document(
    config: &OceanDriftRunConfig,
    motion_families: &[DebrisMotionFamily],
    result: &SourceAreaResult,
    current_metadata: &Value,
    coast_metadata: Option<&Value>,
) -> Result<ReportDocument> {
    let peak = result
        .cells
        .iter()
        .find(|cell| cell.id == result.peak_cell_id)
        .context("peak source cell is absent")?;
    let points = result
        .cells
        .iter()
        .filter(|cell| cell.normalized_weight > 0.0)
        .map(|cell| ReportPoint {
            latitude_deg: cell.position.latitude.0,
            longitude_deg: cell.position.longitude.0,
            weight: cell.normalized_weight,
        })
        .collect::<Vec<_>>();
    let mut diagnostics = peak
        .recoveries
        .iter()
        .map(|recovery| DiagnosticPoint {
            label: recovery.event_id.clone(),
            effective_sample_size: recovery.effective_sample_size,
            log_evidence_increment: recovery.log_compatibility,
        })
        .collect::<Vec<_>>();
    if let Some(isotope) = &peak.isotope {
        diagnostics.push(DiagnosticPoint {
            label: "A2-G1 compatibility screen".to_string(),
            effective_sample_size: isotope.screened_arrival_effective_sample_size,
            log_evidence_increment: isotope.conditional_log_compatibility,
        });
    }
    diagnostics.extend(
        peak.non_recoveries
            .iter()
            .map(|observation| DiagnosticPoint {
                label: observation.observation_id.clone(),
                effective_sample_size: observation.effective_sample_size,
                log_evidence_increment: observation.log_compatibility,
            }),
    );
    let enabled = if config.isotope.is_some() {
        "enabled as a neutral-or-penalizing screen conditional on represented flaperon arrival"
    } else {
        "disabled"
    };
    let windage = motion_families
        .iter()
        .filter(|family| {
            family.motion.windage_fraction > 0.0 || family.motion.windage_speed_m_per_s > 0.0
        })
        .map(|family| {
            format!(
                "{}={:.3}% + {:.3} m/s at {:.1} degrees",
                family.id,
                100.0 * family.motion.windage_fraction,
                family.motion.windage_speed_m_per_s,
                family.motion.windage_angle_degrees
            )
        })
        .collect::<Vec<_>>();
    let wind = if windage.is_empty() {
        "direct windage disabled in every object-motion family".to_string()
    } else {
        format!("distinct direct 10 m windage: {}", windage.join(", "))
    };
    let stokes = if let Some(input) = &config.stokes {
        let responses = motion_families
            .iter()
            .map(|family| {
                format!(
                    "{}={:.0}%",
                    family.id,
                    100.0 * family.motion.stokes_velocity_scale
                )
            })
            .collect::<Vec<_>>()
            .join(", ");
        format!(
            "distinct Stokes velocity field enabled; responses {responses}; finite coastal corners renormalized={}",
            input.renormalize_finite_spatial_corners,
        )
    } else {
        "Stokes drift omitted".to_string()
    };
    let current_corners = format!(
        "Current persistent-land corners renormalized={}; intermittent missing values remain fatal",
        config.currents.renormalize_finite_spatial_corners
    );
    let coast = coast_evidence_condition(config.coast.is_some(), coast_metadata);
    let time_support = config.currents.maximum_interpolation_gap_hours.map_or_else(
        || "No additional current interpolation-gap cutoff configured".to_string(),
        |hours| {
            format!(
                "Current interpolation across timestamp gaps greater than {hours:.1} h is outside-time support"
            )
        },
    );
    let isotope_counts = peak.isotope.as_ref().map(|evaluation| {
        format!(
            "compatible={} marginal={} rejected={} missing_SST={}",
            evaluation.compatible_paths,
            evaluation.marginal_paths,
            evaluation.rejected_paths,
            evaluation.missing_coverage_paths,
        )
    });
    let isotope_sensitivities = config.isotope.as_ref().map(|isotope| {
        format!(
            "Isotope sensitivities: seawater SD={:.2}‰, calibration SD={:.2}°C, residual SD={:.2}°C correlated over {:.1} d, SST SD={:.2}°C, shell smoothing={:.1} d, compatible/rejection simultaneous confidence={:.3}/{:.3}, maximum marginal/rejection penalties={:.3}/{:.3} log units",
            isotope.seawater_delta18o_sd_per_mil,
            isotope.calibration_sd_c,
            isotope.residual_sd_c,
            isotope.correlation_days,
            isotope.sst_field_sd_c,
            isotope.shell_smoothing_days,
            isotope.compatible_simultaneous_confidence,
            isotope.rejection_simultaneous_confidence,
            isotope.maximum_marginal_log_penalty,
            isotope.maximum_rejection_log_penalty,
        )
    });
    let recovery_object_count = motion_families
        .iter()
        .flat_map(|family| &family.debris.events)
        .map(|event| event.object_ids.len().max(1))
        .sum::<usize>();
    let recovery_episode_ids = motion_families
        .iter()
        .flat_map(|family| family.debris.events.iter().map(|event| event.id.as_str()))
        .collect::<BTreeSet<_>>();
    let recovery_episode_count = recovery_episode_ids.len();
    let configured_recovery_entries = motion_families
        .iter()
        .map(|family| family.debris.events.len())
        .sum::<usize>();
    let configured_non_recovery_populations = motion_families
        .iter()
        .filter(|family| family.debris.events.is_empty())
        .count();
    let configured_transport_ensembles =
        configured_recovery_entries + configured_non_recovery_populations;
    let non_recovery_conditions = motion_families
        .iter()
        .flat_map(|family| {
            family.debris.non_recoveries.iter().map(move |observation| {
                format!(
                    "{} / {}: zero reports with explicit Poisson exposure {:.3}",
                    family.id, observation.id, observation.expected_reportable_items
                )
            })
        })
        .collect::<Vec<_>>();
    let peak_family_diagnostics = peak
        .motion_families
        .iter()
        .map(|family| {
            let minimum_arrival_ess = family
                .recoveries
                .iter()
                .map(|recovery| recovery.effective_sample_size)
                .fold(f64::INFINITY, f64::min);
            let minimum_correction_ess = family
                .recovery_ensembles
                .iter()
                .map(|ensemble| ensemble.sampling.correction_weight_effective_sample_size)
                .fold(f64::INFINITY, f64::min);
            format!(
                "Peak {}: terminated={:.1}% (proposal {:.1}%), minimum recovery ESS={:.1}, correction ESS={:.1}",
                family.id,
                100.0 * family.terminated_fraction,
                100.0 * family.proposal_terminated_fraction,
                if minimum_arrival_ess.is_finite() {
                    minimum_arrival_ess
                } else {
                    0.0
                },
                if minimum_correction_ess.is_finite() {
                    minimum_correction_ess
                } else {
                    family.sampling.correction_weight_effective_sample_size
                },
            )
        })
        .collect::<Vec<_>>();
    let mut limitations = vec![
        "Diagnostic source-compatibility result, not a calibrated final MH370 posterior."
            .to_string(),
        "Current families are reported separately and are never averaged using subjective weights."
            .to_string(),
        "A2-G1 covers only the final months; the screen is neutral for any compatible chronology and never density-ranks compatible paths."
            .to_string(),
        "No field-unavailable trajectory is relabelled as beaching; termination fractions and reasons remain in the JSON artifact."
            .to_string(),
    ];
    if configured_recovery_entries > recovery_episode_count {
        limitations.push(
            "A recovery episode represented under more than one defensible object-motion law is counted once using its least-suppressive compatibility; no subjective motion-family mixture weight is introduced."
                .to_string(),
        );
    }
    limitations.extend(metadata_limitations(current_metadata));
    if let Some(metadata) = coast_metadata {
        limitations.extend(metadata_limitations(metadata));
    }
    Ok(ReportDocument {
        title: config.name.clone(),
        subtitle: format!(
            "Uncalibrated family-specific diagnostic; currents={} | isotope={enabled}",
            config.family
        ),
        summary: vec![
            ("Current family".to_string(), config.family.clone()),
            ("Peak source cell".to_string(), result.peak_cell_id.clone()),
            (
                "Peak position".to_string(),
                format!(
                    "{:.3}°, {:.3}°",
                    result.peak_position.latitude.0, result.peak_position.longitude.0
                ),
            ),
            (
                "Weighted trajectories".to_string(),
                format!(
                    "{} × {} cells × {} transport ensembles ({} event-targeted recovery; {} independent non-recovery population) in {} object-motion families",
                    config.particles_per_cell,
                    result.cells.len(),
                    configured_transport_ensembles,
                    configured_recovery_entries,
                    configured_non_recovery_populations,
                    motion_families.len()
                ),
            ),
            (
                "Recovery evidence".to_string(),
                format!("{recovery_object_count} objects in {recovery_episode_count} independent episodes"),
            ),
            (
                "Mean importance-weighted field-termination fraction".to_string(),
                format!("{:.1}%", 100.0 * result.mean_terminated_fraction),
            ),
            (
                "Mean proposal termination fraction".to_string(),
                format!(
                    "{:.1}%",
                    100.0 * result.mean_proposal_terminated_fraction
                ),
            ),
            (
                "Arrival sampler".to_string(),
                format!("{:?}", config.sampling.method),
            ),
            (
                "Peak correction ESS".to_string(),
                format!("{:.1}", peak.sampling.correction_weight_effective_sample_size),
            ),
        ],
        points,
        diagnostics,
        evidence_conditions: vec![
            format!("Current family selected explicitly: {}", config.family),
            format!(
                "Object-motion families selected explicitly: {}",
                motion_families
                    .iter()
                    .map(|family| family.id.as_str())
                    .collect::<Vec<_>>()
                    .join(", ")
            ),
            current_corners,
            format!("Barnacle isotope: {enabled}"),
            wind,
            stokes,
            coast.to_string(),
            time_support,
            isotope_counts.unwrap_or_else(|| "isotope screen disabled".to_string()),
            isotope_sensitivities
                .unwrap_or_else(|| "isotope sensitivity parameters not applicable".to_string()),
            "Recovery dates are discovery intervals; each event's explicit delay distribution separates discovery from modeled coastal arrival.".to_string(),
        ]
        .into_iter()
        .chain(non_recovery_conditions)
        .chain(peak_family_diagnostics)
        .collect(),
        limitations,
        map_context: config.map_context.clone(),
    })
}

fn metadata_limitations(metadata: &Value) -> Vec<String> {
    metadata
        .get("limitations")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(Value::as_str)
        .map(str::to_string)
        .collect()
}

fn maximum_resident_set_kib() -> Option<u64> {
    let status = fs::read_to_string("/proc/self/status").ok()?;
    status.lines().find_map(|line| {
        let value = line.strip_prefix("VmHWM:")?.trim();
        value.strip_suffix(" kB")?.trim().parse().ok()
    })
}

pub fn estimate(config_path: &Path, output: &Path) -> Result<()> {
    prepare_output(output)?;
    let started = Instant::now();
    let config_bytes =
        fs::read(config_path).with_context(|| format!("cannot read {}", config_path.display()))?;
    let config: OceanDriftRunConfig = toml::from_str(
        std::str::from_utf8(&config_bytes).context("ocean-drift config is not UTF-8")?,
    )
    .context("cannot parse ocean-drift TOML")?;
    if !matches!(config.schema_version, 2 | 3)
        || config.name.trim().is_empty()
        || config.family.trim().is_empty()
        || config.particles_per_cell == 0
    {
        bail!("ocean-drift configuration is incomplete or uses an unsupported schema");
    }
    let motion_families = resolved_motion_families(&config)?;
    if motion_families.iter().any(|family| {
        family.motion.windage_fraction > 0.0 || family.motion.windage_speed_m_per_s > 0.0
    }) && config.wind.is_none()
    {
        bail!("nonzero windage requires an explicit wind field");
    }
    let currents = load_field(config_path, &config.currents, "currents")?;
    let metadata_family = currents
        .metadata
        .get("family")
        .and_then(Value::as_str)
        .context("current-field metadata lacks family")?;
    if metadata_family != config.family {
        bail!("configured family does not match current-field metadata");
    }
    let wind = config
        .wind
        .as_ref()
        .map(|input| load_field(config_path, input, "10 m wind"))
        .transpose()?;
    let stokes = config
        .stokes
        .as_ref()
        .map(|input| load_field(config_path, input, "Stokes drift"))
        .transpose()?;
    let coast = config
        .coast
        .as_ref()
        .map(|input| load_field(config_path, input, "coastal interaction"))
        .transpose()?;
    let source_cell_path = resolve(config_path, &config.source_cells);
    let source_file: SourceCellFile = read_json(&source_cell_path, "source-cell file")?;
    if source_file.schema != "mh370-ocean-source-cells-v1" {
        bail!("unsupported source-cell schema");
    }

    let mut isotope_records_path = None;
    let mut sst_loaded = None;
    let isotope_model = if let Some(isotope) = &config.isotope {
        let records_path = resolve(config_path, &isotope.records);
        let records: IsotopeRecordFile = read_json(&records_path, "isotope record")?;
        if records.schema != "mh370-a2-g1-isotope-v1"
            || records.record_count != 49
            || records.records.len() != 49
            || records.terminal_anchor != "2015-07-29"
            || records.records.first().map(|record| record.growth_fraction) != Some(0.0)
            || records.records.last().map(|record| record.growth_fraction) != Some(1.0)
        {
            bail!("canonical A2-G1 input must contain 49 records spanning growth fractions 0 to 1 and anchored to 2015-07-29");
        }
        isotope_records_path = Some(records_path);
        sst_loaded = Some(load_field(config_path, &isotope.sst, "OISST")?);
        Some(BarnacleIsotopeModel {
            records: records.records,
            chronologies: isotope.chronologies.clone(),
            seawater_delta18o_per_mil: isotope.seawater_delta18o_per_mil,
            seawater_delta18o_sd_per_mil: isotope.seawater_delta18o_sd_per_mil,
            calibration_sd_c: isotope.calibration_sd_c,
            residual_sd_c: isotope.residual_sd_c,
            sst_field_sd_c: isotope.sst_field_sd_c,
            shell_smoothing_days: isotope.shell_smoothing_days,
            correlation_days: isotope.correlation_days,
            compatible_simultaneous_confidence: isotope.compatible_simultaneous_confidence,
            rejection_simultaneous_confidence: isotope.rejection_simultaneous_confidence,
            maximum_marginal_log_penalty: isotope.maximum_marginal_log_penalty,
            maximum_rejection_log_penalty: isotope.maximum_rejection_log_penalty,
        })
    } else {
        None
    };

    let simulation = SourceAreaConfig {
        family: config.family.clone(),
        seed: config.seed,
        particles_per_cell: config.particles_per_cell,
        release_unix_seconds: config.release_unix_seconds,
        sampling: config.sampling,
        motion_families: motion_families.clone(),
        isotope: isotope_model,
    };
    let result = evaluate_source_area(
        &simulation,
        &source_file.cells,
        DriftEnvironment {
            currents: &currents.field,
            wind: wind.as_ref().map(|loaded| &loaded.field),
            stokes: stokes.as_ref().map(|loaded| &loaded.field),
            coast: coast.as_ref().map(|loaded| &loaded.field),
        },
        sst_loaded.as_ref().map(|loaded| &loaded.field),
    )?;

    let result_path = output.join("source-area.json");
    let csv_path = output.join("source-area.csv");
    let pdf_path = output.join("source-area.pdf");
    let svg_path = output.join("source-area.svg");
    let png_path = output.join("source-area.png");
    write_json(&result_path, &result)?;
    atomic_write(&csv_path, &source_csv(&result))?;
    let report = report_document(
        &config,
        &motion_families,
        &result,
        &currents.metadata,
        coast.as_ref().map(|field| &field.metadata),
    )?;
    atomic_write(&pdf_path, &build_pdf(&report)?)?;
    atomic_write(&svg_path, &build_posterior_svg(&report)?)?;
    atomic_write(&png_path, &build_accident_panel_png(&report)?)?;

    let mut input_sha256 = BTreeMap::new();
    let mut input_metadata = BTreeMap::new();
    let mut limitations = metadata_limitations(&currents.metadata);
    for (label, field) in [
        ("currents", Some(&currents)),
        ("wind", wind.as_ref()),
        ("stokes", stokes.as_ref()),
        ("coast", coast.as_ref()),
        ("sst", sst_loaded.as_ref()),
    ] {
        if let Some(field) = field {
            input_sha256.insert(format!("{label}.binary"), field.binary_sha256.clone());
            input_sha256.insert(format!("{label}.metadata"), field.metadata_sha256.clone());
            input_metadata.insert(label.to_string(), field.metadata.clone());
            if label != "currents" {
                limitations.extend(metadata_limitations(&field.metadata));
            }
        }
    }
    input_sha256.insert("source_cells".to_string(), sha256_file(&source_cell_path)?);
    if let Some(path) = isotope_records_path {
        input_sha256.insert("isotope_records".to_string(), sha256_file(&path)?);
    }
    limitations.push(
        "Discovery is not beaching; configured discovery-delay distributions are explicit model choices.".to_string(),
    );
    limitations.push("The Gaussian spatial encounter kernel and midpoint integrator are explicit model choices, not published measurements.".to_string());

    let mut outputs = BTreeMap::new();
    for path in [&result_path, &csv_path, &pdf_path, &svg_path, &png_path] {
        let name = path
            .file_name()
            .and_then(|value| value.to_str())
            .context("invalid output filename")?;
        outputs.insert(name.to_string(), sha256_file(path)?);
    }
    let manifest = OceanRunManifest {
        schema_version: 3,
        engine_version: env!("CARGO_PKG_VERSION"),
        executable_sha256: executable_sha256()?,
        command: "estimate-ocean-drift",
        config_path: config_path.display().to_string(),
        config_sha256: sha256_bytes(&config_bytes),
        family: config.family.clone(),
        isotope_enabled: config.isotope.is_some(),
        seed: config.seed,
        particles_per_cell: config.particles_per_cell,
        sampling: config.sampling,
        coast_enabled: config.coast.is_some(),
        current_maximum_interpolation_gap_hours: config.currents.maximum_interpolation_gap_hours,
        current_renormalizes_persistent_land_corners: config
            .currents
            .renormalize_finite_spatial_corners,
        motion_family_ids: motion_families
            .iter()
            .map(|family| family.id.clone())
            .collect(),
        stokes_velocity_scales: motion_families
            .iter()
            .map(|family| (family.id.clone(), family.motion.stokes_velocity_scale))
            .collect(),
        stokes_renormalizes_finite_spatial_corners: config
            .stokes
            .as_ref()
            .is_some_and(|input| input.renormalize_finite_spatial_corners),
        input_sha256,
        input_metadata,
        outputs,
        limitations,
    };
    write_json(&output.join("run-manifest.json"), &manifest)?;
    let receipt = RuntimeReceipt {
        schema_version: 3,
        unix_time_s: SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .context("system clock predates Unix epoch")?
            .as_secs(),
        elapsed_seconds: started.elapsed().as_secs_f64(),
        source_cells: result.cells.len(),
        simulated_paths: result.cells.len()
            * result.particles_per_cell
            * motion_families
                .iter()
                .map(|family| family.debris.events.len().max(1))
                .sum::<usize>(),
        propagated_segments: result
            .cells
            .iter()
            .flat_map(|cell| &cell.motion_families)
            .map(|family| {
                if family.recovery_ensembles.is_empty() {
                    family.sampling.propagated_segments
                } else {
                    family
                        .recovery_ensembles
                        .iter()
                        .map(|ensemble| ensemble.sampling.propagated_segments)
                        .sum()
                }
            })
            .sum(),
        peak_memory_kib: maximum_resident_set_kib(),
    };
    write_json(&output.join("runtime-receipt.json"), &receipt)?;
    println!(
        "status=diagnostic family={} isotope={} sampler={:?} peak={} cells={} paths={} elapsed_s={:.3} png={} pdf={}",
        result.family,
        result.isotope_enabled,
        config.sampling.method,
        result.peak_cell_id,
        result.cells.len(),
        receipt.simulated_paths,
        receipt.elapsed_seconds,
        png_path.display(),
        pdf_path.display(),
    );
    Ok(())
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::coast_evidence_condition;

    #[test]
    fn coast_report_never_invents_beaching_from_a_land_mask() {
        let land_only = json!({
            "component_units": {"land_fraction": "binary fraction"}
        });
        let with_beaching = json!({
            "component_units": {
                "land_fraction": "binary fraction",
                "beaching_rate": "per day"
            }
        });

        assert!(coast_evidence_condition(false, None).contains("disabled"));
        assert!(coast_evidence_condition(true, Some(&land_only)).contains("beaching disabled"));
        assert!(
            coast_evidence_condition(true, Some(&with_beaching)).contains("supplied beaching-rate")
        );
    }
}
