use std::{
    collections::{BTreeMap, BTreeSet},
    fs::{self, OpenOptions},
    io::Write,
    path::{Path, PathBuf},
};

use anyhow::{bail, Context, Result};
use mh370_domain::{great_circle_distance_nm, LatLon};
use mh370_reporting::{
    build_accident_panel_png, build_pdf, build_posterior_svg, ReportDocument, ReportMapBounds,
    ReportMapContext, ReportMapRoute, ReportPoint,
};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

use crate::impact_handoff::{ImpactParticleIdentityV1, ImpactPosteriorHandoffV1};

const SCHEMA_VERSION: u32 = 1;
const APPLICATION_STATUS: &str = "provisional_conditional_sensitivity";
const SUPPORT_POLICY: &str = "condition_on_native_support";

#[derive(Debug, Deserialize)]
struct Configuration {
    schema_version: u32,
    name: String,
    code_revision: String,
    parent_impact_handoffs: Vec<PathBuf>,
    branch_id: String,
    relative_likelihood_floor: f64,
    maximum_source_time_offset_s: f64,
    model: ModelConfiguration,
}

#[derive(Debug, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
enum ModelConfiguration {
    Pleiades {
        grid: PathBuf,
        surfaces: PathBuf,
        manifest: PathBuf,
        surface_id: String,
        source_time_unix_s: f64,
        maximum_nearest_node_distance_nm: f64,
    },
    OceanDrift {
        handoff: PathBuf,
        family_id: String,
        source_time_unix_s: f64,
        maximum_nearest_cell_distance_nm: f64,
        allow_diagnostic_family: bool,
    },
}

#[derive(Debug, Clone)]
struct SurfaceNode {
    id: String,
    position: LatLon,
    log_relative_likelihood: Option<f64>,
    source_status: String,
}

