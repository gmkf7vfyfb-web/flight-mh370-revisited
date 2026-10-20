//! Focused scientific controls for the canonical estimator.
//!
//! Truth-blind inference and scorer-only truth loading are separate APIs. No
//! known-flight function loads MH370 accident-flight observations.

mod config;
mod final_bfo;
mod known_flight;
mod known_flight_score;
mod metrics;
mod synthetic;

pub use config::{ExperimentConfig, SyntheticScenario, ValidationThresholds};
pub use final_bfo::{
    analyze_bfo_pair, search_bfo_pair, solve_bfo_vertical_speed, BfoPairCandidate,
    BfoPairObservation, BfoPairSearchBounds, BfoPairSearchResult, BfoVerticalSolution,
    FinalBfoError,
};
pub use known_flight::{
    parse_known_flight_antenna_power, parse_known_flight_inference, run_known_flight_inference,
    KnownFlightAntennaConfig, KnownFlightAntennaInputs, KnownFlightAntennaObservation,
    KnownFlightAntennaPowerPackage, KnownFlightError, KnownFlightInferenceConfig,
    KnownFlightInferencePackage, KnownFlightInferenceRun, KnownFlightModelConfig,
    KnownFlightObservation, KnownFlightParticle, KnownFlightPriorConfig,
};
pub use known_flight_score::{
    parse_known_flight_truth_csv, score_known_flight, KnownFlightBfoClosure, KnownFlightBtoClosure,
    KnownFlightCheckpointScore, KnownFlightGrid, KnownFlightPairwiseScore, KnownFlightScoreError,
    KnownFlightScoreSummary, KnownFlightScoringConfig, KnownFlightTruthRow,
};
pub use metrics::{summarize_synthetic, SyntheticSummary};
pub use synthetic::{
    run_synthetic, simulate_synthetic, SyntheticDataset, SyntheticError, SyntheticRun,
};
