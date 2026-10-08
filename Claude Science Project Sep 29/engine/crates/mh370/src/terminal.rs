//! Stage 2, the end of flight: every handed-off trajectory continues to impact.
//!
//! For each hand-off row and each of its N children, on the child's own random streams:
//! 1. the terminal module draws the takeover (descent onset or first flame-out, per the module);
//! 2. the runner flies the core dynamics to it, recording the state at each 00:19 burst on
//!    the way (the cruise-model convention, as in the filter: no vertical rate);
//! 3. the module descends from the takeover state to impact, returning one or more descents
//!    with the state at each burst after the takeover;
//! 4. the runner scores every data option from those states with the core measurement model:
//!    BTO Gaussian, BFO jointly with the parent's Kalman bias under each BFO model.
//!
//! Descent j of the M from one takeover has proposal weight exp(lnq_takeover + lnq_j) / M, and
//! the children of a parent share its hand-off weight in proportion (self-normalised per
//! parent). Every data option is a separate log-likelihood column of impacts.npy, computed
//! from the same children, so options compare side by side.

use crate::config::TerminalConfig;
use crate::handoff::{Row, Stop};
use crate::impacts::IMPACT_COLUMNS;
use crate::output::write_npy64;
use flight::environment::{Environment, MPS_PER_KNOT};
use flight::{Aircraft, Parameters};
use hypothesis::{Air, Atmosphere, EpochState, FlightState, FuelFlow, FuelFlowRate, Terminal, TerminalEpoch};
use rand::{Rng, SeedableRng};
use rand_chacha::ChaCha8Rng;
use rayon::prelude::*;
use satcom::{bfo_without_bias_hz, bto_us, gaussian_log_likelihood, BfoBias, Epoch, FinalBfo};
use serde_json::{json, Value};
use std::path::Path;

const FPM_PER_MPS: f64 = 60.0 / 0.3048;

/// Everything stage 2 shares across replicates.
pub struct Stage<'a, E> {
    pub params: &'a Parameters,
    pub environment: &'a E,
    /// The weather grid's time and pressure-altitude span; queries outside are clamped.
    pub span: Option<[(f64, f64); 2]>,
    pub module: &'a dyn Terminal,
    pub children: usize,
    /// The bursts after the stop, in time order; scored at their logged times.
    pub epochs: Vec<Epoch>,
    /// Per data option: (epoch index, BFO?) for each observation it uses.
    options: Vec<Vec<(usize, bool)>>,
    /// Log-likelihood columns: (label, data option, BFO model).
    columns: Vec<(String, usize, Option<usize>)>,
    /// (label, prior, model) of each 00:19 BFO model.
    bfo_models: Vec<(String, f64, FinalBfo)>,
    target: usize,
    /// Satellite position and BTO of the arc epoch.
    arc: (geo::Vec3, f64),
    families: usize,
    latents: usize,
}

