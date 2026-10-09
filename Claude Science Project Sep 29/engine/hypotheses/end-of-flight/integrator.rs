//! The point-mass descent integrator: three degrees of freedom in the air-relative frame, with
//! the wind added to get the ground track.
//!
//! ## Equations
//!
//! State is `(V, gamma, h_p, psi, lat, lon, m)` — true airspeed, air-relative flight-path angle
//! (positive climbing), pressure altitude, true air heading, position and mass:
//!
//! ```text
//!   m dV/dt     = T - D - m g sin(gamma)
//!   m V dgamma/dt = L cos(phi) - m g cos(gamma)
//!   dh_geom/dt  = V sin(gamma)                   dh_p/dt = (T_ISA/T) dh_geom/dt
//!   dpsi/dt     = L sin(phi) / (m V cos(gamma))
//!   dm/dt       = -(fuel flow)
//! ```
//!
//! with `L = c_l q S`, `D = c_d q S`, `q = gamma_air/2 p M^2`, and the ground velocity the air
//! velocity plus the runner's wind. Advanced with classical RK4 on `(V, gamma, h_geom, psi)`;
//! position is advanced with `geo::advance` on the mean ground velocity of the step, which uses
//! the WGS-84 radii of curvature, so the geometry is the same one the core filter uses.
//!
//! ## Step size
//!
//! `dt` is a **parameter**, not a constant, and is not tied to the core filter's 5 s manoeuvre
//! step: a flame-out transition and a high-speed upset both need a far finer step than cruise.
//! [`Integrator::step_for`] returns the fine step inside a window around a named transition time
//! and the base step elsewhere, so a single descent can run coarse in a steady glide and fine
//! through the seconds that matter. The ballistic energy-conservation test uses the step
//! refinement to show fourth-order behaviour.
//!
//! ## Terminating at the sea surface
//!
//! The descent ends when the pressure altitude crosses `Air::surface_pressure_altitude_ft` (the
//! local sea surface in pressure-altitude terms, which the runner takes from ERA5 mean-sea-level
//! pressure where it has it). The crossing is found by linear interpolation within the final
//! step and the impact state is reported there, so the impact is not quantised to the step.

use hypothesis::{Air, Atmosphere};

use super::aero::{Aero, Configuration};
use super::atmos;

#[cfg(test)]
use super::aero::tests::reference;

/// What the pilot or the trim is doing during a step.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Command {
    /// Free dynamics at a fixed trimmed lift coefficient and bank angle: what "no effective
    /// intervention" means. Produces the phugoid at small bank and the descending spiral at
    /// larger bank, from the same equations.
    FixedTrim { c_l: f64, bank_rad: f64 },
    /// Hold a target geometric vertical speed and a target Mach, within the achievable envelope.
    /// Lift is set to the value that curves the flight path onto the target angle; thrust is set
    /// to the value that holds the target Mach, saturating between idle and the full rating.
    Track { vertical_speed_mps: f64, target_mach: f64, bank_rad: f64 },
    /// Hold the best lift-to-drag ratio of the current configuration: the reference glide.
    BestGlide { bank_rad: f64 },
    /// No lift, no drag, no thrust. Only for the ballistic energy-conservation test.
    #[cfg_attr(not(test), allow(dead_code))]
    Ballistic,
}

/// One body state.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Body {
    pub unix_s: f64,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub pressure_altitude_ft: f64,
    pub tas_mps: f64,
    /// Air-relative flight-path angle, radians, positive climbing.
    pub gamma_rad: f64,
    /// True air heading, radians.
    pub heading_rad: f64,
    pub mass_kg: f64,
    pub fuel_kg: f64,
}

impl Body {
    /// Geometric rate of climb, m/s — what the BFO responds to.
    pub fn vertical_speed_mps(&self) -> f64 {
        self.tas_mps * self.gamma_rad.sin()
    }

    /// Specific energy height, m: `V^2/(2g) + h`. Conserved by the ballistic command.
    #[cfg_attr(not(test), allow(dead_code))] // model surface exercised by this module's tests
    pub fn energy_height_m(&self, temperature_k: f64) -> f64 {
        let h = self.pressure_altitude_ft * atmos::M_PER_FT * atmos::geometric_rate_factor(self.pressure_altitude_ft, temperature_k);
        self.tas_mps * self.tas_mps / (2.0 * atmos::G0) + h
    }
}

/// Derivatives of the integrated quantities.
#[derive(Debug, Clone, Copy)]
struct Rates {
    d_tas: f64,
    d_gamma: f64,
    /// Geometric, m/s.
    d_altitude: f64,
    d_heading: f64,
    d_mass: f64,
    /// Diagnostic of the step, not integrated.
    mach: f64,
    /// Bank commanded over the step, rad. Diagnostic, not integrated: it is carried so that the
    /// attitude at the surface crossing can be reported without re-entering the control law.
    bank_rad: f64,
    /// How the step's burn was priced, `FUEL_*` bits. Diagnostic, not integrated.
    fuel_status: u8,
}

/// Bits of `Rates::fuel_status`: how the burn over a step was priced.
const FUEL_UNPRICED: u8 = 1;
const FUEL_BELOW_TABLES: u8 = 2;
const FUEL_EXTRAPOLATED: u8 = 4;
const FUEL_ABOVE_CEILING: u8 = 8;

