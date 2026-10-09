//! Settling: where the wreckage of one ocean impact comes to rest on the seabed.
//!
//! A TRANSFORM, NOT EVIDENCE (brief section 2, rule 1). It returns no log-likelihood of its own
//! (`impact_log_likelihood` is the trait default, 0.0 = "adds nothing") and declares no
//! observations: the one thing that could be scored, the search having found nothing, belongs
//! to searched areas.
//!
//! PRIMARY OUTPUT: WRECKAGE SAMPLES (ARCHITECTURE decision 2, option 3). For each impact sample,
//! [`Settling::emit`] returns `draws` wreckage draws. A draw is ONE settled configuration W of the
//! whole field — one breakup family, one ocean-error realisation, and every class's pieces — and
//! carries weight 1 / draws of its parent, so creating descendants never creates probability.
//! Draws are alternative outcomes, not extra wreckage: a consumer AVERAGES over draws and never
//! multiplies (searched-areas brief, section 2). Within a draw each class is represented by up
//! to K representative elements (breakup.toml, `representatives_per_class`), each standing for
//! `multiplicity` physical pieces of a stated projected area. Draw d of an impact is a function
//! of the impact and d alone, so adaptive refinement from 512 to 4,096 draws keeps the first 512.
//! The runner stage that calls `emit` and stores its rows is core request 12, not built here.
//!
//! SECONDARY OUTPUT: `predict` / `prediction_columns`, a cheap moment diagnostic computed from the
//! same emitter with `moment_draws` draws (one implementation; deterministic per sample).
//!
//! MODEL (after the methodology Pete shared, input not truth):
//!   r_rest = r_contact + carry + drift afloat + integral of (U(z) + error) dt + glide
//!                                                               (+ seabed movement, not modelled)
//! - carry: travel along the impact track after contact (breakup, skipping), V_h x carry_s, with
//!   lateral scatter.
//! - drift afloat: (surface current + per-event surface error + leeway x 10 m wind) x float time,
//!   for the share of a class that floats before it sinks. The share that stays afloat for hours
//!   is surface-drift debris: emitted with fate `afloat` and no seabed position, as the
//!   sink-versus-float hook (queued with Pete; drift consumes the partition later).
//! - sinking: integrated layer by layer, dt = dz / w(z), w the terminal speed of a flooded body
//!   falling broadside, w = k sqrt(2 g s (1 - rho_w/rho_m) / (rho_w Cd)), with s mass per projected
//!   area and k >= 1 a descent factor for fluttering bodies (physics.rs). In-situ density enters
//!   per layer (about +3% by 6 km, so about -1.5% in w).
//! - glide: horizontal motion through the water at G w, heading diffusing with depth with memory
//!   l, giving E|offset|^2 = 2 G^2 l^2 (x - 1 + exp(-x)), x = depth / l (straight glide for l >>
//!   depth, random walk for l << depth). Bounded lateral motion with stated uncertainty, as the
//!   brief asks; not a hydrodynamic model of plate flutter (Andersen, Pesavento and Wang 2005,
//!   J. Fluid Mech. 541; Field et al. 1997, Nature 388) — those set the plausible G and l ranges.
//! - stop at first seabed contact (rule 9): sliding, rolling, burial and remobilisation are a
//!   separate step, not modelled. Contact is found against the seabed at the element's CURRENT
//!   position, so a slope is honoured.
//!
//! ASSUMPTIONS, each declared (brief section 8: educated estimates are acceptable when declared):
//! 1. Breakup families are selected by vertical and total SPECIFIC kinetic energy only
//!    (breakup.rs). The flight-path angle is implied by the two. Attitude and the energy-transfer
//!    duration are recorded upstream but unused here: the first pass spends its complexity on
//!    sinking rate, because at 4 km against 0.1 m/s a sink rate of 2, 0.5, 0.05 or 0.01 m/s moves
//!    an element 0.2, 0.8, 8 or 40 km (brief section 6) — no current precision compensates for an
//!    unsupported sink-rate assumption.
//! 2. Every number in breakup.toml (areal densities, material densities, drag coefficients, glide
//!    ranges, float times, piece counts, mass shares) is an educated estimate. Analogue anchors
//!    for the family selection are in breakup.toml's comments; the analogue and model survey is
//!    data/analogues.csv with primary sources.
//! 3. One family per draw: a field breaks up coherently. When the impact sample carries end of
//!    flight's `debris_class` (drawn once per impact sample, ruled 9 Oct), every draw of that impact
//!    uses it, so every consumer conditions on one draw. Until core request 4 makes it readable from
//!    `ImpactView`, the caller passes it in (`emit_with`, from the impacts file's `debris_class`
//!    column); without it settling draws the family per wreckage draw from the same rule
//!    (breakup.rs), labelled provisional. Families are never averaged within a draw.
//! 4. One ocean-error realisation per draw, shared by every element of that draw and by both
//!    phases (rule 10): the shared integrator realises `OceanErrorModel` from the draw's seed for
//!    the float phase, and the descent evaluates `OceanErrorModel::realise(seed)` with that same
//!    seed. Independent per-fragment noise would shrink the field artificially.
//! 5. Element properties are independent across representatives: pieces of one class are not
//!    identical. Pieces represented by one representative sit at its point; the within-class
//!    spread is carried by the K representatives (a computational choice).
//! 6. Piece area follows from mass conservation: area = mass_share x impact mass / (pieces x s).
//! 7. THE OCEAN COMES FROM `mh370-ocean` (merged 77109b7 / 8d1160f), not from settling:
//!    - currents by depth: the shared `ProfileSource` and `Profile::at_depth`, queried once per
//!      element at the point and time it leaves the surface, and held for its descent (column
//!      assumption: a 4 km descent at 0.15-5 m/s moves an element 0.1-10 km, small against the
//!      ~8-11 km grid of the candidate products);
//!    - the float phase: the shared batch integrator `integrate`, one call per wreckage draw, every
//!      floating element a particle with `ObjectResponse { a_stokes, c_wind = its leeway }` and
//!      `Particle.end_time` = its own sink time, read from `Track.end` (ocean transport item 4,
//!      fe05b0b), so one call carries elements with different sink times through one ocean;
//!    - ocean error: `OceanErrorModel`, realised once per draw from the draw's seed;
//!    - sub-grid diffusion while afloat: the shared `DiffusivityPrior::provisional` (one K per draw,
//!      an eta component) unless the run fixes it.
//!    - the seabed: the shared `Bathymetry` surface (item 3, 75ac7df; GEBCO_2026 at 15 arc-seconds
//!      today, AusSeabed first in priority when obtained), nearest native cell, land refused;
//!    - in-situ density: TEOS-10 (`teos10::rho_and_sound_speed`, item 4) on the WOA23 decade-month
//!      SA/CT climatology of the impact, one column per impact (1 degree does not vary across a
//!      wreckage field), held at its end levels beyond them; an impact outside the loaded
//!      decade-month is refused, not given another month's water.
//!    Both are selected in run.toml `[shared]`; absent, the provisional stand-ins apply.
//!    What settling still supplies itself is in provisional.rs, each item labelled and each to be
//!    deleted when the shared crate serves it: a two-layer analytic column (no gridded product
//!    `ProfileSource` exists yet), uniform surface fields, and the planar seabed and linear density
//!    kept for closed-form tests and the report's controlled depths. Every result is provisional
//!    while the column is, and no current product has been chosen (that is the shared owner's).
//! 8. Below the ocean model's bottom one of the shared crate's three explicit rules applies
//!    (default `hold-deepest-level`; `linear-to-zero-at-seabed` and `refuse` are the declared
//!    alternatives), and the extrapolated depth range is reported per element. A zero is never
//!    substituted silently; `refuse` leaves the element not computed.
//! 9. Vertical velocity: used when the product resolves it (descent speed relative to the ground is
//!    w - w_up); when the product has none it is `Absent`, never read as zero. GLORYS12V1's daily
//!    multiyear dataset has none.
//! 10. Near-bottom unresolved motion: the shared `VerticalStructure::Banded` (item 4), whose
//!    near-bottom band is keyed to height above the seabed; the descent passes the local seabed
//!    depth (`velocity_with_seabed`). Each band is its own independent realisation (the shared
//!    owner's conservative choice), still one draw per wreckage configuration.
//!
//! WHAT IS NOT YET HERE, deliberately: the implosion-at-depth event (descent time is computed
//! and emitted per element, which is the hook), post-contact movement, and the shared breakup
//! field freeze (results/breakup-field-candidate.md is the candidate).

