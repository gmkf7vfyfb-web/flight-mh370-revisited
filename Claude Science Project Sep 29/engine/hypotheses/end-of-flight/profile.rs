//! The descent envelope: **sampled, never assumed**.
//!
//! A constant descent rate from onset to the sea is one member of the envelope, not the envelope.
//! What is sampled here, per the brief's §4:
//!
//! - **continuous** descents at a rate generated from the state and configuration;
//! - **emergency-descent-style upper segments** — idle thrust, speedbrakes out, airspeed towards
//!   MMO — *followed by a separate transition*, because a rapid descent to breathable altitude is
//!   not a complete sea-level approach;
//! - **level-offs and changes of descent rate**, with 10,000 ft and 4,000 ft always in the
//!   candidate set. 10,000 ft is the operationally meaningful emergency level-off. 4,000 ft is
//!   included **because it appears in the recovered simulator data** — cited here only as the
//!   reason for including the altitude, never as support for it having been flown: that data's
//!   provenance is contested and it is evidence about what was rehearsed, not what happened;
//! - **randomly sampled trigger points and profile shapes**, so the ensemble is not a handful of
//!   hand-chosen archetypes;
//! - **substantial lower-altitude flight**: level segments run to tens of minutes, so an hour
//!   between onset and impact need not mean an hour descending. The time actually spent
//!   descending is recorded as a latent rather than inferred from the elapsed time.
//!
//! The reference idle-thrust rates quoted in the brief for sanity-checking (about 2,200 ft/min
//! clean at 0.84M/310 kt below 20,000 ft and about 5,300 with speedbrakes, about 1,400/3,300 at
//! 250 kt, roughly 3 NM per 1,000 ft) come from manuals whose circulating copies are
//! unauthorised. They are used **only** as targets that the sampled rate ranges must bracket, as
//! a declared modelling choice, and are not cited; see the provenance table in `aero.rs`.
//!
//! ## Upset followed by recovery is demonstrated, not asserted
//!
//! [`super::taxonomy::Control::UpsetThenRecovery`] is the one control state that cannot be chosen:
//! it has to be earned. The profile runs the upset on free dynamics, and at the recovery trigger
//! [`Flying::recovery_is_feasible`] checks that the aircraft has the altitude, the Mach margin and
//! the usable lift to recover. Even then the recovery counts only if the integrated vertical speed
//! comes back above `-recovery_rate_fpm` before the aircraft is below `recovery_floor_ft`. A
//! descent that fails is **relabelled** `MaintainedThenLost` and records why, so failed recovery
//! attempts stay in the population instead of being discarded.

use serde::Deserialize;

use super::aero::{Aero, Configuration, Range};
use super::atmos;
use super::integrator::{Body, Command};
use super::taxonomy::{Control, Propulsion};

#[cfg(test)]
use super::aero::tests::reference;

/// The shape of a sampled descent.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Shape {
    /// One descending segment to the surface.
    Continuous,
    /// A high-rate upper segment, then a transition, then a separate approach.
    EmergencyThenTransition,
    /// Descending with one or two level-offs and a rate change at each.
    SteppedLevelOffs,
    /// The configuration's best lift-to-drag glide.
    BestGlide,
    /// Free dynamics at fixed trim and residual bank: phugoid or spiral.
    FreeTrim,
}

impl Shape {
    pub fn code(self) -> f64 {
        match self {
            Shape::Continuous => 0.0,
            Shape::EmergencyThenTransition => 1.0,
            Shape::SteppedLevelOffs => 2.0,
            Shape::BestGlide => 3.0,
            Shape::FreeTrim => 4.0,
        }
    }
}

/// One phase of a profile.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Phase {
    /// Descend at a target rate and Mach until a trigger altitude.
    Descend { rate_fpm: f64, mach: f64, until_altitude_ft: f64, speedbrake_eighths: u8 },
    /// Hold an altitude for a sampled time.
    Level { mach: f64, seconds: f64 },
    /// Best lift-to-drag glide to the surface.
    Glide,
    /// Free dynamics to the surface, or until a recovery trigger.
    Free { c_l: f64, bank_rad: f64, recover_at_altitude_ft: Option<f64> },
    /// A low-rate approach to water contact. The rate band is the ditching-guidance figure of
    /// 200-300 ft/min on final before the flare, used as a modelling parameter.
    Approach { rate_fpm: f64, mach: f64 },
}

