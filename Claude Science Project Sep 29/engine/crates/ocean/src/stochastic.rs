//! The two stochastic parts of transport, kept apart because they mean different things.
//!
//! [`Diffusion`] is unresolved sub-grid dispersion. It is **independent per particle** and applied
//! **per integration step** (never per field cell), as Wiener or Ornstein-Uhlenbeck increments, so
//! its statistics do not depend on the step length (exactly for `RandomWalk`/`Diffusivity`).
//! For reference: the archive's 100 m^2/s is a 2-D RMS of 3.17 NM after one day; CSIRO's
//! 5 NM/day random walk is K = 248 m^2/s. They differ by a factor 2.5 and neither was tested.
//!
//! [`OceanErrorModel`] is error in the ocean product itself. One realisation is drawn **per run**
//! (or per impact event, for settling) and shared by every particle: every recovered object
//! travelled through the same ocean, so independent errors per particle would let each object
//! choose its own ocean (brief rule 4).
//!
//! Random streams: particle `i` uses ChaCha8 stream `i`; the ocean-error realisation uses streams
//! `u64::MAX - 3b` and `u64::MAX - 3b - 1` for band b; the diffusivity draw uses `u64::MAX - 2`. Results are therefore
//! identical for any thread count. With `OceanErrorModel::none()` and a fixed diffusion, changing
//! the run seed changes only the per-particle diffusion (and refloat) streams.
//!
//! **Diffusivity is a component of the shared-environment parameter eta** (ruled 9 October): like the
//! ocean error, it is drawn once per run from a declared prior ([`DiffusivityPrior`]), shared by
//! every particle and every find, and marginalised jointly by the consumers' Monte Carlo over run
//! seeds. CSIRO's 5 NM/day random walk is K = 248 m^2/s, not 100.

use crate::{dot, enu_basis, LonLat, EARTH_RADIUS_M, METRES_PER_NM, SECONDS_PER_DAY};
use rand::{Rng, SeedableRng};
use rand_chacha::ChaCha8Rng;
use rand_distr::StandardNormal;
use serde::Serialize;

pub(crate) const OCEAN_ERROR_STREAM: u64 = u64::MAX;
pub(crate) const DIFFUSIVITY_STREAM: u64 = u64::MAX - 2;

pub(crate) fn rng(seed: u64, stream: u64) -> ChaCha8Rng {
    let mut r = ChaCha8Rng::seed_from_u64(seed);
    r.set_stream(stream);
    r
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub enum Diffusion {
    None,
    /// Isotropic random walk: 2-D RMS displacement `rms_m_per_day` after one day.
    RandomWalk { rms_m_per_day: f64 },
    /// Fickian diffusivity: per-component displacement variance 2 K t.
    Diffusivity { k_m2_s: f64 },
    /// Random flight: per-particle Ornstein-Uhlenbeck velocity, per-component RMS `sigma_m_s`,
    /// decorrelation `lagrangian_time_s`; long-time diffusivity sigma^2 T_L. The velocity is
    /// updated exactly once per step and held through the step.
    RandomFlight { sigma_m_s: f64, lagrangian_time_s: f64 },
}

impl Diffusion {
    pub fn random_walk_nm_per_day(nm: f64) -> Self {
        Diffusion::RandomWalk { rms_m_per_day: nm * METRES_PER_NM }
    }
    /// Per-component standard deviation (m) of the random-walk displacement over `dt` seconds.
    pub fn walk_sigma_m(&self, dt: f64) -> f64 {
        match *self {
            Diffusion::RandomWalk { rms_m_per_day } => rms_m_per_day * (dt / SECONDS_PER_DAY).sqrt() / 2f64.sqrt(),
            Diffusion::Diffusivity { k_m2_s } => (2.0 * k_m2_s * dt).sqrt(),
            _ => 0.0,
        }
    }
    pub fn long_time_diffusivity_m2_s(&self) -> f64 {
        match *self {
            Diffusion::None => 0.0,
            Diffusion::RandomWalk { rms_m_per_day } => rms_m_per_day.powi(2) / (4.0 * SECONDS_PER_DAY),
            Diffusion::Diffusivity { k_m2_s } => k_m2_s,
            Diffusion::RandomFlight { sigma_m_s, lagrangian_time_s } => sigma_m_s.powi(2) * lagrangian_time_s,
        }
    }
    pub fn application(&self) -> &'static str {
        match self {
            Diffusion::None => "none",
            Diffusion::RandomFlight { .. } => "per step, per particle: OU velocity added at both RK2 stages",
            _ => "per step, per particle: Gaussian displacement after the RK2 step",
        }
    }
}