mod breakup;
mod physics;
mod provisional;
pub mod stream;

use breakup::{Breakup, OccupantSpec, FAMILIES};
use hypothesis::{Hypothesis, ImpactView};
use ocean::profile::{BelowModelBottom, ProfileSource};
use ocean::stochastic::{Diffusion, DiffusivityPrior, ErrorKind, OceanErrorModel, VerticalStructure};
use ocean::bathy::Bathymetry;
use ocean::soundspeed::{woa23_period, SoundSpeedClimatology};
use ocean::{analytic::Uniform, Component, Domain, Forcing, LonLat, NoCoast, ObjectResponse, Particle, Refloat, RunSpec, Snapshot, VectorField};
use physics::{Range, Rng, Sinker, Terms};
use provisional::{offset_m, DensityStub, LayeredColumn, PlanarSeabed, ProvisionalSpec};
use serde::Deserialize;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct Params {
    /// Draws behind each `predict` call (the moment diagnostic).
    moment_draws: usize,
    /// Integration step in depth (m).
    step_m: f64,
    /// Terms: carry, float, current, glide, ocean-error, diffusion. All of them for the estimate;
    /// the report turns them off one at a time.
    #[serde(default = "all_terms")]
    terms: Vec<String>,
    /// Below the ocean model's own bottom: `hold-deepest-level`, `linear-to-zero-at-seabed` or
    /// `refuse` (the shared crate's three rules).
    below_model_bottom: String,
    /// Float phase: integrator step (s), Stokes response of floating elements, and a fixed sub-grid
    /// diffusivity (m2/s; absent = the shared provisional prior, one K per draw; 0 = none).
    float_step_s: f64,
    #[serde(default)]
    float_a_stokes: f64,
    #[serde(default)]
    float_diffusivity_m2_s: Option<f64>,
    ocean_error: ErrorSpec,
    /// PROVISIONAL inputs the shared crate does not serve yet (provisional.rs).
    provisional: ProvisionalSpec,
    /// Shared-crate products that REPLACE the provisional seabed and density when given.
    #[serde(default)]
    shared: SharedSpec,
    /// Multiplier on every element's `stays_afloat` share (1 = the table; 0.5 and 1.5 are the
    /// declared sensitivities, Pete 9 Oct).
    #[serde(default = "unit_scale")]
    floating_share_scale: f64,
    /// The implosion-at-depth DECLARED ALTERNATIVE (Pete 9 Oct). Absent = progressive flooding,
    /// the baseline.
    #[serde(default)]
    implosion: Option<Implosion>,
    /// The occupants class (ruling 9 Oct ~04:15): config-gated, absent = off.
    #[serde(default)]
    occupants: Option<OccupantSpec>,
}

fn unit_scale() -> f64 {
    1.0
}

/// Implosion at depth, a declared alternative to progressive flooding. A share of each family's
/// cabin-contents representatives is carried INSIDE a fuselage-section representative of the same
/// draw (chosen uniformly): it shares that section's fate, float and descent down to the
/// collapse depth z_c, drawn per contents element from `collapse_depth_m`, and is released there.
/// Released contents that would stay afloat rise (fate afloat, at the release point); the rest
/// sink from z_c with their own properties. If the section reaches the seabed above z_c, the
/// contents rest with it. The section itself continues unchanged. No airliner calibration case
/// exists: the share and the depth range are assumptions, reported as such.
#[derive(Debug, Clone, Copy, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Implosion {
    /// Share of cabin contents inside a section, per family [intact, broken, fragmented].
    pub inside_share: [f64; 3],
    /// Collapse depth (m), e.g. `{ log_uniform = [10.0, 1000.0] }`. Drawn once per SECTION, so all
    /// contents of one section are released together.
    pub collapse_depth_m: Range,
    /// Trapped-air volume per section representative at the surface (m3), for the implosion
    /// events hydroacoustics asked for. Absent: events carry NaN volumes. A declared assumption.
    #[serde(default)]
    pub sealed_volume_m3: Option<Range>,
}

/// One section collapse (implosion alternative), for hydroacoustics' implosion branch (its entry
/// of 9 Oct ~04:15: "per large sealed piece, a volume and a depth-time sink path"). The sink path
/// is the section's descent at constant terminal speed in its own water column; the event is where
/// and when it reaches its collapse depth.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct ImplosionEvent {
    pub draw: u32,
    pub family: u8,
    /// Physical sections this representative stands for.
    pub multiplicity: f64,
    pub east_m: f64,
    pub north_m: f64,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub depth_m: f64,
    /// From the impact: float time plus descent to the collapse depth (s).
    pub time_since_impact_s: f64,
    /// Sea pressure at the collapse depth (dbar, TEOS-10 p_from_z).
    pub pressure_dbar: f64,
    /// Trapped air at the surface, and isothermally compressed to the collapse pressure (m3).
    pub surface_volume_m3: f64,
    pub volume_at_depth_m3: f64,
    /// Mean descent speed of the section from the surface to the collapse depth (m/s).
    pub mean_sink_mps: f64,
}

/// Per-section random stream of the implosion alternative (collapse depth, volume): separate from
/// the draw's main stream so switching the alternative changes nothing else.
const IMPLOSION_STREAM: u64 = 0x494d_504c_4f53_494f;

const HOST_CLASS: &str = "fuselage-section";
const CONTENTS_CLASS: &str = "cabin-contents";