/// Configuration of the envelope sampler.
#[derive(Deserialize, Debug, Clone, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct EnvelopeConfig {
    /// Descent rate band for a continuous or stepped descent, ft/min (positive down). The band
    /// brackets the clean idle reference rates.
    pub descent_rate_fpm: Range,
    /// Descent rate band for an emergency-style segment with speedbrakes, ft/min.
    pub emergency_rate_fpm: Range,
    /// Mach held in an emergency-style segment. MMO is 0.87; the band stops there.
    pub emergency_mach: Range,
    /// Mach held in an ordinary descent.
    pub descent_mach: Range,
    /// Altitude band in which an emergency segment transitions to the rest of the descent.
    pub transition_altitude_ft: Range,
    /// Extra level-off candidate altitudes are drawn from this band; 10,000 ft and 4,000 ft are
    /// always candidates as well.
    pub leveloff_altitude_ft: Range,
    /// How long a level-off lasts, s. The upper end is what allows substantial low-altitude
    /// flight without an hour of descending.
    pub leveloff_seconds: Range,
    /// Probability of a second level-off given a first.
    pub second_leveloff_probability: f64,
    /// Final-approach rate band for a ditching attempt, ft/min.
    pub approach_rate_fpm: Range,
    /// Altitude at which a ditching attempt begins its final approach, ft.
    pub approach_altitude_ft: Range,
    /// Residual bank angle under free dynamics, degrees. Outcomes depend mostly on this and on
    /// the trim, which is why both are explicit uncertain inputs.
    pub residual_bank_deg: Range,
    /// Trim offset in lift coefficient under free dynamics, added to the level trim.
    pub trim_cl_offset: Range,
    /// Seconds of maintained control before control is lost, for `MaintainedThenLost`.
    pub control_loss_after_s: Range,
    /// Altitude at which an upset recovery is attempted, ft.
    pub recovery_altitude_ft: Range,
    /// Altitude a recovery must be completed above to count, ft.
    pub recovery_floor_ft: f64,
    /// Vertical speed the aircraft must regain for the recovery to count, ft/min (positive down).
    pub recovery_rate_fpm: f64,
    /// Mach above which a recovery is not feasible: beyond the extrapolated part of the model
    /// there is nothing to claim a recovery from.
    pub recovery_mach_limit: f64,
    /// Prior probability that free dynamics (no intervention, and the uncontrolled phase of
    /// maintained-then-lost and upset-then-recovery) DIVERGE into a spiral dive, rather than hold the
    /// drawn residual bank. Pete's ruling, 9 Oct: 0.5, a stated indifference prior, with 0.25 and 0.75
    /// as sensitivities. The ten Boeing engineering-simulator runs split 5/10, but they are chosen
    /// scenarios, not frequencies (results/eof-boeing-calibration-oct09). 0 (the serde default) is the
    /// pre-calibration model, byte-identical, because no extra uniform is drawn.
    #[serde(default)]
    pub spiral_divergent_weight: f64,
    /// Bank doubling time of a divergent spiral, s. Calibrated: Boeing cases 3, 4, 6 and 10 grow bank
    /// by x2.56-2.75 between 60 and 180 s, a doubling time of 82-88 s; the band brackets it.
    #[serde(default = "default_spiral_doubling_s")]
    pub spiral_doubling_s: Range,
    /// Bank at which a divergent spiral stops growing, deg. Boeing's dives read 53-60 deg from the
    /// track, but this point mass reaches their descent rates only near 90 deg
    /// (results/eof-boeing-calibration-oct09, addendum 2), so the cap is a calibration knob, not a
    /// measured bank.
    #[serde(default = "default_spiral_bank_cap_deg")]
    pub spiral_bank_cap_deg: f64,
    /// Smallest bank a divergent spiral grows from, deg: a spiral mode starts from any disturbance,
    /// so a drawn residual bank of 0 does not freeze it.
    #[serde(default = "default_spiral_bank_floor_deg")]
    pub spiral_bank_floor_deg: f64,
}

fn default_spiral_doubling_s() -> Range {
    Range::Uniform([60.0, 120.0])
}
fn default_spiral_bank_cap_deg() -> f64 {
    60.0
}
fn default_spiral_bank_floor_deg() -> f64 {
    1.0
}

impl EnvelopeConfig {
    pub fn check(&self) -> Result<(), String> {
        for (name, r) in [
            ("descent_rate_fpm", self.descent_rate_fpm),
            ("emergency_rate_fpm", self.emergency_rate_fpm),
            ("emergency_mach", self.emergency_mach),
            ("descent_mach", self.descent_mach),
            ("transition_altitude_ft", self.transition_altitude_ft),
            ("leveloff_altitude_ft", self.leveloff_altitude_ft),
            ("leveloff_seconds", self.leveloff_seconds),
            ("approach_rate_fpm", self.approach_rate_fpm),
            ("approach_altitude_ft", self.approach_altitude_ft),
            ("residual_bank_deg", self.residual_bank_deg),
            ("trim_cl_offset", self.trim_cl_offset),
            ("control_loss_after_s", self.control_loss_after_s),
            ("recovery_altitude_ft", self.recovery_altitude_ft),
        ] {
            r.check(&format!("envelope.{name}"))?;
        }
        if !(0.0..=1.0).contains(&self.second_leveloff_probability) {
            return Err("envelope.second_leveloff_probability must be in [0, 1]".into());
        }
        if !(self.recovery_floor_ft.is_finite() && self.recovery_floor_ft > 0.0) {
            return Err("envelope.recovery_floor_ft must be a positive altitude".into());
        }
        if !(self.recovery_rate_fpm.is_finite() && self.recovery_rate_fpm > 0.0) {
            return Err("envelope.recovery_rate_fpm must be a positive rate".into());
        }
        if !(0.0..=1.0).contains(&self.spiral_divergent_weight) {
            return Err("envelope.spiral_divergent_weight must be in [0, 1]".into());
        }
        self.spiral_doubling_s.check("envelope.spiral_doubling_s")?;
        let lo = match self.spiral_doubling_s { Range::Fixed(v) => v, Range::Uniform([a, _]) => a };
        if !(lo > 0.0) {
            return Err("envelope.spiral_doubling_s must be positive".into());
        }
        // Up to 135 deg: an uncontrolled spiral dive can overbank past 90 deg (lift below the horizon).
        if !(self.spiral_bank_cap_deg > 0.0 && self.spiral_bank_cap_deg <= 135.0) {
            return Err("envelope.spiral_bank_cap_deg must be in (0, 135]".into());
        }
        if !(self.spiral_bank_floor_deg >= 0.0 && self.spiral_bank_floor_deg < self.spiral_bank_cap_deg) {
            return Err("envelope.spiral_bank_floor_deg must be in [0, cap)".into());
        }
        Ok(())
    }

