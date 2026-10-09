//! Aircraft cruise and manoeuvre dynamics of Davey et al. (2016), ch. 6-8.
//!
//! Cruise: Mach, control angle and wind error follow Ornstein-Uhlenbeck processes
//! about their set points; true air speed follows local ERA5 temperature; ground
//! velocity follows the selected autopilot mode. Manoeuvres: turns, Mach changes
//! and altitude changes arrive independently with exponential gaps of common mean
//! tau (Jeffreys prior on 0.1-10 h) and are executed at fixed rates.

pub mod environment;

pub mod fuel;

use environment::{Environment, Weather, MPS_PER_KNOT};
use geo::{advance, radii_of_curvature_km, wrap_pi, KM_PER_FT, KM_S_PER_KT};
use rand::Rng;
use rand_distr::{Distribution, Exp1, StandardNormal};
use serde::{Deserialize, Serialize};
use std::f64::consts::{LN_2, PI};
use std::sync::Arc;

/// Model parameters. `Default` is Davey et al. (2016) Table 8.2 and ch. 6-7.
#[derive(Debug, Clone)]
pub struct Parameters {
    pub mach_reversion_per_s: f64,
    pub mach_noise_per_s: f64,
    pub angle_reversion_per_s: f64,
    pub angle_noise_rad2_per_s: f64,
    pub wind_reversion_per_s: f64,
    pub wind_noise_kt2_per_s: f64,
    pub tau_range_h: (f64, f64),
    pub mach_range: (f64, f64),
    pub altitude_range_ft: (f64, f64),
    pub altitude_step_ft: f64,
    pub bank_angle_deg: f64,
    pub mach_rate_per_s: f64,
    pub climb_rate_ft_per_s: f64,
    /// Mean time before lateral navigation reverts to a heading-hold mode.
    pub lnav_switch_mean_s: f64,
    pub cruise_step_s: f64,
    pub manoeuvre_step_s: f64,
    /// Fuel state and the loaded performance tables; `None` leaves fuel unmodelled, which is
    /// the published model (Davey Assumption 4 substitutes the 0.73 Mach floor for a fuel
    /// constraint). Shared behind an `Arc` because the grids are ~4,000 cells and `Parameters`
    /// is cloned per filter; the manifest identifies them by their source hash.
    pub fuel: Option<Arc<FuelModel>>,
    /// Pass the modelled vertical speed to the cruise BFO instead of zero.
    ///
    /// Davey sec. 7.2 carries no vertical rate in the cruise state, and the aircraft's own
    /// Doppler compensation does not include the vertical component of its velocity (sec. 5.3),
    /// so a climbing or descending aircraft has an uncompensated vertical Doppler term that the
    /// published model omits. At the 00:11 geometry that term is 17.5 Hz per 1,000 ft/min against
    /// a 7 Hz measurement standard deviation, so the omission is not small for any particle in a
    /// level change. `false` reproduces the published model exactly.
    pub bfo_vertical_rate: bool,
    /// Optional sampling for the early flight after the 18:01:49 prior (`None`: the published
    /// model). See [`EarlyPhase`].
    pub early: Option<EarlyPhase>,
}

/// Sampling options for the early flight, 18:01 to about 18:40, where the radar record ends and
/// the 18:25-18:28 arcs and the 18:39 BFO constrain the path. Each widens the prior rather than
/// asserting a history: the data assign the weight.
#[derive(Debug, Clone)]
pub struct EarlyPhase {
    /// Mach set points drawn before `mach_until_unix_s` - the prior draw and any acceleration
    /// that starts before then - come from this range instead of `Parameters::mach_range`.
    pub mach_range: (f64, f64),
    pub mach_until_unix_s: f64,
    /// A descent below cruise and a climb back, flown before the radar re-acquisition.
    pub excursion: Option<ExcursionPrior>,
    /// A turn to a sampled ground track at a fixed time (e.g. the 18:22:12 last radar return).
    pub turn: Option<TurnPrior>,
    /// Calibrated-airspeed envelope (min manoeuvring speed, VMO) that clips the early Mach range
    /// at the aircraft's altitude when a set point is drawn.
    pub cas_envelope_kt: Option<(f64, f64)>,
    /// A flight plan drawn uniformly from a declared list of routes.
    pub routes: Option<RoutePrior>,
}

/// Prior over route skeletons: with probability `share`, fly one of `routes` (drawn uniformly)
/// from `unix_s` on true track, then resume the free model.
#[derive(Debug, Clone)]
pub struct RoutePrior {
    pub share: f64,
    pub unix_s: f64,
    pub routes: Vec<Vec<(f64, f64)>>,
}

/// One drawn route.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct EarlyRoute {
    pub index: u32,
    pub unix_s: f64,
    pub started: bool,
}

/// Prior over a vertical excursion. Each draw: a descent from the particle's level starting
/// in `start_unix_s`, at a rate in `descent_fpm`, to a level in `low_ft`; level flight; a
/// climb at a rate in `climb_fpm` that ends at a time in `end_unix_s` at a cruise level drawn
/// like any altitude change. Below the Mach/CAS crossover the speed is a CAS in `cas_kt`.
/// Draws whose descent and climb cannot both fit between start and end are redrawn, so the
/// prior is uniform over the feasible set; `max_tries` bounds that.
#[derive(Debug, Clone)]
pub struct ExcursionPrior {
    pub share: f64,
    pub start_unix_s: (f64, f64),
    pub low_ft: (f64, f64),
    pub descent_fpm: (f64, f64),
    pub climb_fpm: (f64, f64),
    pub end_unix_s: (f64, f64),
    pub cas_kt: (f64, f64),
    pub max_tries: u32,
    /// Maximum climb rate (fpm) at 5,000 ft and at 35,000 ft, linear in between and constant
    /// outside. A draw whose climb rate exceeds the mean ceiling over its climb (total height
    /// over the time the ceiling profile takes) is infeasible and redrawn.
    pub climb_ceiling_fpm: Option<(f64, f64)>,
}

impl ExcursionPrior {
    /// Mean rate (fpm) of a climb from `from_ft` to `to_ft` flown at the ceiling throughout.
    fn mean_ceiling_fpm(&self, from_ft: f64, to_ft: f64) -> f64 {
        let Some((r5, r35)) = self.climb_ceiling_fpm else { return f64::INFINITY };
        let rate = |h: f64| r5 + (r35 - r5) * ((h - 5000.0) / 30000.0).clamp(0.0, 1.0);
        const N: usize = 64;
        let dh = (to_ft - from_ft) / N as f64;
        let minutes: f64 = (0..N).map(|i| dh / rate(from_ft + (i as f64 + 0.5) * dh)).sum();
        (to_ft - from_ft) / minutes
    }
}

/// Prior over a turn at a fixed time to a ground track uniform on `track_deg`.
#[derive(Debug, Clone)]
pub struct TurnPrior {
    pub share: f64,
    pub unix_s: f64,
    pub track_deg: (f64, f64),
}

/// One drawn vertical excursion. Times are unix seconds.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Excursion {
    pub start_s: f64,
    pub low_s: f64,
    pub climb_s: f64,
    pub end_s: f64,
    pub from_ft: f64,
    pub low_ft: f64,
    pub end_ft: f64,
    pub descent_fpm: f64,
    pub climb_fpm: f64,
    pub cas_kt: f64,
    /// The Mach the aircraft resumes at the end, and the cap above the crossover.
    pub resume_mach: f64,
    pub started: bool,
    pub done: bool,
}

impl Excursion {
    fn altitude_at(&self, t: f64) -> f64 {
        if t <= self.start_s {
            self.from_ft
        } else if t < self.low_s {
            self.from_ft - self.descent_fpm / 60.0 * (t - self.start_s)
        } else if t < self.climb_s {
            self.low_ft
        } else if t < self.end_s {
            self.low_ft + self.climb_fpm / 60.0 * (t - self.climb_s)
        } else {
            self.end_ft
        }
    }

    fn vertical_fpm_at(&self, t: f64) -> f64 {
        if t >= self.start_s && t < self.low_s {
            -self.descent_fpm
        } else if t >= self.climb_s && t < self.end_s {
            self.climb_fpm
        } else {
            0.0
        }
    }

    fn mach_at(&self, alt_ft: f64) -> f64 {
        cas_to_mach(self.cas_kt, alt_ft).min(self.resume_mach)
    }
}

/// One drawn fixed-time turn.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct EarlyTurn {
    pub unix_s: f64,
    pub track_deg: f64,
    pub done: bool,
}

/// What a particle drew from [`EarlyPhase`]. Present only when the option is configured.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct EarlyRecord {
    pub initial_mach: f64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub excursion: Option<Excursion>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub turn: Option<EarlyTurn>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub route: Option<EarlyRoute>,
    /// Infeasible excursion draws rejected before one fitted (or `max_tries` if none did).
    pub excursion_rejected: u32,
}