/// Shared ocean products (mh370-ocean, ocean transport items 3 and 4). Each one given replaces its
/// provisional stand-in; each one absent leaves the stand-in, which is reported in the label.
#[derive(Debug, Clone, Default, Deserialize)]
#[serde(deny_unknown_fields)]
struct SharedSpec {
    /// Bathymetry layer manifests, finest first (`Bathymetry::load`), and the window loaded
    /// `[lon_min, lon_max, lat_min, lat_max]`.
    #[serde(default)]
    bathymetry_manifests: Vec<String>,
    #[serde(default)]
    bathymetry_window: Option<[f64; 4]>,
    /// One WOA23 decade-month (the prepared SA/CT grids behind `SoundSpeedClimatology`): in-situ
    /// density by TEOS-10 at each level. Impacts outside its decade-month are refused.
    #[serde(default)]
    density_woa23_manifest: Option<String>,
    /// GLORYS12V1 full-depth column (`GridProfile`, ocean transport's settling deliverable).
    #[serde(default)]
    column_manifest: Option<String>,
    /// Gridded surface current and 10 m wind for the float phase (part or series manifests), read
    /// through ocean transport's `GridField::load_window` for `fields_window` x `fields_time_unix_s`
    /// only (about 16 MB for both, against 1.9 GB whole).
    #[serde(default)]
    surface_current_manifest: Option<String>,
    #[serde(default)]
    wind_manifest: Option<String>,
    #[serde(default)]
    fields_window: Option<[f64; 4]>,
    #[serde(default)]
    fields_time_unix_s: Option<[f64; 2]>,
    /// "column": TEOS-10 on the column's own T and S (consistent with its currents; the default
    /// when the column is a product); "woa23": the climatology above; absent: whichever is given.
    #[serde(default)]
    density_source: Option<String>,
}

/// `OceanErrorModel` in run.toml form.
#[derive(Debug, Clone, Copy, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ErrorSpec {
    /// "none", "uniform-offset" or "eddying".
    kind: ErrorKindName,
    #[serde(default)]
    sigma_m_s: f64,
    #[serde(default)]
    length_scale_m: f64,
    #[serde(default)]
    time_scale_s: f64,
    #[serde(default)]
    modes: usize,
    /// Exponential decay of the amplitude with depth; absent = uniform.
    #[serde(default)]
    efold_m: Option<f64>,
    #[serde(default)]
    deep_ratio: f64,
    /// The shared crate's banded structure (surface, upper, deep and a near-bottom band keyed to
    /// height above the seabed, each its own realisation). Exclusive with `efold_m`.
    #[serde(default)]
    bands: Option<BandSpec>,
}

#[derive(Debug, Clone, Copy, PartialEq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct BandSpec {
    surface_to_m: f64,
    upper_to_m: f64,
    near_bottom_m: f64,
    /// Amplitude factors [surface, upper, deep, near-bottom].
    factors: [f64; 4],
}

#[derive(Debug, Clone, Copy, PartialEq, Deserialize)]
#[serde(rename_all = "kebab-case")]
enum ErrorKindName {
    None,
    UniformOffset,
    Eddying,
}

impl ErrorSpec {
    pub fn model(&self) -> Result<OceanErrorModel, String> {
        let kind = match self.kind {
            ErrorKindName::None => ErrorKind::None,
            ErrorKindName::UniformOffset => ErrorKind::UniformOffset { sigma_m_s: self.sigma_m_s },
            ErrorKindName::Eddying => ErrorKind::Eddying {
                sigma_m_s: self.sigma_m_s,
                length_scale_m: self.length_scale_m,
                time_scale_s: self.time_scale_s,
                modes: self.modes,
            },
        };
        if !(self.sigma_m_s >= 0.0) || (self.kind == ErrorKindName::Eddying && !(self.length_scale_m > 0.0 && self.time_scale_s > 0.0 && self.modes > 0)) {
            return Err("settling: ocean_error needs sigma >= 0, and for eddying positive length, time and modes".into());
        }
        let vertical = match (self.efold_m, self.bands) {
            (Some(_), Some(_)) => return Err("settling: ocean_error takes efold_m or bands, not both".into()),
            (None, Some(b)) => {
                if !(b.surface_to_m > 0.0 && b.upper_to_m > b.surface_to_m && b.near_bottom_m >= 0.0 && b.factors.iter().all(|f| *f >= 0.0)) {
                    return Err("settling: ocean_error bands need 0 < surface_to_m < upper_to_m, near_bottom_m >= 0, factors >= 0".into());
                }
                VerticalStructure::Banded { surface_to_m: b.surface_to_m, upper_to_m: b.upper_to_m, near_bottom_m: b.near_bottom_m, factors: b.factors }
            }
            (None, None) => VerticalStructure::Uniform,
            (Some(efold_m), None) if efold_m > 0.0 && (0.0..=1.0).contains(&self.deep_ratio) => VerticalStructure::Exponential { efold_m, deep_ratio: self.deep_ratio },
            (Some(_), None) => return Err("settling: ocean_error efold_m must be positive and deep_ratio in [0, 1]".into()),
        };
        Ok(OceanErrorModel { kind, vertical })
    }
}

fn all_terms() -> Vec<String> {
    ["carry", "float", "current", "glide", "ocean-error", "diffusion"].map(String::from).to_vec()
}

/// Where an emitted element ended up.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Fate {
    /// At rest on the seabed (first contact).
    Settled = 0,
    /// Stays afloat for hours: surface-drift debris, no seabed position (sink-versus-float hook).
    Afloat = 1,
    /// Could not be computed (no seabed in the column, outside the ocean's support, or an element
    /// not denser than the water). NaN position. Never read as "impossible".
    NotComputed = 2,
}

/// One representative element of one wreckage draw.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct WreckageElement {
    pub draw: u32,
    /// Share of the parent impact sample's weight carried by this element's DRAW (1 / draws).
    /// Every element of a draw has the same value: the draw is the unit of probability.
    pub draw_weight: f64,
    pub family: u8,
    pub class: u8,
    pub fate: Fate,
    /// Physical pieces this representative stands for.
    pub multiplicity: f64,
    pub piece_area_m2: f64,
    pub piece_mass_kg: f64,
    /// Offset of the resting point (or surface position, if afloat) from the impact (m).
    pub east_m: f64,
    pub north_m: f64,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    /// Seabed depth at first contact (m); NaN unless settled.
    pub depth_m: f64,
    /// Time afloat before sinking, and time from leaving the surface to the seabed (s).
    pub float_s: f64,
    pub descent_s: f64,
    pub mean_sink_mps: f64,
    pub below_model_bottom_m: f64,
}

/// Column names (with units) of [`WreckageElement::row`], for the runner's store (core request 12).
pub const WRECKAGE_COLUMNS: [&str; 17] = [
    "draw",
    "draw weight",
    "family",
    "class",
    "fate",
    "multiplicity (pieces)",
    "piece area (m2)",
    "piece mass (kg)",
    "east (m)",
    "north (m)",
    "latitude (deg)",
    "longitude (deg)",
    "depth (m)",
    "float time (s)",
    "descent time (s)",
    "mean sink speed (m per s)",
    "below model bottom (m)",
];

