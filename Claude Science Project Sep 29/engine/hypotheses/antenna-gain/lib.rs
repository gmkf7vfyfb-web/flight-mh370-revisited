//! Antenna gain: the received power of the hourly R1200 log-on acknowledgements carries the
//! gain of 9M-MRO's satellite antenna toward the satellite, which depends on the aircraft's
//! attitude. BTO and BFO do not carry this directional information.
//!
//! PARKED (Pete Large, 28 Sep 2026). The module is set up and tested but not integrated, and must
//! not be run at full scale or quoted as evidence. It stays parked until the estimator runs stably
//! and convergently to impact; Pete then decides. Three reasons:
//! - the earlier held-out tests could not tell the two precompensation endpoints apart (below);
//! - the prediction needs attitude state the core does not expose yet (heading, bank, vertical
//!   speed), and the common calibration offset needs per-particle state (see `core_requests`);
//! - the gain surface is a reconstruction from a published pattern, not the commissioned
//!   9M-MRO installation.
//!
//! # Data
//!
//! Received power (dBm) at the Perth GES, from the released unredacted SITA log
//! (`SITA-35200217-08Mar2014.xlsx`, sha256 b0ccbfb0..., in `data/external/satcom/`), sheet
//! "SU Log", column "Rx Power (dBm)". All five are "Log-on/Log-off Acknowledge" bursts on
//! IOR-R1200-0-36ED, the R-channel assigned at the 18:25:27 log-on, whose initial R-channel EIRP
//! was 10.5 dBW ("AES Process" sheet). Observation IDs are `rxpower:<epoch>` (the runner's
//! `<source>:<item>` form: received power is not in the SATCOM table). While the module is
//! parked it keeps the five values here; un-parking moves them into the SATCOM table
//! (`core_requests`).
//!
//! | epoch | log time (UTC) | SU Log row | dBm    |
//! |-------|----------------|------------|--------|
//! | m1941 | 19:41:02.906   | 7126       | -54.54 |
//! | m2041 | 20:41:04.904   | 7128       | -55.52 |
//! | m2141 | 21:41:26.905   | 7130       | -54.11 |
//! | m2241 | 22:41:21.906   | 7132       | -53.02 |
//! | m0011 | 00:10:59.928   | 7187       | -53.27 |
//!
//! Not used:
//! - 18:25:27-18:28:14: thirteen R600, R1200 and T1200 bursts at -52.3 to -55.3 dBm, just after
//!   the SDU restart. Their power calibration after a restart is unknown, and the aircraft may
//!   have been turning.
//! - The 18:39 and 23:14 call attempts (channel 21000): closed-loop power control (the GES
//!   applied 4 and 6 adjustments; power falls about 10 dB within each call), no calibration.
//! - 00:19:29 (R600, -50.95) and 00:19:37 (R1200, -53.65): end of flight. They need the
//!   descent attitude, the R600-R1200 offset, the HPA output limit and the restart calibration.
//! - C/No: the same carrier power over a noise density; using both would count it twice.
//!
//! # Prediction
//!
//! For a burst with requested EIRP E = 10.5 dBW, the AES radiates E + b (G - G_ref), where G is
//! the antenna gain toward the satellite (dBic) and G_ref = 25.5 - 16.02 + 2.68 = 12.16 dBic is
//! the gain the HPA setting assumes (40 W HPA, 2.68 dB cable loss, 25.5 dBW design contour).
//! b = 0 is full precompensation: the AES corrects its HPA output for the steered-beam gain, so
//! the power carries no attitude information. b = 1 is none: the power follows the gain.
//! First-order EIRP control (network-assigned EIRP, HPA commands) is documented. A second-order
//! correction from the instantaneous steered-beam gain is not documented either way, so the two
//! endpoints are separate conditional runs (`precompensation = "full" | "none"`), never mixed.
//!
//! The received power is Large's (2019) link budget (workbook "Feb 21 Copy of Angles Test
//! Reduced Size Consolidated Final CNo and Doppler(AutoRecovered) (version 1).xlsx", sheet DATA,
//! columns DE to EP; CC BY 4.0, huggingface.co/datasets/peteabiome/mh370-dissertation-spreadsheets):
//!   P = EIRP + FSL(0.1820618 m, aircraft-satellite) + G/T(el) + 27.5
//!       + FSL(0.0832757 m, satellite-GES) + 300 + offset,
//!   FSL(l, R) = 20 log10(l / (4 pi R)),  G/T(el) = -11.5 + 0.01396 el + 1.535e-4 el^2,
//! with el the aircraft's elevation angle from the law of cosines on the ranges. G/T + 27.5 dB is
//! the satellite's L-band receive gain, 18.5 dBi at nadir (Large 2019, printed p. 118). The
//! 300 dB is the transponder, horn and GES antenna gains (about 200 dB) plus about 100 dB for the
//! GES receive chain and fixed losses, which Large fitted by least squares to 3,239 received
//! powers of 7 March 2014, MH371 included (printed pp. 119-120). The satellite comes from the
//! core's ephemeris file (read by path); the Perth GES is Large's [-2368.841, 4881.08, -3342.092] km.
//!
//! The power depends on the path through G and, very weakly, through the ranges: at these
//! epochs P changes by under 0.001 dB per km of range, so given BTO (range s.d. about 5 km) the
//! power carries no usable range information and does not count BTO twice.
//!
//! The gain G comes from `gain-aircraft-coordinates.csv` (built by `prepare/build_gain_table.py`):
//! Large (2019), "GAIN IN AC COORDS TO 68 EL 360 AZ.xlsx", CC BY 4.0 (same dataset). Large
//! digitised the peak-gain-versus-scan-angle curve of the Ball AIRLINK phased array (Westfeldt &
//! Konrad 1992, Fig. 8; 1 deg, 0.2 dB; digitisation s.d. 0.5 dB) and rotated it to two arrays
//! tilted 45 deg either side of the crown (printed pp. 93-95). The table reproduces that
//! construction to 0.04 dB RMS (0.29 dB at worst). Azimuth is clockwise from the nose, elevation
//! above the wing plane; the satellite line of sight is rotated into aircraft axes (forward,
//! right, down) by the aerospace yaw-pitch-roll convention and the table is read bilinearly.
//!
//! Attitude, until the core exposes it (`core_requests`). Over the directions southbound paths
//! see (satellite 24-164 deg right of the nose, 40-56 deg up) the gain spans 11.6-14.5 dBic, and
//! the table's digitised ripples make it steep in places:
//! - heading: the ground track. The true air heading differs by the drift angle (a few degrees;
//!   more in the westerlies south of 25 S); 3-8 deg of drift moves the predicted gain by a median
//!   0.2-0.45 dB and by up to 0.9 dB.
//! - pitch: `pitch_deg` for every particle (0: level flight, as in Large 2019). 3 deg of pitch
//!   moves the gain by up to 0.8 dB.
//! - roll: zero. The core flies its turns at 15 deg of bank, so a particle mid-turn at an epoch
//!   would see the satellite up to 15 deg higher or lower on the wing plane.
//!
//! # Likelihood
//!
//! Gaussian in dB, independent between epochs, s.d. `sd_db` = 1.72 dB: the blocked
//! no-precompensation RMSE of the earlier recreation (below), not tuned to MH371 truth. It is
//! a density of the observed dBm under either endpoint, so the two runs' evidences compare.
//!
//! The receive-chain calibration is common to the five bursts (one channel, one GES, one log-on
//! session), so its error is one offset shared by all epochs. The hook API sees one epoch of one
//! particle at a time, so the module can only fix it (`offset_db`). A fixed offset confounds the
//! endpoints with the calibration: G - G_ref averages about +1 dB, and so does the link model's
//! under-prediction on 7 March, so without an offset term the "none" endpoint wins by absorbing
//! a bias. Recomputed from the earlier MH371 inputs (six bursts, predictions frozen at the ACARS
//! geometry; no positions read here): ln L(none) - ln L(full) = +2.34 with no offset (those runs
//! reported about +2.45), +1.46 with a free common offset, and -0.23 with a free offset once the
//! 02:00 burst is dropped. The earlier preference for "none" thus rests on the calibration and on
//! one burst. That is why the module asks for per-particle module state (`core_requests`, the
//! fourth): with it the offset is marginalised by a Kalman update per particle, as the core does
//! for the BFO bias, instead of being fixed.
//!
//! # Earlier results (carried forward, not re-derived)
//!
//! From the recreation of Large (2019) (v01 `.sources/large-2019-antenna-gain/README.md`):
//! - Held-out comparison, full precompensation versus none: mean log-density difference +0.116
//!   per point in favour of none, 95% interval [-0.194, +0.462], sign-flip p = 0.536. A
//!   forward-only check reversed the sign. The endpoints therefore stay separate, with no prior
//!   weight between them.
//! - The event-level s.d. of 1.72 dB above.
//! - The gain surface is an uncommissioned first pass: not verified as the installed pattern,
//!   with no port/starboard handoff, and it disagrees materially with the workbook gain at the
//!   first MH371 event. (That surface is not used here; this module uses Large's workbook.)
//! - Call-channel power is not integrated: no calibration, a free offset absorbs the signal,
//!   and the bursts within a call are serially dependent.
//! - End-of-flight use also needs HPA output limits, antenna side selection and restart-channel
//!   power calibration.
//!
//! From thread thr_e7vf6bjiyt (27 Aug 2026; its analysis files no longer exist): a level-flight
//! rerun over 11 events gave -0.119 (p = 0.585), RMSE 1.346 dB with no precompensation and
//! 1.063 dB with full precompensation. Large's own workbook note (DATA!DX2:DX3) reads "assumes HPA
//! out does not adjust for peak gain map...test?" and "tested - it doesn't".
//!
//! Not blind on MH371: the s.d. and the link constants were fitted to 7 March data that include
//! MH371, and the earlier MH371 runs used frozen predictions computed at the ACARS truth. MH371 is
//! a calibration flight for this module, not a test of it, so the module stays out of the MH371
//! control (`config/control/mh371.toml`).
//!
//! # Departures from the sources
//!
//! - Elevations 69-90 deg of the gain table are filled by Large's own construction (the median
//!   gain per degree of off-normal angle); the source stops at 68 deg, and a banked aircraft can
//!   see the satellite higher. The step across 68/69 deg is at most 0.23 dB.
//! - Large sampled headings on a grid and assumed level flight; here the particle's state sets the
//!   geometry and the attitude is rotated in full.
//! - The requested EIRP is the 18:25:27 log-on's initial R-channel EIRP, 10.5 dBW, for all five
//!   bursts; Large took it per burst from the log and the decoded LIDUs.