    /// The level-off candidate set: 10,000 ft and 4,000 ft always, plus one sampled altitude.
    pub fn leveloff_candidates(&self, uniform: &mut dyn FnMut() -> f64) -> [f64; 3] {
        [10_000.0, 4_000.0, self.leveloff_altitude_ft.draw(uniform)]
    }

    /// Sample a profile for one descent.
    pub fn sample(
        &self,
        start: &Body,
        propulsion: Propulsion,
        control: Control,
        aero: &Aero,
        uniform: &mut dyn FnMut() -> f64,
    ) -> Profile {
        let shape = self.sample_shape(propulsion, control, uniform);
        let mut phases: Vec<Phase> = Vec::new();
        let level_c_l = {
            let t = atmos::isa_temperature_k(start.pressure_altitude_ft);
            let q = atmos::dynamic_pressure_pa(geo::isa_pressure_pa(start.pressure_altitude_ft), start.tas_mps / atmos::sound_speed_mps(t));
            start.mass_kg * atmos::G0 / (q * aero.wing_area_m2)
        };
        match shape {
            Shape::BestGlide => phases.push(Phase::Glide),
            Shape::FreeTrim => phases.push(Phase::Free {
                c_l: level_c_l + self.trim_cl_offset.draw(uniform),
                bank_rad: self.residual_bank_deg.draw(uniform).to_radians(),
                recover_at_altitude_ft: None,
            }),
            Shape::Continuous => {
                phases.push(Phase::Descend {
                    rate_fpm: self.descent_rate_fpm.draw(uniform),
                    mach: self.descent_mach.draw(uniform),
                    until_altitude_ft: 0.0,
                    speedbrake_eighths: 0,
                });
            }
            Shape::EmergencyThenTransition => {
                let transition = self.transition_altitude_ft.draw(uniform).min(start.pressure_altitude_ft - 1_000.0);
                phases.push(Phase::Descend {
                    rate_fpm: self.emergency_rate_fpm.draw(uniform),
                    mach: self.emergency_mach.draw(uniform).min(aero.mach_crest),
                    until_altitude_ft: transition.max(1_000.0),
                    speedbrake_eighths: 8,
                });
                // The transition is a separate phase: a level-off at the transition altitude,
                // then a new descent at an independently sampled rate.
                phases.push(Phase::Level { mach: self.descent_mach.draw(uniform), seconds: self.leveloff_seconds.draw(uniform) });
                phases.push(Phase::Descend {
                    rate_fpm: self.descent_rate_fpm.draw(uniform),
                    mach: self.descent_mach.draw(uniform),
                    until_altitude_ft: 0.0,
                    speedbrake_eighths: 0,
                });
            }
            Shape::SteppedLevelOffs => {
                let candidates = self.leveloff_candidates(uniform);
                let first = candidates[(uniform() * 3.0) as usize % 3];
                let mut stops = vec![first];
                if uniform() < self.second_leveloff_probability {
                    let second = candidates[(uniform() * 3.0) as usize % 3];
                    if second < first {
                        stops.push(second);
                    }
                }
                let mut previous = start.pressure_altitude_ft;
                for stop in stops {
                    if stop >= previous - 500.0 {
                        continue;
                    }
                    phases.push(Phase::Descend {
                        rate_fpm: self.descent_rate_fpm.draw(uniform),
                        mach: self.descent_mach.draw(uniform),
                        until_altitude_ft: stop,
                        speedbrake_eighths: if uniform() < 0.3 { 8 } else { 0 },
                    });
                    phases.push(Phase::Level { mach: self.descent_mach.draw(uniform), seconds: self.leveloff_seconds.draw(uniform) });
                    previous = stop;
                }
                phases.push(Phase::Descend {
                    rate_fpm: self.descent_rate_fpm.draw(uniform),
                    mach: self.descent_mach.draw(uniform),
                    until_altitude_ft: 0.0,
                    speedbrake_eighths: 0,
                });
            }
        }

        // The control axis then modifies the tail of the profile.
        match control {
            Control::DitchingAttempt => {
                let at = self.approach_altitude_ft.draw(uniform);
                truncate_at(&mut phases, at);
                phases.push(Phase::Approach { rate_fpm: self.approach_rate_fpm.draw(uniform), mach: self.descent_mach.draw(uniform) });
            }
            Control::MaintainedThenLost => {
                let after = self.control_loss_after_s.draw(uniform);
                phases.push(Phase::Free {
                    c_l: level_c_l + self.trim_cl_offset.draw(uniform),
                    bank_rad: self.residual_bank_deg.draw(uniform).to_radians(),
                    recover_at_altitude_ft: None,
                });
                return Profile { shape, phases, control, loss_of_control_after_s: Some(after), recovery_attempt_altitude_ft: None };
            }
            Control::UpsetThenRecovery => {
                let recover_at = self.recovery_altitude_ft.draw(uniform);
                let upset = Phase::Free {
                    c_l: level_c_l + self.trim_cl_offset.draw(uniform),
                    bank_rad: self.residual_bank_deg.draw(uniform).to_radians(),
                    recover_at_altitude_ft: Some(recover_at),
                };
                let tail = Phase::Descend {
                    rate_fpm: self.descent_rate_fpm.draw(uniform),
                    mach: self.descent_mach.draw(uniform),
                    until_altitude_ft: 0.0,
                    speedbrake_eighths: 0,
                };
                return Profile {
                    shape,
                    phases: vec![upset, tail],
                    control,
                    loss_of_control_after_s: None,
                    recovery_attempt_altitude_ft: Some(recover_at),
                };
            }
            Control::NoIntervention => {}
        }
        Profile { shape, phases, control, loss_of_control_after_s: None, recovery_attempt_altitude_ft: None }
    }