impl WreckageElement {
    pub fn row(&self) -> [f64; 17] {
        [
            self.draw as f64,
            self.draw_weight,
            self.family as f64,
            self.class as f64,
            self.fate as u8 as f64,
            self.multiplicity,
            self.piece_area_m2,
            self.piece_mass_kg,
            self.east_m,
            self.north_m,
            self.latitude_deg,
            self.longitude_deg,
            self.depth_m,
            self.float_s,
            self.descent_s,
            self.mean_sink_mps,
            self.below_model_bottom_m,
        ]
    }
}

/// The ocean settling sees: shared-crate types throughout, with the provisional pieces of
/// provisional.rs behind them.
pub struct Ocean {
    pub column: Box<dyn ProfileSource>,
    pub surface_current: Box<dyn VectorField>,
    pub wind: Box<dyn VectorField>,
    pub stokes: Box<dyn VectorField>,
    pub seabed: Seabed,
    pub density: Density,
    pub error: OceanErrorModel,
    pub label: String,
    pub column_label: &'static str,
    pub surface_label: &'static str,
    pub wind_label: &'static str,
}

/// The seabed settling stops at: the provisional plane (tests, the report's controlled depths) or
/// the shared bathymetry surface (GEBCO_2026 today; AusSeabed first in priority when obtained).
pub enum Seabed {
    Planar(PlanarSeabed),
    Shared(Bathymetry),
}

impl Seabed {
    /// Depth (m, positive down) at `p`; None outside the surface or on land (not computed).
    pub fn depth_at(&self, p: LonLat) -> Option<f64> {
        match self {
            Seabed::Planar(s) => s.depth_at(p),
            Seabed::Shared(b) => b.at(p).map(|s| s.depth_m).filter(|d| *d > 0.0),
        }
    }
    pub fn label(&self) -> &'static str {
        match self {
            Seabed::Planar(_) => "PROVISIONAL planar seabed",
            Seabed::Shared(_) => "shared bathymetry (mh370-ocean)",
        }
    }
}

/// In-situ water density: the provisional linear stub, or TEOS-10 on a WOA23 climatology.
pub enum Density {
    Stub(DensityStub),
    Woa23(SoundSpeedClimatology),
    /// TEOS-10 on the water column's own temperature and salinity at the impact.
    Column,
}

/// Density with depth for one impact (the 1-degree climatology does not vary over a wreckage
/// field, so one column per impact).
pub enum RhoColumn {
    Stub(DensityStub),
    /// Levels with finite SA and CT; held at the end levels beyond them (declared).
    Levels { depth_m: Vec<f64>, rho_kg_m3: Vec<f64> },
}

impl RhoColumn {
    pub fn at(&self, z_m: f64) -> f64 {
        match self {
            RhoColumn::Stub(d) => d.at(z_m),
            RhoColumn::Levels { depth_m, rho_kg_m3 } => {
                let k = depth_m.partition_point(|&d| d <= z_m);
                if k == 0 {
                    rho_kg_m3[0]
                } else if k == depth_m.len() {
                    rho_kg_m3[k - 1]
                } else {
                    let f = (z_m - depth_m[k - 1]) / (depth_m[k] - depth_m[k - 1]);
                    rho_kg_m3[k - 1] + f * (rho_kg_m3[k] - rho_kg_m3[k - 1])
                }
            }
        }
    }
}

impl Density {
    pub fn column(&self, impact: &ImpactView, water: &dyn ProfileSource) -> Result<RhoColumn, String> {
        match self {
            Density::Stub(d) => Ok(RhoColumn::Stub(*d)),
            Density::Column => {
                let p = [impact.longitude_deg, impact.latitude_deg];
                let prof = water.profile(impact.unix_s, p).map_err(|e| format!("settling: no column for density at the impact: {e:?}"))?;
                let t = prof.teos10().map_err(|e| format!("settling: TEOS-10 on the column: {e:?}"))?;
                let (mut depth_m, mut rho_kg_m3) = (Vec::new(), Vec::new());
                for (z, r) in t.depth_m.iter().zip(&t.in_situ_density_kg_m3) {
                    if r.is_finite() {
                        depth_m.push(*z);
                        rho_kg_m3.push(*r);
                    }
                }
                if depth_m.is_empty() {
                    return Err("settling: no density levels in the column".into());
                }
                Ok(RhoColumn::Levels { depth_m, rho_kg_m3 })
            }
            Density::Woa23(clim) => {
                let (decade, month) = woa23_period(impact.unix_s);
                if clim.period() != (decade, month) {
                    return Err(format!("settling: density climatology is {:?}, impact needs {decade} month {month}", clim.period()));
                }
                let p = [impact.longitude_deg, impact.latitude_deg];
                let prof = clim.profile(p).ok_or("settling: impact outside the density climatology grid")?;
                let (mut depth_m, mut rho_kg_m3) = (Vec::new(), Vec::new());
                for k in 0..prof.depth_m.len() {
                    let (sa, ct) = (prof.absolute_salinity_g_kg[k], prof.conservative_temperature_c[k]);
                    if !(sa.is_finite() && ct.is_finite()) {
                        continue;
                    }
                    if let Ok((rho, _c)) = ocean::teos10::rho_and_sound_speed(sa, ct, prof.pressure_dbar[k]) {
                        depth_m.push(prof.depth_m[k]);
                        rho_kg_m3.push(rho);
                    }
                }
                if depth_m.is_empty() {
                    return Err("settling: no density levels in the climatology column".into());
                }
                Ok(RhoColumn::Levels { depth_m, rho_kg_m3 })
            }
        }
    }
    pub fn label(&self) -> &'static str {
        match self {
            Density::Stub(_) => "PROVISIONAL linear density",
            Density::Woa23(_) => "TEOS-10 on WOA23 (mh370-ocean)",
            Density::Column => "TEOS-10 on the column's T and S (mh370-ocean)",
        }
    }
}

impl Ocean {
    pub fn provisional(spec: &ProvisionalSpec, error: OceanErrorModel) -> Result<Ocean, String> {
        spec.check()?;
        Ok(Ocean {
            column: Box::new(LayeredColumn::new(spec.upper_current_mps, spec.deep_current_mps, spec.layer_depth_m, spec.level_spacing_m, spec.model_bottom_m)),
            surface_current: Box::new(Uniform::current(spec.surface_current_mps[0], spec.surface_current_mps[1])),
            wind: Box::new(Uniform::new(Component::Wind10m, spec.wind_mps[0], spec.wind_mps[1])),
            stokes: Box::new(Uniform::new(Component::StokesDrift, spec.stokes_mps[0], spec.stokes_mps[1])),
            seabed: Seabed::Planar(spec.seabed),
            density: Density::Stub(spec.density),
            error,
            label: spec.label.clone(),
            column_label: "PROVISIONAL analytic column",
            surface_label: "PROVISIONAL uniform surface current",
            wind_label: "PROVISIONAL uniform wind",
        })
    }
}

/// Float-phase settings.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct FloatPhase {
    pub step_s: f64,
    pub a_stokes: f64,
    pub diffusivity_m2_s: Option<f64>,
}

pub struct Settling {
    breakup: Breakup,
    ocean: Ocean,
    terms: Terms,
    rule: BelowModelBottom,
    float: FloatPhase,
    step_m: f64,
    moment_draws: usize,
    implosion: Option<Implosion>,
}