impl<'a, E: Environment> Stage<'a, E> {
    /// Validate the terminal configuration against the bursts handed on by the filter.
    pub fn new(
        config: &TerminalConfig,
        params: &'a Parameters,
        environment: &'a E,
        span: Option<[(f64, f64); 2]>,
        module: &'a dyn Terminal,
        epochs: Vec<Epoch>,
    ) -> Result<Self, String> {
        if epochs.is_empty() {
            return Err("[terminal]: no bursts after the stop; list them in exclude_epochs".into());
        }
        if epochs.len() > 2 && config.options.iter().any(|o| o.observations.iter().any(|id| id.ends_with(".bfo"))) {
            return Err("[terminal]: the 00:19 BFO models cover two bursts".into());
        }
        let mut options = Vec::new();
        for option in &config.options {
            let mut uses = Vec::new();
            for id in &option.observations {
                let (epoch, quantity) = id.split_once('.').ok_or_else(|| format!("terminal option {}: bad observation {id}", option.id))?;
                let k = epochs.iter().position(|e| e.id == epoch).ok_or_else(|| {
                    format!("terminal option {}: {epoch} is not a burst after the stop (exclude it from the filter)", option.id)
                })?;
                let present = match quantity {
                    "bto" => epochs[k].bto_us.is_some(),
                    "bfo" => epochs[k].bfo_hz.is_some(),
                    _ => false,
                };
                if !present || uses.contains(&(k, quantity == "bfo")) {
                    return Err(format!("terminal option {}: {id} is not a measured BTO or BFO, or is listed twice", option.id));
                }
                uses.push((k, quantity == "bfo"));
            }
            options.push(uses);
        }
        let ids: Vec<&str> = config.options.iter().map(|o| o.id.as_str()).collect();
        if (1..ids.len()).any(|i| ids[..i].contains(&ids[i])) {
            return Err("[terminal]: option ids must be unique".into());
        }
        let bfo_models = config
            .bfo_models
            .iter()
            .map(|(label, m)| Ok((label.clone(), m.prior, FinalBfo::new(&m.model(label)?)?)))
            .collect::<Result<Vec<_>, String>>()?;
        let total: f64 = bfo_models.iter().map(|m| m.1).sum();
        if !bfo_models.is_empty() && (!bfo_models.iter().all(|m| m.1 > 0.0) || (total - 1.0).abs() > 1e-6) {
            return Err(format!("terminal.bfo_models: priors must be positive and sum to 1 (sum {total})"));
        }
        let mut columns = Vec::new();
        for (o, uses) in options.iter().enumerate() {
            let id = &config.options[o].id;
            if uses.iter().any(|u| u.1) {
                if bfo_models.is_empty() {
                    return Err(format!("terminal option {id} uses a BFO: declare terminal.bfo_models"));
                }
                columns.extend(bfo_models.iter().enumerate().map(|(m, (label, ..))| (format!("{id}/{label}"), o, Some(m))));
            } else {
                columns.push((id.clone(), o, None));
            }
        }
        let target = ids.iter().position(|id| *id == config.target).ok_or_else(|| format!("terminal.target {} is not an option", config.target))?;
        let arc = epochs.iter().find(|e| e.id == config.arc).and_then(|e| Some((e.satellite_km, e.bto_us?)));
        let arc = arc.ok_or_else(|| format!("terminal.arc {} is not a burst after the stop with a BTO", config.arc))?;
        let (families, latents) = (module.families().len(), module.latent_columns().len());
        if families == 0 {
            return Err("the terminal module declares no descent families".into());
        }
        Ok(Stage { params, environment, span, module, children: config.children, epochs, options, columns, bfo_models, target, arc, families, latents })
    }

    /// Column names of impacts.npy.
    pub fn impact_columns(&self) -> Vec<String> {
        let mut names: Vec<String> = IMPACT_COLUMNS.iter().map(|c| c.to_string()).collect();
        for e in &self.epochs {
            names.push(format!("bto_residual_us:{}", e.id));
            names.push(format!("bfo_innovation_hz:{}", e.id));
        }
        names.extend(self.module.latent_columns().iter().map(|l| format!("latent:{l}")));
        names.extend(self.columns.iter().map(|(label, ..)| format!("loglik:{label}")));
        names
    }

    /// What run.json records about the stage.
    pub fn manifest(&self) -> Value {
        json!({
            "module_families": self.module.families(),
            "latent_columns": self.module.latent_columns(),
            "children": self.children,
            "epochs": self.epochs.iter().map(|e| json!({"id": e.id, "logged_unix_s": e.logged_unix_s})).collect::<Vec<_>>(),
            "loglik_columns": self.columns.iter().map(|c| &c.0).collect::<Vec<_>>(),
            "bfo_models": self.bfo_models.iter().map(|m| json!({"label": m.0, "prior": m.1})).collect::<Vec<_>>(),
        })
    }

    /// Stage 2 for one replicate: writes impacts.npy to `dir` and returns its diagnostics.
    pub fn run(&self, seed: u64, stop: &Stop, rows: &[Row], dir: &Path) -> Result<Value, String> {
        let width = self.impact_columns().len();
        let per_parent: Vec<(Vec<f64>, Vec<f64>)> =
            rows.par_iter().enumerate().map(|(r, row)| self.children_of(seed, stop, r, row, width)).collect::<Result<_, String>>()?;
        let mut values = Vec::new();
        let mut corrections = Vec::new();
        for (v, c) in per_parent {
            values.extend(v);
            corrections.extend(c);
        }
        let count = values.len() / width;
        write_npy64(&dir.join("impacts.npy"), &[count, width], &values)?;
        Ok(self.diagnostics(&values, width, rows.len(), &corrections))
    }

