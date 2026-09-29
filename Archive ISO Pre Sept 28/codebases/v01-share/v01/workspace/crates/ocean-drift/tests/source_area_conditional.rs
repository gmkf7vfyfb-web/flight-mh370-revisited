use mh370_domain::LatLon;
use mh370_ocean_drift::{
    evaluate_source_area, ArrivalSamplingConfig, ArrivalSamplingMethod, BarnacleChronology,
    BarnacleIsotopeModel, BarnacleRecord, DebrisEvidence, DebrisMotionFamily, DriftEnvironment,
    GeographicBounds, GriddedField, MotionConfig, NonRecoveryObservation, RecoveryEvent,
    SourceAreaCell, SourceAreaConfig,
};

fn constant_field(name: &str, components: &[(&str, f32)]) -> GriddedField {
    let mut bytes = b"MHGRID1\0".to_vec();
    bytes.extend(1u32.to_le_bytes());
    bytes.extend(0u32.to_le_bytes());
    for value in [2u32, 2, 2, components.len() as u32] {
        bytes.extend(value.to_le_bytes());
    }
    for value in [0.0_f64, 1_000_000.0, -20.0, 20.0, -150.0, 150.0] {
        bytes.extend(value.to_le_bytes());
    }
    for (component, value) in components {
        let mut encoded = [0u8; 16];
        encoded[..component.len()].copy_from_slice(component.as_bytes());
        bytes.extend(encoded);
        for _ in 0..8 {
            bytes.extend(value.to_le_bytes());
        }
    }
    GriddedField::from_bytes(name, &bytes).unwrap()
}

fn matching_delta18o(temperature_c: f64, seawater_delta18o: f64) -> f64 {
    (19.0 - temperature_c) / 4.63 + (seawater_delta18o - 0.27)
}

#[test]
fn no_arrival_cell_is_reported_without_aborting_conditional_surface() {
    let currents = constant_field("zero currents", &[("u", 0.0), ("v", 0.0)]);
    let sst = constant_field("constant SST", &[("sst", 20.0)]);
    let records = (0..49)
        .map(|index| BarnacleRecord {
            sample_id: format!("A2-G1-{:02}", index + 1),
            delta18o_calcite_per_mil: matching_delta18o(20.0, 0.4),
            growth_fraction: index as f64 / 48.0,
        })
        .collect::<Vec<_>>();
    let end = 10.0 * 86_400.0;
    let config = SourceAreaConfig {
        family: "synthetic".to_string(),
        seed: 9,
        particles_per_cell: 8,
        release_unix_seconds: 0.0,
        sampling: ArrivalSamplingConfig::default(),
        motion_families: vec![DebrisMotionFamily {
            id: "flaperon-motion".to_string(),
            motion: MotionConfig {
                integration_step_seconds: 86_400.0,
                output_step_seconds: 86_400.0,
                horizontal_diffusivity_m2_per_s: 0.0,
                stokes_velocity_scale: 1.0,
                windage_fraction: 0.0,
                windage_speed_m_per_s: 0.0,
                windage_angle_degrees: 0.0,
                current_standard_error_scale: 0.0,
            },
            debris: DebrisEvidence {
                events: vec![RecoveryEvent {
                    id: "flaperon".to_string(),
                    object_ids: vec!["right-flaperon".to_string()],
                    location: "synthetic recovery".to_string(),
                    position: LatLon::new(0.0, 0.0).unwrap(),
                    discovery_start_unix_seconds: end,
                    discovery_end_unix_seconds: end,
                    discovery_delay: Vec::new(),
                    evidence_weight: 1.0,
                    is_flaperon: true,
                }],
                pre_discovery_window_days: 2.0,
                spatial_bandwidth_km: 1.0,
                probability_floor: 1e-9,
                non_recoveries: Vec::new(),
            },
        }],
        isotope: Some(BarnacleIsotopeModel {
            records,
            chronologies: vec![BarnacleChronology {
                name: "synthetic".to_string(),
                start_unix_seconds: 0.0,
                end_unix_seconds: end,
                prior_weight: 1.0,
            }],
            seawater_delta18o_per_mil: 0.4,
            seawater_delta18o_sd_per_mil: 0.2,
            calibration_sd_c: 1.0,
            residual_sd_c: 1.0,
            sst_field_sd_c: 0.5,
            shell_smoothing_days: 3.0,
            correlation_days: 7.0,
            compatible_simultaneous_confidence: 0.95,
            rejection_simultaneous_confidence: 0.995,
            maximum_marginal_log_penalty: 0.7,
            maximum_rejection_log_penalty: 4.0,
        }),
    };
    let result = evaluate_source_area(
        &config,
        &[
            SourceAreaCell {
                id: "arrival".to_string(),
                position: LatLon::new(0.0, 0.0).unwrap(),
                prior_weight: 0.5,
            },
            SourceAreaCell {
                id: "no-arrival".to_string(),
                position: LatLon::new(0.0, 100.0).unwrap(),
                prior_weight: 0.5,
            },
        ],
        DriftEnvironment {
            currents: &currents,
            wind: None,
            stokes: None,
            coast: None,
        },
        Some(&sst),
    )
    .unwrap();

    let arrival = result
        .cells
        .iter()
        .find(|cell| cell.id == "arrival")
        .unwrap();
    let absent = result
        .cells
        .iter()
        .find(|cell| cell.id == "no-arrival")
        .unwrap();
    assert!(arrival.normalized_weight > 0.999_999);
    assert!(absent.normalized_weight > 0.0);
    assert!(absent.normalized_weight < 1e-6);
    assert!(absent.combined_log_weight.is_some());
    assert_eq!(
        serde_json::to_value(absent.status).unwrap(),
        "no_flaperon_arrival"
    );

    let isotope = arrival.isotope.as_ref().unwrap();
    assert_eq!(isotope.record_count, 49);
    assert_eq!(isotope.usable_arrival_weight_fraction, 1.0);
    let factored = arrival.combined_log_weight.unwrap() - arrival.prior_weight.ln();
    assert!(
        (factored - arrival.debris_log_compatibility - isotope.conditional_log_compatibility).abs()
            < 1e-12
    );
    assert_eq!(isotope.compatible_paths, 8);
    assert_eq!(isotope.marginal_paths, 0);
    assert_eq!(isotope.rejected_paths, 0);
}

