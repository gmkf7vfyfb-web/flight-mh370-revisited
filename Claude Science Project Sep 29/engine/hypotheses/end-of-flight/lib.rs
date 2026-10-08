//! End of flight: the descent from the last reliable cruise state to the sea, as a sampled
//! ensemble rather than an assumed profile.
//!
//! This is the **first code increment** of the end-of-flight model. It supplies the descent
//! taxonomy, the point-mass integrator, the sampled descent envelope, the descent-onset latent
//! and a `Terminal` implementation. It does **not** yet supply the fuel coupling against the
//! core's calibrated tables, the per-engine flame-out, the 00:19 log-on lag likelihood, or the
//! calibration against the ten Boeing engineering-simulator runs; those need core changes or
//! data not in this tree, and each is listed in `hypothesis.toml`.
//!
//! # The assumption this module states
//!
//! That the end of flight is **not** a single assumed behaviour. Neither piloted nor unpiloted is
//! a default here: descent initiation, propulsion state and subsequent control are three
//! independent sampled axes (see `taxonomy.rs`), the descent profile is sampled from an envelope
//! rather than fixed (see `profile.rs`), and the onset is triggered on **predicted** remaining
//! endurance under continued cruise, never on the realised flame-out (see `onset.rs`). Family
//! priors are explicit, reported per family, and recorded as the `family_prior` latent, so that
//! the Monte Carlo allocation across families is never mistaken for a statement of equal prior
//! probability.
//!
//! # How it enters the estimate
//!
//! Through `Terminal` only. The runner flies the core dynamics to `takeover_time` — which is the
//! sampled **descent onset**, not necessarily a flame-out — then this module integrates to the
//! sea surface and returns the impact, the state at each burst after the takeover, and its
//! latents. The runner scores the 00:19 observations with the core measurement model; **no
//! measurement model is reimplemented here**, as the contract requires. No likelihood is returned
//! by this module in this increment.
//!
//! # Sources, and departures from them
//!
//! Every aerodynamic and propulsion constant, with its provenance and whether it is measured,
//! assumed or extrapolated, is tabulated in the `aero.rs` doc comment. In summary:
//!
//! - The **Poll–Schumann B772 energy budget** is implemented in *form* but not with the PS
//!   coefficient set, which is not in this tree and was not reachable offline. The polar is
//!   instead pinned to the PS-derived calibration target the brief quotes — clean `(L/D)max`
//!   20.8–21.4 at 174 t, against Boeing's ~20.7:1 from the Malaysian SIR Appendix 1.6E driftdown.
//!   This is a declared departure, not a silent substitution.
//! - **Windmilling-engine and RAT drag increments are uncertain parameters, not constants**:
//!   there are no public Trent 892 figures. With their default bands the unpowered glide from
//!   35,000 ft runs 85–105 NM, which contains the ~100 NM the brief records.
//! - **Drag rise and pitch above M0.87 are labelled extrapolated.** The brief calls for them to
//!   be shaped from NASA Common Research Model data, which is not in this tree; Lock's
//!   fourth-power law stands in, with its coefficient a swept parameter. Every model including
//!   Boeing's extrapolates beyond M0.87–0.91. Time spent above the crest Mach is recorded per
//!   descent as the `time_extrapolated_s` latent so no result can quietly rest on it.
//! - **MMO is 0.87** from the type certificate, not the 0.89 OpenAP and Poll–Schumann list.
//! - Operational descent rates from mirrored copies of copyrighted manuals (777 FCTM, operator
//!   QRHs) are used **as modelling parameters with a declared sensitivity and are not cited**;
//!   the sampled rate bands bracket them. The FAA/CASA rulemaking fuel-caution threshold is
//!   citable and is used. **Holland's 00:19 descent-rate bounds are deliberately not imported**
//!   as a constraint: they are conditional on a transient assumption this project declines to
//!   treat as established, and importing them would kill the deliberate-descent branch by
//!   assumption rather than by evidence.
//!
//! # Breakup family, and the retired sink-versus-float hook
//!
//! `debris_class` is the breakup FAMILY (0 intact, 1 broken, 2 fragmented), assigned here against
//! settling's definition (`results/breakup-field-candidate.md`) and drawn once per impact sample,
//! with the three probabilities emitted beside it. Architecture accepted this as the contract on
//! 2026-10-09: hydroacoustics and settling read the draw and neither redraws it. It is a latent and
//! a prediction column rather than an `ImpactView` field because adding a field is a core change
//! (core request 4). Debris-configuration EVIDENCE (flap position, recovered-item energy class) is
//! still out of scope by decision; this is the impact-level family, not a likelihood.
//!
//! The `sinks_not_floats` hook was RETIRED on 2026-10-09 by architecture ruling: the sink-versus-
//! float partition belongs to settling, which emits each element's fate (settled or afloat). One
//! owner per partition. This module emits nothing for it.

mod aero;
mod atmos;
mod integrator;
mod onset;
mod profile;
mod taxonomy;

use hypothesis::{
    Atmosphere, Descent, EpochState, FlightState, Hypothesis, Impact, ImpactView, Terminal, TerminalEpoch,
};
use serde::Deserialize;

use aero::{Aero, Configuration, Range};
use integrator::{Body, Integrator};
use onset::{Onset, OnsetConfig};
use profile::{EnvelopeConfig, Flying};
use taxonomy::{Control, Family, Initiation, Propulsion};

/// Sampled aerodynamic and propulsion parameters. Each entry may be a number (fixed) or a
/// `[lo, hi]` pair (sampled uniformly per descent and recorded as a latent).
#[derive(Deserialize, Debug, Clone, PartialEq)]
#[serde(deny_unknown_fields)]
struct AeroParams {
    wing_area_m2: f64,
    span_m: f64,
    oswald_efficiency: Range,
    /// The calibration target. `c_d0` is derived from it, never set independently.
    ld_max_clean: Range,
    mach_crest: f64,
    wave_drag_coefficient: Range,
    crest_cl_sensitivity: f64,
    tuck_cl_per_mach: Range,
    c_l_max_clean: f64,
    windmilling_per_engine: Range,
    rat_increment: Range,
    speedbrake_increment: Range,
    landing_configuration_increment: Range,
    sea_level_static_thrust_n: f64,
    idle_thrust_fraction: Range,
    thrust_density_exponent: f64,
    tsfc_kg_per_n_s: Range,
}

impl AeroParams {
    fn draw(&self, uniform: &mut dyn FnMut() -> f64) -> Aero {
        Aero {
            wing_area_m2: self.wing_area_m2,
            span_m: self.span_m,
            oswald: self.oswald_efficiency.draw(uniform),
            ld_max_clean: self.ld_max_clean.draw(uniform),
            mach_crest: self.mach_crest,
            wave_drag_coefficient: self.wave_drag_coefficient.draw(uniform),
            crest_cl_sensitivity: self.crest_cl_sensitivity,
            tuck_cl_per_mach: self.tuck_cl_per_mach.draw(uniform),
            c_l_max_clean: self.c_l_max_clean,
            windmilling_per_engine: self.windmilling_per_engine.draw(uniform),
            rat_increment: self.rat_increment.draw(uniform),
            speedbrake_increment: self.speedbrake_increment.draw(uniform),
            landing_configuration_increment: self.landing_configuration_increment.draw(uniform),
            sea_level_static_thrust_n: self.sea_level_static_thrust_n,
            idle_thrust_fraction: self.idle_thrust_fraction.draw(uniform),
            thrust_density_exponent: self.thrust_density_exponent,
            tsfc_kg_per_n_s: self.tsfc_kg_per_n_s.draw(uniform),
        }
    }

    /// The midpoint of every sampled band. `Range::draw` is `lo + (hi - lo) * u`, so a uniform
    /// pinned at 0.5 is exactly the midpoint and a fixed entry is itself.
    ///
    /// Used only by [`EndOfFlight::predicted_exhaustion`], which must return the same number from
    /// `takeover_time` and from `descend`: the two hooks have separate uniform streams, and
    /// `descend` recovers the onset mechanism from the lead this prediction implies. Drawing the
    /// aero here would make the two disagree. The descent itself always uses the sampled draw.
    fn nominal(&self) -> Aero {
        self.draw(&mut || 0.5)
    }

    fn check(&self) -> Result<(), String> {
        for (name, r) in [
            ("oswald_efficiency", self.oswald_efficiency),
            ("ld_max_clean", self.ld_max_clean),
            ("wave_drag_coefficient", self.wave_drag_coefficient),
            ("tuck_cl_per_mach", self.tuck_cl_per_mach),
            ("windmilling_per_engine", self.windmilling_per_engine),
            ("rat_increment", self.rat_increment),
            ("speedbrake_increment", self.speedbrake_increment),
            ("landing_configuration_increment", self.landing_configuration_increment),
            ("idle_thrust_fraction", self.idle_thrust_fraction),
            ("tsfc_kg_per_n_s", self.tsfc_kg_per_n_s),
        ] {
            r.check(&format!("aero.{name}"))?;
        }
        if !(self.wing_area_m2 > 0.0 && self.span_m > 0.0 && self.mach_crest > 0.0 && self.c_l_max_clean > 0.0) {
            return Err("aero: wing_area_m2, span_m, mach_crest and c_l_max_clean must be positive".into());
        }
        Ok(())
    }
}

#[derive(Deserialize, Debug, Clone, PartialEq)]
#[serde(deny_unknown_fields)]
struct Params {
    /// Base integration step, s. A parameter: the core filter's 5 s manoeuvre step does not
    /// constrain this module.
    step_s: f64,
    /// Fine step through the flame-out transition, s.
    fine_step_s: f64,
    /// Half-width of the fine-step window around the transition, s.
    fine_window_s: f64,
    /// Ceiling on integrated flight time, s.
    max_flight_s: f64,
    /// Descents returned per child.
    descents_per_child: usize,
    /// Mass to use when the hand-off carries NaN (it does today: core request 1). 174 t is the
    /// reference mass of the brief's calibration target and is about the 9M-MRO zero-fuel mass.
    fallback_mass_kg: f64,
    /// Fuel remaining to assume when the hand-off carries NaN (core request 1).
    ///
    /// **There is deliberately no `fallback_predicted_exhaustion_unix_s`.** Predicted exhaustion
    /// is always derived from the fuel state by [`EndOfFlight::predicted_exhaustion`]; a
    /// configured exhaustion time is the 00:17:30 anchor the architecture removed, and §4 of the
    /// brief says it must not come back. If the fuel state is missing, this fallback fires and is
    /// recorded, which is a defect in the hand-off rather than a number to use quietly.
    fallback_fuel_kg: f64,
    /// Relative prior weights of the propulsion states, in `Propulsion::ALL` order.
    propulsion_weights: [f64; 3],
    /// Relative prior weights of the control states, in `Control::ALL` order.
    control_weights: [f64; 4],
    /// Keep a descent that never reached the sea as its own impact sample instead of finishing it
    /// on a best-glide. **Default off.** A negative result is kept, not deleted: with the flag
    /// off the fact is still recorded in the `timed_out` latent, and with it on the unconverged
    /// state itself is emitted for inspection. It must stay off for any reported impact PDF.
    emit_timed_out_descents: bool,
    aero: AeroParams,
    onset: OnsetConfig,
    envelope: EnvelopeConfig,
}