    fn sample_shape(&self, propulsion: Propulsion, control: Control, uniform: &mut dyn FnMut() -> f64) -> Shape {
        if control == Control::NoIntervention || control == Control::UpsetThenRecovery {
            return Shape::FreeTrim;
        }
        if propulsion == Propulsion::NeitherThrusting {
            // Unpowered but controlled: a glide, or a glide flown at a chosen rate.
            return if uniform() < 0.5 { Shape::BestGlide } else { Shape::Continuous };
        }
        match uniform() {
            u if u < 0.40 => Shape::Continuous,
            u if u < 0.70 => Shape::SteppedLevelOffs,
            _ => Shape::EmergencyThenTransition,
        }
    }
}

/// Drop phases below `altitude_ft` and make the last remaining descent end there.
fn truncate_at(phases: &mut Vec<Phase>, altitude_ft: f64) {
    phases.retain(|p| !matches!(p, Phase::Descend { until_altitude_ft, .. } if *until_altitude_ft < altitude_ft && *until_altitude_ft == 0.0));
    if let Some(Phase::Descend { until_altitude_ft, .. }) = phases.last_mut() {
        if *until_altitude_ft < altitude_ft {
            *until_altitude_ft = altitude_ft;
        }
    } else {
        phases.push(Phase::Descend { rate_fpm: 1_500.0, mach: 0.60, until_altitude_ft: altitude_ft, speedbrake_eighths: 0 });
    }
}

/// One sampled profile.
#[derive(Debug, Clone, PartialEq)]
pub struct Profile {
    pub shape: Shape,
    pub phases: Vec<Phase>,
    pub control: Control,
    /// For `MaintainedThenLost`: seconds after onset at which control is lost.
    pub loss_of_control_after_s: Option<f64>,
    /// For `UpsetThenRecovery`: the altitude at which recovery is attempted.
    pub recovery_attempt_altitude_ft: Option<f64>,
}

/// The state machine that turns a profile into the integrator's per-step command. Mutable,
/// because which phase is current depends on the trajectory, not on the clock alone.
#[derive(Debug, Clone)]
pub struct Flying {
    pub profile: Profile,
    pub aero: Aero,
    pub recovery_floor_ft: f64,
    pub recovery_rate_fpm: f64,
    pub recovery_mach_limit: f64,
    index: usize,
    phase_started_s: f64,
    /// Set when a recovery was attempted at all.
    pub recovery_attempted: bool,
    /// Set when the attempt met the feasibility conditions.
    pub recovery_feasible: bool,
    /// Set when the aircraft actually regained the required vertical speed above the floor.
    pub recovery_demonstrated: bool,
    /// Why a recovery failed, if it did.
    pub recovery_failure: Option<&'static str>,
    pub engines_thrusting: u8,
    /// Bank doubling time if this descent's free dynamics diverge (a spiral dive); None holds the
    /// drawn residual bank. Set by the module after `new`, from `EnvelopeConfig::spiral_*`.
    pub spiral_doubling_s: Option<f64>,
    pub spiral_bank_cap_rad: f64,
    pub spiral_bank_floor_rad: f64,
    /// Seconds after onset at which free dynamics began, if they did.
    pub free_since_s: Option<f64>,
}

