//! Run configuration. A config may name a `base` config; its tables are merged over the
//! base (keys replace, tables merge recursively). Further override files given on the
//! command line are merged the same way, in order. Input paths are resolved relative to
//! the file that names them.

use flight::Parameters;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct Config {
    pub name: String,
    /// Particles for each autopilot-mode filter, in `Mode::ALL` order.
    pub particles_per_mode: [usize; 5],
    pub seeds: Vec<u64>,
    pub resample_ess_fraction: f64,
    pub cases: Vec<Case>,
    pub inputs: Inputs,
    pub prior: PriorConfig,
    pub bfo_bias: BiasConfig,
    pub output: OutputConfig,
    /// Weather sensitivity settings; defaults are the estimate.
    #[serde(default)]
    pub environment: EnvironmentConfig,
    /// Overrides of the published dynamics constants; empty is the estimate.
    #[serde(default)]
    pub dynamics: DynamicsConfig,
    /// Fuel burn and exhaustion evidence; absent leaves fuel unmodelled, as the book does.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub fuel: Option<FuelConfig>,
    /// Sampler settings that change how the posterior is explored but not what it is.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub sampler: Option<SamplerConfig>,
    /// SATCOM epochs left out of the run (e.g. the 00:19 messages after the SDU restart).
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub exclude_epochs: Vec<String>,
    /// Enabled hypotheses and their parameters; empty for the base estimate.
    #[serde(default)]
    pub hypotheses: BTreeMap<String, toml::Value>,
    /// The end-of-flight stage after the filter; absent for runs that end with the filter.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub terminal: Option<TerminalConfig>,
    /// Evidence sets the composer builds from the impact samples.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub compose: Vec<ComposeSet>,
}

#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct TerminalConfig {
    /// The enabled hypothesis whose `terminal()` model continues each trajectory to impact.
    pub module: String,
    /// Trajectories handed off per replicate, and the fewest a stratum with posterior mass keeps.
    pub handoff: usize,
    pub handoff_floor: usize,
    /// Takeover draws (children) per handed-off trajectory.
    pub children: usize,
    /// The burst whose BTO arc defines each impact's `arc_distance_nm`.
    pub arc: String,
    /// The data option the terminal module's score callback evaluates.
    pub target: String,
    /// Data options: each is one log-likelihood column of impacts.npy (one per BFO model if it
    /// uses a BFO), computed from the same children.
    pub options: Vec<DataOption>,
    /// Measurement alternatives for the 00:19 BFOs, the alternative "final-bfo-model".
    #[serde(default)]
    pub bfo_models: BTreeMap<String, BfoModelConfig>,
}

#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct DataOption {
    pub id: String,
    /// Observation IDs of bursts after the stop, e.g. "m0019a.bto".
    #[serde(rename = "use")]
    pub observations: Vec<String>,
}

/// One 00:19 BFO model: no offset (no parameters), a start-up offset (`second_hz`,
/// `first_minus_second_hz`, `points`) or an inflated error (`sd_hz`).
#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct BfoModelConfig {
    pub prior: f64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub second_hz: Option<[f64; 2]>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub first_minus_second_hz: Option<[f64; 2]>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub points: Option<[usize; 2]>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub sd_hz: Option<f64>,
}

impl BfoModelConfig {
    pub fn model(&self, label: &str) -> Result<satcom::FinalBfoModel, String> {
        match (self.second_hz, self.first_minus_second_hz, self.points, self.sd_hz) {
            (None, None, None, None) => Ok(satcom::FinalBfoModel::NoOffset),
            (None, None, None, Some(sd_hz)) => Ok(satcom::FinalBfoModel::Inflated { sd_hz }),
            (Some(second_hz), Some(first_minus_second_hz), Some(points), None) => {
                Ok(satcom::FinalBfoModel::StartupOffset { second_hz, first_minus_second_hz, points })
            }
            _ => Err(format!(
                "terminal.bfo_models.{label}: give nothing (no offset), sd_hz (inflated error), or \
                 second_hz, first_minus_second_hz and points (start-up offset)"
            )),
        }
    }
}