/// Draw what one particle samples from the early-phase options.
fn draw_early<R: Rng>(e: &EarlyPhase, p: &Parameters, from_ft: f64, mach: f64, rng: &mut R) -> EarlyRecord {
    fn u<R: Rng>(r: (f64, f64), rng: &mut R) -> f64 {
        if r.1 > r.0 {
            rng.gen_range(r.0..r.1)
        } else {
            r.0
        }
    }
    let mut rec = EarlyRecord { initial_mach: mach, excursion: None, turn: None, route: None, excursion_rejected: 0 };
    if let Some(x) = &e.excursion {
        if rng.gen_bool(x.share) {
            let levels = Prior::uniform_altitude_levels(p);
            for _ in 0..x.max_tries {
                let start_s = u(x.start_unix_s, rng);
                let low_ft = u(x.low_ft, rng);
                let descent_fpm = u(x.descent_fpm, rng);
                let climb_fpm = u(x.climb_fpm, rng);
                let end_s = u(x.end_unix_s, rng);
                let cas_kt = u(x.cas_kt, rng);
                let end_ft = levels[rng.gen_range(0..levels.len())].0;
                let low_s = start_s + (from_ft - low_ft) / descent_fpm * 60.0;
                let climb_s = end_s - (end_ft - low_ft) / climb_fpm * 60.0;
                if low_ft < from_ft && low_ft < end_ft && low_s <= climb_s && climb_fpm <= x.mean_ceiling_fpm(low_ft, end_ft) {
                    rec.excursion = Some(Excursion {
                        start_s,
                        low_s,
                        climb_s,
                        end_s,
                        from_ft,
                        low_ft,
                        end_ft,
                        descent_fpm,
                        climb_fpm,
                        cas_kt,
                        resume_mach: mach,
                        started: false,
                        done: false,
                    });
                    break;
                }
                rec.excursion_rejected += 1;
            }
        }
    }
    if let Some(t) = &e.turn {
        if rng.gen_bool(t.share) {
            rec.turn = Some(EarlyTurn { unix_s: t.unix_s, track_deg: u(t.track_deg, rng), done: false });
        }
    }
    if let Some(r) = &e.routes {
        if !r.routes.is_empty() && rng.gen_bool(r.share) {
            let index = rng.gen_range(0..r.routes.len() as u32);
            rec.route = Some(EarlyRoute { index, unix_s: r.unix_s, started: false });
        }
    }
    rec
}

/// Mach for a calibrated airspeed at a pressure altitude (ISA, subsonic compressible flow).
pub fn cas_to_mach(cas_kt: f64, pressure_altitude_ft: f64) -> f64 {
    const A0_KT: f64 = 661.478_8;
    const P0_PA: f64 = 101_325.0;
    let qc = P0_PA * ((1.0 + 0.2 * (cas_kt / A0_KT).powi(2)).powf(3.5) - 1.0);
    let p = geo::isa_pressure_pa(pressure_altitude_ft);
    (5.0 * ((qc / p + 1.0).powf(2.0 / 7.0) - 1.0)).sqrt()
}

impl Default for Parameters {
    fn default() -> Self {
        Self {
            mach_reversion_per_s: 1.058e-2,
            mach_noise_per_s: 2.05e-7,
            angle_reversion_per_s: 9.792e-3,
            angle_noise_rad2_per_s: 4.074e-8,
            wind_reversion_per_s: 1.087e-3,
            wind_noise_kt2_per_s: 0.070_21,
            tau_range_h: (0.1, 10.0),
            mach_range: (0.73, 0.84),
            altitude_range_ft: (25_000.0, 43_000.0),
            altitude_step_ft: 1_000.0,
            bank_angle_deg: 15.0,
            mach_rate_per_s: 0.1 / 60.0,
            climb_rate_ft_per_s: 4_000.0 / 60.0,
            lnav_switch_mean_s: 6.0 / LN_2 * 3600.0,
            cruise_step_s: 10.0,
            manoeuvre_step_s: 5.0,
            fuel: None,
            bfo_vertical_rate: false,
            early: None,
        }
    }
}

impl Parameters {
    fn stationary_sd(reversion: f64, noise: f64) -> f64 {
        (noise / (2.0 * reversion)).sqrt()
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[repr(u8)]
pub enum Mode {
    TrueHeading = 0,
    MagneticHeading = 1,
    TrueTrack = 2,
    MagneticTrack = 3,
    LateralNavigation = 4,
}

impl Mode {
    pub const ALL: [Mode; 5] = [Mode::TrueHeading, Mode::MagneticHeading, Mode::TrueTrack, Mode::MagneticTrack, Mode::LateralNavigation];
    fn magnetic(self) -> bool {
        matches!(self, Mode::MagneticHeading | Mode::MagneticTrack)
    }
    fn holds_heading(self) -> bool {
        matches!(self, Mode::TrueHeading | Mode::MagneticHeading)
    }
}

/// Initial-state distribution at the start time (ch. 4).
#[derive(Debug, Clone)]
pub struct Prior {
    pub unix_s: f64,
    pub lat: f64,
    pub lon: f64,
    pub position_sd_nm: f64,
    pub track_deg: f64,
    pub track_sd_deg: f64,
    /// Initial Mach set point, uniform on this range unless `mach_gaussian` is set.
    pub mach_range: (f64, f64),
    /// Initial Mach set point ~ N(mean, sd), unbounded.
    pub mach_gaussian: Option<(f64, f64)>,
    /// Initial altitude: discrete levels (ft) with relative weights.
    pub altitude_levels: Vec<(f64, f64)>,
}

impl Prior {
    /// The base-estimate altitude prior: uniform on the manoeuvre levels.
    pub fn uniform_altitude_levels(p: &Parameters) -> Vec<(f64, f64)> {
        let levels = ((p.altitude_range_ft.1 - p.altitude_range_ft.0) / p.altitude_step_ft).round() as u32;
        (0..=levels).map(|k| (p.altitude_range_ft.0 + p.altitude_step_ft * f64::from(k), 1.0)).collect()
    }

    fn sample_altitude<R: Rng>(&self, rng: &mut R) -> f64 {
        let levels = &self.altitude_levels;
        if levels.iter().all(|(_, w)| *w == levels[0].1) {
            // u32, not usize: the integer width changes which random words are consumed.
            return levels[rng.gen_range(0..=(levels.len() - 1) as u32) as usize].0;
        }
        let total: f64 = levels.iter().map(|(_, w)| w).sum();
        let mut u = rng.gen::<f64>() * total;
        for (level, weight) in levels {
            if u < *weight {
                return *level;
            }
            u -= weight;
        }
        levels[levels.len() - 1].0
    }
}

/// A flight plan imposed by a route hypothesis (the estimate itself has none).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Guidance {
    /// Waypoints (latitude, longitude in degrees) flown in order along great circles.
    pub waypoints: Vec<(f64, f64)>,
    /// What the aircraft does after the last waypoint.
    pub after: AfterRoute,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum AfterRoute {
    /// Resume the estimate's model: the particle's own autopilot mode, random manoeuvres.
    Free,
    /// Lateral navigation to a fixed point for the rest of the flight (no random turns).
    Destination { lat: f64, lon: f64 },
    /// Hold `mode` at this control angle for the rest of the flight (no random turns);
    /// degrees, magnetic for magnetic modes.
    Hold { mode: Mode, angle_deg: f64 },
}

/// Where a guided aircraft is in its plan.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Phase {
    Route(usize),
    Destination(f64, f64),
    Hold,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct GuidanceState {
    pub plan: Guidance,
    pub phase: Phase,
    /// The autopilot mode the particle was drawn with, resumed by `AfterRoute::Free`.
    pub free_mode: Mode,
}

/// A waypoint counts as reached within this distance (or once it is behind the aircraft).
const CAPTURE_NM: f64 = 2.0;
/// Course corrections below this are applied directly rather than flown as a banked turn.
const DIRECT_CORRECTION_RAD: f64 = 1.0 * PI / 180.0;

/// Air data behind the current ground velocity.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct AirData {
    pub true_air_speed_kt: f64,
    /// True air heading, radians from north (after declination in the magnetic modes).
    pub heading_rad: f64,
    /// Nominal wind (times the environment's wind scale) plus the wind-error state.
    pub wind_north_kt: f64,
    pub wind_east_kt: f64,
    pub temperature_k: f64,
}

/// The full dynamic state. It serialises completely (guidance included), so a trajectory
/// written at one epoch continues exactly when read back.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Aircraft {
    pub unix_s: f64,
    pub lat: f64,
    pub lon: f64,
    pub alt_ft: f64,
    alt_target_ft: f64,
    /// Mach set point (ramps towards its target during an acceleration).
    pub mach: f64,
    mach_target: f64,
    mach_deviation: f64,
    /// Control-angle set point, radians; its meaning depends on `mode`.
    control: f64,
    turn_remaining: f64,
    control_deviation: f64,
    wind_error_north_kt: f64,
    wind_error_east_kt: f64,
    pub mode: Mode,
    lnav_switch_unix_s: f64,
    lnav_switch_to: Mode,
    pub tau_s: f64,
    next_turn: f64,
    next_acceleration: f64,
    /// Fuel on board, kg. NaN when the run does not model fuel.
    pub fuel_kg: f64,
    /// Time the last engine stopped, unix seconds; NaN while fuel remains or when not modelled.
    pub fuel_exhausted_unix_s: f64,
    /// This path's draw from the fuel-flow factor prior, N(1.0085, 0.0178).
    fuel_factor: f64,
    /// Seconds flown with the flight level below FL060, where only one speed schedule is
    /// tabulated and the flow is taken at FL060 instead.
    pub fuel_below_tables_s: f64,
    /// Seconds for which the tables returned NO flow at all, so the step burnt nothing. This
    /// used to be pooled into `fuel_below_tables_s`, which hid it: the FL060 clamp burns at a
    /// much HIGHER flow than cruise while this burns at zero, so pooling them made a
    /// fuel-conserving defect look like an altitude-clamp diagnostic. Any nonzero value here is
    /// a bug, not a modelling choice — a trajectory cannot fly without burning.
    pub fuel_no_flow_s: f64,
    /// Why the last no-flow step had no flow, as a small code so the cause can be read off the
    /// saved state without a debugger: 0 none, 1 a non-finite flight level, 2 a non-finite Mach,
    /// 3 a non-finite weight, 4 the tables genuinely had no bracketing pair.
    pub fuel_no_flow_cause: f64,
    /// Seconds flown at a Mach outside the bracketing schedules, where the drag law is
    /// extrapolated rather than interpolated.
    pub fuel_extrapolated_s: f64,
    /// Seconds flown above the service ceiling for the aircraft's weight, where the tables are
    /// empty because the airframe could not sustain the state.
    pub fuel_above_ceiling_s: f64,
    /// Set once the remaining fuel cannot reach the endurance deadline even on the cheapest
    /// continuation the tables allow, so the path is certain to be rejected there.
    pub fuel_doomed: bool,
    /// Log of the prior-to-proposal density ratio accumulated by the endurance speed proposal,
    /// not yet taken into the particle's weight. The filter drains it each step.
    pub fuel_log_weight_correction: f64,
    /// Mach targets drawn from the endurance-restricted part of the mixture. Output-only.
    pub fuel_guided_draws: u16,
    /// The arc the next epoch puts the aircraft on, when the bridge proposal is enabled. Set by
    /// the filter before each step; transient within a step, so it is never serialised and a
    /// deserialised aircraft resumes with turns on the prior until the filter sets it again.
    #[serde(skip)]
    pub arc_target: Option<ArcTarget>,
    /// Turns drawn from the arc-directed part of the mixture. Output-only.
    pub bridged_turns: u16,
    next_climb: f64,
    pub turns: u16,
    pub accelerations: u16,
    pub climbs: u16,
    /// Total angle turned by commanded turns since the start (radians, unsigned). Output-only.
    pub turned_rad: f64,
    /// Time each manoeuvre clock has run (turn, acceleration, climb), s: the exposure in Eq. 7.3.
    exposure_s: [f64; 3],
    /// Ground velocity at `unix_s`, knots.
    pub v_north_kt: f64,
    pub v_east_kt: f64,
    /// Environment at the last lookup. In steady cruise it is refreshed every
    /// `ENVIRONMENT_REFRESH_S`; the grids are hourly at 0.5 deg, so the change over
    /// one minute (~15 km) is far below the wind-error process (5.7 kt SD).
    weather: Weather,
    declination_rad: f64,
    environment_age_s: f64,
    /// Present only for aircraft following a hypothesis's flight plan.
    pub guidance: Option<Box<GuidanceState>>,
    /// Present only when `Parameters::early` is configured.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub early: Option<Box<EarlyRecord>>,
}