/// Prior on the horizontal diffusivity K, an eta component. One K per run, drawn from the run seed.
#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub enum DiffusivityPrior {
    Fixed { k_m2_s: f64 },
    /// ln K uniform on [ln k_min, ln k_max].
    LogUniform { k_min_m2_s: f64, k_max_m2_s: f64 },
}

impl DiffusivityPrior {
    /// PROVISIONAL default, the same for every product until the drogued-drifter replay
    /// (deliverable 9) constrains it per product: log-uniform on 30-1000 m^2/s, i.e. a one-day 2-D
    /// RMS of 1.7-9.9 NM. It spans the archive's 100 m^2/s and CSIRO's 248 m^2/s with room either
    /// side. The sub-grid diffusivity should depend on the product's resolution (0.25 deg OSCAR
    /// resolves less of the eddy field than 1/12 deg GLORYS12), so the prior is p(K | ocean-model).
    pub fn provisional(_ocean_model: &str) -> Self {
        DiffusivityPrior::LogUniform { k_min_m2_s: 30.0, k_max_m2_s: 1000.0 }
    }
    /// The run's diffusion model: Fickian diffusivity with this run's K.
    pub fn draw(&self, seed: u64) -> Diffusion {
        match *self {
            DiffusivityPrior::Fixed { k_m2_s } => Diffusion::Diffusivity { k_m2_s },
            DiffusivityPrior::LogUniform { k_min_m2_s, k_max_m2_s } => {
                let u: f64 = rng(seed, DIFFUSIVITY_STREAM).gen();
                Diffusion::Diffusivity { k_m2_s: (k_min_m2_s.ln() + u * (k_max_m2_s / k_min_m2_s).ln()).exp() }
            }
        }
    }
    /// Log prior density of K (per m^2/s), for consumers that reweight across draws.
    pub fn ln_density(&self, k_m2_s: f64) -> f64 {
        match *self {
            DiffusivityPrior::Fixed { k_m2_s: k0 } => if k_m2_s == k0 { 0.0 } else { f64::NEG_INFINITY },
            DiffusivityPrior::LogUniform { k_min_m2_s, k_max_m2_s } => {
                if k_m2_s >= k_min_m2_s && k_m2_s <= k_max_m2_s {
                    -(k_m2_s * (k_max_m2_s / k_min_m2_s).ln()).ln()
                } else {
                    f64::NEG_INFINITY
                }
            }
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub enum ErrorKind {
    None,
    /// One constant velocity vector per realisation, each component N(0, sigma^2).
    UniformOffset { sigma_m_s: f64 },
    /// Non-divergent random field: streamfunction as `modes` random Fourier modes with Gaussian
    /// spectrum (spatial scale `length_scale_m` in 3-D Earth-centred coordinates, temporal scale
    /// `time_scale_s`); each velocity component has ensemble variance sigma^2.
    Eddying { sigma_m_s: f64, length_scale_m: f64, time_scale_s: f64, modes: usize },
}

/// How the error varies with depth (for settling).
#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub enum VerticalStructure {
    /// One realisation at every depth, same amplitude.
    Uniform,
    /// One realisation, fully correlated in the vertical, amplitude
    /// factor(z) = deep_ratio + (1 - deep_ratio) exp(-z / efold_m).
    Exponential { efold_m: f64, deep_ratio: f64 },
    /// Settling's bands: surface (0 to `surface_to_m`), upper (to `upper_to_m`), deep (below), and a
    /// near-bottom band keyed to **height above the seabed** (within `near_bottom_m` of it), which
    /// takes precedence where the seabed depth is known. Each band has its own amplitude factor and
    /// its **own independent realisation** (separate random streams): correlated within a band,
    /// independent across bands, since surface, interior and bottom-boundary-layer flows are
    /// different processes. Still one draw per run or impact event.
    Banded { surface_to_m: f64, upper_to_m: f64, near_bottom_m: f64, factors: [f64; 4] },
}

/// Band indices of [`VerticalStructure::Banded`].
pub const BAND_SURFACE: usize = 0;
pub const BAND_UPPER: usize = 1;
pub const BAND_DEEP: usize = 2;
pub const BAND_NEAR_BOTTOM: usize = 3;

#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub struct OceanErrorModel {
    pub kind: ErrorKind,
    pub vertical: VerticalStructure,
}

impl OceanErrorModel {
    pub fn none() -> Self {
        OceanErrorModel { kind: ErrorKind::None, vertical: VerticalStructure::Uniform }
    }
    pub fn uniform_offset(sigma_m_s: f64) -> Self {
        OceanErrorModel { kind: ErrorKind::UniformOffset { sigma_m_s }, vertical: VerticalStructure::Uniform }
    }
    pub fn eddying(sigma_m_s: f64, length_scale_m: f64, time_scale_s: f64, modes: usize) -> Self {
        OceanErrorModel {
            kind: ErrorKind::Eddying { sigma_m_s, length_scale_m, time_scale_s, modes },
            vertical: VerticalStructure::Uniform,
        }
    }
    /// Draw the one realisation for a run (or an impact event) from its seed. Banded structures
    /// draw one independent realisation per band.
    pub fn realise(&self, seed: u64) -> OceanErrorRealisation {
        let nb = if matches!(self.vertical, VerticalStructure::Banded { .. }) { 4 } else { 1 };
        let bands = (0..nb).map(|b| self.realise_band(seed, b as u64)).collect();
        OceanErrorRealisation { model: *self, seed, bands }
    }