use geo::{lla_to_ecef, local_basis, Vec3, KM_PER_FT};
use hypothesis::{EpochView, Hypothesis, StateView};
use serde::Deserialize;
use std::f64::consts::PI;
use std::path::PathBuf;

/// (epoch, received power in dBm) of the bursts in the doc comment's table.
const RX_POWER_DBM: [(&str, f64); 5] =
    [("m1941", -54.54), ("m2041", -55.52), ("m2141", -54.11), ("m2241", -53.02), ("m0011", -53.27)];

/// AES gain in aircraft coordinates, dBic: 360 azimuths by 91 elevations.
const GAIN_TABLE: &str = include_str!("gain-aircraft-coordinates.csv");

/// Initial R-channel EIRP of the 18:25:27 log-on (SITA log, "AES Process").
const REQUESTED_EIRP_DBW: f64 = 10.5;
/// Gain assumed by the HPA setting: the 25.5 dBW design contour less 16.02 dBW (40 W) plus the
/// 2.68 dB cable loss (Large 2019 workbook, DATA columns EA-EC).
const REFERENCE_GAIN_DBIC: f64 = 25.5 - 16.02 + 2.68;
const UPLINK_WAVELENGTH_M: f64 = 0.182_061_8;
const DOWNLINK_WAVELENGTH_M: f64 = 0.083_275_7;
/// Satellite receive gain relative to G/T, and the transponder and ground chain (fitted).
const SATELLITE_OFFSET_DB: f64 = 27.5;
const CHAIN_DB: f64 = 300.0;
const PERTH_GES_KM: Vec3 = Vec3::new(-2_368.841, 4_881.08, -3_342.092);

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Params {
    /// Bursts to use, by epoch ID.
    epochs: Vec<String>,
    precompensation: Precompensation,
    /// Event-level s.d. of the received power, dB.
    sd_db: f64,
    /// Receive-chain calibration offset added to every prediction, dB (fixed; see above).
    offset_db: f64,
    /// Nose-up pitch assumed for every particle, degrees.
    pitch_deg: f64,
    /// The core's satellite ephemeris, relative to the repository root.
    ephemeris: PathBuf,
}

