//! The fixed interface between the core estimator and optional modules (hypotheses).
//!
//! A module is a named, optional assumption or body of evidence that may change the estimate.
//! It can only act through the hooks below. It sees plain copies of state, never core
//! internals, and it cannot see other modules. Adding a new kind of hook is a core change,
//! made deliberately and reviewed on its own.
//!
//! The estimator runs in four stages. A module's role in a run comes from the config:
//! 1. The filter runs from the prior through the SATCOM data (to 00:11 when a terminal stage
//!    follows). Every enabled module not named in `[terminal]` or a `[[compose]]` set is a
//!    trajectory module and acts here, in this order:
//!    - [`Hypothesis::adjust_prior`], then [`Hypothesis::adjust_stratum_prior`]: change the
//!      prior (position, track, altitude distribution, initial Mach, autopilot-mode weights);
//!    - [`Hypothesis::extra_epochs`]: ask the runner to stop at additional times, e.g. a radar
//!      fix, so that the next hook can weight the state there;
//!    - [`Hypothesis::epoch_log_likelihood`]: add log-likelihood at every SATCOM epoch and at
//!      every requested extra epoch;
//!    - [`Hypothesis::final_log_likelihood`]: add log-likelihood at the filter's last epoch:
//!      00:19:37 UTC in the base estimate, 00:11 when a terminal stage follows.
//! 2. The terminal stage continues each trajectory to impact. The module named in
//!    `[terminal] module` supplies the [`Terminal`] model: the runner flies the core dynamics
//!    to its takeover time, the module descends, and the runner scores the 00:19 observations.
//! 3. Impact modules, named in `[[compose]]` sets, return [`Hypothesis::impact_log_likelihood`]
//!    for every impact sample, and may fill named [`Hypothesis::predict`]ions.
//! 4. The composer combines the chosen modules into one posterior.
//!
//! Declarations are read once, before a run: [`Hypothesis::observations`] (each observation is
//! used at most once per evidence set, and the runner refuses a run that uses one twice),
//! [`Hypothesis::alternatives`], [`Hypothesis::absolute_scale`] and
//! [`Hypothesis::prediction_columns`].
//!
//! Units: degrees, Unix seconds, and altitude in feet of pressure altitude everywhere, as in
//! the filter. The trajectory hooks use knots. The terminal and impact types use m/s, kg and J.
//! Random numbers come only from the uniform streams the runner passes in.
//!
//! Hooks are called in parallel for millions of samples. They must be cheap, deterministic and
//! free of side effects.

pub mod raw;

/// Autopilot modes in the order used everywhere (prior weights, output `mode` column).
pub const MODES: [&str; 5] = ["true heading", "magnetic heading", "true track", "magnetic track", "lateral navigation"];

/// Initial-state distribution at the start time.
#[derive(Debug, Clone, PartialEq)]
pub struct PriorSpec {
    pub unix_s: f64,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub position_sd_nm: f64,
    /// Mean true ground track, degrees.
    pub track_deg: f64,
    pub track_sd_deg: f64,
    /// Initial Mach set point, uniform on this range...
    pub mach_range: (f64, f64),
    /// ...unless this is set: Gaussian (mean, standard deviation), unbounded, as Davey et al.
    /// Table 8.2 lists ("Control Mach, Gaussian s.d. 0.03").
    pub mach_gaussian: Option<(f64, f64)>,
    /// Initial altitude: discrete levels (ft) with relative weights.
    pub altitude_levels: Vec<(f64, f64)>,
    /// Relative prior weights of the autopilot modes, in [`MODES`] order. A mode with
    /// weight zero is not run.
    pub mode_weights: [f64; 5],
}

/// A read-only copy of one particle's state.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct StateView {
    pub unix_s: f64,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub altitude_ft: f64,
    pub ground_velocity_north_kt: f64,
    pub ground_velocity_east_kt: f64,
    /// Mach set point.
    pub mach: f64,
    /// Index into [`MODES`] (lateral navigation may have reverted to a heading mode).
    pub mode: usize,
    pub manoeuvre_time_constant_h: f64,
    pub turns: u16,
    pub accelerations: u16,
    pub climbs: u16,
    /// Posterior mean of the BFO bias so far (Hz).
    pub bfo_bias_hz: f64,
    /// The particle's option of the run's trajectory-level alternative; 0 if there is none.
    pub alternative: usize,
}

/// The time at which a likelihood hook is being evaluated.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct EpochView<'a> {
    pub id: &'a str,
    pub unix_s: f64,
    /// True for a SATCOM epoch, false for an epoch requested by a hypothesis.
    pub satcom: bool,
}

/// A discrete model choice. Option priors are positive and sum to one.
///
/// Modules that declare the same `name` share one alternative (e.g. "ocean-model"): their
/// labels must match exactly, and the composer marginalises it once, jointly across them. A
/// name only one module uses is that module's own (e.g. {not-H, H} for "pleiades-origin").
/// An evidence set may override the priors (e.g. to sweep the prior of H).
#[derive(Debug, Clone, PartialEq)]
pub struct Alternatives {
    pub name: String,
    /// (label, prior probability).
    pub options: Vec<(String, f64)>,
    /// Axis label for the prior sweep of a two-option alternative. When set, the report draws
    /// the posterior probability of the second option against its prior odds under this label
    /// (e.g. "expected detectable MRO objects (prior odds)"); otherwise against its prior
    /// probability.
    pub sweep_label: Option<String>,
}

