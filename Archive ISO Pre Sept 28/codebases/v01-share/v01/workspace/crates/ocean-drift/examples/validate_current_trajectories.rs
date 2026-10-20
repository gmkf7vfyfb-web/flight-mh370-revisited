//! Deterministic trajectory replay against raw GDP six-hour positions.
//!
//! Every selected interval is scored. If a field terminates, the operational
//! forecast holds its last valid position to the target epoch; completion and
//! termination category are also reported. This avoids survivor-only accuracy.

use std::{collections::BTreeMap, env, fs, io::BufReader};

use mh370_domain::{destination_wgs84, great_circle_distance_nm, Degrees, LatLon, NauticalMiles};
use mh370_ocean_drift::{
    simulate_path, DriftEnvironment, FieldTimeAxis, GriddedField, MotionConfig,
    PathTerminationReason,
};
use rand_chacha::{rand_core::SeedableRng, ChaCha8Rng};
use serde::Serialize;

#[derive(Debug, Clone, Copy)]
struct Observation {
    unix_seconds: f64,
    position: LatLon,
    drogue_lost_unix_seconds: Option<f64>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
enum DrogueStatus {
    Drogued,
    Undrogued,
    Transition,
    Unknown,
}

impl DrogueStatus {
    fn label(self) -> &'static str {
        match self {
            Self::Drogued => "drogued",
            Self::Undrogued => "undrogued",
            Self::Transition => "drogue_transition",
            Self::Unknown => "unknown",
        }
    }
}

#[derive(Debug, Clone)]
struct Candidate {
    trajectory_id: String,
    start: Observation,
    end: Observation,
    prior_day: Option<Observation>,
    drogue_status: DrogueStatus,
}

#[derive(Debug)]
struct CaseResult {
    region: &'static str,
    drogue_status: DrogueStatus,
    current_error_km: f64,
    persistence_error_km: f64,
    prior_velocity_error_km: Option<f64>,
    completed: bool,
}

#[derive(Debug, Serialize)]
struct ScoreSummary {
    cases: usize,
    complete_fraction: f64,
    mean_current_with_terminal_hold_error_km: f64,
    median_current_with_terminal_hold_error_km: f64,
    mean_persistence_error_km: f64,
    median_persistence_error_km: f64,
    current_better_than_persistence_fraction: f64,
    prior_velocity_baseline_cases: usize,
    mean_prior_velocity_error_km: Option<f64>,
    median_prior_velocity_error_km: Option<f64>,
    current_better_than_prior_velocity_fraction: Option<f64>,
}