impl Flying {
    /// The bank of free dynamics at `elapsed_s`: the drawn residual bank, or, for a divergent spiral,
    /// that bank (at least the floor) doubling every `spiral_doubling_s` from the start of free
    /// flight, capped. The sign of the drawn bank sets the direction; a drawn 0 diverges to the right.
    fn free_bank(&mut self, bank0_rad: f64, elapsed_s: f64) -> f64 {
        let since = *self.free_since_s.get_or_insert(elapsed_s);
        match self.spiral_doubling_s {
            None => bank0_rad,
            Some(t2) => {
                let sign = if bank0_rad < 0.0 { -1.0 } else { 1.0 };
                let grown = bank0_rad.abs().max(self.spiral_bank_floor_rad) * 2f64.powf((elapsed_s - since).max(0.0) / t2);
                sign * grown.min(self.spiral_bank_cap_rad)
            }
        }
    }

    pub fn new(profile: Profile, aero: Aero, propulsion: Propulsion, cfg: &EnvelopeConfig) -> Self {
        Flying {
            profile,
            aero,
            recovery_floor_ft: cfg.recovery_floor_ft,
            recovery_rate_fpm: cfg.recovery_rate_fpm,
            recovery_mach_limit: cfg.recovery_mach_limit,
            index: 0,
            phase_started_s: 0.0,
            recovery_attempted: false,
            recovery_feasible: false,
            recovery_demonstrated: false,
            recovery_failure: None,
            engines_thrusting: propulsion.engines_thrusting(),
            spiral_doubling_s: None,
            spiral_bank_cap_rad: cfg.spiral_bank_cap_deg.to_radians(),
            spiral_bank_floor_rad: cfg.spiral_bank_floor_deg.to_radians(),
            free_since_s: None,
        }
    }

    /// Whether a recovery from the current state is feasible: altitude above the floor with
    /// margin, Mach inside the limit, and the usable lift enough for a 1.5 g pull.
    pub fn recovery_is_feasible(&self, body: &Body, mach: f64, q_pa: f64) -> Result<(), &'static str> {
        if body.pressure_altitude_ft <= self.recovery_floor_ft {
            return Err("below the recovery floor at the attempt");
        }
        if mach > self.recovery_mach_limit {
            return Err("Mach beyond the recovery limit");
        }
        let needed_c_l = 1.5 * body.mass_kg * atmos::G0 / (q_pa * self.aero.wing_area_m2);
        if needed_c_l > self.aero.c_l_max_clean {
            return Err("not enough usable lift for a 1.5 g recovery");
        }
        Ok(())
    }

    /// The command for the current step. `elapsed_s` is measured from onset.
    pub fn command(&mut self, body: &Body, elapsed_s: f64) -> (Command, Configuration, f64) {
        // Loss of control overrides the profile when its time arrives.
        if let Some(after) = self.profile.loss_of_control_after_s {
            if elapsed_s >= after {
                if let Some(Phase::Free { c_l, bank_rad, .. }) = self.profile.phases.last().copied() {
                    let bank_rad = self.free_bank(bank_rad, elapsed_s);
                    return (Command::FixedTrim { c_l, bank_rad }, self.configuration(0), 0.0);
                }
            }
        }
        let temperature = atmos::isa_temperature_k(body.pressure_altitude_ft);
        let mach = body.tas_mps / atmos::sound_speed_mps(temperature);
        let q = atmos::dynamic_pressure_pa(geo::isa_pressure_pa(body.pressure_altitude_ft), mach);

        loop {
            let phase = match self.profile.phases.get(self.index).copied() {
                Some(p) => p,
                None => {
                    // Past the end of the profile: hold the last command by gliding.
                    return (Command::BestGlide { bank_rad: 0.0 }, self.configuration(0), 0.0);
                }
            };
            match phase {
                Phase::Descend { rate_fpm, mach: target, until_altitude_ft, speedbrake_eighths } => {
                    if body.pressure_altitude_ft <= until_altitude_ft && self.index + 1 < self.profile.phases.len() {
                        self.advance(elapsed_s);
                        continue;
                    }
                    let rate = -rate_fpm / atmos::FPM_PER_MPS;
                    return (
                        Command::Track { vertical_speed_mps: rate, target_mach: target, bank_rad: 0.0 },
                        self.configuration(speedbrake_eighths),
                        1.0,
                    );
                }
                Phase::Level { mach: target, seconds } => {
                    if elapsed_s - self.phase_started_s >= seconds {
                        self.advance(elapsed_s);
                        continue;
                    }
                    return (Command::Track { vertical_speed_mps: 0.0, target_mach: target, bank_rad: 0.0 }, self.configuration(0), 1.0);
                }
                Phase::Glide => return (Command::BestGlide { bank_rad: 0.0 }, self.configuration(0), 0.0),
                Phase::Approach { rate_fpm, mach: target } => {
                    let rate = -rate_fpm / atmos::FPM_PER_MPS;
                    let mut cfg = self.configuration(0);
                    if cfg.can_reach_landing_configuration() {
                        cfg.landing_configuration = true;
                    }
                    return (Command::Track { vertical_speed_mps: rate, target_mach: target, bank_rad: 0.0 }, cfg, 1.0);
                }
                Phase::Free { c_l, bank_rad, recover_at_altitude_ft } => {
                    if let Some(at) = recover_at_altitude_ft {
                        if body.pressure_altitude_ft <= at && !self.recovery_attempted {
                            self.recovery_attempted = true;
                            match self.recovery_is_feasible(body, mach, q) {
                                Ok(()) => {
                                    self.recovery_feasible = true;
                                    self.advance(elapsed_s);
                                    continue;
                                }
                                Err(why) => {
                                    self.recovery_failure = Some(why);
                                }
                            }
                        }
                    }
                    let bank_rad = self.free_bank(bank_rad, elapsed_s);
                    return (Command::FixedTrim { c_l, bank_rad }, self.configuration(0), 0.0);
                }
            }
        }
    }

    /// Call after each step with the realised vertical speed, so a recovery is judged on what the
    /// aircraft did rather than on what was commanded.
    pub fn observe(&mut self, body: &Body, vertical_speed_mps: f64) {
        if self.recovery_feasible && !self.recovery_demonstrated {
            let descent_fpm = -vertical_speed_mps * atmos::FPM_PER_MPS;
            if body.pressure_altitude_ft > self.recovery_floor_ft && descent_fpm < self.recovery_rate_fpm {
                self.recovery_demonstrated = true;
            } else if body.pressure_altitude_ft <= self.recovery_floor_ft {
                self.recovery_failure = Some("did not regain the rate above the floor");
            }
        }
    }

    /// The control state this descent should be reported as, after the dynamics have had their
    /// say. An undemonstrated recovery is reported as `MaintainedThenLost`, not discarded.
    pub fn realised_control(&self) -> Control {
        match self.profile.control {
            Control::UpsetThenRecovery if !self.recovery_demonstrated => Control::MaintainedThenLost,
            other => other,
        }
    }

    fn advance(&mut self, elapsed_s: f64) {
        self.index += 1;
        self.phase_started_s = elapsed_s;
    }

    fn configuration(&self, speedbrake_eighths: u8) -> Configuration {
        let thrusting = self.engines_thrusting;
        Configuration {
            engines_thrusting: thrusting,
            engines_windmilling: 2 - thrusting,
            rat_deployed: thrusting == 0,
            speedbrake_eighths,
            landing_configuration: false,
        }
    }

    /// Move the propulsion state as fuel is exhausted: an engine failing mid-descent is a changed
    /// configuration, not a new family.
    pub fn set_engines_thrusting(&mut self, n: u8) {
        self.engines_thrusting = n.min(2);
    }
}

