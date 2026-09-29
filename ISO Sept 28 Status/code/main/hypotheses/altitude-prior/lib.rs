//! Altitude prior: the aircraft was near a given flight level at 18:01:49 UTC.
//!
//! Davey et al. (2016) do not publish their initial altitude distribution; the base
//! estimate uses the manoeuvre range (uniform 25,000-43,000 ft in 1,000 ft levels) as a
//! diffuse substitute. Because air speed is Mach times the local speed of sound, the
//! initial altitude changes the reachable ranges before the first speed change. This
//! hypothesis replaces the level weights with a discretised Gaussian.

use hypothesis::{Hypothesis, PriorSpec};
use serde::Deserialize;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Params {
    mean_ft: f64,
    sd_ft: f64,
}

struct AltitudePrior {
    params: Params,
}

pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String> {
    let params: Params = params.clone().try_into().map_err(|e| format!("altitude-prior: {e}"))?;
    if !(params.sd_ft > 0.0) {
        return Err("altitude-prior: sd_ft must be positive".into());
    }
    Ok(Box::new(AltitudePrior { params }))
}

impl Hypothesis for AltitudePrior {
    fn adjust_prior(&self, prior: &mut PriorSpec) {
        let Params { mean_ft, sd_ft } = self.params;
        for (level, weight) in &mut prior.altitude_levels {
            *weight = (-0.5 * ((*level - mean_ft) / sd_ft).powi(2)).exp();
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn weights_peak_at_the_mean_and_fall_off_by_one_sd() {
        let mut prior = PriorSpec {
            unix_s: 0.0,
            latitude_deg: 0.0,
            longitude_deg: 0.0,
            position_sd_nm: 0.5,
            track_deg: 0.0,
            track_sd_deg: 1.0,
            mach_range: (0.73, 0.84),
            mach_gaussian: None,
            altitude_levels: (25..=43).map(|k| (f64::from(k) * 1000.0, 1.0)).collect(),
            mode_weights: [1.0; 5],
        };
        let table: toml::Value = toml::from_str("mean_ft = 35000.0\nsd_ft = 2000.0").unwrap();
        new(&table).unwrap().adjust_prior(&mut prior);
        let weight = |ft: f64| prior.altitude_levels.iter().find(|(l, _)| *l == ft).unwrap().1;
        assert_eq!(weight(35_000.0), 1.0);
        assert!((weight(37_000.0) - (-0.5f64).exp()).abs() < 1e-12);
        assert!(weight(25_000.0) < 1e-5);
    }
}