/// One evidence set: the flight posterior, one 00:19 data option and a chosen set of
/// impact modules, combined into one posterior.
#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct ComposeSet {
    pub id: String,
    /// The terminal stage's data option (a weight column of impacts.npy).
    #[serde(default = "no_terminal_data")]
    pub option: String,
    /// Enabled hypotheses applied through their impact hooks.
    #[serde(default)]
    pub modules: Vec<String>,
    /// Alternatives fixed to one option rather than marginalised: name -> option label.
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub given: BTreeMap<String, String>,
    /// Prior overrides: name -> one probability per option, in declaration order.
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub priors: BTreeMap<String, Vec<f64>>,
    /// Share of the pre-module posterior on uncomputed samples above which the set is
    /// flagged incomplete.
    #[serde(default = "default_tolerance")]
    pub tolerance: f64,
}

fn no_terminal_data() -> String {
    "none".into()
}

fn default_tolerance() -> f64 {
    1e-3
}

/// What each enabled hypothesis does in a run. The config decides: the module named in
/// `[terminal]` and those named in `[[compose]]` sets act after the filter; every other
/// enabled hypothesis acts in the filter.
pub struct Roles {
    pub terminal: Option<String>,
    pub impact: Vec<String>,
    pub trajectory: Vec<String>,
}

impl Config {
    pub fn roles(&self) -> Result<Roles, String> {
        let terminal = self.terminal.as_ref().map(|t| t.module.clone());
        let mut impact: Vec<String> = self.compose.iter().flat_map(|s| s.modules.iter().cloned()).collect();
        impact.sort();
        impact.dedup();
        impact.retain(|name| Some(name) != terminal.as_ref());
        for name in terminal.iter().chain(&impact) {
            if !self.hypotheses.contains_key(name) {
                return Err(format!("module {name} is used but not enabled: add [hypotheses.{name}]"));
            }
        }
        let after_filter = |name: &String| terminal.as_ref() == Some(name) || impact.contains(name);
        let trajectory = self.hypotheses.keys().filter(|n| !after_filter(n)).cloned().collect();
        Ok(Roles { terminal, impact, trajectory })
    }
}

#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct Case {
    pub id: String,
    pub use_bfo: bool,
    /// Whether the BTO enters the likelihood. Default true. Set false, with `use_bfo` false,
    /// for a case whose only evidence is the fuel: the prior propagated under the endurance
    /// requirement alone, which is the first rung of the evidence ladder.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub use_bto: Option<bool>,
    /// Last epoch whose measurements enter the likelihood, e.g. `"m0011"`. Later epochs are
    /// still propagated through and their residuals still recorded, so the 00:19 pair can be
    /// read as a diagnostic on a posterior that was not fitted to it.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub likelihood_until: Option<String>,
    /// Overrides the top-level seeds for this case.
    pub seeds: Option<Vec<u64>>,
}

#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct Inputs {
    pub observations: PathBuf,
    pub ephemeris: PathBuf,
    pub era5: PathBuf,
    pub igrf: PathBuf,
    /// Digitised published latitude pdf, compared against in reports and the app.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub reference_curve: Option<PathBuf>,
    /// Extracted Boeing-derived performance tables; required when `[fuel]` is present. Held
    /// here rather than under `[fuel]` so the loader resolves it against the config's directory
    /// like every other input.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub fuel_tables: Option<PathBuf>,
    /// The fuel session's internal model (`internal-v1.json`, local only); required when
    /// `fuel.model = "internal-v1"` (core request 16 C-1).
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub fuel_model: Option<PathBuf>,
}

#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct PriorConfig {
    pub time_utc: String,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub position_sd_nm: f64,
    pub track_deg: f64,
    pub track_sd_deg: f64,
}

#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct BiasConfig {
    pub mean_hz: f64,
    pub sd_hz: f64,
    /// Variance added to the bias per second between epochs, Hz^2/s. Absent or zero gives the
    /// published model: one unknown constant per trajectory. Set it to let the bias wander, in
    /// which case `bfo_sd_hz` should be the genuinely random part of the noise rather than the
    /// inflated 7 Hz, because the drift now carries what the inflation was standing in for.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub drift_hz2_per_s: Option<f64>,
}

#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct EnvironmentConfig {
    /// Multiplier on the nominal ERA5 wind (1.0 = estimate; 0.0 = nominal wind off).
    #[serde(default = "one")]
    pub wind_scale: f64,
    /// Multiplier on magnetic declination (1.0 = estimate; -1.0 = reversed sign convention).
    #[serde(default = "one")]
    pub declination_scale: f64,
}

fn one() -> f64 {
    1.0
}