const ENVIRONMENT_REFRESH_S: f64 = 60.0;

/// The fuel tables plus the declared prior, shared by every particle in a run.
pub struct FuelModel {
    pub tables: fuel::FuelTables,
    pub initial_kg: f64,
    pub zfw_kg: f64,
    pub factor_mean: f64,
    pub factor_sd: f64,
    /// Endurance-aware proposal, when one is configured: the time the aircraft must still have
    /// had fuel at, and how much of the speed proposal is left on the prior.
    ///
    /// Without this the filter proposes a speed and altitude profile that knows nothing about
    /// the tank, burns fuel along it, and rejects the path at the deadline if it ran dry — which
    /// discarded about seven proposal paths in ten and left the survivors thinly represented in
    /// exactly the region the posterior cares about. With it the fuel state enters the proposal
    /// in two ways, both of them exact:
    ///
    /// 1. A path is killed as soon as it *cannot* reach the deadline even on the cheapest
    ///    continuation the tables allow. That set is a subset of the set the deadline rejects,
    ///    so nothing is excluded that the model would have kept; the only change is that the
    ///    rejection happens at the first epoch it is certain rather than at the deadline, so
    ///    resampling reallocates the effort while there is still flight left to explore.
    /// 2. A new Mach target is drawn from a mixture of the prior and the prior restricted to
    ///    the Mach values the remaining fuel can actually sustain to the deadline, and the
    ///    importance weight is corrected by the exact prior-to-proposal density ratio. The
    ///    mixture keeps the proposal's support equal to the prior's, so the correction is
    ///    bounded and the target distribution is unchanged.
    pub endurance: Option<EnduranceProposal>,
}

/// Where the next arc is, expressed as pure geometry so this crate need not know the
/// measurement model. The filter converts the epoch's BTO into a required aircraft-to-satellite
/// range and hands over the satellite position with it.
#[derive(Clone, Copy, Debug)]
pub struct ArcTarget {
    pub unix_s: f64,
    pub satellite_km: geo::Vec3,
    /// Range from aircraft to satellite the measurement implies, km.
    pub range_km: f64,
    /// One measurement standard deviation in the same units.
    pub sd_km: f64,
    /// Weight left on the unmodified prior, so the proposal keeps the prior's support.
    pub prior_mix: f64,
    /// Candidate turn angles evaluated.
    pub cells: usize,
    /// How many standard deviations count as reaching the arc.
    pub window_sd: f64,
}

/// Settings for the endurance-aware speed proposal.
#[derive(Clone, Copy, Debug)]
pub struct EnduranceProposal {
    /// The deadline the aircraft must still have had fuel at, as a Unix time.
    pub deadline_unix_s: f64,
    /// Weight left on the unmodified prior, so the proposal covers the prior's whole support.
    pub prior_mix: f64,
    /// Mach cells the affordable set is resolved on.
    pub cells: usize,
}

impl std::fmt::Debug for FuelModel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("FuelModel")
            .field("initial_kg", &self.initial_kg)
            .field("zfw_kg", &self.zfw_kg)
            .field("factor_mean", &self.factor_mean)
            .field("factor_sd", &self.factor_sd)
            .finish_non_exhaustive()
    }
}

impl FuelModel {
    pub fn new(tables: fuel::FuelTables, prior: fuel::FuelPrior) -> Self {
        Self {
            tables,
            initial_kg: prior.initial_kg,
            zfw_kg: prior.zfw_kg,
            factor_mean: prior.factor_mean,
            factor_sd: prior.factor_sd,
            endurance: None,
        }
    }
}

impl Aircraft {
    /// Draw from the prior with the autopilot mode fixed (the runner stratifies by mode).
    pub fn sample<R: Rng>(prior: &Prior, mode: Mode, p: &Parameters, env: &impl Environment, rng: &mut R) -> Self {
        let normal = |rng: &mut R| -> f64 { StandardNormal.sample(rng) };
        let (m, n) = radii_of_curvature_km(prior.lat);
        let sd_km = prior.position_sd_nm * geo::KM_PER_NM;
        let lat = prior.lat + (normal(rng) * sd_km / m).to_degrees();
        let lon = prior.lon + (normal(rng) * sd_km / (n * prior.lat.to_radians().cos())).to_degrees();
        let track = (prior.track_deg + prior.track_sd_deg * normal(rng)).to_radians();
        let alt_ft = prior.sample_altitude(rng);
        let mach = match prior.mach_gaussian {
            None => rng.gen_range(prior.mach_range.0..prior.mach_range.1),
            Some((mean, sd)) => mean + sd * normal(rng),
        };
        let (ln_lo, ln_hi) = (p.tau_range_h.0.ln(), p.tau_range_h.1.ln());
        let tau_s = rng.gen_range(ln_lo..ln_hi).exp() * 3600.0;
        let exp = |rng: &mut R| -> f64 { Exp1.sample(rng) };

        let mut a = Self {
            unix_s: prior.unix_s,
            lat,
            lon,
            alt_ft,
            alt_target_ft: alt_ft,
            mach,
            mach_target: mach,
            mach_deviation: normal(rng) * Parameters::stationary_sd(p.mach_reversion_per_s, p.mach_noise_per_s),
            control: 0.0,
            turn_remaining: 0.0,
            control_deviation: normal(rng) * Parameters::stationary_sd(p.angle_reversion_per_s, p.angle_noise_rad2_per_s),
            wind_error_north_kt: normal(rng) * Parameters::stationary_sd(p.wind_reversion_per_s, p.wind_noise_kt2_per_s),
            wind_error_east_kt: normal(rng) * Parameters::stationary_sd(p.wind_reversion_per_s, p.wind_noise_kt2_per_s),
            mode,
            lnav_switch_unix_s: prior.unix_s + exp(rng) * p.lnav_switch_mean_s,
            lnav_switch_to: if rng.gen_bool(0.5) { Mode::TrueHeading } else { Mode::MagneticHeading },
            tau_s,
            next_turn: prior.unix_s + exp(rng) * tau_s,
            next_acceleration: prior.unix_s + exp(rng) * tau_s,
            next_climb: prior.unix_s + exp(rng) * tau_s,
            // The factor is a per-path draw from the calibration's own uncertainty, so the
            // posterior integrates over how well the tables describe this airframe rather than
            // conditioning on the point estimate.
            fuel_kg: match &p.fuel {
                None => f64::NAN,
                Some(f) => f.initial_kg,
            },
            fuel_exhausted_unix_s: f64::NAN,
            fuel_factor: match &p.fuel {
                None => f64::NAN,
                Some(f) => f.factor_mean + f.factor_sd * normal(rng),
            },
            arc_target: None,
            bridged_turns: 0,
            fuel_doomed: false,
            fuel_log_weight_correction: 0.0,
            fuel_guided_draws: 0,
            fuel_below_tables_s: 0.0,
            fuel_no_flow_s: 0.0,
            fuel_no_flow_cause: 0.0,
            fuel_extrapolated_s: 0.0,
            fuel_above_ceiling_s: 0.0,
            turns: 0,
            accelerations: 0,
            climbs: 0,
            exposure_s: [0.0; 3],
            turned_rad: 0.0,
            v_north_kt: 0.0,
            v_east_kt: 0.0,
            weather: Weather { temperature_k: 0.0, wind_east_kt: 0.0, wind_north_kt: 0.0 },
            declination_rad: 0.0,
            environment_age_s: 0.0,
            guidance: None,
            early: None,
        };
        if let Some(e) = &p.early {
            a.early = Some(Box::new(draw_early(e, p, a.alt_ft, a.mach, rng)));
        }
        a.refresh_environment(env);
        // The prior direction is a ground track; express it in the mode's control angle.
        let w = a.weather;
        let declination = a.declination_rad;
        let reference = if a.mode.holds_heading() {
            let (wn, we) = (w.wind_north_kt + a.wind_error_north_kt, w.wind_east_kt + a.wind_error_east_kt);
            let air = a.air_speed_kt(w.speed_of_sound_kt());
            let cross = -wn * track.sin() + we * track.cos();
            track - (cross / air).clamp(-1.0, 1.0).asin()
        } else {
            track
        };
        a.control = wrap_pi(reference - if a.mode.magnetic() { declination } else { 0.0 } - a.control_deviation);
        a.update_ground_velocity(env);
        a
    }