/// The integrator: aerodynamic model plus step policy.
#[derive(Clone, Copy)]
pub struct Integrator<'a> {
    pub aero: Aero,
    /// The core's fuel-flow model (core request 3): the cruise tables times this trajectory's own
    /// fuel-flow factor, the same model that burnt the fuel up to the takeover. `None` prices
    /// powered flight with the module's own swept TSFC, which only the unit tests should use.
    ///
    /// The tables are two-engine cruise schedules at normal thrust, not idle and not one engine
    /// inoperative. The burn at any other thrust is DERIVED: the effective specific consumption at
    /// this flight level, gross weight and Mach is the table flow divided by the module's own
    /// level-flight drag there (clean, both engines), and the flow is thrust times that. In level
    /// cruise this returns the table flow exactly; elsewhere it scales with thrust. It UNDERSTATES
    /// idle flow, because real specific consumption rises at idle, and it treats one engine at a
    /// given thrust like two engines sharing that thrust. Both are declared modelling choices.
    pub fuel: Option<&'a dyn hypothesis::FuelFlow>,
    /// Base step, s. A parameter.
    pub step_s: f64,
    /// Fine step through a transition, s. A parameter.
    pub fine_step_s: f64,
    /// Half-width of the fine-step window around a transition, s.
    pub fine_window_s: f64,
    /// Hard ceiling on integrated flight time, s, so a phugoid that never descends terminates.
    pub max_flight_s: f64,
}

impl std::fmt::Debug for Integrator<'_> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("Integrator")
            .field("step_s", &self.step_s)
            .field("fine_step_s", &self.fine_step_s)
            .field("fine_window_s", &self.fine_window_s)
            .field("max_flight_s", &self.max_flight_s)
            .field("fuel", &self.fuel.is_some())
            .finish()
    }
}

/// What one descent integration produced.
#[derive(Debug, Clone, PartialEq)]
pub struct Trace {
    pub impact: Body,
    /// Air-relative vertical speed at impact, m/s (negative descending).
    pub impact_vertical_speed_mps: f64,
    /// Bank at the surface crossing, rad. Attitude at contact is ruled into the interface and is
    /// reported as the `impact_bank_deg` latent; heading comes from `impact.heading_rad`.
    pub impact_bank_rad: f64,
    /// Ground velocity at impact, m/s.
    pub impact_velocity_east_mps: f64,
    pub impact_velocity_north_mps: f64,
    /// Seconds spent with a descent rate steeper than 100 ft/min.
    pub time_descending_s: f64,
    /// Steepest descent rate reached, ft/min (positive down).
    pub max_descent_rate_fpm: f64,
    /// Seconds spent above the crest Mach, where the model is extrapolated.
    pub time_extrapolated_s: f64,
    /// Highest Mach reached.
    pub max_mach: f64,
    /// Lowest pressure altitude reached before impact, ft — a phugoid can climb afterwards.
    pub min_altitude_ft: f64,
    /// Highest pressure altitude reached, ft. A phugoid that climbs above the weather grid is
    /// recorded rather than silently clamped: the runner's `Air::clamped` flag is also carried.
    pub max_altitude_ft: f64,
    /// True if any atmosphere query was outside the grid.
    pub clamped: bool,
    /// True if the integration hit `max_flight_s` without reaching the surface.
    pub timed_out: bool,
    /// Seconds of powered flight the core's fuel model could not price, burnt at the module's own
    /// TSFC instead (core request 3: `None` is never zero flow).
    pub fuel_unpriced_s: f64,
    /// Seconds priced below FL060 (at FL060: the real flow is higher) and on an extrapolated
    /// schedule (good to about 12% against Boeing), as the core asks them carried.
    pub fuel_below_tables_s: f64,
    pub fuel_extrapolated_s: f64,
    /// Sea-surface pressure altitude at the surface crossing, ft, as the atmosphere gave it.
    pub surface_pressure_altitude_ft: f64,
    pub steps: usize,
}

impl<'a> Integrator<'a> {
    /// The step to use at `t`, given a transition at `transition_unix_s` (for example the
    /// flame-out). The core filter's 5 s manoeuvre step does not constrain this.
    pub fn step_for(&self, t: f64, transition_unix_s: Option<f64>) -> f64 {
        match transition_unix_s {
            Some(tr) if (t - tr).abs() <= self.fine_window_s => self.fine_step_s,
            _ => self.step_s,
        }
    }