impl Default for EnvironmentConfig {
    fn default() -> Self {
        Self { wind_scale: 1.0, declination_scale: 1.0 }
    }
}

/// Overrides of `flight::Parameters` (Davey et al. 2016, Table 8.2 and ch. 6-7).
/// Every field left out keeps its published value, so an empty table is the estimate.
/// Fuel burn and what the fuel state is allowed to say about the trajectory.
///
/// The burn model itself is the calibrated one: tabulated flow times a per-path factor drawn
/// from N(`factor_mean`, `factor_sd`), the calibration against Boeing's Appendix 1.6E figures
/// being N(1.0085, 0.0178). The two evidence terms are separate switches because they make
/// different claims:
///
///   * `require_power_until` is an observation, not an assumption: the aircraft transmitted at
///     that epoch, so a path whose tank ran dry earlier is inconsistent with the data.
///   * `exhaustion_target_utc` with `exhaustion_sd_s` is the weaker claim that the 00:19 log-on
///     followed engine failure and an APU start, so exhaustion should sit shortly before it.
///     Left absent, fuel constrains nothing beyond the hard requirement above.
#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct FuelConfig {
    /// Fuel on board at the prior epoch, kg (43,800 at the 17:06:43 ACARS report).
    pub initial_kg: f64,
    /// Zero-fuel weight, kg (174,196 from the same report).
    pub zfw_kg: f64,
    pub factor_mean: f64,
    pub factor_sd: f64,
    /// Epoch the aircraft must still have had fuel at, e.g. "m0011". Absent applies no such
    /// requirement.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub require_power_until: Option<String>,
    /// Centre of the Gaussian on exhaustion time, as a UTC timestamp.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub exhaustion_target_utc: Option<String>,
    /// Standard deviation of that Gaussian, seconds.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub exhaustion_sd_s: Option<f64>,
    /// How the speed and altitude profile is proposed against the fuel state.
    ///
    /// `"reject"` (the default, and what the published model does) proposes the profile from
    /// the prior alone and rejects the path at `require_power_until` if the tank ran dry.
    /// `"endurance"` lets the fuel state into the proposal: a path is dropped as soon as the
    /// deadline is unreachable on any continuation, and new Mach targets are drawn from a
    /// mixture of the prior and the affordable speeds, with the weight corrected exactly.
    /// Both target the same posterior; only the sampler's efficiency differs.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub proposal: Option<String>,
    /// Weight the endurance proposal leaves on the unmodified prior. Default 0.15.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub proposal_prior_mix: Option<f64>,
    /// Mach cells the affordable set is resolved on. Default 16.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub proposal_cells: Option<usize>,
    /// Flow model: "tables" (the default, the Boeing-derived tables as ported) or
    /// "internal-v1" (the fuel session's grid, read from `inputs.fuel_model`). Core request 16.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub model: Option<String>,
    /// Apply the temperature term tau = 1 + 0.003 dISA (1 + 0.2 M^2) with dISA from the
    /// weather temperature (C-2, audit F2). Default false, the standard day.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub temperature: Option<bool>,
    /// Initial fuel per path as [a, b]: a - factor * b kg (C-4; [43800, 7228] from the 17:06:43
    /// report). Absent uses `initial_kg` for every path.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub initial_from_factor: Option<[f64; 2]>,
    /// Bound every altitude level by the internal model's weight-dependent ceiling (C-5,
    /// audit F5). Needs `model = "internal-v1"`. Default false.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub ceiling: Option<bool>,
    /// Reject paths that contradict the fuel evidence with weight zero instead of the finite
    /// e^-50 penalty (audit F7). Default false.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub hard_reject: Option<bool>,
    /// Fuel pools: 1 (the default) or 2 (core request 16 C-7(b): left and right tanks, the
    /// live engine on the INOP flow after the first flame-out; needs model = "internal-v1").
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub tanks: Option<u8>,
    /// Two-tank prior: left minus right fuel at the prior epoch, [mean, sd] kg. Default
    /// [221, 120] (fuel session, engine-imbalance-180149.csv).
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub tank_imbalance_kg: Option<[f64; 2]>,
    /// Two-tank prior: right-to-left flow ratio, [mean, sd]. Default [1.021, 0.008].
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub tank_flow_ratio: Option<[f64; 2]>,
}