    fn air_speed_kt(&self, speed_of_sound_kt: f64) -> f64 {
        (self.mach + self.mach_deviation) * speed_of_sound_kt
    }

    fn refresh_environment(&mut self, env: &impl Environment) {
        self.weather = env.weather(self.unix_s, self.alt_ft, self.lat, self.lon);
        if self.mode.magnetic() || self.lnav_switch_to.magnetic() {
            self.declination_rad = env.declination_deg(self.alt_ft, self.lat, self.lon).to_radians();
        }
        self.environment_age_s = 0.0;
    }

    /// Ground velocity (north, east kt), true air speed (kt) and wind (north, east kt)
    /// from the cached environment.
    fn kinematics(&self) -> (f64, f64, f64, f64, f64) {
        let w = self.weather;
        let air = self.air_speed_kt(w.speed_of_sound_kt());
        let (wn, we) = (w.wind_north_kt + self.wind_error_north_kt, w.wind_east_kt + self.wind_error_east_kt);
        let mut angle = self.control + self.control_deviation;
        if self.mode.magnetic() {
            angle += self.declination_rad;
        }
        let (s, c) = angle.sin_cos();
        let (vn, ve) = if self.mode.holds_heading() {
            (air * c + wn, air * s + we)
        } else {
            // Eq. 6.18: ground speed along a commanded track with a known wind.
            let along = wn * c + we * s;
            let cross = -wn * s + we * c;
            let gs = along + (air * air - cross * cross).max(0.0).sqrt();
            (gs * c, gs * s)
        };
        (vn, ve, air, wn, we)
    }

    /// Air data from the same values `kinematics` uses, so air velocity plus wind is the
    /// ground velocity.
    /// This path's fuel-flow factor, the multiplier its burn applies to the tables. Read-only:
    /// the terminal stage prices a descent with the same factor the cruise used.
    pub fn fuel_factor(&self) -> f64 {
        self.fuel_factor
    }

    pub fn air_data(&self) -> AirData {
        let (vn, ve, air, wn, we) = self.kinematics();
        AirData {
            true_air_speed_kt: air,
            heading_rad: (ve - we).atan2(vn - wn),
            wind_north_kt: wn,
            wind_east_kt: we,
            temperature_k: self.weather.temperature_k,
        }
    }

    /// Vertical speed, ft/min: plus or minus the climb rate during a level change, else zero.
    pub fn vertical_speed_fpm(&self, p: &Parameters) -> f64 {
        if let Some(x) = self.active_excursion() {
            return x.vertical_fpm_at(self.unix_s);
        }
        if self.alt_ft == self.alt_target_ft {
            0.0
        } else {
            (p.climb_rate_ft_per_s * 60.0).copysign(self.alt_target_ft - self.alt_ft)
        }
    }

    /// Burn `dt` seconds of fuel at the current flight level, weight and Mach.
    ///
    /// Weight falls as fuel burns, so the flow is re-read every step rather than held at the
    /// initial weight. Once the tank is empty the engines have stopped: the time is recorded
    /// and nothing further is burnt. A step whose flow falls outside the tables still burns —
    /// at the clamped or extrapolated value — and its duration is accumulated so the report can
    /// say how much of each trajectory rests on an extrapolation.
    fn burn_fuel(&mut self, p: &Parameters, dt: f64) {
        let Some(model) = &p.fuel else { return };
        if !(self.fuel_kg > 0.0) {
            return;
        }
        let weight_t = (model.zfw_kg + self.fuel_kg) / 1000.0;
        let Some((flow_kg_h, cover)) = model.tables.fuel_flow_kg_h(self.alt_ft / 100.0, weight_t, self.mach) else {
            // The tables gave no flow. This is counted separately from the FL060 clamp because
            // the two have OPPOSITE effects on the burn - the clamp burns at a much higher flow
            // than cruise, this burns nothing - and pooling them hid a defect for weeks. A
            // trajectory cannot fly without burning, so any time accumulated here is a bug.
            // The cause is recorded so it can be read off the saved state.
            self.fuel_no_flow_s += dt;
            self.fuel_no_flow_cause = if !(self.alt_ft / 100.0).is_finite() {
                1.0
            } else if !self.mach.is_finite() {
                2.0
            } else if !weight_t.is_finite() {
                3.0
            } else {
                4.0
            };
            return;
        };
        if cover.below_tables {
            self.fuel_below_tables_s += dt;
        }
        if cover.extrapolated_mach || cover.single_schedule || cover.fit_fallback {
            self.fuel_extrapolated_s += dt;
        }
        if cover.above_ceiling {
            self.fuel_above_ceiling_s += dt;
        }
        let burn = flow_kg_h * self.fuel_factor * dt / 3600.0;
        if burn >= self.fuel_kg {
            // Exhaustion inside this step: interpolate the moment linearly in the step.
            self.fuel_exhausted_unix_s = self.unix_s + dt * self.fuel_kg / burn;
            self.fuel_kg = 0.0;
        } else {
            self.fuel_kg -= burn;
        }
        self.mark_doomed_if_short(model);
    }

    /// Flag the path once no continuation can reach the endurance deadline.
    ///
    /// The test is against `min_flow_kg_h`, the cheapest flow the tables offer at this weight
    /// over every level and speed, so it fires only when the deadline is unreachable however
    /// the aircraft is subsequently flown. A path that fails it would be rejected at the
    /// deadline in any case; flagging it here lets the filter drop it at the next resampling
    /// instead of carrying it to the end.
    fn mark_doomed_if_short(&mut self, model: &FuelModel) {
        let Some(e) = model.endurance else { return };
        if self.fuel_doomed || self.unix_s >= e.deadline_unix_s {
            return;
        }
        if !(self.fuel_kg > 0.0) {
            self.fuel_doomed = true;
            return;
        }
        let weight_t = (model.zfw_kg + self.fuel_kg) / 1000.0;
        let Some(min_flow) = model.tables.min_flow_kg_h(weight_t) else { return };
        let needed = min_flow * self.fuel_factor * (e.deadline_unix_s - self.unix_s) / 3600.0;
        if self.fuel_kg < needed {
            self.fuel_doomed = true;
        }
    }

    fn update_ground_velocity(&mut self, env: &impl Environment) {
        self.refresh_environment(env);
        let (vn, ve, ..) = self.kinematics();
        self.v_north_kt = vn;
        self.v_east_kt = ve;
    }

    /// Advance the aircraft to `unix_s`, sampling manoeuvres and cruise noise.
    pub fn propagate<R: Rng>(&mut self, unix_s: f64, p: &Parameters, env: &impl Environment, rng: &mut R) {
        let normal = |rng: &mut R| -> f64 { StandardNormal.sample(rng) };
        while self.unix_s < unix_s {
            if self.early.is_some() {
                self.early_events(p, env, rng);
            }
            self.start_due_manoeuvres(p, env, rng);
            if self.guidance.is_some() {
                self.steer(env, rng);
            }
            let excursion = self.active_excursion().cloned();
            let manoeuvring = self.turn_remaining != 0.0
                || self.mach != self.mach_target
                || self.alt_ft != self.alt_target_ft
                || excursion.is_some();
            let mut dt = if manoeuvring { p.manoeuvre_step_s } else { p.cruise_step_s };
            dt = dt.min(unix_s - self.unix_s);
            for event in [self.next_turn, self.next_acceleration, self.next_climb, self.lnav_switch_time()] {
                if event > self.unix_s {
                    dt = dt.min(event - self.unix_s);
                }
            }
            if self.early.is_some() {
                for event in self.early_event_times() {
                    if event > self.unix_s {
                        dt = dt.min(event - self.unix_s);
                    }
                }
            }

            // The random-turn clock does not run while a flight plan steers.
            let turn_clock = self.turn_remaining == 0.0 && self.guidance.is_none();
            for (exposure, running) in self.exposure_s.iter_mut().zip([
                turn_clock,
                self.mach == self.mach_target && excursion.is_none(),
                self.alt_ft == self.alt_target_ft && excursion.is_none(),
            ]) {
                if running {
                    *exposure += dt;
                }
            }
            if manoeuvring || self.environment_age_s >= ENVIRONMENT_REFRESH_S {
                self.refresh_environment(env);
            }
            // Turn increment for this step (fixed-bank rate, Eq. 7.4). Half is applied before the
            // position update and half after, so the path is second-order accurate in dt.
            let mut turn_step = 0.0;
            if self.turn_remaining != 0.0 {
                let air = self.air_speed_kt(self.weather.speed_of_sound_kt());
                let rate = 9.806_65 * p.bank_angle_deg.to_radians().tan() / (air * MPS_PER_KNOT);
                turn_step = self.turn_remaining.abs().min(rate * dt).copysign(self.turn_remaining);
                self.control += 0.5 * turn_step;
            }
            let (vn, ve, ..) = self.kinematics();
            let (lat, lon) = advance(self.lat, self.lon, self.alt_ft, vn, ve, dt);
            if self.mode == Mode::LateralNavigation {
                // Great-circle course drift: d(azimuth)/dt = v_east tan(lat) / R.
                let (_, radius) = radii_of_curvature_km(self.lat);
                self.control += ve * KM_S_PER_KT * self.lat.to_radians().tan() / (radius + self.alt_ft * KM_PER_FT) * dt;
            }
            self.lat = lat;
            self.lon = lon;

            if turn_step != 0.0 {
                self.control += 0.5 * turn_step;
                self.turn_remaining -= turn_step;
                self.turned_rad += turn_step.abs();
                if self.turn_remaining.abs() < 1e-12 {
                    self.turn_remaining = 0.0;
                    if self.guidance.is_none() {
                        self.next_turn = self.unix_s + dt + self.exp_gap(rng);
                    }
                }
            }
            if let Some(x) = &excursion {
                // The scripted profile replaces the speed and altitude manoeuvres; their clocks
                // are suspended (and accrue no exposure) until it ends.
                self.alt_ft = x.altitude_at(self.unix_s + dt);
                self.alt_target_ft = self.alt_ft;
                self.mach = x.mach_at(self.alt_ft);
                self.mach_target = self.mach;
            } else if self.mach != self.mach_target {
                self.mach = step_towards(self.mach, self.mach_target, p.mach_rate_per_s * dt);
                if self.mach == self.mach_target {
                    self.next_acceleration = self.unix_s + dt + self.exp_gap(rng);
                }
            }
            if excursion.is_none() && self.alt_ft != self.alt_target_ft {
                self.alt_ft = step_towards(self.alt_ft, self.alt_target_ft, p.climb_rate_ft_per_s * dt);
                if self.alt_ft == self.alt_target_ft {
                    self.next_climb = self.unix_s + dt + self.exp_gap(rng);
                }
            }

            let ou = |x: f64, beta: f64, q: f64, rng: &mut R| {
                let phi = (-beta * dt).exp();
                x * phi + (q / (2.0 * beta) * (1.0 - phi * phi)).sqrt() * normal(rng)
            };
            self.burn_fuel(p, dt);
            self.mach_deviation = ou(self.mach_deviation, p.mach_reversion_per_s, p.mach_noise_per_s, rng);
            self.control_deviation = ou(self.control_deviation, p.angle_reversion_per_s, p.angle_noise_rad2_per_s, rng);
            self.wind_error_north_kt = ou(self.wind_error_north_kt, p.wind_reversion_per_s, p.wind_noise_kt2_per_s, rng);
            self.wind_error_east_kt = ou(self.wind_error_east_kt, p.wind_reversion_per_s, p.wind_noise_kt2_per_s, rng);
            self.unix_s += dt;
            self.environment_age_s += dt;
        }
        self.control = wrap_pi(self.control);
        self.update_ground_velocity(env);
    }