pub fn new(params: &toml::Value) -> Result<Box<dyn Hypothesis>, String> {
    Ok(Box::new(Settling::from_params(params)?))
}

/// Per class, in this order, for the moment diagnostic (piece-weighted over draws).
const CLASS_COLUMNS: [&str; 7] = [
    "settled share",
    "mean east (m)",
    "mean north (m)",
    "sd east (m)",
    "sd north (m)",
    "p90 offset (m)",
    "median descent (s)",
];

impl Settling {
    pub fn from_params(params: &toml::Value) -> Result<Settling, String> {
        let p: Params = params.clone().try_into().map_err(|e| format!("settling: {e}"))?;
        let mut ocean = Ocean::provisional(&p.provisional, p.ocean_error.model()?)?;
        if !p.shared.bathymetry_manifests.is_empty() {
            let paths: Vec<&std::path::Path> = p.shared.bathymetry_manifests.iter().map(std::path::Path::new).collect();
            ocean.seabed = Seabed::Shared(Bathymetry::load(&paths, p.shared.bathymetry_window)?);
        }
        if let Some(m) = &p.shared.density_woa23_manifest {
            ocean.density = Density::Woa23(SoundSpeedClimatology::load(std::path::Path::new(m))?);
        }
        let sh = &p.shared;
        if let Some(m) = &sh.column_manifest {
            ocean.column = Box::new(ocean::GridProfile::load(std::path::Path::new(m))?);
            ocean.column_label = "GLORYS12V1 column (mh370-ocean GridProfile)";
        }
        let window = match (sh.fields_window, sh.fields_time_unix_s) {
            (Some(b), Some(t)) => ocean::field::LoadWindow::new(b, t),
            _ if sh.surface_current_manifest.is_some() || sh.wind_manifest.is_some() => {
                return Err("settling: gridded surface fields need fields_window and fields_time_unix_s".into())
            }
            _ => ocean::field::LoadWindow::all(),
        };
        if let Some(m) = &sh.surface_current_manifest {
            let f = ocean::GridField::load_window(std::path::Path::new(m), &window)?;
            ocean.surface_label = if f.meta().product.starts_with("globcurrent") { "Copernicus-GlobCurrent surface current" } else { "GLORYS12V1 surface current" };
            ocean.surface_current = Box::new(f);
        }
        if let Some(m) = &sh.wind_manifest {
            ocean.wind = Box::new(ocean::GridField::load_window(std::path::Path::new(m), &window)?);
            ocean.wind_label = "ERA5 10 m wind";
        }
        match sh.density_source.as_deref() {
            Some("column") => ocean.density = Density::Column,
            Some("woa23") if matches!(ocean.density, Density::Woa23(_)) => {}
            Some("woa23") => return Err("settling: density_source woa23 needs density_woa23_manifest".into()),
            Some(other) => return Err(format!("settling: density_source `{other}`: column or woa23")),
            None => {}
        }
        ocean.label = if ocean.column_label.starts_with("PROVISIONAL") {
            format!("{}; {}; {}", ocean.label, ocean.seabed.label(), ocean.density.label())
        } else {
            format!("{}; {}; {}; {}; {}; {}", ocean.column_label, ocean.surface_label, ocean.wind_label, ocean.seabed.label(), ocean.density.label(), "Stokes field provisional (unused at a_stokes 0)")
        };
        let rule = parse_rule(&p.below_model_bottom)?;
        let float = FloatPhase { step_s: p.float_step_s, a_stokes: p.float_a_stokes, diffusivity_m2_s: p.float_diffusivity_m2_s };
        let mut breakup = Breakup::parse(include_str!("breakup.toml"))?;
        if let Some(o) = &p.occupants {
            breakup.add_occupants(o)?;
        }
        breakup.scale_floating_share(p.floating_share_scale)?;
        Settling::with(breakup, ocean, &p.terms, rule, float, p.step_m, p.moment_draws)?.with_implosion(p.implosion)
    }

    pub fn with(breakup: Breakup, ocean: Ocean, terms: &[String], rule: BelowModelBottom, float: FloatPhase, step_m: f64, moment_draws: usize) -> Result<Settling, String> {
        if let Some(t) = terms.iter().find(|t| !all_terms().contains(t)) {
            return Err(format!("settling: unknown term `{t}`; known: {:?}", all_terms()));
        }
        if !(step_m > 0.0 && step_m <= 500.0) || moment_draws == 0 || !(float.step_s > 0.0) || !(float.a_stokes >= 0.0) || float.diffusivity_m2_s.is_some_and(|k| !(k >= 0.0)) {
            return Err("settling: step_m in (0, 500], moment_draws and float_step_s positive, a_stokes and diffusivity non-negative".into());
        }
        let has = |name: &str| terms.iter().any(|t| t == name);
        let terms = Terms {
            carry: has("carry"),
            float: has("float"),
            current: has("current"),
            glide: has("glide"),
            ocean_error: has("ocean-error"),
            diffusion: has("diffusion"),
        };
        Ok(Settling { breakup, ocean, terms, rule, float, step_m, moment_draws, implosion: None })
    }

    /// Switch the implosion alternative on (Some) or off (None).
    pub fn with_implosion(mut self, implosion: Option<Implosion>) -> Result<Settling, String> {
        if let Some(i) = implosion {
            if !i.inside_share.iter().all(|x| (0.0..=1.0).contains(x)) || !(i.collapse_depth_m.lo > 0.0) {
                return Err("settling: implosion inside_share in [0, 1] and a positive collapse depth".into());
            }
            if !(self.breakup.classes.iter().any(|c| c == HOST_CLASS) && self.breakup.classes.iter().any(|c| c == CONTENTS_CLASS)) {
                return Err(format!("settling: implosion needs classes `{HOST_CLASS}` and `{CONTENTS_CLASS}`"));
            }
        }
        self.implosion = implosion;
        Ok(self)
    }

    pub fn classes(&self) -> &[String] {
        &self.breakup.classes
    }

    pub fn ocean_label(&self) -> &str {
        &self.ocean.label
    }

    /// P(family | impact), or None outside the selection rule's domain.
    pub fn family_probabilities(&self, impact: &ImpactView) -> Option<[f64; 3]> {
        if !(impact.mass_kg > 0.0) {
            return None;
        }
        self.breakup.selection.from_energy(impact.kinetic_energy_j / impact.mass_kg, impact.vertical_kinetic_energy_j / impact.mass_kg)
    }

    /// The wreckage draws of one impact sample: `draws` settled configurations, each with weight
    /// 1 / draws, the family drawn per wreckage draw (provisional; see `emit_with`). Err if the
    /// impact is outside the module's domain; the caller then records NaN, not an empty field.
    pub fn emit(&self, impact: &ImpactView, draws: usize) -> Result<Vec<WreckageElement>, String> {
        self.emit_with(impact, 0..draws, 1.0 / draws as f64, None)
    }