/// Sampler settings. These change which particles receive effort, never the target posterior.
#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct SamplerConfig {
    /// Enables the auxiliary look-ahead before each BTO epoch, with this much extra standard
    /// deviation (microseconds) added in quadrature to the epoch's own when scoring a
    /// dead-reckoned prediction. The factor is divided out exactly after the real likelihood,
    /// so this value trades steering strength against correction variance and cannot bias the
    /// result. Absent disables the step.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub lookahead_bto_sd_us: Option<f64>,
    /// Epochs at which to apply a resample-move rejuvenation (Gilks & Berzuini): after
    /// resampling, re-simulate each particle's segment from its parent's pre-epoch state with
    /// fresh manoeuvre randomness and accept the candidate by the Metropolis ratio of the two
    /// incremental weights. The proposal is the model's own transition, so the ratio is the
    /// likelihood ratio and the move leaves the target invariant exactly; what it buys is path
    /// diversity among the children that a resample has just made identical.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub rejuvenate_epochs: Vec<String>,
    /// Enables the arc-bridge turn proposal: during the leg into a BTO epoch, turns are drawn
    /// from a mixture of the prior and the turns whose dead-reckoned continuation reaches that
    /// epoch's arc, with the exact prior-to-proposal ratio carried into the weight. This is the
    /// two-ended half of the sampler - the endurance proposal steers speed from what is known at
    /// the start of a leg, this steers heading from where the leg must end. Absent disables it.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub bridge_prior_mix: Option<f64>,
    /// How many standard deviations of the epoch's BTO count as reaching the arc. Default 3.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub bridge_window_sd: Option<f64>,
    /// Candidate turn angles evaluated per draw. Default 24.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub bridge_cells: Option<usize>,
    /// Replaces systematic resampling with Davey's branching scheme (Sect. 8). Absent keeps the
    /// fixed-population resampler.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub branching: Option<BranchingConfig>,
    /// Epochs whose likelihood is applied in stages rather than at once (annealed SMC): the
    /// increment is raised to a power that climbs from zero to one over `temper_stages`, with a
    /// resample and an invariant MCMC move between stages, so the population migrates into a
    /// sharp likelihood gradually instead of meeting all of it at a single instant.
    ///
    /// This is the one remedy for the 19:41 degeneracy that needs no prediction across the leg:
    /// the guide is the likelihood itself, which is exactly computable, rather than a
    /// dead-reckoned forecast of where a particle will be, which is wrong for the 83 % of
    /// particles that manoeuvre during that leg.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub temper_epochs: Vec<String>,
    /// Stages per tempered epoch. Defaults to 4. The product of the stage exponents is one, so
    /// the target posterior is unchanged however many are used.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub temper_stages: Option<usize>,
}

/// Davey Sect. 8 and Table 8.2: the resampling step of the SIR filter implemented as
/// randomised branching over independently propagated trajectories, rather than as systematic
/// resampling of a fixed population. Both are SIR - the book calls its filter "a form of SIR
/// particle filter" (p. 16) and presents branching as a way of resampling, "thus resampling can
/// also be implemented through a randomised branching procedure" (p. 56) - so what this flag
/// selects is the resampling mechanism, not a different class of filter.
///
/// A particle whose weight is at or above the threshold is duplicated into `branch_factor`
/// children, each carrying its parent's weight divided by that factor. One below the threshold
/// is kept with probability equal to its weight, at weight one, and is otherwise pruned; the
/// book notes that pruning is the common outcome. Both arms preserve the weighted sum in
/// expectation (Eq. 8.5), so the scheme is unbiased and the population size floats.
#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct BranchingConfig {
    /// Davey's n-bar, tabulated as 3-10.
    pub branch_factor: u32,
    /// Davey's log eta, tabulated as -25 or -30.
    ///
    /// The book states eta as an absolute threshold on a weight it leaves unnormalised, and
    /// does not fix that weight's scale. Here weights are rescaled each epoch so the best
    /// surviving path sits at one, with the shift banked exactly into the evidence, so the
    /// threshold reads as "this many nats worse than the best path". That is the only reading
    /// on which the tabulated eta and branch factor are mutually consistent: a path that
    /// matched every measurement perfectly would still fall through an absolute e^-25 floor
    /// after a handful of epochs, purely from the repeated division by n-bar.
    pub log_threshold: f64,
    /// Population ceiling. Exceeding it triggers an unbiased systematic reduction back to this
    /// size, which is a departure from the published scheme forced by memory: Davey's
    /// population is bounded only by pruning. Defaults to twice the configured particle count.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub max_particles: Option<usize>,
    /// Redraw each child's manoeuvre time constant from its conditional posterior, as this
    /// engine's systematic resampler does. Davey samples tau once per trajectory and copies it
    /// into the children, which is the default here.
    #[serde(default)]
    pub refresh_tau: bool,
}