#[test]
fn non_recovery_population_uses_an_independent_forward_ensemble() {
    let currents = constant_field("zero currents", &[("u", 0.0), ("v", 0.0)]);
    let end = 10.0 * 86_400.0;
    let config = SourceAreaConfig {
        family: "synthetic".to_string(),
        seed: 12,
        particles_per_cell: 16,
        release_unix_seconds: 0.0,
        sampling: ArrivalSamplingConfig {
            method: ArrivalSamplingMethod::AdaptiveSmc,
            resampling_interval_days: 2.0,
            selection_strength: 4.0,
            start_days_before_recovery: 8.0,
        },
        motion_families: vec![DebrisMotionFamily {
            id: "unobserved-high-windage-population".to_string(),
            motion: MotionConfig {
                integration_step_seconds: 86_400.0,
                output_step_seconds: 86_400.0,
                horizontal_diffusivity_m2_per_s: 0.0,
                stokes_velocity_scale: 0.0,
                windage_fraction: 0.0,
                windage_speed_m_per_s: 0.0,
                windage_angle_degrees: 0.0,
                current_standard_error_scale: 0.0,
            },
            debris: DebrisEvidence {
                events: Vec::new(),
                pre_discovery_window_days: 2.0,
                spatial_bandwidth_km: 100.0,
                probability_floor: 1e-9,
                non_recoveries: vec![NonRecoveryObservation {
                    id: "no-reports".to_string(),
                    location: "synthetic coast".to_string(),
                    bounds: GeographicBounds {
                        south_degrees: -10.0,
                        north_degrees: 10.0,
                        west_degrees: -10.0,
                        east_degrees: 10.0,
                    },
                    observation_start_unix_seconds: 0.0,
                    observation_end_unix_seconds: end,
                    expected_reportable_items: 1.0,
                }],
            },
        }],
        isotope: None,
    };
    let result = evaluate_source_area(
        &config,
        &[SourceAreaCell {
            id: "source".to_string(),
            position: LatLon::new(0.0, 0.0).unwrap(),
            prior_weight: 1.0,
        }],
        DriftEnvironment {
            currents: &currents,
            wind: None,
            stokes: None,
            coast: None,
        },
        None,
    )
    .unwrap();

    let family = &result.cells[0].motion_families[0];
    assert_eq!(family.sampling.method, ArrivalSamplingMethod::Independent);
    assert_eq!(family.sampling.resampling_events, 0);
    assert!(family.recovery_ensembles.is_empty());
    assert!(family.recoveries.is_empty());
    assert_eq!(family.non_recoveries.len(), 1);
    assert_eq!(
        family.non_recoveries[0].conservative_scoring_probability,
        0.0
    );
    assert_eq!(result.cells[0].normalized_weight, 1.0);
}
