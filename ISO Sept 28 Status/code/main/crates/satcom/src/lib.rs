//! Inmarsat Classic Aero measurement model (Davey et al. 2016, ch. 5).
//!
//! BTO: round-trip delay GES -> satellite -> aircraft minus the fixed calibration,
//! Gaussian error with per-message SD. BFO: uplink/downlink Doppler, the aircraft's
//! own Doppler pre-compensation (surface position, nominal satellite at 64.5E),
//! the tabulated satellite + EAFC term, and an unknown constant bias that is
//! marginalised with a scalar Kalman filter (Rao-Blackwellisation, sec. 8.1).

use geo::{lla_to_ecef, local_basis, Vec3, KM_PER_FT, KM_S_PER_KT};
use std::path::Path;

pub const SPEED_OF_LIGHT_KM_S: f64 = 299_792.458;
pub const UPLINK_HZ: f64 = 1_646_652_500.0;
pub const DOWNLINK_HZ: f64 = 3_615_152_500.0;
/// Perth ground earth station, ECEF km.
pub const PERTH_GES_KM: Vec3 = Vec3::new(-2_368.8, 4_881.1, -3_342.0);
/// Nominal satellite assumed by the aircraft's Doppler compensation:
/// 64.5E on the equator, 422 km above the 35,788.12 km nominal altitude.
pub const NOMINAL_SATELLITE_LON_DEG: f64 = 64.5;
pub const NOMINAL_SATELLITE_HEIGHT_KM: f64 = 36_210.12;
/// T_nom (499,962 us) minus the R1200 channel term (4,283 us).
/// Davey Eq. 5.3 prints the channel term with the opposite sign; only this
/// sign reproduces logged BTOs at known aircraft positions (Ashton et al. 2015
/// report the equivalent single bias of -495,679 us).
pub const BTO_FIXED_OFFSET_US: f64 = 499_962.0 - 4_283.0;

/// One logged SATCOM burst (or C-channel cluster mean) with the satellite state at its time.
#[derive(Debug, Clone)]
pub struct Epoch {
    pub id: String,
    /// The time the cruise filter uses: the log time truncated to the second, as the base
    /// estimate always has (`time_utc`).
    pub unix_s: f64,
    /// The SITA log time to the millisecond (`logged_utc`); `unix_s` for C-channel means. The
    /// end-of-flight stage uses it: in a steep descent the BFO moves ~20 Hz per second.
    pub logged_unix_s: f64,
    pub bto_us: Option<f64>,
    pub bto_sd_us: f64,
    pub bfo_hz: Option<f64>,
    pub bfo_sd_hz: f64,
    /// Whether the cruise measurement model applies to this burst's BTO and BFO (`cruise`).
    /// The 00:19 BFOs were sent during the SDU start-up and are for the end-of-flight stage.
    pub cruise_bto: bool,
    pub cruise_bfo: bool,
    /// Events logged with this burst (`events`), e.g. "logon".
    pub events: Vec<String>,
    /// Satellite oscillator translation + ground-station EAFC terms (Hz).
    pub satellite_afc_hz: f64,
    pub satellite_km: Vec3,
    pub satellite_velocity_km_s: Vec3,
}

impl Epoch {
    /// Observation IDs this burst provides: `<id>.bto` and `<id>.bfo` where measured, and
    /// `<id>.<event>` for each event (e.g. `m0019a.logon`). Each may be used once per run.
    pub fn observations(&self) -> Vec<String> {
        let measured = [("bto", self.bto_us.is_some()), ("bfo", self.bfo_hz.is_some())];
        let quantities = measured.into_iter().filter(|(_, present)| *present).map(|(q, _)| q);
        quantities.chain(self.events.iter().map(String::as_str)).map(|q| format!("{}.{q}", self.id)).collect()
    }