struct EndOfFlight {
    params: Params,
    families: Vec<Family>,
}

/// The latent columns, in order. Only this module's own impact hook can read them, which is why
/// the two deferred hooks and the flame-out time are also listed as core requests.
const LATENTS: &[&str] = &[
    "onset_unix_s",
    "onset_mechanism",
    "predicted_endurance_at_onset_s",
    "onset_support_truncated_fraction",
    "realised_flameout_unix_s",
    "flameout_minus_predicted_s",
    "engines_thrusting_at_onset",
    "control_requested",
    "control_realised",
    "recovery_attempted",
    "recovery_demonstrated",
    "profile_shape",
    "family_prior",
    "time_descending_s",
    "max_descent_rate_fpm",
    "time_extrapolated_s",
    "max_mach",
    "max_altitude_ft",
    "impact_vertical_speed_mps",
    "ld_max_clean",
    "windmilling_per_engine",
    "rat_increment",
    "mass_kg_assumed",
    "fuel_kg_assumed",
    // Seconds the CORE flew this trajectory on powered dynamics after its own tanks ran dry,
    // between the hand-off and this module's takeover. Non-zero when the module's predicted
    // exhaustion (its own TSFC burn, 12.7 % below the core's FPPM burn at the fixture state) lands
    // after the core's realised exhaustion: the core then keeps cruising with nothing in the
    // tanks, and the module starts from a dry aircraft. This is the measured cost of the burn gap
    // until core request 3 gives both stages one fuel-flow model. Zero if the core had not run
    // dry by the takeover. When non-zero, `realised_flameout_unix_s` above is the takeover time,
    // not the core's exhaustion, which is `onset_unix_s` minus this.
    "powered_after_core_exhaustion_s",
    // Ground velocity at takeover, so that a consumer can place the aircraft at a burst that fell
    // BEFORE the takeover - which the module never flies through and so cannot report directly.
    "takeover_ground_velocity_east_mps",
    "takeover_ground_velocity_north_mps",
    // Position at the last burst this module flew through (the latest requested epoch), when the
    // aircraft was still airborne then; NaN if it was already down or if the takeover came after
    // every burst. Used for impact displacement from the 00:19:37 position.
    "last_burst_latitude_deg",
    "last_burst_longitude_deg",
    "weather_clamped",
    "timed_out",
    // Attitude at contact, ruled into the interface by architecture on 2026-10-08. Both are
    // derived from the integrated state at the solved surface crossing. They are latents rather
    // than `ImpactView` fields until core request 4 lifts them, which is why request 4 must not
    // drift: settling and hydroacoustics read them by name in the meantime.
    "impact_heading_deg",
    "impact_bank_deg",
    // The impact energy-transfer columns, ruled 2026-10-08. All NaN at first pass: the integrator
    // terminates AT the sea surface, so P(t) is the power history of an event this module does not
    // simulate. Deriving one from `tau ~ dv / a_bar` without a justified deceleration model would
    // make tau a function of the taxonomy family by the back door, which the ruling forbids.
    // Conventions, the fragment-tracking rule, the n_pulses threshold and what would remove the
    // NaN are in `results/eof-impact-energy-method.md`.
    //
    // Kinetic energy AT CONTACT is deliberately not among these: it is already a first-class
    // field, `ImpactView::kinetic_energy_j`, which the runner computes as 0.5 m |v|^2 from this
    // module's own impact state, with `vertical_kinetic_energy_j` beside it. Contact energy is an
    // upper bound on `impact_energy_transferred_j` and must never be aliased to it.
    "impact_energy_transferred_j",
    "energy_transfer_t05_s",
    "energy_transfer_t95_s",
    "energy_transfer_tau90_s",
    "energy_transfer_peak_rate_w",
    "energy_transfer_n_pulses",
    // How the energy-transfer columns were obtained. 0 = not computed, no water-entry model;
    // non-zero values are reserved for derivations that do not exist yet. Composition rule 4 makes
    // NaN mean "not computed", and this flag is what lets a consumer tell that from "computed as
    // zero" mechanically rather than by reading prose.
    "impact_tau_method",
    // Breakup family, PROVISIONAL, implemented 2026-10-09 against settling's candidate definition
    // (`results/breakup-field-candidate.md`, sections 2-3). Settling owns the definition and the
    // constants; this module implements the assignment. The three probabilities come from the
    // vertical and total contact speeds; `debris_class` is the family index 0 intact, 1 broken,
    // 2 fragmented, DRAWN ONCE per impact sample so that every consumer conditions on the same
    // draw and no two modules can disagree about one physical event. NaN where the rule refuses
    // (no mass, non-finite speed), never a default family.
    "breakup_p_intact",
    "breakup_p_broken",
    "breakup_p_fragmented",
    "debris_class",
    // `sinks_not_floats` was retired here on 2026-10-09 (architecture ruling): settling owns the
    // sink-versus-float partition through its emitted element fates.
];

/// Settling's breakup-family constants, quoted verbatim from `results/breakup-field-candidate.md`
/// section 2. They live in settling's table; the fixtures test below is what keeps this copy honest.
const BREAKUP_INTACT_DESCENT_MPS: f64 = 8.0;
const BREAKUP_INTACT_SPEED_MPS: f64 = 100.0;
const BREAKUP_FRAGMENTED_SPEED_MPS: f64 = 110.0;
const BREAKUP_LOG_WIDTH: f64 = 0.2;

/// P(intact), P(broken), P(fragmented) from the descent rate and total speed at contact, m/s.
/// Settling's rule: with L the logistic and V_d floored at 0.01 m/s,
/// P(intact) = L(ln(a/V_d)/s) L(ln(c/V)/s); P(fragmented) = (1 - P(intact)) L(ln(V/b)/s).
/// Refuses (None) outside its domain rather than defaulting a family.
fn breakup_probabilities(descent_mps: f64, speed_mps: f64) -> Option<[f64; 3]> {
    if !(speed_mps.is_finite() && speed_mps > 0.0 && descent_mps.is_finite()) || descent_mps > speed_mps + 1e-9 {
        return None;
    }
    let l = |x: f64| 1.0 / (1.0 + (-x).exp());
    let v_d = descent_mps.abs().max(0.01);
    let s = BREAKUP_LOG_WIDTH;
    let intact = l((BREAKUP_INTACT_DESCENT_MPS / v_d).ln() / s) * l((BREAKUP_INTACT_SPEED_MPS / speed_mps).ln() / s);
    let fragmented = (1.0 - intact) * l((speed_mps / BREAKUP_FRAGMENTED_SPEED_MPS).ln() / s);
    Some([intact, 1.0 - intact - fragmented, fragmented])
}

/// Value of the `impact_tau_method` latent when no water-entry model exists, which is every sample
/// at first pass.
const TAU_METHOD_NOT_COMPUTED: f64 = 0.0;

pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String> {
    let params: Params = params.clone().try_into().map_err(|e| format!("end-of-flight: {e}"))?;
    if !(params.step_s > 0.0 && params.fine_step_s > 0.0 && params.fine_window_s >= 0.0 && params.max_flight_s > 0.0) {
        return Err("end-of-flight: step_s, fine_step_s and max_flight_s must be positive and fine_window_s non-negative".into());
    }
    if params.descents_per_child == 0 {
        return Err("end-of-flight: descents_per_child must be at least 1".into());
    }
    if params.propulsion_weights.iter().any(|w| !w.is_finite() || *w < 0.0) || params.propulsion_weights.iter().sum::<f64>() <= 0.0 {
        return Err("end-of-flight: propulsion_weights must be non-negative with a positive sum".into());
    }
    if params.control_weights.iter().any(|w| !w.is_finite() || *w < 0.0) || params.control_weights.iter().sum::<f64>() <= 0.0 {
        return Err("end-of-flight: control_weights must be non-negative with a positive sum".into());
    }
    if !(params.fallback_mass_kg > 1_000.0 && params.fallback_fuel_kg >= 0.0) {
        return Err("end-of-flight: fallback_mass_kg must exceed 1 t and fallback_fuel_kg be non-negative".into());
    }
    params.aero.check()?;
    params.onset.check()?;
    params.envelope.check()?;
    Ok(Box::new(EndOfFlight { params, families: taxonomy::legal_families() }))
}

impl Hypothesis for EndOfFlight {
    fn terminal(&self) -> Option<&dyn Terminal> {
        Some(self)
    }

    /// No observation is consumed by this module. The runner scores the 00:19 bursts with the
    /// core measurement model; the log-on lag likelihood (`m0019a.logon`) is a later increment
    /// and will be declared here when it exists.
    fn observations(&self) -> Vec<String> {
        Vec::new()
    }

    /// The breakup family as a named prediction column, so it reaches the impacts file and the
    /// composer under its own name. It is the SAME draw as the `debris_class` latent - read back,
    /// never redrawn - and NaN where the latent is NaN (the rule refused) or not supplied.
    fn prediction_columns(&self) -> Vec<String> {
        vec!["debris_class".into()]
    }

    fn predict(&self, impact: &ImpactView, out: &mut [f64]) {
        let k = LATENTS.iter().position(|n| *n == "debris_class");
        let value = match k {
            Some(k) if impact.latents.len() == LATENTS.len() => impact.latents[k],
            _ => f64::NAN,
        };
        if let Some(slot) = out.first_mut() {
            *slot = value;
        }
    }
}

/// Everything about a parent trajectory this module needs, with the fallbacks applied once.
struct Parent {
    /// Exhaustion under CONTINUED CRUISE, derived from `fuel_kg` — never a realised flame-out and
    /// never a configured clock time. See [`EndOfFlight::predicted_exhaustion`].
    predicted_exhaustion_unix_s: f64,
    mass_kg: f64,
    fuel_kg: f64,
    /// A fallback fired for the mass. On a real hand-off this must be false for every parent.
    mass_assumed: bool,
    /// A fallback fired for the fuel. On a real hand-off this must be false for every parent.
    fuel_assumed: bool,
}

impl EndOfFlight {
    fn parent(&self, state: &FlightState) -> Parent {
        let mass_known = state.mass_kg.is_finite() && state.mass_kg > 1_000.0;
        let fuel_known = state.fuel_kg.is_finite() && state.fuel_kg >= 0.0;
        let mass_kg = if mass_known { state.mass_kg } else { self.params.fallback_mass_kg };
        let fuel_kg = if fuel_known { state.fuel_kg } else { self.params.fallback_fuel_kg };
        Parent {
            predicted_exhaustion_unix_s: self.predicted_exhaustion(state, mass_kg, fuel_kg),
            mass_kg,
            fuel_kg,
            mass_assumed: !mass_known,
            fuel_assumed: !fuel_known,
        }
    }

