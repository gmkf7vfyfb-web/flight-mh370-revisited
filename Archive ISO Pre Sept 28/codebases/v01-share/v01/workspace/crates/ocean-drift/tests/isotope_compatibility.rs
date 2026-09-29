use mh370_domain::LatLon;
use mh370_ocean_drift::{
    BarnacleChronology, BarnacleIsotopeModel, BarnacleRecord, DriftPath, DriftPoint, GriddedField,
};

fn temperature_field(times: &[f64], temperatures: &[f32]) -> GriddedField {
    assert_eq!(times.len(), temperatures.len());
    let mut bytes = b"MHGRID1\0".to_vec();
    bytes.extend(1u32.to_le_bytes());
    bytes.extend(0u32.to_le_bytes());
    for value in [times.len() as u32, 2, 2, 1] {
        bytes.extend(value.to_le_bytes());
    }
    for value in times {
        bytes.extend(value.to_le_bytes());
    }
    for value in [-1.0_f64, 1.0, -1.0, 1.0] {
        bytes.extend(value.to_le_bytes());
    }
    let mut name = [0u8; 16];
    name[..3].copy_from_slice(b"sst");
    bytes.extend(name);
    for temperature in temperatures {
        for _ in 0..4 {
            bytes.extend(temperature.to_le_bytes());
        }
    }
    GriddedField::from_bytes("synthetic SST", &bytes).unwrap()
}

fn path(end: f64) -> DriftPath {
    DriftPath {
        points: vec![
            DriftPoint {
                unix_seconds: 0.0,
                position: LatLon::new(0.0, 0.0).unwrap(),
            },
            DriftPoint {
                unix_seconds: end,
                position: LatLon::new(0.0, 0.0).unwrap(),
            },
        ],
        termination: None,
        log_importance_weight: 0.0,
    }
}

fn calcite_for_temperature(temperature: f64) -> f64 {
    (19.0 - temperature) / 4.63 + (0.4 - 0.27)
}

fn model(chronologies: Vec<BarnacleChronology>, target_temperature: f64) -> BarnacleIsotopeModel {
    BarnacleIsotopeModel {
        records: [0.0, 0.5, 1.0]
            .into_iter()
            .enumerate()
            .map(|(index, growth_fraction)| BarnacleRecord {
                sample_id: format!("sample-{index}"),
                delta18o_calcite_per_mil: calcite_for_temperature(target_temperature),
                growth_fraction,
            })
            .collect(),
        chronologies,
        seawater_delta18o_per_mil: 0.4,
        seawater_delta18o_sd_per_mil: 0.05,
        calibration_sd_c: 0.3,
        residual_sd_c: 0.7,
        sst_field_sd_c: 0.3,
        shell_smoothing_days: 1.0,
        correlation_days: 2.0,
        compatible_simultaneous_confidence: 0.95,
        rejection_simultaneous_confidence: 0.995,
        maximum_marginal_log_penalty: 0.7,
        maximum_rejection_log_penalty: 4.0,
    }
}

fn chronology(name: &str, start_days: f64, end_days: f64) -> BarnacleChronology {
    BarnacleChronology {
        name: name.to_string(),
        start_unix_seconds: start_days * 86_400.0,
        end_unix_seconds: end_days * 86_400.0,
        prior_weight: 1.0,
    }
}

#[test]
fn any_compatible_chronology_is_neutral_despite_an_incompatible_alternative() {
    let times = [0.0, 4.0, 9.0, 10.0, 14.0, 20.0].map(|days| days * 86_400.0);
    let sst = temperature_field(&times, &[35.0, 35.0, 20.0, 20.0, 20.0, 20.0]);
    let model = model(
        vec![
            chronology("incompatible", 0.0, 4.0),
            chronology("compatible", 10.0, 14.0),
        ],
        20.0,
    );
    let evaluation = model
        .evaluate_conditional(&[path(20.0 * 86_400.0)], &[1.0], &sst)
        .unwrap();
    assert_eq!(evaluation.compatible_paths, 1);
    assert_eq!(evaluation.rejected_paths, 0);
    assert_eq!(evaluation.conditional_log_compatibility, 0.0);
}

#[test]
fn marginal_penalty_is_soft_and_rejection_is_bounded() {
    let times = [0.0, 4.0 * 86_400.0];
    let chronology = chronology("only", 0.0, 4.0);
    let mut marginal = None;
    for offset_tenths in 1..100 {
        let temperature = 20.0 + offset_tenths as f32 / 10.0;
        let sst = temperature_field(&times, &[temperature, temperature]);
        let evaluation = model(vec![chronology.clone()], 20.0)
            .evaluate_conditional(&[path(4.0 * 86_400.0)], &[1.0], &sst)
            .unwrap();
        if evaluation.marginal_paths == 1 {
            marginal = Some(evaluation);
            break;
        }
    }
    let marginal = marginal.expect("synthetic offset should cross the marginal envelope");
    assert!(marginal.conditional_log_compatibility <= 0.0);
    assert!(marginal.conditional_log_compatibility >= -0.7);

    let rejected_sst = temperature_field(&times, &[50.0, 50.0]);
    let rejected = model(vec![chronology], 20.0)
        .evaluate_conditional(&[path(4.0 * 86_400.0)], &[1.0], &rejected_sst)
        .unwrap();
    assert_eq!(rejected.rejected_paths, 1);
    assert!((rejected.conditional_log_compatibility + 4.0).abs() < 1e-12);
}

#[test]
fn missing_sst_coverage_is_neutral_and_reported_not_survivor_conditioned() {
    let sst = temperature_field(&[0.0, 4.0 * 86_400.0], &[20.0, 20.0]);
    let evaluation = model(vec![chronology("outside", 10.0, 14.0)], 20.0)
        .evaluate_conditional(&[path(20.0 * 86_400.0)], &[2.0], &sst)
        .unwrap();
    assert_eq!(evaluation.missing_coverage_paths, 1);
    assert_eq!(evaluation.usable_paths, 0);
    assert_eq!(evaluation.missing_coverage_arrival_weight_fraction, 1.0);
    assert_eq!(evaluation.conditional_log_compatibility, 0.0);
}

#[test]
fn one_unevaluable_chronology_prevents_all_chronology_rejection() {
    let sst = temperature_field(&[0.0, 4.0 * 86_400.0], &[50.0, 50.0]);
    let evaluation = model(
        vec![
            chronology("covered-and-rejected", 0.0, 4.0),
            chronology("outside-sst-support", 10.0, 14.0),
        ],
        20.0,
    )
    .evaluate_conditional(&[path(20.0 * 86_400.0)], &[1.0], &sst)
    .unwrap();
    assert_eq!(evaluation.rejected_paths, 0);
    assert_eq!(evaluation.missing_coverage_paths, 1);
    assert_eq!(evaluation.conditional_log_compatibility, 0.0);
}