    /// The IDs the cruise filter consumes from this burst when it filters it.
    pub fn cruise_observations(&self, use_bfo: bool) -> Vec<String> {
        let mut ids = Vec::new();
        if self.cruise_bto && self.bto_us.is_some() {
            ids.push(format!("{}.bto", self.id));
        }
        if use_bfo && self.cruise_bfo && self.bfo_hz.is_some() {
            ids.push(format!("{}.bfo", self.id));
        }
        ids
    }
}

pub fn bto_us(satellite_km: Vec3, lat: f64, lon: f64, alt_ft: f64) -> f64 {
    let aircraft = lla_to_ecef(lat, lon, alt_ft * KM_PER_FT);
    let path_km = (satellite_km - aircraft).norm() + (satellite_km - PERTH_GES_KM).norm();
    2.0 * path_km / SPEED_OF_LIGHT_KM_S * 1e6 - BTO_FIXED_OFFSET_US
}

/// Predicted BFO excluding the unknown bias. Velocities: north/east in knots, vertical in ft/min.
pub fn bfo_without_bias_hz(epoch: &Epoch, lat: f64, lon: f64, alt_ft: f64, v_north_kt: f64, v_east_kt: f64, v_up_fpm: f64) -> f64 {
    let (north, east, up) = local_basis(lat, lon);
    let horizontal = north * (v_north_kt * KM_S_PER_KT) + east * (v_east_kt * KM_S_PER_KT);
    let velocity = horizontal + up * (v_up_fpm * KM_PER_FT / 60.0);
    let aircraft = lla_to_ecef(lat, lon, alt_ft * KM_PER_FT);

    let to_satellite = (epoch.satellite_km - aircraft).unit();
    let uplink = -UPLINK_HZ / SPEED_OF_LIGHT_KM_S * (epoch.satellite_velocity_km_s - velocity).dot(to_satellite);
    let ges_to_satellite = (epoch.satellite_km - PERTH_GES_KM).unit();
    let downlink = -DOWNLINK_HZ / SPEED_OF_LIGHT_KM_S * epoch.satellite_velocity_km_s.dot(ges_to_satellite);

    let nominal = lla_to_ecef(0.0, NOMINAL_SATELLITE_LON_DEG, NOMINAL_SATELLITE_HEIGHT_KM);
    let from_nominal = (lla_to_ecef(lat, lon, 0.0) - nominal).unit();
    let compensation = UPLINK_HZ / SPEED_OF_LIGHT_KM_S * horizontal.dot(from_nominal);

    uplink + downlink + compensation + epoch.satellite_afc_hz
}

/// Longitude east of the satellite where the predicted BTO equals `bto` at `lat` (for plotting arcs).
pub fn arc_longitude(satellite_km: Vec3, lat: f64, alt_ft: f64, bto: f64) -> Option<f64> {
    let (mut west, mut east) = (NOMINAL_SATELLITE_LON_DEG + 0.5, 150.0);
    let f = |lon: f64| bto_us(satellite_km, lat, lon, alt_ft) - bto;
    if f(west) > 0.0 || f(east) < 0.0 {
        return None;
    }
    for _ in 0..60 {
        let mid = 0.5 * (west + east);
        if f(mid) < 0.0 { west = mid } else { east = mid }
    }
    Some(0.5 * (west + east))
}

/// Gaussian posterior of the constant BFO bias for one trajectory.
#[derive(Debug, Clone, Copy)]
pub struct BfoBias {
    pub mean_hz: f64,
    pub variance_hz2: f64,
}

impl BfoBias {
    /// Marginal log-likelihood of `measured` given the bias-free prediction, then the Kalman update.
    pub fn update(&mut self, predicted_without_bias: f64, measured: f64, noise_sd: f64) -> f64 {
        let innovation = measured - predicted_without_bias - self.mean_hz;
        let s = self.variance_hz2 + noise_sd * noise_sd;
        let gain = self.variance_hz2 / s;
        self.mean_hz += gain * innovation;
        self.variance_hz2 *= 1.0 - gain;
        -0.5 * (innovation * innovation / s + (std::f64::consts::TAU * s).ln())
    }
}