#[derive(Deserialize, Serialize, Clone, Default)]
#[serde(deny_unknown_fields)]
pub struct DynamicsConfig {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub mach_reversion_per_s: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub mach_noise_per_s: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub angle_reversion_per_s: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub angle_noise_rad2_per_s: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub wind_reversion_per_s: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub wind_noise_kt2_per_s: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub tau_range_h: Option<(f64, f64)>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub mach_range: Option<(f64, f64)>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub altitude_range_ft: Option<(f64, f64)>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub altitude_step_ft: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub bank_angle_deg: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub mach_rate_per_s: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub climb_rate_ft_per_s: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub lnav_switch_mean_s: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub cruise_step_s: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub manoeuvre_step_s: Option<f64>,
    /// Pass the modelled vertical speed to the cruise BFO instead of zero. Default false,
    /// which reproduces the published model (Davey sec. 7.2 carries no cruise vertical rate).
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub bfo_vertical_rate: Option<bool>,
    /// Early-flight sampling options (absent: the published model). When set, each seed also
    /// writes early.npy, row-aligned with final.npy (columns `filter::EARLY_COLUMNS`).
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub early: Option<EarlyConfig>,
}

/// `[dynamics.early]`: widen the prior over the first minutes after 18:01:49. Times are UTC.
#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct EarlyConfig {
    /// Mach range for set points drawn before `mach_until_utc` (prior draw and accelerations).
    pub mach_range: (f64, f64),
    pub mach_until_utc: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub excursion: Option<ExcursionConfig>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub turn: Option<TurnConfig>,
    /// Clip the early Mach range at each set point to this calibrated-airspeed envelope.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub cas_envelope_kt: Option<(f64, f64)>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub routes: Option<RoutesConfig>,
}

/// `[dynamics.early.routes]`: fly a route drawn uniformly from the list built from `first`
/// (each a list of fix names, in order) times `then` (each a list of fix names, possibly
/// empty), starting at `start_utc`, then resume the free model. Fix names resolve through
/// `waypoints_csv` (name, lat, lon).
#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct RoutesConfig {
    pub share: f64,
    pub start_utc: String,
    pub waypoints_csv: String,
    pub first: Vec<Vec<String>>,
    pub then: Vec<Vec<String>>,
}

impl RoutesConfig {
    /// The route names and coordinates, in the order the index column of early.npy uses.
    pub fn expand(&self) -> Result<(Vec<String>, Vec<Vec<(f64, f64)>>), String> {
        let text = std::fs::read_to_string(&self.waypoints_csv).map_err(|e| format!("{}: {e}", self.waypoints_csv))?;
        let mut fixes = std::collections::BTreeMap::new();
        for line in text.lines().skip(1) {
            let f: Vec<&str> = line.split(',').map(str::trim).collect();
            if f.len() >= 3 {
                if let (Ok(lat), Ok(lon)) = (f[1].parse::<f64>(), f[2].parse::<f64>()) {
                    fixes.insert(f[0].to_string(), (lat, lon));
                }
            }
        }
        let (mut names, mut routes) = (Vec::new(), Vec::new());
        for a in &self.first {
            for b in &self.then {
                let seq: Vec<&String> = a.iter().chain(b.iter()).collect();
                let pts = seq
                    .iter()
                    .map(|n| fixes.get(n.as_str()).copied().ok_or_else(|| format!("unknown fix {n} in dynamics.early.routes")))
                    .collect::<Result<Vec<_>, _>>()?;
                names.push(seq.iter().map(|s| s.as_str()).collect::<Vec<_>>().join("-"));
                routes.push(pts);
            }
        }
        Ok((names, routes))
    }
}

