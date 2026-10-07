//! Arc kernel: a placeholder end-of-flight model, so that the stages after the filter (impact
//! modules, the composer) can run before the end-of-flight model exists. It is plumbing, not a
//! model, and every page it produces says so.
//!
//! The aircraft flies on under the core dynamics until `takeover_unix_s` (by default the last
//! transmission, 00:19:37.443 UTC), then comes down at a signed distance along its ground track,
//! drawn from a normal distribution (`distance_nm`: by default mean 0 and s.d. 50 NM, deliberately
//! broad). The impact time is the takeover time plus that distance at the takeover ground speed.
//! It models no descent: the vertical velocity and mass are NaN (not computed), and so are the
//! impact energies. Bursts after the takeover find the aircraft down.
//!
//! Source: none. It resembles the "within some distance of the 7th arc" assumption behind
//! unpiloted end-of-flight analyses only in shape; that assumption is not adopted here, and the
//! End of flight module replaces this one.

use hypothesis::{Atmosphere, Descent, EpochState, FlightState, Hypothesis, Impact, Terminal, TerminalEpoch};
use serde::Deserialize;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Params {
    /// Unix seconds; a hand-off later than this takes over at once.
    takeover_unix_s: f64,
    distance_nm: Normal,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Normal {
    mean: f64,
    sd: f64,
}

struct ArcKernel {
    params: Params,
}

pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String> {
    let params: Params = params.clone().try_into().map_err(|e| format!("arc-kernel: {e}"))?;
    let Normal { mean, sd } = params.distance_nm;
    if !(params.takeover_unix_s.is_finite() && mean.is_finite() && sd >= 0.0) {
        return Err("arc-kernel: need a finite takeover time and distance mean, and sd >= 0".into());
    }
    Ok(Box::new(ArcKernel { params }))
}

impl Hypothesis for ArcKernel {
    fn terminal(&self) -> Option<&dyn Terminal> {
        Some(self)
    }
}

impl Terminal for ArcKernel {
    fn families(&self) -> Vec<String> {
        vec!["placeholder".into()]
    }

    fn latent_columns(&self) -> Vec<String> {
        vec!["distance_nm".into()]
    }

    fn takeover_time(&self, handoff: &FlightState, _uniform: &mut dyn FnMut() -> f64) -> (f64, f64) {
        (self.params.takeover_unix_s.max(handoff.unix_s), 0.0)
    }

    fn descend(
        &self,
        takeover: &FlightState,
        _atmosphere: &dyn Atmosphere,
        uniform: &mut dyn FnMut() -> f64,
        epochs: &[TerminalEpoch],
        _score: &dyn Fn(&[Option<EpochState>]) -> f64,
    ) -> Vec<Descent> {
        // Box-Muller: one standard normal from two uniforms on (0, 1).
        let (u1, u2) = (uniform(), uniform());
        let z = (-2.0 * u1.ln()).sqrt() * (std::f64::consts::TAU * u2).cos();
        let distance_nm = self.params.distance_nm.mean + self.params.distance_nm.sd * z;
        let (east, north) = (takeover.ground_velocity_east_mps, takeover.ground_velocity_north_mps);
        let speed_kt = east.hypot(north) / geo::M_PER_KT_S;
        let seconds = distance_nm / speed_kt * 3600.0;
        let (lat, lon) =
            geo::advance(takeover.latitude_deg, takeover.longitude_deg, 0.0, north / geo::M_PER_KT_S, east / geo::M_PER_KT_S, seconds);
        vec![Descent {
            impact: Impact {
                unix_s: takeover.unix_s + seconds.abs(),
                latitude_deg: lat,
                longitude_deg: lon,
                velocity_east_mps: east,
                velocity_north_mps: north,
                velocity_up_mps: f64::NAN,
                mass_kg: f64::NAN,
            },
            family: 0,
            at_epochs: vec![None; epochs.len()],
            latents: vec![distance_nm],
            log_q_correction: 0.0,
        }]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// With the normal draw at its mean (u2 = 1/4 makes the cosine zero), the impact lies 100 NM
    /// along a due-south track: checked with an independent haversine distance on a sphere.
    #[test]
    fn the_impact_lies_the_drawn_distance_along_the_track() {
        let table: toml::Value = toml::from_str("takeover_unix_s = 1000.0\ndistance_nm = { mean = 100.0, sd = 50.0 }").unwrap();
        let module = new(&table).unwrap();
        let terminal = module.terminal().unwrap();
        let state = FlightState {
            unix_s: 400.0,
            latitude_deg: -35.0,
            longitude_deg: 95.0,
            altitude_ft: 35_000.0,
            ground_velocity_east_mps: 0.0,
            ground_velocity_north_mps: -250.0,
            vertical_speed_mps: 0.0,
            mach: 0.8,
            true_air_speed_mps: 240.0,
            heading_deg: 180.0,
            wind_east_mps: 0.0,
            wind_north_mps: -10.0,
            mode: 2,
            mass_kg: f64::NAN,
            fuel_kg: f64::NAN,
            realised_flameout_unix_s: f64::NAN,
        };
        assert_eq!(terminal.takeover_time(&state, &mut || 0.5).0, 1000.0);
        let mut draws = [0.5, 0.25].into_iter();
        struct Still;
        impl Atmosphere for Still {
            fn at(&self, _: f64, _: f64, _: f64, _: f64) -> hypothesis::Air {
                unreachable!("the placeholder reads no weather")
            }
        }
        let later = [TerminalEpoch { id: "late".into(), unix_s: 2000.0 }];
        let descents = terminal.descend(&state, &Still, &mut || draws.next().unwrap(), &later, &|_| 0.0);
        let d = &descents[0];
        assert_eq!(d.latents, vec![100.0]);
        assert_eq!(d.at_epochs, vec![None]);
        let (a, b) = ((-35f64).to_radians(), d.impact.latitude_deg.to_radians());
        let dlon = (d.impact.longitude_deg - 95.0).to_radians();
        let h = ((b - a) / 2.0).sin().powi(2) + a.cos() * b.cos() * (dlon / 2.0).sin().powi(2);
        let haversine_nm = 2.0 * 3440.065 * h.sqrt().asin();
        assert!((haversine_nm - 100.0).abs() < 0.5, "{haversine_nm} NM");
        // 100 NM at 250 m/s (486 kt) is 741 s after the takeover state.
        assert!((d.impact.unix_s - 400.0 - 100.0 * 1852.0 / 250.0).abs() < 1e-6);
        assert!(d.impact.velocity_up_mps.is_nan() && d.impact.mass_kg.is_nan());
    }
}