    /// Integrate from `start` until the surface, `max_flight_s` or a caller-supplied stop.
    ///
    /// `command(body, elapsed_s) -> (Command, Configuration, f64)` is the control law: it returns
    /// what to fly, the configuration to fly it in, and the thrust setting. Returning the
    /// configuration each step is what lets propulsion be an evolving state — an engine failing
    /// mid-descent is a changed `Configuration`, not a new family.
    ///
    /// `sample(body)` is called at every step boundary with the integrated state, so a caller can
    /// record the state at a SATCOM burst time without the integrator knowing about bursts.
    pub fn run(
        &self,
        start: Body,
        atmosphere: &dyn Atmosphere,
        transition_unix_s: Option<f64>,
        command: &mut dyn FnMut(&Body, f64) -> (Command, Configuration, f64),
        sample: &mut dyn FnMut(&Body, &Air),
    ) -> Trace {
        let mut body = start;
        let mut trace = Trace {
            impact: body,
            impact_vertical_speed_mps: f64::NAN,
            impact_bank_rad: f64::NAN,
            impact_velocity_east_mps: f64::NAN,
            impact_velocity_north_mps: f64::NAN,
            time_descending_s: 0.0,
            max_descent_rate_fpm: 0.0,
            time_extrapolated_s: 0.0,
            max_mach: 0.0,
            min_altitude_ft: body.pressure_altitude_ft,
            max_altitude_ft: body.pressure_altitude_ft,
            clamped: false,
            timed_out: false,
            fuel_unpriced_s: 0.0,
            fuel_below_tables_s: 0.0,
            fuel_extrapolated_s: 0.0,
            surface_pressure_altitude_ft: f64::NAN,
            steps: 0,
        };
        let t0 = body.unix_s;
        loop {
            let air = atmosphere.at(body.unix_s, body.pressure_altitude_ft, body.latitude_deg, body.longitude_deg);
            trace.clamped |= air.clamped;
            sample(&body, &air);
            if body.pressure_altitude_ft <= air.surface_pressure_altitude_ft {
                break;
            }
            if body.unix_s - t0 >= self.max_flight_s || trace.steps > 4_000_000 {
                trace.timed_out = true;
                break;
            }
            let dt = self.step_for(body.unix_s, transition_unix_s).max(1e-4);
            let (cmd, cfg, setting) = command(&body, body.unix_s - t0);
            let next = self.advance(&body, atmosphere, &cmd, &cfg, setting, dt);

            // Diagnostics over the step.
            let rates = self.rates(&body, &air, &cmd, &cfg, setting);
            let descent_fpm = -rates.d_altitude * atmos::FPM_PER_MPS;
            if descent_fpm > 100.0 {
                trace.time_descending_s += dt;
            }
            trace.max_descent_rate_fpm = trace.max_descent_rate_fpm.max(descent_fpm);
            trace.max_mach = trace.max_mach.max(rates.mach);
            trace.impact_bank_rad = rates.bank_rad;
            if rates.fuel_status & FUEL_UNPRICED != 0 {
                trace.fuel_unpriced_s += dt;
            }
            if rates.fuel_status & FUEL_BELOW_TABLES != 0 {
                trace.fuel_below_tables_s += dt;
            }
            if rates.fuel_status & FUEL_EXTRAPOLATED != 0 {
                trace.fuel_extrapolated_s += dt;
            }
            if self.aero.is_extrapolated(rates.mach) {
                trace.time_extrapolated_s += dt;
            }
            trace.min_altitude_ft = trace.min_altitude_ft.min(next.pressure_altitude_ft);
            trace.max_altitude_ft = trace.max_altitude_ft.max(next.pressure_altitude_ft);
            trace.steps += 1;

            // Surface crossing inside this step: solve for the crossing rather than quantise to
            // the step. The first guess is linear in altitude; because RK4 is nonlinear in dt,
            // the guess is then bracketed and bisected to a tolerance of 1e-3 ft, which converges
            // well inside the 40-iteration cap even from a 30 s step.
            if next.pressure_altitude_ft <= air.surface_pressure_altitude_ft && body.pressure_altitude_ft > air.surface_pressure_altitude_ft {
                let surface = air.surface_pressure_altitude_ft;
                let span = body.pressure_altitude_ft - next.pressure_altitude_ft;
                let mut lo = 0.0;
                let mut hi = dt;
                let mut partial = next;
                let mut guess = if span > 0.0 { dt * ((body.pressure_altitude_ft - surface) / span).clamp(0.0, 1.0) } else { dt };
                for _ in 0..40 {
                    partial = self.advance(&body, atmosphere, &cmd, &cfg, setting, guess);
                    let residual = partial.pressure_altitude_ft - surface;
                    if residual.abs() < 1e-3 {
                        break;
                    }
                    if residual > 0.0 {
                        lo = guess;
                    } else {
                        hi = guess;
                    }
                    guess = 0.5 * (lo + hi);
                }
                body = partial;
                break;
            }
            body = next;
        }
        let air = atmosphere.at(body.unix_s, body.pressure_altitude_ft, body.latitude_deg, body.longitude_deg);
        trace.impact = body;
        trace.surface_pressure_altitude_ft = air.surface_pressure_altitude_ft;
        let factor = atmos::geometric_rate_factor(body.pressure_altitude_ft, air.temperature_k);
        trace.impact_vertical_speed_mps = body.vertical_speed_mps() * factor;
        let horizontal = body.tas_mps * body.gamma_rad.cos();
        trace.impact_velocity_east_mps = horizontal * body.heading_rad.sin() + air.wind_east_mps;
        trace.impact_velocity_north_mps = horizontal * body.heading_rad.cos() + air.wind_north_mps;
        trace
    }

