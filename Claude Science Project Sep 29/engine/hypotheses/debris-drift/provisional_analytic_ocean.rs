//! PROVISIONAL ANALYTIC OCEAN - NOT THE SHARED TRANSPORT, AND NOT EVIDENCE.
//!
//! Allowed by the architecture ruling of 2026-10-08 (coordination/OCEAN_DRIFT.md, question 2):
//! closed-form fields only, a straight-line coast, no data access, no gridded interpolation. It
//! exists so that the source-grid, interpolation and recovery-observation layers can be built and
//! tested, and so that the pilot becomes a field swap when `crates/ocean` lands. It is deleted then.
//! Every number that passes through it is provisional.
//!
//! The call shape it assumes is the one stated in the drift interface request in
//! coordination/OCEAN_TRANSPORT.md, so that the shared owner can reject it rather than inherit it:
//! batch release; persistent per-particle object response (a_stokes, c_wind), never redrawn per
//! step; current, Stokes drift and 10 m wind supplied as separate components; diffusion as a
//! declared parameter; beaching returns an along-coast coordinate and a time.
//!
//! Geometry is a local tangent plane (equirectangular about a reference point), adequate for a
//! closed-form test field and for nothing else.

use super::rng::Rng;

const KM_PER_DEG: f64 = 111.195;

#[derive(Debug, Clone, Copy)]
pub struct LocalPlane {
    pub lat0: f64,
    pub lon0: f64,
}

impl LocalPlane {
    pub fn to_xy(&self, lat: f64, lon: f64) -> (f64, f64) {
        let x = (lon - self.lon0) * KM_PER_DEG * self.lat0.to_radians().cos();
        let y = (lat - self.lat0) * KM_PER_DEG;
        (x, y)
    }
    /// `[lon, lat]`, the shared API's convention.
    pub fn to_lonlat(&self, x: f64, y: f64) -> [f64; 2] {
        [self.lon0 + x / (KM_PER_DEG * self.lat0.to_radians().cos()), self.lat0 + y / KM_PER_DEG]
    }
}

/// Closed-form surface current, m/s.
#[derive(Debug, Clone, Copy)]
pub enum Current {
    Uniform { east: f64, north: f64 },
    /// Solid-body rotation about (cx, cy) km, angular rate omega rad/s (positive anticlockwise).
    #[cfg_attr(not(test), allow(dead_code))]
    SolidBody { omega: f64, cx: f64, cy: f64 },
}

/// A straight coast. Ocean is where `normal . r < offset_km`; the along-coast coordinate is
/// `tangent . r` with tangent = normal rotated 90 degrees anticlockwise.
#[derive(Debug, Clone, Copy)]
pub struct Coast {
    pub normal: (f64, f64),
    pub offset_km: f64,
}

impl Coast {
    pub fn through(p: (f64, f64), q: (f64, f64), ocean_point: (f64, f64)) -> Coast {
        let (tx, ty) = (q.0 - p.0, q.1 - p.1);
        let len = (tx * tx + ty * ty).sqrt();
        let mut n = (ty / len, -tx / len);
        let mut off = n.0 * p.0 + n.1 * p.1;
        if n.0 * ocean_point.0 + n.1 * ocean_point.1 > off {
            n = (-n.0, -n.1);
            off = -off;
        }
        Coast { normal: n, offset_km: off }
    }
    pub fn signed(&self, x: f64, y: f64) -> f64 {
        self.normal.0 * x + self.normal.1 * y - self.offset_km
    }
    pub fn along(&self, x: f64, y: f64) -> f64 {
        -self.normal.1 * x + self.normal.0 * y
    }
}

/// Persistent object response of one particle.
#[derive(Debug, Clone, Copy)]
pub struct Response {
    /// Multiplier on the Stokes drift (1 = full surface Stokes drift).
    pub a_stokes: f64,
    /// Direct wind drag as a fraction of the 10 m wind (leeway beyond Stokes).
    pub c_wind: f64,
}

#[derive(Debug, Clone, Copy)]
pub struct AnalyticOcean {
    pub current: Current,
    /// Scale applied to the current: one shared-environment realisation (rule 8 of the brief).
    pub current_scale: f64,
    pub stokes: (f64, f64),
    pub wind: (f64, f64),
    /// Isotropic horizontal diffusivity, m^2/s, as a random walk with per-component variance
    /// 2 K dt per step.
    pub diffusivity_m2s: f64,
    pub coast: Option<Coast>,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Fate {
    pub beached: bool,
    /// Days after release at beaching, or at the end of integration.
    pub t_days: f64,
    pub x_km: f64,
    pub y_km: f64,
    /// Along-coast coordinate at beaching (NaN if not beached).
    pub s_km: f64,
}

impl AnalyticOcean {
    fn velocity(&self, x: f64, y: f64, r: &Response) -> (f64, f64) {
        let (cu, cv) = match self.current {
            Current::Uniform { east, north } => (east, north),
            Current::SolidBody { omega, cx, cy } => {
                (-omega * (y - cy) * 1000.0, omega * (x - cx) * 1000.0)
            }
        };
        (
            self.current_scale * cu + r.a_stokes * self.stokes.0 + r.c_wind * self.wind.0,
            self.current_scale * cv + r.a_stokes * self.stokes.1 + r.c_wind * self.wind.1,
        )
    }

    /// Heun (RK2) for the deterministic velocity plus an additive random walk; stops at the
    /// first coast crossing, located by linear interpolation within the step.
    pub fn integrate(&self, x0: f64, y0: f64, r: &Response, dt_s: f64, n_steps: usize, rng: &mut Rng) -> Fate {
        let (mut x, mut y) = (x0, y0);
        let sd_km = (2.0 * self.diffusivity_m2s * dt_s).sqrt() / 1000.0;
        let dtk = dt_s / 1000.0;
        for step in 0..n_steps {
            let (u1, v1) = self.velocity(x, y, r);
            let (xp, yp) = (x + u1 * dtk, y + v1 * dtk);
            let (u2, v2) = self.velocity(xp, yp, r);
            let mut xn = x + 0.5 * (u1 + u2) * dtk;
            let mut yn = y + 0.5 * (v1 + v2) * dtk;
            if sd_km > 0.0 {
                xn += sd_km * rng.normal();
                yn += sd_km * rng.normal();
            }
            if let Some(c) = &self.coast {
                let (a, b) = (c.signed(x, y), c.signed(xn, yn));
                if b >= 0.0 {
                    let f = if b - a > 0.0 { (-a / (b - a)).clamp(0.0, 1.0) } else { 1.0 };
                    let (xb, yb) = (x + f * (xn - x), y + f * (yn - y));
                    return Fate {
                        beached: true,
                        t_days: (step as f64 + f) * dt_s / 86_400.0,
                        x_km: xb,
                        y_km: yb,
                        s_km: c.along(xb, yb),
                    };
                }
            }
            x = xn;
            y = yn;
        }
        Fate { beached: false, t_days: n_steps as f64 * dt_s / 86_400.0, x_km: x, y_km: y, s_km: f64::NAN }
    }
}