impl Alternatives {
    pub fn new(name: &str, options: &[(&str, f64)]) -> Self {
        let options = options.iter().map(|(label, p)| (label.to_string(), *p)).collect();
        Alternatives { name: name.to_string(), options, sweep_label: None }
    }
}

pub trait Hypothesis: Send + Sync {
    /// Observation IDs this module's hooks use. SATCOM data are `<epoch>.bto`, `<epoch>.bfo`
    /// and `<epoch>.<event>` (e.g. `m0019a.logon`). Other data are `<source>:<item>`, prefixed
    /// by the data source rather than the module (e.g. `debris:flaperon-reunion`), so that two
    /// modules using the same datum collide.
    fn observations(&self) -> Vec<String> {
        Vec::new()
    }

    /// Discrete alternatives. For a trajectory module, each option runs as a separate stratum
    /// of the filter, like the autopilot modes (at most one set per run). For an impact or
    /// terminal module, these are the sets `impact_log_likelihood` distinguishes, in the order
    /// of its `choice` argument. An impact alternative named like the run's trajectory
    /// alternative is not marginalised again: each impact uses its parent stratum's option.
    fn alternatives(&self) -> Vec<Alternatives> {
        Vec::new()
    }

    /// True if impact log-likelihoods under different options share one scale (normalised
    /// densities of the module's data, or all divided by the same background), so that they
    /// may be mixed. If false, the composer reports the options only as labelled conditional
    /// results.
    fn absolute_scale(&self) -> bool {
        false
    }

    /// Names, with units, of what [`Hypothesis::predict`] writes, in order. Names (like
    /// alternative names and option labels) become column names: no `,` `/` `:` or line breaks.
    fn prediction_columns(&self) -> Vec<String> {
        Vec::new()
    }

    fn adjust_prior(&self, _prior: &mut PriorSpec) {}

    /// Called after `adjust_prior` for the trajectory module that declares the run's
    /// trajectory-level alternative: the prior of the stratum for option `alternative`.
    fn adjust_stratum_prior(&self, _alternative: usize, _prior: &mut PriorSpec) {}

    /// Additional (id, unix time) epochs at which the runner should stop.
    fn extra_epochs(&self) -> Vec<(String, f64)> {
        Vec::new()
    }

    fn epoch_log_likelihood(&self, _epoch: &EpochView, _state: &StateView) -> f64 {
        0.0
    }

    fn final_log_likelihood(&self, _state: &StateView) -> f64 {
        0.0
    }

    /// The end-of-flight model, for the module named in `[terminal] module`.
    fn terminal(&self) -> Option<&dyn Terminal> {
        None
    }

    /// ln p(this module's data | impact, choice), where `choice` holds one option index per
    /// entry of `alternatives()`. Return a finite value; negative infinity only where the data
    /// are genuinely impossible; NaN for "not computed" (outside the module's data domain),
    /// which the composer reports and never reads as zero likelihood. Never a floor.
    fn impact_log_likelihood(&self, _impact: &ImpactView, _choice: &[usize]) -> f64 {
        0.0
    }

    /// Fill `out` (one slot per prediction column) for one impact; NaN means not computed.
    fn predict(&self, _impact: &ImpactView, _out: &mut [f64]) {}
}

/// Every hypothesis module exports `pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String>`.
pub type Constructor = fn(&toml::Value) -> Result<Box<dyn Hypothesis>, String>;

/// Weather from the runner's ERA5 grid, and IGRF declination.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Air {
    pub temperature_k: f64,
    /// ISA pressure at the query's pressure altitude.
    pub pressure_pa: f64,
    pub wind_east_mps: f64,
    pub wind_north_mps: f64,
    pub declination_deg: f64,
    /// Pressure altitude of the local sea surface, from ERA5 mean-sea-level pressure where the
    /// grid carries it; 0 (ISA sea level) otherwise. A descent ends here.
    pub surface_pressure_altitude_ft: f64,
    /// True where the query lay outside the grid's altitude or time span and was clamped.
    pub clamped: bool,
}

/// Wind and temperature at (time, pressure altitude, position), served by the runner.
pub trait Atmosphere: Sync {
    fn at(&self, unix_s: f64, altitude_ft: f64, latitude_deg: f64, longitude_deg: f64) -> Air;
}

