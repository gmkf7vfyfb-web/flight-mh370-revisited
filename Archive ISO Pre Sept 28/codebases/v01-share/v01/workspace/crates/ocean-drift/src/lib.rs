//! Forward ocean transport and conditional debris evidence for MH370.
//!
//! HYCOM analysis and GDP drifter-climatology fields are deliberately kept as
//! separate model families. The crate owns scientific equations; the runner
//! owns configuration, file selection, and report generation.

mod field;
mod isotope;
mod observations;
mod sampling;
mod source_area;
mod transport;

pub use field::{FieldError, FieldTimeAxis, GriddedField, VelocitySample};
pub use isotope::{
    BarnacleChronology, BarnacleIsotopeModel, BarnacleRecord, IsotopeClassification, IsotopeError,
    IsotopeEvaluation,
};
pub use observations::{
    DebrisEvaluation, DebrisEvidence, DebrisObservationError, DiscoveryDelayBin, GeographicBounds,
    NonRecoveryEvaluation, NonRecoveryObservation, RecoveryEvaluation, RecoveryEvent,
};
pub use sampling::{
    ArrivalSamplingConfig, ArrivalSamplingMethod, SamplingDiagnostics, SamplingEventDiagnostics,
};
pub use source_area::{
    evaluate_source_area, DebrisMotionFamily, MotionFamilyEvaluation, RecoveryEnsembleEvaluation,
    SourceAreaCell, SourceAreaConfig, SourceAreaError, SourceAreaResult, SourceCellResult,
    SourceCellStatus,
};
pub use transport::{
    simulate_path, DriftEnvironment, DriftPath, DriftPoint, MotionConfig, PathTermination,
    PathTerminationReason, TransportError,
};

/// UTC seconds for 2014-03-08 00:19:00, the seventh-arc release epoch.
pub const MH370_SEVENTH_ARC_UNIX_S: f64 = 1_394_237_940.0;
/// UTC seconds for 2015-07-29 00:00:00, the reported flaperon recovery date.
pub const FLAPERON_RECOVERY_UNIX_S: f64 = 1_438_128_000.0;