#[derive(Deserialize, Debug, Clone, Copy, PartialEq)]
enum Precompensation {
    /// The AES corrects its HPA output for the steered-beam gain: b = 0.
    #[serde(rename = "full")]
    Full,
    /// It does not: b = 1.
    #[serde(rename = "none")]
    Uncompensated,
}

/// One burst with the satellite geometry that does not depend on the particle.
#[derive(Debug, Clone)]
struct Burst {
    epoch: String,
    observed_dbm: f64,
    satellite_km: Vec3,
    downlink_km: f64,
}

struct AntennaGain {
    bursts: Vec<Burst>,
    /// b: 0 for full precompensation, 1 for none.
    departure_scale: f64,
    sd_db: f64,
    offset_db: f64,
    pitch_deg: f64,
    gain: GainTable,
}

pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String> {
    let p: Params = params.clone().try_into().map_err(|e| format!("antenna-gain: {e}"))?;
    if !(p.sd_db > 0.0 && p.sd_db.is_finite() && p.offset_db.is_finite() && p.pitch_deg.abs() <= 20.0) {
        return Err("antenna-gain: need sd_db > 0, a finite offset_db and |pitch_deg| <= 20".into());
    }
    if p.epochs.is_empty() {
        return Err("antenna-gain: no epochs".into());
    }
    let satellites = read_ephemeris(&p.ephemeris)?;
    let mut bursts = Vec::new();
    for epoch in &p.epochs {
        let observed_dbm = RX_POWER_DBM
            .iter()
            .find(|(id, _)| id == epoch)
            .map(|&(_, dbm)| dbm)
            .ok_or_else(|| format!("antenna-gain: no received power for epoch {epoch}"))?;
        let satellite_km = satellites
            .iter()
            .find(|(id, _)| id == epoch)
            .map(|&(_, km)| km)
            .ok_or_else(|| format!("antenna-gain: epoch {epoch} is not in {}", p.ephemeris.display()))?;
        if bursts.iter().any(|b: &Burst| &b.epoch == epoch) {
            return Err(format!("antenna-gain: epoch {epoch} listed twice"));
        }
        bursts.push(Burst::new(epoch, observed_dbm, satellite_km));
    }
    let departure_scale = match p.precompensation {
        Precompensation::Full => 0.0,
        Precompensation::Uncompensated => 1.0,
    };
    Ok(Box::new(AntennaGain {
        bursts,
        departure_scale,
        sd_db: p.sd_db,
        offset_db: p.offset_db,
        pitch_deg: p.pitch_deg,
        gain: GainTable::parse(GAIN_TABLE)?,
    }))
}