/// The aircraft where the core dynamics hand over: at the hand-off (00:11) and at the takeover.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct FlightState {
    pub unix_s: f64,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub altitude_ft: f64,
    pub ground_velocity_east_mps: f64,
    pub ground_velocity_north_mps: f64,
    /// Plus or minus the climb rate during a level change, otherwise zero.
    pub vertical_speed_mps: f64,
    pub mach: f64,
    pub true_air_speed_mps: f64,
    /// True air heading, degrees.
    pub heading_deg: f64,
    /// ERA5 wind plus the model's wind-error state.
    pub wind_east_mps: f64,
    pub wind_north_mps: f64,
    /// Index into [`MODES`].
    pub mode: usize,
    /// Zero-fuel mass plus fuel; NaN until the core models fuel.
    pub mass_kg: f64,
    /// NaN until the core models fuel.
    pub fuel_kg: f64,
    /// NaN until the core models fuel.
    pub fuel_exhaustion_unix_s: f64,
}

/// A SATCOM burst after the filter's stop, at its logged time (00:19:29.416 for the R600,
/// 00:19:37.443 for the R1200).
#[derive(Debug, Clone, PartialEq)]
pub struct TerminalEpoch {
    pub id: String,
    pub unix_s: f64,
}

/// The aircraft at one requested epoch, as a terminal module returns it.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct EpochState {
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub altitude_ft: f64,
    pub velocity_east_mps: f64,
    pub velocity_north_mps: f64,
    pub velocity_up_mps: f64,
}

/// The impact fields a terminal module supplies. The runner derives the flight-path angle
/// and the total and vertical kinetic energy from them, so those definitions exist once.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Impact {
    pub unix_s: f64,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub velocity_east_mps: f64,
    pub velocity_north_mps: f64,
    pub velocity_up_mps: f64,
    pub mass_kg: f64,
}

/// One descent from a takeover state to impact.
#[derive(Debug, Clone, PartialEq)]
pub struct Descent {
    pub impact: Impact,
    /// Index into [`Terminal::families`].
    pub family: usize,
    /// One entry per requested epoch: `None` where the aircraft was already down, which makes
    /// any data option that uses that epoch impossible.
    pub at_epochs: Vec<Option<EpochState>>,
    /// One value per [`Terminal::latent_columns`] entry.
    pub latents: Vec<f64>,
    /// ln(prior / proposal) of this descent given the takeover state; 0 for a prior draw.
    pub log_q_correction: f64,
}

/// The end-of-flight model: from the powered state at the first flame-out to impact.
///
/// Uniform streams yield draws on the open interval (0, 1). Each call gets a fresh stream,
/// seeded by (seed, hand-off row, child, purpose).
pub trait Terminal: Send + Sync {
    /// Descent families, e.g. glide, ditching, spiral, dive. The module samples them from its
    /// declared prior, and the composer reports results per family.
    fn families(&self) -> Vec<String>;

    /// Names of the latent variables each descent records, e.g. the second flame-out time or
    /// the gap between engines. Only this module's own impact hook reads them.
    fn latent_columns(&self) -> Vec<String> {
        Vec::new()
    }

    /// The first flame-out for one child of the trajectory handed off at `handoff`. Returns
    /// (unix time, not before the hand-off; ln(prior / proposal) of the draw). The runner then
    /// flies the core dynamics to that time.
    fn takeover_time(&self, handoff: &FlightState, uniform: &mut dyn FnMut() -> f64) -> (f64, f64);

    /// One or more independent draws from the module's descent proposal, starting from the
    /// takeover state. `epochs` are the 00:19 epochs at or after the takeover; earlier ones
    /// were flown on the core dynamics.
    ///
    /// `score(candidates)` gives the log-likelihood of the configured target observations
    /// (`[terminal] target`, BFO models mixed by their priors) with candidate states at
    /// `epochs`. Use it only to adapt the proposal. The runner scores every observation once
    /// for the final weights, and `log_q_correction` keeps those weights exact.
    fn descend(
        &self,
        takeover: &FlightState,
        atmosphere: &dyn Atmosphere,
        uniform: &mut dyn FnMut() -> f64,
        epochs: &[TerminalEpoch],
        score: &dyn Fn(&[Option<EpochState>]) -> f64,
    ) -> Vec<Descent>;
}

/// One impact sample, as impact modules see it. It carries no weight: modules return
/// likelihoods only, and the files the runner writes carry the weights. Integer fields are
/// `usize::MAX` ("not given") when the samples lack them, e.g. a CSV for `mh370 evaluate`.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct ImpactView<'a> {
    /// Row of the parent trajectory in `handoff.npy`.
    pub parent: usize,
    pub unix_s: f64,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub velocity_east_mps: f64,
    pub velocity_north_mps: f64,
    pub velocity_up_mps: f64,
    /// Below the horizontal, positive when descending.
    pub flight_path_angle_deg: f64,
    pub mass_kg: f64,
    pub kinetic_energy_j: f64,
    pub vertical_kinetic_energy_j: f64,
    /// Index into the terminal module's families.
    pub family: usize,
    /// The first flame-out: time and place.
    pub takeover_unix_s: f64,
    pub takeover_latitude_deg: f64,
    pub takeover_longitude_deg: f64,
    pub takeover_altitude_ft: f64,
    /// The parent trajectory's autopilot mode and trajectory-level option.
    pub mode: usize,
    pub alternative: usize,
    /// The terminal module's latents; empty for every other module.
    pub latents: &'a [f64],
}