    /// Every child of one hand-off row: its impact rows (weights self-normalised within the
    /// parent) and each child's mean proposal correction (for the self-check).
    fn children_of(&self, seed: u64, stop: &Stop, r: usize, row: &Row, width: usize) -> Result<(Vec<f64>, Vec<f64>), String> {
        if (row.aircraft.unix_s - stop.unix_s).abs() > 1e-3 {
            return Err(format!("hand-off row {r} is not at the stop time"));
        }
        let bias = BfoBias { mean_hz: row.bias.mean_hz, variance_hz2: row.bias.variance_hz2 };
        let handoff = flight_state(&row.aircraft, self.params);
        let atmosphere = Weather { environment: self.environment, span: self.span };
        let mut out = Vec::new();
        let mut log_weights = Vec::new();
        let mut corrections = Vec::with_capacity(self.children);
        for c in 0..self.children {
            let drawn = self.module.takeover(&handoff, &mut uniform(seed, 2, c, r));
            let (takeover, q_takeover) = (drawn.unix_s, drawn.log_q_correction);
            if !(takeover.is_finite() && takeover >= handoff.unix_s && q_takeover.is_finite()) {
                return Err(format!("{r}/{c}: takeover {takeover} (correction {q_takeover}) is not a finite time after the hand-off"));
            }
            // Powered flight on the core dynamics, through the bursts before the takeover.
            let mut aircraft = row.aircraft.clone();
            let mut rng = child_stream(seed, 1, c, r);
            let later = self.epochs.iter().position(|e| e.logged_unix_s > takeover).unwrap_or(self.epochs.len());
            let mut states: Vec<Option<EpochState>> = vec![None; self.epochs.len()];
            for (k, epoch) in self.epochs[..later].iter().enumerate() {
                aircraft.propagate(epoch.logged_unix_s, self.params, self.environment, &mut rng);
                states[k] = Some(powered_state(&aircraft));
            }
            aircraft.propagate(takeover, self.params, self.environment, &mut rng);
            let at = flight_state(&aircraft, self.params);
            let fuel = CoreFuel { model: self.params.fuel.as_deref(), factor: aircraft.fuel_factor() };

            let requested: Vec<TerminalEpoch> =
                self.epochs[later..].iter().map(|e| TerminalEpoch { id: e.id.clone(), unix_s: e.logged_unix_s }).collect();
            // For the module's proposal only; NaN if it passes the wrong number of states.
            let score = |candidates: &[Option<EpochState>]| {
                if candidates.len() != self.epochs.len() - later {
                    return f64::NAN;
                }
                let mut all = states.clone();
                all[later..].copy_from_slice(candidates);
                self.target_log_likelihood(&all, bias)
            };
            let descents =
                self.module.descend_after(&at, &drawn, &atmosphere, &fuel, &mut uniform(seed, 3, c, r), &requested, &score);
            if descents.is_empty() {
                return Err(format!("{r}/{c}: the terminal module returned no descent"));
            }
            let mut mean = 0.0;
            for d in &descents {
                let i = &d.impact;
                let valid = i.unix_s.is_finite() && i.unix_s >= takeover && i.latitude_deg.is_finite() && i.longitude_deg.is_finite();
                if !valid || d.family >= self.families || d.latents.len() != self.latents || d.at_epochs.len() != requested.len() {
                    return Err(format!("{r}/{c}: descent with a non-finite or early impact, unknown family, or wrong latents/epochs length"));
                }
                if !d.log_q_correction.is_finite() {
                    return Err(format!("{r}/{c}: non-finite log proposal correction"));
                }
                let finite = |s: &EpochState| {
                    [s.latitude_deg, s.longitude_deg, s.altitude_ft, s.velocity_east_mps, s.velocity_north_mps, s.velocity_up_mps]
                        .iter()
                        .all(|v| v.is_finite())
                };
                if !d.at_epochs.iter().flatten().all(finite) {
                    return Err(format!("{r}/{c}: a state at a burst is not finite (use None if the aircraft was down)"));
                }
                let mut all = states.clone();
                all[later..].copy_from_slice(&d.at_epochs);
                let q = q_takeover + d.log_q_correction;
                mean += q.exp() / descents.len() as f64;
                log_weights.push(q - (descents.len() as f64).ln());
                out.extend(self.impact_row(r, row, &at, d, q, &all, bias));
            }
            corrections.push(mean);
        }
        // Self-normalise within the parent: the children share its hand-off weight.
        let max = log_weights.iter().copied().fold(f64::NEG_INFINITY, f64::max);
        let total: f64 = log_weights.iter().map(|lw| (lw - max).exp()).sum();
        for (k, lw) in log_weights.iter().enumerate() {
            out[k * width] = row.weight * (lw - max).exp() / total;
        }
        Ok((out, corrections))
    }