    /// Exhaustion time under **continued cruise**, computed per trajectory from the handed-off
    /// fuel state.
    ///
    /// This is deliberately not `FlightState::realised_flameout_unix_s`. That field is an
    /// *outcome*: it is NaN for every trajectory still holding fuel at the hand-off — 43.14 % of
    /// the reference posterior — and triggering a descent on it would assume foreknowledge no crew
    /// had, which §4 of the brief forbids as circular. An earlier version of this function read
    /// that field and fell through to a configured constant of 00:17:30 UTC whenever it was NaN,
    /// which silently reinstated for nearly half the posterior the fixed exhaustion anchor the
    /// architecture had removed. There is no such constant in this module any more: if the fuel
    /// state is missing, `fallback_fuel_kg` fires and says so in the `fuel_kg_assumed` latent.
    ///
    /// Method. Level cruise is held at the hand-off altitude and true airspeed. Lift equals
    /// weight, so `c_l` follows from the dynamic pressure; `c_d` comes from the module's own polar
    /// at the hand-off Mach; thrust required equals drag; and the burn is `thrust * tsfc`. The
    /// integration is explicit in 60 s steps so that the mass lost to the burn feeds back into
    /// `c_l` — a single-point flow would overestimate endurance, because a lighter aircraft burns
    /// less. ISA is used rather than the runner's weather: the prediction is a cruise-burn
    /// estimate, `takeover_time` has no `Atmosphere` in scope, and the ERA5 temperature anomaly is
    /// small against the TSFC band this model sweeps.
    ///
    /// Returns `f64::INFINITY` when there is no fuel to burn and no sensible cruise condition, so
    /// that an anticipatory onset simply never triggers rather than triggering at an invented time.
    fn predicted_exhaustion(&self, state: &FlightState, mass_kg: f64, fuel_kg: f64) -> f64 {
        if !(fuel_kg > 0.0) {
            // Already dry at the hand-off: exhaustion is the realised time when we have it, and
            // otherwise the hand-off epoch itself. Either way it is not in the future.
            return if state.realised_flameout_unix_s.is_finite() { state.realised_flameout_unix_s } else { state.unix_s };
        }
        let aero = self.params.aero.nominal();
        let cfg = Configuration::powered();
        let air = Atmosphere::at(&atmos::Standard, state.unix_s, state.altitude_ft, state.latitude_deg, state.longitude_deg);
        let rho = atmos::density_kg_m3(air.pressure_pa, air.temperature_k);
        let tas = state.true_air_speed_mps;
        let q = 0.5 * rho * tas * tas;
        if !(q > 0.0) || !(aero.wing_area_m2 > 0.0) {
            return f64::INFINITY;
        }
        const STEP_S: f64 = 60.0;
        let mut remaining = fuel_kg;
        let mut mass = mass_kg;
        let mut elapsed = 0.0;
        // 24 h of cruise is far beyond any trajectory this module sees; the cap exists so a
        // pathological state cannot spin here.
        while remaining > 0.0 && elapsed < 86_400.0 {
            let c_l = (mass * atmos::G0) / (q * aero.wing_area_m2);
            let c_d = aero.c_d(c_l, state.mach, &cfg);
            let thrust_n = c_d * q * aero.wing_area_m2;
            let flow = aero.fuel_flow_kg_s(thrust_n);
            if !(flow > 0.0) {
                return f64::INFINITY;
            }
            let burn = flow * STEP_S;
            if burn >= remaining {
                elapsed += remaining / flow;
                break;
            }
            remaining -= burn;
            mass -= burn;
            elapsed += STEP_S;
        }
        state.unix_s + elapsed
    }

    /// Draw the propulsion and control axes, restricted to the cells legal for `mechanism`, and
    /// return them with their joint prior weight.
    fn draw_axes(&self, mechanism: Initiation, uniform: &mut dyn FnMut() -> f64) -> (Propulsion, Control, f64) {
        let mut weights = self.params.propulsion_weights;
        for (i, p) in Propulsion::ALL.iter().enumerate() {
            if !(Family { initiation: mechanism, propulsion: *p, control: Control::NoIntervention }).is_legal() {
                weights[i] = 0.0;
            }
        }
        let (propulsion, p_prior) = pick(&weights, &Propulsion::ALL, uniform);
        let (control, c_prior) = pick(&self.params.control_weights, &Control::ALL, uniform);
        (propulsion, control, p_prior * c_prior)
    }

    /// Integrate one descent from the takeover state.
    #[allow(clippy::too_many_arguments)]
    fn fly(
        &self,
        takeover: &FlightState,
        parent: &Parent,
        atmosphere: &dyn Atmosphere,
        onset: &Onset,
        propulsion: Propulsion,
        control: Control,
        aero: Aero,
        epochs: &[TerminalEpoch],
        uniform: &mut dyn FnMut() -> f64,
    ) -> (Impact, Vec<Option<EpochState>>, Flying, integrator::Trace, f64) {
        let start = Body {
            unix_s: takeover.unix_s,
            latitude_deg: takeover.latitude_deg,
            longitude_deg: takeover.longitude_deg,
            pressure_altitude_ft: takeover.altitude_ft,
            tas_mps: takeover.true_air_speed_mps,
            gamma_rad: 0.0,
            heading_rad: takeover.heading_deg.to_radians(),
            mass_kg: parent.mass_kg,
            fuel_kg: if propulsion == Propulsion::NeitherThrusting { 0.0 } else { parent.fuel_kg },
        };
        let shape = self.params.envelope.sample(&start, propulsion, control, &aero, uniform);
        let flying = std::cell::RefCell::new(Flying::new(shape, aero, propulsion, &self.params.envelope));
        let it = Integrator {
            aero,
            step_s: self.params.step_s,
            fine_step_s: self.params.fine_step_s,
            fine_window_s: self.params.fine_window_s,
            max_flight_s: self.params.max_flight_s,
        };

        // The realised flame-out emerges from the integration: it is the first time the module's
        // own fuel state reaches zero, which a descent moves away from the predicted exhaustion.
        // Single flame-out event in this increment, per the brief's §5.
        let realised_flameout = std::cell::Cell::new(if propulsion == Propulsion::NeitherThrusting { onset.unix_s } else { f64::NAN });
        let states = std::cell::RefCell::new(vec![None; epochs.len()]);
        let previous = std::cell::Cell::new(Option::<(Body, f64)>::None);

        let transition = if realised_flameout.get().is_finite() {
            Some(realised_flameout.get())
        } else {
            Some(parent.predicted_exhaustion_unix_s)
        };
        let trace = it.run(
            start,
            atmosphere,
            transition,
            &mut |body, elapsed| {
                if body.fuel_kg <= 0.0 && !realised_flameout.get().is_finite() {
                    realised_flameout.set(body.unix_s);
                }
                let mut f = flying.borrow_mut();
                if realised_flameout.get().is_finite() && body.unix_s >= realised_flameout.get() {
                    f.set_engines_thrusting(0);
                }
                f.command(body, elapsed)
            },
            &mut |body, air| {
                let factor = atmos::geometric_rate_factor(body.pressure_altitude_ft, air.temperature_k);
                let up = body.vertical_speed_mps() * factor;
                flying.borrow_mut().observe(body, up);
                if let Some((prev, prev_up)) = previous.get() {
                    let mut states = states.borrow_mut();
                    for (k, epoch) in epochs.iter().enumerate() {
                        if states[k].is_none() && prev.unix_s <= epoch.unix_s && epoch.unix_s <= body.unix_s {
                            states[k] = Some(interpolate(&prev, prev_up, body, up, epoch.unix_s, air));
                        }
                    }
                }
                previous.set(Some((*body, up)));
            },
        );

        let impact = Impact {
            unix_s: trace.impact.unix_s,
            latitude_deg: trace.impact.latitude_deg,
            longitude_deg: trace.impact.longitude_deg,
            velocity_east_mps: trace.impact_velocity_east_mps,
            velocity_north_mps: trace.impact_velocity_north_mps,
            velocity_up_mps: trace.impact_vertical_speed_mps,
            mass_kg: trace.impact.mass_kg,
        };
        (impact, states.into_inner(), flying.into_inner(), trace, realised_flameout.get())
    }
}

/// Linear interpolation of a body state onto a burst time, with the wind of the bracketing step.
fn interpolate(a: &Body, a_up: f64, b: &Body, b_up: f64, at: f64, air: &hypothesis::Air) -> EpochState {
    let span = b.unix_s - a.unix_s;
    let f = if span > 0.0 { ((at - a.unix_s) / span).clamp(0.0, 1.0) } else { 0.0 };
    let mix = |x: f64, y: f64| x + (y - x) * f;
    let heading = mix(a.heading_rad, b.heading_rad);
    let horizontal = mix(a.tas_mps * a.gamma_rad.cos(), b.tas_mps * b.gamma_rad.cos());
    EpochState {
        latitude_deg: mix(a.latitude_deg, b.latitude_deg),
        longitude_deg: mix(a.longitude_deg, b.longitude_deg),
        altitude_ft: mix(a.pressure_altitude_ft, b.pressure_altitude_ft),
        velocity_east_mps: horizontal * heading.sin() + air.wind_east_mps,
        velocity_north_mps: horizontal * heading.cos() + air.wind_north_mps,
        velocity_up_mps: mix(a_up, b_up),
    }
}

/// Draw one option from relative weights, returning it and its normalised prior.
fn pick<T: Copy>(weights: &[f64], options: &[T], uniform: &mut dyn FnMut() -> f64) -> (T, f64) {
    let total: f64 = weights.iter().sum();
    if !(total > 0.0) {
        return (options[options.len() - 1], 0.0);
    }
    let draw = uniform() * total;
    let mut acc = 0.0;
    for (i, w) in weights.iter().enumerate() {
        acc += *w;
        if draw < acc {
            return (options[i], *w / total);
        }
    }
    let last = weights.len() - 1;
    (options[last], weights[last] / total)
}

impl Terminal for EndOfFlight {
    fn families(&self) -> Vec<String> {
        self.families.iter().map(Family::label).collect()
    }

    fn latent_columns(&self) -> Vec<String> {
        LATENTS.iter().map(|s| (*s).to_string()).collect()
    }

    /// The module's takeover time is the sampled **descent onset**, which for an anticipatory or
    /// fuel-cue mechanism is *earlier* than any flame-out. The trait's doc comment calls this
    /// "the first flame-out"; that reading is specific to a flame-out-associated onset and is
    /// raised as core request 2.
    fn takeover_time(&self, handoff: &FlightState, uniform: &mut dyn FnMut() -> f64) -> (f64, f64) {
        let parent = self.parent(handoff);
        let onset = self.params.onset.draw(handoff.unix_s, parent.predicted_exhaustion_unix_s, uniform);
        (onset.unix_s.max(handoff.unix_s), onset.log_q_correction)
    }