    /// One RK4 step.
    fn advance(
        &self,
        body: &Body,
        atmosphere: &dyn Atmosphere,
        cmd: &Command,
        cfg: &Configuration,
        setting: f64,
        dt: f64,
    ) -> Body {
        // RK4 on (V, gamma, h_geom, psi, m). Altitude is integrated geometrically and converted
        // back to pressure altitude once, at the end of the step.
        let factor = {
            let air = atmosphere.at(body.unix_s, body.pressure_altitude_ft, body.latitude_deg, body.longitude_deg);
            atmos::geometric_rate_factor(body.pressure_altitude_ft, air.temperature_k)
        };
        let shift = |b: &Body, r: &Rates, h: f64| Body {
            unix_s: b.unix_s + h,
            tas_mps: (b.tas_mps + h * r.d_tas).max(1.0),
            gamma_rad: b.gamma_rad + h * r.d_gamma,
            pressure_altitude_ft: b.pressure_altitude_ft + h * r.d_altitude / (factor * atmos::M_PER_FT),
            heading_rad: b.heading_rad + h * r.d_heading,
            mass_kg: b.mass_kg + h * r.d_mass,
            fuel_kg: b.fuel_kg + h * r.d_mass,
            ..*b
        };
        let at = |b: &Body| {
            let air = atmosphere.at(b.unix_s, b.pressure_altitude_ft, b.latitude_deg, b.longitude_deg);
            self.rates(b, &air, cmd, cfg, setting)
        };
        let k1 = at(body);
        let b2 = shift(body, &k1, dt / 2.0);
        let k2 = at(&b2);
        let b3 = shift(body, &k2, dt / 2.0);
        let k3 = at(&b3);
        let b4 = shift(body, &k3, dt);
        let k4 = at(&b4);
        let combine = |f: fn(&Rates) -> f64| (f(&k1) + 2.0 * f(&k2) + 2.0 * f(&k3) + f(&k4)) / 6.0;
        let d_tas = combine(|r| r.d_tas);
        let d_gamma = combine(|r| r.d_gamma);
        let d_altitude = combine(|r| r.d_altitude);
        let d_heading = combine(|r| r.d_heading);
        let d_mass = combine(|r| r.d_mass);

        let mut out = Body {
            unix_s: body.unix_s + dt,
            tas_mps: (body.tas_mps + dt * d_tas).max(1.0),
            gamma_rad: body.gamma_rad + dt * d_gamma,
            pressure_altitude_ft: body.pressure_altitude_ft + dt * d_altitude / (factor * atmos::M_PER_FT),
            heading_rad: body.heading_rad + dt * d_heading,
            mass_kg: body.mass_kg + dt * d_mass,
            fuel_kg: (body.fuel_kg + dt * d_mass).max(0.0),
            ..*body
        };
        // Position on the mean ground velocity of the step, in knots, through the core's geometry.
        let air = atmosphere.at(body.unix_s, body.pressure_altitude_ft, body.latitude_deg, body.longitude_deg);
        let mean_heading = 0.5 * (body.heading_rad + out.heading_rad);
        let mean_horizontal = 0.5 * (body.tas_mps * body.gamma_rad.cos() + out.tas_mps * out.gamma_rad.cos());
        let east = mean_horizontal * mean_heading.sin() + air.wind_east_mps;
        let north = mean_horizontal * mean_heading.cos() + air.wind_north_mps;
        let (lat, lon) = geo::advance(
            body.latitude_deg,
            body.longitude_deg,
            body.pressure_altitude_ft,
            north / geo::M_PER_KT_S,
            east / geo::M_PER_KT_S,
            dt,
        );
        out.latitude_deg = lat;
        out.longitude_deg = geo::wrap_longitude(lon);
        out
    }

    /// The right-hand side of the equations of motion for one command.
    fn rates(&self, body: &Body, air: &Air, cmd: &Command, cfg: &Configuration, setting: f64) -> Rates {
        let temperature = if air.temperature_k.is_finite() && air.temperature_k > 100.0 {
            air.temperature_k
        } else {
            atmos::isa_temperature_k(body.pressure_altitude_ft)
        };
        let sound = atmos::sound_speed_mps(temperature);
        let mach = body.tas_mps / sound;
        let rho = atmos::density_kg_m3(air.pressure_pa, temperature);
        let q = 0.5 * rho * body.tas_mps * body.tas_mps;
        let mass = if body.mass_kg.is_finite() && body.mass_kg > 1.0 { body.mass_kg } else { f64::NAN };
        let weight = mass * atmos::G0;
        let s = self.aero.wing_area_m2;

        if let Command::Ballistic = cmd {
            // No aerodynamic forces at all: the energy-conservation reference.
            return Rates {
                d_tas: -atmos::G0 * body.gamma_rad.sin(),
                d_gamma: -atmos::G0 * body.gamma_rad.cos() / body.tas_mps,
                d_altitude: body.tas_mps * body.gamma_rad.sin(),
                d_heading: 0.0,
                d_mass: 0.0,
                mach,
                bank_rad: 0.0,
                fuel_status: 0,
            };
        }

        let (c_l, bank, thrust) = match *cmd {
            Command::Ballistic => unreachable!("handled above"),
            Command::FixedTrim { c_l, bank_rad } => {
                let trimmed = (c_l - self.aero.tuck_cl_shift(mach)).clamp(-self.aero.c_l_max_clean, self.aero.c_l_max_clean);
                let thrust = self.aero.thrust_n(cfg, rho, setting);
                (trimmed, bank_rad, thrust)
            }
            Command::BestGlide { bank_rad } => (self.aero.c_l_at_ld_max_in(cfg), bank_rad, self.aero.thrust_n(cfg, rho, setting)),
            Command::Track { vertical_speed_mps, target_mach, bank_rad } => {
                // Lift: curve the path towards the flight-path angle the target rate implies,
                // with a first-order lag of `tau` seconds, then cap at the usable lift.
                let target_gamma = (vertical_speed_mps / body.tas_mps).clamp(-0.9, 0.9).asin();
                let tau = 8.0;
                let d_gamma_wanted = (target_gamma - body.gamma_rad) / tau;
                let needed = (mass * (body.tas_mps * d_gamma_wanted + atmos::G0 * body.gamma_rad.cos())) / (q * s * bank_rad.cos().max(0.05));
                let c_l = needed.clamp(-self.aero.c_l_max_clean, self.aero.c_l_max_clean);
                // Thrust: hold the target Mach against the drag at this lift.
                let drag = self.aero.c_d(c_l, mach, cfg) * q * s;
                let wanted = drag + weight * body.gamma_rad.sin() + mass * (target_mach * sound - body.tas_mps) / tau;
                let full = self.aero.thrust_n(cfg, rho, 1.0);
                let idle = self.aero.thrust_n(cfg, rho, 0.0);
                (c_l, bank_rad, wanted.clamp(idle.min(full), full.max(idle)))
            }
        };
        let lift = c_l * q * s;
        let drag = self.aero.c_d(c_l, mach, cfg) * q * s;
        let v = body.tas_mps.max(1.0);
        let (burn_kg_s, fuel_status) =
            if body.fuel_kg > 0.0 && thrust > 0.0 { self.burn_kg_s(body, thrust, q, mach, mass) } else { (0.0, 0) };
        Rates {
            d_tas: (thrust - drag) / mass - atmos::G0 * body.gamma_rad.sin(),
            d_gamma: (lift * bank.cos() - weight * body.gamma_rad.cos()) / (mass * v),
            d_altitude: body.tas_mps * body.gamma_rad.sin(),
            d_heading: lift * bank.sin() / (mass * v * body.gamma_rad.cos().max(0.05)),
            d_mass: -burn_kg_s,
            mach,
            bank_rad: bank,
            fuel_status,
        }
    }