    /// The vertical excursion in progress, if any.
    pub fn active_excursion(&self) -> Option<&Excursion> {
        self.early.as_deref()?.excursion.as_ref().filter(|x| x.started && !x.done)
    }

    /// Times at which a step must end so an early-phase event is applied on time.
    fn early_event_times(&self) -> [f64; 6] {
        let mut t = [f64::INFINITY; 6];
        let Some(rec) = self.early.as_deref() else { return t };
        if let Some(r) = rec.route.as_ref().filter(|r| !r.started) {
            t[5] = r.unix_s;
        }
        if let Some(turn) = rec.turn.as_ref().filter(|turn| !turn.done) {
            t[0] = turn.unix_s;
        }
        if let Some(x) = rec.excursion.as_ref().filter(|x| !x.done) {
            t[1..5].copy_from_slice(&[x.start_s, x.low_s, x.climb_s, x.end_s]);
        }
        t
    }

    /// Apply any early-phase event now due: the fixed-time turn, and the start or end of the
    /// vertical excursion.
    fn early_events<R: Rng>(&mut self, p: &Parameters, env: &impl Environment, rng: &mut R) {
        let now = self.unix_s;
        let Some(rec) = self.early.as_deref() else { return };
        if let Some(route) = rec.route.clone().filter(|r| !r.started && now >= r.unix_s) {
            if let Some(routes) = p.early.as_ref().and_then(|e| e.routes.as_ref()) {
                let waypoints = routes.routes[route.index as usize].clone();
                self.set_guidance(Guidance { waypoints, after: AfterRoute::Free }, env, rng);
            }
            if let Some(r) = self.early.as_mut().and_then(|r| r.route.as_mut()) {
                r.started = true;
            }
        }
        let Some(rec) = self.early.as_deref() else { return };
        let turn = rec.turn.clone().filter(|turn| !turn.done && now >= turn.unix_s);
        let mut excursion = rec.excursion.clone();
        if let Some(turn) = turn {
            // Turn from the present ground track to the drawn one, by the shorter way. The
            // change of ground track stands in for the change of control angle in every mode.
            self.refresh_environment(env);
            let (vn, ve, ..) = self.kinematics();
            self.turn_remaining = wrap_pi(turn.track_deg.to_radians() - ve.atan2(vn));
            self.next_turn = if self.turn_remaining == 0.0 { now + self.exp_gap(rng) } else { f64::INFINITY };
            if let Some(t) = self.early.as_mut().and_then(|r| r.turn.as_mut()) {
                t.done = true;
            }
        }
        if let Some(x) = excursion.as_mut() {
            if !x.started && now >= x.start_s {
                // Begin from wherever the aircraft is now; a speed or altitude change already
                // under way is abandoned. If the level changed since the draw, keep the drawn
                // rates and slide the climb (and end) later if the descent now takes longer.
                x.started = true;
                x.start_s = now;
                x.from_ft = self.alt_ft.max(x.low_ft);
                x.low_s = now + (x.from_ft - x.low_ft) / x.descent_fpm * 60.0;
                if x.low_s > x.climb_s {
                    x.climb_s = x.low_s;
                    x.end_s = x.climb_s + (x.end_ft - x.low_ft) / x.climb_fpm * 60.0;
                }
                self.next_acceleration = f64::INFINITY;
                self.next_climb = f64::INFINITY;
                self.alt_target_ft = self.alt_ft;
                self.mach = x.mach_at(self.alt_ft);
                self.mach_target = self.mach;
            } else if x.started && !x.done && now >= x.end_s {
                x.done = true;
                self.alt_ft = x.end_ft;
                self.alt_target_ft = x.end_ft;
                self.mach_target = x.resume_mach;
                self.next_climb = now + self.exp_gap(rng);
                if self.mach == self.mach_target {
                    self.next_acceleration = now + self.exp_gap(rng);
                }
            }
            if let Some(r) = self.early.as_mut() {
                r.excursion = excursion;
            }
        }
    }

    /// Gibbs update of the static manoeuvre time constant given this path's history.
    ///
    /// With the Jeffreys prior (Eq. 7.6) and the path likelihood tau^-N exp(-E/tau)
    /// (Eq. 7.3 over the three independent manoeuvre types), the rate lambda = 1/tau has
    /// density proportional to lambda^(N-1) exp(-E lambda) on [1/tau_max, 1/tau_min].
    /// Pending gaps are memoryless, so running clocks are redrawn from the new tau.
    /// This keeps duplicated particles from sharing a handful of tau values after resampling.
    pub fn refresh_manoeuvre_rate<R: Rng>(&mut self, p: &Parameters, rng: &mut R) {
        const GRID: usize = 512;
        let n = f64::from(self.turns + self.accelerations + self.climbs);
        let e: f64 = self.exposure_s.iter().sum();
        let (lo, hi) = ((1.0 / (p.tau_range_h.1 * 3600.0)).ln(), (1.0 / (p.tau_range_h.0 * 3600.0)).ln());
        // Log density in u = ln(lambda): n u - e exp(u) (log-concave); inverse CDF on a fine grid.
        let du = (hi - lo) / GRID as f64;
        let log_density = |u: f64| n * u - e * u.exp();
        let peak = (0..=GRID).map(|i| log_density(lo + i as f64 * du)).fold(f64::NEG_INFINITY, f64::max);
        let mut cdf = [0.0; GRID + 1];
        let mut previous = (log_density(lo) - peak).exp();
        for i in 1..=GRID {
            let current = (log_density(lo + i as f64 * du) - peak).exp();
            cdf[i] = cdf[i - 1] + 0.5 * (previous + current);
            previous = current;
        }
        let target = rng.gen::<f64>() * cdf[GRID];
        let i = cdf.partition_point(|&c| c < target).clamp(1, GRID);
        let fraction = (target - cdf[i - 1]) / (cdf[i] - cdf[i - 1]).max(f64::MIN_POSITIVE);
        self.tau_s = (-(lo + (i as f64 - 1.0 + fraction) * du)).exp();

        let now = self.unix_s;
        for next in [&mut self.next_turn, &mut self.next_acceleration, &mut self.next_climb] {
            if next.is_finite() {
                let gap: f64 = Exp1.sample(rng);
                *next = now + gap * self.tau_s;
            }
        }
    }

    /// Follow `plan` from now on: fly true track along its waypoints, then apply its
    /// after-route policy. Random turns stop while the plan steers; speed and altitude
    /// changes and all cruise noise continue as in the estimate.
    pub fn set_guidance<R: Rng>(&mut self, plan: Guidance, env: &impl Environment, rng: &mut R) {
        let free_mode = self.mode;
        self.enter_mode(Mode::TrueTrack, env);
        self.next_turn = f64::INFINITY;
        self.guidance = Some(Box::new(GuidanceState { plan, phase: Phase::Route(0), free_mode }));
        self.steer(env, rng);
    }

    /// Switch autopilot mode keeping the current air heading (heading modes) or ground
    /// track (track modes).
    fn enter_mode(&mut self, mode: Mode, env: &impl Environment) {
        self.refresh_environment(env);
        let (vn, ve, _, wn, we) = self.kinematics();
        self.mode = mode;
        self.refresh_environment(env);
        let mut angle = if mode.holds_heading() { (ve - we).atan2(vn - wn) } else { ve.atan2(vn) };
        if mode.magnetic() {
            angle -= self.declination_rad;
        }
        self.control = angle - self.control_deviation;
        self.turn_remaining = 0.0;
    }

    /// Point the control angle at the plan's current target; advance the plan when a
    /// waypoint is reached.
    fn steer<R: Rng>(&mut self, env: &impl Environment, rng: &mut R) {
        loop {
            let Some(g) = self.guidance.as_deref() else { return };
            let target = match g.phase {
                Phase::Route(i) if i < g.plan.waypoints.len() => g.plan.waypoints[i],
                Phase::Route(_) => {
                    let after = g.plan.after;
                    self.finish_route(after, env, rng);
                    continue;
                }
                Phase::Destination(lat, lon) => (lat, lon),
                Phase::Hold => return,
            };
            let (bearing, distance_nm) = bearing_and_distance((self.lat, self.lon), target);
            let error = wrap_pi(bearing - self.control - self.control_deviation);
            if let Phase::Route(i) = g.phase {
                if distance_nm < CAPTURE_NM || error.abs() > PI / 2.0 {
                    self.guidance.as_mut().unwrap().phase = Phase::Route(i + 1);
                    continue;
                }
            }
            if error.abs() < DIRECT_CORRECTION_RAD {
                self.control += error;
                self.turn_remaining = 0.0;
            } else {
                self.turn_remaining = error;
            }
            return;
        }
    }

