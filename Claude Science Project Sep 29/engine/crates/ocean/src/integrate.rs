//! The batch forward integrator drift and Pleiades call.
//!
//! Given N particles, each with a release position, release time and persistent
//! [`ObjectResponse`], integrate forward to the last caller-chosen output time and return, per
//! particle, a [`Snapshot`] at every output time plus the termination [`Event`]s: beaching with a
//! coast-segment ID and time, leaving the domain, and field gaps (land in the product mask,
//! outside the time axis, non-finite values), each flagged as itself.
//!
//! Velocity, never pre-summed by a product:
//! `v = u_current + a_stokes*u_stokes + c_wind*R(leeway_angle)*U10
//!      + leeway_speed*R(leeway_angle)*U10/|U10| + u_ocean_error + u_random_flight`,
//! then a random-walk displacement after the step if that diffusion model is chosen.
//! RK2 midpoint on the sphere with a fixed step, shortened to land exactly on output times.

use crate::coast::{Coastline, LineId, SegmentId};
use crate::field::{Component, FieldGap, VectorField};
use crate::products::Inclusion;
use crate::stochastic::{rng, Diffusion, OceanErrorModel, OceanErrorRealisation};
use crate::{displace, LonLat, OCEAN_MODEL_ALTERNATIVE};
use rand::Rng;
use rand_distr::StandardNormal;
use rayon::prelude::*;
use serde::Serialize;

/// Per-particle object response, persistent for the whole integration (never redrawn per step).
#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub struct ObjectResponse {
    /// Multiplier on the product's surface Stokes drift.
    pub a_stokes: f64,
    /// Leeway coefficient on the 10 m wind.
    pub c_wind: f64,
    /// Deflection of the `c_wind` term from downwind, degrees, positive clockwise (to the right of
    /// downwind). Default 0: CSIRO's proportional windage is downwind (ruling D-f).
    pub wind_angle_deg: f64,
    /// Deflection of the constant-magnitude term `leeway_speed_mps` from downwind, degrees, positive
    /// clockwise; CSIRO's "16 deg left of downwind" is -16. Applies to that term only: CSIRO rotates
    /// only the extra leeway (Griffin et al. 2017 Part II p. 13, Fig. 3.1 caption; ruling D-f).
    pub leeway_angle_deg: f64,
    /// Constant-magnitude leeway, m/s, along the downwind direction rotated by `leeway_angle_deg`
    /// (CSIRO 2017 Part II flaperon response; ruling D-d). Zero when |U10| < [`LEEWAY_CALM_WIND_MPS`].
    pub leeway_speed_mps: f64,
}

/// Below this 10 m wind speed the downwind direction is undefined and the constant-magnitude
/// leeway is zero (declared; recorded in provenance).
pub const LEEWAY_CALM_WIND_MPS: f64 = 0.5;

impl ObjectResponse {
    pub fn new(a_stokes: f64, c_wind: f64) -> Self {
        ObjectResponse { a_stokes, c_wind, wind_angle_deg: 0.0, leeway_angle_deg: 0.0, leeway_speed_mps: 0.0 }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub struct Particle {
    pub release: LonLat,
    /// Unix seconds UTC.
    pub release_time: f64,
    pub response: ObjectResponse,
    /// The particle's own stopping time (settling's float phase ends at each element's sink time).
    /// `None`: run to the last output time. The state at this time is [`Track::end`]; output
    /// times after it are [`Snapshot::PastEnd`].
    pub end_time: Option<f64>,
}

impl Particle {
    pub fn new(release: LonLat, release_time: f64, response: ObjectResponse) -> Self {
        Particle { release, release_time, response, end_time: None }
    }
}

/// The separate velocity components. The product is a run argument: swap these fields and nothing
/// in the consumer changes.
#[derive(Clone, Copy)]
pub struct Forcing<'a> {
    pub current: &'a dyn VectorField,
    pub stokes: Option<&'a dyn VectorField>,
    pub wind10: Option<&'a dyn VectorField>,
}

impl Forcing<'_> {
    /// The value this run takes for the `ocean-model` alternative: the products of the components
    /// in use, joined by `+`.
    ///
    /// A run on a comparison-only product (OSCAR) is labelled `comparison:<ids>`: it is not a value of
    /// the alternative, and a module must not declare it to the composer.
    pub fn ocean_model(&self) -> String {
        let mut ids = vec![self.current.meta().product.clone()];
        ids.extend(self.stokes.map(|f| f.meta().product.clone()));
        ids.extend(self.wind10.map(|f| f.meta().product.clone()));
        let label = ids.join("+");
        if self.is_comparison() { format!("comparison:{label}") } else { label }
    }