#[derive(Debug, Serialize)]
struct Summary {
    schema: &'static str,
    family: String,
    current_field: String,
    stokes_field: Option<String>,
    stokes_velocity_scale: f64,
    renormalize_finite_stokes_corners: bool,
    renormalize_finite_current_corners: bool,
    maximum_current_interpolation_gap_hours: Option<f64>,
    trajectory_file: String,
    horizon_days: f64,
    requested_segments: usize,
    candidate_segments: usize,
    in_time_support_candidate_segments: usize,
    attempted_segments: usize,
    completed_segments: usize,
    field_terminated_segments: usize,
    termination_reasons: BTreeMap<PathTerminationReason, usize>,
    first_start_unix_seconds: f64,
    last_start_unix_seconds: f64,
    all_attempts: ScoreSummary,
    by_longitude_region: BTreeMap<&'static str, ScoreSummary>,
    by_drogue_status: BTreeMap<&'static str, ScoreSummary>,
    survivor_median_current_error_km: f64,
    survivor_mean_current_error_km: f64,
    survivor_median_persistence_error_km: f64,
    survivor_mean_persistence_error_km: f64,
    survivor_current_better_fraction: f64,
    interpretation: String,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let arguments = env::args().collect::<Vec<_>>();
    if arguments.len() < 4 || arguments.len() > 12 {
        return Err(
            "usage: validate_current_trajectories FAMILY CURRENT.mhgrid GDP_6H.csv [horizon_days] [segments] [output.json] [STOKES.mhgrid|none] [MAX_CURRENT_GAP_HOURS] [STOKES_VELOCITY_SCALE] [RENORMALIZE_FINITE_STOKES_CORNERS] [RENORMALIZE_FINITE_CURRENT_CORNERS]"
                .into(),
        );
    }
    let family = arguments[1].as_str();
    if family.trim().is_empty() {
        return Err("family must be nonempty".into());
    }
    let horizon_days = arguments
        .get(4)
        .map(|value| value.parse::<f64>())
        .transpose()?
        .unwrap_or(30.0);
    let requested_segments = arguments
        .get(5)
        .map(|value| value.parse::<usize>())
        .transpose()?
        .unwrap_or(600);
    if !horizon_days.is_finite() || horizon_days <= 0.0 || requested_segments == 0 {
        return Err("horizon and segment count must be positive".into());
    }
    let maximum_current_interpolation_gap_hours = arguments
        .get(8)
        .filter(|value| value.as_str() != "none")
        .map(|value| value.parse::<f64>())
        .transpose()?;
    let stokes_velocity_scale = arguments
        .get(9)
        .map(|value| value.parse::<f64>())
        .transpose()?
        .unwrap_or(1.0);
    let renormalize_finite_stokes_corners = arguments
        .get(10)
        .map(|value| value.parse::<bool>())
        .transpose()?
        .unwrap_or(false);
    let renormalize_finite_current_corners = arguments
        .get(11)
        .map(|value| value.parse::<bool>())
        .transpose()?
        .unwrap_or(false);
    let current_file = fs::File::open(&arguments[2])?;
    let mut field =
        GriddedField::from_reader(family, BufReader::with_capacity(1024 * 1024, current_file))?;
    field.set_maximum_time_interpolation_gap_seconds(
        maximum_current_interpolation_gap_hours.map(|hours| hours * 3_600.0),
    )?;
    field.set_renormalize_finite_spatial_corners(renormalize_finite_current_corners);
    let stokes_path = arguments.get(7).filter(|path| path.as_str() != "none");
    let stokes = if let Some(path) = stokes_path {
        let stokes_file = fs::File::open(path)?;
        let mut stokes = GriddedField::from_reader(
            "stokes",
            BufReader::with_capacity(1024 * 1024, stokes_file),
        )?;
        stokes.set_renormalize_finite_spatial_corners(renormalize_finite_stokes_corners);
        Some(stokes)
    } else {
        if renormalize_finite_stokes_corners {
            return Err("Stokes spatial repair requires a Stokes field".into());
        }
        None
    };
    let field_time_range =
        (field.time_axis == FieldTimeAxis::UnixSeconds).then(|| field.time_range());
    let trajectories = parse_trajectories(&fs::read_to_string(&arguments[3])?)?;
    let horizon_seconds = horizon_days * 86_400.0;
    let all_candidates = candidates(&trajectories, horizon_seconds);
    let candidates = all_candidates
        .iter()
        .filter(|candidate| {
            field_time_range.map_or(true, |(first, last)| {
                candidate.start.unix_seconds >= first && candidate.end.unix_seconds <= last
            })
        })
        .cloned()
        .collect::<Vec<_>>();
    let selected = evenly_spaced(&candidates, requested_segments);
    if selected.is_empty() {
        return Err("no replay intervals found".into());
    }

    let mut cases = Vec::with_capacity(selected.len());
    let mut survivor_current_errors = Vec::new();
    let mut survivor_persistence_errors = Vec::new();
    let mut termination_reasons = BTreeMap::new();
    for candidate in &selected {
        let mut rng = ChaCha8Rng::seed_from_u64(stable_key(&candidate.trajectory_id));
        let path = simulate_path(
            DriftEnvironment {
                currents: &field,
                wind: None,
                stokes: stokes.as_ref(),
                coast: None,
            },
            candidate.start.position,
            candidate.start.unix_seconds,
            candidate.end.unix_seconds,
            MotionConfig {
                integration_step_seconds: 21_600.0,
                output_step_seconds: 21_600.0,
                horizontal_diffusivity_m2_per_s: 0.0,
                stokes_velocity_scale,
                windage_fraction: 0.0,
                windage_speed_m_per_s: 0.0,
                windage_angle_degrees: 0.0,
                current_standard_error_scale: 0.0,
            },
            &mut rng,
        )?;
        let completed = path.termination.is_none();
        if let Some(termination) = &path.termination {
            *termination_reasons.entry(termination.reason).or_insert(0) += 1;
        }
        let predicted = path.points.last().ok_or("empty simulated path")?.position;
        let current_error_km = distance_km(predicted, candidate.end.position);
        let persistence_error_km = distance_km(candidate.start.position, candidate.end.position);
        let prior_velocity_error_km = candidate
            .prior_day
            .and_then(|prior| prior_velocity_prediction(prior, candidate.start, horizon_seconds))
            .map(|prediction| distance_km(prediction, candidate.end.position));
        if completed {
            survivor_current_errors.push(current_error_km);
            survivor_persistence_errors.push(persistence_error_km);
        }
        cases.push(CaseResult {
            region: longitude_region(candidate.start.position.longitude.0),
            drogue_status: candidate.drogue_status,
            current_error_km,
            persistence_error_km,
            prior_velocity_error_km,
            completed,
        });
    }