impl Burst {
    fn new(epoch: &str, observed_dbm: f64, satellite_km: Vec3) -> Self {
        let downlink_km = (satellite_km - PERTH_GES_KM).norm();
        Burst { epoch: epoch.to_string(), observed_dbm, satellite_km, downlink_km }
    }
}

impl Hypothesis for AntennaGain {
    fn observations(&self) -> Vec<String> {
        self.bursts.iter().map(|b| format!("rxpower:{}", b.epoch)).collect()
    }

    fn epoch_log_likelihood(&self, epoch: &EpochView, state: &StateView) -> f64 {
        match self.bursts.iter().find(|b| epoch.satcom && b.epoch == epoch.id) {
            Some(burst) => gaussian_log_density(burst.observed_dbm, self.predicted_dbm(burst, state), self.sd_db),
            None => 0.0,
        }
    }
}

impl AntennaGain {
    /// The received power this particle predicts for `burst`, dBm.
    fn predicted_dbm(&self, burst: &Burst, state: &StateView) -> f64 {
        let (lat, lon) = (state.latitude_deg, state.longitude_deg);
        let aircraft = lla_to_ecef(lat, lon, state.altitude_ft * KM_PER_FT);
        let to_satellite = burst.satellite_km - aircraft;
        let uplink_km = to_satellite.norm();
        let (north, east, up) = local_basis(lat, lon);
        let line = to_satellite * (1.0 / uplink_km);
        let line_ned = [line.dot(north), line.dot(east), -line.dot(up)];
        // Ground track stands in for the air heading until the core exposes it.
        let heading_deg = state.ground_velocity_east_kt.atan2(state.ground_velocity_north_kt).to_degrees();
        let attitude = Attitude { heading_deg, pitch_deg: self.pitch_deg, roll_deg: 0.0 };
        let (azimuth, elevation) = aircraft_angles(line_ned, attitude);
        let eirp_dbw = REQUESTED_EIRP_DBW + self.departure_scale * (self.gain.gain_dbic(azimuth, elevation) - REFERENCE_GAIN_DBIC);
        received_dbm(eirp_dbw, uplink_km, burst.downlink_km, aircraft.norm(), burst.satellite_km.norm()) + self.offset_db
    }
}

/// True heading (clockwise from north), nose-up pitch and right-wing-down roll, degrees.
#[derive(Debug, Clone, Copy)]
struct Attitude {
    heading_deg: f64,
    pitch_deg: f64,
    roll_deg: f64,
}

