//! The recovery-observation layer: from simulated beachings to the probability of the observed
//! finds (brief section 4), in the conditional form D5 of results/davey-ch11-alignment.md.
//!
//! Found items from source x form a thinned Poisson field with intensity lambda q(y | x) over
//! y = (along-coast position s, discovery time t), where
//!
//!   q(s, t | x) = (1/N) sum_i K_h(s - s_i) f_delay(t - t_i) P_I(seg(s), t)
//!
//! over the N released particles, i running over those that beached at (s_i, t_i) - particles that
//! never beach contribute nothing, and nothing is renormalised over survivors. K_h is a Gaussian of
//! declared bandwidth h (locality point versus true arrival point: explicit model error, not a
//! floor); f_delay is the declared arrival-to-discovery delay (ARRIVAL AND DISCOVERY ARE DIFFERENT
//! QUANTITIES; the delay is modelled, never chosen to fit); P_I is RELATIVE identification
//! probability, piecewise constant by coast segment and time period. Q(x) is the integral of q over
//! all segments and over [0, window_end].
//!
//! Under the scale-invariant prior p(lambda) ~ 1/lambda the count term integrates to Gamma(N)/N!,
//! independent of Q(x), so the likelihood of N finds is exactly
//!
//!   L(x) = prod_j q(y_j | x) / Q(x),
//!
//! Consequences, all intended and all tested: lambda drops out; a constant factor in P_I cancels;
//! the absolute arrival probability cancels (only the distribution of identified items over coast
//! and time matters); and a source sending items to a coast with high P_I where nothing was found
//! (Western Australia) is penalised through Q(x). The price is the information in the count
//! itself, given up under the vague prior on lambda. A reported discovery interval [a, b] is
//! treated as a uniform date within it. Per object class c the field has its own lambda_c, so the
//! factor for object j is q_c(y_j)/Q_c; a class with no finds is uninformative under this prior.

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

/// Relative identification probability by coast segment and time period.
#[derive(Debug, Clone)]
pub struct Identification {
    /// Segment boundaries along the coast, km, increasing; segment k is [edges[k], edges[k+1]).
    pub edges_km: Vec<f64>,
    /// Period boundaries, days after release, increasing; period p is [breaks[p-1], breaks[p]),
    /// with period 0 before breaks[0] and the last after breaks[last].
    pub breaks_days: Vec<f64>,
    /// rel[k][p] >= 0. Only ratios matter.
    pub rel: Vec<Vec<f64>>,
}

impl Identification {
    pub fn uniform(edges_km: Vec<f64>) -> Self {
        let n = edges_km.len() - 1;
        Identification { edges_km, breaks_days: vec![], rel: vec![vec![1.0]; n] }
    }
    pub fn validate(&self) -> Result<(), String> {
        let ns = self.edges_km.len().saturating_sub(1);
        if ns == 0 || self.rel.len() != ns {
            return Err(format!("identification: {} segments but {} rows", ns, self.rel.len()));
        }
        if self.rel.iter().any(|r| r.len() != self.breaks_days.len() + 1 || r.iter().any(|v| !(*v >= 0.0))) {
            return Err("identification: each row needs breaks+1 non-negative values".into());
        }
        if self.edges_km.windows(2).any(|w| w[1] <= w[0]) || self.breaks_days.windows(2).any(|w| w[1] <= w[0]) {
            return Err("identification: edges and breaks must increase".into());
        }
        Ok(())
    }
    pub fn segment(&self, s: f64) -> Option<usize> {
        if s < self.edges_km[0] || s >= *self.edges_km.last().unwrap() {
            return None;
        }
        Some(self.edges_km.partition_point(|&e| e <= s) - 1)
    }
    /// Integral over t in [a, b] of f_delay(t - t0) P_I(k, t) dt.
    fn delay_integral(&self, k: usize, t0: f64, a: f64, b: f64, delay: &Delay) -> f64 {
        let mut cuts = vec![a];
        cuts.extend(self.breaks_days.iter().copied().filter(|&x| x > a && x < b));
        cuts.push(b);
        let mut acc = 0.0;
        for w in cuts.windows(2) {
            let p = self.breaks_days.partition_point(|&x| x <= w[0]);
            let r = self.rel[k][p];
            if r > 0.0 {
                acc += r * (delay.cdf(w[1] - t0) - delay.cdf(w[0] - t0));
            }
        }
        acc
    }
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
    pub s_km: f64,
    pub t_days: f64,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Observation {
    pub id: String,
    pub class: usize,
    pub s_km: f64,
    /// Discovery interval, days after release; a single reported day d is [d, d + 1).
    pub t_start_days: f64,
    pub t_end_days: f64,
}

#[derive(Debug, Clone)]
pub struct Recovery {
    pub ident: Identification,
    pub delay: Delay,
    pub bandwidth_km: f64,
    pub window_end_days: f64,
}

/// One observation's factor, with its Monte Carlo quality.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Factor {
    pub q: f64,
    /// Effective number of particles contributing to q (Kish).
    pub n_eff: f64,
}

impl Recovery {
    /// q(y_j | x) for one observation from one ensemble of `n_released` particles.
    pub fn q(&self, obs: &Observation, arrivals: &[Arrival], n_released: usize) -> Factor {
        let Some(k) = self.ident.segment(obs.s_km) else {
            return Factor { q: 0.0, n_eff: 0.0 };
        };
        let h = self.bandwidth_km;
        let norm = 1.0 / (h * (std::f64::consts::TAU).sqrt());
        let width = obs.t_end_days - obs.t_start_days;
        let (mut s1, mut s2) = (0.0, 0.0);
        for a in arrivals {
            let z = (obs.s_km - a.s_km) / h;
            if z.abs() > 40.0 {
                continue;
            }
            let c = norm * (-0.5 * z * z).exp()
                * self.ident.delay_integral(k, a.t_days, obs.t_start_days, obs.t_end_days, &self.delay)
                / width;
            s1 += c;
            s2 += c * c;
        }
        Factor { q: s1 / n_released as f64, n_eff: if s2 > 0.0 { s1 * s1 / s2 } else { 0.0 } }
    }

    /// Q(x): the expected identified fraction over all segments and [0, window_end].
    pub fn q_total(&self, arrivals: &[Arrival], n_released: usize) -> f64 {
        let h = self.bandwidth_km;
        let e = &self.ident.edges_km;
        let mut acc = 0.0;
        for a in arrivals {
            for k in 0..e.len() - 1 {
                let mass = phi((e[k + 1] - a.s_km) / h) - phi((e[k] - a.s_km) / h);
                if mass > 1e-15 {
                    acc += mass * self.ident.delay_integral(k, a.t_days, 0.0, self.window_end_days, &self.delay);
                }
            }
        }
        acc / n_released as f64
    }
}
