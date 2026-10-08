//! Hydroacoustics: forward-propagate each impact sample to predicted arrivals at the IMS
//! hydroacoustic stations, by the deep sound channel (SOFAR) and acoustic-gravity-wave (AGW)
//! branches kept separate, and assess detectability before any detection is claimed.
//!
//! Brief: `Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md`.
//!
//! MODE. Only `mode = "predictive"` exists. `impact_log_likelihood` returns exactly 0.0, which
//! means "module selected, no data used" (ruled 2026-10-08, coordination/HYDROACOUSTICS.md); NaN
//! is reserved for a sample the module could not compute. A likelihood mode is refused at
//! construction until injection-recovery has given P_D against received level, spanning the
//! coupling-efficiency prior (brief §2 rule 2 and the 8 October impact-source section). The
//! eventual form is (1 - P_D) + P_D x (match to detections / background rate).
//!
//! WHAT IS COMPUTED NOW, per station and impact sample: WGS84 geodesic range and back-azimuth
//! (Vincenty, checked against Karney), and the SOFAR arrival time with a standard deviation from
//! a declared group-speed prior. The group speed is PROVISIONAL (run.toml) and is replaced by the
//! modal group speed along each path once the propagation engine is validated against Blackman
//! et al. (2004), UCRL-TR-207323, with the air8 non-detection at H01 as the negative control.
//!
//! WHAT IS NOT COMPUTED, and is NaN by design: transmission loss, received exposure and pressure
//! (no validated propagation engine yet); the AGW arrival (no modal AGW solver yet); and the
//! AGW impulsive/non-impulsive regime, which needs the seafloor depth at the impact point (a
//! shared-layer lookup owned by ocean transport, not yet in ImpactView) and
//! energy_transfer_tau90_s (an end-of-flight latent, not yet readable by name — core request 1).
//!
//! STATIONS come from one documented source, FDSN metadata for network IM via EarthScope, epoch
//! valid 2014-03-08 (data/stations.csv, rebuilt by prepare/fetch_stations.py). The constants
//! below are the plain means of the three triad elements.
//!
//! DEPARTURES FROM PRIOR WORK. The archived crate's transfer function and near-field shock law
//! were never calibrated and are not ported (brief §11). Its arrival and energy relations are
//! ported, rewritten to this API, with its three tests: zero range, energy x4 gives pressure x2,
//! and the H01W/H08S scale, the last re-derived for the FDSN coordinates (the archived values
//! differ by 4.3 and 9.0 km).
//!
//! THREE DURATIONS are distinct and only meet here: energy_transfer_tau90_s (end of flight's),
//! acoustic source duration and received signal duration (both this module's). A received
//! duration is never returned to end of flight as an estimate of the first.

// The exposure and cutoff relations are tested now and used once transmission loss and the
// seafloor depth arrive; until then they are dead code in a non-test build.
#[allow(dead_code)]
mod physics;

use hypothesis::{Hypothesis, ImpactView};
use serde::Deserialize;

/// (name, latitude, longitude) of each triad centroid, from data/stations.csv.
const STATIONS: [(&str, f64, f64); 5] = [
    ("H01W", -34.890303, 114.142637),
    ("H08S", -7.639380, 72.483828),
    ("H08N", -6.337533, 71.002077),
    ("H11N", 19.720514, 166.899582),
    ("H11S", 18.498257, 166.697245),
];

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Params {
    mode: String,
    stations: Vec<String>,
    /// Provisional SOFAR group speed prior, km/s, mean and standard deviation.
    sofar_group_speed_km_s: f64,
    sofar_group_speed_sd_km_s: f64,
}

struct Hydroacoustics {
    stations: Vec<(String, f64, f64)>,
    speed: f64,
    speed_sd: f64,
}

const PER_STATION: [&str; 4] =
    ["range_km", "backazimuth_deg", "sofar_arrival_unix_s", "sofar_arrival_sd_s"];

pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String> {
    let p: Params = params.clone().try_into().map_err(|e| format!("hydroacoustics: {e}"))?;
    if p.mode != "predictive" {
        return Err(format!(
            "hydroacoustics: mode `{}` refused; only `predictive` exists until injection-recovery \
             gives P_D against received level (brief §2 rule 2)",
            p.mode
        ));
    }
    if !(p.sofar_group_speed_km_s > 0.0 && p.sofar_group_speed_sd_km_s >= 0.0) {
        return Err("hydroacoustics: group speed must be positive, its sd non-negative".into());
    }
    let mut stations = Vec::new();
    for name in &p.stations {
        let s = STATIONS
            .iter()
            .find(|s| s.0 == name)
            .ok_or_else(|| format!("hydroacoustics: unknown station `{name}`"))?;
        stations.push((s.0.to_string(), s.1, s.2));
    }
    if stations.is_empty() {
        return Err("hydroacoustics: no stations".into());
    }
    Ok(Box::new(Hydroacoustics {
        stations,
        speed: p.sofar_group_speed_km_s,
        speed_sd: p.sofar_group_speed_sd_km_s,
    }))
}