    fn impact_row(&self, r: usize, row: &Row, at: &FlightState, d: &hypothesis::Descent, q: f64, states: &[Option<EpochState>], bias: BfoBias) -> Vec<f64> {
        let i = &d.impact;
        let (ve, vn, vu) = (i.velocity_east_mps, i.velocity_north_mps, i.velocity_up_mps);
        let speed2 = ve * ve + vn * vn + vu * vu;
        let mut v = vec![
            f64::NAN, // weight, set per parent
            r as f64,
            row.mode as f64,
            row.alternative as f64,
            d.family as f64,
            i.unix_s,
            i.latitude_deg,
            i.longitude_deg,
            ve,
            vn,
            vu,
            (-vu).atan2(ve.hypot(vn)).to_degrees(),
            i.mass_kg,
            0.5 * i.mass_kg * speed2,
            0.5 * i.mass_kg * vu * vu,
            at.unix_s,
            at.latitude_deg,
            at.longitude_deg,
            at.altitude_ft,
            satcom::arc_distance_nm(self.arc.0, i.latitude_deg, i.longitude_deg, 0.0, self.arc.1),
            q,
        ];
        for (epoch, state) in self.epochs.iter().zip(states) {
            let (bto, bfo) = match state {
                Some(s) => {
                    let bto = epoch.bto_us.map_or(f64::NAN, |z| z - bto_us(epoch.satellite_km, s.latitude_deg, s.longitude_deg, s.altitude_ft));
                    let bfo = epoch.bfo_hz.map_or(f64::NAN, |z| z - predicted_bfo(epoch, s) - bias.mean_hz);
                    (bto, bfo)
                }
                None => (f64::NAN, f64::NAN),
            };
            v.extend([bto, bfo]);
        }
        v.extend(&d.latents);
        for (_, option, model) in &self.columns {
            v.push(self.log_likelihood(*option, *model, states, bias));
        }
        v
    }

    /// ln p(the option's observations | the states at the bursts), under one BFO model. Minus
    /// infinity if the aircraft was down before a burst the option uses.
    fn log_likelihood(&self, option: usize, model: Option<usize>, states: &[Option<EpochState>], bias: BfoBias) -> f64 {
        let mut total = 0.0;
        let mut contacts = [None, None];
        for &(k, is_bfo) in &self.options[option] {
            let (epoch, Some(s)) = (&self.epochs[k], &states[k]) else { return f64::NEG_INFINITY };
            if is_bfo {
                contacts[k] = Some((epoch.bfo_hz.unwrap(), predicted_bfo(epoch, s), epoch.bfo_sd_hz));
            } else {
                let residual = epoch.bto_us.unwrap() - bto_us(epoch.satellite_km, s.latitude_deg, s.longitude_deg, s.altitude_ft);
                total += gaussian_log_likelihood(residual, epoch.bto_sd_us);
            }
        }
        match model {
            Some(m) => total + self.bfo_models[m].2.log_likelihood(bias, contacts),
            None => total,
        }
    }

