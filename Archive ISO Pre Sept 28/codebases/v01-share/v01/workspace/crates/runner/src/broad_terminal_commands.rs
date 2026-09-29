//! In-memory composition of the broad 00:11 handoff, exact R600 contact, and
//! one explicitly declared mirrored end-of-flight family.
//!
//! File/config loading remains a thin future CLI concern. This module owns no
//! scientific equation: powered continuation, SATCOM scoring, system timing,
//! and end-of-flight propagation are delegated to their respective spokes.

use std::collections::{BTreeMap, BTreeSet};

use anyhow::{bail, Context, Result};
use mh370_domain::{AircraftState, Feet, FeetPerMinute, Hertz, Knots, Seconds};
use mh370_end_of_flight::{
    attempt_controlled_to_uncontrolled_with_atmosphere_and_checkpoints,
    conditional_successful_apu_sdu_logon_lag_likelihood, exact_dual_exhaustion_boundary,
    AerodynamicModel, ApuStartPolicy, AtmosphereProfile, ConditionalLagSupport,
    ConditionalModelFamily, ConditionalSuccessfulApuSduTimingInput, ControlCommand, ControlFamily,
    ControlledToUncontrolledAttempt, ControlledToUncontrolledPolicy, ExactDualExhaustionBoundary,
    ExactDualExhaustionBoundaryInput, ExactTimeCheckpoint, ExactTimeCheckpointSchedule,
    IntegrationSettings, Kilograms, MetresPerSecond, ModelWeight, R600ObservedLogonTime,
    RestartTransientFamily, SuccessfulApuSduErlangLagConfig, TransitionAtmosphere,
    TransitionAtmosphereError, TransitionKernelInput, UtcPosixSeconds,
};
use mh370_estimator::{
    BroadDualEngineExhaustionOutcome, BroadDualEngineExhaustionResult, BroadEvidenceDispositionV1,
    BroadEvidenceIdentityV1, BroadFlightModel, BroadFlightState, BroadPosteriorHandoffParticleV1,
    BroadPosteriorHandoffV1,
};
use mh370_particle_filter::{normalize_log_weights, rng_for};
use mh370_satcom::{
    score_exact_time_satcom_contact, ExactTimeSatcomContact, ExactTimeSatcomContactFit,
    SatcomModelConfig,
};
use serde::{Deserialize, Serialize};

use crate::broad_impact_handoff::{
    BroadImpactDataV1, BroadImpactHandoffV1, BroadLogonTimingParticleEvidenceV1,
    BroadLogonTimingZeroSupportReasonV1, BroadOutcomeMassCellV1, BroadOutcomeMassV1,
    BroadR600ParticleEvidenceV1, BroadR600ZeroSupportReasonV1, BroadTerminalDrawIdentityV1,
    BroadTerminalEvidenceModelV1, BroadTerminalOutcomeV1, BroadTerminalParticleIdentityV1,
    BroadTerminalParticleV1, BROAD_IMPACT_HANDOFF_SCHEMA_ID, BROAD_IMPACT_HANDOFF_SCHEMA_VERSION,
};
use crate::impact_handoff::{
    EnuVelocityV1, EvidenceApplicationRoleV1, EvidenceIdentityV2, ImpactEnergyV1,
};
use crate::sha256_bytes;

const SIDECAR_SCHEMA_ID: &str = "mh370-broad-terminal-transition-sidecar";
const SIDECAR_SCHEMA_VERSION: u32 = 1;
const MPS_PER_KNOT: f64 = 1_852.0 / 3_600.0;
const MPS_PER_FPM: f64 = 0.304_8 / 60.0;
const TIME_TOLERANCE_S: f64 = 1.0e-6;

/// Maps one consumed identity in the broad handoff to its open downstream
/// identity. The mapping prevents a syntactically valid terminal ledger from
/// silently dropping or relabelling parent evidence.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub(crate) struct BroadUpstreamEvidenceMappingV1 {
    pub source: BroadEvidenceIdentityV1,
    pub downstream: EvidenceIdentityV2,
}

/// Caller-owned terminal inputs after file resolution and hash verification.
///
/// `mirrored_policies` must contain an exact port/starboard bank-sign mirror.
/// One continuation realization is shared by the pair, so the mirror changes
/// only the terminal conditional family and not the preceding powered path.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct BroadTerminalPropagationConfigV1 {
    pub time_origin_unix_s_utc: f64,
    pub final_powered_bound: Seconds,
    pub continuation_draws_per_parent: u32,
    pub apu_accessible_reserved_fuel: Kilograms,
    pub ocxo_restart_count: u32,
    pub restart_transient: RestartTransientFamily,
    pub mirrored_policies: [ControlledToUncontrolledPolicy; 2],
    pub aerodynamics: AerodynamicModel,
    pub fallback_atmosphere: AtmosphereProfile,
    pub apu_start_policy: ApuStartPolicy,
    pub integration: IntegrationSettings,
    pub environment_family_id: String,
    pub environment_input_sha256: BTreeMap<String, String>,
    pub r600_contact: ExactTimeSatcomContact,
    pub satcom: SatcomModelConfig,
    pub upstream_evidence_mappings: Vec<BroadUpstreamEvidenceMappingV1>,
}