    /// True when any component is a comparison-only product (`ProductRole::Comparison`).
    pub fn is_comparison(&self) -> bool {
        let comp = |f: &dyn VectorField| crate::products::product(&f.meta().product).map_or(false, |p| p.role == crate::products::ProductRole::Comparison);
        comp(self.current) || self.stokes.map_or(false, comp) || self.wind10.map_or(false, comp)
    }
}

/// Integration domain; leaving it ends a trajectory with [`Event::LeftDomain`].
#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub struct Domain {
    pub lon_min: f64,
    pub lon_max: f64,
    pub lat_min: f64,
    pub lat_max: f64,
}

impl Domain {
    pub fn contains(&self, p: LonLat) -> bool {
        p[0] >= self.lon_min && p[0] <= self.lon_max && p[1] >= self.lat_min && p[1] <= self.lat_max
    }
}

/// Refloat hook after beaching. Off by default.
#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub enum Refloat {
    Off,
    /// Refloat with probability 1 - exp(-rate dt) per step, returning to the last sea position.
    RatePerDay(f64),
}

pub struct RunSpec<'a> {
    pub forcing: Forcing<'a>,
    pub coast: &'a dyn Coastline,
    pub domain: Domain,
    pub step_s: f64,
    /// Ascending unix seconds; the run ends at the last.
    pub output_times: Vec<f64>,
    pub diffusion: Diffusion,
    pub ocean_error: OceanErrorModel,
    pub refloat: Refloat,
    pub seed: u64,
    /// Drift declares that its fitted leeway already absorbs Stokes drift (arXiv:2005.09527).
    pub leeway_absorbs_stokes: bool,
    /// Accept a current whose Stokes content is `Partial` or `Unknown`. Recorded in provenance.
    pub accept_partial_stokes_overlap: bool,
    /// A constant-magnitude leeway was fitted as a residual on top of explicit Stokes drift, so
    /// `leeway_speed_mps > 0` with `a_stokes > 0` is allowed. Otherwise that combination is the
    /// transplanted-system error (drift review E1) and is refused. Recorded in provenance.
    pub explicit_residual: bool,
    /// Worker threads; 0 lets rayon choose. Results do not depend on it.
    pub threads: usize,
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub enum Event {
    /// `snapped_m > 0`: a land-mask stranding moved that far onto the coastline's shore.
    Beached { t: f64, at: LonLat, segment: SegmentId, line: LineId, chainage_m: f64, snapped_m: f64 },
    Refloated { t: f64, at: LonLat },
    LeftDomain { t: f64, at: LonLat },
    /// A field had no value: `Land` here means stranded in the product's land mask before the
    /// coastline was reached, and further than the coastline's snap distance from its shore.
    FieldGap { t: f64, at: LonLat, component: Component, gap: FieldGap },
    NonFinitePosition { t: f64 },
    ReleasedOnLand { t: f64, at: LonLat },
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub enum Snapshot {
    NotReleased,
    Afloat(LonLat),
    Beached { at: LonLat, segment: SegmentId, line: LineId, chainage_m: f64, snapped_m: f64 },
    /// The trajectory ended for a reason other than beaching; see the events.
    Ended,
    /// After the particle's own `end_time`.
    PastEnd,
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize)]
pub enum Fate {
    Afloat,
    Beached,
    LeftDomain,
    FieldGap,
    NonFinite,
    ReleasedOnLand,
}

#[derive(Clone, Debug, Serialize)]
pub struct Track {
    pub snapshots: Vec<Snapshot>,
    pub events: Vec<Event>,
    pub fate: Fate,
    /// State at the particle's own `end_time`, when it has one (`Ended` if it terminated first).
    pub end: Option<Snapshot>,
}

#[derive(Clone, Debug, Serialize)]
pub struct Provenance {
    pub alternative: &'static str,
    pub ocean_model: String,
    pub current: String,
    pub stokes: Option<String>,
    pub wind10: Option<String>,
    pub coast: String,
    pub step_s: f64,
    pub diffusion: Diffusion,
    pub diffusion_application: &'static str,
    pub ocean_error: OceanErrorModel,
    pub refloat: Refloat,
    pub seed: u64,
    pub accept_partial_stokes_overlap: bool,
    pub explicit_residual: bool,
    pub leeway_calm_wind_mps: f64,
    pub integrator: &'static str,
}