    /// Fuel burn at a thrust, kg/s, and how it was priced. See the `fuel` field for the
    /// derivation from the core's two-engine cruise tables. A state the core cannot price
    /// (`None`: non-finite argument, weight outside 140-300 t, no fuel model) falls back to the
    /// module's own TSFC and is flagged `FUEL_UNPRICED`, so the seconds flown that way are
    /// recorded - never read as zero flow, never substituted silently.
    fn burn_kg_s(&self, body: &Body, thrust_n: f64, q: f64, mach: f64, mass: f64) -> (f64, u8) {
        let own = self.aero.fuel_flow_kg_s(thrust_n);
        let Some(model) = self.fuel else { return (own, 0) };
        let Some(rate) = model.fuel_flow_kg_h(body.pressure_altitude_ft / 100.0, mass / 1000.0, mach) else {
            return (own, FUEL_UNPRICED);
        };
        let s = self.aero.wing_area_m2;
        let c_l_level = mass * atmos::G0 / (q * s);
        let cruise_drag = self.aero.c_d(c_l_level, mach, &Configuration::powered()) * q * s;
        if !(cruise_drag > 0.0 && rate.kg_h.is_finite() && rate.kg_h > 0.0) {
            return (own, FUEL_UNPRICED);
        }
        let mut status = 0;
        if rate.below_tables {
            status |= FUEL_BELOW_TABLES;
        }
        if rate.extrapolated {
            status |= FUEL_EXTRAPOLATED;
        }
        if rate.above_ceiling {
            status |= FUEL_ABOVE_CEILING;
        }
        (thrust_n * rate.kg_h / 3600.0 / cruise_drag, status)
    }

    /// The trimmed lift coefficient of steady level flight at a mass and dynamic pressure:
    /// `c_l = m g / (q S)`. Used by the level-flight-equilibrium test and by the profile sampler.
    #[cfg_attr(not(test), allow(dead_code))] // model surface exercised by this module's tests
    pub fn level_c_l(&self, mass_kg: f64, q_pa: f64) -> f64 {
        mass_kg * atmos::G0 / (q_pa * self.aero.wing_area_m2)
    }

    /// Lanchester's phugoid period, `pi sqrt(2) V / g`. The closed form the free-dynamics
    /// integration is checked against.
    #[cfg_attr(not(test), allow(dead_code))] // model surface exercised by this module's tests
    pub fn phugoid_period_s(tas_mps: f64) -> f64 {
        std::f64::consts::PI * std::f64::consts::SQRT_2 * tas_mps / atmos::G0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A frozen atmosphere: still air at one pressure and temperature, whatever the altitude.
    /// Lanchester's phugoid period assumes constant density, so the closed-form check needs it.
    struct Frozen {
        pressure_pa: f64,
        temperature_k: f64,
    }

    impl Atmosphere for Frozen {
        fn at(&self, _: f64, _: f64, _: f64, _: f64) -> Air {
            Air {
                temperature_k: self.temperature_k,
                pressure_pa: self.pressure_pa,
                wind_east_mps: 0.0,
                wind_north_mps: 0.0,
                declination_deg: 0.0,
                surface_pressure_altitude_ft: -1e9,
                clamped: false,
            }
        }
    }

    fn integrator(step_s: f64) -> Integrator<'static> {
        Integrator { aero: reference(), fuel: None, step_s, fine_step_s: step_s / 10.0, fine_window_s: 5.0, max_flight_s: 7_200.0 }
    }

    fn body(altitude_ft: f64, tas: f64, gamma_deg: f64) -> Body {
        Body {
            unix_s: 1_394_237_000.0,
            latitude_deg: -35.0,
            longitude_deg: 93.0,
            pressure_altitude_ft: altitude_ft,
            tas_mps: tas,
            gamma_rad: gamma_deg.to_radians(),
            heading_rad: std::f64::consts::PI,
            mass_kg: 174_000.0,
            fuel_kg: 0.0,
        }
    }

