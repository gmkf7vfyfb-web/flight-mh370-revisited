//! Sinking physics for one element: terminal speed, and the path from first water contact to
//! first seabed contact through a depth-varying current (rule 9: the calculation stops there).
//!
//! Ported from the previous harness's `physics.rs` (terminal speed, element description, glide
//! memory model, generator), rewritten from moments to sample paths: the descent is integrated
//! layer by layer, dt = dz / w(z), so a current that changes with depth and a seabed that
//! changes with position are both honoured, and the ocean error is one realisation per event
//! passed in by the caller rather than drawn per element.

use serde::Deserialize;

use super::ocean_stub::{BelowModelBottom, ErrorModel, Profile};

/// Standard gravity (m/s2).
pub const GRAVITY: f64 = 9.80665;

/// A parameter: fixed, uniform, or log-uniform (for scale parameters) on [lo, hi].
#[derive(Debug, Clone, Copy, PartialEq, Deserialize)]
#[serde(try_from = "RangeSpec")]
pub struct Range {
    pub lo: f64,
    pub hi: f64,
    pub log: bool,
}

#[derive(Deserialize)]
#[serde(untagged)]
enum RangeSpec {
    Fixed(f64),
    Uniform { uniform: [f64; 2] },
    LogUniform { log_uniform: [f64; 2] },
}

impl TryFrom<RangeSpec> for Range {
    type Error = String;
    fn try_from(spec: RangeSpec) -> Result<Self, String> {
        let range = match spec {
            RangeSpec::Fixed(x) => Range { lo: x, hi: x, log: false },
            RangeSpec::Uniform { uniform: [lo, hi] } => Range { lo, hi, log: false },
            RangeSpec::LogUniform { log_uniform: [lo, hi] } => Range { lo, hi, log: true },
        };
        if !(range.lo.is_finite() && range.hi.is_finite() && range.lo <= range.hi) || (range.log && range.lo <= 0.0) {
            return Err(format!("bad range [{}, {}]", range.lo, range.hi));
        }
        Ok(range)
    }
}

impl Range {
    /// The value at quantile `q`.
    pub fn quantile(&self, q: f64) -> f64 {
        if self.log {
            (self.lo.ln() + q * (self.hi.ln() - self.lo.ln())).exp()
        } else {
            self.lo + q * (self.hi - self.lo)
        }
    }

    pub fn draw(&self, rng: &mut Rng) -> f64 {
        self.quantile(rng.uniform())
    }
}

/// Steady terminal sinking speed (m/s) of a flooded body falling broadside:
/// w = sqrt(2 g s (1 - rho_w / rho_m) / (rho_w Cd)), where s is its mass per unit projected
/// area (kg/m2), rho_m its material density, rho_w the in-situ water density and Cd its drag
/// coefficient. Submerged weight m g (1 - rho_w / rho_m) balances drag rho_w Cd A w^2 / 2; only
/// m / A matters, not size. NaN if the body is not denser than the water.
pub fn terminal_speed(areal_density_kg_m2: f64, material_density_kg_m3: f64, drag_coefficient: f64, water_density_kg_m3: f64) -> f64 {
    let buoyancy = 1.0 - water_density_kg_m3 / material_density_kg_m3;
    if !(buoyancy > 0.0) {
        return f64::NAN;
    }
    (2.0 * GRAVITY * areal_density_kg_m2 * buoyancy / (water_density_kg_m3 * drag_coefficient)).sqrt()
}

/// One element class in one breakup family: the distributions of what sets where it rests.
/// All ranges are independent and drawn per representative element.
#[derive(Debug, Clone, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Element {
    /// Mass per unit projected area in its falling attitude (kg/m2).
    pub areal_density_kg_m2: Range,
    /// Density of the flooded element's material mix (kg/m3), above sea water's.
    pub material_density_kg_m3: Range,
    pub drag_coefficient: Range,
    /// Mean descent speed over the steady broadside terminal speed: above one for bodies that
    /// flutter or tumble and spend part of the fall edge-on.
    pub descent_factor: Range,
    /// Horizontal speed through the water over the descent speed while gliding or tumbling.
    pub glide_ratio: Range,
    /// Descent (m) over which the glide heading loses its memory. Much less than the depth:
    /// the glide is a random walk; much more: a straight glide in one direction.
    pub glide_memory_m: Range,
    /// Travel along the impact track after first contact (breakup, skipping, sliding), as the
    /// horizontal impact speed times this time (s).
    pub carry_s: Range,
    /// Scatter across the track, as a fraction of the along-track travel.
    pub carry_lateral: f64,
    /// Share of elements that sink at once...
    pub sinks_at_once: f64,
    /// ...and that never sink within hours (surface-drift debris, not settled). The rest float
    /// for `float_s` seconds first.
    pub stays_afloat: f64,
    pub float_s: Range,
    /// Downwind drift while afloat, as a fraction of the 10 m wind (leeway), on top of the
    /// surface current.
    pub leeway: Range,
    /// Number of physical pieces of this class in this family.
    pub pieces: Range,
    /// Share of the impact mass in this class (shares sum to one within a family).
    pub mass_share: f64,
}