#[derive(Clone, Debug, Serialize)]
pub struct RunOutput {
    pub output_times: Vec<f64>,
    pub tracks: Vec<Track>,
    pub provenance: Provenance,
}

/// Why a run was refused before integrating.
#[derive(Clone, Debug, PartialEq)]
pub enum CompositionError {
    MissingComponent(Component),
    WrongComponent { expected: Component, got: Component },
    /// Stokes drift would be counted twice.
    DoubleCount(String),
    BadSpec(String),
}

fn check(spec: &RunSpec, particles: &[Particle]) -> Result<(), CompositionError> {
    let f = &spec.forcing;
    for (field, expected) in [(Some(f.current), Component::Current), (f.stokes, Component::StokesDrift), (f.wind10, Component::Wind10m)] {
        if let Some(field) = field {
            if field.meta().component != expected {
                return Err(CompositionError::WrongComponent { expected, got: field.meta().component });
            }
        }
    }
    if !(spec.step_s > 0.0) || spec.output_times.is_empty() || spec.output_times.windows(2).any(|w| !(w[1] > w[0])) {
        return Err(CompositionError::BadSpec("step must be positive and output times non-empty and ascending".into()));
    }
    let uses_stokes = particles.iter().any(|p| p.response.a_stokes != 0.0);
    let uses_wind = particles.iter().any(|p| p.response.c_wind != 0.0 || p.response.leeway_speed_mps != 0.0);
    if !spec.explicit_residual && particles.iter().any(|p| p.response.leeway_speed_mps > 0.0 && p.response.a_stokes > 0.0) {
        return Err(CompositionError::DoubleCount(
            "leeway_speed_mps > 0 with a_stokes > 0: a response measured without explicit Stokes is being \
             transplanted; set explicit_residual only for a residual fitted on top of explicit Stokes"
                .into(),
        ));
    }
    if uses_stokes && f.stokes.is_none() {
        return Err(CompositionError::MissingComponent(Component::StokesDrift));
    }
    if uses_wind && f.wind10.is_none() {
        return Err(CompositionError::MissingComponent(Component::Wind10m));
    }
    if uses_stokes {
        let c = &f.current.meta().contents;
        match c.stokes {
            Inclusion::Included => {
                return Err(CompositionError::DoubleCount(format!("current {} already contains Stokes drift", f.current.meta().product)))
            }
            Inclusion::Partial | Inclusion::Unknown if !spec.accept_partial_stokes_overlap => {
                return Err(CompositionError::DoubleCount(format!(
                    "current {} may contain Stokes drift ({:?}); set accept_partial_stokes_overlap to proceed",
                    f.current.meta().product,
                    c.stokes
                )))
            }
            _ => {}
        }
        if spec.leeway_absorbs_stokes {
            return Err(CompositionError::DoubleCount("the leeway is declared to absorb Stokes drift".into()));
        }
    }
    Ok(())
}

struct Ctx<'a> {
    spec: &'a RunSpec<'a>,
    error: &'a OceanErrorRealisation,
}