    /// The target option's log-likelihood, BFO models mixed by their priors: for proposals only.
    fn target_log_likelihood(&self, states: &[Option<EpochState>], bias: BfoBias) -> f64 {
        if !self.options[self.target].iter().any(|u| u.1) {
            return self.log_likelihood(self.target, None, states, bias);
        }
        let terms: Vec<f64> = (0..self.bfo_models.len())
            .map(|m| self.bfo_models[m].1.ln() + self.log_likelihood(self.target, Some(m), states, bias))
            .collect();
        let max = terms.iter().copied().fold(f64::NEG_INFINITY, f64::max);
        if max == f64::NEG_INFINITY {
            return max;
        }
        max + terms.iter().map(|t| (t - max).exp()).sum::<f64>().ln()
    }

    /// Per replicate: the proposal self-check (mean correction per child, which is 1 in
    /// expectation for an exactly normalised proposal) and, per column, the log-evidence
    /// increment and the effective sample size over rows and over parents.
    fn diagnostics(&self, values: &[f64], width: usize, parents: usize, corrections: &[f64]) -> Value {
        let rows: Vec<&[f64]> = values.chunks_exact(width).collect();
        let n = corrections.len() as f64;
        let mean = corrections.iter().sum::<f64>() / n;
        let sd = (corrections.iter().map(|c| (c - mean).powi(2)).sum::<f64>() / (n - 1.0).max(1.0)).sqrt();
        let ess = |weight: &dyn Fn(&[f64]) -> f64| {
            let w: Vec<f64> = rows.iter().map(|row| weight(row)).collect();
            let total: f64 = w.iter().sum();
            let mut by_parent = vec![0.0; parents];
            for (row, wi) in rows.iter().zip(&w) {
                by_parent[row[1] as usize] += wi;
            }
            let ess = |v: &[f64]| total * total / v.iter().map(|x| x * x).sum::<f64>();
            (total, ess(&w), ess(&by_parent))
        };
        let (_, prior_rows, prior_parents) = ess(&|row| row[0]);
        let first_loglik = width - self.columns.len();
        let columns: Vec<Value> = self
            .columns
            .iter()
            .enumerate()
            .map(|(c, (label, ..))| {
                let k = first_loglik + c;
                let max = rows.iter().map(|row| row[k]).fold(f64::NEG_INFINITY, f64::max);
                if max == f64::NEG_INFINITY {
                    // Every descent makes these observations impossible.
                    return json!({"column": label, "log_evidence_increment": null, "ess_rows": 0.0, "ess_parents": 0.0});
                }
                let (total, rows_ess, parents_ess) = ess(&|row| row[0] * (row[k] - max).exp());
                json!({"column": label, "log_evidence_increment": max + total.ln(), "ess_rows": rows_ess, "ess_parents": parents_ess})
            })
            .collect();
        json!({
            "parents": parents,
            "children": corrections.len(),
            "descents": rows.len(),
            "proposal_self_check": {"mean_correction": mean, "standard_error": sd / n.sqrt()},
            "ess_prior": {"rows": prior_rows, "parents": prior_parents},
            "columns": columns,
        })
    }
}

/// The runner's weather service for terminal modules.
struct Weather<'a, E> {
    environment: &'a E,
    span: Option<[(f64, f64); 2]>,
}

impl<E: Environment> Atmosphere for Weather<'_, E> {
    fn at(&self, unix_s: f64, altitude_ft: f64, latitude_deg: f64, longitude_deg: f64) -> Air {
        let w = self.environment.weather(unix_s, altitude_ft, latitude_deg, longitude_deg);
        let outside = |(lo, hi): (f64, f64), x: f64| !(lo..=hi).contains(&x);
        Air {
            temperature_k: w.temperature_k,
            pressure_pa: geo::isa_pressure_pa(altitude_ft),
            wind_east_mps: w.wind_east_kt * MPS_PER_KNOT,
            wind_north_mps: w.wind_north_kt * MPS_PER_KNOT,
            declination_deg: self.environment.declination_deg(altitude_ft, latitude_deg, longitude_deg),
            surface_pressure_altitude_ft: 0.0,
            clamped: self.span.is_some_and(|[time, altitude]| outside(time, unix_s) || outside(altitude, altitude_ft)),
        }
    }
}

