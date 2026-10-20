//! TEOS-10, once, for every consumer (brief rule 9): settling's in-situ density, hydroacoustics'
//! sound speed, and pressure from depth.
//!
//! Two implementations of the one standard, each used where it is complete, cross-checked in tests:
//! - **Preparation** (Python `gsw`, the official GSW-C wrapper) converts products whose state is
//!   in-situ temperature and practical salinity (WOA23, HYCOM) to Absolute Salinity SA and
//!   Conservative Temperature CT on the product grid, including the Absolute Salinity Anomaly atlas
//!   (`SA_from_SP`) and `CT_from_t`, which the Rust port lacks.
//! - **Runtime** (Rust `gsw` 0.2.3, GSW-rs) evaluates `rho`, `sound_speed` and `p_from_z` from SA, CT
//!   and p with the same 75-term polynomial. For a product carrying potential temperature and
//!   practical salinity (GLORYS12) it forms SA as Reference Salinity (SA anomaly set to zero, which
//!   is reported) and CT with `ct_from_pt`. In-situ temperature is refused here: it must be converted
//!   in preparation.

use crate::profile::{Profile, Salinity, Temperature};
use serde::Serialize;

#[derive(Clone, Debug, PartialEq, Serialize)]
pub enum Teos10Error {
    /// In-situ temperature must be converted to CT in preparation (`gsw.CT_from_t`).
    InSituTemperatureNeedsPreparation,
    Gsw(String),
}

/// SA, CT and the derived state on a profile's levels.
#[derive(Clone, Debug, PartialEq, Serialize)]
pub struct Teos10Profile {
    pub depth_m: Vec<f64>,
    pub absolute_salinity_g_kg: Vec<f64>,
    pub conservative_temperature_c: Vec<f64>,
    pub pressure_dbar: Vec<f64>,
    pub in_situ_density_kg_m3: Vec<f64>,
    pub sound_speed_m_s: Vec<f64>,
    /// False when SA was formed as Reference Salinity (anomaly taken as zero). In the open
    /// Southern Indian Ocean the anomaly is below about 0.02 g/kg: under 2e-5 relative in density.
    pub sa_anomaly_included: bool,
}

fn gsw_err(e: gsw::Error) -> Teos10Error {
    Teos10Error::Gsw(format!("{e:?}"))
}

/// Sea pressure (dbar) at geometric depth `depth_m` (positive down) and latitude, TEOS-10 `p_from_z`.
pub fn pressure_dbar(depth_m: f64, lat_deg: f64) -> f64 {
    gsw::conversions::p_from_z(-depth_m, lat_deg, None, None).unwrap_or(f64::NAN)
}

/// In-situ density (kg/m^3) and sound speed (m/s) from SA, CT, p.
pub fn rho_and_sound_speed(sa: f64, ct: f64, p: f64) -> Result<(f64, f64), Teos10Error> {
    Ok((gsw::volume::rho(sa, ct, p).map_err(gsw_err)?, gsw::volume::sound_speed(sa, ct, p).map_err(gsw_err)?))
}

impl Profile {
    /// TEOS-10 state on this profile's levels.
    pub fn teos10(&self) -> Result<Teos10Profile, Teos10Error> {
        let (sa, anomaly) = match &self.salinity {
            Salinity::Absolute(sa) => (sa.clone(), true),
            Salinity::Practical(sp) => (sp.iter().map(|&s| gsw::conversions::sr_from_sp(s)).collect(), false),
        };
        let ct: Vec<f64> = match &self.temperature {
            Temperature::Conservative(ct) => ct.clone(),
            Temperature::Potential(pt) => sa
                .iter()
                .zip(pt)
                .map(|(&s, &t)| gsw::conversions::ct_from_pt(s, t).map_err(gsw_err))
                .collect::<Result<_, _>>()?,
            Temperature::InSitu(_) => return Err(Teos10Error::InSituTemperatureNeedsPreparation),
        };
        let mut rho = Vec::with_capacity(sa.len());
        let mut c = Vec::with_capacity(sa.len());
        for k in 0..sa.len() {
            let (r, s) = rho_and_sound_speed(sa[k], ct[k], self.pressure_dbar[k])?;
            rho.push(r);
            c.push(s);
        }
        Ok(Teos10Profile {
            depth_m: self.depth_m.clone(),
            absolute_salinity_g_kg: sa,
            conservative_temperature_c: ct,
            pressure_dbar: self.pressure_dbar.clone(),
            in_situ_density_kg_m3: rho,
            sound_speed_m_s: c,
            sa_anomaly_included: anomaly,
        })
    }
}

impl Teos10Profile {
    /// In-situ density at depth `z_m`, linear between levels; the first level is held above it and
    /// the deepest below it (the profile query's `at_depth` reports when that is extrapolation).
    pub fn rho_at(&self, z_m: f64) -> f64 {
        let d = &self.depth_m;
        let r = &self.in_situ_density_kg_m3;
        if z_m <= d[0] {
            return r[0];
        }
        if z_m >= d[d.len() - 1] {
            return r[r.len() - 1];
        }
        let i = d.partition_point(|&x| x <= z_m) - 1;
        r[i] + (z_m - d[i]) / (d[i + 1] - d[i]) * (r[i + 1] - r[i])
    }
}