    fn descend(
        &self,
        takeover: &FlightState,
        atmosphere: &dyn Atmosphere,
        uniform: &mut dyn FnMut() -> f64,
        epochs: &[TerminalEpoch],
        _score: &dyn Fn(&[Option<EpochState>]) -> f64,
    ) -> Vec<Descent> {
        let parent = self.parent(takeover);
        // The onset mechanism was drawn in `takeover_time`, whose uniform stream is not shared
        // with this hook. It is recovered exactly rather than redrawn independently: the
        // mechanism is sampled from its conditional posterior given the realised onset lead,
        // p(m | lead) proportional to w_m f_m(lead), so the joint law of (lead, mechanism) is the
        // same as the forward draw's. Core request 2 would remove the need for this.
        let lead = parent.predicted_exhaustion_unix_s - takeover.unix_s;
        let mut out = Vec::with_capacity(self.params.descents_per_child);
        for _ in 0..self.params.descents_per_child {
            let (mechanism, mechanism_prior) = self.params.onset.classify(lead, uniform);
            // An aircraft with no fuel at takeover has no power available, whatever was intended:
            // its propulsion state is NeitherThrusting, not a draw. Before this guard the axis was
            // drawn regardless, so a dry parent could be labelled two-thrusting and handed a
            // POWERED profile (a level-off held on thrust, say) that the integrator then flew with
            // the engines cut at the first step - wrong label and incoherent physics. On the
            // full-scale 00:11 snapshot that was ~2/3 of the dry-at-hand-off descents, and every
            // child the core flew dry before takeover (~50% of the weight) was exposed to it.
            // A fuel-cue RESPONSE is impossible from empty tanks, and FuelCue x NeitherThrusting is
            // not a legal cell, so a dry fuel-cue label becomes flame-out-associated. The mechanism
            // label stays provisional until core request 2 regardless.
            let dry = !(parent.fuel_kg > 0.0);
            let (mechanism, mechanism_prior) = if dry && mechanism == Initiation::FuelCue {
                let w = self.params.onset.mechanism_weights;
                let total: f64 = w.iter().sum();
                (Initiation::FlameOutAssociated, if total > 0.0 { w[2] / total } else { 0.0 })
            } else {
                (mechanism, mechanism_prior)
            };
            let onset = Onset {
                unix_s: takeover.unix_s,
                mechanism,
                predicted_endurance_at_onset_s: lead,
                mechanism_prior,
                support_truncated_fraction: f64::NAN,
                log_q_correction: 0.0,
            };
            let (propulsion, control, axes_prior) = if dry {
                let (control, c_prior) = pick(&self.params.control_weights, &Control::ALL, uniform);
                (Propulsion::NeitherThrusting, control, c_prior)
            } else {
                self.draw_axes(mechanism, uniform)
            };
            let aero = self.params.aero.draw(uniform);
            let (impact, states, flying, trace, realised_flameout) =
                self.fly(takeover, &parent, atmosphere, &onset, propulsion, control, aero, epochs, uniform);

            // A descent that never reached the sea is a negative result. By default it is
            // finished on a best glide so the sample is usable, and the fact is recorded;
            // `emit_timed_out_descents` keeps the unconverged state instead. Nothing is deleted.
            let (impact, states, trace) = if trace.timed_out && !self.params.emit_timed_out_descents {
                let glide = self.finish_on_a_glide(&impact, &parent, atmosphere, aero, epochs, states);
                (glide.0, glide.1, trace)
            } else {
                (impact, states, trace)
            };

            let realised_control = flying.realised_control();
            // Breakup family from the contact state, drawn once for this impact sample. The speeds
            // are the ones the runner's kinetic_energy_j and vertical_kinetic_energy_j are made
            // from, so V and V_d here are exactly sqrt(2e) and sqrt(2e_v) of settling's rule.
            let contact_speed = (impact.velocity_east_mps.powi(2) + impact.velocity_north_mps.powi(2) + impact.velocity_up_mps.powi(2)).sqrt();
            let contact_descent = (-impact.velocity_up_mps).max(0.0);
            let breakup = if impact.mass_kg > 0.0 { breakup_probabilities(contact_descent, contact_speed) } else { None };
            let (breakup_p, debris_class) = match breakup {
                Some(p) => {
                    let u = uniform();
                    let class = if u < p[0] { 0.0 } else if u < p[0] + p[1] { 1.0 } else { 2.0 };
                    (p, class)
                }
                None => ([f64::NAN; 3], f64::NAN),
            };
            let latents = vec![
                takeover.unix_s,
                mechanism.code(),
                lead,
                f64::NAN, // the truncation fraction is known in takeover_time only: core request 2
                realised_flameout,
                realised_flameout - parent.predicted_exhaustion_unix_s,
                propulsion.code(),
                control.code(),
                realised_control.code(),
                f64::from(u8::from(flying.recovery_attempted)),
                f64::from(u8::from(flying.recovery_demonstrated)),
                flying.profile.shape.code(),
                mechanism_prior * axes_prior,
                trace.time_descending_s,
                trace.max_descent_rate_fpm,
                trace.time_extrapolated_s,
                trace.max_mach,
                trace.max_altitude_ft,
                impact.velocity_up_mps,
                aero.ld_max_clean,
                aero.windmilling_per_engine,
                aero.rat_increment,
                f64::from(u8::from(parent.mass_assumed)),
                f64::from(u8::from(parent.fuel_assumed)),
                if takeover.realised_flameout_unix_s.is_finite() {
                    (takeover.unix_s - takeover.realised_flameout_unix_s).max(0.0)
                } else {
                    0.0
                },
                takeover.ground_velocity_east_mps,
                takeover.ground_velocity_north_mps,
                states.last().copied().flatten().map_or(f64::NAN, |s| s.latitude_deg),
                states.last().copied().flatten().map_or(f64::NAN, |s| s.longitude_deg),
                f64::from(u8::from(trace.clamped)),
                f64::from(u8::from(trace.timed_out)),
                trace.impact.heading_rad.to_degrees().rem_euclid(360.0),
                trace.impact_bank_rad.to_degrees(),
                // The six energy-transfer columns. NaN is a result here, not a gap: the
                // integrator stops at the surface, so there is no P(t) to integrate. See
                // `results/eof-impact-energy-method.md`.
                f64::NAN, // impact_energy_transferred_j
                f64::NAN, // energy_transfer_t05_s
                f64::NAN, // energy_transfer_t95_s
                f64::NAN, // energy_transfer_tau90_s
                f64::NAN, // energy_transfer_peak_rate_w
                f64::NAN, // energy_transfer_n_pulses
                TAU_METHOD_NOT_COMPUTED,
                breakup_p[0],
                breakup_p[1],
                breakup_p[2],
                debris_class,
            ];
            debug_assert_eq!(latents.len(), LATENTS.len());
            let family = taxonomy::index_of(&Family { initiation: mechanism, propulsion, control: realised_control })
                .or_else(|| taxonomy::index_of(&Family { initiation: mechanism, propulsion, control }))
                .unwrap_or(0);
            out.push(Descent { impact, family, at_epochs: states, latents, log_q_correction: 0.0 });
        }
        out
    }
}

