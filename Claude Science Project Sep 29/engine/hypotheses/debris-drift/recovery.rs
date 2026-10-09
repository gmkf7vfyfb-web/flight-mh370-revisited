//! The recovery-observation layer: from simulated beachings to the probability of the observed
//! finds (brief section 4), in the conditional form D5 of results/davey-ch11-alignment.md, with
//! the find episodes of grouping G1 (results/debris-drift-find-episodes.md, ruled the working
//! default on 9 October).
//!
//! Found items of class c from source x form a thinned Poisson field with intensity
//! lambda_c q_c(y | x, nu) over y = (place on the coast, discovery time), where
//!
//!   q_c(y | x, nu) = (1/N) sum_i K_h(d(y, y_i)) f_delay(t - t_i) nu[seg(y), period(t)]
//!
//! over the N released particles of class c, i running over those that beached at (y_i, t_i).
//! Particles that never beach contribute nothing and nothing is renormalised over survivors. K_h is
//! a Gaussian of declared bandwidth h per km of coast (locality versus true arrival point: explicit
//! model error, not a floor); f_delay is the declared arrival-to-discovery delay (ARRIVAL AND
//! DISCOVERY ARE DIFFERENT QUANTITIES; the delay is modelled, never chosen to fit). Distance d is
//! along-coast chainage where the transport supplies it (same coast line only), and great-circle
//! distance otherwise (land-mask stranding before the real coastline exists; declared).
//!
//! **Detection blocks (G1).** nu is the RELATIVE identification level of block b = (coast
//! segment, discovery period). q and Q are linear in nu:
//!
//!   q_j = sum_b nu_b a_jb,   Q_c = sum_b nu_b A_cb,
//!
//! so the coefficients a and A are computed once per ensemble and the levels are marginalised by
//! cheap dot products over common draws. Under p(lambda_c) ~ 1/lambda_c the count term integrates
//! to Gamma(N)/N!, independent of Q, so the likelihood of the finds is exactly
//!
//!   L(x) = E_eta E_nu prod_j q_{c_j}(y_j | x, eta, nu) / Q_{c_j}(x | eta, nu),
//!
//! with the shared environment eta and the levels nu marginalised OUTSIDE the product over finds
//! (rule 8). Only a global constant in nu cancels; differences between blocks do not, which is
//! why the levels are latent with a declared prior (ruling of 9 October, correcting D5). A coast
//! outside every segment has nu = 0: absence there carries no information (the Western Australia
//! term is deferred by brief section 13 and enters only when a segment for it is declared).

/// Kernel contributions beyond this many bandwidths are not computed. A Gaussian tail at 20 sigma
/// is not a model of anything, and a find supported only by such tails is Monte Carlo unresolved
/// (more particles are needed), never scored from the tail: "not computed" is not "impossible",
/// and it is not a pseudo-likelihood either.
pub const KERNEL_CUTOFF_SIGMA: f64 = 6.0;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Delay {
    /// Uniform on [0, max_days].
    Uniform { max_days: f64 },
    /// Exponential with the given mean.
    Exponential { mean_days: f64 },
}

impl Delay {
    pub fn cdf(&self, d: f64) -> f64 {
        if d <= 0.0 {
            return 0.0;
        }
        match *self {
            Delay::Uniform { max_days } => (d / max_days).min(1.0),
            Delay::Exponential { mean_days } => 1.0 - (-d / mean_days).exp(),
        }
    }
}

/// A place on the coast: chainage on a coast line where the transport has one, and always the
/// geographic position.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Place {
    pub lonlat: [f64; 2],
    pub line: Option<u32>,
    pub s_km: f64,
}

impl Place {
    pub fn at(lonlat: [f64; 2]) -> Self {
        Place { lonlat, line: None, s_km: f64::NAN }
    }
    pub fn on_line(line: u32, s_km: f64, lonlat: [f64; 2]) -> Self {
        Place { lonlat, line: Some(line), s_km }
    }
}

/// Distance in km along the coast if both places are on chainage lines (infinite across lines),
/// great-circle otherwise.
pub fn coast_distance_km(a: &Place, b: &Place) -> f64 {
    match (a.line, b.line) {
        (Some(la), Some(lb)) => {
            if la == lb { (a.s_km - b.s_km).abs() } else { f64::INFINITY }
        }
        _ => great_circle_km(a.lonlat, b.lonlat),
    }
}