impl Ctx<'_> {
    fn velocity(&self, r: &ObjectResponse, t: f64, p: LonLat, flight: [f64; 2]) -> Result<[f64; 2], (Component, FieldGap)> {
        let f = &self.spec.forcing;
        let get = |field: &dyn VectorField, c: Component| -> Result<[f64; 2], (Component, FieldGap)> {
            let v = field.sample(t, p).map_err(|g| (c, g))?;
            if v[0].is_finite() && v[1].is_finite() { Ok(v) } else { Err((c, FieldGap::NonFinite)) }
        };
        let mut v = get(f.current, Component::Current)?;
        if r.a_stokes != 0.0 {
            let s = get(f.stokes.expect("checked"), Component::StokesDrift)?;
            v[0] += r.a_stokes * s[0];
            v[1] += r.a_stokes * s[1];
        }
        if r.c_wind != 0.0 || r.leeway_speed_mps != 0.0 {
            let w = get(f.wind10.expect("checked"), Component::Wind10m)?;
            let rot = |deg: f64| {
                let (sn, cs) = deg.to_radians().sin_cos();
                [w[0] * cs + w[1] * sn, -w[0] * sn + w[1] * cs]
            };
            if r.c_wind != 0.0 {
                let a = rot(r.wind_angle_deg);
                v[0] += r.c_wind * a[0];
                v[1] += r.c_wind * a[1];
            }
            let speed = w[0].hypot(w[1]);
            if r.leeway_speed_mps != 0.0 && speed >= LEEWAY_CALM_WIND_MPS {
                let b = rot(r.leeway_angle_deg);
                let k = r.leeway_speed_mps / speed;
                v[0] += k * b[0];
                v[1] += k * b[1];
            }
        }
        let e = self.error.velocity(t, p, 0.0);
        Ok([v[0] + e[0] + flight[0], v[1] + e[1] + flight[1]])
    }

    fn run_one(&self, index: usize, particle: &Particle) -> Track {
        let spec = self.spec;
        let times = &spec.output_times;
        let mut g = rng(spec.seed, index as u64);
        let mut snapshots = Vec::with_capacity(times.len());
        let mut events = Vec::new();
        let mut k = 0;
        while k < times.len() && times[k] < particle.release_time {
            snapshots.push(Snapshot::NotReleased);
            k += 1;
        }
        let stop = particle.end_time.unwrap_or(f64::INFINITY);
        let own_end = |fill: Snapshot| particle.end_time.map(|_| if matches!(fill, Snapshot::NotReleased) { Snapshot::NotReleased } else { fill });
        let end = |mut snaps: Vec<Snapshot>, fill: Snapshot, events: Vec<Event>, fate: Fate| {
            let n0 = snaps.len();
            snaps.resize(times.len(), fill);
            for (k, s) in snaps.iter_mut().enumerate().skip(n0) {
                if times[k] > stop {
                    *s = Snapshot::PastEnd;
                }
            }
            Track { snapshots: snaps, events, fate, end: own_end(fill) }
        };
        let (mut t, mut p) = (particle.release_time, particle.release);
        if k == times.len() && particle.end_time.is_none() {
            return end(snapshots, Snapshot::NotReleased, events, Fate::Afloat);
        }
        if spec.coast.is_land(p) {
            events.push(Event::ReleasedOnLand { t, at: p });
            return end(snapshots, Snapshot::Ended, events, Fate::ReleasedOnLand);
        }
        if !spec.domain.contains(p) {
            events.push(Event::LeftDomain { t, at: p });
            return end(snapshots, Snapshot::Ended, events, Fate::LeftDomain);
        }
        let (flight_sigma, tl) = match spec.diffusion {
            Diffusion::RandomFlight { sigma_m_s, lagrangian_time_s } => (sigma_m_s, lagrangian_time_s),
            _ => (0.0, 1.0),
        };
        let mut flight = [flight_sigma * g.sample::<f64, _>(StandardNormal), flight_sigma * g.sample::<f64, _>(StandardNormal)];
        // Some((point, segment, last sea position)) while beached with refloat on.
        let mut beached: Option<(Snapshot, LonLat)> = None;
        let r = &particle.response;
        let horizon = particle.end_time.unwrap_or(times[times.len() - 1]);
        let mut end_state: Option<Snapshot> = None;
        loop {
            let out_t = if k < times.len() { times[k] } else { f64::INFINITY };
            let target = out_t.min(horizon);
            if target < t - 1e-6 {
                break;
            }
            while t < target - 1e-6 {
                let dt = spec.step_s.min(target - t);
                if let Some((_, sea)) = beached {
                    let Refloat::RatePerDay(rate) = spec.refloat else { unreachable!() };
                    if g.gen::<f64>() < 1.0 - (-rate * dt / 86_400.0).exp() {
                        beached = None;
                        p = sea;
                        events.push(Event::Refloated { t: t + dt, at: p });
                    }
                    t += dt;
                    continue;
                }
                if flight_sigma > 0.0 {
                    let rho = (-dt / tl).exp();
                    let s = flight_sigma * (1.0 - rho * rho).sqrt();
                    flight = [rho * flight[0] + s * g.sample::<f64, _>(StandardNormal), rho * flight[1] + s * g.sample::<f64, _>(StandardNormal)];
                }
                let step = (|| {
                    let v1 = self.velocity(r, t, p, flight)?;
                    let pm = displace(p, v1[0] * dt * 0.5, v1[1] * dt * 0.5);
                    let v2 = self.velocity(r, t + 0.5 * dt, pm, flight)?;
                    Ok(displace(p, v2[0] * dt, v2[1] * dt))
                })();
                let (pn, hit_at) = match step {
                    Err((component, gap)) => match (gap, spec.coast.snap(p)) {
                        (FieldGap::Land, Some(hit)) => (p, Some((hit, t))),
                        _ => {
                            events.push(Event::FieldGap { t, at: p, component, gap });
                            return end(snapshots, Snapshot::Ended, events, Fate::FieldGap);
                        }
                    },
                    Ok(mut pn) => {
                        let sw = spec.diffusion.walk_sigma_m(dt);
                        if sw > 0.0 {
                            pn = displace(pn, sw * g.sample::<f64, _>(StandardNormal), sw * g.sample::<f64, _>(StandardNormal));
                        }
                        if !(pn[0].is_finite() && pn[1].is_finite()) {
                            events.push(Event::NonFinitePosition { t: t + dt });
                            return end(snapshots, Snapshot::Ended, events, Fate::NonFinite);
                        }
                        let hit = spec.coast.first_crossing(p, pn);
                        (pn, hit.map(|h| (h, t + h.fraction * dt)))
                    }
                };
                if let Some((hit, th)) = hit_at {
                    events.push(Event::Beached { t: th, at: hit.point, segment: hit.segment, line: hit.line, chainage_m: hit.chainage_m, snapped_m: hit.snapped_m });
                    let snap = Snapshot::Beached { at: hit.point, segment: hit.segment, line: hit.line, chainage_m: hit.chainage_m, snapped_m: hit.snapped_m };
                    match spec.refloat {
                        Refloat::Off => {
                            snapshots.push(snap);
                            return end(snapshots, snap, events, Fate::Beached);
                        }
                        Refloat::RatePerDay(_) => {
                            beached = Some((snap, p));
                            p = hit.point;
                            t += dt;
                            continue;
                        }
                    }
                }
                if !spec.domain.contains(pn) {
                    events.push(Event::LeftDomain { t: t + dt, at: pn });
                    return end(snapshots, Snapshot::Ended, events, Fate::LeftDomain);
                }
                p = pn;
                t += dt;
            }
            let here = match beached {
                Some((snap, _)) => snap,
                None => Snapshot::Afloat(p),
            };
            if k < times.len() && out_t <= target + 1e-6 {
                snapshots.push(here);
                k += 1;
            }
            if t >= horizon - 1e-6 {
                if particle.end_time.is_some() {
                    end_state = Some(here);
                }
                break;
            }
        }
        while k < times.len() {
            snapshots.push(if times[k] > stop { Snapshot::PastEnd } else { Snapshot::NotReleased });
            k += 1;
        }
        let fate = if beached.is_some() { Fate::Beached } else { Fate::Afloat };
        Track { snapshots, events, fate, end: end_state }
    }
}