    fn finish_route<R: Rng>(&mut self, after: AfterRoute, env: &impl Environment, rng: &mut R) {
        match after {
            AfterRoute::Free => {
                let mode = self.guidance.take().unwrap().free_mode;
                self.enter_mode(mode, env);
                self.next_turn = self.unix_s + self.exp_gap(rng);
            }
            AfterRoute::Destination { lat, lon } => {
                self.guidance.as_mut().unwrap().phase = Phase::Destination(lat, lon);
            }
            AfterRoute::Hold { mode, angle_deg } => {
                self.enter_mode(mode, env);
                self.turn_remaining = wrap_pi(angle_deg.to_radians() - self.control - self.control_deviation);
                self.guidance.as_mut().unwrap().phase = Phase::Hold;
            }
        }
    }

    fn lnav_switch_time(&self) -> f64 {
        if self.mode == Mode::LateralNavigation { self.lnav_switch_unix_s } else { f64::INFINITY }
    }

    fn exp_gap<R: Rng>(&self, rng: &mut R) -> f64 {
        let e: f64 = Exp1.sample(rng);
        e * self.tau_s
    }

    /// A new turn: uniform on the prior's full circle, or, with an arc target set, from a
    /// mixture that favours turns which bring the aircraft onto the next arc.
    ///
    /// This is the two-ended half of the sampler. The endurance proposal steers speed using
    /// what is known at the start of a leg; this steers heading using where the leg has to end.
    /// It exists because the 19:41 crossing is tangential - one BTO standard deviation admits
    /// about 122 NM along track against 4.2 NM across it - so the arc accepts a thin sliver of
    /// headings and an unguided turn almost never lands in it.
    ///
    /// Each candidate turn is scored by dead-reckoning the resulting ground track to the target
    /// epoch and measuring the aircraft-to-satellite range there. That ignores the wind change
    /// and any later manoeuvre over the leg, which is why the prior keeps a share of the
    /// mixture and why the window is several standard deviations wide: the proposal only has to
    /// be better than uniform, and the exact prior-to-proposal ratio accumulated here makes any
    /// error in it a question of efficiency rather than of correctness.
    fn draw_turn<R: Rng>(&mut self, rng: &mut R) -> f64 {
        let Some(t) = self.arc_target else { return rng.gen_range(-PI..PI) };
        let dt = t.unix_s - self.unix_s;
        if dt <= 0.0 {
            return rng.gen_range(-PI..PI);
        }
        let speed_kt = self.v_north_kt.hypot(self.v_east_kt);
        if !(speed_kt > 0.0) {
            return rng.gen_range(-PI..PI);
        }
        let track = self.v_east_kt.atan2(self.v_north_kt);
        let cells = t.cells.max(4);
        let width = 2.0 * PI / cells as f64;
        // Dead-reckon each candidate turn and mark those that reach the arc.
        let mut ok = vec![false; cells];
        let mut hits = 0usize;
        for (c, slot) in ok.iter_mut().enumerate() {
            let turn = -PI + width * (c as f64 + 0.5);
            let b = track + turn;
            let (lat, lon) = geo::advance(
                self.lat, self.lon, self.alt_ft,
                speed_kt * b.cos(), speed_kt * b.sin(), dt);
            let r = (t.satellite_km - geo::lla_to_ecef(lat, lon, self.alt_ft * KM_PER_FT)).norm();
            if (r - t.range_km).abs() <= t.window_sd * t.sd_km {
                *slot = true;
                hits += 1;
            }
        }
        if hits == 0 || hits == cells {
            return rng.gen_range(-PI..PI);
        }
        let alpha = t.prior_mix;
        let guided = rng.gen_bool(1.0 - alpha);
        let index = if guided {
            let k = rng.gen_range(0..hits);
            ok.iter().enumerate().filter(|(_, &b)| b).map(|(i, _)| i).nth(k).unwrap_or(0)
        } else {
            rng.gen_range(0..cells)
        };
        let turn = -PI + width * (index as f64 + rng.gen::<f64>());
        // Prior density is 1 / 2pi everywhere; in a cell the proposal adds
        // (1 - alpha) / (hits * width) on top of alpha / 2pi.
        let q_rel = alpha + if ok[index] { (1.0 - alpha) * cells as f64 / hits as f64 } else { 0.0 };
        if guided {
            self.bridged_turns += 1;
        }
        self.fuel_log_weight_correction -= q_rel.ln();
        turn
    }

    /// A new Mach target: uniform on the prior's range, or, with an endurance proposal
    /// configured, from a mixture that favours the speeds the remaining fuel can sustain.
    ///
    /// The affordable set is resolved on a Mach grid rather than by a root-find because the
    /// `a M^2 + b / M^2` drag law is U-shaped: flow falls to the economical speed and rises
    /// either side of it, so the affordable set can be an interior interval. A cell counts as
    /// affordable if holding that Mach at the present level to the deadline costs no more than
    /// the fuel on board; that is a *sufficient* test for the cell, and the prior mixture
    /// component keeps every other cell reachable, so no trajectory the prior allows is
    /// excluded. The returned draw carries its exact log prior-to-proposal ratio into
    /// `fuel_log_weight_correction`, which the filter takes into the particle's weight.
    fn draw_mach_target<R: Rng>(&mut self, p: &Parameters, rng: &mut R) -> f64 {
        let (lo, hi) = match &p.early {
            Some(e) if self.unix_s < e.mach_until_unix_s => match e.cas_envelope_kt {
                None => e.mach_range,
                Some((cas_lo, cas_hi)) => {
                    let lo = e.mach_range.0.max(cas_to_mach(cas_lo, self.alt_ft));
                    let hi = e.mach_range.1.min(cas_to_mach(cas_hi, self.alt_ft));
                    if lo < hi {
                        (lo, hi)
                    } else {
                        // No overlap: the envelope bound nearest the declared range.
                        let m = hi.max(e.mach_range.0).min(e.mach_range.1);
                        (m, m)
                    }
                }
            },
            _ => p.mach_range,
        };
        let uniform = |rng: &mut R| if hi > lo { rng.gen_range(lo..hi) } else { lo };
        let Some(model) = &p.fuel else { return uniform(rng) };
        let Some(e) = model.endurance else { return uniform(rng) };
        let remaining_h = (e.deadline_unix_s - self.unix_s) / 3600.0;
        if remaining_h <= 0.0 || !(self.fuel_kg > 0.0) || !(hi > lo) {
            return uniform(rng);
        }
        let weight_t = (model.zfw_kg + self.fuel_kg) / 1000.0;
        let budget_kg_h = self.fuel_kg / (self.fuel_factor * remaining_h);
        let flows = model.tables.flow_grid(self.alt_ft / 100.0, weight_t, (lo, hi), e.cells);
        let affordable: Vec<bool> = flows.iter().map(|f| f.is_some_and(|f| f <= budget_kg_h)).collect();
        let n_aff = affordable.iter().filter(|&&a| a).count();
        if n_aff == 0 || n_aff == e.cells {
            // Every speed is affordable, or none is. Either way the restriction carries no
            // information and the prior is already the right proposal.
            return uniform(rng);
        }
        // Mixture: `prior_mix` on the prior, the rest uniform on the affordable cells. Both
        // components are uniform within a cell, so the density ratio is constant per cell.
        let (alpha, cells) = (e.prior_mix, e.cells as f64);
        let guided = rng.gen_bool(1.0 - alpha);
        let index = if guided {
            let k = rng.gen_range(0..n_aff);
            affordable.iter().enumerate().filter(|(_, &a)| a).map(|(i, _)| i).nth(k).unwrap_or(0)
        } else {
            rng.gen_range(0..e.cells)
        };
        let width = (hi - lo) / cells;
        let mach = lo + width * (index as f64 + rng.gen::<f64>());
        // Prior density is 1 / (hi - lo) everywhere. In a cell the proposal density is
        // alpha / (hi - lo) plus, where affordable, (1 - alpha) / (n_aff * width).
        let q_rel = alpha + if affordable[index] { (1.0 - alpha) * cells / n_aff as f64 } else { 0.0 };
        if guided {
            self.fuel_guided_draws += 1;
        }
        self.fuel_log_weight_correction -= q_rel.ln();
        mach
    }

    fn start_due_manoeuvres<R: Rng>(&mut self, p: &Parameters, env: &impl Environment, rng: &mut R) {
        // A started manoeuvre suspends its clock until it completes; a draw equal to the
        // current value (e.g. the same flight level) completes immediately.
        let now = self.unix_s;
        if self.next_turn <= now {
            self.turn_remaining = self.draw_turn(rng);
            self.turns += 1;
            self.next_turn = if self.turn_remaining == 0.0 { now + self.exp_gap(rng) } else { f64::INFINITY };
        }
        if self.next_acceleration <= now {
            self.mach_target = self.draw_mach_target(p, rng);
            self.accelerations += 1;
            self.next_acceleration = if self.mach_target == self.mach { now + self.exp_gap(rng) } else { f64::INFINITY };
        }
        if self.next_climb <= now {
            let levels = ((p.altitude_range_ft.1 - p.altitude_range_ft.0) / p.altitude_step_ft).round() as u32;
            self.alt_target_ft = p.altitude_range_ft.0 + p.altitude_step_ft * f64::from(rng.gen_range(0..=levels));
            self.climbs += 1;
            self.next_climb = if self.alt_target_ft == self.alt_ft { now + self.exp_gap(rng) } else { f64::INFINITY };
        }
        if self.lnav_switch_time() <= now {
            // Revert to heading hold, keeping the current air heading.
            self.refresh_environment(env);
            let (vn, ve, _, wn, we) = self.kinematics();
            let mut heading = (ve - we).atan2(vn - wn);
            if self.lnav_switch_to.magnetic() {
                heading -= self.declination_rad;
            }
            self.mode = self.lnav_switch_to;
            self.control = heading - self.control_deviation;
        }
    }
}