pub fn great_circle_km(a: [f64; 2], b: [f64; 2]) -> f64 {
    let (p1, p2) = (a[1].to_radians(), b[1].to_radians());
    let dl = (b[0] - a[0]).to_radians();
    let h = ((p2 - p1) / 2.0).sin().powi(2) + p1.cos() * p2.cos() * (dl / 2.0).sin().powi(2);
    2.0 * 6_371.008_8 * h.sqrt().min(1.0).asin()
}

/// Standard normal CDF via the complementary error function (Numerical Recipes erfcc,
/// fractional error below 1.2e-7).
pub fn phi(z: f64) -> f64 {
    let x = -z / std::f64::consts::SQRT_2;
    let t = 1.0 / (1.0 + 0.5 * x.abs());
    let y = t * (-x * x - 1.265_512_23 + t * (1.000_023_68 + t * (0.374_091_96 + t * (0.096_784_18
        + t * (-0.186_288_06 + t * (0.278_868_07 + t * (-1.135_203_98 + t * (1.488_515_87
        + t * (-0.822_152_23 + t * 0.170_872_77))))))))).exp();
    let erfc = if x >= 0.0 { y } else { 2.0 - y };
    0.5 * erfc
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Arrival {
    pub place: Place,
    /// Detection segment of the beaching point; None is a coast outside every segment.
    pub segment: Option<usize>,
    pub t_days: f64,
    /// Statistical weight of the trajectory: 1 for a released particle, 1/M for each of the M
    /// children of a split particle (`[splitting]`). Sums over released particles stay unbiased.
    pub w: f64,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Observation {
    pub id: String,
    pub class: usize,
    pub place: Place,
    pub segment: usize,
    /// Discovery interval, days after release; a single reported day d is [d, d + 1).
    pub t_start_days: f64,
    pub t_end_days: f64,
}

/// A segment's extent in chainage, for the exact kernel mass in Q when chainage exists.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Edge {
    pub line: u32,
    pub start_km: f64,
    pub end_km: f64,
    pub segment: usize,
}

#[derive(Debug, Clone)]
pub struct Recovery {
    pub n_segments: usize,
    /// Period boundaries, days after release, increasing; period p is [breaks[p-1], breaks[p]).
    pub breaks_days: Vec<f64>,
    pub edges: Vec<Edge>,
    pub delay: Delay,
    pub bandwidth_km: f64,
    pub window_end_days: f64,
}

/// The linear coefficients of one class ensemble. `a[j]` is non-zero only in the blocks of find
/// j's own segment.
#[derive(Debug, Clone, PartialEq)]
pub struct Coefficients {
    pub a: Vec<Vec<f64>>,
    pub big_a: Vec<f64>,
    /// Kish effective number of particles contributing to each find (levels all 1).
    pub n_eff: Vec<f64>,
    /// Number of particles with non-zero kernel weight for each find (inside the cut-off and
    /// before the find's interval ends). A sizing diagnostic: hits are Poisson in the particle count.
    pub hits: Vec<usize>,
}

impl Recovery {
    pub fn n_periods(&self) -> usize {
        self.breaks_days.len() + 1
    }
    pub fn n_blocks(&self) -> usize {
        self.n_segments * self.n_periods()
    }
    pub fn period(&self, t: f64) -> usize {
        self.breaks_days.partition_point(|&b| b <= t)
    }

    /// For each period p: integral over t in [a, b] intersect period p of f_delay(t - t0) dt.
    fn delay_by_period(&self, t0: f64, a: f64, b: f64, out: &mut [f64]) {
        let mut cuts = vec![a];
        cuts.extend(self.breaks_days.iter().copied().filter(|&x| x > a && x < b));
        cuts.push(b);
        for w in cuts.windows(2) {
            let p = self.period(w[0]);
            out[p] += self.delay.cdf(w[1] - t0) - self.delay.cdf(w[0] - t0);
        }
    }

    /// Kernel mass of an arrival in each segment, for Q: exact over chainage edges when the
    /// arrival is on a line with edges, otherwise all its mass in its own segment.
    fn segment_mass(&self, a: &Arrival, out: &mut Vec<(usize, f64)>) {
        out.clear();
        if let Some(line) = a.place.line {
            let mut any = false;
            for e in self.edges.iter().filter(|e| e.line == line) {
                any = true;
                let m = phi((e.end_km - a.place.s_km) / self.bandwidth_km) - phi((e.start_km - a.place.s_km) / self.bandwidth_km);
                if m > 1e-15 {
                    out.push((e.segment, m));
                }
            }
            if any {
                return;
            }
        }
        if let Some(s) = a.segment {
            out.push((s, 1.0));
        }
    }

    /// Coefficients for the finds `obs` (all of this ensemble's class) from `arrivals` out of
    /// `n_released` particles.
    pub fn coefficients(&self, obs: &[&Observation], arrivals: &[Arrival], n_released: usize) -> Coefficients {
        let (np, nb) = (self.n_periods(), self.n_blocks());
        let n = n_released as f64;
        let h = self.bandwidth_km;
        let norm = 1.0 / (h * std::f64::consts::TAU.sqrt());
        let mut a = vec![vec![0.0; nb]; obs.len()];
        let mut n_eff = vec![0.0; obs.len()];
        let mut hits = vec![0usize; obs.len()];
        let mut tmp = vec![0.0; np];
        for (j, o) in obs.iter().enumerate() {
            let width = o.t_end_days - o.t_start_days;
            let (mut s1, mut s2) = (0.0, 0.0);
            for ar in arrivals {
                let z = coast_distance_km(&o.place, &ar.place) / h;
                if !(z <= KERNEL_CUTOFF_SIGMA) || ar.t_days >= o.t_end_days {
                    continue;
                }
                tmp.iter_mut().for_each(|x| *x = 0.0);
                self.delay_by_period(ar.t_days, o.t_start_days, o.t_end_days, &mut tmp);
                let k = norm * (-0.5 * z * z).exp() / width;
                let mut c = 0.0;
                for p in 0..np {
                    let v = ar.w * k * tmp[p];
                    a[j][o.segment * np + p] += v / n;
                    c += v;
                }
                s1 += c;
                s2 += c * c;
                if c > 0.0 {
                    hits[j] += 1;
                }
            }
            n_eff[j] = if s2 > 0.0 { s1 * s1 / s2 } else { 0.0 };
        }
        let mut big_a = vec![0.0; nb];
        let mut mass = Vec::new();
        for ar in arrivals {
            if ar.t_days >= self.window_end_days {
                continue;
            }
            self.segment_mass(ar, &mut mass);
            if mass.is_empty() {
                continue;
            }
            tmp.iter_mut().for_each(|x| *x = 0.0);
            self.delay_by_period(ar.t_days, 0.0, self.window_end_days, &mut tmp);
            for &(s, m) in &mass {
                for p in 0..np {
                    big_a[s * np + p] += ar.w * m * tmp[p] / n;
                }
            }
        }
        Coefficients { a, big_a, n_eff, hits }
    }
}

pub fn dot(a: &[f64], b: &[f64]) -> f64 {
    a.iter().zip(b).map(|(x, y)| x * y).sum()
}

/// The declared prior on the relative identification levels: ln nu_b ~ N(mu[period(b)], sigma^2)
/// independently by block (G1, first pass), realised as `draws` common draws shared by every
/// source node, so that the likelihood surface is smooth in the levels' Monte Carlo error.
#[derive(Debug, Clone, PartialEq)]
pub struct LevelDraws {
    pub draws: Vec<Vec<f64>>,
}

impl LevelDraws {
    pub fn new(n_segments: usize, ln_mean_by_period: &[f64], sigma: f64, draws: usize, seed: u64) -> Self {
        let np = ln_mean_by_period.len();
        let mut rng = super::rng::Rng::derive(&[seed, 0x1E_7E15]);
        let d = draws.max(1);
        let draws = (0..d)
            .map(|_| (0..n_segments * np).map(|b| (ln_mean_by_period[b % np] + sigma * rng.normal()).exp()).collect())
            .collect();
        LevelDraws { draws }
    }
    #[cfg_attr(not(test), allow(dead_code))]
    pub fn fixed(levels: Vec<f64>) -> Self {
        LevelDraws { draws: vec![levels] }
    }
}