/// The runner's fuel-flow service for terminal modules (core request 3): the cruise tables and
/// this trajectory's own fuel-flow factor, so the descent is priced by the model the cruise
/// burn used. `None` where the core cannot price the state - see [`FuelFlow`] for what a module
/// must do then; it is never zero flow.
struct CoreFuel<'a> {
    model: Option<&'a flight::FuelModel>,
    factor: f64,
}

impl FuelFlow for CoreFuel<'_> {
    fn fuel_flow_kg_h(&self, flight_level: f64, weight_t: f64, mach: f64) -> Option<FuelFlowRate> {
        let (flow, cover) = self.model?.tables.fuel_flow_kg_h(flight_level, weight_t, mach)?;
        let kg_h = flow * self.factor;
        (kg_h.is_finite() && kg_h > 0.0).then_some(FuelFlowRate {
            kg_h,
            extrapolated: cover.extrapolated_mach || cover.single_schedule || cover.fit_fallback,
            below_tables: cover.below_tables,
            above_ceiling: cover.above_ceiling,
        })
    }
}

/// The core aircraft state as a terminal module sees it.
fn flight_state(a: &Aircraft, p: &Parameters) -> FlightState {
    let air = a.air_data();
    FlightState {
        unix_s: a.unix_s,
        latitude_deg: a.lat,
        longitude_deg: a.lon,
        altitude_ft: a.alt_ft,
        ground_velocity_east_mps: a.v_east_kt * MPS_PER_KNOT,
        ground_velocity_north_mps: a.v_north_kt * MPS_PER_KNOT,
        vertical_speed_mps: a.vertical_speed_fpm(p) / FPM_PER_MPS,
        mach: a.mach,
        true_air_speed_mps: air.true_air_speed_kt * MPS_PER_KNOT,
        heading_deg: air.heading_rad.to_degrees().rem_euclid(360.0),
        wind_east_mps: air.wind_east_kt * MPS_PER_KNOT,
        wind_north_mps: air.wind_north_kt * MPS_PER_KNOT,
        mode: a.mode as usize,
        // The fuel state the filter is already carrying. NaN is retained when no fuel model is
        // configured, which means "not computed", not "impossible". `realised_flameout_unix_s`
        // is the time the tanks actually ran dry and stays NaN for a trajectory still holding
        // fuel; a terminal module wanting PREDICTED endurance derives it from `fuel_kg`.
        mass_kg: p.fuel.as_ref().map_or(f64::NAN, |m| m.zfw_kg + a.fuel_kg),
        fuel_kg: if p.fuel.is_some() { a.fuel_kg } else { f64::NAN },
        realised_flameout_unix_s: a.fuel_exhausted_unix_s,
    }
}

/// A powered state at a burst, with no vertical rate (the cruise-model convention).
fn powered_state(a: &Aircraft) -> EpochState {
    EpochState {
        latitude_deg: a.lat,
        longitude_deg: a.lon,
        altitude_ft: a.alt_ft,
        velocity_east_mps: a.v_east_kt * MPS_PER_KNOT,
        velocity_north_mps: a.v_north_kt * MPS_PER_KNOT,
        velocity_up_mps: 0.0,
    }
}

fn predicted_bfo(epoch: &Epoch, s: &EpochState) -> f64 {
    let (vn, ve) = (s.velocity_north_mps / MPS_PER_KNOT, s.velocity_east_mps / MPS_PER_KNOT);
    bfo_without_bias_hz(epoch, s.latitude_deg, s.longitude_deg, s.altitude_ft, vn, ve, s.velocity_up_mps * FPM_PER_MPS)
}

/// The stream of one (purpose, child, hand-off row): purposes 1 powered flight, 2 takeover,
/// 3 descent. Disjoint from every filter stream, whose top 16 bits are the stratum.
fn child_stream(seed: u64, purpose: u64, child: usize, row: usize) -> ChaCha8Rng {
    let mut rng = ChaCha8Rng::seed_from_u64(seed);
    rng.set_stream(((0xF000 | purpose) << 48) | ((child as u64) << 32) | row as u64);
    rng
}