    let mut by_longitude_region = BTreeMap::new();
    for region in ["western_10e_60e", "central_60e_100e", "eastern_100e_150e"] {
        let regional = cases
            .iter()
            .filter(|case| case.region == region)
            .collect::<Vec<_>>();
        if !regional.is_empty() {
            by_longitude_region.insert(region, summarize(&regional));
        }
    }
    let mut by_drogue_status = BTreeMap::new();
    for status in [
        DrogueStatus::Drogued,
        DrogueStatus::Undrogued,
        DrogueStatus::Transition,
        DrogueStatus::Unknown,
    ] {
        let selected = cases
            .iter()
            .filter(|case| case.drogue_status == status)
            .collect::<Vec<_>>();
        if !selected.is_empty() {
            by_drogue_status.insert(status.label(), summarize(&selected));
        }
    }
    let survivor_better = survivor_current_errors
        .iter()
        .zip(&survivor_persistence_errors)
        .filter(|(forecast, persistence)| forecast < persistence)
        .count();
    let leakage = if family.to_ascii_lowercase().contains("gdp") {
        "Raw drifters may contribute to the GDP climatology, so this is not statistically held out."
    } else if family.to_ascii_lowercase().contains("hycom")
        || family.to_ascii_lowercase().contains("gofs")
    {
        "The assimilative HYCOM+NCODA reanalysis may use surface observations related to the validating drifter network, so this is not guaranteed held out."
    } else {
        "Assimilation or climatology overlap with the validating drifters has not been excluded."
    };
    let summary = Summary {
        schema: "mh370-current-trajectory-replay-v5",
        family: family.to_string(),
        current_field: arguments[2].clone(),
        stokes_field: stokes_path.cloned(),
        stokes_velocity_scale,
        renormalize_finite_stokes_corners,
        renormalize_finite_current_corners,
        maximum_current_interpolation_gap_hours,
        trajectory_file: arguments[3].clone(),
        horizon_days,
        requested_segments,
        candidate_segments: all_candidates.len(),
        in_time_support_candidate_segments: candidates.len(),
        attempted_segments: cases.len(),
        completed_segments: survivor_current_errors.len(),
        field_terminated_segments: termination_reasons.values().sum(),
        termination_reasons,
        first_start_unix_seconds: selected
            .iter()
            .map(|candidate| candidate.start.unix_seconds)
            .fold(f64::INFINITY, f64::min),
        last_start_unix_seconds: selected
            .iter()
            .map(|candidate| candidate.start.unix_seconds)
            .fold(f64::NEG_INFINITY, f64::max),
        all_attempts: summarize(&cases.iter().collect::<Vec<_>>()),
        by_longitude_region,
        by_drogue_status,
        survivor_median_current_error_km: median(survivor_current_errors.clone()),
        survivor_mean_current_error_km: mean(&survivor_current_errors),
        survivor_median_persistence_error_km: median(survivor_persistence_errors.clone()),
        survivor_mean_persistence_error_km: mean(&survivor_persistence_errors),
        survivor_current_better_fraction: survivor_better as f64
            / survivor_current_errors.len() as f64,
        interpretation: format!(
            "Candidates outside the field's declared outer time range are reported but not selected. Every selected in-time interval is scored. A terminated {family} path holds its last valid position to the target time and remains in all-attempt metrics; internal time-gap and other termination categories are separate. Drogued, undrogued, and intervals spanning drogue loss are reported separately because explicit surface Stokes drift is not the same physical forecast for those targets. Persistence and a prior-24-hour constant-velocity baseline are reported. Field declared time support is {:?}. {leakage}",
            field_time_range,
        ),
    };
    let rendered = serde_json::to_string_pretty(&summary)? + "\n";
    if let Some(output) = arguments.get(6) {
        fs::write(output, rendered)?;
    } else {
        print!("{rendered}");
    }
    Ok(())
}