/// A measurement alternative for the 00:19 BFOs. Both were sent during the satellite data unit's
/// start-up: the first by the R600 log-on request, the second by the R1200 acknowledge. Whether
/// the cruise model holds for them is questioned, so each alternative is scored separately.
#[derive(Debug, Clone, PartialEq)]
pub enum FinalBfoModel {
    /// The cruise model: measurement noise only.
    NoOffset,
    /// A start-up offset added to each measured BFO: the second's uniform on `second_hz`, the
    /// first's larger by a uniform `first_minus_second_hz` (one shared start-up event),
    /// integrated by Gauss-Legendre quadrature with `points` nodes per range.
    StartupOffset { second_hz: [f64; 2], first_minus_second_hz: [f64; 2], points: [usize; 2] },
    /// The cruise model with this noise s.d. in place of the tabulated one.
    Inflated { sd_hz: f64 },
}

/// The joint likelihood of the selected 00:19 BFOs under one [`FinalBfoModel`].
#[derive(Debug, Clone)]
pub struct FinalBfo {
    /// (offset of the first and second BFO, quadrature weight); weights sum to one.
    nodes: Vec<([f64; 2], f64)>,
    sd_hz: Option<f64>,
}

impl FinalBfo {
    pub fn new(model: &FinalBfoModel) -> Result<Self, String> {
        match model {
            FinalBfoModel::NoOffset => Ok(FinalBfo { nodes: vec![([0.0, 0.0], 1.0)], sd_hz: None }),
            FinalBfoModel::Inflated { sd_hz } if *sd_hz > 0.0 && sd_hz.is_finite() => {
                Ok(FinalBfo { nodes: vec![([0.0, 0.0], 1.0)], sd_hz: Some(*sd_hz) })
            }
            FinalBfoModel::Inflated { sd_hz } => Err(format!("inflated BFO s.d. {sd_hz} must be positive")),
            FinalBfoModel::StartupOffset { second_hz, first_minus_second_hz, points } => {
                let second = uniform_quadrature(*second_hz, points[0])?;
                let decay = uniform_quadrature(*first_minus_second_hz, points[1])?;
                let nodes = second.iter().flat_map(|&(b, wb)| decay.iter().map(move |&(d, wd)| ([b + d, b], wb * wd))).collect();
                Ok(FinalBfo { nodes, sd_hz: None })
            }
        }
    }

    /// ln p(selected BFOs). `contacts` holds (measured, predicted without bias, noise s.d.) for
    /// the first and second burst, `None` where the burst's BFO is not used. One bias, with the
    /// trajectory's posterior `bias` from the cruise BFOs, is shared by both; the offsets are
    /// marginalised over the model's prior.
    pub fn log_likelihood(&self, bias: BfoBias, contacts: [Option<(f64, f64, f64)>; 2]) -> f64 {
        if contacts.iter().all(Option::is_none) {
            return 0.0;
        }
        let (mut max, mut sum) = (f64::NEG_INFINITY, 0.0);
        for (offsets, weight) in &self.nodes {
            let mut state = bias;
            let mut value = weight.ln();
            for (contact, offset) in contacts.iter().zip(offsets) {
                if let Some((measured, predicted, sd)) = contact {
                    value += state.update(*predicted, measured - offset, self.sd_hz.unwrap_or(*sd));
                }
            }
            if value > max {
                sum = sum * (max - value).exp() + 1.0;
                max = value;
            } else {
                sum += (value - max).exp();
            }
        }
        max + sum.ln()
    }
}