impl Element {
    pub fn check(&self) -> Result<(), String> {
        let unit = |x: f64| (0.0..=1.0).contains(&x);
        let positive = [
            ("areal_density_kg_m2", self.areal_density_kg_m2),
            ("drag_coefficient", self.drag_coefficient),
            ("descent_factor", self.descent_factor),
            ("pieces", self.pieces),
        ];
        if let Some((name, _)) = positive.iter().find(|(_, r)| r.lo <= 0.0) {
            return Err(format!("{name} must be positive"));
        }
        if self.material_density_kg_m3.lo <= 1060.0 {
            return Err("material_density_kg_m3 must exceed the densest deep sea water (1,060 kg/m3)".into());
        }
        let non_negative = [self.glide_ratio, self.carry_s, self.float_s, self.leeway];
        if non_negative.iter().any(|r| r.lo < 0.0) || self.glide_memory_m.lo <= 0.0 || !(self.carry_lateral >= 0.0) {
            return Err("glide, carry, float and leeway ranges must be non-negative, glide memory positive".into());
        }
        if !unit(self.sinks_at_once) || !unit(self.stays_afloat) || self.sinks_at_once + self.stays_afloat > 1.0 + 1e-12 {
            return Err("sinks_at_once and stays_afloat are shares that sum to at most one".into());
        }
        if !unit(self.mass_share) {
            return Err("mass_share must lie in [0, 1]".into());
        }
        Ok(())
    }
}

/// Which terms of the resting offset are on. All of them for the estimate; the report turns
/// them off one at a time to show what each contributes. `ocean_error` switches the per-event
/// realisation of unresolved motion.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Terms {
    pub carry: bool,
    pub float: bool,
    pub current: bool,
    pub glide: bool,
    pub ocean_error: bool,
}

/// One realisation of the ocean's unresolved motion for a whole impact event (rule 10): every
/// element of one wreckage draw sees the same values.
#[derive(Debug, Clone, Copy, PartialEq, Default)]
pub struct OceanRealisation {
    pub surface: [f64; 2],
    pub upper: [f64; 2],
    pub deep: [f64; 2],
    pub near_bottom: [f64; 2],
}

impl OceanRealisation {
    pub fn draw(model: &ErrorModel, rng: &mut Rng) -> OceanRealisation {
        let mut pair = |sd: f64| [sd * rng.normal(), sd * rng.normal()];
        OceanRealisation {
            surface: pair(model.surface_mps),
            upper: pair(model.upper_mps),
            deep: pair(model.deep_mps),
            near_bottom: pair(model.near_bottom_mps),
        }
    }
}

/// Where and when a sinking element first touches the seabed, from its release point.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Landing {
    /// Offset of the seabed contact from the release point (m).
    pub offset_m: [f64; 2],
    pub depth_m: f64,
    pub descent_s: f64,
    /// Depth range (m) over which the current was extrapolated below the model bottom.
    pub below_model_bottom_m: f64,
    /// Mean descent speed (m/s): depth over descent time.
    pub mean_sink_mps: f64,
}

/// What a sinking element is made of, as drawn for one representative.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Sinker {
    pub areal_density_kg_m2: f64,
    pub material_density_kg_m3: f64,
    pub drag_coefficient: f64,
    pub descent_factor: f64,
    pub glide_ratio: f64,
    pub glide_memory_m: f64,
}

impl Sinker {
    pub fn draw(e: &Element, rng: &mut Rng) -> Sinker {
        Sinker {
            areal_density_kg_m2: e.areal_density_kg_m2.draw(rng),
            material_density_kg_m3: e.material_density_kg_m3.draw(rng),
            drag_coefficient: e.drag_coefficient.draw(rng),
            descent_factor: e.descent_factor.draw(rng),
            glide_ratio: e.glide_ratio.draw(rng),
            glide_memory_m: e.glide_memory_m.draw(rng),
        }
    }

    /// Descent speed (m/s) in water of density rho.
    pub fn speed(&self, water_density_kg_m3: f64) -> f64 {
        self.descent_factor * terminal_speed(self.areal_density_kg_m2, self.material_density_kg_m3, self.drag_coefficient, water_density_kg_m3)
    }
}

