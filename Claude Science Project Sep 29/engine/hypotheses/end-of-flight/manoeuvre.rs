//! Piloted manoeuvres after the onset (gap G-turn; Pete's rulings 12 Oct 2026: full turn model, no fixed cap on the number of
//! turns; Davey sampling until about 25 min before impact; sweep and circuit not exclusive; no sun term). Applies only to the
//! PILOTED laws (Track, BestGlide); free flight keeps its residual bank.
//!
//! Two regimes, switched online when the terminal window opens (time to go = height / descent rate at or below
//! `terminal_window_s`, or the ditching approach has begun):
//! 1. before the window: Davey et al. (2016, ch. 6-7) turns - a Poisson process with time constant tau (Jeffreys prior on
//!    0.1-10 h, the core's prior; interim until the core passes each particle's own tau, core request), turn angle uniform on
//!    the circle;
//! 2. inside the window, the terminal families, each optional and not exclusive:
//!    (a) random turns, uniform angle, at a rate drawn per descent (log-uniform hyper-prior);
//!    (b) a search sweep of 1-3 full orbits, starting inside the window;
//!    (c) a ditching circuit (ditching attempts only) when the approach begins: downwind past the site, base, final into the
//!        wind or along the swell (across the wind, a swell proxy: no swell data). A sweep still pending is flown first.
//! Latents carry every hyper-draw and what was begun, so the sweep and circuit probabilities and the circuit's final-heading
//! choice re-weight exactly (U[0, 1] hyper-priors, proposal 0.5 = the marginal).

/// How a manoeuvre steers.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Steer {
    /// Turn to an absolute heading of kind 0-3 (see module doc); `x` = side (+/-1) for kind 1, heading change (rad) for kind 3.
    Heading { kind: u8, x: f64 },
    /// Turn through a signed angle (rad): an orbit is +/-2 pi per circle.
    Delta(f64),
    /// Fly straight for this many seconds.
    Hold(f64),
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Manoeuvre {
    /// Seconds after the onset at which it may begin (the queue is sequential).
    pub start_s: f64,
    pub steer: Steer,
    pub bank_rad: f64,
    /// 0 terminal random turn, 1 sweep, 2 circuit leg, 3 Davey-regime turn.
    pub source: u8,
}

/// The ditching circuit drawn for a profile: leg durations, side of the base turn, bank.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Circuit {
    pub downwind_s: f64,
    pub base_s: f64,
    pub side: f64,
    pub bank_rad: f64,
    /// Final heading: 0 into the wind, 1 along the swell (across the wind, side `swell_side`).
    pub final_kind: u8,
    pub swell_side: f64,
}

/// The manoeuvres drawn for one descent.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct ManoeuvreDraw {
    /// Davey-regime turns, start times from the onset.
    pub queue: Vec<Manoeuvre>,
    /// Terminal-window manoeuvres (random turns and the sweep), start times from the window's opening.
    pub terminal: Vec<Manoeuvre>,
    pub circuit: Option<Circuit>,
    pub davey_tau_h: Option<f64>,
    pub ln_rate_per_min: Option<f64>,
    pub window_s: f64,
    pub sweep_eligible: bool,
    pub sweep_drawn: bool,
    pub circuit_eligible: bool,
}

/// Heading wrapped to (-pi, pi].
pub fn wrap_pi(a: f64) -> f64 {
    let t = std::f64::consts::TAU;
    let mut x = a % t;
    if x > std::f64::consts::PI {
        x -= t;
    } else if x <= -std::f64::consts::PI {
        x += t;
    }
    x
}

/// Runtime state of the manoeuvre queue for one descent.
#[derive(Debug, Clone, Default)]
pub struct Pilot {
    pub queue: Vec<Manoeuvre>,
    pub terminal: Vec<Manoeuvre>,
    pub circuit: Option<Circuit>,
    pub window_s: f64,
    /// Unix time at which the terminal window opened (NaN: never).
    pub window_opened_unix_s: f64,
    next: usize,
    /// (remaining signed turn, bank) of the active turn.
    active: Option<(f64, f64, u8)>,
    hold_until: Option<f64>,
    last_heading: Option<f64>,
    circuit_started: bool,
    /// Turns begun: Davey regime, terminal random turns; sweeps begun; circuit begun; total |heading change| flown.
    pub davey_begun: u32,
    pub terminal_begun: u32,
    pub sweeps_begun: u32,
    pub circuit_begun: bool,
    pub heading_change_rad: f64,
}