/// `[dynamics.early.excursion]`: a descent and climb back before radar re-acquisition.
#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct ExcursionConfig {
    /// Prior probability that a trajectory flies the excursion.
    pub share: f64,
    pub start_utc: (String, String),
    pub low_ft: (f64, f64),
    pub descent_fpm: (f64, f64),
    pub climb_fpm: (f64, f64),
    /// Window in which the climb ends (back at a cruise level).
    pub end_utc: (String, String),
    /// Calibrated airspeed below the Mach/CAS crossover.
    pub cas_kt: (f64, f64),
    #[serde(default = "default_max_tries")]
    pub max_tries: u32,
    /// Maximum climb rate (fpm) at 5,000 ft and 35,000 ft; see `flight::ExcursionPrior`.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub climb_ceiling_fpm: Option<(f64, f64)>,
}

fn default_max_tries() -> u32 {
    1000
}

/// `[dynamics.early.turn]`: a turn at a fixed time to a ground track drawn uniformly.
#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct TurnConfig {
    pub share: f64,
    pub at_utc: String,
    pub track_deg: (f64, f64),
}

impl EarlyConfig {
    pub fn resolve(&self) -> Result<flight::EarlyPhase, String> {
        let t = |s: &str| satcom::parse_utc(s);
        let excursion = match &self.excursion {
            None => None,
            Some(x) => {
                if !(0.0..=1.0).contains(&x.share) {
                    return Err("dynamics.early.excursion.share must be in [0, 1]".into());
                }
                Some(flight::ExcursionPrior {
                    share: x.share,
                    start_unix_s: (t(&x.start_utc.0)?, t(&x.start_utc.1)?),
                    low_ft: x.low_ft,
                    descent_fpm: x.descent_fpm,
                    climb_fpm: x.climb_fpm,
                    end_unix_s: (t(&x.end_utc.0)?, t(&x.end_utc.1)?),
                    cas_kt: x.cas_kt,
                    max_tries: x.max_tries,
                    climb_ceiling_fpm: x.climb_ceiling_fpm,
                })
            }
        };
        let turn = match &self.turn {
            None => None,
            Some(x) => {
                if !(0.0..=1.0).contains(&x.share) {
                    return Err("dynamics.early.turn.share must be in [0, 1]".into());
                }
                Some(flight::TurnPrior { share: x.share, unix_s: t(&x.at_utc)?, track_deg: x.track_deg })
            }
        };
        let routes = match &self.routes {
            None => None,
            Some(r) => {
                if !(0.0..=1.0).contains(&r.share) {
                    return Err("dynamics.early.routes.share must be in [0, 1]".into());
                }
                Some(flight::RoutePrior { share: r.share, unix_s: t(&r.start_utc)?, routes: r.expand()?.1 })
            }
        };
        Ok(flight::EarlyPhase {
            mach_range: self.mach_range,
            mach_until_unix_s: t(&self.mach_until_utc)?,
            excursion,
            turn,
            cas_envelope_kt: self.cas_envelope_kt,
            routes,
        })
    }
}

impl DynamicsConfig {
    /// The published parameters with this config's overrides applied.
    pub fn apply(&self, mut p: Parameters) -> Parameters {
        macro_rules! set {
            ($($field:ident),*) => {$(if let Some(v) = self.$field { p.$field = v; })*};
        }
        set!(mach_reversion_per_s, mach_noise_per_s, angle_reversion_per_s, angle_noise_rad2_per_s,
             wind_reversion_per_s, wind_noise_kt2_per_s, tau_range_h, mach_range, altitude_range_ft,
             altitude_step_ft, bank_angle_deg, mach_rate_per_s, climb_rate_ft_per_s, lnav_switch_mean_s,
             cruise_step_s, manoeuvre_step_s, bfo_vertical_rate);
        p
    }
}

#[derive(Deserialize, Serialize, Clone)]
#[serde(deny_unknown_fields)]
pub struct OutputConfig {
    pub route_interval_s: f64,
    pub route_samples: usize,
    /// Particles per mode and SATCOM step saved with their residuals (0 = off).
    #[serde(default)]
    pub residual_samples: usize,
    /// If set, write history.npy (row-aligned with final.npy): the turns, speed changes,
    /// altitude changes and degrees turned after this epoch (e.g. "m1839", 18:40).
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub history_after_epoch: Option<String>,
    /// Epochs at which to write a full-state hand-off WITHOUT stopping the filter, each to
    /// `<seed dir>/handoff-<epoch>/` in the same format as the stop hand-off. The filter carries
    /// on to its last epoch, so one run serves every downstream stage that starts at any of
    /// these epochs as well as the full posterior. Unlike `[terminal]`, this does not require
    /// the run to stop before the bursts a later stage will score.
    ///
    /// Each snapshot is the posterior given the data up to and including that epoch: the
    /// particles and weights after the epoch's update, tempering and resampling, and the mode
    /// probabilities from each mode's evidence to date - never from later data. The draws use
    /// streams no filter step uses, so final.npy is the same with or without them.
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub handoff_epochs: Vec<String>,
    /// Rows per replicate at each of `handoff_epochs`.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub handoff_rows: Option<usize>,
    /// The fewest rows any mode with posterior mass keeps at each of `handoff_epochs` (default 1).
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub handoff_floor: Option<usize>,
}