    /// Draws `indices` of an impact, each with `draw_weight`. `family`: the impact sample's
    /// `debris_class` (end of flight's single draw) when the caller has it, used by every draw; None
    /// draws it per wreckage draw from P(family | impact). Draw d is the same whatever range it is
    /// emitted in, so adaptive refinement emits only the new indices.
    pub fn emit_with(&self, impact: &ImpactView, indices: std::ops::Range<usize>, draw_weight: f64, family: Option<usize>) -> Result<Vec<WreckageElement>, String> {
        let families = self.family_probabilities(impact).ok_or("settling: impact outside the family-selection domain (mass, energy)")?;
        if family.is_some_and(|f| f >= FAMILIES.len()) {
            return Err("settling: debris_class must be 0, 1 or 2".into());
        }
        let rho = self.ocean.density.column(impact, self.ocean.column.as_ref())?;
        let mut out = Vec::new();
        for d in indices {
            let mut rng = Rng::seeded(&seed_words(impact, d));
            let u = rng.uniform();
            let f = family.unwrap_or_else(|| pick(&families, u));
            let seed = rng.next_u64();
            self.draw_field(impact, d, draw_weight, f, seed, &rho, &mut rng, &mut out, None)?;
        }
        Ok(out)
    }

    /// As `emit_with`, also returning the implosion alternative's section collapses (empty when
    /// the alternative is off or the family has no sealed sections, inside_share = 0).
    pub fn emit_with_events(&self, impact: &ImpactView, indices: std::ops::Range<usize>, draw_weight: f64, family: Option<usize>) -> Result<(Vec<WreckageElement>, Vec<ImplosionEvent>), String> {
        let families = self.family_probabilities(impact).ok_or("settling: impact outside the family-selection domain (mass, energy)")?;
        if family.is_some_and(|f| f >= FAMILIES.len()) {
            return Err("settling: debris_class must be 0, 1 or 2".into());
        }
        let rho = self.ocean.density.column(impact, self.ocean.column.as_ref())?;
        let (mut out, mut events) = (Vec::new(), Vec::new());
        for d in indices {
            let mut rng = Rng::seeded(&seed_words(impact, d));
            let u = rng.uniform();
            let f = family.unwrap_or_else(|| pick(&families, u));
            let seed = rng.next_u64();
            self.draw_field(impact, d, draw_weight, f, seed, &rho, &mut rng, &mut out, Some(&mut events))?;
        }
        Ok((out, events))
    }