impl Pilot {
    pub fn new(d: &ManoeuvreDraw) -> Self {
        Pilot { queue: d.queue.clone(), terminal: d.terminal.clone(), circuit: d.circuit, window_s: d.window_s, window_opened_unix_s: f64::NAN, ..Default::default() }
    }

    pub fn is_empty(&self) -> bool {
        self.queue.is_empty() && self.terminal.is_empty() && self.circuit.is_none()
    }

    /// Bank (rad, positive right) for a piloted command at this step. `wind_*` is the wind the aircraft is in (towards which it
    /// blows, m/s); `in_approach` is true once the ditching approach phase has begun.
    #[allow(clippy::too_many_arguments)]
    pub fn bank(&mut self, heading_rad: f64, elapsed_s: f64, wind_east_mps: f64, wind_north_mps: f64, in_approach: bool, unix_s: f64, altitude_ft: f64, vertical_speed_mps: f64) -> f64 {
        // Terminal window: opens once, when the time to go at the present descent rate is within the window, or at the approach.
        if !self.window_opened_unix_s.is_finite() {
            let to_go = if vertical_speed_mps < -0.5 { altitude_ft.max(0.0) * 0.3048 / -vertical_speed_mps } else { f64::INFINITY };
            if to_go <= self.window_s || in_approach {
                self.window_opened_unix_s = unix_s;
                // Davey turns not yet begun are replaced by the terminal families (a turn in progress finishes).
                self.queue.truncate(self.next);
                let mut t: Vec<Manoeuvre> = self.terminal.iter().map(|m| Manoeuvre { start_s: elapsed_s + m.start_s, ..*m }).collect();
                t.sort_by(|a, b| a.start_s.total_cmp(&b.start_s));
                self.queue.extend(t);
            }
        }
        let turned = self.last_heading.map_or(0.0, |h| wrap_pi(heading_rad - h));
        self.last_heading = Some(heading_rad);
        self.heading_change_rad += turned.abs();
        if let Some((rem, bank, src)) = self.active {
            let rem = rem - turned;
            if rem.abs() > 0.01 {
                self.active = Some((rem, bank, src));
                // Full bank until the last 20 deg, then proportional (roll-out), never below a fifth.
                return rem.signum() * bank * (rem.abs() / 0.35).clamp(0.2, 1.0);
            }
            self.active = None;
        }
        if let Some(t) = self.hold_until {
            if elapsed_s < t {
                return 0.0;
            }
            self.hold_until = None;
        }
        if in_approach && !self.circuit_started {
            if let Some(c) = self.circuit {
                self.circuit_started = true;
                self.circuit_begun = true;
                let final_leg = if c.final_kind == 0 { Steer::Heading { kind: 0, x: 0.0 } } else { Steer::Heading { kind: 1, x: c.swell_side } };
                let legs = [
                    Manoeuvre { start_s: elapsed_s, steer: Steer::Heading { kind: 4, x: 0.0 }, bank_rad: c.bank_rad, source: 2 },
                    Manoeuvre { start_s: elapsed_s, steer: Steer::Hold(c.downwind_s), bank_rad: 0.0, source: 2 },
                    Manoeuvre { start_s: elapsed_s, steer: Steer::Delta(c.side * std::f64::consts::FRAC_PI_2), bank_rad: c.bank_rad, source: 2 },
                    Manoeuvre { start_s: elapsed_s, steer: Steer::Hold(c.base_s), bank_rad: 0.0, source: 2 },
                    Manoeuvre { start_s: elapsed_s, steer: final_leg, bank_rad: c.bank_rad, source: 2 },
                ];
                // The circuit follows a sweep still pending (flown first, at once); remaining random turns are dropped.
                let pending_sweeps: Vec<Manoeuvre> = self.queue[self.next..].iter().filter(|m| m.source == 1).map(|m| Manoeuvre { start_s: elapsed_s, ..*m }).collect();
                self.queue.truncate(self.next);
                self.queue.extend(pending_sweeps);
                self.queue.extend(legs);
            }
        }
        while self.next < self.queue.len() && elapsed_s >= self.queue[self.next].start_s {
            let m = self.queue[self.next];
            self.next += 1;
            let into_wind = if wind_east_mps.hypot(wind_north_mps) > 0.5 { (-wind_east_mps).atan2(-wind_north_mps) } else { heading_rad };
            let delta = match m.steer {
                Steer::Hold(s) => {
                    self.hold_until = Some(elapsed_s + s);
                    return 0.0;
                }
                Steer::Delta(d) => d,
                Steer::Heading { kind, x } => {
                    let target = match kind {
                        0 => into_wind,
                        1 => into_wind + x * std::f64::consts::FRAC_PI_2,
                        3 => heading_rad + x,
                        _ => into_wind + std::f64::consts::PI, // downwind leg of the circuit
                    };
                    wrap_pi(target - heading_rad)
                }
            };
            match m.source {
                0 => self.terminal_begun += 1,
                1 => self.sweeps_begun += 1,
                3 => self.davey_begun += 1,
                _ => {}
            }
            if delta.abs() > 0.01 {
                self.active = Some((delta, m.bank_rad, m.source));
                return delta.signum() * m.bank_rad;
            }
        }
        0.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The queue turns through the commanded angles: a 2-circle orbit adds 4 pi of heading change, an into-wind turn ends on
    /// the wind's reciprocal, and a hold flies straight. Heading integrated at a fixed turn rate per unit bank.
    #[test]
    fn the_manoeuvre_queue_turns_through_what_it_commands() {
        let q = vec![
            Manoeuvre { start_s: 10.0, steer: Steer::Delta(-2.0 * std::f64::consts::TAU), bank_rad: 0.4, source: 1 },
            Manoeuvre { start_s: 20.0, steer: Steer::Heading { kind: 0, x: 0.0 }, bank_rad: 0.4, source: 3 },
            Manoeuvre { start_s: 30.0, steer: Steer::Hold(50.0), bank_rad: 0.0, source: 3 },
        ];
        let mut p = Pilot::new(&ManoeuvreDraw { queue: q, window_s: 0.0, ..Default::default() });
        let (mut psi, dt) = (0.3_f64, 0.1);
        let (we, wn) = (10.0, 0.0); // wind blowing towards east: into wind = heading west (-90 deg)
        let mut t = 0.0;
        while t < 400.0 {
            let b = p.bank(psi, t, we, wn, false, 1_394_237_969.0, 35_000.0, 0.0);
            psi = wrap_pi(psi + 0.15 * b * dt);
            t += dt;
        }
        assert_eq!(p.sweeps_begun, 1);
        assert_eq!(p.davey_begun, 1); // the hold is not a turn
        assert!((wrap_pi(psi - (-std::f64::consts::FRAC_PI_2))).abs() < 0.02, "{}", psi);
        assert!(p.heading_change_rad > 2.0 * std::f64::consts::TAU - 0.05);
    }
}

#[cfg(test)]
mod window_tests {
    use super::*;