#[cfg(test)]
pub(super) mod tests {
    use super::*;

    pub fn envelope() -> EnvelopeConfig {
        EnvelopeConfig {
            descent_rate_fpm: Range::Uniform([800.0, 3_500.0]),
            emergency_rate_fpm: Range::Uniform([3_000.0, 6_500.0]),
            emergency_mach: Range::Uniform([0.80, 0.87]),
            descent_mach: Range::Uniform([0.50, 0.78]),
            transition_altitude_ft: Range::Uniform([8_000.0, 15_000.0]),
            leveloff_altitude_ft: Range::Uniform([1_500.0, 30_000.0]),
            leveloff_seconds: Range::Uniform([60.0, 2_400.0]),
            second_leveloff_probability: 0.4,
            approach_rate_fpm: Range::Uniform([200.0, 300.0]),
            approach_altitude_ft: Range::Uniform([500.0, 2_000.0]),
            residual_bank_deg: Range::Uniform([0.0, 35.0]),
            trim_cl_offset: Range::Uniform([-0.08, 0.08]),
            control_loss_after_s: Range::Uniform([30.0, 1_800.0]),
            recovery_altitude_ft: Range::Uniform([8_000.0, 25_000.0]),
            recovery_floor_ft: 3_000.0,
            recovery_rate_fpm: 4_000.0,
            recovery_mach_limit: 0.92,
            spiral_divergent_weight: 0.0,
            spiral_doubling_s: Range::Uniform([60.0, 120.0]),
            spiral_bank_cap_deg: 60.0,
            spiral_bank_floor_deg: 1.0,
        }
    }

    /// A divergent spiral doubles its bank every doubling time from the start of free flight, grows from
    /// the floor when the drawn bank is 0, keeps the drawn direction, and stops at the cap; a neutral
    /// one holds the drawn bank.
    #[test]
    fn a_divergent_spiral_doubles_its_bank_and_stops_at_the_cap() {
        let e = envelope();
        let p = e.sample(&body(35_000.0), Propulsion::NeitherThrusting, Control::NoIntervention, &reference(), &mut || 0.5);
        let mut f = Flying::new(p, reference(), Propulsion::NeitherThrusting, &e);
        assert_eq!(f.free_bank(-0.1, 10.0), -0.1, "neutral holds the drawn bank");
        let mut f2 = f.clone();
        f2.spiral_doubling_s = Some(80.0);
        f2.free_since_s = None;
        let b0 = f2.free_bank(-10f64.to_radians(), 100.0);
        assert!((b0 + 10f64.to_radians()).abs() < 1e-12, "starts from the drawn bank: {b0}");
        let b1 = f2.free_bank(-10f64.to_radians(), 180.0);
        assert!((b1 + 20f64.to_radians()).abs() < 1e-9, "one doubling after 80 s: {}", b1.to_degrees());
        let capped = f2.free_bank(-10f64.to_radians(), 100.0 + 80.0 * 5.0);
        assert!((capped + 60f64.to_radians()).abs() < 1e-12, "capped at 60 deg: {}", capped.to_degrees());
        let mut f3 = f.clone();
        f3.spiral_doubling_s = Some(80.0);
        f3.free_since_s = None;
        let _ = f3.free_bank(0.0, 0.0);
        assert!((f3.free_bank(0.0, 80.0) - 2f64.to_radians()).abs() < 1e-12, "a drawn 0 grows from the 1 deg floor");
        f.free_since_s = None;
    }