/// Initial great-circle bearing (radians from north) and distance (NM) from `a` to `b`, on a sphere.
fn bearing_and_distance(a: (f64, f64), b: (f64, f64)) -> (f64, f64) {
    let (la1, lo1, la2, lo2) = (a.0.to_radians(), a.1.to_radians(), b.0.to_radians(), b.1.to_radians());
    let d_lon = lo2 - lo1;
    let bearing = (d_lon.sin() * la2.cos()).atan2(la1.cos() * la2.sin() - la1.sin() * la2.cos() * d_lon.cos());
    let h = ((la2 - la1) / 2.0).sin().powi(2) + la1.cos() * la2.cos() * (d_lon / 2.0).sin().powi(2);
    (bearing, 2.0 * 3440.065 * h.sqrt().asin())
}

fn step_towards(value: f64, target: f64, max_step: f64) -> f64 {
    if (target - value).abs() <= max_step { target } else { value + max_step.copysign(target - value) }
}

#[cfg(test)]
mod tests {
    use super::*;
    use environment::CalmAir;
    use rand::SeedableRng;
    use rand_chacha::ChaCha8Rng;

    fn prior() -> Prior {
        Prior {
            unix_s: 0.0,
            lat: 0.0,
            lon: 90.0,
            position_sd_nm: 0.0,
            track_deg: 180.0,
            track_sd_deg: 0.0,
            mach_range: (0.73, 0.84),
            mach_gaussian: None,
            altitude_levels: Prior::uniform_altitude_levels(&Parameters::default()),
        }
    }

    fn quiet() -> Parameters {
        // No manoeuvres within the test horizon, negligible cruise noise.
        Parameters {
            tau_range_h: (1e9, 1.1e9),
            mach_noise_per_s: 1e-30,
            angle_noise_rad2_per_s: 1e-30,
            wind_noise_kt2_per_s: 1e-30,
            lnav_switch_mean_s: 1e12,
            ..Parameters::default()
        }
    }

    #[test]
    fn unmanoeuvred_cruise_flies_south_at_true_air_speed_in_still_air() {
        let mut rng = ChaCha8Rng::seed_from_u64(1);
        for _ in 0..20 {
            let mut a = Aircraft::sample(&prior(), Mode::ALL[rng.gen_range(0..5)], &quiet(), &CalmAir, &mut rng);
            let tas = a.mach * (1.4f64 * 287.052_87 * 216.65).sqrt() / MPS_PER_KNOT;
            a.propagate(3600.0, &quiet(), &CalmAir, &mut rng);
            // Independent estimate: meridional arc on WGS-84 near the equator is ~59.7 NM per degree.
            let south_nm = -a.lat * 59.7;
            assert!((south_nm - tas).abs() / tas < 0.01, "{south_nm} vs {tas} in {:?}", a.mode);
            assert!((a.lon - 90.0).abs() < 1e-6);
        }
    }

    fn fuel_model_with_endurance(deadline_unix_s: f64) -> FuelModel {
        let p = concat!(env!("CARGO_MANIFEST_DIR"), "/../../data/fuel-tables.json");
        let tables = fuel::FuelTables::from_json(&std::fs::read_to_string(p).expect("fuel tables")).unwrap();
        let mut m = FuelModel::new(tables, fuel::FuelPrior::default());
        m.endurance = Some(EnduranceProposal { deadline_unix_s, prior_mix: 0.15, cells: 16 });
        m
    }

    #[test]
    fn the_endurance_proposal_leaves_the_mach_prior_unchanged() {
        // The proposal is only legitimate if reweighting undoes it exactly. Draw Mach targets
        // through the shipped `draw_mach_target` at a fuel state tight enough that most speeds
        // are unaffordable, carry each draw's own log prior-to-proposal correction, and check
        // that the *weighted* distribution is the uniform prior the book specifies rather than
        // the skewed thing the proposal actually sampled from.
        let (deadline, fuel_kg, alt_ft) = (3.0 * 3600.0, 17_500.0, 35_000.0);
        let mut p = quiet();
        p.fuel = Some(std::sync::Arc::new(fuel_model_with_endurance(deadline)));
        let model = p.fuel.clone().unwrap();
        let (lo, hi) = p.mach_range;
        let cells = 16;

        // Check first that this state actually splits the Mach range, so the test cannot pass
        // by never engaging the restricted branch at all - which is how it passed the first
        // time it was written.
        let weight_t = (model.zfw_kg + fuel_kg) / 1000.0;
        let budget = fuel_kg / (1.0085 * deadline / 3600.0);
        let grid = model.tables.flow_grid(alt_ft / 100.0, weight_t, (lo, hi), cells);
        let n_aff = grid.iter().filter(|f| f.is_some_and(|f| f <= budget)).count();
        assert!(
            n_aff > 0 && n_aff < cells,
            "the test state must leave some speeds affordable and some not; got {n_aff} of {cells} \
             against a budget of {budget:.0} kg/h over flows {grid:?}"
        );

        let mut rng = ChaCha8Rng::seed_from_u64(11);
        let bins = 8;
        let (mut weighted, mut raw, mut total) = (vec![0.0f64; bins], vec![0.0f64; bins], 0.0);
        for _ in 0..40_000 {
            let mut a = Aircraft::sample(&prior(), Mode::TrueTrack, &p, &CalmAir, &mut rng);
            a.alt_ft = alt_ft;
            a.fuel_kg = fuel_kg;
            a.fuel_log_weight_correction = 0.0;
            let m = a.draw_mach_target(&p, &mut rng);
            let b = (((m - lo) / (hi - lo)) * bins as f64) as usize;
            let b = b.min(bins - 1);
            let w = a.fuel_log_weight_correction.exp();
            weighted[b] += w;
            raw[b] += 1.0;
            total += w;
        }
        let drawn: Vec<f64> = raw.iter().map(|c| c / 40_000.0).collect();
        assert!(
            drawn[0] > 1.6 * drawn[bins - 1],
            "the proposal should visibly favour slow cruise here, got {drawn:?}"
        );
        for (b, w) in weighted.iter().enumerate() {
            let share = w / total;
            assert!(
                (share - 1.0 / bins as f64).abs() < 0.012,
                "bin {b} carries weighted share {share}, not the uniform {}; weights {weighted:?}",
                1.0 / bins as f64
            );
        }
    }

    #[test]
    fn a_path_that_cannot_reach_the_deadline_is_flagged_early() {
        // The pruning test must fire before the deadline, not at it; that is the whole point.
        let deadline = 6.0 * 3600.0;
        let mut p = quiet();
        p.fuel = Some(std::sync::Arc::new(fuel_model_with_endurance(deadline)));
        let mut rng = ChaCha8Rng::seed_from_u64(12);
        let mut a = Aircraft::sample(&prior(), Mode::TrueTrack, &p, &CalmAir, &mut rng);
        a.fuel_kg = 3_000.0; // nowhere near six hours at any speed
        a.propagate(600.0, &p, &CalmAir, &mut rng);
        assert!(a.fuel_doomed, "a tank this small cannot reach the deadline on any continuation");
        assert!(a.unix_s < deadline, "and it should be known well before the deadline");

        let mut b = Aircraft::sample(&prior(), Mode::TrueTrack, &p, &CalmAir, &mut rng);
        b.fuel_kg = 40_000.0;
        b.propagate(600.0, &p, &CalmAir, &mut rng);
        assert!(!b.fuel_doomed, "a full tank is not doomed six hours out");
    }

    #[test]
    fn manoeuvre_counts_follow_the_exponential_gap_model() {
        // tau fixed at 1 h, no manoeuvre duration effects dominate: ~T/tau manoeuvres of each type.
        let p = Parameters { tau_range_h: (1.0, 1.0 + 1e-9), ..Parameters::default() };
        let mut rng = ChaCha8Rng::seed_from_u64(2);
        let (mut turns, mut accels, n) = (0u32, 0u32, 400);
        for _ in 0..n {
            let mut a = Aircraft::sample(&prior(), Mode::TrueTrack, &p, &CalmAir, &mut rng);
            a.propagate(6.0 * 3600.0, &p, &CalmAir, &mut rng);
            turns += u32::from(a.turns);
            accels += u32::from(a.accelerations);
        }
        // Expected just under 6 per 6 h (finite manoeuvre durations lengthen gaps slightly).
        for mean in [turns as f64 / n as f64, accels as f64 / n as f64] {
            assert!((5.0..6.3).contains(&mean), "{mean}");
        }
    }

    #[test]
    fn tau_refresh_matches_its_conditional_distribution() {
        // No manoeuvres over E: lambda density ~ lambda^-1 exp(-E lambda); with N events,
        // ~ lambda^(N-1) exp(-E lambda). Compare the sample mean of lambda with quadrature.
        let p = Parameters::default();
        let mut rng = ChaCha8Rng::seed_from_u64(4);
        let mut a = Aircraft::sample(&prior(), Mode::TrueTrack, &p, &CalmAir, &mut rng);
        for (events, exposure_h) in [(0u16, 6.0), (1, 18.0), (4, 18.0)] {
            a.turns = events;
            a.accelerations = 0;
            a.climbs = 0;
            a.exposure_s = [exposure_h * 3600.0, 0.0, 0.0];
            let draws = 20_000;
            let mean: f64 = (0..draws)
                .map(|_| {
                    a.refresh_manoeuvre_rate(&p, &mut rng);
                    3600.0 / a.tau_s
                })
                .sum::<f64>()
                / draws as f64;
            // Independent midpoint quadrature in lambda (per hour) on [0.1, 10].
            let (mut z, mut m) = (0.0, 0.0);
            for k in 0..200_000 {
                let l = 0.1 + (k as f64 + 0.5) * (9.9 / 200_000.0);
                let d = l.powi(i32::from(events) - 1) * (-exposure_h * l).exp();
                z += d;
                m += d * l;
            }
            assert!((mean - m / z).abs() / (m / z) < 0.02, "{events}: {mean} vs {}", m / z);
        }
    }