    #[allow(clippy::too_many_arguments)]
    fn draw_field(&self, impact: &ImpactView, draw: usize, draw_weight: f64, family: usize, seed: u64, rho: &RhoColumn, rng: &mut Rng, out: &mut Vec<WreckageElement>, events: Option<&mut Vec<ImplosionEvent>>) -> Result<(), String> {
        let origin: LonLat = [impact.longitude_deg, impact.latitude_deg];
        let t0 = impact.unix_s;
        let lonlat = |offset: [f64; 2]| ocean::displace(origin, offset[0], offset[1]);
        let seabed = |offset: [f64; 2]| self.ocean.seabed.depth_at(lonlat(offset));
        let velocity = [impact.velocity_east_mps, impact.velocity_north_mps];
        let speed = velocity[0].hypot(velocity[1]);
        let realisation = self.ocean.error.realise(seed);
        let first = out.len();
        // Pass 1: every element's properties, carry and fate, in a fixed order of draws.
        struct Pending {
            sinker: Sinker,
            at: [f64; 2],
            float_s: f64,
            leeway: f64,
            /// Carried inside a section (implosion alternative): (host index, collapse depth,
            /// rises when released).
            inside: Option<(usize, f64, bool)>,
        }
        let mut pending: Vec<Option<Pending>> = Vec::new();
        let host_class = self.breakup.classes.iter().position(|c| c == HOST_CLASS);
        let contents_class = self.breakup.classes.iter().position(|c| c == CONTENTS_CLASS);
        let mut hosts: Vec<usize> = Vec::new();
        for (c, element) in self.breakup.elements[family].iter().enumerate() {
            let pieces = element.pieces.draw(rng).round().max(1.0);
            let k = (pieces as usize).min(self.breakup.representatives_per_class);
            for _ in 0..k {
                let sinker = Sinker::draw(element, rng);
                let piece_mass = element.mass_share * impact.mass_kg / pieces;
                // Drawn whether or not the term is on (common random numbers across the report's
                // term-by-term runs).
                let (carry_t, carry_x) = (element.carry_s.draw(rng), 2.0 * rng.uniform() - 1.0);
                let mut at = [0.0; 2];
                if self.terms.carry && speed > 0.0 {
                    let along = [velocity[0] / speed, velocity[1] / speed];
                    let d = speed * carry_t;
                    let lateral = element.carry_lateral * d * carry_x;
                    at = [d * along[0] - lateral * along[1], d * along[1] + lateral * along[0]];
                }
                let fate_u = rng.uniform();
                let (float_t, leeway) = (element.float_s.draw(rng), element.leeway.draw(rng));
                // Drawn for every contents element whether or not the alternative is on (common
                // random numbers).
                let (inside_u, zc_u, host_u) = if Some(c) == contents_class { (rng.uniform(), rng.uniform(), rng.uniform()) } else { (1.0, 0.0, 0.0) };
                let mut row = WreckageElement {
                    draw: draw as u32,
                    draw_weight,
                    family: family as u8,
                    class: c as u8,
                    fate: Fate::NotComputed,
                    multiplicity: pieces / k as f64,
                    piece_area_m2: piece_mass / sinker.areal_density_kg_m2,
                    piece_mass_kg: piece_mass,
                    east_m: f64::NAN,
                    north_m: f64::NAN,
                    latitude_deg: f64::NAN,
                    longitude_deg: f64::NAN,
                    depth_m: f64::NAN,
                    float_s: 0.0,
                    descent_s: f64::NAN,
                    mean_sink_mps: f64::NAN,
                    below_model_bottom_m: f64::NAN,
                };
                if Some(c) == host_class {
                    hosts.push(pending.len());
                }
                if let (Some(imp), false) = (self.implosion, hosts.is_empty()) {
                    if Some(c) == contents_class && inside_u < imp.inside_share[family] {
                        let h = hosts[((host_u * hosts.len() as f64) as usize).min(hosts.len() - 1)];
                        let _ = zc_u;
                        let z_c = imp.collapse_depth_m.quantile(Rng::seeded(&[seed, h as u64, IMPLOSION_STREAM]).uniform());
                        let host_row = out[first + h];
                        match &pending[h] {
                            // The section stays afloat: so do its contents, with it.
                            None => {
                                (row.fate, row.float_s, row.east_m, row.north_m, row.longitude_deg, row.latitude_deg) =
                                    (host_row.fate, host_row.float_s, host_row.east_m, host_row.north_m, host_row.longitude_deg, host_row.latitude_deg);
                                out.push(row);
                                pending.push(None);
                            }
                            Some(hp) => {
                                row.float_s = hp.float_s;
                                let (at, float_s) = (hp.at, hp.float_s);
                                out.push(row);
                                pending.push(Some(Pending { sinker, at, float_s, leeway, inside: Some((h, z_c, fate_u < element.stays_afloat)) }));
                            }
                        }
                        continue;
                    }
                }
                if fate_u < element.stays_afloat {
                    // Surface-drift debris: its position after carry; drift owns what happens next.
                    let p = lonlat(at);
                    row.fate = Fate::Afloat;
                    row.float_s = f64::INFINITY;
                    (row.east_m, row.north_m, row.longitude_deg, row.latitude_deg) = (at[0], at[1], p[0], p[1]);
                    out.push(row);
                    pending.push(None);
                    continue;
                }
                let floats = fate_u >= element.stays_afloat + element.sinks_at_once && self.terms.float;
                row.float_s = if floats { float_t } else { 0.0 };
                out.push(row);
                pending.push(Some(Pending { sinker, at, float_s: row.float_s, leeway, inside: None }));
            }
        }
        // Pass 2: the float phase, through the shared integrator, one call for the whole draw.
        let floaters: Vec<usize> = (0..pending.len()).filter(|&i| pending[i].as_ref().is_some_and(|p| p.float_s > 0.0 && p.inside.is_none())).collect();
        if !floaters.is_empty() {
            // Each element stops at its own sink time (`Particle.end_time`, ocean transport item 4);
            // one output time at the last of them, every track read at its own `end`.
            let last = floaters.iter().map(|&i| t0 + pending[i].as_ref().unwrap().float_s).fold(f64::MIN, f64::max);
            let particles: Vec<Particle> = floaters
                .iter()
                .map(|&i| {
                    let p = pending[i].as_ref().unwrap();
                    let mut q = Particle::new(lonlat(p.at), t0, ObjectResponse::new(self.float.a_stokes, p.leeway));
                    q.end_time = Some(t0 + p.float_s);
                    q
                })
                .collect();
            let diffusion = match (self.terms.diffusion, self.float.diffusivity_m2_s) {
                (false, _) | (true, Some(0.0)) => Diffusion::None,
                (true, Some(k)) => Diffusion::Diffusivity { k_m2_s: k },
                (true, None) => DiffusivityPrior::provisional(&self.ocean.label).draw(seed),
            };
            let spec = RunSpec {
                forcing: Forcing {
                    current: self.ocean.surface_current.as_ref(),
                    stokes: (self.float.a_stokes != 0.0).then_some(self.ocean.stokes.as_ref()),
                    wind10: Some(self.ocean.wind.as_ref()),
                },
                coast: &NoCoast,
                domain: Domain { lon_min: origin[0] - 10.0, lon_max: origin[0] + 10.0, lat_min: (origin[1] - 10.0).max(-89.0), lat_max: (origin[1] + 10.0).min(89.0) },
                step_s: self.float.step_s,
                output_times: vec![last],
                diffusion,
                ocean_error: if self.terms.ocean_error { self.ocean.error } else { OceanErrorModel::none() },
                refloat: Refloat::Off,
                seed,
                leeway_absorbs_stokes: false,
                accept_partial_stokes_overlap: false,
                explicit_residual: false,
                threads: 1,
            };
            let run = ocean::integrate(&spec, &particles).map_err(|e| format!("settling: float phase refused by the shared integrator: {e:?}"))?;
            for (j, &i) in floaters.iter().enumerate() {
                let p = pending[i].as_mut().unwrap();
                match run.tracks[j].end {
                    Some(Snapshot::Afloat(q)) => p.at = offset_m(origin, q),
                    // Left the integrator's domain or hit a field gap while afloat: not computed.
                    _ => pending[i] = None,
                }
            }
        }
        // Pass 3: the descent of every sinking element, from where and when it left the surface.
        // Each element has its own random stream (seed, index), so switching one element's
        // treatment leaves every other element's draws unchanged.
        let rho = |z: f64| rho.at(z);
        let error = self.terms.ocean_error.then_some(&realisation);
        let erng = |i: usize| Rng::seeded(&[seed, i as u64]);
        for (i, slot) in pending.iter().enumerate() {
            let Some(p) = slot else { continue };
            let row = &mut out[first + i];
            if row.fate == Fate::Afloat || p.inside.is_some() {
                continue;
            }
            let start = lonlat(p.at);
            let t_start = t0 + p.float_s;
            let Ok(profile) = self.ocean.column.profile(t_start, start) else { continue };
            if let Some(landing) = physics::sink(p.at, t_start, &p.sinker, &profile, &rho, error, &self.terms, self.rule, self.step_m, &seabed, &lonlat, &mut erng(i)) {
                let rest = [p.at[0] + landing.offset_m[0], p.at[1] + landing.offset_m[1]];
                let q = lonlat(rest);
                row.fate = Fate::Settled;
                (row.east_m, row.north_m, row.longitude_deg, row.latitude_deg) = (rest[0], rest[1], q[0], q[1]);
                (row.depth_m, row.descent_s, row.mean_sink_mps, row.below_model_bottom_m) =
                    (landing.depth_m, landing.descent_s, landing.mean_sink_mps, landing.below_model_bottom_m);
            }
        }
        // Pass 3b (implosion alternative): contents follow their host's own path (same stream) to
        // the collapse depth, then are released.
        for (i, slot) in pending.iter().enumerate() {
            let Some(Pending { sinker, inside: Some((h, z_c, rises)), .. }) = slot else { continue };
            let Some(host) = &pending[*h] else { continue };
            let start = lonlat(host.at);
            let t_start = t0 + host.float_s;
            let Ok(profile) = self.ocean.column.profile(t_start, start) else { continue };
            let to_collapse = |o: [f64; 2]| seabed(o).map(|d| d.min(*z_c));
            let Some(part) = physics::sink(host.at, t_start, &host.sinker, &profile, &rho, error, &self.terms, self.rule, self.step_m, &to_collapse, &lonlat, &mut erng(*h)) else { continue };
            let release = [host.at[0] + part.offset_m[0], host.at[1] + part.offset_m[1]];
            let q = lonlat(release);
            let row = &mut out[first + i];
            if part.depth_m < z_c - 1e-6 {
                // The section met the seabed above its collapse depth: the contents rest with it.
                row.fate = Fate::Settled;
                (row.east_m, row.north_m, row.longitude_deg, row.latitude_deg) = (release[0], release[1], q[0], q[1]);
                (row.depth_m, row.descent_s, row.mean_sink_mps, row.below_model_bottom_m) = (part.depth_m, part.descent_s, part.mean_sink_mps, part.below_model_bottom_m);
                continue;
            }
            if *rises {
                // Buoyant contents rise from the collapse point: surface-drift debris, for drift.
                row.fate = Fate::Afloat;
                row.float_s = f64::INFINITY;
                (row.east_m, row.north_m, row.longitude_deg, row.latitude_deg) = (release[0], release[1], q[0], q[1]);
                continue;
            }
            let t_release = t_start + part.descent_s;
            let Ok(profile) = self.ocean.column.profile(t_release, q) else { continue };
            if let Some(landing) = physics::sink_from(release, part.depth_m, t_release, sinker, &profile, &rho, error, &self.terms, self.rule, self.step_m, &seabed, &lonlat, &mut erng(i)) {
                let rest = [release[0] + landing.offset_m[0], release[1] + landing.offset_m[1]];
                let r = lonlat(rest);
                let descent = part.descent_s + landing.descent_s;
                row.fate = Fate::Settled;
                (row.east_m, row.north_m, row.longitude_deg, row.latitude_deg) = (rest[0], rest[1], r[0], r[1]);
                (row.depth_m, row.descent_s, row.mean_sink_mps, row.below_model_bottom_m) =
                    (landing.depth_m, descent, landing.depth_m / descent, part.below_model_bottom_m + landing.below_model_bottom_m);
            }
        }
        // Pass 3c: the sections' own collapses, when asked for (hydroacoustics' implosion branch).
        if let (Some(events), Some(imp)) = (events, self.implosion) {
            if imp.inside_share[family] > 0.0 {
                for &h in &hosts {
                    let Some(host) = &pending[h] else { continue };
                    if out[first + h].fate == Fate::Afloat {
                        continue;
                    }
                    let mut r = Rng::seeded(&[seed, h as u64, IMPLOSION_STREAM]);
                    let z_c = imp.collapse_depth_m.quantile(r.uniform());
                    let v0 = imp.sealed_volume_m3.map_or(f64::NAN, |v| v.quantile(r.uniform()));
                    let start = lonlat(host.at);
                    let t_start = t0 + host.float_s;
                    let Ok(profile) = self.ocean.column.profile(t_start, start) else { continue };
                    let to_collapse = |o: [f64; 2]| seabed(o).map(|d| d.min(z_c));
                    let Some(part) = physics::sink(host.at, t_start, &host.sinker, &profile, &rho, error, &self.terms, self.rule, self.step_m, &to_collapse, &lonlat, &mut erng(h)) else { continue };
                    if part.depth_m < z_c - 1e-6 {
                        continue; // reached the seabed first: no collapse in the water column
                    }
                    let at = [host.at[0] + part.offset_m[0], host.at[1] + part.offset_m[1]];
                    let q = lonlat(at);
                    let p = ocean::teos10::pressure_dbar(part.depth_m, q[1]);
                    events.push(ImplosionEvent {
                        draw: draw as u32,
                        family: family as u8,
                        multiplicity: out[first + h].multiplicity,
                        east_m: at[0],
                        north_m: at[1],
                        latitude_deg: q[1],
                        longitude_deg: q[0],
                        depth_m: part.depth_m,
                        time_since_impact_s: host.float_s + part.descent_s,
                        pressure_dbar: p,
                        surface_volume_m3: v0,
                        volume_at_depth_m3: v0 * 10.1325 / (10.1325 + p),
                        mean_sink_mps: part.mean_sink_mps,
                    });
                }
            }
        }
        Ok(())
    }
}