    fn body(altitude_ft: f64) -> Body {
        Body {
            unix_s: 1_394_237_000.0,
            latitude_deg: -35.0,
            longitude_deg: 93.0,
            pressure_altitude_ft: altitude_ft,
            tas_mps: 235.0,
            gamma_rad: 0.0,
            heading_rad: std::f64::consts::PI,
            mass_kg: 174_000.0,
            fuel_kg: 500.0,
        }
    }

    /// A deterministic sweep of the uniform stream, so the ensemble can be characterised without
    /// a random number generator.
    fn sweep(n: usize) -> impl FnMut() -> f64 {
        let mut i = 0usize;
        move || {
            // A low-discrepancy sequence (golden-ratio additive recurrence) over (0, 1).
            i += 1;
            let x = (i as f64 * 0.618_033_988_749_895 + 0.5 / n as f64) % 1.0;
            if x <= 0.0 {
                1e-9
            } else {
                x
            }
        }
    }

    /// 10,000 ft and 4,000 ft are always in the candidate set, with one sampled altitude beside
    /// them. 4,000 ft is there because it appears in the recovered simulator data; that is the
    /// reason for including the altitude, not evidence it was flown.
    #[test]
    fn the_level_off_candidates_always_include_ten_and_four_thousand_feet() {
        let e = envelope();
        let mut u = sweep(16);
        for _ in 0..16 {
            let c = e.leveloff_candidates(&mut u);
            assert!(c.contains(&10_000.0) && c.contains(&4_000.0), "{c:?}");
            assert!(c[2] >= 1_500.0 && c[2] <= 30_000.0, "{c:?}");
        }
    }

    /// The envelope is an envelope: over a sweep of the stream a powered, controlled descent
    /// produces every shape, not one archetype, and the emergency shape always has a *separate*
    /// transition phase after its high-rate segment.
    #[test]
    fn the_sampled_ensemble_spans_the_shapes_and_the_emergency_shape_has_a_transition() {
        let e = envelope();
        let aero = reference();
        let mut u = sweep(400);
        let mut shapes = std::collections::BTreeSet::new();
        let mut emergency_checked = 0;
        for _ in 0..400 {
            let p = e.sample(&body(35_000.0), Propulsion::TwoThrusting, Control::MaintainedThenLost, &aero, &mut u);
            shapes.insert(p.shape.code() as i64);
            if p.shape == Shape::EmergencyThenTransition {
                emergency_checked += 1;
                // High-rate segment with speedbrakes, then a level transition, then a new descent
                // at an independently sampled rate: a rapid descent is not a sea-level approach.
                assert!(matches!(p.phases[0], Phase::Descend { speedbrake_eighths: 8, .. }), "{:?}", p.phases[0]);
                assert!(matches!(p.phases[1], Phase::Level { .. }), "{:?}", p.phases[1]);
                assert!(matches!(p.phases[2], Phase::Descend { speedbrake_eighths: 0, .. }), "{:?}", p.phases[2]);
            }
        }
        assert_eq!(shapes, [0, 1, 2].into_iter().collect::<std::collections::BTreeSet<_>>(), "shapes seen: {shapes:?}");
        assert!(emergency_checked > 20, "only {emergency_checked} emergency profiles in 400 draws");
    }

    /// An hour between onset and impact need not be an hour descending: the level-off band runs
    /// to 2,400 s, so profiles exist whose level time exceeds half an hour.
    #[test]
    fn level_segments_allow_substantial_low_altitude_flight() {
        let e = envelope();
        let aero = reference();
        let mut u = sweep(600);
        let mut best = 0.0f64;
        for _ in 0..600 {
            let p = e.sample(&body(35_000.0), Propulsion::TwoThrusting, Control::DitchingAttempt, &aero, &mut u);
            let level: f64 = p.phases.iter().filter_map(|x| if let Phase::Level { seconds, .. } = x { Some(*seconds) } else { None }).sum();
            best = best.max(level);
        }
        assert!(best > 1_800.0, "longest level time only {best} s");
    }

    /// A ditching attempt always ends with a low-rate approach phase, and the rate is the
    /// 200-300 ft/min band used as a modelling parameter.
    #[test]
    fn a_ditching_attempt_ends_with_a_low_rate_approach() {
        let e = envelope();
        let aero = reference();
        let mut u = sweep(100);
        for _ in 0..100 {
            let p = e.sample(&body(35_000.0), Propulsion::NeitherThrusting, Control::DitchingAttempt, &aero, &mut u);
            match p.phases.last() {
                Some(Phase::Approach { rate_fpm, .. }) => assert!(*rate_fpm >= 200.0 && *rate_fpm <= 300.0, "{rate_fpm}"),
                other => panic!("ditching attempt did not end on an approach: {other:?}"),
            }
        }
    }