/// Integrate one element down the water column from `start` (m, local east/north of the
/// release point's origin) until it first meets the seabed.
///
/// Each step of `step_m` of depth takes dt = dz / w(z) and moves the element by the current at
/// mid-step (plus the event's error realisation) times dt, and by the glide: speed G w in a
/// heading that diffuses with depth so that E[cos(heading change over dz)] = exp(-dz / l). When
/// a step is longer than the memory l, the heading forgets itself within the step and the glide
/// is added as its diffusive limit, an isotropic Gaussian of variance G^2 l dz per component;
/// otherwise the heading walk is followed in sub-steps of at most l / 10. The seabed is found by testing depth after each step against `seabed(position)`
/// and interpolating linearly within the step. Returns None if the column has no seabed
/// (land, outside the grid) or the element cannot sink (water denser than the element).
#[allow(clippy::too_many_arguments)]
pub fn sink(
    start: [f64; 2],
    sinker: &Sinker,
    profile: &Profile,
    ocean: &OceanRealisation,
    error: &ErrorModel,
    terms: &Terms,
    rule: BelowModelBottom,
    step_m: f64,
    seabed: &dyn Fn([f64; 2]) -> Option<f64>,
    rng: &mut Rng,
) -> Option<Landing> {
    let mut at = start;
    let mut z = 0.0;
    let mut t = 0.0;
    let mut below = 0.0;
    let mut heading = std::f64::consts::TAU * rng.uniform();
    let (g, l) = (if terms.glide { sinker.glide_ratio } else { 0.0 }, sinker.glide_memory_m);
    let mut floor = seabed(at)?;
    for _ in 0..100_000 {
        let dz = step_m;
        let mid = z + dz / 2.0;
        // A refusal (rule `refuse` below the model bottom) leaves the element not computed.
        let sample = profile.at_depth(mid, Some(floor.max(mid)), rule).ok()?;
        let beyond = sample.extrapolated;
        // Descent speed relative to the ground: the element's own w, less any resolved upward
        // water velocity. Absent is not zero: with no resolved w the element's own speed is used
        // and the absence is the product's declared property, not a value.
        let w = sinker.speed(profile.density_at(mid)) - sample.w_up.unwrap_or(0.0);
        if !(w > 0.0) {
            return None;
        }
        let dt = dz / w;
        let mut u = [0.0; 2];
        if terms.current {
            u = [sample.u_east, sample.v_north];
        }
        if terms.ocean_error {
            let band = if mid < error.upper_depth_m { ocean.upper } else { ocean.deep };
            u = [u[0] + band[0], u[1] + band[1]];
            if floor - mid < error.near_bottom_m {
                u = [u[0] + ocean.near_bottom[0], u[1] + ocean.near_bottom[1]];
            }
        }
        let mut step = [u[0] * dt, u[1] * dt];
        // The same random numbers are drawn whether or not a term is on (common random numbers),
        // so the report's term-by-term comparisons differ only by the term.
        if l <= dz {
            // Diffusive limit: G^2 l dz per component per step. Summed over the column this gives
            // 2 G^2 l H against the exact 2 G^2 l^2 (H/l - 1 + exp(-H/l)): relative error l / H,
            // at most 1.25% at l = dz = 50 m over 4 km.
            let sd = g * (l * dz).sqrt();
            let (a, b) = (rng.normal(), rng.normal());
            step = [step[0] + sd * a, step[1] + sd * b];
        } else {
            // Heading walk in sub-steps h of at most l / 10, each straight in the heading at its
            // START. Segment headings then correlate as exp(-k h / l), exactly the continuous
            // law at lag k h, and the mean square differs from the continuous one by O((h/l)^2).
            // (A mid-step heading inflates every lag by exp(h / 2l): +4.6% at h/l = 0.09, which
            // the closed-form test caught.)
            let n = (10.0 * dz / l).ceil().max(1.0) as usize;
            let h = dz / n as f64;
            for _ in 0..n {
                step = [step[0] + g * h * heading.sin(), step[1] + g * h * heading.cos()];
                heading += (2.0 * h / l).sqrt() * rng.normal();
            }
        }
        let next = [at[0] + step[0], at[1] + step[1]];
        let next_floor = seabed(next)?;
        if z + dz >= next_floor {
            // Contact within this step: z + f dz = floor + f (next_floor - floor).
            let denom = dz - (next_floor - floor);
            let f = if denom > 0.0 { ((floor - z) / denom).clamp(0.0, 1.0) } else { 0.0 };
            let landing = [at[0] + f * step[0], at[1] + f * step[1]];
            let depth = z + f * dz;
            if beyond {
                below += f * dz;
            }
            let descent_s = t + f * dt;
            return Some(Landing {
                offset_m: [landing[0] - start[0], landing[1] - start[1]],
                depth_m: depth,
                descent_s,
                below_model_bottom_m: below,
                mean_sink_mps: if descent_s > 0.0 { depth / descent_s } else { f64::NAN },
            });
        }
        if beyond {
            below += dz;
        }
        at = next;
        floor = next_floor;
        z += dz;
        t += dt;
    }
    None
}

/// A small deterministic generator (SplitMix64) for the draws: seeded from an impact sample's
/// own fields and the draw index, so a wreckage draw is a function of the sample and of its
/// index alone — refining from 512 to 4,096 draws keeps the first 512 unchanged.
pub struct Rng(u64);

impl Rng {
    pub fn seeded(words: &[u64]) -> Rng {
        Rng(words.iter().fold(0x243F_6A88_85A3_08D3, |s, w| mix(s ^ w)))
    }

    /// A uniform draw on (0, 1).
    pub fn uniform(&mut self) -> f64 {
        self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
        ((mix(self.0) >> 11) as f64 + 0.5) / (1u64 << 53) as f64
    }

    pub fn normal(&mut self) -> f64 {
        (-2.0 * self.uniform().ln()).sqrt() * (std::f64::consts::TAU * self.uniform()).cos()
    }
}

fn mix(mut z: u64) -> u64 {
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    z ^ (z >> 31)
}