impl EndOfFlight {
    /// Finish an unconverged descent on a best glide from its last state, so a timed-out phugoid
    /// still yields a usable impact sample. The `timed_out` latent records that this happened.
    fn finish_on_a_glide(
        &self,
        last: &Impact,
        parent: &Parent,
        atmosphere: &dyn Atmosphere,
        aero: Aero,
        epochs: &[TerminalEpoch],
        mut states: Vec<Option<EpochState>>,
    ) -> (Impact, Vec<Option<EpochState>>) {
        let air = atmosphere.at(last.unix_s, 0.0, last.latitude_deg, last.longitude_deg);
        let _ = air;
        let speed = (last.velocity_east_mps.powi(2) + last.velocity_north_mps.powi(2)).sqrt().max(80.0);
        let start = Body {
            unix_s: last.unix_s,
            latitude_deg: last.latitude_deg,
            longitude_deg: last.longitude_deg,
            pressure_altitude_ft: 10_000.0,
            tas_mps: speed,
            gamma_rad: -0.05,
            heading_rad: last.velocity_east_mps.atan2(last.velocity_north_mps),
            mass_kg: parent.mass_kg,
            fuel_kg: 0.0,
        };
        let it = Integrator {
            aero,
            step_s: self.params.step_s,
            fine_step_s: self.params.fine_step_s,
            fine_window_s: 0.0,
            max_flight_s: 3_600.0,
        };
        let cfg = Configuration::glide();
        let mut previous: Option<(Body, f64)> = None;
        let trace = it.run(
            start,
            atmosphere,
            None,
            &mut |_, _| (integrator::Command::BestGlide { bank_rad: 0.0 }, cfg, 0.0),
            &mut |body, air| {
                let up = body.vertical_speed_mps() * atmos::geometric_rate_factor(body.pressure_altitude_ft, air.temperature_k);
                if let Some((prev, prev_up)) = previous {
                    for (k, epoch) in epochs.iter().enumerate() {
                        if states[k].is_none() && prev.unix_s <= epoch.unix_s && epoch.unix_s <= body.unix_s {
                            states[k] = Some(interpolate(&prev, prev_up, body, up, epoch.unix_s, air));
                        }
                    }
                }
                previous = Some((*body, up));
            },
        );
        let _ = &previous;
        (
            Impact {
                unix_s: trace.impact.unix_s,
                latitude_deg: trace.impact.latitude_deg,
                longitude_deg: trace.impact.longitude_deg,
                velocity_east_mps: trace.impact_velocity_east_mps,
                velocity_north_mps: trace.impact_velocity_north_mps,
                velocity_up_mps: trace.impact_vertical_speed_mps,
                mass_kg: trace.impact.mass_kg,
            },
            states,
        )
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use hypothesis::Air;

    /// The parameter block of `run.toml`, so the tests exercise the configuration that would be
    /// lifted into a core config rather than a private one.
    fn params() -> toml::Value {
        let text = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/end-of-flight/run.toml")).expect("run.toml");
        let run: toml::Value = toml::from_str(&text).expect("run.toml parses");
        run.get("hypotheses").and_then(|h| h.get("end-of-flight")).expect("[hypotheses.end-of-flight]").clone()
    }

    /// `smoke/terminal.toml` selects this module for `mh370 terminal` sweeps and has to carry the
    /// parameter block itself, because an override cannot pull `run.toml` in without also pulling
    /// its base, `config/integrated.toml`. The copy is guarded here rather than trusted: if the two
    /// drift, a sweep would quietly run on different physics from the tests.
    #[test]
    fn the_smoke_override_carries_run_toml_parameters_verbatim() {
        let text = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/end-of-flight/smoke/terminal.toml"))
            .expect("smoke/terminal.toml");
        let smoke: toml::Value = toml::from_str(&text).expect("smoke/terminal.toml parses");
        let block = smoke.get("hypotheses").and_then(|h| h.get("end-of-flight")).expect("[hypotheses.end-of-flight]");
        assert_eq!(block, &params(), "smoke/terminal.toml has drifted from run.toml");
        let terminal = smoke.get("terminal").expect("[terminal]");
        assert_eq!(terminal.get("module").and_then(|m| m.as_str()), Some("end-of-flight"));
        assert_eq!(terminal.get("target").and_then(|m| m.as_str()), Some("none"), "the smoke default is the held-out case");
    }

    fn module() -> Box<dyn Hypothesis> {
        new(&params()).expect("the run.toml parameter block constructs the module")
    }

    const ONSET_22_41: f64 = 1_394_232_060.0; // 22:41:00 UTC
    const EXHAUSTION: f64 = 1_394_237_850.0; // 00:17:30 UTC
    const R600: f64 = 1_394_237_969.416; // 00:19:29.416 UTC
    const R1200: f64 = 1_394_237_977.443; // 00:19:37.443 UTC

    /// The derivation that replaced the 00:17:30 anchor, checked against the only independent
    /// number available: the reference run's mean burn of 5,764 kg/h over the whole posterior.
    ///
    /// The module's cruise burn comes from its own polar and a swept TSFC, not from the core's
    /// Boeing-calibrated tables (core request 3), so this is a sanity bound rather than a
    /// calibration. A band of 4,000-8,000 kg/h brackets the reference figure generously; a
    /// derivation outside it means the polar, the TSFC sweep or the level-flight condition is
    /// wrong, not that the band is tight.
    #[test]
    fn the_derived_cruise_burn_is_near_the_reference_run() {
        let h = handoff(ONSET_22_41);
        let predicted = predicted_exhaustion_of(&h);
        let seconds = predicted - h.unix_s;
        assert!(seconds > 0.0 && seconds.is_finite(), "endurance {seconds} s");
        let burn_kg_h = h.fuel_kg / seconds * 3_600.0;
        println!("fuel {:.1} kg, endurance {:.1} s, derived cruise burn {:.0} kg/h, recovered exhaustion {:+.0} s from the fixture's", h.fuel_kg, seconds, burn_kg_h, predicted - EXHAUSTION);
        assert!(
            (4_000.0..8_000.0).contains(&burn_kg_h),
            "derived cruise burn {burn_kg_h:.0} kg/h is outside the sanity band around the reference run's 5,764"
        );
        // And the fixture's scenario is recovered: the fuel load was set to run dry at
        // EXHAUSTION, so the module must find that time from `fuel_kg` alone. The tolerance is
        // the difference between the fixture's flat reference burn and the module's own
        // mass-varying integration, which is the thing being tested.
        assert!(
            (predicted - EXHAUSTION).abs() < 900.0,
            "recovered exhaustion {predicted} is {} s from the fixture's {EXHAUSTION}",
            predicted - EXHAUSTION
        );
    }

    /// The 00:17:30 anchor must not come back, by any route. It was a configured
    /// `exhaustion_target_utc` worth 0.168 nats, the reference run removes it, and an earlier
    /// version of `parent()` reinstated it for the ~43 % of the posterior whose realised flame-out
    /// is NaN. There is now no constant to fall back to: with no fuel state the *fuel* fallback
    /// fires, says so, and the exhaustion is still derived.
    #[test]
    fn no_configured_exhaustion_time_survives_anywhere() {
        let m = module();
        let t = m.terminal().unwrap();
        let names = t.latent_columns();
        let at = |n: &str| names.iter().position(|x| x == n).unwrap();

        // A hand-off with no fuel state at all, as the core sent before request 1 landed.
        let bare = handoff_without_fuel_state(ONSET_22_41);
        let predicted = predicted_exhaustion_of(&bare);
        assert!(
            (predicted - EXHAUSTION).abs() > 1.0,
            "the predicted exhaustion landed exactly on the removed 00:17:30 anchor"
        );
        // and the fallbacks announce themselves rather than supplying a number quietly.
        for d in t.descend(&bare, &atmos::Standard, &mut sweep(0.21), &epochs(), &|_| 0.0) {
            assert_eq!(d.latents[at("mass_kg_assumed")], 1.0);
            assert_eq!(d.latents[at("fuel_kg_assumed")], 1.0);
        }
    }

    /// KNOWN DEFECT, kept as a failing test rather than deleted (found by the 9 Oct smoke run,
    /// `runs/eof-term-n4`). Between `takeover_time` and `descend` the CORE propagates the aircraft
    /// on its own calibrated burn and its own stochastic manoeuvres. `descend` then recomputes the
    /// onset lead from that propagated state, and `classify` recovers the flame-out-associated
    /// mechanism only for a lead of exactly zero. After propagation the lead is never exactly
    /// zero, so every flame-out draw is relabelled: anticipatory if the recomputed lead is
    /// positive, anticipatory with ZERO prior weight if the core ran the tanks dry first. On the
    /// smoke hand-off that was 53 % of the weight with an impossible label, and the
    /// flame-out-associated families were absent altogether.
    ///
    /// This could not happen before the fuel-state fix only because both hooks measured the lead
    /// against the same configured 00:17:30 constant - the anchor that had to go. No module-side
    /// recomputation can be exact while the two hooks see different states; the fix is core
    /// request 2, passing `takeover_time`'s draw to `descend`. The test simulates the core's
    /// propagation with the reference burn and asserts the drawn mechanism survives.
    #[test]
    #[ignore = "fails until core request 2 passes takeover_time's draw into descend; see coordination/architecture.md 2026-10-09"]
    fn the_flameout_mechanism_survives_the_cores_propagation() {
        // Flame-out-associated onset only: the drawn takeover IS the predicted exhaustion.
        let h = handoff(ONSET_22_41);
        let takeover = predicted_exhaustion_of(&h);
        // The core flies from the hand-off to the takeover on ITS burn, which is higher than this
        // module's (5,764 against 5,033 kg/h), so it arrives with less fuel, possibly none.
        let burnt = CRUISE_BURN_KG_S * (takeover - h.unix_s);
        let fuel = (h.fuel_kg - burnt).max(0.0);
        let dry_at = if fuel > 0.0 { f64::NAN } else { h.unix_s + h.fuel_kg / CRUISE_BURN_KG_S };
        let at = FlightState {
            unix_s: takeover,
            fuel_kg: fuel,
            mass_kg: ZFW_KG + fuel,
            realised_flameout_unix_s: dry_at,
            ..handoff(ONSET_22_41)
        };
        let mut v = params();
        v.as_table_mut().unwrap().get_mut("onset").unwrap().as_table_mut().unwrap().insert(
            "mechanism_weights".into(),
            toml::Value::Array(vec![toml::Value::Float(0.0), toml::Value::Float(0.0), toml::Value::Float(1.0)]),
        );
        let m = new(&v).unwrap();
        let t = m.terminal().unwrap();
        let names = t.latent_columns();
        let at_mech = names.iter().position(|n| n == "onset_mechanism").unwrap();
        for d in t.descend(&at, &atmos::Standard, &mut sweep(0.41), &epochs(), &|_| 0.0) {
            assert_eq!(d.latents[at_mech], Initiation::FlameOutAssociated.code(), "a flame-out draw came back relabelled");
        }
    }

    /// Settling's three analogue fixtures (`results/breakup-field-candidate.md` section 2, also
    /// `breakup::tests::analogue_anchors` in settling): two implementations checked against one set
    /// of numbers is the honest form of "one definition" while the constants live in settling's table.
    #[test]
    fn breakup_probabilities_reproduce_settlings_fixtures() {
        let close = |got: [f64; 3], want: [f64; 3], tol: [f64; 3], name: &str| {
            for k in 0..3 {
                assert!((got[k] - want[k]).abs() <= tol[k], "{name}[{k}]: {} against {}", got[k], want[k]);
            }
        };
        // AF447: V_d 55, V 78 -> (5.05e-5, 0.8479, 0.1520)
        close(breakup_probabilities(55.0, 78.0).unwrap(), [5.05e-5, 0.8479, 0.1520], [5e-7, 5e-5, 5e-5], "AF447");
        // US Airways 1549: V_d 3.8, V 64 -> (0.8817, 0.1109, 0.0074)
        close(breakup_probabilities(3.8, 64.0).unwrap(), [0.8817, 0.1109, 0.0074], [5e-5, 5e-5, 5e-5], "US1549");
        // Swissair 111: V 154, 20 deg nose down -> V_d = 154 sin 20 = 52.67 -> (8.4e-6, 0.1568, 0.8432)
        close(breakup_probabilities(154.0 * 20f64.to_radians().sin(), 154.0).unwrap(), [8.4e-6, 0.1568, 0.8432], [5e-8, 5e-5, 5e-5], "SR111");
        // Refuses outside the domain rather than defaulting a family.
        assert!(breakup_probabilities(10.0, 0.0).is_none());
        assert!(breakup_probabilities(f64::NAN, 50.0).is_none());
        assert!(breakup_probabilities(60.0, 50.0).is_none(), "descent faster than total speed");
        // A level contact is floored, not refused.
        assert!(breakup_probabilities(0.0, 60.0).is_some());
    }

    /// Contract item 3: a hand-off already dry takes the no-thrust branch. Found failing on the
    /// full-scale 00:11 snapshot (9 Oct), where ~2/3 of dry-parent descents were labelled thrusting
    /// and given powered profiles. The propulsion state of an aircraft with no fuel is not a draw.
    #[test]
    fn a_dry_aircraft_takes_the_no_thrust_branch() {
        let m = module();
        let t = m.terminal().unwrap();
        let names = t.latent_columns();
        let at = |n: &str| names.iter().position(|x| x == n).unwrap();
        let fams = t.families();
        let dry = FlightState { fuel_kg: 0.0, mass_kg: ZFW_KG, realised_flameout_unix_s: EXHAUSTION - 120.0, ..handoff(EXHAUSTION) };
        let mut n = 0;
        for i in 0..40 {
            for d in t.descend(&dry, &atmos::Standard, &mut sweep(i as f64 * 0.023 + 0.05), &epochs(), &|_| 0.0) {
                assert_eq!(d.latents[at("engines_thrusting_at_onset")], 0.0, "a dry aircraft was labelled thrusting");
                let label = &fams[d.family];
                assert!(label.contains("none-thrusting"), "dry aircraft in family {label}");
                assert!(!label.starts_with("fuel-cue"), "fuel-cue response from empty tanks: {label}");
                n += 1;
            }
        }
        assert!(n > 100);
    }

    /// The realised flame-out must never be read as a prediction. Two hand-offs identical except
    /// that one has already run dry at a recorded time must predict the same exhaustion, because
    /// the prediction comes from `fuel_kg`.
    #[test]
    fn the_realised_flameout_does_not_drive_the_prediction() {
        let a = handoff(ONSET_22_41);
        let b = FlightState { realised_flameout_unix_s: EXHAUSTION - 7_200.0, ..handoff(ONSET_22_41) };
        let (pa, pb) = (predicted_exhaustion_of(&a), predicted_exhaustion_of(&b));
        assert!((pa - pb).abs() < 1e-6, "the realised flame-out moved the prediction: {pa} vs {pb}");
    }

    /// The module's own predicted exhaustion for a hand-off, read through its public surface
    /// rather than recomputed in the test. With the anticipatory support empty and all prior
    /// weight on the flame-out-associated mechanism, the drawn onset **is** the predicted
    /// exhaustion, for every draw.
    ///
    /// This exists because the earlier tests measured onset leads against a hard-coded
    /// `EXHAUSTION` of 00:17:30, which is the anchor the architecture removed: the test suite was
    /// carrying the same defect as `parent()`. The yardstick is now whatever the module derives
    /// from the handed-off fuel state.
    fn predicted_exhaustion_of(h: &FlightState) -> f64 {
        let mut v = params();
        let onset = v.as_table_mut().unwrap().get_mut("onset").unwrap().as_table_mut().unwrap();
        onset.insert(
            "anticipatory_lead_s".into(),
            toml::Value::Array(vec![toml::Value::Float(0.0), toml::Value::Float(0.0)]),
        );
        onset.insert(
            "mechanism_weights".into(),
            toml::Value::Array(vec![toml::Value::Float(0.0), toml::Value::Float(0.0), toml::Value::Float(1.0)]),
        );
        let h2 = new(&v).unwrap();
        let t = h2.terminal().unwrap();
        let (takeover, _) = t.takeover_time(h, &mut sweep(0.37));
        takeover
    }

    /// Cruise burn used to build the fixture's fuel load, kg/s. It is close to the reference
    /// run's 5,764 kg/h mean over the whole posterior, and
    /// `the_derived_cruise_burn_is_near_the_reference_run` pins the module's own derivation
    /// against that figure rather than against this constant.
    const CRUISE_BURN_KG_S: f64 = 5_764.0 / 3_600.0;

    /// Zero-fuel mass, kg. 174 t is the brief's calibration mass and about the 9M-MRO ZFW.
    const ZFW_KG: f64 = 174_000.0;

    fn handoff(unix_s: f64) -> FlightState {
        FlightState {
            unix_s,
            latitude_deg: -32.0,
            longitude_deg: 95.5,
            altitude_ft: 35_000.0,
            ground_velocity_east_mps: -20.0,
            ground_velocity_north_mps: -230.0,
            vertical_speed_mps: 0.0,
            mach: 0.81,
            true_air_speed_mps: 240.0,
            heading_deg: 186.0,
            wind_east_mps: -8.0,
            wind_north_mps: 4.0,
            mode: 2,
            // Core request 1 landed in f07e9f0, so the hand-off carries the fuel state and no
            // fallback should fire. The fuel load is the amount that runs the tanks dry at
            // `EXHAUSTION` under a reference cruise burn, so the fixture chooses a scenario with a
            // known exhaustion time and the module has to recover it from `fuel_kg` alone. A
            // later hand-off therefore carries less fuel and implies a shorter onset lead, which
            // is what gives the synthetic-recovery test its spread.
            mass_kg: ZFW_KG + (CRUISE_BURN_KG_S * (EXHAUSTION - unix_s)).max(0.0),
            fuel_kg: (CRUISE_BURN_KG_S * (EXHAUSTION - unix_s)).max(0.0),
            // Still holding fuel at the hand-off, like 43.14 % of the reference posterior. The
            // module must never read this to predict: it is an outcome, not a forecast.
            realised_flameout_unix_s: f64::NAN,
        }
    }

    /// A hand-off as the core sent it *before* request 1 landed: no fuel state at all. Used only
    /// by the test that checks the fallbacks still work and flag themselves.
    fn handoff_without_fuel_state(unix_s: f64) -> FlightState {
        FlightState { mass_kg: f64::NAN, fuel_kg: f64::NAN, ..handoff(unix_s) }
    }

    /// A deterministic uniform stream for the tests: splitmix64, seeded from the offset.
    ///
    /// An additive low-discrepancy recurrence was tried first and is **wrong** here: successive
    /// draws are then strongly correlated, and because `OnsetConfig::draw` consumes one uniform
    /// to choose the mechanism and the next to place the lead, the second draw could never land
    /// in the oversampled early window. The importance correction then had mean 1.10 rather than
    /// 1. A stream used to check a weighting rule must not have structure of its own.
    fn sweep(offset: f64) -> impl FnMut() -> f64 {
        let mut state = (offset * 1_000_003.0) as u64 ^ 0x9e37_79b9_7f4a_7c15;
        move || {
            state = state.wrapping_add(0x9e37_79b9_7f4a_7c15);
            let mut z = state;
            z = (z ^ (z >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
            z = (z ^ (z >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
            z ^= z >> 31;
            let u = (z >> 11) as f64 / (1u64 << 53) as f64;
            if u <= 0.0 {
                f64::MIN_POSITIVE
            } else {
                u
            }
        }
    }

    fn epochs() -> Vec<TerminalEpoch> {
        vec![TerminalEpoch { id: "m0019a".into(), unix_s: R600 }, TerminalEpoch { id: "m0019b".into(), unix_s: R1200 }]
    }

    /// The `run.toml` parameter block parses, every validation path rejects what it should, and
    /// the declarations are the ones the contract requires.
    #[test]
    fn the_module_constructs_and_declares_what_it_should() {
        let m = module();
        assert!(m.terminal().is_some());
        // No observation is consumed in this increment: the runner scores the 00:19 bursts.
        assert!(m.observations().is_empty());
        // The deferred hooks are present as named prediction columns and always NaN.
        assert_eq!(m.prediction_columns(), vec!["debris_class".to_string()]);
        assert!(!m.terminal().unwrap().latent_columns().iter().any(|n| n == "sinks_not_floats"), "sinks_not_floats is retired");
        let mut out = [0.0];
        let latents: Vec<f64> = Vec::new();
        let view = ImpactView {
            parent: 0,
            unix_s: EXHAUSTION,
            latitude_deg: -35.0,
            longitude_deg: 93.0,
            velocity_east_mps: 0.0,
            velocity_north_mps: -100.0,
            velocity_up_mps: -60.0,
            flight_path_angle_deg: 30.0,
            mass_kg: 174_000.0,
            kinetic_energy_j: 0.0,
            vertical_kinetic_energy_j: 0.0,
            family: 0,
            takeover_unix_s: ONSET_22_41,
            takeover_latitude_deg: -32.0,
            takeover_longitude_deg: 95.5,
            takeover_altitude_ft: 35_000.0,
            mode: 2,
            alternative: 0,
            latents: &latents,
        };
        m.predict(&view, &mut out);
        assert!(out[0].is_nan(), "with no latents supplied the breakup family is not computed, not zero: {out:?}");
        // With the module's own latents it reads the drawn family back - the same draw, never redrawn.
        let mut full = vec![f64::NAN; LATENTS.len()];
        let k = LATENTS.iter().position(|n| *n == "debris_class").unwrap();
        full[k] = 2.0;
        let with = ImpactView { latents: &full, ..view };
        m.predict(&with, &mut out);
        assert_eq!(out[0], 2.0, "predict must return the drawn debris_class unchanged");
        // The impact hook returns no likelihood in this increment.
        assert_eq!(m.impact_log_likelihood(&view, &[]), 0.0);

        let t = m.terminal().unwrap();
        assert_eq!(t.families().len(), 24);
        assert_eq!(t.latent_columns().len(), LATENTS.len());
        for name in t.latent_columns() {
            assert!(!name.contains(',') && !name.contains('/') && !name.contains(':') && !name.contains('\n'), "{name}");
        }
        // Validation.
        let bad = |edit: &str| {
            let mut v = params();
            let patch: toml::Value = toml::from_str(edit).unwrap();
            if let (Some(table), Some(p)) = (v.as_table_mut(), patch.as_table()) {
                for (k, val) in p {
                    table.insert(k.clone(), val.clone());
                }
            }
            new(&v).is_err()
        };
        assert!(bad("step_s = 0.0"));
        assert!(bad("descents_per_child = 0"));
        assert!(bad("control_weights = [0.0, 0.0, 0.0, 0.0]"));
        assert!(bad("fallback_mass_kg = 10.0"));
        assert!(bad("unknown_key = 1"), "deny_unknown_fields must reject an unknown key");
    }

    /// The takeover time is the sampled descent onset, it never precedes the hand-off, and with
    /// the empty support it is the predicted exhaustion. This is the V1/V2 switch.
    #[test]
    fn the_takeover_time_is_the_sampled_onset_and_the_empty_support_gives_v1() {
        let m = module();
        let t = m.terminal().unwrap();
        let h = handoff(ONSET_22_41);
        // The onset window is measured against the exhaustion this module DERIVES for this
        // hand-off, not against a clock constant. The fixture's fuel load is set from a flat
        // reference burn while the module integrates the mass it loses, so the two differ by
        // minutes - and the point of the fix is that the module's own number is what governs.
        let exhaustion = predicted_exhaustion_of(&h);
        let mut early = 0;
        for i in 0..200 {
            let (takeover, q) = t.takeover_time(&h, &mut sweep(i as f64 * 0.013));
            assert!(takeover >= h.unix_s, "takeover before the hand-off: {takeover}");
            assert!(takeover <= exhaustion + 1e-6, "takeover after the predicted exhaustion: {takeover}");
            assert!(q.is_finite());
            if exhaustion - takeover > 2_880.0 {
                early += 1;
            }
        }
        assert!(early > 10, "the early window was barely sampled: {early} of 200");

        // V1: the empty support. One config key, not a different code path.
        let mut v = params();
        v.as_table_mut()
            .unwrap()
            .get_mut("onset")
            .unwrap()
            .as_table_mut()
            .unwrap()
            .insert("anticipatory_lead_s".into(), toml::Value::Array(vec![toml::Value::Float(0.0), toml::Value::Float(0.0)]));
        let v1 = new(&v).unwrap();
        let t1 = v1.terminal().unwrap();
        let exhaustion = predicted_exhaustion_of(&h);
        let mut leads = Vec::new();
        for i in 0..100 {
            let (takeover, _) = t1.takeover_time(&h, &mut sweep(i as f64 * 0.017));
            leads.push(exhaustion - takeover);
        }
        // Only the fuel-cue and flame-out mechanisms remain, so no lead exceeds the cue window's
        // widest reach of 4,200 s - 20 s = 4,180 s, and a good share are exactly zero.
        assert!(leads.iter().all(|l| *l <= 4_180.0 + 1e-6), "a lead survived the empty support: {:?}", leads.iter().cloned().fold(0.0, f64::max));
        assert!(leads.iter().filter(|l| l.abs() < 1e-9).count() > 20, "the flame-out mechanism was barely drawn");
    }

    /// `descend` returns usable descents: impacts at the sea surface, after the takeover, with
    /// finite positions and the full latent vector; and the states at the two 00:19 bursts are
    /// filled when the aircraft was still airborne and `None` when it was already down.
    #[test]
    fn descend_returns_well_formed_descents() {
        let m = module();
        let t = m.terminal().unwrap();
        let eps = epochs();
        let mut airborne_at_r600 = 0;
        let mut down_at_r600 = 0;
        let mut families = std::collections::BTreeSet::new();
        let mut shapes = std::collections::BTreeSet::new();
        for i in 0..40 {
            let mut u = sweep(i as f64 * 0.011);
            let (takeover_unix, _) = t.takeover_time(&handoff(ONSET_22_41), &mut u);
            let takeover = FlightState { unix_s: takeover_unix, ..handoff(takeover_unix) };
            let descents = t.descend(&takeover, &atmos::Standard, &mut sweep(i as f64 * 0.019), &eps, &|_| 0.0);
            assert_eq!(descents.len(), 4, "descents_per_child");
            for d in &descents {
                assert!(d.impact.unix_s >= takeover_unix - 1e-6, "impact before the takeover");
                assert!(d.impact.latitude_deg.is_finite() && d.impact.longitude_deg.is_finite());
                assert!(d.impact.velocity_up_mps.is_finite() && d.impact.velocity_up_mps < 0.0, "{}", d.impact.velocity_up_mps);
                assert!(d.impact.mass_kg.is_finite() && d.impact.mass_kg > 100_000.0);
                assert!(d.family < 24);
                assert_eq!(d.latents.len(), LATENTS.len());
                assert_eq!(d.at_epochs.len(), 2);
                assert!(d.log_q_correction.is_finite());
                // The impact is at the sea surface and south of the tropics, in the ocean the
                // 00:11 posterior lives in.
                assert!(d.impact.latitude_deg < -20.0 && d.impact.latitude_deg > -60.0, "{}", d.impact.latitude_deg);
                families.insert(d.family);
                shapes.insert(d.latents[11] as i64);
                match d.at_epochs[0] {
                    Some(s) => {
                        airborne_at_r600 += 1;
                        assert!(s.altitude_ft > -10.0 && s.altitude_ft < 50_000.0, "{}", s.altitude_ft);
                        assert!(s.velocity_up_mps.is_finite());
                    }
                    None => down_at_r600 += 1,
                }
            }
        }
        assert!(families.len() > 5, "only {} families reached: {families:?}", families.len());
        assert!(shapes.len() > 2, "only {} profile shapes reached: {shapes:?}", shapes.len());
        assert!(airborne_at_r600 > 0 && down_at_r600 > 0, "airborne {airborne_at_r600}, down {down_at_r600}");
    }

    /// The deferred-hook latents are present and NaN, and the extrapolation and assumption flags
    /// are recorded rather than lost: with the hand-off carrying NaN for the fuel state, every
    /// descent is flagged as using the assumed mass.
    #[test]
    fn the_deferred_hooks_and_the_provenance_flags_are_recorded() {
        let m = module();
        let t = m.terminal().unwrap();
        let names = t.latent_columns();
        let at = |name: &str| names.iter().position(|n| n == name).unwrap_or_else(|| panic!("no latent {name}"));
        let descents = t.descend(&handoff(EXHAUSTION - 1_800.0), &atmos::Standard, &mut sweep(0.3), &epochs(), &|_| 0.0);
        for d in &descents {
            let class = d.latents[at("debris_class")];
            assert!([0.0, 1.0, 2.0].contains(&class), "debris_class must be a drawn family index, got {class}");
            let p: f64 = ["breakup_p_intact", "breakup_p_broken", "breakup_p_fragmented"].iter().map(|n| d.latents[at(n)]).sum();
            assert!((p - 1.0).abs() < 1e-12, "breakup probabilities sum to {p}");
            // Architecture's acceptance rule: on a real hand-off no fallback may fire at all. The
            // fixture carries the fuel state request 1 delivered, so a flag here means the
            // hand-off is defective and that is the finding, not a number to use.
            assert_eq!(d.latents[at("mass_kg_assumed")], 0.0, "no mass fallback may fire on a real hand-off");
            assert_eq!(d.latents[at("fuel_kg_assumed")], 0.0, "no fuel fallback may fire on a real hand-off");
            // The energy-transfer columns are declared NaN hooks, not gaps: there is no
            // water-entry model, and `impact_tau_method` says so mechanically.
            for name in [
                "impact_energy_transferred_j",
                "energy_transfer_t05_s",
                "energy_transfer_t95_s",
                "energy_transfer_tau90_s",
                "energy_transfer_peak_rate_w",
                "energy_transfer_n_pulses",
            ] {
                assert!(d.latents[at(name)].is_nan(), "{name} must be NaN until a water-entry model exists");
            }
            assert_eq!(d.latents[at("impact_tau_method")], TAU_METHOD_NOT_COMPUTED);
            // The burn-gap diagnostic is a duration, never negative and never NaN; the fixture has
            // not run dry, so it must be exactly zero here.
            assert_eq!(d.latents[at("powered_after_core_exhaustion_s")], 0.0);
            assert!(d.latents[at("takeover_ground_velocity_east_mps")].is_finite());
            assert!(d.latents[at("takeover_ground_velocity_north_mps")].is_finite());
            // Attitude at contact is reported, and is a real outcome of the dynamics.
            let heading = d.latents[at("impact_heading_deg")];
            assert!((0.0..360.0).contains(&heading), "impact heading {heading}");
            assert!(d.latents[at("impact_bank_deg")].abs() <= 90.0, "impact bank {}", d.latents[at("impact_bank_deg")]);
            assert!(d.latents[at("time_extrapolated_s")].is_finite());
            assert!(d.latents[at("family_prior")] >= 0.0 && d.latents[at("family_prior")] <= 1.0);
            assert!(d.latents[at("time_descending_s")] >= 0.0);
            // The realised flame-out is recorded and is not the predicted one by construction
            // unless the branch is flame-out-associated.
            assert!(d.latents[at("realised_flameout_unix_s")].is_nan() || d.latents[at("realised_flameout_unix_s")].is_finite());
        }
    }

    /// An hour between onset and impact need not be an hour descending: over an ensemble started
    /// 3,600 s before the predicted exhaustion, some descents spend well under half the elapsed
    /// time with a descent rate steeper than 100 ft/min.
    #[test]
    fn an_hour_to_impact_need_not_be_an_hour_descending() {
        let m = module();
        let t = m.terminal().unwrap();
        let start = EXHAUSTION - 3_600.0;
        let mut best = 1.0f64;
        for i in 0..30 {
            for d in t.descend(&handoff(start), &atmos::Standard, &mut sweep(i as f64 * 0.023), &epochs(), &|_| 0.0) {
                let elapsed = d.impact.unix_s - start;
                if elapsed > 600.0 {
                    best = best.min(d.latents[13] / elapsed);
                }
            }
        }
        assert!(best < 0.6, "every descent spent at least {:.0}% of its flight descending", best * 100.0);
    }

    // ---------------------------------------------------------------------------------------
    // §11: the BFO vertical-speed sensitivity, against a finite difference.
    //
    // The measurement model lives in `crates/satcom` and is NOT reimplemented here: the contract
    // forbids it and the runner does the scoring. What follows is a test-only geometry fixture,
    // reachable from no run, whose only job is to check the derivative of the BFO with respect to
    // the geometric vertical speed. A hypothesis may not depend on `satcom`, so the two constants
    // and the satellite states are repeated as fixtures with their provenance.
    // ---------------------------------------------------------------------------------------

    /// Inmarsat Classic Aero L-band uplink, Hz, and the speed of light, km/s. Fixtures copied
    /// from `crates/satcom/src/lib.rs` (`UPLINK_HZ`, `SPEED_OF_LIGHT_KM_S`).
    const UPLINK_HZ: f64 = 1_646_652_500.0;
    const C_KM_S: f64 = 299_792.458;

    /// Inmarsat-3F1 ECEF state at an epoch, km and km/s, from `data/satellite-ephemeris.csv`.
    struct Sat {
        position: geo::Vec3,
        velocity: geo::Vec3,
    }

    /// m0011: 2014-03-08T00:10:59Z.
    fn sat_0011() -> Sat {
        Sat {
            position: geo::Vec3::new(18_181.158_95, 38_050.482_29, 434.568_805),
            velocity: geo::Vec3::new(0.001_675, -0.001_573, -0.082_087),
        }
    }

    /// m0019a: 2014-03-08T00:19:29Z, the 7th arc.
    fn sat_0019a() -> Sat {
        Sat {
            position: geo::Vec3::new(18_182.020_38, 38_049.649_62, 392.417_794),
            velocity: geo::Vec3::new(0.001_584, -0.001_634, -0.083_208),
        }
    }

    /// The aircraft-dependent part of the BFO: the uplink Doppler of the aircraft's own motion
    /// plus its Doppler pre-compensation, which uses the horizontal velocity only. The satellite,
    /// downlink and AFC terms are constants in the vertical speed and are omitted, so this is a
    /// *difference* function for the derivative test, not a BFO predictor.
    fn bfo_aircraft_terms_hz(sat: &Sat, lat: f64, lon: f64, alt_ft: f64, v_north_mps: f64, v_east_mps: f64, v_up_mps: f64) -> f64 {
        let (north, east, up) = geo::local_basis(lat, lon);
        let horizontal = north * (v_north_mps / 1_000.0) + east * (v_east_mps / 1_000.0);
        let velocity = horizontal + up * (v_up_mps / 1_000.0);
        let aircraft = geo::lla_to_ecef(lat, lon, alt_ft * geo::KM_PER_FT);
        let to_satellite = (sat.position - aircraft).unit();
        let uplink = -UPLINK_HZ / C_KM_S * (sat.velocity - velocity).dot(to_satellite);
        let nominal = geo::lla_to_ecef(0.0, 64.5, 36_210.12);
        let from_nominal = (geo::lla_to_ecef(lat, lon, 0.0) - nominal).unit();
        let compensation = UPLINK_HZ / C_KM_S * horizontal.dot(from_nominal);
        uplink + compensation
    }

    /// The closed-form sensitivity: `(f_up / c) (u_up . u_aircraft->satellite)`, in Hz per m/s.
    fn bfo_sensitivity_hz_per_mps(sat: &Sat, lat: f64, lon: f64, alt_ft: f64) -> f64 {
        let (_, _, up) = geo::local_basis(lat, lon);
        let aircraft = geo::lla_to_ecef(lat, lon, alt_ft * geo::KM_PER_FT);
        let to_satellite = (sat.position - aircraft).unit();
        UPLINK_HZ / C_KM_S * up.dot(to_satellite) / 1_000.0
    }

    /// §11 test 5 — the BFO vertical-speed sensitivity, analytic against a central finite
    /// difference, at both relevant geometries.
    ///
    /// **A correction to the brief.** §7 of the master prompt records 17.50 Hz per 1,000 ft/min
    /// "at the 00:11 geometry". Computed from the engine's own satellite ephemeris, 17.50 is
    /// consistent with the **7th-arc (00:19a, BTO 18,400 us) geometry**, which gives 17.52, and
    /// inconsistent with the 00:11 arc (BTO 18,040 us), which gives 17.81 — 1.8% away. The BTO
    /// fixes the slant range and so the elevation angle, so the value is nearly constant along
    /// each arc (17.80 to 17.81 from 30S to 40S on the 00:11 arc) and differs between arcs. The
    /// §7 argument is unaffected in substance — a +-20 Hz bias excursion still matches
    /// 1,123 ft/min at 00:11 rather than 1,143 — but the attribution should be corrected before
    /// it reaches the paper.
    #[test]
    fn the_bfo_vertical_speed_sensitivity_matches_a_finite_difference() {
        let fpm_1000 = 1_000.0 * atmos::M_PER_FT / 60.0; // 5.08 m/s
        for (name, sat, lat, lon, expected_per_1000fpm) in [
            ("00:11 arc", sat_0011(), -35.0, 91.546_0, 17.81),
            ("00:19a arc (7th arc)", sat_0019a(), -35.0, 92.875_2, 17.52),
        ] {
            let alt = 35_000.0;
            let analytic = bfo_sensitivity_hz_per_mps(&sat, lat, lon, alt);
            let h = 1e-4;
            let plus = bfo_aircraft_terms_hz(&sat, lat, lon, alt, -230.0, -20.0, h);
            let minus = bfo_aircraft_terms_hz(&sat, lat, lon, alt, -230.0, -20.0, -h);
            let numerical = (plus - minus) / (2.0 * h);
            assert!(
                (analytic - numerical).abs() / analytic.abs() < 1e-6,
                "{name}: analytic {analytic} Hz per m/s, finite difference {numerical}"
            );
            let per_1000fpm = analytic * fpm_1000;
            assert!((per_1000fpm - expected_per_1000fpm).abs() < 0.02, "{name}: {per_1000fpm} Hz per 1,000 ft/min");
            // The horizontal terms do not leak into the vertical derivative.
            let other = bfo_aircraft_terms_hz(&sat, lat, lon, alt, 100.0, 50.0, h) - bfo_aircraft_terms_hz(&sat, lat, lon, alt, 100.0, 50.0, -h);
            assert!((other / (2.0 * h) - numerical).abs() / analytic.abs() < 1e-9, "{name}: the derivative depends on the horizontal velocity");
        }
        // The two geometries differ by 1.7%, which is the correction above.
        let a = bfo_sensitivity_hz_per_mps(&sat_0011(), -35.0, 91.546_0, 35_000.0);
        let b = bfo_sensitivity_hz_per_mps(&sat_0019a(), -35.0, 92.875_2, 35_000.0);
        assert!((a / b - 1.0) > 0.01 && (a / b - 1.0) < 0.025, "ratio {}", a / b);
        // And a +-20 Hz excursion is the descent rate §7 quotes, at each geometry.
        assert!((20.0 / (a * fpm_1000) * 1_000.0 - 1_123.0).abs() < 5.0);
        assert!((20.0 / (b * fpm_1000) * 1_000.0 - 1_143.0).abs() < 5.0);
    }

    // ---------------------------------------------------------------------------------------
    // §11 / composition rule 8: one synthetic-recovery test.
    // ---------------------------------------------------------------------------------------

    /// Generate the data from a **known** descent, then recover the onset lead from the module's
    /// own proposal by importance sampling, and check that the 90% credible interval covers the
    /// truth and that the posterior is sharper than the prior.
    ///
    /// The observation model here — a Gaussian on the impact position with a declared 15 km
    /// standard deviation — is a **test fixture**, not a likelihood this module returns. The
    /// module returns no likelihood; the runner scores the SATCOM bursts with the core
    /// measurement model. The point of the test is that the proposal can recover a latent it
    /// generated, which is what composition rule 8 asks for.
    #[test]
    fn a_synthetic_descent_recovers_its_own_onset_lead() {
        let m = module();
        let t = m.terminal().unwrap();
        let eps = epochs();
        let truth_lead = 2_400.0;
        let truth_takeover = EXHAUSTION - truth_lead;

        // The known descent: one draw of the proposal at a fixed stream offset.
        let truth = t.descend(&handoff(truth_takeover), &atmos::Standard, &mut sweep(0.4242), &eps, &|_| 0.0).remove(0);
        let (truth_lat, truth_lon) = (truth.impact.latitude_deg, truth.impact.longitude_deg);
        assert!(truth_lat.is_finite() && truth_lon.is_finite());

        // Importance sampling over the onset lead with the module's own proposal.
        let sd_km = 15.0;
        let mut samples: Vec<(f64, f64)> = Vec::new(); // (lead, weight)
        for i in 0..260 {
            let mut u = sweep(i as f64 * 0.00731 + 0.07);
            let (takeover_unix, log_q) = t.takeover_time(&handoff(ONSET_22_41), &mut u);
            let state = handoff(takeover_unix);
            let lead = predicted_exhaustion_of(&state) - takeover_unix;
            for d in t.descend(&state, &atmos::Standard, &mut sweep(i as f64 * 0.01117 + 0.31), &eps, &|_| 0.0) {
                let dlat = (d.impact.latitude_deg - truth_lat) * 111.32;
                let dlon = (d.impact.longitude_deg - truth_lon) * 111.32 * truth_lat.to_radians().cos();
                let r2 = dlat * dlat + dlon * dlon;
                let log_w = log_q + d.log_q_correction - 0.5 * r2 / (sd_km * sd_km);
                samples.push((lead, log_w));
            }
        }
        assert!(samples.len() > 500, "{} samples", samples.len());

        let max = samples.iter().map(|(_, w)| *w).fold(f64::NEG_INFINITY, f64::max);
        assert!(max.is_finite(), "every weight was zero: the proposal never covered the truth");
        let mut weighted: Vec<(f64, f64)> = samples.iter().map(|(l, w)| (*l, (w - max).exp())).collect();
        let total: f64 = weighted.iter().map(|(_, w)| *w).sum();
        let ess = total * total / weighted.iter().map(|(_, w)| w * w).sum::<f64>();
        weighted.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());

        let quantile = |p: f64| {
            let target = p * total;
            let mut acc = 0.0;
            for (lead, w) in &weighted {
                acc += *w;
                if acc >= target {
                    return *lead;
                }
            }
            weighted.last().unwrap().0
        };
        let (lo, hi) = (quantile(0.05), quantile(0.95));
        assert!(lo <= truth_lead && truth_lead <= hi, "the 90% interval [{lo}, {hi}] s misses the truth {truth_lead} s (ESS {ess:.1})");
        // And it is informative: narrower than the 5,760 s prior support.
        assert!(hi - lo < 5_760.0, "the interval [{lo}, {hi}] is no narrower than the prior");
        // Report the Monte Carlo adequacy rather than hide it: this is a test-scale ensemble, so
        // the ESS is small by construction and the test asserts only that it is usable.
        assert!(ess > 3.0, "ESS {ess:.2} is too small for the interval to mean anything");
    }

    /// The runner's own self-check: the mean of `exp(log_q_correction)` over a child's descents
    /// should be one. Here the takeover correction carries the defensive onset proposal and the
    /// descent correction is zero, so the product's mean is checked over the takeover draws.
    #[test]
    fn the_proposal_corrections_average_one() {
        let m = module();
        let t = m.terminal().unwrap();
        let h = handoff(ONSET_22_41);
        let n = 4_000;
        let mut mean = 0.0;
        for i in 0..n {
            let (_, q) = t.takeover_time(&h, &mut sweep(i as f64 / n as f64));
            mean += q.exp() / n as f64;
        }
        assert!((mean - 1.0).abs() < 0.03, "mean correction {mean}");
    }

    /// The module reads the runner's atmosphere rather than assuming ISA: a warm anomaly changes
    /// the density and so the impact.
    #[test]
    fn the_descent_responds_to_the_supplied_atmosphere() {
        struct Warm;
        impl Atmosphere for Warm {
            fn at(&self, _: f64, altitude_ft: f64, _: f64, _: f64) -> Air {
                Air {
                    temperature_k: atmos::isa_temperature_k(altitude_ft) + 15.0,
                    pressure_pa: geo::isa_pressure_pa(altitude_ft),
                    wind_east_mps: 0.0,
                    wind_north_mps: 0.0,
                    declination_deg: 0.0,
                    surface_pressure_altitude_ft: 0.0,
                    clamped: false,
                }
            }
        }
        let m = module();
        let t = m.terminal().unwrap();
        let state = handoff(EXHAUSTION - 1_200.0);
        let isa = t.descend(&state, &atmos::Standard, &mut sweep(0.77), &epochs(), &|_| 0.0).remove(0);
        let warm = t.descend(&state, &Warm, &mut sweep(0.77), &epochs(), &|_| 0.0).remove(0);
        let moved = (isa.impact.latitude_deg - warm.impact.latitude_deg).abs() + (isa.impact.longitude_deg - warm.impact.longitude_deg).abs();
        assert!(moved > 1e-6, "the atmosphere made no difference: {moved} deg");
    }

    /// Negative results are kept, not deleted: the timed-out flag is a latent, and the config
    /// flag that emits the unconverged state itself defaults off.
    #[test]
    fn unconverged_descents_are_recorded_and_the_flag_defaults_off() {
        let v = params();
        assert_eq!(v.get("emit_timed_out_descents").and_then(toml::Value::as_bool), Some(false));
        let m = module();
        let t = m.terminal().unwrap();
        let names = t.latent_columns();
        assert!(names.contains(&"timed_out".to_string()));
        // With a one-minute ceiling every descent from cruise altitude times out, and each is
        // still returned, with the flag set, rather than dropped.
        let mut short = params();
        short.as_table_mut().unwrap().insert("max_flight_s".into(), toml::Value::Float(60.0));
        let m2 = new(&short).unwrap();
        let t2 = m2.terminal().unwrap();
        let at = names.iter().position(|n| n == "timed_out").unwrap();
        let descents = t2.descend(&handoff(EXHAUSTION - 1_200.0), &atmos::Standard, &mut sweep(0.5), &epochs(), &|_| 0.0);
        assert_eq!(descents.len(), 4);
        assert!(descents.iter().all(|d| d.latents[at] == 1.0), "a timed-out descent was not flagged");
        // Finished on a glide by default, so the sample is still at the sea surface.
        assert!(descents.iter().all(|d| d.impact.latitude_deg.is_finite()));
    }
}