    /// §11 test 1 — ballistic energy conservation. With no lift, drag or thrust the specific
    /// energy height V^2/2g + h is exact, and halving the step cuts the residual by about 2^4,
    /// which is what RK4 should do.
    #[test]
    fn ballistic_flight_conserves_energy_at_fourth_order() {
        let mut residuals = Vec::new();
        for step in [2.0, 1.0, 0.5] {
            let it = integrator(step);
            let start = body(35_000.0, 240.0, -5.0);
            let e0 = start.energy_height_m(atmos::isa_temperature_k(35_000.0));
            let trace = it.run(
                start,
                &atmos::Standard,
                None,
                &mut |_, _| (Command::Ballistic, Configuration::glide(), 0.0),
                &mut |_, _| {},
            );
            let e1 = trace.impact.energy_height_m(atmos::isa_temperature_k(trace.impact.pressure_altitude_ft));
            residuals.push(((e1 - e0) / e0).abs());
            assert!(trace.impact.pressure_altitude_ft.abs() < 1.0, "did not reach the surface: {:?}", trace.impact.pressure_altitude_ft);
        }
        assert!(residuals[0] < 1e-6, "residual at 2 s: {:e}", residuals[0]);
        for w in residuals.windows(2) {
            assert!(w[1] <= w[0], "refinement made it worse: {:e} -> {:e}", w[0], w[1]);
        }
        assert!(residuals[2] < 1e-9, "residual at 0.5 s: {:e}", residuals[2]);
    }

    /// §11 test 2 — level-flight equilibrium. At the trimmed lift coefficient with thrust equal
    /// to drag the aircraft holds altitude and speed: over 600 s the altitude moves less than
    /// 20 ft and the Mach less than 0.001.
    #[test]
    fn level_flight_is_an_equilibrium() {
        let it = integrator(1.0);
        let (alt, mass) = (20_000.0, 174_000.0);
        let t = atmos::isa_temperature_k(alt);
        let p = geo::isa_pressure_pa(alt);
        let tas = 0.60 * atmos::sound_speed_mps(t);
        let q = 0.5 * atmos::density_kg_m3(p, t) * tas * tas;
        let c_l = it.level_c_l(mass, q);
        // Thrust exactly cancels drag: solve the setting rather than assume one.
        let cfg = Configuration::powered();
        let drag = it.aero.c_d(c_l, tas / atmos::sound_speed_mps(t), &cfg) * q * it.aero.wing_area_m2;
        let full = it.aero.thrust_n(&cfg, atmos::density_kg_m3(p, t), 1.0);
        let setting = drag / full;
        let start = Body { fuel_kg: 0.0, ..body(alt, tas, 0.0) };
        let mut last = start;
        let mut it2 = it;
        it2.max_flight_s = 600.0;
        let trace = it2.run(
            start,
            &atmos::Standard,
            None,
            &mut |_, _| (Command::FixedTrim { c_l, bank_rad: 0.0 }, cfg, setting),
            &mut |b, _| last = *b,
        );
        assert!(trace.timed_out, "level flight should not reach the surface");
        assert!((last.pressure_altitude_ft - alt).abs() < 20.0, "altitude drift {} ft", last.pressure_altitude_ft - alt);
        let mach = last.tas_mps / atmos::sound_speed_mps(atmos::isa_temperature_k(last.pressure_altitude_ft));
        assert!((mach - 0.60).abs() < 1e-3, "Mach drift {}", mach - 0.60);
        assert!(last.gamma_rad.abs() < 1e-3, "gamma drift {}", last.gamma_rad);
    }

    /// §11 test 3 — the free-dynamics oscillation has Lanchester's period pi sqrt(2) V / g.
    ///
    /// Lanchester's closed form assumes **constant density**, so it is tested against a frozen
    /// atmosphere; under the real ISA gradient the same integration gives a period about 10%
    /// shorter, because climbing into thinner air removes lift and so stiffens the oscillation.
    /// Both numbers are asserted: the first checks the integrator against the closed form, the
    /// second records a physical difference that would otherwise look like an error.
    #[test]
    fn the_phugoid_period_matches_lanchester() {
        // Drag and thrust removed, so the oscillation is the undamped classical phugoid.
        let mut aero = reference();
        aero.ld_max_clean = 1e9; // c_d0 -> 0
        aero.oswald = 1e9; // k -> 0
        aero.wave_drag_coefficient = 0.0;
        aero.tuck_cl_per_mach = 0.0;
        let it = Integrator { aero, fuel: None, step_s: 0.05, fine_step_s: 0.05, fine_window_s: 0.0, max_flight_s: 400.0 };
        let (alt, mass, tas) = (20_000.0, 174_000.0, 200.0);
        let frozen = Frozen { pressure_pa: geo::isa_pressure_pa(alt), temperature_k: atmos::isa_temperature_k(alt) };
        let q = atmos::dynamic_pressure_pa(frozen.pressure_pa, tas / atmos::sound_speed_mps(frozen.temperature_k));
        let c_l = it.level_c_l(mass, q);
        let cfg = Configuration { engines_thrusting: 0, engines_windmilling: 0, rat_deployed: false, speedbrake_eighths: 0, landing_configuration: false };

        let period = |atmosphere: &dyn Atmosphere| {
            let mut crossings: Vec<f64> = Vec::new();
            let mut previous: Option<(f64, f64)> = None;
            it.run(body(alt, tas, 0.5), atmosphere, None, &mut |_, _| (Command::FixedTrim { c_l, bank_rad: 0.0 }, cfg, 0.0), &mut |b, _| {
                let deviation = b.pressure_altitude_ft - alt;
                if let Some((t_prev, d_prev)) = previous {
                    if d_prev < 0.0 && deviation >= 0.0 {
                        // Linear interpolation of the upward zero crossing.
                        crossings.push(t_prev + (b.unix_s - t_prev) * (-d_prev) / (deviation - d_prev));
                    }
                }
                previous = Some((b.unix_s, deviation));
            });
            assert!(crossings.len() >= 3, "only {} crossings", crossings.len());
            (crossings[2] - crossings[0]) / 2.0
        };

        let lanchester = Integrator::phugoid_period_s(tas);
        assert!((lanchester - 90.61).abs() < 0.02, "closed form {lanchester}");
        let frozen_period = period(&frozen);
        assert!(
            (frozen_period - lanchester).abs() / lanchester < 0.001,
            "constant density: measured {frozen_period} s, Lanchester {lanchester} s"
        );
        let isa_period = period(&atmos::Standard);
        assert!((isa_period - 81.80).abs() / 81.80 < 0.02, "ISA gradient: measured {isa_period} s, expected about 81.8 s");
        assert!(isa_period < frozen_period, "the density gradient should shorten the period");
    }