/// The shared crate's below-model-bottom rule by its run.toml name.
pub fn parse_rule(name: &str) -> Result<BelowModelBottom, String> {
    match name {
        "refuse" => Ok(BelowModelBottom::Refuse),
        "hold-deepest-level" => Ok(BelowModelBottom::HoldDeepestLevel),
        "linear-to-zero-at-seabed" => Ok(BelowModelBottom::LinearToZeroAtSeabed),
        other => Err(format!("settling: unknown below_model_bottom `{other}`; known: refuse, hold-deepest-level, linear-to-zero-at-seabed")),
    }
}

/// The impact sample's own fields and the draw index, as generator seed words.
fn seed_words(impact: &ImpactView, draw: usize) -> Vec<u64> {
    vec![
        impact.parent as u64,
        impact.unix_s.to_bits(),
        impact.latitude_deg.to_bits(),
        impact.longitude_deg.to_bits(),
        impact.velocity_east_mps.to_bits(),
        impact.velocity_north_mps.to_bits(),
        impact.velocity_up_mps.to_bits(),
        draw as u64,
    ]
}

/// Index of the category u in [0, 1) falls into.
fn pick(p: &[f64], u: f64) -> usize {
    let total: f64 = p.iter().sum();
    let mut sum = 0.0;
    for (i, x) in p.iter().enumerate() {
        sum += x / total;
        if u < sum {
            return i;
        }
    }
    p.len() - 1
}

/// Weighted quantile of (value, weight) pairs.
fn quantile(mut v: Vec<(f64, f64)>, q: f64) -> f64 {
    v.retain(|(x, w)| x.is_finite() && *w > 0.0);
    if v.is_empty() {
        return f64::NAN;
    }
    v.sort_by(|a, b| a.0.total_cmp(&b.0));
    let total: f64 = v.iter().map(|x| x.1).sum();
    let mut sum = 0.0;
    for (x, w) in &v {
        sum += w;
        if sum >= q * total {
            return *x;
        }
    }
    v[v.len() - 1].0
}

impl Hypothesis for Settling {
    fn prediction_columns(&self) -> Vec<String> {
        let mut columns: Vec<String> = FAMILIES.iter().map(|f| format!("{f} probability")).collect();
        columns.push("contact depth (m)".into());
        for class in &self.breakup.classes {
            columns.extend(CLASS_COLUMNS.iter().map(|c| format!("{class} {c}")));
        }
        columns
    }

    /// The moment diagnostic: family probabilities, contact depth, and per class the piece-
    /// weighted settled share, mean and spread of the resting offset, its 90th-percentile
    /// distance and the median descent time, from `moment_draws` wreckage draws. NaN where not
    /// computed.
    fn predict(&self, impact: &ImpactView, out: &mut [f64]) {
        out.fill(f64::NAN);
        let Some(families) = self.family_probabilities(impact) else { return };
        out[..3].copy_from_slice(&families);
        out[3] = self.ocean.seabed.depth_at([impact.longitude_deg, impact.latitude_deg]).unwrap_or(f64::NAN);
        let Ok(rows) = self.emit(impact, self.moment_draws) else { return };
        for (c, slot) in out[4..].chunks_exact_mut(CLASS_COLUMNS.len()).enumerate() {
            let class: Vec<&WreckageElement> = rows.iter().filter(|r| r.class as usize == c).collect();
            let all: f64 = class.iter().map(|r| r.multiplicity * r.draw_weight).sum();
            let settled: Vec<&&WreckageElement> = class.iter().filter(|r| r.fate == Fate::Settled).collect();
            let w: f64 = settled.iter().map(|r| r.multiplicity * r.draw_weight).sum();
            slot[0] = if all > 0.0 { w / all } else { f64::NAN };
            if !(w > 0.0) {
                continue;
            }
            let mean = |f: &dyn Fn(&WreckageElement) -> f64| settled.iter().map(|r| r.multiplicity * r.draw_weight * f(r)).sum::<f64>() / w;
            let (me, mn) = (mean(&|r| r.east_m), mean(&|r| r.north_m));
            slot[1] = me;
            slot[2] = mn;
            slot[3] = mean(&|r| (r.east_m - me).powi(2)).sqrt();
            slot[4] = mean(&|r| (r.north_m - mn).powi(2)).sqrt();
            slot[5] = quantile(settled.iter().map(|r| (r.east_m.hypot(r.north_m), r.multiplicity * r.draw_weight)).collect(), 0.9);
            slot[6] = quantile(settled.iter().map(|r| (r.descent_s, r.multiplicity * r.draw_weight)).collect(), 0.5);
        }
    }
}

#[cfg(test)]
mod tests;