/// Azimuth (clockwise from the nose, [0, 360)) and elevation (above the wing plane) in degrees
/// of a unit line of sight given in local north-east-down axes. The body axes (forward, right,
/// down) are the NED axes turned by heading, then pitch, then roll (aerospace yaw-pitch-roll).
fn aircraft_angles(line_ned: [f64; 3], attitude: Attitude) -> (f64, f64) {
    let (sh, ch) = attitude.heading_deg.to_radians().sin_cos();
    let (sp, cp) = attitude.pitch_deg.to_radians().sin_cos();
    let (sr, cr) = attitude.roll_deg.to_radians().sin_cos();
    let forward = [cp * ch, cp * sh, -sp];
    let right = [sr * sp * ch - cr * sh, sr * sp * sh + cr * ch, sr * cp];
    let down = [cr * sp * ch + sr * sh, cr * sp * sh - sr * ch, cr * cp];
    let dot = |axis: [f64; 3]| axis[0] * line_ned[0] + axis[1] * line_ned[1] + axis[2] * line_ned[2];
    let (f, r, d) = (dot(forward), dot(right), dot(down));
    (r.atan2(f).to_degrees().rem_euclid(360.0), (-d).atan2(f.hypot(r)).to_degrees())
}

/// Received power at the GES (dBm) for an AES EIRP (dBW), by Large's (2019) link budget. The
/// satellite G/T uses the aircraft's elevation angle from the law of cosines on the ranges, as
/// the workbook does.
fn received_dbm(eirp_dbw: f64, uplink_km: f64, downlink_km: f64, aircraft_radius_km: f64, satellite_radius_km: f64) -> f64 {
    let free_space_db = |wavelength_m: f64, range_km: f64| 20.0 * (wavelength_m / (4.0 * PI * range_km * 1_000.0)).log10();
    let cos_zenith = (aircraft_radius_km.powi(2) + uplink_km.powi(2) - satellite_radius_km.powi(2)) / (2.0 * aircraft_radius_km * uplink_km);
    let elevation_deg = cos_zenith.clamp(-1.0, 1.0).acos().to_degrees() - 90.0;
    let satellite_gt_db = -11.5 + 0.013_96 * elevation_deg + 1.535e-4 * elevation_deg.powi(2);
    eirp_dbw
        + free_space_db(UPLINK_WAVELENGTH_M, uplink_km)
        + satellite_gt_db
        + SATELLITE_OFFSET_DB
        + free_space_db(DOWNLINK_WAVELENGTH_M, downlink_km)
        + CHAIN_DB
}

fn gaussian_log_density(x: f64, mean: f64, sd: f64) -> f64 {
    let z = (x - mean) / sd;
    -0.5 * z * z - (sd * (2.0 * PI).sqrt()).ln()
}

/// Gain (dBic) on a 1-degree grid: azimuth 0..359 clockwise from the nose, elevation 0..90.
struct GainTable {
    /// Azimuth-major, 91 elevations per azimuth.
    dbic: Vec<f64>,
}

impl GainTable {
    const ELEVATIONS: usize = 91;

    fn parse(text: &str) -> Result<Self, String> {
        let mut lines = text.lines().filter(|l| !l.starts_with('#'));
        let header: Vec<&str> = lines.next().ok_or("gain table: empty")?.split(',').collect();
        let expected: Vec<String> = std::iter::once("azimuth_deg".to_string()).chain((0..Self::ELEVATIONS).map(|e| e.to_string())).collect();
        if header != expected {
            return Err("gain table: header must be azimuth_deg,0,...,90".into());
        }
        let mut dbic = Vec::with_capacity(360 * Self::ELEVATIONS);
        for (azimuth, line) in lines.enumerate() {
            let fields: Vec<&str> = line.split(',').collect();
            if fields.len() != Self::ELEVATIONS + 1 || fields[0] != azimuth.to_string() {
                return Err(format!("gain table: row {azimuth} is malformed"));
            }
            for field in &fields[1..] {
                let value: f64 = field.parse().map_err(|e| format!("gain table: row {azimuth}: {e}"))?;
                dbic.push(value);
            }
        }
        if dbic.len() != 360 * Self::ELEVATIONS {
            return Err(format!("gain table: {} values, expected {}", dbic.len(), 360 * Self::ELEVATIONS));
        }
        Ok(GainTable { dbic })
    }

    fn at(&self, azimuth: usize, elevation: usize) -> f64 {
        self.dbic[azimuth * Self::ELEVATIONS + elevation]
    }