/// Dynamic terminal atmosphere plus the air-temperature quantity needed to
/// convert the broad state's Mach number at exact exhaustion to true airspeed.
pub(crate) trait BroadTerminalEnvironment: TransitionAtmosphere {
    fn speed_of_sound_m_s(
        &self,
        time: Seconds,
        position: mh370_domain::LatLon,
        pressure_altitude: Feet,
    ) -> std::result::Result<f64, TransitionAtmosphereError>;
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(tag = "chronology", rename_all = "snake_case")]
pub(crate) enum BroadPoweredTerminalPathV1 {
    EndedNoLaterThanR600 {
        result: Box<BroadDualEngineExhaustionResult>,
    },
    ReachedR600 {
        state_at_r600: BroadFlightState,
        result_after_r600: Box<BroadDualEngineExhaustionResult>,
    },
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct BroadTerminalTransitionRecordV1 {
    pub identity: BroadTerminalParticleIdentityV1,
    pub reconstructed_parent_state: BroadFlightState,
    pub powered_path: BroadPoweredTerminalPathV1,
    pub terminal_policy: ControlledToUncontrolledPolicy,
    pub exhaustion_boundary: Option<ExactDualExhaustionBoundary>,
    pub end_of_flight: Option<ControlledToUncontrolledAttempt>,
    pub r600_fit: Option<ExactTimeSatcomContactFit>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub(crate) struct BroadTerminalTransitionSidecarV1 {
    pub schema_id: String,
    pub schema_version: u32,
    pub parent_handoff_sha256: String,
    pub parent_run_identity_sha256: String,
    pub terminal_family_id: String,
    pub terminal_seed: u64,
    pub propagation: BroadTerminalPropagationConfigV1,
    pub records: Vec<BroadTerminalTransitionRecordV1>,
    pub limitations: Vec<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub(crate) struct BroadTerminalBuildArtifactsV1 {
    pub handoff: BroadImpactHandoffV1,
    pub sidecar: BroadTerminalTransitionSidecarV1,
    /// Exact pretty-JSON bytes, including the final newline, whose SHA-256 is
    /// recorded in `handoff.run.transition_sidecar_sha256`.
    pub sidecar_bytes: Vec<u8>,
}

#[derive(Serialize)]
struct RunIdentityPreimage<'a> {
    domain: &'static str,
    hypothesis_id: &'a str,
    producer_executable_sha256: &'a str,
    config_sha256: &'a str,
    input_sha256: &'a BTreeMap<String, String>,
    model_sha256: &'a crate::broad_impact_handoff::BroadImpactModelHashesV1,
    code_revision: &'a str,
    terminal_seed: u64,
    parent_handoff_sha256: &'a str,
    parent_run_identity_sha256: &'a str,
    terminal_family_id: &'a str,
    terminal_family_config_sha256: &'a str,
    transition_sidecar_sha256: &'a str,
}

/// Build the terminal artifact using the canonical broad-flight model.
///
/// The keyed continuation stream is shared by the two mirrored terminal
/// policies. Different continuation indices receive disjoint deterministic
/// streams. No fuel quantity is adjusted to make a path exhaust near R600.
pub(crate) fn build_broad_terminal_with_model<E: BroadTerminalEnvironment>(
    parent: &BroadPosteriorHandoffV1,
    template: BroadImpactHandoffV1,
    propagation: BroadTerminalPropagationConfigV1,
    powered_model: &BroadFlightModel<'_>,
    terminal_environment: &E,
) -> Result<BroadTerminalBuildArtifactsV1> {
    let r600_relative = template.r600_evidence.time_utc_unix_s - propagation.time_origin_unix_s_utc;
    let final_bound = propagation.final_powered_bound;
    let terminal_seed = template.run.terminal_seed;
    build_broad_terminal_with_continuation(
        parent,
        template,
        propagation,
        terminal_environment,
        |source, continuation_index| {
            let mut rng = rng_for(
                terminal_seed,
                "broad-terminal-powered-continuation",
                0,
                source.identity.particle,
                u64::from(continuation_index),
            );
            let initial = source.to_broad_flight_state();
            let first = powered_model
                .continue_to_exact_dual_engine_exhaustion(
                    &initial,
                    Seconds(r600_relative),
                    &mut rng,
                )
                .context("powered continuation to exact R600 failed")?;
            if first.outcome == BroadDualEngineExhaustionOutcome::NoExhaustionByBound {
                if (first.state.powered_flight.aircraft.time.0 - r600_relative).abs()
                    > TIME_TOLERANCE_S
                {
                    bail!("powered continuation did not end at exact R600");
                }
                let second = powered_model
                    .continue_to_exact_dual_engine_exhaustion(&first.state, final_bound, &mut rng)
                    .context("powered continuation after exact R600 failed")?;
                Ok(BroadPoweredTerminalPathV1::ReachedR600 {
                    state_at_r600: first.state,
                    result_after_r600: Box::new(second),
                })
            } else {
                Ok(BroadPoweredTerminalPathV1::EndedNoLaterThanR600 {
                    result: Box::new(first),
                })
            }
        },
    )
}

/// Terminal continuation does not yet implement the schema-2 requirement to
/// independently refresh selected pending clocks for every continuation draw.
/// Keep this at the in-memory builder boundary so no caller can silently reuse
/// the filtering artifact's disposable future randomness.
pub(crate) fn reject_pending_renewal_refresh_parent(
    parent: &BroadPosteriorHandoffV1,
) -> Result<()> {
    if parent.run.pending_renewal_refresh.is_some() {
        bail!(
            "broad-terminal inference cannot consume a pending-renewal-refresh parent until every independent continuation draw refreshes the configured clocks before propagation"
        );
    }
    Ok(())
}

#[allow(clippy::too_many_arguments)]
fn build_broad_terminal_with_continuation<E, F>(
    parent: &BroadPosteriorHandoffV1,
    mut handoff: BroadImpactHandoffV1,
    propagation: BroadTerminalPropagationConfigV1,
    terminal_environment: &E,
    mut continuation: F,
) -> Result<BroadTerminalBuildArtifactsV1>
where
    E: BroadTerminalEnvironment,
    F: FnMut(&BroadPosteriorHandoffParticleV1, u32) -> Result<BroadPoweredTerminalPathV1>,
{
    parent
        .validate()
        .context("invalid broad posterior parent handoff")?;
    reject_pending_renewal_refresh_parent(parent)?;
    validate_and_bind_header(parent, &mut handoff, &propagation)?;

    let draws_per_parent = propagation
        .continuation_draws_per_parent
        .checked_mul(2)
        .context("terminal draw count overflow")?;
    let draw_log_probability = -(f64::from(draws_per_parent)).ln();
    let r600_relative = handoff.r600_evidence.time_utc_unix_s - propagation.time_origin_unix_s_utc;

    let mut particles = Vec::with_capacity(
        parent
            .particles
            .len()
            .saturating_mul(draws_per_parent as usize),
    );
    let mut records = Vec::with_capacity(particles.capacity());
    for source in &parent.particles {
        let reconstructed = source.to_broad_flight_state();
        for continuation_index in 0..propagation.continuation_draws_per_parent {
            let powered_path = continuation(source, continuation_index)?;
            for (mirror_index, policy) in propagation.mirrored_policies.iter().enumerate() {
                let draw_id = continuation_index
                    .checked_mul(2)
                    .and_then(|value| value.checked_add(mirror_index as u32))
                    .context("terminal draw identity overflow")?;
                let identity = BroadTerminalParticleIdentityV1 {
                    parent: source.identity.clone(),
                    prior_root: source.prior_root.clone(),
                    stratum: source.stratum,
                    terminal_draw: BroadTerminalDrawIdentityV1 {
                        terminal_seed: handoff.run.terminal_seed,
                        terminal_family_id: handoff.terminal_family.id.clone(),
                        draw_id,
                    },
                };
                let executed = execute_terminal_draw(
                    reconstructed,
                    powered_path.clone(),
                    policy,
                    &propagation,
                    terminal_environment,
                    r600_relative,
                )?;
                let logon_timing = terminal_timing_evidence(
                    &handoff.terminal_evidence_model,
                    &executed.r600,
                    executed.exhaustion_time_relative,
                    executed.outcome,
                    propagation.time_origin_unix_s_utc,
                    r600_relative,
                )?;
                particles.push(BroadTerminalParticleV1 {
                    identity: identity.clone(),
                    upstream_normalized_log_weight: source.normalized_log_weight,
                    terminal_draw_log_probability: draw_log_probability,
                    continuation_log_prior_over_proposal: 0.0,
                    terminal_time_utc_unix_s: propagation.time_origin_unix_s_utc
                        + executed.terminal_time_relative.0,
                    r600: executed.r600,
                    logon_timing,
                    posterior_normalized_log_weight: None,
                    outcome: executed.outcome,
                    impact: executed.impact,
                });
                records.push(BroadTerminalTransitionRecordV1 {
                    identity,
                    reconstructed_parent_state: reconstructed,
                    powered_path: powered_path.clone(),
                    terminal_policy: policy.clone(),
                    exhaustion_boundary: executed.exhaustion_boundary,
                    end_of_flight: executed.end_of_flight,
                    r600_fit: executed.r600_fit,
                });
            }
        }
    }

    let sidecar = BroadTerminalTransitionSidecarV1 {
        schema_id: SIDECAR_SCHEMA_ID.to_string(),
        schema_version: SIDECAR_SCHEMA_VERSION,
        parent_handoff_sha256: handoff.parent.handoff_sha256.clone(),
        parent_run_identity_sha256: parent.run.run_identity_sha256.clone(),
        terminal_family_id: handoff.terminal_family.id.clone(),
        terminal_seed: handoff.run.terminal_seed,
        propagation,
        records,
        limitations: vec![
            "terminal families are conditional alternatives, not calibrated frequencies"
                .to_string(),
            "mirrored terminal policies share the same powered continuation realization"
                .to_string(),
            "R600 BTO is the only central terminal weight update; BFO is not scored".to_string(),
            "the optional Erlang branch is conditional on a successful APU/SDU restart chain and is not an independent exhaustion window"
                .to_string(),
            "impact attitude and water-contact duration remain unresolved".to_string(),
        ],
    };
    let sidecar_bytes = pretty_json_bytes(&sidecar)?;
    handoff.run.transition_sidecar_sha256 = sha256_bytes(&sidecar_bytes);

    normalize_terminal_particles(&mut handoff, &mut particles)?;
    handoff.outcome_mass = outcome_mass(&particles)?;
    handoff.particles = particles;
    handoff.run.run_identity_sha256 = terminal_run_identity(&handoff)?;
    handoff
        .validate()
        .context("constructed broad terminal handoff failed validation")?;

    Ok(BroadTerminalBuildArtifactsV1 {
        handoff,
        sidecar,
        sidecar_bytes,
    })
}

struct ExecutedTerminalDraw {
    outcome: BroadTerminalOutcomeV1,
    terminal_time_relative: Seconds,
    exhaustion_time_relative: Option<Seconds>,
    r600: BroadR600ParticleEvidenceV1,
    r600_fit: Option<ExactTimeSatcomContactFit>,
    impact: Option<BroadImpactDataV1>,
    exhaustion_boundary: Option<ExactDualExhaustionBoundary>,
    end_of_flight: Option<ControlledToUncontrolledAttempt>,
}

fn execute_terminal_draw<E: BroadTerminalEnvironment>(
    parent_state: BroadFlightState,
    path: BroadPoweredTerminalPathV1,
    policy: &ControlledToUncontrolledPolicy,
    config: &BroadTerminalPropagationConfigV1,
    environment: &E,
    r600_relative: f64,
) -> Result<ExecutedTerminalDraw> {
    match path {
        BroadPoweredTerminalPathV1::EndedNoLaterThanR600 { result } => {
            let result = *result;
            match result.outcome {
                BroadDualEngineExhaustionOutcome::Exhausted => {
                    let checkpoint_elapsed = Seconds(r600_relative - result.state.fuel.time.0);
                    execute_from_exhaustion(
                        parent_state,
                        result,
                        policy,
                        config,
                        environment,
                        Some(checkpoint_elapsed),
                    )
                }
                BroadDualEngineExhaustionOutcome::AlreadyExhaustedBeforeStart => {
                    Ok(powered_only_outcome(
                        result,
                        BroadTerminalOutcomeV1::AlreadyExhaustedBeforeCheckpoint,
                        BroadR600ZeroSupportReasonV1::DidNotReachEpoch,
                    ))
                }
                BroadDualEngineExhaustionOutcome::NoExhaustionByBound => {
                    bail!("internal chronology mismatch before R600")
                }
                BroadDualEngineExhaustionOutcome::TrajectoryRejected => {
                    let reason = rejection_reason(result.state)?;
                    Ok(powered_only_outcome(
                        result,
                        BroadTerminalOutcomeV1::PoweredContinuationRejected { reason },
                        BroadR600ZeroSupportReasonV1::RejectedBeforeEpoch,
                    ))
                }
                BroadDualEngineExhaustionOutcome::FuelModelUnavailable => Ok(powered_only_outcome(
                    result,
                    BroadTerminalOutcomeV1::FuelModelUnavailable,
                    BroadR600ZeroSupportReasonV1::RejectedBeforeEpoch,
                )),
            }
        }
        BroadPoweredTerminalPathV1::ReachedR600 {
            state_at_r600,
            result_after_r600,
        } => {
            let result_after_r600 = *result_after_r600;
            let (r600, r600_fit) = score_powered_r600(state_at_r600, config, r600_relative)?;
            match result_after_r600.outcome {
                BroadDualEngineExhaustionOutcome::Exhausted => {
                    let mut executed = execute_from_exhaustion(
                        parent_state,
                        result_after_r600,
                        policy,
                        config,
                        environment,
                        None,
                    )?;
                    executed.r600 = r600;
                    executed.r600_fit = r600_fit;
                    Ok(executed)
                }
                BroadDualEngineExhaustionOutcome::NoExhaustionByBound => {
                    Ok(powered_after_r600_outcome(
                        result_after_r600,
                        BroadTerminalOutcomeV1::NoExhaustionByBound,
                        r600,
                        r600_fit,
                    ))
                }
                BroadDualEngineExhaustionOutcome::TrajectoryRejected => {
                    let reason = rejection_reason(result_after_r600.state)?;
                    Ok(powered_after_r600_outcome(
                        result_after_r600,
                        BroadTerminalOutcomeV1::PoweredContinuationRejected { reason },
                        r600,
                        r600_fit,
                    ))
                }
                BroadDualEngineExhaustionOutcome::FuelModelUnavailable => {
                    Ok(powered_after_r600_outcome(
                        result_after_r600,
                        BroadTerminalOutcomeV1::FuelModelUnavailable,
                        r600,
                        r600_fit,
                    ))
                }
                BroadDualEngineExhaustionOutcome::AlreadyExhaustedBeforeStart => {
                    Ok(powered_after_r600_outcome(
                        result_after_r600,
                        BroadTerminalOutcomeV1::AlreadyExhaustedBeforeCheckpoint,
                        r600,
                        r600_fit,
                    ))
                }
            }
        }
    }
}

fn execute_from_exhaustion<E: BroadTerminalEnvironment>(
    parent_state: BroadFlightState,
    exhaustion: BroadDualEngineExhaustionResult,
    policy: &ControlledToUncontrolledPolicy,
    config: &BroadTerminalPropagationConfigV1,
    environment: &E,
    r600_checkpoint_elapsed: Option<Seconds>,
) -> Result<ExecutedTerminalDraw> {
    let state = exhaustion.state;
    let sound_speed = environment
        .speed_of_sound_m_s(
            state.powered_flight.aircraft.time,
            state.powered_flight.aircraft.position,
            state.powered_flight.aircraft.altitude,
        )
        .context("terminal environment cannot supply boundary sound speed")?;
    if !sound_speed.is_finite() || sound_speed <= 0.0 {
        bail!("terminal environment supplied invalid sound speed");
    }
    let boundary = exact_dual_exhaustion_boundary(ExactDualExhaustionBoundaryInput {
        aircraft: state.powered_flight.aircraft,
        heading_true: state.powered_flight.heading_true,
        true_airspeed: MetresPerSecond(state.powered_flight.mach * sound_speed),
        powered_fuel: state.fuel,
        apu_accessible_reserved_fuel: config.apu_accessible_reserved_fuel,
        ocxo_restart_count: config.ocxo_restart_count,
    })
    .context("cannot map exact powered exhaustion boundary")?;
    let input = TransitionKernelInput {
        initial: boundary.initial.clone(),
        family: ConditionalModelFamily {
            control: ControlFamily::Controlled,
            restart_transient: config.restart_transient,
        },
        model_weight: ModelWeight(1.0),
        control: policy.pre_trigger_controlled.clone(),
        aerodynamics: config.aerodynamics,
        atmosphere: config.fallback_atmosphere.clone(),
        apu_start_policy: config.apu_start_policy,
        integration: config.integration,
    };
    let schedule = ExactTimeCheckpointSchedule {
        requested_elapsed_times: r600_checkpoint_elapsed.into_iter().collect(),
    };
    let attempt = attempt_controlled_to_uncontrolled_with_atmosphere_and_checkpoints(
        &input,
        policy,
        &schedule,
        environment,
    )
    .context("end-of-flight transition failed")?;
    let (r600, r600_fit) = match r600_checkpoint_elapsed {
        Some(_) => score_terminal_checkpoint(
            attempt.checkpoints.first(),
            attempt.transition.terminal.kinematics.point_mass.time,
            parent_state,
            config,
        )?,
        None => (
            BroadR600ParticleEvidenceV1::ZeroSupport {
                reason: BroadR600ZeroSupportReasonV1::DidNotReachEpoch,
            },
            None,
        ),
    };
    let (outcome, impact) = match attempt.transition.impact.clone() {
        Some(impact) => (
            BroadTerminalOutcomeV1::Impact,
            Some(convert_impact(
                impact,
                attempt.transition.terminal.kinematics.ground_track_true,
                config.time_origin_unix_s_utc,
            )),
        ),
        None => (
            BroadTerminalOutcomeV1::EndOfFlightNonImpact {
                termination: attempt.transition.termination,
            },
            None,
        ),
    };
    Ok(ExecutedTerminalDraw {
        outcome,
        terminal_time_relative: attempt.transition.terminal.kinematics.point_mass.time,
        exhaustion_time_relative: Some(state.fuel.time),
        r600,
        r600_fit,
        impact,
        exhaustion_boundary: Some(boundary),
        end_of_flight: Some(attempt),
    })
}

fn score_terminal_checkpoint(
    checkpoint: Option<&ExactTimeCheckpoint>,
    terminal_time: Seconds,
    parent_state: BroadFlightState,
    config: &BroadTerminalPropagationConfigV1,
) -> Result<(
    BroadR600ParticleEvidenceV1,
    Option<ExactTimeSatcomContactFit>,
)> {
    let Some(checkpoint) = checkpoint else {
        return Ok((
            BroadR600ParticleEvidenceV1::ZeroSupport {
                reason: BroadR600ZeroSupportReasonV1::DidNotReachEpoch,
            },
            None,
        ));
    };
    if !checkpoint.state.electrical.satcom_powered {
        return Ok((
            BroadR600ParticleEvidenceV1::ZeroSupport {
                reason: BroadR600ZeroSupportReasonV1::SatcomUnpowered,
            },
            None,
        ));
    }
    let aircraft = aircraft_from_terminal_checkpoint(
        checkpoint,
        parent_state.bfo_bias.mean_hz,
        config.time_origin_unix_s_utc,
    );
    let fit = score_exact_time_satcom_contact(
        aircraft,
        parent_state.bfo_bias,
        config.r600_contact,
        &config.satcom,
    )
    .context("cannot score exact R600 end-of-flight checkpoint")?;
    if terminal_time.0 + TIME_TOLERANCE_S < checkpoint.state.kinematics.point_mass.time.0 {
        bail!("terminal transition ends before its retained checkpoint");
    }
    Ok((r600_evidence(fit), Some(fit)))
}

fn score_powered_r600(
    state: BroadFlightState,
    config: &BroadTerminalPropagationConfigV1,
    r600_relative: f64,
) -> Result<(
    BroadR600ParticleEvidenceV1,
    Option<ExactTimeSatcomContactFit>,
)> {
    if (state.powered_flight.aircraft.time.0 - r600_relative).abs() > TIME_TOLERANCE_S {
        bail!("powered R600 state is not at the exact contact epoch");
    }
    let mut aircraft = state.powered_flight.aircraft;
    aircraft.time = Seconds(config.time_origin_unix_s_utc + aircraft.time.0);
    let fit = score_exact_time_satcom_contact(
        aircraft,
        state.bfo_bias,
        config.r600_contact,
        &config.satcom,
    )
    .context("cannot score exact powered R600 state")?;
    Ok((r600_evidence(fit), Some(fit)))
}

fn aircraft_from_terminal_checkpoint(
    checkpoint: &ExactTimeCheckpoint,
    bfo_bias_hz: f64,
    time_origin_unix_s: f64,
) -> AircraftState {
    let state = &checkpoint.state.kinematics;
    AircraftState {
        time: Seconds(time_origin_unix_s + state.point_mass.time.0),
        position: state.point_mass.position,
        altitude: state.point_mass.altitude,
        track_true: state.ground_track_true,
        ground_speed: Knots(state.ground_speed.0 / MPS_PER_KNOT),
        vertical_speed: FeetPerMinute(state.vertical_speed.0 / MPS_PER_FPM),
        bfo_bias: Hertz(bfo_bias_hz),
    }
}

fn r600_evidence(fit: ExactTimeSatcomContactFit) -> BroadR600ParticleEvidenceV1 {
    BroadR600ParticleEvidenceV1::Scored {
        predicted_bto_us: fit.bto.predicted.0,
        residual_observed_minus_predicted_us: fit.bto.residual.0,
        log_likelihood: fit.bto.log_likelihood,
    }
}

fn powered_only_outcome(
    result: BroadDualEngineExhaustionResult,
    outcome: BroadTerminalOutcomeV1,
    reason: BroadR600ZeroSupportReasonV1,
) -> ExecutedTerminalDraw {
    ExecutedTerminalDraw {
        outcome,
        terminal_time_relative: result.state.powered_flight.aircraft.time,
        exhaustion_time_relative: result.exhaustion_time,
        r600: BroadR600ParticleEvidenceV1::ZeroSupport { reason },
        r600_fit: None,
        impact: None,
        exhaustion_boundary: None,
        end_of_flight: None,
    }
}

fn powered_after_r600_outcome(
    result: BroadDualEngineExhaustionResult,
    outcome: BroadTerminalOutcomeV1,
    r600: BroadR600ParticleEvidenceV1,
    r600_fit: Option<ExactTimeSatcomContactFit>,
) -> ExecutedTerminalDraw {
    ExecutedTerminalDraw {
        outcome,
        terminal_time_relative: result.state.powered_flight.aircraft.time,
        exhaustion_time_relative: result.exhaustion_time,
        r600,
        r600_fit,
        impact: None,
        exhaustion_boundary: None,
        end_of_flight: None,
    }
}

fn rejection_reason(state: BroadFlightState) -> Result<mh370_estimator::BroadRejectionReason> {
    match state.status {
        mh370_estimator::BroadFlightParticleStatus::Rejected { reason, .. } => Ok(reason),
        mh370_estimator::BroadFlightParticleStatus::Active => {
            bail!("trajectory-rejected outcome retained an active state")
        }
    }
}

fn convert_impact(
    impact: mh370_end_of_flight::ImpactData,
    ground_track_true: mh370_domain::Degrees,
    time_origin_unix_s: f64,
) -> BroadImpactDataV1 {
    let track = ground_track_true.to_radians();
    BroadImpactDataV1 {
        time_utc_unix_s: time_origin_unix_s + impact.point.time.0,
        position_wgs84: impact.point.position,
        true_airspeed_m_s: impact.true_airspeed.0,
        ground_velocity_enu_m_s: EnuVelocityV1 {
            east: impact.ground_speed.0 * track.sin(),
            north: impact.ground_speed.0 * track.cos(),
            up: impact.vertical_speed.0,
        },
        impact_angle_below_horizontal_deg: impact.impact_angle.0,
        mass_kg: impact.mass.0,
        energy: ImpactEnergyV1 {
            total_j: impact.kinetic_energy.0,
            horizontal_j: impact.horizontal_kinetic_energy.0,
            vertical_j: impact.vertical_kinetic_energy.0,
        },
        attitude: None,
        contact_duration_s: None,
    }
}

fn terminal_timing_evidence(
    model: &BroadTerminalEvidenceModelV1,
    r600: &BroadR600ParticleEvidenceV1,
    exhaustion_relative: Option<Seconds>,
    outcome: BroadTerminalOutcomeV1,
    time_origin_unix_s: f64,
    r600_relative: f64,
) -> Result<Option<BroadLogonTimingParticleEvidenceV1>> {
    if matches!(model, BroadTerminalEvidenceModelV1::R600BtoOnly)
        || !matches!(r600, BroadR600ParticleEvidenceV1::Scored { .. })
    {
        return Ok(None);
    }
    let BroadTerminalEvidenceModelV1::JointR600BtoAndLogonTiming {
        erlang_shape,
        erlang_rate_per_s,
        ..
    } = model
    else {
        unreachable!();
    };
    let Some(exhaustion) = exhaustion_relative else {
        return Ok(Some(BroadLogonTimingParticleEvidenceV1::ZeroSupport {
            reason: timing_zero_support_reason(outcome)?,
        }));
    };
    if exhaustion.0 >= r600_relative - TIME_TOLERANCE_S {
        return Ok(Some(BroadLogonTimingParticleEvidenceV1::ZeroSupport {
            reason: BroadLogonTimingZeroSupportReasonV1::ExhaustionAtOrAfterLogonRequest,
        }));
    }
    let scale = Seconds(1.0 / *erlang_rate_per_s);
    let timing = conditional_successful_apu_sdu_logon_lag_likelihood(
        SuccessfulApuSduErlangLagConfig {
            shape: *erlang_shape,
            scale,
        },
        ConditionalSuccessfulApuSduTimingInput {
            observed_r600_logon_time: R600ObservedLogonTime {
                absolute_utc_posix_seconds: UtcPosixSeconds(time_origin_unix_s + r600_relative),
                relative_seconds: Seconds(r600_relative),
                relative_epoch_utc_posix_seconds: UtcPosixSeconds(time_origin_unix_s),
            },
            dual_generator_loss_relative_seconds: exhaustion,
        },
    )
    .context("invalid conditional R600 timing model")?;
    if timing.support != ConditionalLagSupport::PositiveLag
        || !timing.normalized_log_density_per_second.is_finite()
    {
        bail!("positive pre-R600 exhaustion produced no timing support");
    }
    Ok(Some(BroadLogonTimingParticleEvidenceV1::Scored {
        dual_engine_exhaustion_time_utc_unix_s: time_origin_unix_s + exhaustion.0,
        logon_request_lag_s: timing.lag.0,
        log_likelihood: timing.normalized_log_density_per_second,
    }))
}

fn timing_zero_support_reason(
    outcome: BroadTerminalOutcomeV1,
) -> Result<BroadLogonTimingZeroSupportReasonV1> {
    match outcome {
        BroadTerminalOutcomeV1::NoExhaustionByBound => {
            Ok(BroadLogonTimingZeroSupportReasonV1::NoExhaustionByBound)
        }
        BroadTerminalOutcomeV1::PoweredContinuationRejected { .. } => {
            Ok(BroadLogonTimingZeroSupportReasonV1::ContinuationRejectedBeforeExhaustion)
        }
        BroadTerminalOutcomeV1::FuelModelUnavailable => {
            Ok(BroadLogonTimingZeroSupportReasonV1::FuelModelUnavailable)
        }
        BroadTerminalOutcomeV1::AlreadyExhaustedBeforeCheckpoint => {
            Ok(BroadLogonTimingZeroSupportReasonV1::AlreadyExhaustedBeforeCheckpoint)
        }
        BroadTerminalOutcomeV1::Impact | BroadTerminalOutcomeV1::EndOfFlightNonImpact { .. } => {
            bail!("terminal outcome requires an explicit exhaustion time")
        }
    }
}

fn validate_and_bind_header(
    parent: &BroadPosteriorHandoffV1,
    handoff: &mut BroadImpactHandoffV1,
    config: &BroadTerminalPropagationConfigV1,
) -> Result<()> {
    if handoff.schema_id != BROAD_IMPACT_HANDOFF_SCHEMA_ID
        || handoff.schema_version != BROAD_IMPACT_HANDOFF_SCHEMA_VERSION
        || !handoff.particles.is_empty()
        || config.continuation_draws_per_parent == 0
        || !config.time_origin_unix_s_utc.is_finite()
        || !config.final_powered_bound.is_finite()
        || config.environment_family_id.trim().is_empty()
        || config.environment_input_sha256.is_empty()
        || config.r600_contact.bfo.is_some()
    {
        bail!("invalid broad terminal build template or propagation configuration");
    }
    let contact_time =
        config.r600_contact.satellite_source_epoch.0 + config.r600_contact.satellite_delta.0;
    let r600_relative = handoff.r600_evidence.time_utc_unix_s - config.time_origin_unix_s_utc;
    if (contact_time - handoff.r600_evidence.time_utc_unix_s).abs() > TIME_TOLERANCE_S
        || config.r600_contact.observed_bto.0.to_bits()
            != handoff.r600_evidence.observed_bto_us.to_bits()
        || config.r600_contact.bto_standard_deviation.0.to_bits()
            != handoff.r600_evidence.standard_deviation_us.to_bits()
        || config.final_powered_bound.0 <= r600_relative
    {
        bail!("terminal bounds and exact R600 contact disagree");
    }
    validate_mirrored_policies(&config.mirrored_policies)?;

    let consumed_source = parent
        .evidence
        .entries()
        .iter()
        .filter(|entry| entry.disposition == BroadEvidenceDispositionV1::Consumed)
        .map(|entry| &entry.identity)
        .collect::<BTreeSet<_>>();
    let mapped_source = config
        .upstream_evidence_mappings
        .iter()
        .map(|mapping| &mapping.source)
        .collect::<BTreeSet<_>>();
    let mapped_downstream = config
        .upstream_evidence_mappings
        .iter()
        .map(|mapping| &mapping.downstream)
        .collect::<BTreeSet<_>>();
    if consumed_source != mapped_source
        || mapped_source.len() != config.upstream_evidence_mappings.len()
        || mapped_downstream.len() != config.upstream_evidence_mappings.len()
    {
        bail!("upstream evidence mapping is incomplete or duplicated");
    }

    handoff.parent.schema_version = parent.schema_version;
    handoff.parent.run_identity_sha256 = parent.run.run_identity_sha256.clone();
    handoff.parent.config_sha256 = parent.run.config_sha256.clone();
    handoff.parent.input_sha256 = parent.run.input_sha256.clone();
    handoff.parent.evidence_ledger_sha256 = sha256_bytes(&serde_json::to_vec(&parent.evidence)?);
    handoff.parent.consumed_evidence = config
        .upstream_evidence_mappings
        .iter()
        .map(|mapping| mapping.downstream.clone())
        .collect();
    handoff.parent.model_family = parent.run.model_family.clone();
    handoff.parent.seed = parent.run.seed;
    handoff.parent.checkpoint_id = parent.checkpoint.checkpoint_id.clone();
    handoff.parent.source_epoch_id = parent.run.source_epoch_id.clone();
    handoff.parent.checkpoint_time_unix_s_utc =
        config.time_origin_unix_s_utc + parent.checkpoint.state_time.0;
    handoff.parent.conditioning = parent.checkpoint.conditioning.clone();
    handoff.parent.configured_particle_count = parent.run.configured_particles;
    handoff.parent.retained_particle_count = parent.particles.len();
    handoff.outcome_mass = BroadOutcomeMassV1::default();
    Ok(())
}

fn validate_mirrored_policies(policies: &[ControlledToUncontrolledPolicy; 2]) -> Result<()> {
    let [left, right] = policies;
    if left.scenario.label.trim().is_empty()
        || right.scenario.label.trim().is_empty()
        || left.scenario.label == right.scenario.label
        || left.scenario.trigger != right.scenario.trigger
        || left.pre_trigger_controlled != right.pre_trigger_controlled
        || left.post_trigger_uncontrolled.segments.len()
            != right.post_trigger_uncontrolled.segments.len()
    {
        bail!("terminal policies are not a declared mirror pair");
    }
    for (left, right) in left
        .post_trigger_uncontrolled
        .segments
        .iter()
        .zip(&right.post_trigger_uncontrolled.segments)
    {
        if left.start_offset != right.start_offset || !mirrored_command(left.command, right.command)
        {
            bail!("terminal post-trigger schedules are not exact bank mirrors");
        }
    }
    Ok(())
}

fn mirrored_command(left: ControlCommand, right: ControlCommand) -> bool {
    match (left, right) {
        (
            ControlCommand::Uncontrolled {
                lift_coefficient: left_lift,
                bank_angle: left_bank,
            },
            ControlCommand::Uncontrolled {
                lift_coefficient: right_lift,
                bank_angle: right_bank,
            },
        ) => {
            left_lift.to_bits() == right_lift.to_bits()
                && (left_bank.0 + right_bank.0).abs() <= 1.0e-12
        }
        _ => false,
    }
}

fn normalize_terminal_particles(
    handoff: &mut BroadImpactHandoffV1,
    particles: &mut [BroadTerminalParticleV1],
) -> Result<()> {
    let pre = particles
        .iter()
        .map(|particle| {
            particle.upstream_normalized_log_weight
                + particle.terminal_draw_log_probability
                + particle.continuation_log_prior_over_proposal
        })
        .collect::<Vec<_>>();
    let (_, pre_normalizer) = normalize_log_weights(&pre)?;
    let raw = particles
        .iter()
        .map(|particle| {
            terminal_particle_log_likelihood(&handoff.terminal_evidence_model, particle)
                .map(|increment| {
                    particle.upstream_normalized_log_weight
                        + particle.terminal_draw_log_probability
                        + particle.continuation_log_prior_over_proposal
                        + increment
                })
                .unwrap_or(f64::NEG_INFINITY)
        })
        .collect::<Vec<_>>();
    let (normalized, posterior_normalizer) = normalize_log_weights(&raw)
        .context("no terminal particle has support under the selected evidence branch")?;
    for (particle, normalized) in particles.iter_mut().zip(normalized) {
        particle.posterior_normalized_log_weight = normalized.is_finite().then_some(normalized);
    }
    let application = handoff
        .evidence
        .applications
        .iter_mut()
        .find(|application| application.id == handoff.r600_evidence.application_id)
        .context("R600 evidence application is absent from the template ledger")?;
    if application.role != EvidenceApplicationRoleV1::WeightUpdate {
        bail!("R600 application is not the sole terminal weight update");
    }
    application.log_evidence_increment = Some(posterior_normalizer - pre_normalizer);
    Ok(())
}

fn terminal_particle_log_likelihood(
    model: &BroadTerminalEvidenceModelV1,
    particle: &BroadTerminalParticleV1,
) -> Option<f64> {
    let bto = match particle.r600 {
        BroadR600ParticleEvidenceV1::Scored { log_likelihood, .. } => log_likelihood,
        BroadR600ParticleEvidenceV1::ZeroSupport { .. } => return None,
    };
    match model {
        BroadTerminalEvidenceModelV1::R600BtoOnly => Some(bto),
        BroadTerminalEvidenceModelV1::JointR600BtoAndLogonTiming { .. } => {
            match particle.logon_timing {
                Some(BroadLogonTimingParticleEvidenceV1::Scored { log_likelihood, .. }) => {
                    Some(bto + log_likelihood)
                }
                Some(BroadLogonTimingParticleEvidenceV1::ZeroSupport { .. }) | None => None,
            }
        }
    }
}

fn outcome_mass(particles: &[BroadTerminalParticleV1]) -> Result<BroadOutcomeMassV1> {
    let pre = particles
        .iter()
        .map(|particle| {
            particle.upstream_normalized_log_weight
                + particle.terminal_draw_log_probability
                + particle.continuation_log_prior_over_proposal
        })
        .collect::<Vec<_>>();
    let (_, pre_normalizer) = normalize_log_weights(&pre)?;
    let mut result = BroadOutcomeMassV1::default();
    for (particle, pre_weight) in particles.iter().zip(pre) {
        let cell = outcome_cell_mut(&mut result, particle.outcome);
        cell.draw_count += 1;
        cell.pre_r600_normalized_mass += (pre_weight - pre_normalizer).exp();
        cell.posterior_normalized_mass += particle
            .posterior_normalized_log_weight
            .map_or(0.0, f64::exp);
    }
    Ok(result)
}

fn outcome_cell_mut(
    mass: &mut BroadOutcomeMassV1,
    outcome: BroadTerminalOutcomeV1,
) -> &mut BroadOutcomeMassCellV1 {
    match outcome {
        BroadTerminalOutcomeV1::Impact => &mut mass.impact,
        BroadTerminalOutcomeV1::NoExhaustionByBound => &mut mass.no_exhaustion_by_bound,
        BroadTerminalOutcomeV1::PoweredContinuationRejected { .. } => &mut mass.rejected,
        BroadTerminalOutcomeV1::FuelModelUnavailable => &mut mass.fuel_model_unavailable,
        BroadTerminalOutcomeV1::AlreadyExhaustedBeforeCheckpoint => {
            &mut mass.already_exhausted_before_checkpoint
        }
        BroadTerminalOutcomeV1::EndOfFlightNonImpact { .. } => &mut mass.end_of_flight_non_impact,
    }
}

fn pretty_json_bytes(value: &impl Serialize) -> Result<Vec<u8>> {
    let mut bytes = serde_json::to_vec_pretty(value)?;
    bytes.push(b'\n');
    Ok(bytes)
}

fn terminal_run_identity(handoff: &BroadImpactHandoffV1) -> Result<String> {
    Ok(sha256_bytes(&serde_json::to_vec(&RunIdentityPreimage {
        domain: "mh370-broad-terminal-run-v1",
        hypothesis_id: &handoff.run.hypothesis_id,
        producer_executable_sha256: &handoff.run.producer_executable_sha256,
        config_sha256: &handoff.run.config_sha256,
        input_sha256: &handoff.run.input_sha256,
        model_sha256: &handoff.run.model_sha256,
        code_revision: &handoff.run.code_revision,
        terminal_seed: handoff.run.terminal_seed,
        parent_handoff_sha256: &handoff.parent.handoff_sha256,
        parent_run_identity_sha256: &handoff.parent.run_identity_sha256,
        terminal_family_id: &handoff.terminal_family.id,
        terminal_family_config_sha256: &handoff.terminal_family.config_sha256,
        transition_sidecar_sha256: &handoff.run.transition_sidecar_sha256,
    })?))
}

#[cfg(test)]
mod tests {
    use mh370_domain::{Degrees, LatLon, Microseconds, Vec3};
    use mh370_dynamics::{
        PendingRenewal, PoweredEventClocks, PoweredEventCounters, PoweredFlightCommand,
        PoweredFlightState, PoweredLateralMode,
    };
    use mh370_end_of_flight::{
        AtmosphereNode, ControlSegment, ControlTransitionTrigger, ControlledToUncontrolledScenario,
        KilogramsPerCubicMetre, KilogramsPerSecond, PoweredFuelState, SquareMetres,
        TransitionAtmosphereSample,
    };
    use mh370_estimator::{
        BroadCheckpointMetadataV1, BroadConditioningSemanticsV1, BroadEvidenceComponentV1,
        BroadEvidenceEntryV1, BroadEvidenceLedgerV1, BroadEvidenceStateEffectV1,
        BroadFlightDiagnostics, BroadFlightParticleStatus, BroadFlightScores,
        BroadFuelDiagnosticStatus, BroadParticleEvidenceScoreV1, BroadPendingRenewalRefreshConfig,
        BroadPosteriorParticleIdentityV1, BroadPriorRootIdentityV1, BroadRunMetadataV1,
        BroadStratumMetadataV1, BROAD_POSTERIOR_HANDOFF_SCHEMA_VERSION,
    };
    use mh370_particle_filter::StratumId;
    use mh370_satcom::{
        BfoBiasState, BfoConstants, BtoConstants, SatelliteEcefPropagationLimit, SatelliteEcefState,
    };

    use super::*;
    use crate::broad_impact_handoff::{
        BroadImpactModelHashesV1, BroadImpactParentV1, BroadImpactRunProvenanceV1,
        BroadR600EvidenceV1, BroadTerminalFamilyV1, BroadTerminalModelHashesV1,
    };
    use crate::impact_handoff::{
        AbsoluteTimeBasisV1, EvidenceApplicationV1, EvidenceDispositionV2, EvidenceEntryV2,
        EvidenceLedgerV2,
    };

    const ORIGIN: f64 = 1_394_215_309.0;
    const M0011: f64 = 22_150.0;
    const R600: f64 = 22_660.416;

    #[derive(Debug)]
    struct ConstantEnvironment;

    impl TransitionAtmosphere for ConstantEnvironment {
        fn sample(
            &self,
            _time: Seconds,
            _position: LatLon,
            _pressure_altitude: Feet,
        ) -> std::result::Result<TransitionAtmosphereSample, TransitionAtmosphereError> {
            Ok(TransitionAtmosphereSample {
                density: KilogramsPerCubicMetre(0.38),
                wind_north: MetresPerSecond(0.0),
                wind_east: MetresPerSecond(0.0),
            })
        }
    }

    impl BroadTerminalEnvironment for ConstantEnvironment {
        fn speed_of_sound_m_s(
            &self,
            _time: Seconds,
            _position: LatLon,
            _pressure_altitude: Feet,
        ) -> std::result::Result<f64, TransitionAtmosphereError> {
            Ok(295.0)
        }
    }

    fn digest(byte: char) -> String {
        std::iter::repeat(byte).take(64).collect()
    }

    fn powered_state(time: f64, bias: f64) -> PoweredFlightState {
        PoweredFlightState {
            aircraft: AircraftState {
                time: Seconds(time),
                position: LatLon::new(-35.0, 90.0).unwrap(),
                altitude: Feet(35_000.0),
                track_true: Degrees(180.0),
                ground_speed: Knots(470.0),
                vertical_speed: FeetPerMinute(0.0),
                bfo_bias: Hertz(bias),
            },
            heading_true: Degrees(180.0),
            mach: 0.78,
            bank_angle: Degrees(0.0),
            command: PoweredFlightCommand {
                lateral_mode: PoweredLateralMode::ConstantTrueTrack,
                selected_control: Degrees(180.0),
                great_circle_destination: None,
                target_mach: 0.78,
                target_pressure_altitude: Feet(35_000.0),
            },
            event_clocks: PoweredEventClocks {
                lateral: None,
                speed: None,
                altitude: None,
            },
            event_counters: PoweredEventCounters::default(),
        }
    }

    fn fuel(time: f64, exhausted: bool) -> PoweredFuelState {
        if exhausted {
            PoweredFuelState {
                time: Seconds(time),
                zero_fuel_weight: Kilograms(174_369.0),
                left_usable_feed: Kilograms(0.0),
                right_usable_feed: Kilograms(0.0),
                reserved_fuel: Kilograms(20.0),
                unusable_fuel: Kilograms(0.0),
                left_exhaustion_time: Some(Seconds(time - 10.0)),
                right_exhaustion_time: Some(Seconds(time)),
                dual_engine_exhaustion_time: Some(Seconds(time)),
            }
        } else {
            PoweredFuelState {
                time: Seconds(time),
                zero_fuel_weight: Kilograms(174_369.0),
                left_usable_feed: Kilograms(500.0),
                right_usable_feed: Kilograms(500.0),
                reserved_fuel: Kilograms(20.0),
                unusable_fuel: Kilograms(0.0),
                left_exhaustion_time: None,
                right_exhaustion_time: None,
                dual_engine_exhaustion_time: None,
            }
        }
    }

    fn flight_state(slot: usize, time: f64, exhausted: bool) -> BroadFlightState {
        let bias = 150.0 + slot as f64;
        BroadFlightState {
            stratum: StratumId(1),
            powered_flight: powered_state(time, bias),
            fuel: fuel(time, exhausted),
            fuel_flow_scale: 1.0,
            fuel_quantity_offset_kg: 0.0,
            bfo_bias: BfoBiasState {
                mean_hz: bias,
                variance_hz2: 16.0,
            },
            status: BroadFlightParticleStatus::Active,
            fuel_status: BroadFuelDiagnosticStatus::Valid,
            scores: BroadFlightScores {
                cumulative_bto_log_likelihood: -1.0,
                cumulative_bfo_log_likelihood: 0.0,
                bto_observations: 1,
                bfo_observations: 0,
            },
            last_fit: None,
            diagnostics: BroadFlightDiagnostics::default(),
        }
    }

    fn parent_handoff() -> BroadPosteriorHandoffV1 {
        let evidence_identity = BroadEvidenceIdentityV1 {
            epoch_id: "satcom-through-m0011".to_string(),
            channel: None,
            component: BroadEvidenceComponentV1::Bto,
        };
        let evidence = BroadEvidenceLedgerV1::from_entries(vec![BroadEvidenceEntryV1 {
            identity: evidence_identity.clone(),
            disposition: BroadEvidenceDispositionV1::Consumed,
            state_effect: BroadEvidenceStateEffectV1::None,
        }])
        .unwrap();
        let model_family = "broad-powered-marked-jump-v1".to_string();
        let checkpoint_id = "m0011-filtered".to_string();
        let particles = (0..2)
            .map(|slot| {
                let state = flight_state(slot, M0011, false);
                BroadPosteriorHandoffParticleV1 {
                    identity: BroadPosteriorParticleIdentityV1 {
                        model_family: model_family.clone(),
                        seed: 7,
                        checkpoint_id: checkpoint_id.clone(),
                        particle: slot,
                    },
                    prior_root: BroadPriorRootIdentityV1 {
                        model_family: model_family.clone(),
                        seed: 7,
                        source_epoch_id: "m1801".to_string(),
                        stratum: StratumId(1),
                        initial_particle: slot,
                    },
                    parent_particle: None,
                    descendant_count: 1,
                    stratum: StratumId(1),
                    normalized_log_weight: 0.5_f64.ln(),
                    source_log_likelihood: -1.0,
                    cumulative_log_prior_over_proposal: 0.0,
                    powered_flight: state.powered_flight,
                    fuel: state.fuel,
                    fuel_flow_scale: state.fuel_flow_scale,
                    fuel_quantity_offset_kg: state.fuel_quantity_offset_kg,
                    bfo_bias: state.bfo_bias,
                    status: state.status,
                    fuel_status: state.fuel_status,
                    scores: state.scores,
                    last_fit: state.last_fit,
                    diagnostics: state.diagnostics,
                    evidence_scores: vec![BroadParticleEvidenceScoreV1 {
                        identity: evidence_identity.clone(),
                        log_likelihood: -1.0,
                    }],
                }
            })
            .collect();
        BroadPosteriorHandoffV1 {
            schema_version: BROAD_POSTERIOR_HANDOFF_SCHEMA_VERSION,
            run: BroadRunMetadataV1 {
                model_family,
                seed: 7,
                run_identity_sha256: digest('1'),
                config_sha256: digest('2'),
                input_sha256: BTreeMap::from([("satcom".to_string(), digest('3'))]),
                time_origin_utc: "2014-03-07T18:01:49Z".to_string(),
                source_epoch_id: "m1801".to_string(),
                source_time: Seconds(0.0),
                source_time_utc: "2014-03-07T18:01:49Z".to_string(),
                dynamics_model_family: "powered-marked-jump-era5-v1".to_string(),
                fuel_model_family: "declared-broad-extension".to_string(),
                pending_renewal_refresh: None,
                powered_performance_model_family: "segment-force-balance".to_string(),
                powered_aerodynamic_family: "openap-b772-attached-flow".to_string(),
                powered_thrust_family: "openap-b772-trent895".to_string(),
                powered_thrust_multiplier: 1.25,
                powered_static_thrust_cap_per_engine_n: 411_480.0,
                powered_maximum_additional_drag_coefficient: 0.1,
                configured_particles: 2,
                strata: vec![BroadStratumMetadataV1 {
                    id: StratumId(1),
                    name: "broad".to_string(),
                    process_family: "marked-jump".to_string(),
                    scientific_log_prior_probability: 0.0,
                    allocated_particles: 2,
                }],
            },
            checkpoint: BroadCheckpointMetadataV1 {
                checkpoint_id,
                state_epoch_id: "m0011".to_string(),
                state_time: Seconds(M0011),
                state_time_utc: "2014-03-08T00:10:59Z".to_string(),
                conditioning: BroadConditioningSemanticsV1::Filtering {
                    through_epoch_id: "m0011".to_string(),
                },
            },
            evidence,
            particles,
        }
    }

    fn policies() -> [ControlledToUncontrolledPolicy; 2] {
        let pre = mh370_end_of_flight::ControlSchedule {
            segments: vec![ControlSegment {
                start_offset: Seconds(0.0),
                command: ControlCommand::Controlled {
                    lift_load_factor: 1.0,
                    bank_angle: Degrees(0.0),
                },
            }],
        };
        std::array::from_fn(|index| ControlledToUncontrolledPolicy {
            scenario: ControlledToUncontrolledScenario {
                label: if index == 0 { "port" } else { "starboard" }.to_string(),
                trigger: ControlTransitionTrigger::DualEngineGeneratorLoss,
            },
            pre_trigger_controlled: pre.clone(),
            post_trigger_uncontrolled: mh370_end_of_flight::ControlSchedule {
                segments: vec![ControlSegment {
                    start_offset: Seconds(0.0),
                    command: ControlCommand::Uncontrolled {
                        lift_coefficient: 0.3,
                        bank_angle: Degrees(if index == 0 { -15.0 } else { 15.0 }),
                    },
                }],
            },
        })
    }

    fn satcom_config() -> SatcomModelConfig {
        SatcomModelConfig {
            bto: BtoConstants {
                speed_of_light_km_s: 299_792.458,
                nominal_delay_us: 0.0,
                channel_term_us: 0.0,
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
        }
    }

    fn template(joint: bool) -> BroadImpactHandoffV1 {
        let upstream = EvidenceIdentityV2 {
            dataset_id: "mh370-satcom".to_string(),
            observation_id: "through-m0011".to_string(),
            component_id: "bto".to_string(),
            channel_id: None,
        };
        let r600 = EvidenceIdentityV2 {
            dataset_id: "inmarsat-log".to_string(),
            observation_id: "m0019-r600".to_string(),
            component_id: "bto".to_string(),
            channel_id: Some("r600".to_string()),
        };
        let timing = EvidenceIdentityV2 {
            dataset_id: "inmarsat-log".to_string(),
            observation_id: "m0019-r600".to_string(),
            component_id: "logon_request_time".to_string(),
            channel_id: Some("r600".to_string()),
        };
        let fuel_window = EvidenceIdentityV2 {
            dataset_id: "derived-event".to_string(),
            observation_id: "m0019".to_string(),
            component_id: "fuel_exhaustion_window".to_string(),
            channel_id: None,
        };
        let occurrence = EvidenceIdentityV2 {
            dataset_id: "inmarsat-log".to_string(),
            observation_id: "m0019-r600".to_string(),
            component_id: "logon_occurrence".to_string(),
            channel_id: Some("r600".to_string()),
        };
        let terminal_evidence_model = if joint {
            BroadTerminalEvidenceModelV1::JointR600BtoAndLogonTiming {
                logon_request_identity: timing.clone(),
                fuel_exhaustion_window_identity: fuel_window.clone(),
                logon_occurrence_identity: occurrence.clone(),
                erlang_shape: 8,
                erlang_rate_per_s: 1.0 / 14.875,
            }
        } else {
            BroadTerminalEvidenceModelV1::R600BtoOnly
        };
        let mut entries = vec![
            EvidenceEntryV2 {
                identity: upstream.clone(),
                dependence_group_id: "upstream-m0011".to_string(),
                disposition: EvidenceDispositionV2::Consumed,
                application_id: Some("embedded-upstream".to_string()),
            },
            EvidenceEntryV2 {
                identity: r600.clone(),
                dependence_group_id: "final-logon".to_string(),
                disposition: EvidenceDispositionV2::Consumed,
                application_id: Some("terminal-update".to_string()),
            },
        ];
        if joint {
            entries.extend([
                EvidenceEntryV2 {
                    identity: timing,
                    dependence_group_id: "final-logon".to_string(),
                    disposition: EvidenceDispositionV2::Consumed,
                    application_id: Some("terminal-update".to_string()),
                },
                EvidenceEntryV2 {
                    identity: fuel_window,
                    dependence_group_id: "final-logon".to_string(),
                    disposition: EvidenceDispositionV2::HeldOut,
                    application_id: None,
                },
                EvidenceEntryV2 {
                    identity: occurrence,
                    dependence_group_id: "final-logon".to_string(),
                    disposition: EvidenceDispositionV2::HeldOut,
                    application_id: None,
                },
            ]);
        }
        BroadImpactHandoffV1 {
            schema_id: BROAD_IMPACT_HANDOFF_SCHEMA_ID.to_string(),
            schema_version: BROAD_IMPACT_HANDOFF_SCHEMA_VERSION,
            time_basis: AbsoluteTimeBasisV1 {
                scale: "utc".to_string(),
                epoch: "1970-01-01T00:00:00Z".to_string(),
                unit: "second".to_string(),
                convention: "posix_seconds_no_leap_representation".to_string(),
            },
            run: BroadImpactRunProvenanceV1 {
                hypothesis_id: if joint { "joint" } else { "bto-only" }.to_string(),
                run_identity_sha256: digest('a'),
                producer_executable_sha256: digest('b'),
                config_sha256: digest('c'),
                input_sha256: BTreeMap::from([("terminal".to_string(), digest('d'))]),
                model_sha256: BroadImpactModelHashesV1 {
                    dynamics_sha256: digest('d'),
                    fuel_sha256: digest('e'),
                    satcom_sha256: digest('f'),
                    end_of_flight_sha256: digest('1'),
                },
                code_revision: "test-revision".to_string(),
                terminal_seed: 370_019,
                transition_sidecar_sha256: digest('2'),
            },
            parent: BroadImpactParentV1 {
                schema_version: BROAD_POSTERIOR_HANDOFF_SCHEMA_VERSION,
                handoff_sha256: digest('3'),
                run_identity_sha256: digest('4'),
                config_sha256: digest('5'),
                input_sha256: BTreeMap::from([("placeholder".to_string(), digest('6'))]),
                evidence_ledger_sha256: digest('7'),
                consumed_evidence: vec![upstream],
                model_family: "placeholder".to_string(),
                seed: 0,
                checkpoint_id: "placeholder".to_string(),
                source_epoch_id: "placeholder".to_string(),
                checkpoint_time_unix_s_utc: ORIGIN + M0011,
                conditioning: BroadConditioningSemanticsV1::Filtering {
                    through_epoch_id: "m0011".to_string(),
                },
                configured_particle_count: 2,
                retained_particle_count: 2,
            },
            terminal_family: BroadTerminalFamilyV1 {
                id: "mirrored-terminal".to_string(),
                model_family: "controlled-to-uncontrolled-point-mass".to_string(),
                config_sha256: digest('8'),
                model_sha256: BroadTerminalModelHashesV1 {
                    end_of_flight_sha256: digest('9'),
                },
            },
            r600_evidence: BroadR600EvidenceV1 {
                identity: r600,
                dependence_group_id: "final-logon".to_string(),
                application_id: "terminal-update".to_string(),
                time_utc_unix_s: ORIGIN + R600,
                elapsed_from_parent_checkpoint_s: R600 - M0011,
                observed_bto_us: 18_400.0,
                standard_deviation_us: 63.0,
            },
            terminal_evidence_model,
            evidence: EvidenceLedgerV2 {
                entries,
                applications: vec![
                    EvidenceApplicationV1 {
                        id: "embedded-upstream".to_string(),
                        role: EvidenceApplicationRoleV1::EmbeddedUpstream,
                        model_family: "broad-parent".to_string(),
                        config_sha256: digest('a'),
                        input_sha256: BTreeMap::from([("parent".to_string(), digest('b'))]),
                        log_evidence_increment: None,
                    },
                    EvidenceApplicationV1 {
                        id: "terminal-update".to_string(),
                        role: EvidenceApplicationRoleV1::WeightUpdate,
                        model_family: if joint {
                            "normal-bto-plus-conditional-erlang"
                        } else {
                            "normal-bto"
                        }
                        .to_string(),
                        config_sha256: digest('c'),
                        input_sha256: BTreeMap::from([("r600".to_string(), digest('d'))]),
                        log_evidence_increment: Some(0.0),
                    },
                ],
            },
            outcome_mass: BroadOutcomeMassV1::default(),
            particles: Vec::new(),
        }
    }

    fn propagation() -> BroadTerminalPropagationConfigV1 {
        BroadTerminalPropagationConfigV1 {
            time_origin_unix_s_utc: ORIGIN,
            final_powered_bound: Seconds(R600 + 600.0),
            continuation_draws_per_parent: 1,
            apu_accessible_reserved_fuel: Kilograms(20.0),
            ocxo_restart_count: 0,
            restart_transient: RestartTransientFamily::CommonOcxoWarmup,
            mirrored_policies: policies(),
            aerodynamics: AerodynamicModel {
                reference_area: SquareMetres(427.8),
                zero_lift_drag_coefficient: 0.02,
                induced_drag_factor: 0.04,
                minimum_lift_coefficient: 0.0,
                maximum_lift_coefficient: 1.5,
                maximum_bank_angle: Degrees(60.0),
                minimum_true_airspeed: MetresPerSecond(20.0),
                maximum_true_airspeed: MetresPerSecond(400.0),
            },
            fallback_atmosphere: AtmosphereProfile {
                nodes: vec![AtmosphereNode {
                    altitude: Feet(0.0),
                    density: KilogramsPerCubicMetre(1.225),
                    wind_north: MetresPerSecond(0.0),
                    wind_east: MetresPerSecond(0.0),
                }],
            },
            apu_start_policy: ApuStartPolicy::OnDualEngineGeneratorLoss {
                start_delay: Seconds(2.0),
                start_fuel: Kilograms(1.0),
                generator_delay: Seconds(2.0),
                running_fuel_flow: KilogramsPerSecond(0.05),
            },
            integration: IntegrationSettings {
                time_step: Seconds(1.0),
                maximum_duration: Seconds(900.0),
                sea_surface_altitude: Feet(0.0),
                maximum_steps: 2_000,
            },
            environment_family_id: "constant-test".to_string(),
            environment_input_sha256: BTreeMap::from([("weather".to_string(), digest('e'))]),
            r600_contact: ExactTimeSatcomContact {
                satellite_source_epoch: Seconds(ORIGIN + R600),
                satellite_source_state: SatelliteEcefState {
                    position_km: Vec3::new(18_161.0, 38_060.0, 1_029.0),
                    velocity_km_s: Vec3::new(0.0, 0.0, 0.0),
                },
                satellite_delta: Seconds(0.0),
                satellite_propagation_limit: SatelliteEcefPropagationLimit {
                    maximum_absolute_delta: Seconds(1.0),
                },
                ground_station_position_km: Vec3::new(-2_403.0, 5_385.0, 2_440.0),
                observed_bto: Microseconds(18_400.0),
                bto_standard_deviation: Microseconds(63.0),
                bfo: None,
            },
            satcom: satcom_config(),
            upstream_evidence_mappings: vec![BroadUpstreamEvidenceMappingV1 {
                source: BroadEvidenceIdentityV1 {
                    epoch_id: "satcom-through-m0011".to_string(),
                    channel: None,
                    component: BroadEvidenceComponentV1::Bto,
                },
                downstream: EvidenceIdentityV2 {
                    dataset_id: "mh370-satcom".to_string(),
                    observation_id: "through-m0011".to_string(),
                    component_id: "bto".to_string(),
                    channel_id: None,
                },
            }],
        }
    }

    fn exhausted_result(slot: usize) -> BroadDualEngineExhaustionResult {
        let time = R600 - 30.0 - slot as f64;
        exhausted_result_at(slot, time, R600)
    }

    fn exhausted_result_at(
        slot: usize,
        time: f64,
        target_bound: f64,
    ) -> BroadDualEngineExhaustionResult {
        let mut state = flight_state(slot, time, true);
        state.powered_flight.aircraft.position =
            LatLon::new(-35.0 - slot as f64 * 0.01, 90.0).unwrap();
        BroadDualEngineExhaustionResult {
            outcome: BroadDualEngineExhaustionOutcome::Exhausted,
            state,
            target_bound: Seconds(target_bound),
            exhaustion_time: Some(Seconds(time)),
            transition_diagnostics: BroadFlightDiagnostics::default(),
            exact_boundary_reintegrations: 1,
            boundary_events_at_start: PoweredEventCounters::default(),
            boundary_events_at_end: PoweredEventCounters::default(),
        }
    }

    #[test]
    fn synthetic_bridge_scores_fractional_r600_and_preserves_mirrored_outcomes() {
        let parent = parent_handoff();
        parent.validate().unwrap();
        let artifacts = build_broad_terminal_with_continuation(
            &parent,
            template(false),
            propagation(),
            &ConstantEnvironment,
            |source, _| {
                Ok(BroadPoweredTerminalPathV1::EndedNoLaterThanR600 {
                    result: Box::new(exhausted_result(source.identity.particle)),
                })
            },
        )
        .unwrap();

        assert_eq!(artifacts.handoff.particles.len(), 4);
        assert_eq!(artifacts.sidecar.records.len(), 4);
        assert!(artifacts
            .handoff
            .particles
            .iter()
            .all(|particle| matches!(particle.r600, BroadR600ParticleEvidenceV1::Scored { .. })));
        assert!(artifacts
            .sidecar
            .records
            .iter()
            .all(|record| record.reconstructed_parent_state
                == parent.particles[record.identity.parent.particle].to_broad_flight_state()));
        assert_eq!(
            sha256_bytes(&artifacts.sidecar_bytes),
            artifacts.handoff.run.transition_sidecar_sha256
        );
        artifacts.handoff.validate().unwrap();
    }

    #[test]
    fn terminal_builder_rejects_refresh_parent_before_calling_continuation() {
        let mut parent = parent_handoff();
        parent.run.pending_renewal_refresh = Some(BroadPendingRenewalRefreshConfig {
            lateral: true,
            speed: true,
            altitude: true,
        });
        for particle in &mut parent.particles {
            let time = particle.powered_flight.aircraft.time.0;
            let pending = Some(PendingRenewal {
                not_before: Seconds(time),
                next_event: Seconds(time + 60.0),
            });
            particle.powered_flight.event_clocks = PoweredEventClocks {
                lateral: pending,
                speed: pending,
                altitude: pending,
            };
        }
        parent.validate().unwrap();
        let mut continuation_called = false;
        let error = build_broad_terminal_with_continuation(
            &parent,
            template(false),
            propagation(),
            &ConstantEnvironment,
            |source, _| {
                continuation_called = true;
                Ok(BroadPoweredTerminalPathV1::EndedNoLaterThanR600 {
                    result: Box::new(exhausted_result(source.identity.particle)),
                })
            },
        )
        .unwrap_err();
        assert!(!continuation_called);
        assert!(error.to_string().contains(
            "cannot consume a pending-renewal-refresh parent until every independent continuation draw refreshes"
        ));
    }

    #[test]
    fn joint_branch_scores_timing_atomically_and_holds_out_occurrence_window() {
        let artifacts = build_broad_terminal_with_continuation(
            &parent_handoff(),
            template(true),
            propagation(),
            &ConstantEnvironment,
            |source, _| {
                Ok(BroadPoweredTerminalPathV1::EndedNoLaterThanR600 {
                    result: Box::new(exhausted_result(source.identity.particle)),
                })
            },
        )
        .unwrap();
        assert!(artifacts.handoff.particles.iter().all(|particle| matches!(
            particle.logon_timing,
            Some(BroadLogonTimingParticleEvidenceV1::Scored { .. })
        )));
        assert_eq!(
            artifacts
                .handoff
                .evidence
                .entries
                .iter()
                .filter(|entry| entry.disposition == EvidenceDispositionV2::HeldOut)
                .count(),
            2
        );
        artifacts.handoff.validate().unwrap();
    }

    #[test]
    fn joint_branch_keeps_powered_r600_score_but_zeroes_post_logon_exhaustion() {
        let artifacts = build_broad_terminal_with_continuation(
            &parent_handoff(),
            template(true),
            propagation(),
            &ConstantEnvironment,
            |source, _| {
                if source.identity.particle == 0 {
                    Ok(BroadPoweredTerminalPathV1::EndedNoLaterThanR600 {
                        result: Box::new(exhausted_result(0)),
                    })
                } else {
                    Ok(BroadPoweredTerminalPathV1::ReachedR600 {
                        state_at_r600: flight_state(1, R600, false),
                        result_after_r600: Box::new(exhausted_result_at(
                            1,
                            R600 + 30.0,
                            R600 + 600.0,
                        )),
                    })
                }
            },
        )
        .unwrap();
        let after_logon = artifacts
            .handoff
            .particles
            .iter()
            .filter(|particle| particle.identity.parent.particle == 1)
            .collect::<Vec<_>>();
        assert_eq!(after_logon.len(), 2);
        assert!(after_logon.iter().all(|particle| {
            matches!(particle.r600, BroadR600ParticleEvidenceV1::Scored { .. })
                && matches!(
                    particle.logon_timing,
                    Some(BroadLogonTimingParticleEvidenceV1::ZeroSupport {
                        reason:
                            BroadLogonTimingZeroSupportReasonV1::ExhaustionAtOrAfterLogonRequest
                    })
                )
                && particle.posterior_normalized_log_weight.is_none()
        }));
        artifacts.handoff.validate().unwrap();
    }
}