#[derive(Debug)]
struct Surface {
    family_id: String,
    family_label: String,
    family_admitted: bool,
    source_time_unix_s: f64,
    maximum_nearest_distance_nm: f64,
    boundary: Option<Vec<[f64; 2]>>,
    arc_coordinates_deg: Vec<[f64; 2]>,
    nodes: Vec<SurfaceNode>,
    limitations: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct OceanHandoff {
    schema: String,
    families: Vec<OceanFamily>,
}

#[derive(Debug, Deserialize)]
struct OceanFamily {
    id: String,
    label: String,
    decision: String,
    admitted: bool,
    #[serde(default)]
    failed_checks: Vec<String>,
    #[serde(default)]
    limitations: Vec<String>,
    cells: Vec<OceanCell>,
}

#[derive(Debug, Deserialize)]
struct OceanCell {
    id: String,
    latitude_deg: f64,
    longitude_deg: f64,
    relative_log_likelihood: f64,
    status: String,
}

#[derive(Debug, Clone, Serialize)]
struct PositionSummary {
    latitude_deg: f64,
    longitude_deg: f64,
}

#[derive(Debug, Clone, Serialize)]
struct BranchParticle {
    identity: ImpactParticleIdentityV1,
    latitude_deg: f64,
    longitude_deg: f64,
    impact_time_unix_s: f64,
    baseline_weight: f64,
    conditional_weight: f64,
    relative_log_likelihood: Option<f64>,
    nearest_surface_distance_nm: Option<f64>,
    surface_cell_id: Option<String>,
    source_cell_status: Option<String>,
    support_status: &'static str,
    used_likelihood_floor: bool,
}

#[derive(Debug, Serialize)]
struct ConditionalSpatialResult {
    schema_id: &'static str,
    schema_version: u32,
    name: String,
    branch_id: String,
    application_status: &'static str,
    central_posterior_updated: bool,
    support_policy: &'static str,
    parent_impact_handoff_sha256: Vec<String>,
    numerical_seed_count: usize,
    family_id: String,
    family_label: String,
    family_admitted: bool,
    relative_likelihood_floor: f64,
    source_time_unix_s: f64,
    seventh_arc_coordinates_deg: Vec<[f64; 2]>,
    impact_time_offset_range_s: [f64; 2],
    particles: usize,
    supported_particles: usize,
    unsupported_particles: usize,
    floored_particles: usize,
    supported_baseline_mass: f64,
    relative_score_log_normalizer: f64,
    baseline_effective_sample_size: f64,
    conditional_effective_sample_size: f64,
    baseline_mean: PositionSummary,
    conditional_mean: PositionSummary,
    mean_shift_nm: f64,
    limitations: Vec<String>,
    particle_values: Vec<BranchParticle>,
}

#[derive(Debug, Serialize)]
struct RunManifest {
    schema_version: u32,
    command: &'static str,
    producer_executable_sha256: String,
    code_revision: String,
    config_sha256: String,
    input_sha256: BTreeMap<String, String>,
    output_sha256: BTreeMap<String, String>,
    reproduction_command: String,
    scientific_scope: Vec<String>,
}

#[derive(Debug)]
struct GridRow {
    id: String,
    along_index: usize,
    cross_index: usize,
    position: LatLon,
}

fn resolve(configuration: &Path, value: &Path) -> PathBuf {
    if value.is_absolute() {
        value.to_path_buf()
    } else {
        configuration
            .parent()
            .unwrap_or_else(|| Path::new("."))
            .join(value)
    }
}

fn sha256_bytes(bytes: &[u8]) -> String {
    hex::encode(Sha256::digest(bytes))
}

fn read_hashed(path: &Path, label: &str, hashes: &mut BTreeMap<String, String>) -> Result<Vec<u8>> {
    let bytes =
        fs::read(path).with_context(|| format!("cannot read {label} {}", path.display()))?;
    hashes.insert(label.to_string(), sha256_bytes(&bytes));
    Ok(bytes)
}

fn parse_fields(line: &str, expected: usize) -> Result<Vec<&str>> {
    let fields = line.trim_end_matches('\r').split(',').collect::<Vec<_>>();
    if fields.len() != expected {
        bail!("CSV row has {} fields; expected {expected}", fields.len());
    }
    Ok(fields)
}

fn parse_grid(bytes: &[u8]) -> Result<Vec<GridRow>> {
    let text = std::str::from_utf8(bytes).context("Pleiades grid is not UTF-8")?;
    let mut lines = text.lines();
    let header = lines.next().context("Pleiades grid is empty")?;
    if header
        != "schema_version,grid_id,cell_id,along_index,cross_index,along_nm,cross_nm,latitude_deg,longitude_deg,quadrature_area_km2,trapezoidal_weight"
    {
        bail!("unexpected Pleiades grid header");
    }
    let mut rows = Vec::new();
    let mut ids = BTreeSet::new();
    for line in lines.filter(|line| !line.trim().is_empty()) {
        let fields = parse_fields(line, 11)?;
        if fields[0] != "pleiades-conditional-source-surface/1.0.0" {
            bail!("unexpected Pleiades row schema");
        }
        let id = fields[2].to_string();
        if !ids.insert(id.clone()) {
            bail!("duplicate Pleiades grid cell {id}");
        }
        rows.push(GridRow {
            id,
            along_index: fields[3].parse().context("invalid along index")?,
            cross_index: fields[4].parse().context("invalid cross index")?,
            position: LatLon::new(
                fields[7].parse().context("invalid grid latitude")?,
                fields[8].parse().context("invalid grid longitude")?,
            )?,
        });
    }
    if rows.is_empty() {
        bail!("Pleiades grid has no rows");
    }
    Ok(rows)
}

fn parse_surface_values(bytes: &[u8], surface_id: &str) -> Result<BTreeMap<String, Option<f64>>> {
    let text = std::str::from_utf8(bytes).context("Pleiades surfaces are not UTF-8")?;
    let mut lines = text.lines();
    let header = lines.next().context("Pleiades surfaces are empty")?;
    if header
        != "schema_version,surface_id,cell_id,relative_likelihood,log_relative_likelihood,normalized_density_per_km2,normalized_probability_mass"
    {
        bail!("unexpected Pleiades surface header");
    }
    let mut values = BTreeMap::new();
    for line in lines.filter(|line| !line.trim().is_empty()) {
        let fields = parse_fields(line, 7)?;
        if fields[1] != surface_id {
            continue;
        }
        let log_value = if fields[4].is_empty() {
            None
        } else {
            let value = fields[4]
                .parse::<f64>()
                .context("invalid log-relative Pleiades value")?;
            if !value.is_finite() || value > 1.0e-12 {
                bail!("Pleiades log-relative likelihood is invalid");
            }
            Some(value)
        };
        if values.insert(fields[2].to_string(), log_value).is_some() {
            bail!("duplicate Pleiades surface cell {}", fields[2]);
        }
    }
    if values.is_empty() {
        bail!("selected Pleiades surface is absent");
    }
    Ok(values)
}

fn boundary(rows: &[GridRow]) -> Result<Vec<[f64; 2]>> {
    let maximum_along = rows
        .iter()
        .map(|row| row.along_index)
        .max()
        .context("Pleiades grid has no along extent")?;
    let maximum_cross = rows
        .iter()
        .map(|row| row.cross_index)
        .max()
        .context("Pleiades grid has no cross extent")?;
    let positions = rows
        .iter()
        .map(|row| ((row.along_index, row.cross_index), row.position))
        .collect::<BTreeMap<_, _>>();
    let mut polygon = Vec::new();
    for cross in 0..=maximum_cross {
        polygon.push(to_lon_lat(
            *positions
                .get(&(0, cross))
                .context("grid boundary is incomplete")?,
        ));
    }
    for along in 1..=maximum_along {
        polygon.push(to_lon_lat(
            *positions
                .get(&(along, maximum_cross))
                .context("grid boundary is incomplete")?,
        ));
    }
    for cross in (0..maximum_cross).rev() {
        polygon.push(to_lon_lat(
            *positions
                .get(&(maximum_along, cross))
                .context("grid boundary is incomplete")?,
        ));
    }
    for along in (1..maximum_along).rev() {
        polygon.push(to_lon_lat(
            *positions
                .get(&(along, 0))
                .context("grid boundary is incomplete")?,
        ));
    }
    Ok(polygon)
}

fn to_lon_lat(position: LatLon) -> [f64; 2] {
    [position.longitude.0, position.latitude.0]
}

fn point_in_polygon(position: LatLon, polygon: &[[f64; 2]]) -> bool {
    let x = position.longitude.0;
    let y = position.latitude.0;
    let mut inside = false;
    let mut previous = polygon.len() - 1;
    for current in 0..polygon.len() {
        let [xi, yi] = polygon[current];
        let [xj, yj] = polygon[previous];
        let cross = (x - xj) * (yi - yj) - (y - yj) * (xi - xj);
        let on_segment = cross.abs() <= 1.0e-10
            && x >= xj.min(xi) - 1.0e-10
            && x <= xj.max(xi) + 1.0e-10
            && y >= yj.min(yi) - 1.0e-10
            && y <= yj.max(yi) + 1.0e-10;
        if on_segment {
            return true;
        }
        if ((yi > y) != (yj > y)) && x < (xj - xi) * (y - yi) / (yj - yi) + xi {
            inside = !inside;
        }
        previous = current;
    }
    inside
}

fn load_pleiades(
    configuration_path: &Path,
    grid_path: &Path,
    surfaces_path: &Path,
    manifest_path: &Path,
    surface_id: &str,
    source_time_unix_s: f64,
    maximum_nearest_node_distance_nm: f64,
    hashes: &mut BTreeMap<String, String>,
) -> Result<Surface> {
    if !source_time_unix_s.is_finite()
        || source_time_unix_s <= 0.0
        || !maximum_nearest_node_distance_nm.is_finite()
        || maximum_nearest_node_distance_nm <= 0.0
        || maximum_nearest_node_distance_nm > 5.0
    {
        bail!("invalid Pleiades source time or nearest-node distance");
    }
    let grid_path = resolve(configuration_path, grid_path);
    let surfaces_path = resolve(configuration_path, surfaces_path);
    let manifest_path = resolve(configuration_path, manifest_path);
    let grid_bytes = read_hashed(&grid_path, "pleiades_grid", hashes)?;
    let surface_bytes = read_hashed(&surfaces_path, "pleiades_surfaces", hashes)?;
    let manifest_bytes = read_hashed(&manifest_path, "pleiades_manifest", hashes)?;
    let manifest: serde_json::Value = serde_json::from_slice(&manifest_bytes)
        .context("cannot parse Pleiades handoff manifest")?;
    if manifest["schema_id"] != "pleiades-conditional-source-surface/1.0.0"
        || manifest["handoff_status"] != "source_only_conditional_proxy_handoff"
    {
        bail!("Pleiades manifest is not the supported conditional proxy handoff");
    }
    let manifest_surface = manifest["surfaces"]
        .as_array()
        .and_then(|surfaces| {
            surfaces
                .iter()
                .find(|surface| surface["surface_id"].as_str() == Some(surface_id))
        })
        .context("selected Pleiades surface is absent from its manifest")?;
    let family_label = manifest_surface["label"]
        .as_str()
        .context("selected Pleiades surface has no label")?
        .to_string();
    let expected_grid_hash = manifest["artifacts"]
        .as_array()
        .and_then(|artifacts| {
            artifacts
                .iter()
                .find(|artifact| artifact["path"].as_str() == Some("grid.csv"))
        })
        .and_then(|artifact| artifact["sha256"].as_str())
        .context("Pleiades grid hash is absent from manifest")?;
    let expected_surface_hash = manifest["artifacts"]
        .as_array()
        .and_then(|artifacts| {
            artifacts
                .iter()
                .find(|artifact| artifact["path"].as_str() == Some("surfaces.csv"))
        })
        .and_then(|artifact| artifact["sha256"].as_str())
        .context("Pleiades surface hash is absent from manifest")?;
    if hashes.get("pleiades_grid").map(String::as_str) != Some(expected_grid_hash)
        || hashes.get("pleiades_surfaces").map(String::as_str) != Some(expected_surface_hash)
    {
        bail!("Pleiades grid/surface bytes do not match the selected manifest");
    }

    let rows = parse_grid(&grid_bytes)?;
    let values = parse_surface_values(&surface_bytes, surface_id)?;
    if rows.len() != values.len() {
        bail!("Pleiades grid and selected surface have different cell counts");
    }
    let polygon = boundary(&rows)?;
    let centre_cross = rows
        .iter()
        .map(|row| row.cross_index)
        .max()
        .context("Pleiades grid has no cross-arc extent")?
        / 2;
    let arc_coordinates_deg = rows
        .iter()
        .filter(|row| row.cross_index == centre_cross)
        .map(|row| [row.position.latitude.0, row.position.longitude.0])
        .collect::<Vec<_>>();
    let nodes = rows
        .into_iter()
        .map(|row| {
            let log_relative_likelihood = values
                .get(&row.id)
                .copied()
                .context("Pleiades selected surface is missing a grid cell")?;
            Ok(SurfaceNode {
                id: row.id,
                position: row.position,
                log_relative_likelihood,
                source_status: "grid_node".to_string(),
            })
        })
        .collect::<Result<Vec<_>>>()?;
    Ok(Surface {
        family_id: surface_id.to_string(),
        family_label,
        family_admitted: false,
        source_time_unix_s,
        maximum_nearest_distance_nm: maximum_nearest_node_distance_nm,
        boundary: Some(polygon),
        arc_coordinates_deg,
        nodes,
        limitations: vec![
            "The image-object identity, false-positive process, and image-selection process are uncalibrated; this is a conditional proxy, not core evidence.".to_string(),
            "Alternative Pleiades transport families represent the same image hypothesis and are run separately, never multiplied.".to_string(),
            "Arbitrary impact positions use a declared nearest 5-NM grid-node discretization after an explicit native-boundary check.".to_string(),
        ],
    })
}

fn load_ocean_drift(
    configuration_path: &Path,
    handoff_path: &Path,
    family_id: &str,
    source_time_unix_s: f64,
    maximum_nearest_cell_distance_nm: f64,
    allow_diagnostic_family: bool,
    hashes: &mut BTreeMap<String, String>,
) -> Result<Surface> {
    if !source_time_unix_s.is_finite()
        || source_time_unix_s <= 0.0
        || !maximum_nearest_cell_distance_nm.is_finite()
        || maximum_nearest_cell_distance_nm <= 0.0
        || maximum_nearest_cell_distance_nm > 75.0
    {
        bail!("invalid ocean-drift source time or nearest-cell distance");
    }
    let handoff_path = resolve(configuration_path, handoff_path);
    let bytes = read_hashed(&handoff_path, "ocean_drift_handoff", hashes)?;
    parse_ocean_drift(
        &bytes,
        family_id,
        source_time_unix_s,
        maximum_nearest_cell_distance_nm,
        allow_diagnostic_family,
    )
}

fn parse_ocean_drift(
    bytes: &[u8],
    family_id: &str,
    source_time_unix_s: f64,
    maximum_nearest_cell_distance_nm: f64,
    allow_diagnostic_family: bool,
) -> Result<Surface> {
    let handoff: OceanHandoff =
        serde_json::from_slice(&bytes).context("cannot parse ocean-drift family handoff")?;
    if handoff.schema != "mh370-ocean-drift-family-likelihood-handoff-v1" {
        bail!("unsupported ocean-drift family handoff schema");
    }
    let family = handoff
        .families
        .into_iter()
        .find(|family| family.id == family_id)
        .context("selected ocean-drift family is absent")?;
    if !family.admitted && !allow_diagnostic_family {
        bail!("selected ocean-drift family is diagnostic-only and was not explicitly allowed");
    }
    if family.cells.is_empty() {
        bail!("selected ocean-drift family has no cells");
    }
    let mut ids = BTreeSet::new();
    let mut nodes = Vec::with_capacity(family.cells.len());
    for cell in family.cells {
        if !ids.insert(cell.id.clone())
            || cell.status.trim().is_empty()
            || !cell.relative_log_likelihood.is_finite()
            || cell.relative_log_likelihood > 1.0e-12
        {
            bail!("ocean-drift family contains an invalid source cell");
        }
        nodes.push(SurfaceNode {
            id: cell.id,
            position: LatLon::new(cell.latitude_deg, cell.longitude_deg)?,
            log_relative_likelihood: Some(cell.relative_log_likelihood),
            source_status: cell.status,
        });
    }
    let mut limitations = family.limitations;
    if !family.failed_checks.is_empty() {
        limitations.push(format!(
            "Family decision {} failed: {}.",
            family.decision,
            family.failed_checks.join(", ")
        ));
    }
    limitations.push(
        "This release exposes the source surface only as an explicitly enabled conditional sensitivity; it does not change the central posterior."
            .to_string(),
    );
    Ok(Surface {
        family_id: family.id,
        family_label: family.label,
        family_admitted: family.admitted,
        source_time_unix_s,
        maximum_nearest_distance_nm: maximum_nearest_cell_distance_nm,
        boundary: None,
        arc_coordinates_deg: nodes
            .iter()
            .map(|node| [node.position.latitude.0, node.position.longitude.0])
            .collect(),
        nodes,
        limitations,
    })
}

fn query_surface(surface: &Surface, position: LatLon) -> Option<(&SurfaceNode, f64)> {
    if let Some(boundary) = &surface.boundary {
        if !point_in_polygon(position, boundary) {
            return None;
        }
    }
    let (node, distance_nm) = surface
        .nodes
        .iter()
        .map(|node| (node, great_circle_distance_nm(position, node.position).0))
        .min_by(|first, second| first.1.total_cmp(&second.1))?;
    (distance_nm <= surface.maximum_nearest_distance_nm).then_some((node, distance_nm))
}

fn logsumexp(values: impl Iterator<Item = f64>) -> Option<f64> {
    let values = values.collect::<Vec<_>>();
    let maximum = values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    maximum.is_finite().then(|| {
        maximum
            + values
                .iter()
                .map(|value| (value - maximum).exp())
                .sum::<f64>()
                .ln()
    })
}

fn effective_sample_size(weights: impl Iterator<Item = f64>) -> f64 {
    let weights = weights.collect::<Vec<_>>();
    let total = weights.iter().sum::<f64>();
    let squared = weights.iter().map(|weight| weight * weight).sum::<f64>();
    if squared > 0.0 {
        total * total / squared
    } else {
        0.0
    }
}

fn mean_position<'a>(
    particles: impl Iterator<Item = (&'a BranchParticle, f64)>,
) -> Result<PositionSummary> {
    let particles = particles.collect::<Vec<_>>();
    let total = particles.iter().map(|(_, weight)| weight).sum::<f64>();
    if !total.is_finite() || total <= 0.0 {
        bail!("position summary has zero or invalid weight");
    }
    let latitude_deg = particles
        .iter()
        .map(|(particle, weight)| particle.latitude_deg * weight)
        .sum::<f64>()
        / total;
    let sine = particles
        .iter()
        .map(|(particle, weight)| particle.longitude_deg.to_radians().sin() * weight)
        .sum::<f64>()
        / total;
    let cosine = particles
        .iter()
        .map(|(particle, weight)| particle.longitude_deg.to_radians().cos() * weight)
        .sum::<f64>()
        / total;
    Ok(PositionSummary {
        latitude_deg,
        longitude_deg: sine.atan2(cosine).to_degrees(),
    })
}

fn report_bounds(particles: &[BranchParticle]) -> Result<ReportMapBounds> {
    let longitude_min = particles
        .iter()
        .map(|particle| particle.longitude_deg)
        .fold(f64::INFINITY, f64::min);
    let longitude_max = particles
        .iter()
        .map(|particle| particle.longitude_deg)
        .fold(f64::NEG_INFINITY, f64::max);
    let latitude_min = particles
        .iter()
        .map(|particle| particle.latitude_deg)
        .fold(f64::INFINITY, f64::min);
    let latitude_max = particles
        .iter()
        .map(|particle| particle.latitude_deg)
        .fold(f64::NEG_INFINITY, f64::max);
    if !longitude_min.is_finite()
        || !longitude_max.is_finite()
        || !latitude_min.is_finite()
        || !latitude_max.is_finite()
    {
        bail!("cannot derive report bounds");
    }
    let longitude_margin = ((longitude_max - longitude_min) * 0.08).max(0.25);
    let latitude_margin = ((latitude_max - latitude_min) * 0.08).max(0.25);
    Ok(ReportMapBounds {
        longitude_min_deg: longitude_min - longitude_margin,
        longitude_max_deg: longitude_max + longitude_margin,
        latitude_min_deg: latitude_min - latitude_margin,
        latitude_max_deg: latitude_max + latitude_margin,
    })
}

fn validate_parent_suite(parents: &[(String, ImpactPosteriorHandoffV1)]) -> Result<()> {
    let (_, first) = parents
        .first()
        .context("no parent impact handoffs were supplied")?;
    let first_source = &first.source_runs[0];
    let first_scenario = &first.eof_scenarios[0];
    let mut seeds = BTreeSet::new();
    for (_, parent) in parents {
        let source = &parent.source_runs[0];
        let scenario = &parent.eof_scenarios[0];
        if !seeds.insert(source.seed)
            || parent.run.producer_executable_sha256 != first.run.producer_executable_sha256
            || parent.run.code_revision != first.run.code_revision
            || source.model_family != first_source.model_family
            || source.upstream_config_sha256 != first_source.upstream_config_sha256
            || source.upstream_input_sha256 != first_source.upstream_input_sha256
            || source.relative_time_origin_unix_s_utc
                != first_source.relative_time_origin_unix_s_utc
            || source.source_checkpoint_time_unix_s_utc
                != first_source.source_checkpoint_time_unix_s_utc
            || scenario.id != first_scenario.id
            || scenario.family != first_scenario.family
            || scenario.config_sha256 != first_scenario.config_sha256
            || !compatible_evidence_ledgers(&parent.evidence, &first.evidence)
            || parent.impact_conditioning.conditioned_on != first.impact_conditioning.conditioned_on
        {
            bail!(
                "parent impact handoffs are not distinct numerical seeds of one identical scientific family"
            );
        }
    }
    Ok(())
}

fn compatible_evidence_ledgers(
    first: &crate::impact_handoff::EvidenceLedgerV2,
    second: &crate::impact_handoff::EvidenceLedgerV2,
) -> bool {
    first.entries == second.entries
        && first.applications.len() == second.applications.len()
        && first
            .applications
            .iter()
            .zip(&second.applications)
            .all(|(left, right)| {
                left.id == right.id
                    && left.role == right.role
                    && left.model_family == right.model_family
                    && left.input_sha256 == right.input_sha256
            })
}

fn evaluate(
    configuration: &Configuration,
    parents: Vec<(String, ImpactPosteriorHandoffV1)>,
    surface: Surface,
) -> Result<ConditionalSpatialResult> {
    validate_parent_suite(&parents)?;
    let numerical_seed_count = parents.len();
    let parent_log_pool_weight = -(numerical_seed_count as f64).ln();
    let particle_count = parents
        .iter()
        .map(|(_, parent)| parent.particles.len())
        .sum::<usize>();
    let floor_log = configuration.relative_likelihood_floor.ln();
    let mut raw_log_weights = Vec::with_capacity(particle_count);
    let mut branch_particles = Vec::with_capacity(particle_count);
    let mut supported_baseline_mass = 0.0;
    let mut floored_particles = 0;
    let mut minimum_offset = f64::INFINITY;
    let mut maximum_offset = f64::NEG_INFINITY;

    let parent_sha256 = parents
        .iter()
        .map(|(hash, _)| hash.clone())
        .collect::<Vec<_>>();
    for (_, parent) in parents {
        for particle in parent.particles {
            let baseline_log_weight = particle.normalized_log_weight + parent_log_pool_weight;
            let baseline_weight = baseline_log_weight.exp();
            let position = particle.kinematics.position_wgs84;
            let offset = particle.kinematics.time_utc_unix_s - surface.source_time_unix_s;
            minimum_offset = minimum_offset.min(offset);
            maximum_offset = maximum_offset.max(offset);
            if offset.abs() > configuration.maximum_source_time_offset_s {
                bail!(
                    "impact time differs from fixed surface source time by {:.1} s (limit {:.1} s)",
                    offset.abs(),
                    configuration.maximum_source_time_offset_s
                );
            }
            match query_surface(&surface, position) {
                Some((node, distance_nm)) => {
                    let (log_likelihood, used_floor) = match node.log_relative_likelihood {
                        Some(value) if value >= floor_log => (value, false),
                        _ => (floor_log, true),
                    };
                    supported_baseline_mass += baseline_weight;
                    floored_particles += usize::from(used_floor);
                    raw_log_weights.push(Some(baseline_log_weight + log_likelihood));
                    branch_particles.push(BranchParticle {
                        identity: particle.identity,
                        latitude_deg: position.latitude.0,
                        longitude_deg: position.longitude.0,
                        impact_time_unix_s: particle.kinematics.time_utc_unix_s,
                        baseline_weight,
                        conditional_weight: 0.0,
                        relative_log_likelihood: Some(log_likelihood),
                        nearest_surface_distance_nm: Some(distance_nm),
                        surface_cell_id: Some(node.id.clone()),
                        source_cell_status: Some(node.source_status.clone()),
                        support_status: "supported",
                        used_likelihood_floor: used_floor,
                    });
                }
                None => {
                    raw_log_weights.push(None);
                    branch_particles.push(BranchParticle {
                        identity: particle.identity,
                        latitude_deg: position.latitude.0,
                        longitude_deg: position.longitude.0,
                        impact_time_unix_s: particle.kinematics.time_utc_unix_s,
                        baseline_weight,
                        conditional_weight: 0.0,
                        relative_log_likelihood: None,
                        nearest_surface_distance_nm: None,
                        surface_cell_id: None,
                        source_cell_status: None,
                        support_status: "out_of_support",
                        used_likelihood_floor: false,
                    });
                }
            }
        }
    }
    let log_normalizer = logsumexp(raw_log_weights.iter().filter_map(|value| *value))
        .context("surface gives no finite support to the parent impact posterior")?;
    supported_baseline_mass = supported_baseline_mass.clamp(0.0, 1.0);
    if (1.0 - supported_baseline_mass).abs() <= 1.0e-12 {
        supported_baseline_mass = 1.0;
    }
    for (particle, raw_log_weight) in branch_particles.iter_mut().zip(raw_log_weights) {
        particle.conditional_weight = raw_log_weight
            .map(|value| (value - log_normalizer).exp())
            .unwrap_or(0.0);
    }
    let conditional_total = branch_particles
        .iter()
        .map(|particle| particle.conditional_weight)
        .sum::<f64>();
    if (conditional_total - 1.0).abs() > 1.0e-10
        || !supported_baseline_mass.is_finite()
        || supported_baseline_mass <= 0.0
    {
        bail!("conditional sensitivity weights did not normalize");
    }
    let baseline_mean = mean_position(
        branch_particles
            .iter()
            .map(|particle| (particle, particle.baseline_weight)),
    )?;
    let conditional_mean = mean_position(
        branch_particles
            .iter()
            .map(|particle| (particle, particle.conditional_weight)),
    )?;
    let mean_shift_nm = great_circle_distance_nm(
        LatLon::new(baseline_mean.latitude_deg, baseline_mean.longitude_deg)?,
        LatLon::new(
            conditional_mean.latitude_deg,
            conditional_mean.longitude_deg,
        )?,
    )
    .0;
    let supported_particles = branch_particles
        .iter()
        .filter(|particle| particle.support_status == "supported")
        .count();
    let baseline_effective_sample_size = effective_sample_size(
        branch_particles
            .iter()
            .map(|particle| particle.baseline_weight),
    );
    let conditional_effective_sample_size = effective_sample_size(
        branch_particles
            .iter()
            .map(|particle| particle.conditional_weight),
    );
    let mut limitations = surface.limitations;
    limitations.push(format!(
        "Out-of-support parent mass {:.6} is removed only by the explicit '{}' sensitivity condition; it is not evidence against those particles.",
        1.0 - supported_baseline_mass,
        SUPPORT_POLICY
    ));
    limitations.push(format!(
        "Relative scores are floored at {:.3e}; this is a declared numerical sensitivity and not a physical false-positive calibration.",
        configuration.relative_likelihood_floor
    ));
    limitations.push(
        "This branch is deliberately separate from the parent SATCOM/impact posterior and cannot be stacked with another family representing the same observations."
            .to_string(),
    );
    if conditional_effective_sample_size < 50.0
        || conditional_effective_sample_size < 0.01 * branch_particles.len() as f64
    {
        limitations.push(format!(
            "Conditional ESS {:.2} is too small for a stable narrow contour; interpret location and area only as a particle-resolution sensitivity warning.",
            conditional_effective_sample_size
        ));
    }

    Ok(ConditionalSpatialResult {
        schema_id: "mh370-conditional-spatial-sensitivity",
        schema_version: SCHEMA_VERSION,
        name: configuration.name.clone(),
        branch_id: configuration.branch_id.clone(),
        application_status: APPLICATION_STATUS,
        central_posterior_updated: false,
        support_policy: SUPPORT_POLICY,
        parent_impact_handoff_sha256: parent_sha256,
        numerical_seed_count,
        family_id: surface.family_id,
        family_label: surface.family_label,
        family_admitted: surface.family_admitted,
        relative_likelihood_floor: configuration.relative_likelihood_floor,
        source_time_unix_s: surface.source_time_unix_s,
        seventh_arc_coordinates_deg: surface.arc_coordinates_deg,
        impact_time_offset_range_s: [minimum_offset, maximum_offset],
        particles: branch_particles.len(),
        supported_particles,
        unsupported_particles: branch_particles.len() - supported_particles,
        floored_particles,
        supported_baseline_mass,
        relative_score_log_normalizer: log_normalizer,
        baseline_effective_sample_size,
        conditional_effective_sample_size,
        baseline_mean,
        conditional_mean,
        mean_shift_nm,
        limitations,
        particle_values: branch_particles,
    })
}

fn report_document(
    result: &ConditionalSpatialResult,
    conditional: bool,
    bounds: ReportMapBounds,
) -> ReportDocument {
    let (title_suffix, subtitle) = if conditional {
        (
            "conditional sensitivity",
            format!(
                "{}; ESS {:.1} (baseline {:.1}); not a central posterior update",
                result.family_label,
                result.conditional_effective_sample_size,
                result.baseline_effective_sample_size,
            ),
        )
    } else {
        (
            "parent impact baseline",
            "Parent impact particles before the optional spatial sensitivity".to_string(),
        )
    };
    let points = result
        .particle_values
        .iter()
        .map(|particle| ReportPoint {
            latitude_deg: particle.latitude_deg,
            longitude_deg: particle.longitude_deg,
            weight: if conditional {
                particle.conditional_weight
            } else {
                particle.baseline_weight
            },
        })
        .collect();
    ReportDocument {
        title: format!("{} — {title_suffix}", result.name),
        subtitle,
        summary: vec![
            ("Branch".to_string(), result.branch_id.clone()),
            ("Surface family".to_string(), result.family_id.clone()),
            (
                "Supported parent mass".to_string(),
                format!("{:.3}%", 100.0 * result.supported_baseline_mass),
            ),
            (
                "Mean shift".to_string(),
                format!("{:.2} NM", result.mean_shift_nm),
            ),
            (
                "ESS baseline / conditional".to_string(),
                format!(
                    "{:.1} / {:.1}",
                    result.baseline_effective_sample_size, result.conditional_effective_sample_size
                ),
            ),
        ],
        points,
        diagnostics: Vec::new(),
        evidence_conditions: vec![
            format!("Application status: {}", result.application_status),
            format!("Support policy: {}", result.support_policy),
            format!(
                "Central posterior updated: {}",
                result.central_posterior_updated
            ),
        ],
        limitations: result.limitations.clone(),
        map_context: Some(ReportMapContext {
            bounds,
            references: Vec::new(),
            routes: vec![ReportMapRoute {
                label: "FL400 seventh arc".to_string(),
                style: "arc".to_string(),
                coordinates_deg: result.seventh_arc_coordinates_deg.clone(),
            }],
        }),
    }
}

fn csv(result: &ConditionalSpatialResult) -> String {
    let mut output = String::from(
        "source_run_id,model_family,seed,particle_index,eof_scenario_id,eof_draw_id,latitude_deg,longitude_deg,impact_time_unix_s,baseline_weight,conditional_weight,relative_log_likelihood,nearest_surface_distance_nm,surface_cell_id,source_cell_status,support_status,used_likelihood_floor\n",
    );
    for particle in &result.particle_values {
        output.push_str(&format!(
            "{},{},{},{},{},{},{:.12},{:.12},{:.6},{:.16e},{:.16e},{},{},{},{},{},{}\n",
            particle.identity.source_run_id,
            particle.identity.upstream.model_family,
            particle.identity.upstream.seed,
            particle.identity.upstream.particle,
            particle.identity.eof_scenario_id,
            particle.identity.eof_draw_id,
            particle.latitude_deg,
            particle.longitude_deg,
            particle.impact_time_unix_s,
            particle.baseline_weight,
            particle.conditional_weight,
            particle
                .relative_log_likelihood
                .map(|value| format!("{value:.16e}"))
                .unwrap_or_default(),
            particle
                .nearest_surface_distance_nm
                .map(|value| format!("{value:.12}"))
                .unwrap_or_default(),
            particle.surface_cell_id.as_deref().unwrap_or_default(),
            particle.source_cell_status.as_deref().unwrap_or_default(),
            particle.support_status,
            particle.used_likelihood_floor,
        ));
    }
    output
}

fn atomic_write(path: &Path, bytes: &[u8]) -> Result<()> {
    let parent = path.parent().context("artifact path has no parent")?;
    fs::create_dir_all(parent)?;
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
        .with_context(|| format!("cannot create {}", temporary.display()))?;
    stream.write_all(bytes)?;
    stream.sync_all()?;
    drop(stream);
    fs::rename(&temporary, path)?;
    Ok(())
}

fn write_json(path: &Path, value: &impl Serialize) -> Result<()> {
    let mut bytes = serde_json::to_vec_pretty(value)?;
    bytes.push(b'\n');
    atomic_write(path, &bytes)
}

fn prepare_output(path: &Path) -> Result<()> {
    if path.exists() {
        if fs::read_dir(path)?.next().is_some() {
            bail!("output directory is not empty: {}", path.display());
        }
    } else {
        fs::create_dir_all(path)?;
    }
    Ok(())
}

pub(crate) fn apply(configuration_path: &Path, output: &Path) -> Result<()> {
    prepare_output(output)?;
    let configuration_bytes = fs::read(configuration_path)
        .with_context(|| format!("cannot read {}", configuration_path.display()))?;
    let configuration: Configuration = toml::from_str(
        std::str::from_utf8(&configuration_bytes).context("configuration is not UTF-8")?,
    )
    .context("cannot parse conditional spatial configuration")?;
    if configuration.schema_version != SCHEMA_VERSION
        || configuration.name.trim().is_empty()
        || configuration.code_revision.trim().is_empty()
        || configuration.branch_id.trim().is_empty()
        || configuration.parent_impact_handoffs.is_empty()
        || !configuration.relative_likelihood_floor.is_finite()
        || !(0.0..=1.0).contains(&configuration.relative_likelihood_floor)
        || configuration.relative_likelihood_floor == 0.0
        || !configuration.maximum_source_time_offset_s.is_finite()
        || configuration.maximum_source_time_offset_s < 0.0
    {
        bail!("invalid conditional spatial configuration");
    }
    let mut hashes = BTreeMap::from([(
        "configuration".to_string(),
        sha256_bytes(&configuration_bytes),
    )]);
    let mut parents = Vec::with_capacity(configuration.parent_impact_handoffs.len());
    for (index, configured_path) in configuration.parent_impact_handoffs.iter().enumerate() {
        let parent_path = resolve(configuration_path, configured_path);
        let label = format!("parent_impact_handoff_{index}");
        let parent_bytes = read_hashed(&parent_path, &label, &mut hashes)?;
        let parent_sha256 = hashes[&label].clone();
        let parent: ImpactPosteriorHandoffV1 = serde_json::from_slice(&parent_bytes)
            .with_context(|| format!("cannot parse parent impact handoff {index}"))?;
        parent
            .validate()
            .with_context(|| format!("invalid parent impact handoff {index}"))?;
        parents.push((parent_sha256, parent));
    }
    let surface = match &configuration.model {
        ModelConfiguration::Pleiades {
            grid,
            surfaces,
            manifest,
            surface_id,
            source_time_unix_s,
            maximum_nearest_node_distance_nm,
        } => load_pleiades(
            configuration_path,
            grid,
            surfaces,
            manifest,
            surface_id,
            *source_time_unix_s,
            *maximum_nearest_node_distance_nm,
            &mut hashes,
        )?,
        ModelConfiguration::OceanDrift {
            handoff,
            family_id,
            source_time_unix_s,
            maximum_nearest_cell_distance_nm,
            allow_diagnostic_family,
        } => load_ocean_drift(
            configuration_path,
            handoff,
            family_id,
            *source_time_unix_s,
            *maximum_nearest_cell_distance_nm,
            *allow_diagnostic_family,
            &mut hashes,
        )?,
    };
    let result = evaluate(&configuration, parents, surface)?;
    let bounds = report_bounds(&result.particle_values)?;
    let baseline = report_document(&result, false, bounds);
    let conditional = report_document(&result, true, bounds);

    let result_path = output.join("conditional-spatial-sensitivity.json");
    let csv_path = output.join("conditional-spatial-particles.csv");
    write_json(&result_path, &result)?;
    atomic_write(&csv_path, csv(&result).as_bytes())?;
    let artifacts = [
        ("baseline.pdf", build_pdf(&baseline)?),
        ("baseline.svg", build_posterior_svg(&baseline)?),
        ("baseline.png", build_accident_panel_png(&baseline)?),
        ("conditional.pdf", build_pdf(&conditional)?),
        ("conditional.svg", build_posterior_svg(&conditional)?),
        ("conditional.png", build_accident_panel_png(&conditional)?),
    ];
    for (name, bytes) in artifacts {
        atomic_write(&output.join(name), &bytes)?;
    }
    let output_names = [
        "conditional-spatial-sensitivity.json",
        "conditional-spatial-particles.csv",
        "baseline.pdf",
        "baseline.svg",
        "baseline.png",
        "conditional.pdf",
        "conditional.svg",
        "conditional.png",
    ];
    let output_sha256 = output_names
        .iter()
        .map(|name| {
            let bytes = fs::read(output.join(name))?;
            Ok((name.to_string(), sha256_bytes(&bytes)))
        })
        .collect::<Result<BTreeMap<_, _>>>()?;
    let manifest = RunManifest {
        schema_version: SCHEMA_VERSION,
        command: "apply-conditional-surface",
        producer_executable_sha256: crate::executable_sha256()?,
        code_revision: configuration.code_revision.clone(),
        config_sha256: hashes["configuration"].clone(),
        input_sha256: hashes,
        output_sha256,
        reproduction_command: format!(
            "mh370 apply-conditional-surface --config {} --output {}",
            configuration_path.display(),
            output.display()
        ),
        scientific_scope: result.limitations.clone(),
    };
    write_json(&output.join("run-manifest.json"), &manifest)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn point(latitude_deg: f64, longitude_deg: f64) -> LatLon {
        LatLon::new(latitude_deg, longitude_deg).unwrap()
    }

    #[test]
    fn native_boundary_includes_edges_and_rejects_extrapolation() {
        let polygon = vec![[90.0, -40.0], [100.0, -40.0], [100.0, -30.0], [90.0, -30.0]];
        assert!(point_in_polygon(point(-35.0, 95.0), &polygon));
        assert!(point_in_polygon(point(-40.0, 95.0), &polygon));
        assert!(point_in_polygon(point(-30.0, 100.0), &polygon));
        assert!(!point_in_polygon(point(-29.999, 95.0), &polygon));
        assert!(!point_in_polygon(point(-35.0, 100.001), &polygon));
    }

    #[test]
    fn query_requires_both_native_support_and_distance_limit() {
        let surface = Surface {
            family_id: "fixture".to_string(),
            family_label: "Fixture".to_string(),
            family_admitted: false,
            source_time_unix_s: 1_394_237_940.0,
            maximum_nearest_distance_nm: 5.0,
            boundary: Some(vec![
                [94.9, -35.1],
                [95.1, -35.1],
                [95.1, -34.9],
                [94.9, -34.9],
            ]),
            arc_coordinates_deg: vec![[-35.0, 95.0]],
            nodes: vec![SurfaceNode {
                id: "node".to_string(),
                position: point(-35.0, 95.0),
                log_relative_likelihood: Some(-1.0),
                source_status: "grid_node".to_string(),
            }],
            limitations: Vec::new(),
        };
        assert_eq!(
            query_surface(&surface, point(-35.0, 95.0)).unwrap().0.id,
            "node"
        );
        assert!(query_surface(&surface, point(-34.91, 95.0)).is_none());
        assert!(query_surface(&surface, point(-35.0, 95.11)).is_none());
    }

    #[test]
    fn ocean_diagnostic_family_requires_opt_in_and_preserves_cell_status() {
        let fixture = br#"{
          "schema":"mh370-ocean-drift-family-likelihood-handoff-v1",
          "families":[{
            "id":"diagnostic-family",
            "label":"Diagnostic family",
            "decision":"diagnostic_only",
            "admitted":false,
            "failed_checks":["stability"],
            "limitations":["fixture limitation"],
            "cells":[{
              "id":"arc-135",
              "latitude_deg":-21.5,
              "longitude_deg":103.9,
              "relative_log_likelihood":-2.0,
              "status":"no_flaperon_arrival"
            }]
          }]
        }"#;
        assert!(
            parse_ocean_drift(fixture, "diagnostic-family", 1_394_237_940.0, 75.0, false,).is_err()
        );
        let surface =
            parse_ocean_drift(fixture, "diagnostic-family", 1_394_237_940.0, 75.0, true).unwrap();
        assert!(!surface.family_admitted);
        assert_eq!(surface.nodes[0].source_status, "no_flaperon_arrival");
        assert_eq!(surface.nodes[0].log_relative_likelihood, Some(-2.0));
    }