    /// §11 test 4 — still-air glide distance equals altitude x (L/D), in the energy-height form
    /// that makes the identity exact.
    ///
    /// For a constant-lift-coefficient glide `dE/dx = -1/(L/D)` with `E = h + V^2/2g`, so the
    /// distance is `(L/D) x (E_start - E_end)`. The geometric altitude alone gives the leading
    /// term — here 93.7 NM, the ~100 NM the brief records for best glide — and the kinetic energy
    /// traded as the aircraft slows into denser air adds the remaining ~9.7 NM. Asserting the
    /// plain `h x (L/D)` would be asserting an error of 10%, so both are checked and named.
    #[test]
    fn still_air_glide_distance_is_altitude_times_lift_to_drag() {
        let it = integrator(1.0);
        let cfg = Configuration::glide();
        let ld = it.aero.ld_max_in(&cfg);
        let alt = 35_000.0;
        // Start at the configuration's best-glide speed and equilibrium angle.
        let c_l = it.aero.c_l_at_ld_max_in(&cfg);
        let speed_at = |altitude_ft: f64| {
            let t = atmos::isa_temperature_k(altitude_ft);
            let rho = atmos::density_kg_m3(geo::isa_pressure_pa(altitude_ft), t);
            (174_000.0 * atmos::G0 / (0.5 * rho * it.aero.wing_area_m2 * c_l)).sqrt()
        };
        let (v_start, v_end) = (speed_at(alt), speed_at(0.0));
        let start = body(alt, v_start, -(1.0f64 / ld).atan().to_degrees());
        let trace = it.run(start, &atmos::Standard, None, &mut |_, _| (Command::BestGlide { bank_rad: 0.0 }, cfg, 0.0), &mut |_, _| {});

        // Great-circle distance from the start, independently computed.
        let (a, b) = ((-35f64).to_radians(), trace.impact.latitude_deg.to_radians());
        let dlon = (trace.impact.longitude_deg - 93.0).to_radians();
        let hav = ((b - a) / 2.0).sin().powi(2) + a.cos() * b.cos() * (dlon / 2.0).sin().powi(2);
        let flown_nm = 2.0 * 3_440.065 * hav.sqrt().asin();

        let altitude_term_nm = alt * atmos::M_PER_FT / atmos::M_PER_NM * ld;
        let energy_height_m = alt * atmos::M_PER_FT + (v_start * v_start - v_end * v_end) / (2.0 * atmos::G0);
        let expected_nm = ld * energy_height_m / atmos::M_PER_NM;
        assert!((altitude_term_nm - 93.7).abs() < 0.5, "the altitude term is the brief's ~100 NM: {altitude_term_nm}");
        assert!((expected_nm - 103.4).abs() < 0.5, "energy-height prediction {expected_nm} NM");
        assert!((flown_nm - expected_nm).abs() / expected_nm < 0.01, "flew {flown_nm} NM, predicted {expected_nm} NM");
        // The kinetic-energy trade is the whole of the difference, and it is positive.
        assert!(flown_nm > altitude_term_nm, "{flown_nm} vs {altitude_term_nm}");
    }

    /// The step is a parameter and is refined near a named transition, independent of the core
    /// filter's 5 s manoeuvre step.
    #[test]
    fn the_step_is_refined_through_a_transition() {
        let it = integrator(5.0);
        assert_eq!(it.step_for(1_000.0, None), 5.0);
        assert_eq!(it.step_for(1_000.0, Some(1_002.0)), 0.5);
        assert_eq!(it.step_for(1_000.0, Some(1_020.0)), 5.0);
        // A descent through a transition takes more steps than the same descent without one.
        let cfg = Configuration::glide();
        let start = body(10_000.0, 200.0, -3.0);
        let coarse = it.run(start, &atmos::Standard, None, &mut |_, _| (Command::BestGlide { bank_rad: 0.0 }, cfg, 0.0), &mut |_, _| {});
        let fine = it.run(
            start,
            &atmos::Standard,
            Some(start.unix_s + 60.0),
            &mut |_, _| (Command::BestGlide { bank_rad: 0.0 }, cfg, 0.0),
            &mut |_, _| {},
        );
        assert!(fine.steps > coarse.steps, "{} vs {}", fine.steps, coarse.steps);
        assert!((fine.impact.pressure_altitude_ft - coarse.impact.pressure_altitude_ft).abs() < 1.0);
    }