    #[test]
    fn a_full_turn_returns_to_its_start() {
        // Limiting case: a 360-degree turn (two 180-degree turns) at 15 deg bank closes its circle.
        // Radius v^2 / (g tan 15deg) is ~7.5 km at 290 m/s; a first-order integrator misses by ~km.
        let p = Parameters { manoeuvre_step_s: 5.0, ..quiet() };
        let mut rng = ChaCha8Rng::seed_from_u64(5);
        let mut b = Aircraft::sample(&prior(), Mode::TrueTrack, &p, &CalmAir, &mut rng);
        b.turn_remaining = PI - 1e-9;
        let tas = b.air_speed_kt(CalmAir.weather(0.0, 0.0, 0.0, 0.0).speed_of_sound_kt()) * MPS_PER_KNOT;
        let period = std::f64::consts::TAU * tas / (9.806_65 * 15f64.to_radians().tan());
        b.propagate(period / 2.0, &p, &CalmAir, &mut rng);
        b.turn_remaining = PI - 1e-9;
        b.propagate(period, &p, &CalmAir, &mut rng);
        let miss_km = ((b.lat - 0.0).powi(2) + (b.lon - 90.0).powi(2)).sqrt() * 111.3;
        assert!(miss_km < 0.3, "circle misses its start by {miss_km} km");
    }

    const MEKAR: (f64, f64) = (6.503888888888889, 96.49111111111111);
    const NILAM: (f64, f64) = (6.756388888888889, 95.97638888888889);
    const IGOGU: (f64, f64) = (7.516944444444444, 94.41666666666667);

    /// Frequent random manoeuvres (tau ~ 0.1 h) and no cruise noise, to show guidance suppresses turns.
    fn busy() -> Parameters {
        Parameters { tau_range_h: (0.1, 0.1 + 1e-9), lnav_switch_mean_s: 1e12, ..quiet() }
    }

    fn start_on_n571() -> Prior {
        // 10 NM past MEKAR toward NILAM (flat-earth offset is ample over 10 NM).
        let (b, d) = bearing_and_distance(MEKAR, NILAM);
        let f = 10.0 / d;
        Prior {
            lat: MEKAR.0 + f * (NILAM.0 - MEKAR.0),
            lon: MEKAR.1 + f * (NILAM.1 - MEKAR.1),
            track_deg: b.to_degrees(),
            ..prior()
        }
    }

    #[test]
    fn a_route_is_flown_through_its_waypoints_then_held() {
        let p = busy();
        let mut rng = ChaCha8Rng::seed_from_u64(6);
        let mut a = Aircraft::sample(&start_on_n571(), Mode::MagneticHeading, &p, &CalmAir, &mut rng);
        let plan = Guidance { waypoints: vec![NILAM, IGOGU], after: AfterRoute::Hold { mode: Mode::TrueTrack, angle_deg: 180.0 } };
        a.set_guidance(plan, &CalmAir, &mut rng);
        let (mut near_nilam, mut near_igogu) = (f64::MAX, f64::MAX);
        for k in 1..=240 {
            a.propagate(k as f64 * 15.0, &p, &CalmAir, &mut rng);
            near_nilam = near_nilam.min(bearing_and_distance((a.lat, a.lon), NILAM).1);
            near_igogu = near_igogu.min(bearing_and_distance((a.lat, a.lon), IGOGU).1);
        }
        assert!(near_nilam < CAPTURE_NM + 0.5, "closest to NILAM {near_nilam} NM");
        assert!(near_igogu < CAPTURE_NM + 0.5, "closest to IGOGU {near_igogu} NM");
        let track = a.v_east_kt.atan2(a.v_north_kt).to_degrees().rem_euclid(360.0);
        assert!((track - 180.0).abs() < 0.5, "held track {track}");
        assert_eq!(a.turns, 0, "random turns must not start while a plan steers");
        assert!(a.accelerations > 0, "speed changes continue under guidance");
    }

    #[test]
    fn lateral_navigation_to_a_destination_closes_at_ground_speed() {
        let p = busy();
        let mut rng = ChaCha8Rng::seed_from_u64(7);
        let mut a = Aircraft::sample(&prior(), Mode::TrueTrack, &p, &CalmAir, &mut rng);
        let dest = (-45.0, 104.0);
        a.set_guidance(Guidance { waypoints: vec![], after: AfterRoute::Destination { lat: dest.0, lon: dest.1 } }, &CalmAir, &mut rng);
        let (_, d0) = bearing_and_distance((a.lat, a.lon), dest);
        let mut flown = 0.0;
        for k in 1..=120 {
            a.propagate(k as f64 * 60.0, &p, &CalmAir, &mut rng);
            flown += a.v_north_kt.hypot(a.v_east_kt) / 60.0;
        }
        let (bearing, d1) = bearing_and_distance((a.lat, a.lon), dest);
        // Two hours on the great circle: the distance falls by what was flown (1% for speed-change sampling).
        assert!(((d0 - d1) - flown).abs() / flown < 0.01, "closed {} NM of {flown} NM", d0 - d1);
        let track = a.v_east_kt.atan2(a.v_north_kt);
        assert!(wrap_pi(track - bearing).abs() < 1f64.to_radians());
        assert_eq!(a.turns, 0);
    }

    #[test]
    fn a_free_policy_hands_back_to_the_particles_own_mode_and_random_turns() {
        let p = busy();
        let mut rng = ChaCha8Rng::seed_from_u64(8);
        let mut a = Aircraft::sample(&start_on_n571(), Mode::MagneticTrack, &p, &CalmAir, &mut rng);
        a.set_guidance(Guidance { waypoints: vec![NILAM], after: AfterRoute::Free }, &CalmAir, &mut rng);
        a.propagate(3.0 * 3600.0, &p, &CalmAir, &mut rng);
        assert!(a.guidance.is_none());
        assert_eq!(a.mode, Mode::MagneticTrack);
        assert!(a.turns > 0, "random turns resume after the route");
    }

    #[test]
    fn air_data_and_wind_reproduce_the_ground_velocity() {
        // Still air, so the wind is the wind-error state alone: nonzero, and carried through.
        let p = Parameters::default();
        let mut rng = ChaCha8Rng::seed_from_u64(9);
        for mode in Mode::ALL {
            let mut a = Aircraft::sample(&prior(), mode, &p, &CalmAir, &mut rng);
            a.propagate(1800.0, &p, &CalmAir, &mut rng);
            let d = a.air_data();
            let (s, c) = d.heading_rad.sin_cos();
            assert!((d.true_air_speed_kt * c + d.wind_north_kt - a.v_north_kt).abs() < 1e-9, "{mode:?}");
            assert!((d.true_air_speed_kt * s + d.wind_east_kt - a.v_east_kt).abs() < 1e-9, "{mode:?}");
            assert!(d.wind_north_kt != 0.0 && d.wind_east_kt != 0.0);
        }
    }

    #[test]
    fn a_serialised_aircraft_continues_bit_identically() {
        // Written mid-flight and read back, the state must continue exactly as the original on
        // the same random stream. Three states: free and mid-manoeuvre (an infinite clock), and
        // guided (always an infinite turn clock) on its route and then to its destination.
        let p = busy();
        let mut rng = ChaCha8Rng::seed_from_u64(10);
        let mut free = Aircraft::sample(&prior(), Mode::MagneticTrack, &p, &CalmAir, &mut rng);
        let mut t = 0.0;
        while [free.next_turn, free.next_acceleration, free.next_climb].iter().all(|c| c.is_finite()) {
            t += 30.0;
            assert!(t < 7200.0, "no manoeuvre started in two hours");
            free.propagate(t, &p, &CalmAir, &mut rng);
        }
        let mut guided = Aircraft::sample(&start_on_n571(), Mode::TrueHeading, &p, &CalmAir, &mut rng);
        let after = AfterRoute::Destination { lat: -30.0, lon: 95.0 };
        guided.set_guidance(Guidance { waypoints: vec![NILAM, IGOGU], after }, &CalmAir, &mut rng);
        let mut on_route = guided.clone();
        on_route.propagate(300.0, &p, &CalmAir, &mut rng);
        guided.propagate(1500.0, &p, &CalmAir, &mut rng);
        assert!(matches!(on_route.guidance.as_ref().unwrap().phase, Phase::Route(_)));
        assert!(matches!(guided.guidance.as_ref().unwrap().phase, Phase::Destination(..)));
        for (mut a, stop) in [(free, t), (on_route, 300.0), (guided, 1500.0)] {
            let written = toml::to_string(&a).unwrap();
            assert!(written.contains("= inf"), "no infinite clock at {stop} s");
            let mut read: Aircraft = toml::from_str(&written).unwrap();
            assert_eq!(toml::to_string(&read).unwrap(), written);
            let (mut r1, mut r2) = (ChaCha8Rng::seed_from_u64(11), ChaCha8Rng::seed_from_u64(11));
            a.propagate(stop + 3600.0, &p, &CalmAir, &mut r1);
            read.propagate(stop + 3600.0, &p, &CalmAir, &mut r2);
            assert_eq!(toml::to_string(&read).unwrap(), toml::to_string(&a).unwrap(), "after {stop} s");
        }
    }

    #[test]
    fn ou_stationary_sd_matches_published_values() {
        let p = Parameters::default();
        assert!((Parameters::stationary_sd(p.mach_reversion_per_s, p.mach_noise_per_s) - 3.113e-3).abs() < 1e-5);
        assert!((Parameters::stationary_sd(p.angle_reversion_per_s, p.angle_noise_rad2_per_s).to_degrees() - 0.0826).abs() < 1e-3);
        assert!((Parameters::stationary_sd(p.wind_reversion_per_s, p.wind_noise_kt2_per_s) - 5.684).abs() < 1e-2);
    }
}