/// Integrate every particle through one ocean. Refuses compositions that count a component twice.
pub fn integrate(spec: &RunSpec, particles: &[Particle]) -> Result<RunOutput, CompositionError> {
    check(spec, particles)?;
    let error = spec.ocean_error.realise(spec.seed);
    let ctx = Ctx { spec, error: &error };
    let work = || particles.par_iter().enumerate().map(|(i, p)| ctx.run_one(i, p)).collect::<Vec<_>>();
    let tracks = if spec.threads == 0 {
        work()
    } else {
        rayon::ThreadPoolBuilder::new()
            .num_threads(spec.threads)
            .build()
            .map_err(|e| CompositionError::BadSpec(e.to_string()))?
            .install(work)
    };
    let f = &spec.forcing;
    Ok(RunOutput {
        output_times: spec.output_times.clone(),
        tracks,
        provenance: Provenance {
            alternative: OCEAN_MODEL_ALTERNATIVE,
            ocean_model: f.ocean_model(),
            current: f.current.meta().description.clone(),
            stokes: f.stokes.map(|s| s.meta().description.clone()),
            wind10: f.wind10.map(|s| s.meta().description.clone()),
            coast: spec.coast.label(),
            step_s: spec.step_s,
            diffusion: spec.diffusion,
            diffusion_application: spec.diffusion.application(),
            ocean_error: spec.ocean_error,
            refloat: spec.refloat,
            seed: spec.seed,
            accept_partial_stokes_overlap: spec.accept_partial_stokes_overlap,
            explicit_residual: spec.explicit_residual,
            leeway_calm_wind_mps: LEEWAY_CALM_WIND_MPS,
            integrator: "RK2 midpoint on the sphere, fixed step shortened to output times",
        },
    })
}