/// Uniform draws on the open interval (0, 1), for terminal modules.
fn uniform(seed: u64, purpose: u64, child: usize, row: usize) -> impl FnMut() -> f64 {
    let mut rng = child_stream(seed, purpose, child, row);
    move || ((rng.gen::<u64>() >> 11) as f64 + 0.5) / (1u64 << 53) as f64
}


#[cfg(test)]
mod tests {
    use super::*;
    use hypothesis::{Descent, Impact, NoFuelModel, Takeover};
    use std::sync::Mutex;

    fn model() -> flight::FuelModel {
        let p = concat!(env!("CARGO_MANIFEST_DIR"), "/../../data/fuel-tables.json");
        let tables = flight::fuel::FuelTables::from_json(&std::fs::read_to_string(p).expect("fuel tables")).unwrap();
        flight::FuelModel::new(tables, flight::fuel::FuelPrior::default())
    }

    /// Core request 3: the descent is priced by the cruise model with the trajectory's own
    /// factor - not a second model, and never zero.
    #[test]
    fn core_fuel_is_the_cruise_tables_times_the_trajectorys_factor() {
        let m = model();
        let (fl, w, mach, factor) = (350.0, 200.0, 0.80, 1.0213);
        let (base, _) = m.tables.fuel_flow_kg_h(fl, w, mach).unwrap();
        let got = CoreFuel { model: Some(&m), factor }.fuel_flow_kg_h(fl, w, mach).unwrap();
        assert!((got.kg_h - base * factor).abs() < 1e-9, "{} against {}", got.kg_h, base * factor);
        assert!(!got.extrapolated && !got.below_tables && !got.above_ceiling);
        // Ordinary cruise is priced in the range the Boeing validation covers.
        assert!((4_000.0..9_000.0).contains(&got.kg_h), "{}", got.kg_h);
        // Low level is priced, and says it was clamped; it is not zero.
        let low = CoreFuel { model: Some(&m), factor }.fuel_flow_kg_h(20.0, w, 0.45).unwrap();
        assert!(low.below_tables && low.kg_h > 0.0);
        // Unpriceable states are None, never Some(0).
        for (fl, w, mach) in [(f64::NAN, w, mach), (fl, f64::NAN, mach), (fl, w, f64::NAN), (fl, 900.0, mach)] {
            let r = CoreFuel { model: Some(&m), factor }.fuel_flow_kg_h(fl, w, mach);
            assert!(r.map_or(true, |r| r.kg_h > 0.0), "({fl}, {w}, {mach}) priced at {r:?}");
        }
        assert!(CoreFuel { model: None, factor }.fuel_flow_kg_h(fl, w, mach).is_none());
    }

    /// A module that overrides neither new hook behaves exactly as before: the defaults call
    /// `takeover_time` and `descend` with the same streams.
    struct Plain;
    impl Terminal for Plain {
        fn families(&self) -> Vec<String> {
            vec!["only".into()]
        }
        fn takeover_time(&self, h: &FlightState, u: &mut dyn FnMut() -> f64) -> (f64, f64) {
            (h.unix_s + 100.0 * u(), -0.25)
        }
        fn descend(&self, t: &FlightState, _: &dyn Atmosphere, u: &mut dyn FnMut() -> f64, e: &[TerminalEpoch], _: &dyn Fn(&[Option<EpochState>]) -> f64) -> Vec<Descent> {
            vec![descent(t.unix_s + u(), e.len(), vec![])]
        }
    }