    /// No intervention is free dynamics, whatever the propulsion state, and the residual bank and
    /// trim offset are the explicit uncertain inputs the outcome depends on.
    #[test]
    fn no_intervention_is_free_dynamics_with_sampled_bank_and_trim() {
        let e = envelope();
        let aero = reference();
        let mut u = sweep(50);
        let mut banks = Vec::new();
        for _ in 0..50 {
            let p = e.sample(&body(35_000.0), Propulsion::NeitherThrusting, Control::NoIntervention, &aero, &mut u);
            assert_eq!(p.shape, Shape::FreeTrim);
            match p.phases.as_slice() {
                [Phase::Free { bank_rad, recover_at_altitude_ft: None, .. }] => banks.push(bank_rad.to_degrees()),
                other => panic!("{other:?}"),
            }
        }
        let spread = banks.iter().cloned().fold(f64::MIN, f64::max) - banks.iter().cloned().fold(f64::MAX, f64::min);
        assert!(spread > 20.0, "residual bank barely varied: {spread} deg");
    }

    /// A recovery is refused when the altitude, the Mach or the usable lift will not support it,
    /// and an undemonstrated recovery is relabelled rather than discarded.
    #[test]
    fn an_upset_recovery_must_be_demonstrated() {
        let e = envelope();
        let aero = reference();
        let mut u = sweep(8);
        let p = e.sample(&body(35_000.0), Propulsion::NeitherThrusting, Control::UpsetThenRecovery, &aero, &mut u);
        assert_eq!(p.control, Control::UpsetThenRecovery);
        assert!(p.recovery_attempt_altitude_ft.is_some());
        let mut flying = Flying::new(p, aero, Propulsion::NeitherThrusting, &e);
        // Below the floor: refused.
        let q = atmos::dynamic_pressure_pa(geo::isa_pressure_pa(2_000.0), 0.50);
        assert!(flying.recovery_is_feasible(&body(2_000.0), 0.50, q).is_err());
        // Beyond the Mach limit: refused.
        let q = atmos::dynamic_pressure_pa(geo::isa_pressure_pa(20_000.0), 0.95);
        assert_eq!(flying.recovery_is_feasible(&body(20_000.0), 0.95, q).err(), Some("Mach beyond the recovery limit"));
        // Too little dynamic pressure for 1.5 g: refused.
        let q = 1_500.0;
        assert_eq!(flying.recovery_is_feasible(&body(20_000.0), 0.50, q).err(), Some("not enough usable lift for a 1.5 g recovery"));
        // Feasible, but never demonstrated: relabelled, with a reason.
        let q = atmos::dynamic_pressure_pa(geo::isa_pressure_pa(20_000.0), 0.60);
        assert!(flying.recovery_is_feasible(&body(20_000.0), 0.60, q).is_ok());
        assert_eq!(flying.realised_control(), Control::MaintainedThenLost);
        flying.recovery_feasible = true;
        flying.observe(&body(2_000.0), -100.0);
        assert!(!flying.recovery_demonstrated);
        assert_eq!(flying.recovery_failure, Some("did not regain the rate above the floor"));
        // Demonstrated: kept.
        flying.recovery_failure = None;
        flying.observe(&body(10_000.0), -5.0);
        assert!(flying.recovery_demonstrated);
        assert_eq!(flying.realised_control(), Control::UpsetThenRecovery);
    }

    /// Propulsion is an evolving state: the configuration follows the engine count, and the RAT
    /// comes out only when nothing is thrusting.
    #[test]
    fn the_configuration_follows_the_evolving_engine_count() {
        let e = envelope();
        let aero = reference();
        let mut u = sweep(4);
        let p = e.sample(&body(35_000.0), Propulsion::TwoThrusting, Control::MaintainedThenLost, &aero, &mut u);
        let mut flying = Flying::new(p, aero, Propulsion::TwoThrusting, &e);
        let (_, cfg, _) = flying.command(&body(30_000.0), 1.0);
        assert_eq!((cfg.engines_thrusting, cfg.engines_windmilling, cfg.rat_deployed), (2, 0, false));
        flying.set_engines_thrusting(1);
        let (_, cfg, _) = flying.command(&body(29_000.0), 2.0);
        assert_eq!((cfg.engines_thrusting, cfg.engines_windmilling, cfg.rat_deployed), (1, 1, false));
        flying.set_engines_thrusting(0);
        let (_, cfg, _) = flying.command(&body(28_000.0), 3.0);
        assert_eq!((cfg.engines_thrusting, cfg.engines_windmilling, cfg.rat_deployed), (0, 2, true));
    }

    #[test]
    fn the_envelope_configuration_is_validated() {
        assert!(envelope().check().is_ok());
        assert!(EnvelopeConfig { second_leveloff_probability: 2.0, ..envelope() }.check().is_err());
        assert!(EnvelopeConfig { recovery_floor_ft: 0.0, ..envelope() }.check().is_err());
        assert!(EnvelopeConfig { descent_rate_fpm: Range::Uniform([5.0, 1.0]), ..envelope() }.check().is_err());
    }
}