    /// The surface crossing is interpolated, not quantised to the step: a 30 s step lands within
    /// a foot of the surface rather than hundreds of feet below it.
    #[test]
    fn the_impact_is_interpolated_within_the_final_step() {
        let it = integrator(30.0);
        let cfg = Configuration::glide();
        let trace = it.run(
            body(5_000.0, 200.0, -4.0),
            &atmos::Standard,
            None,
            &mut |_, _| (Command::BestGlide { bank_rad: 0.0 }, cfg, 0.0),
            &mut |_, _| {},
        );
        assert!(trace.impact.pressure_altitude_ft.abs() < 1.0, "{} ft", trace.impact.pressure_altitude_ft);
        assert!(trace.impact_vertical_speed_mps < 0.0);
        assert!(trace.time_descending_s > 0.0 && trace.max_descent_rate_fpm > 0.0);
    }

    /// Deliverable 1 fixture, not a check: free dynamics (no intervention, unpowered) from Boeing-like
    /// starts, written as 1 Hz X/Y/altitude traces so `smoke/boeing_calibration.py` can measure them
    /// exactly as it measures the ten engineering-simulator cases. Run with
    /// `EOF_CALIB_OUT=<dir> cargo test -p mh370-hypotheses -- --ignored free_dynamics_traces_for_calibration`.
    #[test]
    #[ignore]
    fn free_dynamics_traces_for_calibration() {
        let Ok(dir) = std::env::var("EOF_CALIB_OUT") else { return };
        let it = integrator(1.0);
        let cfg = Configuration::glide();
        for alt in [35_000.0, 40_000.0] {
            // The module's own free-trim lift: the LEVEL trim at the start state (profile.rs, Shape::FreeTrim),
            // plus the sampled offset. Not the best-glide C_L.
            let st = body(alt, 240.0, 0.0);
            let t_k = atmos::isa_temperature_k(alt);
            let q = atmos::dynamic_pressure_pa(geo::isa_pressure_pa(alt), st.tas_mps / atmos::sound_speed_mps(t_k));
            let c_l0 = st.mass_kg * atmos::G0 / (q * it.aero.wing_area_m2);
            for bank in [0.0, 2.0, 5.0, 8.0, 12.0, 15.0, 20.0, 25.0, 30.0, 35.0] {
                for dcl in [-0.08, 0.0, 0.08] {
                    let start = body(alt, 240.0, 0.0);
                    let mut rows = String::from("time_s,lat_deg,lon_deg,alt_ft,heading_rad\n");
                    let mut next = start.unix_s;
                    let c_l = c_l0 + dcl;
                    let trace = it.run(
                        start,
                        &atmos::Standard,
                        None,
                        &mut |_, _| (Command::FixedTrim { c_l, bank_rad: f64::to_radians(bank) }, cfg, 0.0),
                        &mut |b, _| {
                            if b.unix_s >= next {
                                rows.push_str(&format!("{},{},{},{},{}\n", b.unix_s - start.unix_s, b.latitude_deg, b.longitude_deg, b.pressure_altitude_ft, b.heading_rad));
                                next += 1.0;
                            }
                        },
                    );
                    rows.push_str(&format!("{},{},{},{},{}\n", trace.impact.unix_s - start.unix_s, trace.impact.latitude_deg, trace.impact.longitude_deg, 0.0, trace.impact.heading_rad));
                    let name = format!("{dir}/free-alt{alt:.0}-bank{bank:.0}-dcl{dcl:+.2}.csv");
                    std::fs::write(&name, rows).expect("write trace");
                }
            }
        }
    }

    /// A bank angle under fixed trim turns the aircraft and reduces the vertical component of
    /// lift, so the descending spiral falls out of the same equations as the phugoid.
    #[test]
    fn residual_bank_gives_a_descending_spiral_from_the_same_equations() {
        let it = integrator(1.0);
        let cfg = Configuration::glide();
        let c_l = it.aero.c_l_at_ld_max_in(&cfg);
        let start = body(35_000.0, 230.0, 0.0);
        let level = it.run(start, &atmos::Standard, None, &mut |_, _| (Command::FixedTrim { c_l, bank_rad: 0.0 }, cfg, 0.0), &mut |_, _| {});
        let spiral = it.run(
            start,
            &atmos::Standard,
            None,
            &mut |_, _| (Command::FixedTrim { c_l, bank_rad: 35f64.to_radians() }, cfg, 0.0),
            &mut |_, _| {},
        );
        // The comparison is the *mean* rate, not the peak: with zero bank the fixed-trim case
        // pitches up, phugoids and eventually dives, so its peak rate is the higher of the two
        // while it takes far longer to reach the water.
        let mean = |t: &Trace| 35_000.0 / (t.impact.unix_s - start.unix_s) * 60.0;
        assert!(mean(&spiral) > mean(&level), "{} vs {} ft/min mean", mean(&spiral), mean(&level));
        let turned = (spiral.impact.heading_rad - start.heading_rad).abs();
        assert!(turned > std::f64::consts::TAU, "the spiral should turn through more than one circle: {turned} rad");
        assert!(spiral.impact.unix_s < level.impact.unix_s, "the spiral should reach the water sooner");
    }
}