    #[test]
    fn log_normalization_and_effective_sample_size_are_independent_checks() {
        let log_normalizer = logsumexp([0.2_f64.ln(), 0.8_f64.ln()].into_iter()).unwrap();
        assert!(log_normalizer.abs() < 1.0e-12);
        let normalized = [
            (0.2_f64.ln() - log_normalizer).exp(),
            (0.8_f64.ln() - log_normalizer).exp(),
        ];
        assert!((normalized.iter().sum::<f64>() - 1.0).abs() < 1.0e-12);
        assert!(
            (effective_sample_size(normalized.into_iter()) - 1.4705882352941175).abs() < 1.0e-12
        );
    }

    #[test]
    fn numerical_seed_ledgers_may_have_distinct_evidence_normalizers_only() {
        use crate::impact_handoff::{
            EvidenceApplicationRoleV1, EvidenceApplicationV1, EvidenceLedgerV2,
        };

        let application = |config: char, log_evidence_increment: f64| EvidenceApplicationV1 {
            id: "r600-bto-at-0019".to_string(),
            role: EvidenceApplicationRoleV1::WeightUpdate,
            model_family: "corrected-r600-bto-given-reception".to_string(),
            config_sha256: config.to_string().repeat(64),
            input_sha256: BTreeMap::from([("satcom".to_string(), "a".repeat(64))]),
            log_evidence_increment: Some(log_evidence_increment),
        };
        let first = EvidenceLedgerV2 {
            entries: Vec::new(),
            applications: vec![application('b', -5.0)],
        };
        let second = EvidenceLedgerV2 {
            entries: Vec::new(),
            applications: vec![application('c', -5.2)],
        };
        assert!(compatible_evidence_ledgers(&first, &second));
        let mut incompatible = second;
        incompatible.applications[0]
            .input_sha256
            .insert("satcom".to_string(), "d".repeat(64));
        assert!(!compatible_evidence_ledgers(&first, &incompatible));
    }

    #[test]
    fn equal_numerical_seed_pool_preserves_total_mass() {
        let seed_weights = [[0.2, 0.8], [0.5, 0.5], [0.1, 0.9]];
        let pooled = seed_weights
            .iter()
            .flat_map(|weights| weights.iter())
            .map(|weight| weight / seed_weights.len() as f64)
            .sum::<f64>();
        assert!((pooled - 1.0).abs() < 1.0e-12);
    }
}