/// Load a config and merge any override files over it, in order.
pub fn load(paths: &[PathBuf]) -> Result<Config, String> {
    load_with(paths, None)
}

/// As `load`, with one further table merged last. The app sends its controls through
/// here, so a run made in the app is the same as one made with an override file.
pub fn load_with(paths: &[PathBuf], last: Option<toml::Table>) -> Result<Config, String> {
    let mut table = load_table(&paths[0], 0)?;
    for path in &paths[1..] {
        merge(&mut table, load_table(path, 0)?);
    }
    if let Some(last) = last {
        merge(&mut table, last);
    }
    toml::Value::Table(table).try_into().map_err(|e| format!("{}: {e}", paths[0].display()))
}

fn load_table(path: &Path, depth: usize) -> Result<toml::Table, String> {
    if depth > 8 {
        return Err(format!("{}: base configs nest too deeply", path.display()));
    }
    let text = std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let mut table: toml::Table = toml::from_str(&text).map_err(|e| format!("{}: {e}", path.display()))?;
    let dir = path.parent().unwrap_or(Path::new("."));
    if let Some(toml::Value::Table(inputs)) = table.get_mut("inputs") {
        for (_, value) in inputs.iter_mut() {
            if let toml::Value::String(p) = value {
                let resolved = dir.join(p.as_str()).to_string_lossy().into_owned();
                *p = resolved;
            }
        }
    }
    match table.remove("base") {
        None => Ok(table),
        Some(toml::Value::String(base)) => {
            let mut merged = load_table(&dir.join(base), depth + 1)?;
            merge(&mut merged, table);
            Ok(merged)
        }
        Some(_) => Err(format!("{}: `base` must be a path", path.display())),
    }
}

fn merge(base: &mut toml::Table, over: toml::Table) {
    for (key, value) in over {
        match (base.get_mut(&key), value) {
            (Some(toml::Value::Table(b)), toml::Value::Table(o)) => merge(b, o),
            (_, value) => {
                base.insert(key, value);
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The module in [terminal] acts there even when a set lists it (for its own data); modules
    /// in sets are impact modules; every other enabled one is a trajectory module.
    #[test]
    fn roles_come_from_the_config() {
        let base = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/../../config/davey2016.toml")).unwrap();
        let text = format!(
            "{base}\n[hypotheses.eof]\n[hypotheses.drift]\n[hypotheses.prior]\n[terminal]\nmodule = \"eof\"\n\
             handoff = 10\nhandoff_floor = 1\nchildren = 1\narc = \"m0019a\"\ntarget = \"none\"\n\
             options = [{{ id = \"none\", use = [] }}]\n\
             [[compose]]\nid = \"all\"\nmodules = [\"drift\", \"eof\"]\n"
        );
        let config: Config = toml::from_str(&text).unwrap();
        let roles = config.roles().unwrap();
        assert_eq!(roles.terminal.as_deref(), Some("eof"));
        assert_eq!(roles.impact, ["drift"]);
        assert_eq!(roles.trajectory, ["prior"]);
        let missing: Config = toml::from_str(&format!("{base}\n[[compose]]\nid = \"x\"\nmodules = [\"absent\"]\n")).unwrap();
        assert!(missing.roles().is_err());
    }

    #[test]
    fn overlay_merges_tables_and_replaces_everything_else() {
        let mut base: toml::Table = toml::from_str("seeds = [1, 2]\n[prior]\na = 1\nb = 2").unwrap();
        let over: toml::Table = toml::from_str("seeds = [3]\n[prior]\nb = 5").unwrap();
        merge(&mut base, over);
        assert_eq!(base["seeds"].as_array().unwrap().len(), 1);
        assert_eq!(base["prior"]["a"].as_integer(), Some(1));
        assert_eq!(base["prior"]["b"].as_integer(), Some(5));
    }
}