impl Hypothesis for Hydroacoustics {
    /// No data are consumed in predictive mode.
    fn observations(&self) -> Vec<String> {
        Vec::new()
    }

    /// A constant likelihood of one is exact for "no data used", so it is on an absolute scale.
    fn absolute_scale(&self) -> bool {
        true
    }

    fn prediction_columns(&self) -> Vec<String> {
        let mut cols = Vec::new();
        for (name, _, _) in &self.stations {
            for c in PER_STATION {
                cols.push(format!("{name}_{c}"));
            }
        }
        cols.push("agw_impulsive".into());
        cols
    }

    fn impact_log_likelihood(&self, _impact: &ImpactView, _choice: &[usize]) -> f64 {
        0.0
    }

    fn predict(&self, impact: &ImpactView, out: &mut [f64]) {
        for (i, (_, lat, lon)) in self.stations.iter().enumerate() {
            let (d, _) =
                physics::geodesic_inverse(impact.latitude_deg, impact.longitude_deg, *lat, *lon);
            let (_, back) =
                physics::geodesic_inverse(*lat, *lon, impact.latitude_deg, impact.longitude_deg);
            let (t, sd) = physics::travel_time_s(d, self.speed, self.speed_sd);
            let o = &mut out[i * PER_STATION.len()..(i + 1) * PER_STATION.len()];
            o[0] = d;
            o[1] = back.rem_euclid(360.0);
            o[2] = impact.unix_s + t;
            o[3] = sd;
        }
        // Needs seafloor depth (shared layer) and energy_transfer_tau90_s by name; neither is
        // readable yet, so the regime is "not assessed".
        out[self.stations.len() * PER_STATION.len()] = f64::NAN;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn params(mode: &str) -> toml::Value {
        toml::from_str(&format!(
            "mode = \"{mode}\"\nstations = [\"H01W\", \"H08S\"]\n\
             sofar_group_speed_km_s = 1.49\nsofar_group_speed_sd_km_s = 0.0\n"
        ))
        .unwrap()
    }

    fn impact(lat: f64, lon: f64) -> ImpactView<'static> {
        ImpactView {
            parent: 0,
            unix_s: 1_000.0,
            latitude_deg: lat,
            longitude_deg: lon,
            velocity_east_mps: 80.0,
            velocity_north_mps: 0.0,
            velocity_up_mps: -100.0,
            flight_path_angle_deg: 51.3,
            mass_kg: 174_000.0,
            kinetic_energy_j: 0.5 * 174_000.0 * (80.0f64.powi(2) + 100.0f64.powi(2)),
            vertical_kinetic_energy_j: 0.5 * 174_000.0 * 100.0f64.powi(2),
            family: 0,
            takeover_unix_s: 0.0,
            takeover_latitude_deg: lat,
            takeover_longitude_deg: lon,
            takeover_altitude_ft: 35_000.0,
            mode: 0,
            alternative: 0,
            latents: &[],
        }
    }

    #[test]
    fn predictive_mode_contributes_exactly_nothing() {
        let h = new(&params("predictive")).unwrap();
        assert_eq!(h.impact_log_likelihood(&impact(-37.225, 88.9), &[]), 0.0);
        assert!(h.observations().is_empty());
        assert!(h.alternatives().is_empty());
    }

    #[test]
    fn likelihood_mode_is_refused_until_the_pd_gate() {
        assert!(new(&params("likelihood")).is_err());
    }

    #[test]
    fn predictions_fill_every_column_and_mark_the_regime_not_assessed() {
        let h = new(&params("predictive")).unwrap();
        let cols = h.prediction_columns();
        assert_eq!(cols.len(), 9);
        let mut out = vec![0.0; cols.len()];
        h.predict(&impact(-34.9167, 92.0472), &mut out);
        assert!((out[0] - 2_015.2833).abs() < 1e-3);
        assert!((out[2] - 1_000.0 - 2_015.2833 / 1.49).abs() < 1e-3);
        assert!((out[5] - 149.26776).abs() < 1e-4, "{}", out[5]);
        assert!(out[8].is_nan());
        assert!(cols.iter().all(|c| !c.contains(['/', ',', ':'])));
    }
}