fn candidates(
    trajectories: &BTreeMap<String, Vec<Observation>>,
    horizon_seconds: f64,
) -> Vec<Candidate> {
    let mut result = Vec::new();
    let stride = ((horizon_seconds / 21_600.0).round() as usize).max(1);
    for (trajectory_id, observations) in trajectories {
        for start_index in (0..observations.len()).step_by(stride) {
            let start = observations[start_index];
            let target_time = start.unix_seconds + horizon_seconds;
            let Some(end) = observations[start_index..]
                .iter()
                .find(|item| (item.unix_seconds - target_time).abs() < 1.0)
                .copied()
            else {
                continue;
            };
            let prior_time = start.unix_seconds - 86_400.0;
            let prior_day = observations[..=start_index]
                .iter()
                .find(|item| (item.unix_seconds - prior_time).abs() < 1.0)
                .copied();
            result.push(Candidate {
                trajectory_id: trajectory_id.clone(),
                start,
                end,
                prior_day,
                drogue_status: classify_drogue(start, end),
            });
        }
    }
    result.sort_by(|first, second| {
        first
            .start
            .unix_seconds
            .total_cmp(&second.start.unix_seconds)
            .then_with(|| first.trajectory_id.cmp(&second.trajectory_id))
    });
    result
}

fn classify_drogue(start: Observation, end: Observation) -> DrogueStatus {
    let Some(lost) = start.drogue_lost_unix_seconds else {
        return DrogueStatus::Unknown;
    };
    if end.unix_seconds < lost {
        DrogueStatus::Drogued
    } else if start.unix_seconds >= lost {
        DrogueStatus::Undrogued
    } else {
        DrogueStatus::Transition
    }
}

fn evenly_spaced(candidates: &[Candidate], requested: usize) -> Vec<Candidate> {
    if candidates.len() <= requested {
        return candidates.to_vec();
    }
    (0..requested)
        .map(|index| {
            let candidate_index = index * candidates.len() / requested;
            candidates[candidate_index].clone()
        })
        .collect()
}

fn summarize(cases: &[&CaseResult]) -> ScoreSummary {
    let current = cases
        .iter()
        .map(|case| case.current_error_km)
        .collect::<Vec<_>>();
    let persistence = cases
        .iter()
        .map(|case| case.persistence_error_km)
        .collect::<Vec<_>>();
    let prior_velocity = cases
        .iter()
        .filter_map(|case| case.prior_velocity_error_km.map(|error| (*case, error)))
        .collect::<Vec<_>>();
    let current_better_persistence = cases
        .iter()
        .filter(|case| case.current_error_km < case.persistence_error_km)
        .count();
    let prior_values = prior_velocity
        .iter()
        .map(|(_, error)| *error)
        .collect::<Vec<_>>();
    let current_better_prior = prior_velocity
        .iter()
        .filter(|(case, error)| case.current_error_km < *error)
        .count();
    ScoreSummary {
        cases: cases.len(),
        complete_fraction: cases.iter().filter(|case| case.completed).count() as f64
            / cases.len() as f64,
        mean_current_with_terminal_hold_error_km: mean(&current),
        median_current_with_terminal_hold_error_km: median(current),
        mean_persistence_error_km: mean(&persistence),
        median_persistence_error_km: median(persistence),
        current_better_than_persistence_fraction: current_better_persistence as f64
            / cases.len() as f64,
        prior_velocity_baseline_cases: prior_values.len(),
        mean_prior_velocity_error_km: (!prior_values.is_empty()).then(|| mean(&prior_values)),
        median_prior_velocity_error_km: (!prior_values.is_empty())
            .then(|| median(prior_values.clone())),
        current_better_than_prior_velocity_fraction: (!prior_values.is_empty())
            .then_some(current_better_prior as f64 / prior_values.len() as f64),
    }
}

fn prior_velocity_prediction(
    prior: Observation,
    start: Observation,
    horizon_seconds: f64,
) -> Option<LatLon> {
    let elapsed = start.unix_seconds - prior.unix_seconds;
    if elapsed <= 0.0 {
        return None;
    }
    let distance = great_circle_distance_nm(prior.position, start.position).0;
    if distance == 0.0 {
        return Some(start.position);
    }
    let first_latitude = prior.position.latitude.to_radians();
    let second_latitude = start.position.latitude.to_radians();
    let longitude_difference =
        (start.position.longitude.0 - prior.position.longitude.0).to_radians();
    let bearing = (longitude_difference.sin() * second_latitude.cos())
        .atan2(
            first_latitude.cos() * second_latitude.sin()
                - first_latitude.sin() * second_latitude.cos() * longitude_difference.cos(),
        )
        .to_degrees()
        .rem_euclid(360.0);
    destination_wgs84(
        start.position,
        Degrees(bearing),
        NauticalMiles(distance * horizon_seconds / elapsed),
    )
    .ok()
}