    /// Bilinear in azimuth (wrapping) and elevation. The satellite below the wing plane is
    /// outside the model: no particle near the 19:41-00:11 arcs gets there (the satellite stands
    /// 40-56 deg above the horizon), so meeting one stops the run rather than guessing a gain.
    fn gain_dbic(&self, azimuth_deg: f64, elevation_deg: f64) -> f64 {
        assert!(
            (0.0..=90.0).contains(&elevation_deg),
            "antenna-gain: satellite {elevation_deg:.1} deg from the wing plane, outside the gain table"
        );
        let azimuth = azimuth_deg.rem_euclid(360.0);
        let a0 = azimuth.floor();
        let (i, fa) = (a0 as usize % 360, azimuth - a0);
        let j = (elevation_deg.floor() as usize).min(Self::ELEVATIONS - 2);
        let fe = elevation_deg - j as f64;
        let row = |e: usize| self.at(i, e) * (1.0 - fa) + self.at((i + 1) % 360, e) * fa;
        row(j) * (1.0 - fe) + row(j + 1) * fe
    }
}

/// (epoch ID, satellite ECEF km) from the core's ephemeris CSV (`epoch_id`, `x_km`, `y_km`, `z_km`).
fn read_ephemeris(path: &std::path::Path) -> Result<Vec<(String, Vec3)>, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("antenna-gain: {}: {e}", path.display()))?;
    let mut lines = text.lines();
    let header: Vec<&str> = lines.next().unwrap_or_default().split(',').collect();
    let column = |name: &str| header.iter().position(|h| *h == name).ok_or(format!("antenna-gain: {} has no {name} column", path.display()));
    let (id, x, y, z) = (column("epoch_id")?, column("x_km")?, column("y_km")?, column("z_km")?);
    lines
        .filter(|l| !l.trim().is_empty())
        .map(|line| {
            let f: Vec<&str> = line.split(',').collect();
            let number = |k: usize| f.get(k).and_then(|v| v.parse::<f64>().ok()).ok_or(format!("antenna-gain: bad line in {}: {line}", path.display()));
            Ok((f[id].to_string(), Vec3::new(number(x)?, number(y)?, number(z)?)))
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn line_of_sight(azimuth_deg: f64, elevation_deg: f64) -> [f64; 3] {
        let (sa, ca) = azimuth_deg.to_radians().sin_cos();
        let (se, ce) = elevation_deg.to_radians().sin_cos();
        [ce * ca, ce * sa, -se]
    }

    fn assert_close(actual: f64, expected: f64, tolerance: f64, what: &str) {
        assert!((actual - expected).abs() <= tolerance, "{what}: {actual} vs {expected}");
    }

    #[test]
    fn gain_at_tabulated_cells_matches_the_source_table() {
        let table = GainTable::parse(GAIN_TABLE).unwrap();
        // (azimuth, elevation, value, cell of Sheet1 in "GAIN IN AC COORDS TO 68 EL 360 AZ.xlsx").
        for (azimuth, elevation, dbic, cell) in [
            (0.0, 0.0, 4.3, "B361"),
            (1.0, 0.0, 4.6, "B2"),
            (90.0, 45.0, 14.5, "AU91"),
            (270.0, 45.0, 14.5, "AU271"),
            (180.0, 10.0, 6.6, "L181"),
            (135.0, 30.0, 12.9, "AF136"),
            (45.0, 55.0, 14.0, "BE46"),
            (359.0, 68.0, 12.3, "BR360"),
        ] {
            assert_close(table.gain_dbic(azimuth, elevation), dbic, 1e-12, cell);
        }
        // Between cells: bilinear, and the azimuth wraps through the nose (azimuths 359 and 0).
        assert_close(table.gain_dbic(359.5, 0.0), (4.6 + 4.3) / 2.0, 1e-12, "wrap at the nose");
        assert_close(table.gain_dbic(-0.5, 0.0), table.gain_dbic(359.5, 0.0), 1e-12, "negative azimuth");
        assert_close(table.gain_dbic(90.0, 45.5), (14.5 + table.at(90, 46)) / 2.0, 1e-12, "between elevations");
    }

    #[test]
    fn attitude_rotation_limiting_cases() {
        let level = |heading_deg| Attitude { heading_deg, pitch_deg: 0.0, roll_deg: 0.0 };
        // Level at 040: a satellite at 070 true, 25 deg up, is 30 deg right of the nose, 25 deg up.
        let (azimuth, elevation) = aircraft_angles(line_of_sight(70.0, 25.0), level(40.0));
        assert_close(azimuth, 30.0, 1e-9, "level azimuth");
        assert_close(elevation, 25.0, 1e-9, "level elevation");
        // Ten degrees nose-up with the satellite dead ahead lowers it by ten degrees.
        let pitched = Attitude { heading_deg: 40.0, pitch_deg: 10.0, roll_deg: 0.0 };
        let (azimuth, elevation) = aircraft_angles(line_of_sight(40.0, 25.0), pitched);
        assert_close(azimuth.min(360.0 - azimuth), 0.0, 1e-9, "pitched azimuth");
        assert_close(elevation, 15.0, 1e-9, "pitched elevation");
        // Twenty degrees right wing down raises a satellite on the right by twenty degrees...
        let rolled = Attitude { heading_deg: 40.0, pitch_deg: 0.0, roll_deg: 20.0 };
        let (azimuth, elevation) = aircraft_angles(line_of_sight(130.0, 30.0), rolled);
        assert_close(azimuth, 90.0, 1e-9, "rolled azimuth");
        assert_close(elevation, 50.0, 1e-9, "rolled elevation");
        // ...and moves the zenith twenty degrees towards the left wing.
        let (azimuth, elevation) = aircraft_angles([0.0, 0.0, -1.0], rolled);
        assert_close(azimuth, 270.0, 1e-9, "zenith azimuth");
        assert_close(elevation, 70.0, 1e-9, "zenith elevation");
    }

    #[test]
    fn link_budget_reproduces_the_workbook() {
        // Large (2019) "Feb 21 Copy of Angles Test ... (version 1).xlsx", DATA row 114 (MH371,
        // 01:55:23, R600, requested EIRP 12.5 dBW, gain 10.4 dBic): EIRP 10.74 dBW, ranges
        // DB114, AN114, DD114 and DC114, and P = X114 - EP114 = -56.16 - 0.8534766196173962.
        let eirp_dbw = 12.5 + (10.4 - REFERENCE_GAIN_DBIC);
        assert_close(eirp_dbw, 10.74, 1e-12, "EIRP (EC114)");
        let predicted = received_dbm(eirp_dbw, 39_418.669_007_120_39, 39_148.339_512_715_78, 6_377.985_184_164_145, 42_163.444_416_479_22);
        assert_close(predicted, -56.16 - 0.853_476_619_617_396_2, 1e-9, "received power");
    }

    /// An aircraft on the equator at 090 E heading north, with the satellite due east 45 deg up
    /// at 37,000 km: the satellite is broadside to starboard at 45 deg, where the table gives
    /// 14.5 dBic (Sheet1!AU91).
    fn broadside_case() -> (Burst, StateView) {
        let aircraft = lla_to_ecef(0.0, 90.0, 0.0);
        let (_, east, up) = local_basis(0.0, 90.0);
        let s = std::f64::consts::FRAC_1_SQRT_2 * 37_000.0;
        let burst = Burst::new("m1941", -54.54, aircraft + east * s + up * s);
        let state = StateView {
            unix_s: 0.0,
            latitude_deg: 0.0,
            longitude_deg: 90.0,
            altitude_ft: 0.0,
            ground_velocity_north_kt: 480.0,
            ground_velocity_east_kt: 0.0,
            mach: 0.8,
            mode: 0,
            manoeuvre_time_constant_h: 1.0,
            turns: 0,
            accelerations: 0,
            climbs: 0,
            bfo_bias_hz: 0.0,
            alternative: 0,
        };
        (burst, state)
    }

    fn module(bursts: Vec<Burst>, departure_scale: f64) -> AntennaGain {
        let gain = GainTable::parse(GAIN_TABLE).unwrap();
        AntennaGain { bursts, departure_scale, sd_db: 1.72, offset_db: 0.0, pitch_deg: 0.0, gain }
    }

    #[test]
    fn likelihood_matches_a_hand_computed_value() {
        // By hand: EIRP 10.5 + (14.5 - 12.16) = 12.84 dBW; uplink 37,000 km at 45 deg elevation
        // (G/T -10.560963 dB/K); satellite radius 41,754.3100 km, downlink to the Perth GES
        // 36,638.8494 km; P = 12.84 - 188.1439 - 10.5610 + 27.5 - 194.8527 + 300 = -53.217486 dBm;
        // ln N(-54.54; -53.217486, 1.72) = -0.5 (1.322514 / 1.72)^2 - ln(1.72 sqrt(2 pi)) = -1.756869.
        let (burst, state) = broadside_case();
        let epoch = EpochView { id: "m1941", unix_s: 0.0, satcom: true };
        let none = module(vec![burst.clone()], 1.0);
        assert_close(none.predicted_dbm(&none.bursts[0], &state), -53.217_486, 1e-6, "predicted power");
        assert_close(none.epoch_log_likelihood(&epoch, &state), -1.756_869, 1e-6, "log-likelihood");
        // Full precompensation drops the 2.34 dB departure; other epochs add nothing.
        let full = module(vec![burst], 0.0);
        assert_close(full.predicted_dbm(&full.bursts[0], &state), -55.557_486, 1e-6, "full precompensation");
        assert_eq!(none.epoch_log_likelihood(&EpochView { id: "m2041", unix_s: 0.0, satcom: true }, &state), 0.0);
        assert_eq!(none.epoch_log_likelihood(&EpochView { id: "m1941", unix_s: 0.0, satcom: false }, &state), 0.0);
        // The range enters only weakly: 10 km east (7.07 km closer) moves the link by 0.0045 dB.
        let mut closer = state;
        closer.longitude_deg += 10.0 / 111.32;
        let shift = full.predicted_dbm(&full.bursts[0], &closer) - full.predicted_dbm(&full.bursts[0], &state);
        assert_close(shift, 0.004_46, 5e-5, "range sensitivity");
    }

    /// Minimal generator for the synthetic test (hypotheses may not depend on `rand`).
    struct SplitMix(u64);
    impl SplitMix {
        fn uniform(&mut self) -> f64 {
            self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
            let mut z = self.0;
            z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
            z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
            ((z ^ (z >> 31)) >> 11) as f64 / (1u64 << 53) as f64
        }
        fn normal(&mut self) -> f64 {
            let (u, v) = (self.uniform().max(1e-300), self.uniform());
            (-2.0 * u.ln()).sqrt() * (2.0 * PI * v).cos()
        }
    }

    /// Synthetic recovery: draw a heading from a uniform prior, generate the five powers from it
    /// with the modelled noise, and check that the 90% highest-posterior set of heading covers the
    /// truth in 90% of replicates (exact for a correct likelihood). Halving the assumed s.d. must
    /// break the coverage, so the test can fail.
    #[test]
    fn synthetic_headings_are_covered_at_the_nominal_rate() {
        let (burst, state) = broadside_case();
        let aircraft = lla_to_ecef(0.0, 90.0, 0.0);
        let (north, east, up) = local_basis(0.0, 90.0);
        // Five satellite directions spanning the cruise epochs' elevations (40-56 deg).
        let bursts: Vec<Burst> = [(240.0, 56.0), (250.0, 55.0), (265.0, 52.0), (285.0, 48.0), (300.0, 40.0)]
            .iter()
            .map(|&(azimuth, elevation): &(f64, f64)| {
                let [n, e, d] = line_of_sight(azimuth, elevation);
                Burst::new(&burst.epoch, 0.0, aircraft + (north * n + east * e - up * d) * 37_000.0)
            })
            .collect();
        let model = module(bursts, 1.0);
        let predict = |heading_deg: f64| {
            let mut s = state;
            let (sh, ch) = heading_deg.to_radians().sin_cos();
            (s.ground_velocity_north_kt, s.ground_velocity_east_kt) = (480.0 * ch, 480.0 * sh);
            model.bursts.iter().map(|b| model.predicted_dbm(b, &s)).collect::<Vec<f64>>()
        };
        let grid: Vec<Vec<f64>> = (0..360).map(|h| predict(h as f64 + 0.5)).collect();
        let coverage = |assumed_sd: f64, replicates: usize, rng: &mut SplitMix| {
            let mut covered = 0;
            for _ in 0..replicates {
                let truth = (rng.uniform() * 360.0) as usize;
                let data: Vec<f64> = grid[truth].iter().map(|p| p + 1.72 * rng.normal()).collect();
                let log_post: Vec<f64> = grid
                    .iter()
                    .map(|pred| pred.iter().zip(&data).map(|(p, y)| gaussian_log_density(*y, *p, assumed_sd)).sum())
                    .collect();
                let top = log_post.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
                let mut weights: Vec<(f64, usize)> = log_post.iter().enumerate().map(|(i, l)| ((l - top).exp(), i)).collect();
                let total: f64 = weights.iter().map(|w| w.0).sum();
                weights.sort_by(|a, b| b.0.total_cmp(&a.0));
                let mut mass = 0.0;
                for (w, i) in weights {
                    if mass >= 0.9 * total {
                        break;
                    }
                    mass += w;
                    if i == truth {
                        covered += 1;
                        break;
                    }
                }
            }
            covered as f64 / replicates as f64
        };
        let mut rng = SplitMix(370);
        let nominal = coverage(1.72, 2000, &mut rng);
        assert!((nominal - 0.9).abs() < 0.025, "coverage {nominal} with the true s.d.");
        let overconfident = coverage(0.86, 2000, &mut rng);
        assert!(overconfident < 0.8, "coverage {overconfident} with half the s.d.");
    }
}
