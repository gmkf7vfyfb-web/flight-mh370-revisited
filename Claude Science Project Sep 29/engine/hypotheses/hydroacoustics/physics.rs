//! Closed-form physics the module can state exactly: the WGS84 geodesic to each station, arrival
//! time at a declared group speed, the energy-to-exposure reference relation, and the first
//! acoustic-mode cutoff. Nothing here is a propagation model; transmission loss is an input.

use geo::{WGS84_A_KM, WGS84_F};

/// Seawater density and sound speed used only in the reference-energy relation below. Both are
/// declared constants, not measurements; the propagation engine replaces them per path.
pub const RHO_SEAWATER_KG_M3: f64 = 1025.0;
pub const C_REFERENCE_M_S: f64 = 1500.0;

/// Geodesic on the WGS84 ellipsoid by Vincenty's inverse method. Returns (distance km, forward
/// azimuth at point 1 in degrees clockwise from north). Converges to well under a metre at
/// every geometry this module meets; it is not used near antipodal points, where it can fail, and
/// returns NaN there rather than a wrong answer. Checked against Karney's algorithm
/// (geographiclib 2.1) in the tests below.
pub fn geodesic_inverse(lat1: f64, lon1: f64, lat2: f64, lon2: f64) -> (f64, f64) {
    let a = WGS84_A_KM * 1000.0;
    let f = WGS84_F;
    let b = a * (1.0 - f);
    let l = (lon2 - lon1).to_radians();
    let u1 = ((1.0 - f) * lat1.to_radians().tan()).atan();
    let u2 = ((1.0 - f) * lat2.to_radians().tan()).atan();
    let (su1, cu1) = u1.sin_cos();
    let (su2, cu2) = u2.sin_cos();
    if lat1 == lat2 && lon1 == lon2 {
        return (0.0, 0.0);
    }
    let mut lambda = l;
    for _ in 0..200 {
        let (sl, cl) = lambda.sin_cos();
        let sin_sigma = ((cu2 * sl).powi(2) + (cu1 * su2 - su1 * cu2 * cl).powi(2)).sqrt();
        if sin_sigma == 0.0 {
            return (0.0, 0.0);
        }
        let cos_sigma = su1 * su2 + cu1 * cu2 * cl;
        let sigma = sin_sigma.atan2(cos_sigma);
        let sin_alpha = cu1 * cu2 * sl / sin_sigma;
        let cos2_alpha = 1.0 - sin_alpha * sin_alpha;
        let cos_2sm = if cos2_alpha != 0.0 { cos_sigma - 2.0 * su1 * su2 / cos2_alpha } else { 0.0 };
        let c = f / 16.0 * cos2_alpha * (4.0 + f * (4.0 - 3.0 * cos2_alpha));
        let prev = lambda;
        lambda = l + (1.0 - c) * f * sin_alpha
            * (sigma + c * sin_sigma * (cos_2sm + c * cos_sigma * (-1.0 + 2.0 * cos_2sm * cos_2sm)));
        if (lambda - prev).abs() < 1e-13 {
            let u_sq = cos2_alpha * (a * a - b * b) / (b * b);
            let aa = 1.0 + u_sq / 16384.0 * (4096.0 + u_sq * (-768.0 + u_sq * (320.0 - 175.0 * u_sq)));
            let bb = u_sq / 1024.0 * (256.0 + u_sq * (-128.0 + u_sq * (74.0 - 47.0 * u_sq)));
            let d_sigma = bb * sin_sigma
                * (cos_2sm + bb / 4.0
                    * (cos_sigma * (-1.0 + 2.0 * cos_2sm * cos_2sm)
                        - bb / 6.0 * cos_2sm * (-3.0 + 4.0 * sin_sigma * sin_sigma)
                            * (-3.0 + 4.0 * cos_2sm * cos_2sm)));
            let s = b * aa * (sigma - d_sigma);
            let (sl, cl) = lambda.sin_cos();
            let az1 = (cu2 * sl).atan2(cu1 * su2 - su1 * cu2 * cl).to_degrees();
            return (s / 1000.0, az1);
        }
    }
    (f64::NAN, f64::NAN)
}

/// Arrival at a station for a declared group speed with a standard deviation. Returns
/// (travel time s, standard deviation s), linearised in the speed: sd_t = d sd_c / c^2. The
/// impact-time uncertainty is not added here; each impact sample carries its own time.
pub fn travel_time_s(distance_km: f64, group_speed_km_s: f64, group_speed_sd_km_s: f64) -> (f64, f64) {
    let t = distance_km / group_speed_km_s;
    (t, distance_km * group_speed_sd_km_s / (group_speed_km_s * group_speed_km_s))
}

/// Pressure-squared exposure (Pa^2 s) at 1 m from a point source near the surface that radiates
/// `acoustic_energy_j` into the lower half-space: energy flux density E / (2 pi r0^2) times rho c.
/// The radiation pattern of a near-surface source (the Lloyd-mirror dipole) is NOT modelled here;
/// it is a declared alternative for the source model, not a constant to bury in this relation.
pub fn source_exposure_1m_pa2s(acoustic_energy_j: f64) -> f64 {
    RHO_SEAWATER_KG_M3 * C_REFERENCE_M_S * acoustic_energy_j / (2.0 * std::f64::consts::PI)
}

/// Received exposure (Pa^2 s) after a transmission loss in dB re 1 m. TL comes from the
/// propagation engine; NaN in gives NaN out, which is "not assessed".
pub fn received_exposure_pa2s(acoustic_energy_j: f64, transmission_loss_db: f64) -> f64 {
    source_exposure_1m_pa2s(acoustic_energy_j) * 10f64.powf(-transmission_loss_db / 10.0)
}