fn longitude_region(longitude: f64) -> &'static str {
    if longitude < 60.0 {
        "western_10e_60e"
    } else if longitude < 100.0 {
        "central_60e_100e"
    } else {
        "eastern_100e_150e"
    }
}

fn distance_km(first: LatLon, second: LatLon) -> f64 {
    great_circle_distance_nm(first, second).0 * 1.852
}

fn stable_key(identifier: &str) -> u64 {
    identifier
        .bytes()
        .fold(0xcbf2_9ce4_8422_2325, |hash, byte| {
            (hash ^ u64::from(byte)).wrapping_mul(0x0000_0100_0000_01b3)
        })
}

fn parse_trajectories(
    text: &str,
) -> Result<BTreeMap<String, Vec<Observation>>, Box<dyn std::error::Error>> {
    let mut tracks: BTreeMap<String, Vec<Observation>> = BTreeMap::new();
    for (index, line) in text.lines().enumerate().skip(2) {
        if line.trim().is_empty() {
            continue;
        }
        let fields = line.split(',').collect::<Vec<_>>();
        if fields.len() < 4 {
            return Err(format!("invalid trajectory row {}", index + 1).into());
        }
        let latitude = fields[2].parse::<f64>()?;
        let longitude = fields[3].parse::<f64>()?;
        let drogue_lost_unix_seconds = fields
            .get(4)
            .filter(|value| !value.trim().is_empty())
            .map(|value| parse_utc(value))
            .transpose()?;
        if !(-50.0..=30.0).contains(&latitude) || !(10.0..=150.0).contains(&longitude) {
            continue;
        }
        tracks
            .entry(fields[0].to_string())
            .or_default()
            .push(Observation {
                unix_seconds: parse_utc(fields[1])?,
                position: LatLon::new(latitude, longitude)?,
                drogue_lost_unix_seconds,
            });
    }
    for observations in tracks.values_mut() {
        observations.sort_by(|first, second| first.unix_seconds.total_cmp(&second.unix_seconds));
    }
    Ok(tracks)
}

fn parse_utc(value: &str) -> Result<f64, Box<dyn std::error::Error>> {
    if value.len() != 20 || !value.ends_with('Z') {
        return Err(format!("unsupported UTC timestamp: {value}").into());
    }
    let year = value[0..4].parse::<i64>()?;
    let month = value[5..7].parse::<i64>()?;
    let day = value[8..10].parse::<i64>()?;
    let hour = value[11..13].parse::<i64>()?;
    let minute = value[14..16].parse::<i64>()?;
    let second = value[17..19].parse::<i64>()?;
    Ok((days_from_civil(year, month, day) * 86_400 + hour * 3_600 + minute * 60 + second) as f64)
}

fn days_from_civil(year: i64, month: i64, day: i64) -> i64 {
    let year = year - i64::from(month <= 2);
    let era = if year >= 0 { year } else { year - 399 } / 400;
    let year_of_era = year - era * 400;
    let shifted_month = month + if month > 2 { -3 } else { 9 };
    let day_of_year = (153 * shifted_month + 2) / 5 + day - 1;
    let day_of_era = 365 * year_of_era + year_of_era / 4 - year_of_era / 100 + day_of_year;
    era * 146_097 + day_of_era - 719_468
}

fn mean(values: &[f64]) -> f64 {
    values.iter().sum::<f64>() / values.len() as f64
}

fn median(mut values: Vec<f64>) -> f64 {
    values.sort_by(f64::total_cmp);
    let middle = values.len() / 2;
    if values.len() % 2 == 0 {
        (values[middle - 1] + values[middle]) / 2.0
    } else {
        values[middle]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn observation(time: f64, lost: Option<f64>) -> Observation {
        Observation {
            unix_seconds: time,
            position: LatLon::new(0.0, 0.0).unwrap(),
            drogue_lost_unix_seconds: lost,
        }
    }

    #[test]
    fn drogue_status_separates_physical_validation_targets() {
        assert_eq!(
            classify_drogue(observation(0.0, Some(20.0)), observation(10.0, Some(20.0))),
            DrogueStatus::Drogued
        );
        assert_eq!(
            classify_drogue(observation(20.0, Some(20.0)), observation(30.0, Some(20.0))),
            DrogueStatus::Undrogued
        );
        assert_eq!(
            classify_drogue(observation(10.0, Some(20.0)), observation(30.0, Some(20.0))),
            DrogueStatus::Transition
        );
        assert_eq!(
            classify_drogue(observation(0.0, None), observation(10.0, None)),
            DrogueStatus::Unknown
        );
    }
}
