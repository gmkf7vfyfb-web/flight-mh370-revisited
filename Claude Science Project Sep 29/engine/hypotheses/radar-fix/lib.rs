//! Radar fixes: primary-radar positions at fixed times, each scored as an isotropic Gaussian in
//! great-circle distance (NM), optionally mixed with a broad outlier component so a misread or
//! spurious plot cannot dominate. Used for the military returns after the continuous track ends
//! at 18:01:49: the sparse plots in the 18:03-18:15 gap and the last return at 18:22:12, which
//! Davey (2016, p. 21) used only qualitatively. Densities are normalised (per NM^2), so the
//! module adds the same constant to every trajectory family's evidence.

use hypothesis::{EpochView, Hypothesis, StateView};
use serde::Deserialize;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Fix {
    epoch: String,
    unix_s: f64,
    latitude_deg: f64,
    longitude_deg: f64,
    sd_nm: f64,
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Params {
    fixes: Vec<Fix>,
    /// Prior probability that a plot is unrelated to the aircraft's position (0 = none).
    #[serde(default)]
    outlier_fraction: f64,
    /// Standard deviation of the outlier component (NM).
    #[serde(default = "default_outlier_sd")]
    outlier_sd_nm: f64,
}

fn default_outlier_sd() -> f64 {
    50.0
}

struct RadarFix {
    params: Params,
}

pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String> {
    let params: Params = params.clone().try_into().map_err(|e| format!("radar-fix: {e}"))?;
    if params.fixes.is_empty() || !params.fixes.iter().all(|f| f.sd_nm > 0.0 && f.unix_s.is_finite()) {
        return Err("radar-fix: need at least one fix, each with positive sd_nm and finite unix_s".into());
    }
    if !(0.0..1.0).contains(&params.outlier_fraction) || !(params.outlier_sd_nm > 0.0) {
        return Err("radar-fix: outlier_fraction must be in [0, 1) and outlier_sd_nm positive".into());
    }
    Ok(Box::new(RadarFix { params }))
}

/// Great-circle distance on a sphere of 3440.065 NM (haversine).
fn distance_nm(lat1: f64, lon1: f64, lat2: f64, lon2: f64) -> f64 {
    let (p1, p2) = (lat1.to_radians(), lat2.to_radians());
    let (dp, dl) = (p2 - p1, (lon2 - lon1).to_radians());
    let a = (dp / 2.0).sin().powi(2) + p1.cos() * p2.cos() * (dl / 2.0).sin().powi(2);
    2.0 * 3440.065 * a.sqrt().min(1.0).asin()
}

fn log_gauss2(d: f64, sd: f64) -> f64 {
    -0.5 * (d / sd).powi(2) - (2.0 * std::f64::consts::PI * sd * sd).ln()
}

/// Log density of a plot at distance `d` from the aircraft: Gaussian, or a mixture with a broad
/// outlier component when `eps` > 0.
fn score(d: f64, sd: f64, eps: f64, outlier_sd: f64) -> f64 {
    let inlier = log_gauss2(d, sd);
    if eps == 0.0 {
        return inlier;
    }
    let (a, b) = ((1.0 - eps).ln() + inlier, eps.ln() + log_gauss2(d, outlier_sd));
    let m = a.max(b);
    m + ((a - m).exp() + (b - m).exp()).ln()
}

impl Hypothesis for RadarFix {
    fn observations(&self) -> Vec<String> {
        self.params.fixes.iter().map(|f| format!("radar:{}", f.epoch)).collect()
    }

    fn extra_epochs(&self) -> Vec<(String, f64)> {
        self.params.fixes.iter().map(|f| (f.epoch.clone(), f.unix_s)).collect()
    }

    fn epoch_log_likelihood(&self, epoch: &EpochView, state: &StateView) -> f64 {
        if epoch.satcom {
            return 0.0;
        }
        let Some(f) = self.params.fixes.iter().find(|f| f.epoch == epoch.id) else { return 0.0 };
        let d = distance_nm(state.latitude_deg, state.longitude_deg, f.latitude_deg, f.longitude_deg);
        score(d, f.sd_nm, self.params.outlier_fraction, self.params.outlier_sd_nm)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ten_nm_past_mekar_is_ten_nm_from_mekar() {
        let d = distance_nm(6.5038889, 96.4911111, 6.5779, 96.3410);
        assert!((d - 10.0).abs() < 0.05, "{d}");
    }

    #[test]
    fn an_outlier_mixture_is_bounded_below_by_its_broad_component() {
        let far = score(120.0, 3.0, 0.1, 50.0);
        assert!(far >= (0.1f64).ln() + log_gauss2(120.0, 50.0) - 1e-12);
        assert!((score(0.0, 3.0, 0.0, 50.0) - log_gauss2(0.0, 3.0)).abs() < 1e-15);
    }
}