    /// Core request 2: a module that does override them gets its own draw back unchanged.
    struct Carries(Mutex<Vec<Vec<f64>>>);
    impl Terminal for Carries {
        fn families(&self) -> Vec<String> {
            vec!["only".into()]
        }
        fn takeover_time(&self, _: &FlightState, _: &mut dyn FnMut() -> f64) -> (f64, f64) {
            unreachable!("the runner calls takeover")
        }
        fn descend(&self, _: &FlightState, _: &dyn Atmosphere, _: &mut dyn FnMut() -> f64, _: &[TerminalEpoch], _: &dyn Fn(&[Option<EpochState>]) -> f64) -> Vec<Descent> {
            unreachable!("the runner calls descend_after")
        }
        fn takeover(&self, h: &FlightState, u: &mut dyn FnMut() -> f64) -> Takeover {
            Takeover { unix_s: h.unix_s + 60.0, log_q_correction: 0.0, draw: vec![2.0, 0.0, u()] }
        }
        fn descend_after(&self, t: &FlightState, drawn: &Takeover, _: &dyn Atmosphere, fuel: &dyn FuelFlow, _: &mut dyn FnMut() -> f64, e: &[TerminalEpoch], _: &dyn Fn(&[Option<EpochState>]) -> f64) -> Vec<Descent> {
            self.0.lock().unwrap().push(drawn.draw.clone());
            assert!(fuel.fuel_flow_kg_h(350.0, 200.0, 0.8).is_none(), "NoFuelModel prices nothing");
            vec![descent(t.unix_s, e.len(), vec![])]
        }
    }

    fn descent(unix_s: f64, epochs: usize, latents: Vec<f64>) -> Descent {
        let impact = Impact { unix_s, latitude_deg: -37.0, longitude_deg: 89.0, velocity_east_mps: 0.0, velocity_north_mps: 0.0, velocity_up_mps: -10.0, mass_kg: 180_000.0 };
        Descent { impact, family: 0, at_epochs: vec![None; epochs], latents, log_q_correction: 0.0 }
    }

    fn state() -> FlightState {
        FlightState {
            unix_s: 1_394_237_459.0, latitude_deg: -36.0, longitude_deg: 90.0, altitude_ft: 35_000.0,
            ground_velocity_east_mps: 100.0, ground_velocity_north_mps: -200.0, vertical_speed_mps: 0.0,
            mach: 0.8, true_air_speed_mps: 240.0, heading_deg: 200.0, wind_east_mps: 0.0, wind_north_mps: 0.0,
            mode: 2, mass_kg: 175_000.0, fuel_kg: 800.0, realised_flameout_unix_s: f64::NAN,
        }
    }

    struct Still;
    impl Atmosphere for Still {
        fn at(&self, _: f64, _: f64, _: f64, _: f64) -> Air {
            Air { temperature_k: 220.0, pressure_pa: 23_800.0, wind_east_mps: 0.0, wind_north_mps: 0.0, declination_deg: 0.0, surface_pressure_altitude_ft: 0.0, clamped: false }
        }
    }

    #[test]
    fn the_default_hooks_are_the_old_pair_on_the_same_streams() {
        let h = state();
        let stream = || {
            let mut k = 0.0;
            move || {
                k += 0.125;
                k
            }
        };
        let (mut a, mut b) = (stream(), stream());
        let drawn = Plain.takeover(&h, &mut a);
        assert_eq!((drawn.unix_s, drawn.log_q_correction, drawn.draw.len()), (Plain.takeover_time(&h, &mut b).0, -0.25, 0));
        let (mut a, mut b) = (stream(), stream());
        let new = Plain.descend_after(&h, &drawn, &Still, &NoFuelModel, &mut a, &[], &|_| 0.0);
        let old = Plain.descend(&h, &Still, &mut b, &[], &|_| 0.0);
        assert_eq!(new, old);
    }

    #[test]
    fn an_overriding_module_gets_its_own_draw_back() {
        let m = Carries(Mutex::new(Vec::new()));
        let h = state();
        let mut u = || 0.375;
        let drawn = m.takeover(&h, &mut u);
        // The runner flies the core in between; the module must not need to recompute anything.
        let flown = FlightState { unix_s: drawn.unix_s, fuel_kg: 0.0, realised_flameout_unix_s: h.unix_s + 30.0, ..h };
        m.descend_after(&flown, &drawn, &Still, &NoFuelModel, &mut u, &[], &|_| 0.0);
        assert_eq!(m.0.lock().unwrap().as_slice(), &[vec![2.0, 0.0, 0.375]]);
    }
}