/// Gauss-Legendre nodes for the mean over a uniform range; the weights sum to one. A range of
/// zero width is a fixed value.
fn uniform_quadrature(range: [f64; 2], points: usize) -> Result<Vec<(f64, f64)>, String> {
    if !(range[0].is_finite() && range[1].is_finite() && range[0] <= range[1] && (2..=256).contains(&points)) {
        return Err(format!("start-up offset range {range:?} with {points} points: need lo <= hi and 2-256 points"));
    }
    if range[0] == range[1] {
        return Ok(vec![(range[0], 1.0)]);
    }
    let mut nodes = Vec::with_capacity(points);
    for i in 0..points {
        // Newton iteration from the classic initial guess for the i-th root of P_n.
        let mut x = (std::f64::consts::PI * (i as f64 + 0.75) / (points as f64 + 0.5)).cos();
        let mut derivative = 1.0;
        for _ in 0..100 {
            let (mut previous, mut current) = (1.0, x);
            for k in 2..=points {
                let next = ((2 * k - 1) as f64 * x * current - (k - 1) as f64 * previous) / k as f64;
                previous = current;
                current = next;
            }
            derivative = points as f64 * (x * current - previous) / (x * x - 1.0);
            let delta = current / derivative;
            x -= delta;
            if delta.abs() < 1e-15 {
                break;
            }
        }
        let value = 0.5 * (range[0] + range[1]) + 0.5 * x * (range[1] - range[0]);
        nodes.push((value, 1.0 / ((1.0 - x * x) * derivative * derivative)));
    }
    let total: f64 = nodes.iter().map(|(_, w)| w).sum();
    Ok(nodes.into_iter().map(|(v, w)| (v, w / total)).collect())
}

/// Signed distance (NM) from the arc on which the predicted BTO equals `bto`: the BTO residual
/// at this position over the local BTO gradient. Positive beyond the arc, away from the
/// sub-satellite point.
pub fn arc_distance_nm(satellite_km: Vec3, lat: f64, lon: f64, alt_ft: f64, bto: f64) -> f64 {
    let here = bto_us(satellite_km, lat, lon, alt_ft);
    // One nautical mile north and east (3,600 kt for one second).
    let (lat_n, lon_n) = geo::advance(lat, lon, alt_ft, 3600.0, 0.0, 1.0);
    let (lat_e, lon_e) = geo::advance(lat, lon, alt_ft, 0.0, 3600.0, 1.0);
    let gradient = (bto_us(satellite_km, lat_n, lon_n, alt_ft) - here).hypot(bto_us(satellite_km, lat_e, lon_e, alt_ft) - here);
    (here - bto) / gradient
}

pub fn gaussian_log_likelihood(residual: f64, sd: f64) -> f64 {
    -0.5 * ((residual / sd).powi(2) + (std::f64::consts::TAU * sd * sd).ln())
}

/// Join the observation and satellite-ephemeris tables on `epoch_id`, in time order.
pub fn load_epochs(observations: &Path, ephemeris: &Path) -> Result<Vec<Epoch>, String> {
    let ephemeris = read_csv(ephemeris)?;
    let mut epochs = Vec::new();
    for row in read_csv(observations)? {
        let id = row.get("epoch_id")?.to_string();
        let sat = ephemeris
            .iter()
            .find(|r| r.get("epoch_id").ok() == Some(id.as_str()))
            .ok_or_else(|| format!("no ephemeris for epoch {id}"))?;
        let v = |r: &Row, k: &str| -> Result<f64, String> { r.number(k)?.ok_or_else(|| format!("{id}: missing {k}")) };
        let unix_s = parse_utc(row.get("time_utc")?)?;
        let logged = row.get("logged_utc")?.trim();
        let (bto_us, bfo_hz) = (row.number("bto_us")?, row.number("bfo_hz")?);
        let cruise: Vec<&str> = row.get("cruise")?.split_whitespace().collect();
        for quantity in &cruise {
            let present = match *quantity {
                "bto" => bto_us.is_some(),
                "bfo" => bfo_hz.is_some(),
                other => return Err(format!("{id}: unknown cruise quantity {other}")),
            };
            if !present {
                return Err(format!("{id}: cruise lists {quantity}, which was not measured"));
            }
        }
        epochs.push(Epoch {
            unix_s,
            logged_unix_s: if logged.is_empty() { unix_s } else { parse_utc(logged)? },
            bto_us,
            bto_sd_us: row.number("bto_sd_us")?.unwrap_or(f64::NAN),
            bfo_hz,
            bfo_sd_hz: row.number("bfo_sd_hz")?.unwrap_or(f64::NAN),
            cruise_bto: cruise.contains(&"bto"),
            cruise_bfo: cruise.contains(&"bfo"),
            events: row.get("events")?.split_whitespace().map(str::to_string).collect(),
            satellite_afc_hz: v(&row, "satellite_afc_hz")?,
            satellite_km: Vec3::new(v(sat, "x_km")?, v(sat, "y_km")?, v(sat, "z_km")?),
            satellite_velocity_km_s: Vec3::new(v(sat, "vx_km_s")?, v(sat, "vy_km_s")?, v(sat, "vz_km_s")?),
            id,
        });
    }
    epochs.sort_by(|a, b| a.unix_s.total_cmp(&b.unix_s));
    Ok(epochs)
}

