//! Initial Mach: the 18:01:49 Mach set point is Gaussian, as in Davey et al. (2016) Table 8.2
//! ("Control Mach, Gaussian s.d. 0.03"), rather than uniform on 0.73-0.84 as Ch. 4 states.
//!
//! Fig. 10.6 of the book shows prior mass up to Mach 0.87 at 18:02, which only a Gaussian
//! initial Mach can produce. The mean is not published; 0.82 is read from Fig. 10.6 and
//! was agreed with the project owner. Mach after a speed change is still uniform on
//! 0.73-0.84 (Ch. 7), unchanged.

use hypothesis::{Hypothesis, PriorSpec};
use serde::Deserialize;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Params {
    mean: f64,
    sd: f64,
}

struct InitialMach {
    params: Params,
}

pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String> {
    let params: Params = params.clone().try_into().map_err(|e| format!("initial-mach: {e}"))?;
    if !(params.sd > 0.0 && params.mean > 0.5 && params.mean < 1.0) {
        return Err("initial-mach: need 0.5 < mean < 1 and sd > 0".into());
    }
    Ok(Box::new(InitialMach { params }))
}

impl Hypothesis for InitialMach {
    fn adjust_prior(&self, prior: &mut PriorSpec) {
        prior.mach_gaussian = Some((self.params.mean, self.params.sd));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sets_the_published_gaussian_and_leaves_the_rest() {
        let base = PriorSpec {
            unix_s: 0.0,
            latitude_deg: 5.6,
            longitude_deg: 99.0,
            position_sd_nm: 0.5,
            track_deg: 295.66,
            track_sd_deg: 1.0,
            mach_range: (0.73, 0.84),
            mach_gaussian: None,
            altitude_levels: vec![(25_000.0, 1.0), (43_000.0, 1.0)],
            mode_weights: [1.0; 5],
        };
        let mut prior = base.clone();
        new(&toml::from_str("mean = 0.82\nsd = 0.03").unwrap()).unwrap().adjust_prior(&mut prior);
        assert_eq!(prior.mach_gaussian, Some((0.82, 0.03)));
        // Fig. 10.6 shows mass at Mach 0.87: 1.67 sd above the mean, ~5% of draws.
        let z: f64 = (0.87 - 0.82) / 0.03;
        assert!((z - 1.6667).abs() < 1e-3);
        prior.mach_gaussian = None;
        assert_eq!(prior, base);
    }
}