/// RMS pressure over a received signal duration. The duration is the RECEIVED duration, which
/// is never an estimate of the source duration or of energy_transfer_tau90_s.
pub fn rms_pressure_pa(exposure_pa2s: f64, received_duration_s: f64) -> f64 {
    (exposure_pa2s / received_duration_s).sqrt()
}

/// First acoustic-mode cutoff of a water layer of depth `h_m`: f_c = c / 4H (rigid bottom,
/// pressure-release surface). Below f_c the layer supports no propagating acoustic mode and the
/// acoustic-gravity branch applies.
pub fn mode_cutoff_hz(sound_speed_m_s: f64, h_m: f64) -> f64 {
    sound_speed_m_s / (4.0 * h_m)
}

/// Which side of the cutoff a source of duration `tau_s` falls on for the AGW band: impulsive
/// when its roll-off 1/tau lies above f_c. NaN tau or depth gives None, "not assessed".
pub fn agw_impulsive(tau_s: f64, sound_speed_m_s: f64, h_m: f64) -> Option<bool> {
    if !(tau_s.is_finite() && h_m.is_finite() && tau_s > 0.0 && h_m > 0.0) {
        return None;
    }
    Some(1.0 / tau_s > mode_cutoff_hz(sound_speed_m_s, h_m))
}

#[cfg(test)]
mod tests {
    use super::*;

    // Hand-computed fixtures: Karney's geodesic (geographiclib 2.1, Geodesic.WGS84.Inverse) from
    // (-34.9167, 92.0472) to the FDSN triad centroids in data/stations.csv.
    const SRC: (f64, f64) = (-34.9167, 92.0472);
    const H01W: (f64, f64) = (-34.890303, 114.142637);
    const H08S: (f64, f64) = (-7.639380, 72.483828);

    #[test]
    fn zero_range_has_zero_travel_time() {
        let (d, _) = geodesic_inverse(SRC.0, SRC.1, SRC.0, SRC.1);
        assert_eq!(d, 0.0);
        let (t, sd) = travel_time_s(d, 1.482, 0.006);
        assert_eq!((t, sd), (0.0, 0.0));
    }

    #[test]
    fn geodesic_matches_karney_to_a_metre() {
        let (d1, az1) = geodesic_inverse(SRC.0, SRC.1, H01W.0, H01W.1);
        let (d2, az2) = geodesic_inverse(SRC.0, SRC.1, H08S.0, H08S.1);
        assert!((d1 - 2_015.2833).abs() < 1e-3, "{d1}");
        assert!((d2 - 3_622.9940).abs() < 1e-3, "{d2}");
        assert!((az1 - 96.29274).abs() < 1e-4, "{az1}");
        assert!((az2 + 38.10045).abs() < 1e-4, "{az2}");
        let (_, back) = geodesic_inverse(H08S.0, H08S.1, SRC.0, SRC.1);
        assert!((back - 149.26776).abs() < 1e-4, "{back}");
    }

    /// The H01W/H08S scale test, ported: at 1.49 km/s the travel times are 22.54 and 40.53
    /// minutes. Re-derived for the FDSN coordinates, which move the archived 2,011 / 3,632 km by
    /// +4.3 / -9.0 km — the disagreement the brief warned of in the old configs.
    #[test]
    fn cape_leeuwin_and_diego_garcia_scale() {
        let (d1, _) = geodesic_inverse(SRC.0, SRC.1, H01W.0, H01W.1);
        let (d2, _) = geodesic_inverse(SRC.0, SRC.1, H08S.0, H08S.1);
        let (t1, _) = travel_time_s(d1, 1.49, 0.0);
        let (t2, _) = travel_time_s(d2, 1.49, 0.0);
        assert!((t1 / 60.0 - 22.54).abs() < 0.01, "{}", t1 / 60.0);
        assert!((t2 / 60.0 - 40.53).abs() < 0.01, "{}", t2 / 60.0);
    }

    #[test]
    fn energy_times_four_gives_pressure_times_two() {
        let e1 = received_exposure_pa2s(1.0e5, 90.0);
        let e4 = received_exposure_pa2s(4.0e5, 90.0);
        let ratio = rms_pressure_pa(e4, 10.0) / rms_pressure_pa(e1, 10.0);
        assert!((ratio - 2.0).abs() < 1e-12);
    }

    /// Hand computation: rho c / 2 pi = 1,537,500 / 6.2831853 = 244,700.7 Pa^2 s per joule at
    /// 1 m; after 100 dB that is 2.447007e-5 Pa^2 s per joule.
    #[test]
    fn reference_exposure_hand_value() {
        assert!((source_exposure_1m_pa2s(1.0) - 244_700.7).abs() < 0.1);
        assert!((received_exposure_pa2s(1.0, 100.0) - 2.447_007e-5).abs() < 1e-11);
        assert!(received_exposure_pa2s(1.0, f64::NAN).is_nan());
    }

    #[test]
    fn mode_cutoff_matches_brief_table() {
        for (h, period) in [(3000.0, 8.0), (4000.0, 10.667), (5000.0, 13.333), (6000.0, 16.0)] {
            assert!((1.0 / mode_cutoff_hz(1500.0, h) - period).abs() < 1e-3);
        }
        assert_eq!(agw_impulsive(1.0, 1500.0, 4000.0), Some(true));
        assert_eq!(agw_impulsive(20.0, 1500.0, 4000.0), Some(false));
        assert_eq!(agw_impulsive(f64::NAN, 1500.0, 4000.0), None);
        assert_eq!(agw_impulsive(1.0, 1500.0, f64::NAN), None);
    }
}