struct Row {
    header: std::rc::Rc<Vec<String>>,
    cells: Vec<String>,
}

impl Row {
    fn get(&self, key: &str) -> Result<&str, String> {
        let i = self.header.iter().position(|h| h == key).ok_or_else(|| format!("missing column {key}"))?;
        Ok(self.cells.get(i).map(String::as_str).unwrap_or(""))
    }
    fn number(&self, key: &str) -> Result<Option<f64>, String> {
        let text = self.get(key)?.trim();
        if text.is_empty() {
            return Ok(None);
        }
        text.parse().map(Some).map_err(|_| format!("{key}: not a number: {text}"))
    }
}

fn read_csv(path: &Path) -> Result<Vec<Row>, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
    let mut lines = text.lines().filter(|l| !l.trim().is_empty());
    let header = std::rc::Rc::new(lines.next().ok_or("empty csv")?.split(',').map(str::to_string).collect::<Vec<_>>());
    Ok(lines
        .map(|l| Row { header: header.clone(), cells: l.split(',').map(str::to_string).collect() })
        .collect())
}

/// Parse `YYYY-MM-DDTHH:MM:SS[.fff]Z` to Unix seconds.
pub fn parse_utc(text: &str) -> Result<f64, String> {
    let bad = || format!("bad UTC time {text}");
    let t = text.trim().trim_end_matches('Z');
    let (date, time) = t.split_once('T').ok_or_else(bad)?;
    let d: Vec<i64> = date.split('-').map(|x| x.parse().map_err(|_| bad())).collect::<Result<_, _>>()?;
    let h: Vec<f64> = time.split(':').map(|x| x.parse().map_err(|_| bad())).collect::<Result<_, _>>()?;
    if d.len() != 3 || h.len() != 3 {
        return Err(bad());
    }
    // Days from civil (proleptic Gregorian), Howard Hinnant's algorithm.
    let (y, m) = if d[1] <= 2 { (d[0] - 1, d[1] + 9) } else { (d[0], d[1] - 3) };
    let era = y.div_euclid(400);
    let yoe = y - era * 400;
    let doy = (153 * m + 2) / 5 + d[2] - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    let days = era * 146_097 + doe - 719_468;
    Ok(days as f64 * 86_400.0 + h[0] * 3600.0 + h[1] * 60.0 + h[2])
}

#[cfg(test)]
mod tests {
    use super::*;

    fn fixture_epoch() -> Epoch {
        Epoch {
            id: "fixture".into(),
            unix_s: 0.0,
            logged_unix_s: 0.0,
            bto_us: None,
            bto_sd_us: 29.0,
            bfo_hz: None,
            bfo_sd_hz: 7.0,
            cruise_bto: true,
            cruise_bfo: true,
            events: Vec::new(),
            satellite_afc_hz: -18.075_833_333_333,
            satellite_km: Vec3::new(18_161.906_97, 38_060.473_36, 1_029.903_202),
            satellite_velocity_km_s: Vec3::new(0.002_195, -0.000_728, -0.045_877),
        }
    }