    fn realise_band(&self, seed: u64, band: u64) -> BandRealisation {
        let mut r = rng(seed, OCEAN_ERROR_STREAM - 3 * band);
        let mut n = || -> f64 { r.sample(StandardNormal) };
        let (offset, modes, amplitude) = match self.kind {
            ErrorKind::None => ([0.0; 2], vec![], 0.0),
            ErrorKind::UniformOffset { sigma_m_s } => ([sigma_m_s * n(), sigma_m_s * n()], vec![], 0.0),
            ErrorKind::Eddying { sigma_m_s, length_scale_m, time_scale_s, modes } => {
                let m: Vec<Mode> = (0..modes)
                    .map(|_| Mode {
                        k: [n() / length_scale_m, n() / length_scale_m, n() / length_scale_m],
                        omega: n() / time_scale_s,
                        phase: 0.0,
                    })
                    .collect();
                ([0.0; 2], m, sigma_m_s * length_scale_m * (2.0 / modes as f64).sqrt())
            }
        };
        let mut r2 = rng(seed, OCEAN_ERROR_STREAM - 3 * band - 1);
        let modes = modes
            .into_iter()
            .map(|mut m| {
                m.phase = r2.gen::<f64>() * std::f64::consts::TAU;
                m
            })
            .collect();
        BandRealisation { offset, modes, amplitude }
    }
}

#[derive(Clone, Debug)]
struct BandRealisation {
    offset: [f64; 2],
    modes: Vec<Mode>,
    amplitude: f64,
}

#[derive(Clone, Debug)]
struct Mode {
    k: [f64; 3],
    omega: f64,
    phase: f64,
}

/// One drawn ocean error, shared by every particle that uses it.
#[derive(Clone, Debug)]
pub struct OceanErrorRealisation {
    pub model: OceanErrorModel,
    pub seed: u64,
    bands: Vec<BandRealisation>,
}

impl OceanErrorRealisation {
    /// Error velocity east/north, m/s, at time `t`, position `p` and depth `depth_m` (0 at the
    /// surface), seabed depth unknown.
    pub fn velocity(&self, t: f64, p: LonLat, depth_m: f64) -> [f64; 2] {
        self.velocity_with_seabed(t, p, depth_m, None)
    }

    /// As [`Self::velocity`], with the local seabed depth so the near-bottom band can apply.
    pub fn velocity_with_seabed(&self, t: f64, p: LonLat, depth_m: f64, seabed_m: Option<f64>) -> [f64; 2] {
        let (band, f) = match self.model.vertical {
            VerticalStructure::Uniform => (0, 1.0),
            VerticalStructure::Exponential { efold_m, deep_ratio } => {
                (0, deep_ratio + (1.0 - deep_ratio) * (-depth_m / efold_m).exp())
            }
            VerticalStructure::Banded { surface_to_m, upper_to_m, near_bottom_m, factors } => {
                let b = if seabed_m.is_some_and(|s| s - depth_m <= near_bottom_m) {
                    BAND_NEAR_BOTTOM
                } else if depth_m <= surface_to_m {
                    BAND_SURFACE
                } else if depth_m <= upper_to_m {
                    BAND_UPPER
                } else {
                    BAND_DEEP
                };
                (b, factors[b])
            }
        };
        let br = &self.bands[band];
        if br.modes.is_empty() {
            return [f * br.offset[0], f * br.offset[1]];
        }
        let (r, e, n) = enu_basis(p);
        let x = [r[0] * EARTH_RADIUS_M, r[1] * EARTH_RADIUS_M, r[2] * EARTH_RADIUS_M];
        let mut g = [0.0f64; 2];
        for m in &br.modes {
            let s = (dot(m.k, x) + m.omega * t + m.phase).sin();
            g[0] += s * dot(m.k, e);
            g[1] += s * dot(m.k, n);
        }
        // grad psi = -A sum sin(.) k ; u = -d psi/dn, v = d psi/de
        let a = br.amplitude * f;
        [a * g[1], -a * g[0]]
    }
}