    /// The terminal window opens on time to go and swaps the Davey turns for the terminal families; a ditching circuit at the
    /// approach flies a pending sweep first and ends into the wind.
    #[test]
    fn the_terminal_window_and_the_circuit_follow_the_rules() {
        let d = ManoeuvreDraw {
            queue: vec![Manoeuvre { start_s: 5_000.0, steer: Steer::Heading { kind: 3, x: 1.0 }, bank_rad: 0.4, source: 3 }],
            terminal: vec![Manoeuvre { start_s: 4_000.0, steer: Steer::Delta(std::f64::consts::TAU), bank_rad: 0.4, source: 1 }],
            circuit: Some(Circuit { downwind_s: 30.0, base_s: 20.0, side: 1.0, bank_rad: 0.4, final_kind: 0, swell_side: 1.0 }),
            window_s: 1_500.0,
            ..Default::default()
        };
        let mut p = Pilot::new(&d);
        let (mut psi, dt, wn) = (0.0_f64, 0.1, -10.0); // wind blowing towards south: into wind = north (0)
        // Level flight: no window.
        assert_eq!(p.bank(psi, 0.0, 0.0, wn, false, 0.0, 30_000.0, 0.0), 0.0);
        assert!(!p.window_opened_unix_s.is_finite());
        // Descending 1,000 ft/min from 20,000 ft: 20 min to go, inside 25 min: the window opens; the Davey turn is dropped.
        let _ = p.bank(psi, 100.0, 0.0, wn, false, 100.0, 20_000.0, -5.08);
        assert!(p.window_opened_unix_s.is_finite());
        // Approach begins before the sweep's time: the sweep is flown first, then the circuit.
        let mut t = 200.0;
        while t < 900.0 {
            let b = p.bank(psi, t, 0.0, wn, true, t, 1_000.0, -1.5);
            psi = wrap_pi(psi + 0.15 * b * dt);
            t += dt;
        }
        assert_eq!((p.davey_begun, p.sweeps_begun, p.circuit_begun), (0, 1, true));
        assert!(wrap_pi(psi).abs() < 0.03, "{psi}");
    }
}