    /// Values from an independent scalar Python implementation of the same equations.
    #[test]
    fn bto_and_bfo_match_independent_fixture() {
        let e = fixture_epoch();
        let cases = [
            (-10.0, 85.0, 25_000.0, -450.0, 50.0, 0.0, 9_151.491_113_446_828, 13.952_695_799_684),
            (-25.0, 95.0, 35_000.0, -430.0, 80.0, 500.0, 16_292.998_083_343_264, 39.600_796_781_578),
            (-40.0, 105.0, 43_000.0, -410.0, 110.0, -500.0, 25_852.164_284_276_834, 39.788_037_143_149),
        ];
        for (lat, lon, alt, vn, ve, vu, bto, bfo) in cases {
            assert!((bto_us(e.satellite_km, lat, lon, alt) - bto).abs() < 1e-6);
            assert!((bfo_without_bias_hz(&e, lat, lon, alt, vn, ve, vu) - bfo).abs() < 1e-6);
        }
    }

    #[test]
    fn bias_filter_is_exact_gaussian_marginal() {
        // With zero prior variance the marginal reduces to the plain Gaussian.
        let mut b = BfoBias { mean_hz: 150.0, variance_hz2: 0.0 };
        let ll = b.update(100.0, 257.0, 7.0);
        assert!((ll - gaussian_log_likelihood(7.0, 7.0)).abs() < 1e-12);
        // Two updates shrink the variance as 1/(1/P + 2/R).
        let mut b = BfoBias { mean_hz: 150.0, variance_hz2: 625.0 };
        b.update(0.0, 150.0, 7.0);
        b.update(0.0, 150.0, 7.0);
        assert!((b.variance_hz2 - 1.0 / (1.0 / 625.0 + 2.0 / 49.0)).abs() < 1e-9);
    }

    #[test]
    fn final_bfos_share_one_bias() {
        // Two contacts, bias N(150, 4), noise s.d. 3 and 5: residuals r = (2, -3) and covariance
        // C = [[13, 4], [4, 29]] (det 361, r' C^-1 r = 281/361), solved by hand.
        let model = FinalBfo::new(&FinalBfoModel::NoOffset).unwrap();
        let bias = BfoBias { mean_hz: 150.0, variance_hz2: 4.0 };
        let both = model.log_likelihood(bias, [Some((182.0, 30.0, 3.0)), Some((-2.0, -149.0, 5.0))]);
        let expected = -std::f64::consts::TAU.ln() - 0.5 * 361f64.ln() - 0.5 * 281.0 / 361.0;
        assert!((both - expected).abs() < 1e-12, "{both} vs {expected}");
        assert_eq!(model.log_likelihood(bias, [None, None]), 0.0);
    }

    #[test]
    fn startup_offset_integrates_its_uniform_prior() {
        // The quadrature is exact for x^4 on [0, 1] (mean 1/5).
        let nodes = uniform_quadrature([0.0, 1.0], 16).unwrap();
        assert!((nodes.iter().map(|(x, w)| w * x.powi(4)).sum::<f64>() - 0.2).abs() < 1e-13);
        // A contact whose innovation sits mid-way in a 113 Hz uniform offset range, more than
        // 7 predictive s.d. from either end: the marginal density is 1/113.
        let model = FinalBfoModel::StartupOffset { second_hz: [17.0, 130.0], first_minus_second_hz: [0.0, 6.0], points: [64, 16] };
        let bias = BfoBias { mean_hz: 150.0, variance_hz2: 4.0 };
        let second = Some((-2.0, -225.5, 7.0));
        let value = FinalBfo::new(&model).unwrap().log_likelihood(bias, [None, second]);
        assert!((value + 113f64.ln()).abs() < 1e-9, "{value}");
    }

    #[test]
    fn utc_parser() {
        assert_eq!(parse_utc("2014-03-07T18:01:49Z").unwrap(), 1_394_215_309.0);
    }
}
