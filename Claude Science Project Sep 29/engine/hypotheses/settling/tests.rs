//! Brief section 11: a hand-computed terminal velocity; the limiting case (no current, no glide:
//! directly below); closed-form checks (uniform current at constant sink speed, a two-layer
//! current, a sloping seabed, the float phase through the shared integrator); one
//! synthetic-recovery coverage test; plus the weighting, mass, coherence and determinism fixtures
//! the sample contract depends on. Since 9 Oct every ocean quantity comes through `ocean`
//! (mh370-ocean) types; provisional.rs supplies only the column, seabed and density.

use super::*;
use ocean::analytic::UniformColumn;
use physics::{terminal_speed, Range, GRAVITY};
use provisional::{DensityStub, PlanarSeabed};

/// A test ocean: still water at every depth, 4 km flat seabed, uniform density, no error.
#[derive(Clone)]
struct TestOcean {
    spec: ProvisionalSpec,
    error: OceanErrorModel,
}

impl TestOcean {
    fn ocean(&self) -> Ocean {
        Ocean::provisional(&self.spec, self.error).unwrap()
    }
}

fn stub() -> TestOcean {
    TestOcean {
        spec: ProvisionalSpec {
            label: "test".into(),
            surface_current_mps: [0.0; 2],
            wind_mps: [0.0; 2],
            stokes_mps: [0.0; 2],
            upper_current_mps: [0.0; 2],
            deep_current_mps: [0.0; 2],
            layer_depth_m: 1000.0,
            level_spacing_m: 50.0,
            model_bottom_m: 7000.0,
            seabed: PlanarSeabed { reference: [92.0, -35.0], depth_m: 4000.0, slope_deg: 0.0, slope_azimuth_deg: 0.0 },
            density: DensityStub { surface_kg_m3: 1025.0, gradient_kg_m3_per_km: 0.0 },
        },
        error: OceanErrorModel::none(),
    }
}

/// A test ocean with everything moving, for the weighting and determinism fixtures.
fn busy() -> TestOcean {
    let mut o = stub();
    o.spec.surface_current_mps = [0.1, 0.02];
    o.spec.wind_mps = [6.0, -2.0];
    o.spec.upper_current_mps = [0.05, 0.02];
    o.spec.deep_current_mps = [0.02, 0.01];
    o.error = OceanErrorModel::uniform_offset(0.05);
    o
}

/// Float phase with no diffusion: closed-form fixtures stay deterministic.
fn still_float() -> FloatPhase {
    FloatPhase { step_s: 600.0, a_stokes: 0.0, diffusivity_m2_s: Some(0.0) }
}

fn impact(parent: usize, vd: f64, vh: f64) -> ImpactView<'static> {
    let mass = 175_000.0;
    ImpactView {
        parent,
        unix_s: 1_394_238_000.0,
        latitude_deg: -35.0,
        longitude_deg: 92.0,
        velocity_east_mps: 0.0,
        velocity_north_mps: vh,
        velocity_up_mps: -vd,
        flight_path_angle_deg: vd.atan2(vh).to_degrees(),
        mass_kg: mass,
        kinetic_energy_j: 0.5 * mass * (vd * vd + vh * vh),
        vertical_kinetic_energy_j: 0.5 * mass * vd * vd,
        family: 0,
        takeover_unix_s: f64::NAN,
        takeover_latitude_deg: f64::NAN,
        takeover_longitude_deg: f64::NAN,
        takeover_altitude_ft: f64::NAN,
        mode: 0,
        alternative: 0,
        latents: &[],
    }
}

fn fixed(x: f64) -> Range {
    Range { lo: x, hi: x, log: false }
}

/// A table in which every element is one fixed sinker: s = 600 kg/m2, rho_m 5,000, Cd 1, no
/// glide, sinks at once, no carry. Its terminal speed at rho_w 1,025 is 3.021152 m/s (below).
fn one_sinker(glide_ratio: f64, glide_memory_m: f64) -> Breakup {
    let mut b = Breakup::parse(include_str!("breakup.toml")).unwrap();
    for row in b.elements.iter_mut() {
        for e in row.iter_mut() {
            e.areal_density_kg_m2 = fixed(600.0);
            e.material_density_kg_m3 = fixed(5000.0);
            e.drag_coefficient = fixed(1.0);
            e.descent_factor = fixed(1.0);
            e.glide_ratio = fixed(glide_ratio);
            e.glide_memory_m = fixed(glide_memory_m);
            e.carry_s = fixed(0.0);
            e.carry_lateral = 0.0;
            e.sinks_at_once = 1.0;
            e.stays_afloat = 0.0;
            e.pieces = fixed(1.0);
        }
    }
    b
}

/// As `one_sinker`, but every element floats for exactly `float_s` with leeway `leeway` first.
fn one_floater(float_s: f64, leeway: f64) -> Breakup {
    let mut b = one_sinker(0.0, 1.0);
    for row in b.elements.iter_mut() {
        for e in row.iter_mut() {
            e.sinks_at_once = 0.0;
            e.float_s = fixed(float_s);
            e.leeway = fixed(leeway);
        }
    }
    b
}

fn settling_f(b: Breakup, o: TestOcean, terms: &[&str], float: FloatPhase) -> Settling {
    let terms: Vec<String> = terms.iter().map(|s| s.to_string()).collect();
    Settling::with(b, o.ocean(), &terms, BelowModelBottom::HoldDeepestLevel, float, 50.0, 64).unwrap()
}

fn settling(b: Breakup, o: TestOcean, terms: &[&str]) -> Settling {
    settling_f(b, o, terms, still_float())
}

const W: f64 = 3.021152;

#[test]
fn terminal_speed_by_hand_and_the_sphere_formula() {
    // By hand: s = 600 kg/m2, rho_m = 5,000 kg/m3, Cd = 1.0, rho_w = 1,025.
    // Buoyancy factor 1 - 1025/5000 = 0.795; 2 x 9.80665 x 600 x 0.795 = 9,355.544;
    // / 1025 = 9.127360; sqrt = 3.021152 m/s.
    assert!((terminal_speed(600.0, 5000.0, 1.0, 1025.0) - W).abs() < 1e-6);
    // At rho_w = 1,045 (about 4 km in situ): 1 - 1045/5000 = 0.791; 2 g 600 0.791 / 1045 =
    // 8.907629; sqrt = 2.984565 m/s, 1.2% slower.
    assert!((terminal_speed(600.0, 5000.0, 1.0, 1045.0) - 2.984565).abs() < 1e-5);
    // Independent route: a sphere of radius r has s = 4 r rho_m / 3, so the textbook
    // w = sqrt(8 g r (rho_m - rho_w) / (3 rho_w Cd)) must follow. Steel ball, 5 mm, Cd 0.47:
    // 1.3610 m/s.
    let (r, rho, cd) = (0.005, 7850.0, 0.47);
    let textbook = (8.0 * GRAVITY * r * (rho - 1025.0) / (3.0 * 1025.0 * cd)).sqrt();
    assert!((textbook - 1.3610).abs() < 1e-4);
    assert!((terminal_speed(4.0 * r * rho / 3.0, rho, cd, 1025.0) - textbook).abs() < 1e-12);
    // Not denser than the water: not computed, never a speed of zero.
    assert!(terminal_speed(100.0, 1000.0, 1.0, 1025.0).is_nan());
}

#[test]
fn no_current_no_glide_lands_directly_below() {
    let s = settling(one_sinker(0.0, 1.0), stub(), &["carry", "float", "current", "glide", "ocean-error"]);
    let rows = s.emit(&impact(1, 50.0, 80.0), 4).unwrap();
    assert!(!rows.is_empty());
    for r in &rows {
        assert_eq!(r.fate, Fate::Settled);
        assert!(r.east_m.abs() < 1e-9 && r.north_m.abs() < 1e-9, "{r:?}");
        assert!((r.depth_m - 4000.0).abs() < 1e-9);
        assert!((r.descent_s - 4000.0 / W).abs() < 1e-3);
    }
}

#[test]
fn uniform_current_constant_speed_closed_form() {
    // U = (0.1, -0.05) m/s at every depth, w = 3.021152 m/s, H = 4,000 m:
    // T = H / w = 1,323.99 s; offset = U T = (132.399, -66.200) m.
    let mut o = stub();
    o.spec.upper_current_mps = [0.1, -0.05];
    o.spec.deep_current_mps = [0.1, -0.05];
    let s = settling(one_sinker(0.0, 1.0), o, &["current"]);
    for r in s.emit(&impact(2, 50.0, 80.0), 3).unwrap() {
        assert!((r.east_m - 132.399).abs() < 0.01 && (r.north_m + 66.200).abs() < 0.01, "{r:?}");
    }
}

#[test]
fn two_layer_current_closed_form() {
    // 0.2 m/s east above 1,000 m, 0.02 m/s north below, H = 4,000 m, w = 3.021152. The profile
    // is linear between its 50 m levels, so the step 950 -> 1,000 m carries the mean of the two
    // layers: the closed form for that piecewise-linear profile puts the effective interface at
    // 975 m. east = 0.2 x 975 / w = 64.5449 m; north = 0.02 x 3025 / w = 20.0255 m. (This is a
    // property of any level-based product, not of the stub: a sharp interface is smeared over
    // one level spacing.)
    let mut o = stub();
    o.spec.upper_current_mps = [0.2, 0.0];
    o.spec.deep_current_mps = [0.0, 0.02];
    let s = settling(one_sinker(0.0, 1.0), o, &["current"]);
    for r in s.emit(&impact(3, 50.0, 80.0), 2).unwrap() {
        assert!((r.east_m - 64.5449).abs() < 0.001 && (r.north_m - 20.0255).abs() < 0.001, "{r:?}");
    }
}

#[test]
fn sloping_seabed_is_met_where_the_element_is() {
    // Seabed deepens to the south at 10 deg: D(n) = 4000 - n tan(10 deg) for northward offset n.
    // Current 0.3 m/s north, w = 3.021152: n(z) = 0.3 z / w, so contact at
    // z = 4000 / (1 + 0.3 tan(10 deg) / w) = 4000 / 1.0175097 = 3931.17 m, n = 390.36 m.
    let mut o = stub();
    o.spec.seabed.slope_deg = 10.0;
    o.spec.seabed.slope_azimuth_deg = 180.0;
    o.spec.upper_current_mps = [0.0, 0.3];
    o.spec.deep_current_mps = [0.0, 0.3];
    let s = settling(one_sinker(0.0, 1.0), o, &["current"]);
    for r in s.emit(&impact(4, 50.0, 80.0), 2).unwrap() {
        assert!((r.depth_m - 3931.17).abs() < 0.5 && (r.north_m - 390.36).abs() < 0.5, "{r:?}");
    }
}

#[test]
fn below_model_bottom_is_extrapolated_explicitly_and_recorded() {
    // Model bottom 3,000 m over a 4,000 m seabed, deep current 0.1 m/s east (deep layer from
    // 1,000 m, smeared over 950-1,000 m by the level interpolation: effective interface 975 m).
    // Hold: 0.1 x (4000 - 975) / w = 100.1274 m.
    // Linear to zero at the seabed: 0.1 x (3000 - 975) / w + 0.1 x 1000 x 0.5 / w = 83.5774 m
    // (the mid-step rule integrates a linear ramp exactly).
    // Refuse: not computed.
    let mut o = stub();
    o.spec.model_bottom_m = 3000.0;
    o.spec.deep_current_mps = [0.1, 0.0];
    let terms: Vec<String> = vec!["current".into()];
    let run = |rule| Settling::with(one_sinker(0.0, 1.0), o.ocean(), &terms, rule, still_float(), 50.0, 8).unwrap().emit(&impact(5, 50.0, 80.0), 1).unwrap();
    let (hold, ramp, refuse) = (run(BelowModelBottom::HoldDeepestLevel), run(BelowModelBottom::LinearToZeroAtSeabed), run(BelowModelBottom::Refuse));
    assert!((hold[0].east_m - 100.1274).abs() < 0.001, "{:?}", hold[0]);
    assert!((ramp[0].east_m - 83.5774).abs() < 0.001, "{:?}", ramp[0]);
    assert!((hold[0].below_model_bottom_m - 1000.0).abs() < 1e-9);
    assert!(refuse.iter().all(|r| r.fate == Fate::NotComputed && r.east_m.is_nan()));
}

/// Mean square glide offset against 2 G^2 l^2 (x - 1 + exp(-x)), x = H / l, in both regimes of
/// the integrator (memory shorter than a step: Gaussian increments; longer: heading walk).
#[test]
fn glide_matches_its_closed_form_mean_square() {
    for (g, l) in [(0.5, 5.0), (0.4, 80.0), (0.3, 800.0), (0.2, 1.0e6)] {
        let s = settling(one_sinker(g, l), stub(), &["glide"]);
        let mut sum = 0.0;
        let mut n = 0.0;
        for p in 0..200 {
            for r in s.emit(&impact(100 + p, 50.0, 80.0), 10).unwrap() {
                sum += r.east_m * r.east_m + r.north_m * r.north_m;
                n += 1.0;
            }
        }
        let x = 4000.0 / l;
        let expected = 2.0 * g * g * l * l * (x + (-x).exp_m1());
        // 200 impacts x 10 draws x 6 classes (one piece each) = 12,000 rows; the relative
        // standard error of a 2-D Gaussian mean square is sqrt(1 / n) ~ 1%; the diffusive limit
        // adds l / H (0.1% at l = 5) and the sub-stepped walk O(1%).
        assert!((sum / n / expected - 1.0).abs() < 0.05, "g {g} l {l}: {} vs {expected}", sum / n);
    }
}

#[test]
fn draws_split_the_parent_weight_and_conserve_mass() {
    let s = settling(Breakup::parse(include_str!("breakup.toml")).unwrap(), busy(), &["carry", "float", "current", "glide", "ocean-error", "diffusion"]);
    let imp = impact(7, 60.0, 120.0);
    let draws = 32;
    let rows = s.emit(&imp, draws).unwrap();
    // One weight per draw, summing to the parent's one.
    let mut weights = vec![f64::NAN; draws];
    for r in &rows {
        weights[r.draw as usize] = r.draw_weight;
    }
    assert!((weights.iter().sum::<f64>() - 1.0).abs() < 1e-12);
    // Within a draw, pieces x piece mass sums to the impact mass (shares sum to one).
    for d in 0..draws as u32 {
        let m: f64 = rows.iter().filter(|r| r.draw == d).map(|r| r.multiplicity * r.piece_mass_kg).sum();
        assert!((m / imp.mass_kg - 1.0).abs() < 1e-9, "draw {d}: {m}");
    }
}

#[test]
fn refinement_appends_draws_and_is_deterministic() {
    let s = settling(Breakup::parse(include_str!("breakup.toml")).unwrap(), busy(), &["carry", "float", "current", "glide", "ocean-error", "diffusion"]);
    let imp = impact(8, 60.0, 120.0);
    let few = s.emit(&imp, 8).unwrap();
    let many = s.emit(&imp, 32).unwrap();
    let prefix: Vec<_> = many.iter().filter(|r| r.draw < 8).collect();
    assert_eq!(few.len(), prefix.len());
    for (a, b) in few.iter().zip(prefix) {
        // Identical apart from the draw weight, which is 1 / draws.
        assert_eq!((a.east_m.to_bits(), a.north_m.to_bits(), a.class, a.family), (b.east_m.to_bits(), b.north_m.to_bits(), b.class, b.family));
    }
}

#[test]
fn one_ocean_realisation_per_draw() {
    // Ocean error only, identical sinkers, nothing else: every element of a draw is displaced by
    // the same error vector times its descent time, so all offsets in a draw are parallel, while
    // different draws point different ways.
    let mut o = stub();
    o.error = OceanErrorModel::uniform_offset(0.05);
    let s = settling(one_sinker(0.0, 1.0), o, &["ocean-error"]);
    let rows = s.emit(&impact(9, 60.0, 120.0), 6).unwrap();
    let mut headings = Vec::new();
    for d in 0..6u32 {
        let draw: Vec<_> = rows.iter().filter(|r| r.draw == d).collect();
        let first = draw[0];
        for r in &draw {
            assert!((r.east_m - first.east_m).abs() < 1e-9 && (r.north_m - first.north_m).abs() < 1e-9);
        }
        headings.push(first.north_m.atan2(first.east_m));
    }
    assert!(headings.windows(2).any(|w| (w[0] - w[1]).abs() > 0.1));
}

/// Synthetic recovery: generate "observed" fields from a known impact and element set (draws the
/// emitter is never asked for, indices from 100,000), then check that the emitter's 90% central
/// interval of the field centroid covers the observed centroids at the nominal rate. The same
/// model generates both, so this tests the sampling machinery and its weighting, not the physics.
#[test]
fn synthetic_recovery_coverage() {
    let mut o = stub();
    o.spec.upper_current_mps = [0.05, 0.02];
    o.spec.deep_current_mps = [0.02, 0.01];
    o.error = OceanErrorModel { kind: ErrorKind::UniformOffset { sigma_m_s: 0.1 }, vertical: VerticalStructure::Exponential { efold_m: 500.0, deep_ratio: 0.2 } };
    o.spec.surface_current_mps = [0.1, 0.0];
    o.spec.wind_mps = [5.0, 0.0];
    let s = settling_f(Breakup::parse(include_str!("breakup.toml")).unwrap(), o, &["carry", "float", "current", "glide", "ocean-error", "diffusion"], FloatPhase { step_s: 600.0, a_stokes: 0.0, diffusivity_m2_s: None });
    let imp = impact(10, 60.0, 120.0);
    // Engine-class centroid east (m), piece-weighted, per draw.
    let centroid = |rows: &[WreckageElement], d: u32| {
        let r: Vec<_> = rows.iter().filter(|r| r.draw == d && r.class == 0 && r.fate == Fate::Settled).collect();
        let w: f64 = r.iter().map(|r| r.multiplicity).sum();
        r.iter().map(|r| r.multiplicity * r.east_m).sum::<f64>() / w
    };
    let emitted = s.emit(&imp, 512).unwrap();
    let mut predicted: Vec<f64> = (0..512).map(|d| centroid(&emitted, d)).collect();
    predicted.sort_by(f64::total_cmp);
    let (lo, hi) = (predicted[25], predicted[486]);
    // "Observed" fields: draws 100,000.. of the same impact (independent seeds).
    let truth = s.emit_with(&imp, 100_000..100_400, 1.0 / 400.0, None).unwrap();
    let covered = (100_000..100_400u32).filter(|&d| (lo..=hi).contains(&centroid(&truth, d))).count();
    let rate = covered as f64 / 400.0;
    // Nominal 0.90; binomial sd sqrt(0.09 / 400) = 0.015, plus the interval's own sampling error.
    assert!((rate - 0.90).abs() < 0.05, "coverage {rate}");
}


#[test]
fn float_phase_through_the_shared_integrator_closed_form() {
    // Floats 3,600 s in a uniform surface current (0.10, 0.02) m/s with leeway 0.03 of a
    // (5, -2) m/s wind: drift velocity (0.25, -0.04) m/s, so (900, -144) m afloat, then sinks
    // 4,000 m in still water straight down. Offsets are on the shared crate's sphere; RK2 on a
    // uniform field over 3.6 km is exact to well under a metre.
    let mut o = stub();
    o.spec.surface_current_mps = [0.10, 0.02];
    o.spec.wind_mps = [5.0, -2.0];
    let s = settling(one_floater(3600.0, 0.03), o, &["float", "current"]);
    for r in s.emit(&impact(20, 50.0, 80.0), 2).unwrap() {
        assert_eq!(r.fate, Fate::Settled);
        assert!((r.float_s - 3600.0).abs() < 1e-9);
        assert!((r.east_m - 900.0).abs() < 0.5 && (r.north_m + 144.0).abs() < 0.5, "{r:?}");
        assert!((r.descent_s - 4000.0 / W).abs() < 1e-3);
    }
    // Float switched off: the element sinks at the contact point.
    let mut o = stub();
    o.spec.surface_current_mps = [0.10, 0.02];
    let s = settling(one_floater(3600.0, 0.03), o, &["current"]);
    for r in s.emit(&impact(20, 50.0, 80.0), 1).unwrap() {
        assert!(r.east_m.abs() < 1e-9 && r.north_m.abs() < 1e-9 && r.float_s == 0.0);
    }
}

#[test]
fn one_ocean_across_float_and_descent() {
    // Ocean error only (uniform offset, uniform in depth). Elements float for different times
    // then sink; every element of a draw is displaced by the SAME error vector e times its total
    // time in the water, (float + H / w). So within a draw all offsets are parallel and their
    // lengths scale with total time: the float phase (inside the shared integrator) and the
    // descent (OceanErrorModel::realise with the same seed) see one ocean.
    let mut o = stub();
    o.error = OceanErrorModel::uniform_offset(0.05);
    let mut b = one_floater(1.0, 0.0);
    for (c, e) in b.elements[1].iter_mut().enumerate() {
        e.float_s = fixed(600.0 * (c + 1) as f64);
    }
    let s = settling(b, o, &["float", "ocean-error"]);
    let rows = s.emit_with(&impact(21, 50.0, 80.0), 0..4, 0.25, Some(1)).unwrap();
    let mut directions = Vec::new();
    for d in 0..4u32 {
        let draw: Vec<_> = rows.iter().filter(|r| r.draw == d).collect();
        let e = [draw[0].east_m / (draw[0].float_s + draw[0].descent_s), draw[0].north_m / (draw[0].float_s + draw[0].descent_s)];
        for r in &draw {
            let t = r.float_s + r.descent_s;
            assert!((r.east_m - e[0] * t).abs() < 0.5 && (r.north_m - e[1] * t).abs() < 0.5, "draw {d}: {r:?} against e {e:?}");
        }
        directions.push(e[1].atan2(e[0]));
    }
    assert!(directions.windows(2).any(|w| (w[0] - w[1]).abs() > 0.1), "draws must see different oceans");
}

#[test]
fn float_diffusion_matches_its_variance() {
    // Fixed K = 200 m2/s for T = 7,200 s: each component has variance 2 K T = 2.88e6 m2
    // (sd 1,697 m), drawn by the shared integrator's per-particle walk.
    let s = settling_f(one_floater(7200.0, 0.0), stub(), &["float", "diffusion"], FloatPhase { step_s: 600.0, a_stokes: 0.0, diffusivity_m2_s: Some(200.0) });
    let mut sum = 0.0;
    let mut n = 0.0;
    for p in 0..100 {
        for r in s.emit(&impact(300 + p, 50.0, 80.0), 10).unwrap() {
            sum += r.east_m * r.east_m + r.north_m * r.north_m;
            n += 2.0;
        }
    }
    // 6,000 elements, 12,000 components: relative standard error sqrt(2 / 12,000) = 1.3%.
    assert!((sum / n / 2.88e6 - 1.0).abs() < 0.05, "{}", sum / n);
    // The provisional prior path draws one K per draw and runs.
    let s = settling_f(one_floater(7200.0, 0.0), stub(), &["float", "diffusion"], FloatPhase { step_s: 600.0, a_stokes: 0.0, diffusivity_m2_s: None });
    assert!(s.emit(&impact(400, 50.0, 80.0), 2).unwrap().iter().all(|r| r.fate == Fate::Settled));
}

#[test]
fn resolved_vertical_velocity_is_used_and_absence_is_not_zero() {
    // The shared crate's analytic column with an upwelling w_up = +0.5 m/s: ground-relative
    // descent speed 3.021152 - 0.5 = 2.521152 m/s, so 4,000 m takes 1,586.58 s, not 1,324.00 s.
    let mut o = stub().ocean();
    o.column = Box::new(UniformColumn::new(0.0, 0.0, Some(0.5), (0..=140).map(|k| 50.0 * k as f64).collect(), 7000.0));
    let terms: Vec<String> = vec!["current".into()];
    let s = Settling::with(one_sinker(0.0, 1.0), o, &terms, BelowModelBottom::HoldDeepestLevel, still_float(), 50.0, 8).unwrap();
    for r in s.emit(&impact(22, 50.0, 80.0), 1).unwrap() {
        assert!((r.descent_s - 4000.0 / (W - 0.5)).abs() < 0.01, "{r:?}");
    }
    // Absent (the layered column): the element's own speed.
    let s = settling(one_sinker(0.0, 1.0), stub(), &["current"]);
    assert!((s.emit(&impact(22, 50.0, 80.0), 1).unwrap()[0].descent_s - 4000.0 / W).abs() < 1e-3);
}

#[test]
fn a_given_debris_class_fixes_the_family_of_every_draw() {
    let s = settling(Breakup::parse(include_str!("breakup.toml")).unwrap(), busy(), &["carry", "current"]);
    let rows = s.emit_with(&impact(23, 60.0, 120.0), 0..16, 1.0 / 16.0, Some(2)).unwrap();
    assert!(rows.iter().all(|r| r.family == 2));
    assert!(s.emit_with(&impact(23, 60.0, 120.0), 0..1, 1.0, Some(3)).is_err());
}

#[test]
fn run_toml_constructs_and_predict_fills_or_refuses() {
    // Without [shared]: the provisional stand-ins, so the test needs no data files (the shared
    // products are exercised by the ignored `shared_products_load_and_answer`).
    let text = include_str!("run.toml");
    let table: toml::Table = toml::from_str(text).unwrap();
    let mut params = table["hypotheses"]["settling"].clone();
    assert!(params.as_table_mut().unwrap().remove("shared").is_some());
    let h = new(&params).unwrap();
    let columns = h.prediction_columns();
    assert_eq!(columns.len(), 4 + 6 * CLASS_COLUMNS.len());
    assert!(columns.iter().all(|c| !c.contains([',', '/', ':', '\n'])));
    let mut out = vec![0.0; columns.len()];
    h.predict(&impact(11, 60.0, 120.0), &mut out);
    assert!(out[..5].iter().all(|x| x.is_finite()), "{out:?}");
    // The engine settles on the seabed every time.
    assert!((out[4] - 1.0).abs() < 1e-12);
    // No mass: refuse (NaN), never zero.
    let mut bad = impact(12, 60.0, 120.0);
    bad.mass_kg = f64::NAN;
    h.predict(&bad, &mut out);
    assert!(out.iter().all(|x| x.is_nan()));
}

/// Report generator, not a test: `SETTLING_REPORT_DIR=<dir> [SETTLING_REPORT_DEPTHS=3000,4000]
/// cargo test --release -p mh370-hypotheses settling::tests::report -- --ignored`. Writes the
/// sensitivity summary and the baseline element samples behind the report page. Every number
/// depends on the PROVISIONAL inputs (run.toml) and is labelled so in the page.
#[test]
#[ignore]
fn report() {
    use std::io::Write;
    let dir = std::path::PathBuf::from(std::env::var("SETTLING_REPORT_DIR").expect("set SETTLING_REPORT_DIR"));
    let depths: Vec<f64> = std::env::var("SETTLING_REPORT_DEPTHS").unwrap_or("3000,4000,5000".into()).split(',').map(|x| x.trim().parse().unwrap()).collect();
    std::fs::create_dir_all(&dir).unwrap();
    let table: toml::Table = toml::from_str(include_str!("run.toml")).unwrap();
    let p = &table["hypotheses"]["settling"];
    let spec: ProvisionalSpec = p["provisional"].clone().try_into().unwrap();
    let error: ErrorSpec = p["ocean_error"].clone().try_into().unwrap();
    let base = TestOcean { spec, error: error.model().unwrap() };
    let base_float = FloatPhase { step_s: 600.0, a_stokes: 0.0, diffusivity_m2_s: None };
    let draws = 256;
    let imp = impact(1, 60.0, 150.0);
    let all = ["carry", "float", "current", "glide", "ocean-error", "diffusion"];
    let without = |t: &str| all.iter().copied().filter(|x| *x != t).collect::<Vec<_>>();
    let scale = |b: &mut Breakup, f: f64| {
        for row in b.elements.iter_mut() {
            for e in row.iter_mut() {
                e.areal_density_kg_m2 = Range { lo: e.areal_density_kg_m2.lo * f, hi: e.areal_density_kg_m2.hi * f, log: e.areal_density_kg_m2.log };
            }
        }
    };
    let float_scale = |b: &mut Breakup, f: f64| {
        for row in b.elements.iter_mut() {
            for e in row.iter_mut() {
                e.float_s = Range { lo: e.float_s.lo * f, hi: e.float_s.hi * f, log: e.float_s.log };
            }
        }
    };
    type OceanEdit = fn(&mut TestOcean);
    // (label, terms, ocean edit, areal-density scale, float-time scale, float settings)
    let fp = |a: f64, k: Option<f64>| FloatPhase { step_s: 600.0, a_stokes: a, diffusivity_m2_s: k };
    let variants: Vec<(&str, Vec<&str>, OceanEdit, f64, f64, FloatPhase)> = vec![
        ("baseline", all.to_vec(), |_| {}, 1.0, 1.0, base_float),
        ("no float (sink at contact)", without("float"), |_| {}, 1.0, 1.0, base_float),
        ("float time x0.5", all.to_vec(), |_| {}, 1.0, 0.5, base_float),
        ("float time x2", all.to_vec(), |_| {}, 1.0, 2.0, base_float),
        ("sink rate x0.5 (s x0.25)", all.to_vec(), |_| {}, 0.25, 1.0, base_float),
        ("sink rate x2 (s x4)", all.to_vec(), |_| {}, 4.0, 1.0, base_float),
        ("no glide", without("glide"), |_| {}, 1.0, 1.0, base_float),
        ("no carry", without("carry"), |_| {}, 1.0, 1.0, base_float),
        ("no current", without("current"), |_| {}, 1.0, 1.0, base_float),
        ("current x2", all.to_vec(), |o| {
            o.spec.upper_current_mps = o.spec.upper_current_mps.map(|x| 2.0 * x);
            o.spec.deep_current_mps = o.spec.deep_current_mps.map(|x| 2.0 * x);
        }, 1.0, 1.0, base_float),
        ("deep current reversed", all.to_vec(), |o| o.spec.deep_current_mps = o.spec.deep_current_mps.map(|x| -x), 1.0, 1.0, base_float),
        ("surface current p90 (0.31 m/s)", all.to_vec(), |o| o.spec.surface_current_mps = [0.31, 0.0], 1.0, 1.0, base_float),
        ("no wind (leeway off)", all.to_vec(), |o| o.spec.wind_mps = [0.0, 0.0], 1.0, 1.0, base_float),
        ("ocean error fully correlated in depth (exponential)", all.to_vec(), |o| {
            o.error = OceanErrorModel { kind: ErrorKind::UniformOffset { sigma_m_s: 0.10 }, vertical: VerticalStructure::Exponential { efold_m: 500.0, deep_ratio: 0.2 } };
        }, 1.0, 1.0, base_float),
        ("no near-bottom error band", all.to_vec(), |o| {
            if let VerticalStructure::Banded { surface_to_m, upper_to_m, near_bottom_m, factors } = o.error.vertical {
                o.error.vertical = VerticalStructure::Banded { surface_to_m, upper_to_m, near_bottom_m, factors: [factors[0], factors[1], factors[2], factors[2]] };
            }
        }, 1.0, 1.0, base_float),
        ("Stokes on (a = 1)", all.to_vec(), |_| {}, 1.0, 1.0, fp(1.0, None)),
        ("diffusivity 30 m2/s", all.to_vec(), |_| {}, 1.0, 1.0, fp(0.0, Some(30.0))),
        ("diffusivity 1000 m2/s", all.to_vec(), |_| {}, 1.0, 1.0, fp(0.0, Some(1000.0))),
        ("no ocean error", without("ocean-error"), |_| {}, 1.0, 1.0, base_float),
    ];
    let mut summary = std::fs::File::create(dir.join("sensitivity.csv")).unwrap();
    writeln!(summary, "variant,depth_m,family,class,settled_share,median_offset_m,p90_offset_m,median_descent_s,p90_descent_s,field_p90_radius_m,rows_per_draw").unwrap();
    let mut samples = std::fs::File::create(dir.join("baseline_samples.csv")).unwrap();
    writeln!(samples, "depth_m,family,class,draw,fate,multiplicity,piece_area_m2,east_m,north_m,float_s,descent_s,mean_sink_mps").unwrap();
    for &depth in &depths {
        for (label, terms, edit, s_scale, f_scale, float) in &variants {
            let mut o = base.clone();
            o.spec.seabed.depth_m = depth;
            edit(&mut o);
            let mut b = Breakup::parse(include_str!("breakup.toml")).unwrap();
            scale(&mut b, *s_scale);
            float_scale(&mut b, *f_scale);
            let st = settling_f(b, o, terms, *float);
            for f in 0..3 {
                let rows = st.emit_with(&imp, 0..draws, 1.0 / draws as f64, Some(f)).unwrap();
                let per_draw = rows.len() as f64 / draws as f64;
                // Field extent: per draw, the piece-weighted 90% radius of settled pieces about
                // their centroid; reported as the median over draws.
                let mut radii: Vec<(f64, f64)> = Vec::new();
                for d in 0..draws as u32 {
                    let r: Vec<_> = rows.iter().filter(|r| r.draw == d && r.fate == Fate::Settled).collect();
                    let w: f64 = r.iter().map(|r| r.multiplicity).sum();
                    if w > 0.0 {
                        let (ce, cn) = (r.iter().map(|r| r.multiplicity * r.east_m).sum::<f64>() / w, r.iter().map(|r| r.multiplicity * r.north_m).sum::<f64>() / w);
                        radii.push((quantile(r.iter().map(|r| ((r.east_m - ce).hypot(r.north_m - cn), r.multiplicity)).collect(), 0.9), 1.0));
                    }
                }
                let field = quantile(radii, 0.5);
                for (c, class) in st.classes().iter().enumerate() {
                    let cls: Vec<_> = rows.iter().filter(|r| r.class as usize == c).collect();
                    let all_w: f64 = cls.iter().map(|r| r.multiplicity).sum();
                    let set: Vec<_> = cls.iter().filter(|r| r.fate == Fate::Settled).collect();
                    let w: f64 = set.iter().map(|r| r.multiplicity).sum();
                    let dist: Vec<(f64, f64)> = set.iter().map(|r| (r.east_m.hypot(r.north_m), r.multiplicity)).collect();
                    let t: Vec<(f64, f64)> = set.iter().map(|r| (r.descent_s, r.multiplicity)).collect();
                    writeln!(
                        summary,
                        "{label},{depth},{},{class},{:.6},{:.3},{:.3},{:.1},{:.1},{:.3},{:.2}",
                        FAMILIES[f],
                        w / all_w,
                        quantile(dist.clone(), 0.5),
                        quantile(dist, 0.9),
                        quantile(t.clone(), 0.5),
                        quantile(t, 0.9),
                        field,
                        per_draw
                    )
                    .unwrap();
                }
                if *label == "baseline" {
                    for r in &rows {
                        writeln!(samples, "{depth},{},{},{},{},{:.4},{:.4},{:.3},{:.3},{:.1},{:.1},{:.4}", FAMILIES[f], st.classes()[r.class as usize], r.draw, r.fate as u8, r.multiplicity, r.piece_area_m2, r.east_m, r.north_m, r.float_s, r.descent_s, r.mean_sink_mps).unwrap();
                    }
                }
            }
        }
    }
}

// ---------------------------------------------------------------------------------------------
// Streaming to a consumer (core request 12 stub; stream.rs).
// ---------------------------------------------------------------------------------------------

use stream::{stream_impact, BoxSearchPlaceholder, StreamPolicy, WreckageConsumerStub};

fn stream_settling() -> Settling {
    settling(Breakup::parse(include_str!("breakup.toml")).unwrap(), busy(), &["carry", "current", "glide", "ocean-error"])
}

/// Half-plane east of the impact: pieces land on either side depending on the draw's ocean error.
fn half_box() -> BoxSearchPlaceholder {
    BoxSearchPlaceholder { east_m: [0.0, 1.0e9], north_m: [-1.0e9, 1.0e9], min_area_m2: 1.0, q: 0.1 }
}

fn manual_mean(s: &Settling, imp: &ImpactView, draws: usize, c: &dyn WreckageConsumerStub) -> f64 {
    let rows = s.emit(imp, draws).unwrap();
    (0..draws as u32)
        .map(|d| {
            let draw: Vec<WreckageElement> = rows.iter().filter(|r| r.draw == d).copied().collect();
            c.draw_value(imp, &draw)
        })
        .sum::<f64>()
        / draws as f64
}

#[test]
fn stream_mean_is_the_plain_average_over_draws_and_chunking_does_not_change_it() {
    let s = stream_settling();
    let imp = impact(31, 60.0, 120.0);
    let c = half_box();
    // Tolerances unreachable: the driver refines 8 -> 16 -> 32 in three emitted chunks.
    let p = StreamPolicy { pilot_draws: 8, max_draws: 32, abs_tol: 1e-12, rel_tol: 1e-12, keep_rows: false };
    let r = stream_impact(&s, &imp, None, &c, &p).unwrap();
    assert_eq!(r.draws, 32);
    let m = manual_mean(&s, &imp, 32, &c);
    assert!((r.mean - m).abs() < 1e-12, "{} vs {}", r.mean, m);
    // One chunk of 32 gives the same mean as 8 + 8 + 16.
    let one = stream_impact(&s, &imp, None, &c, &StreamPolicy { pilot_draws: 32, ..p }).unwrap();
    assert_eq!(one.mean.to_bits(), r.mean.to_bits());
}

#[test]
fn stream_empty_box_converges_at_the_pilot() {
    let s = stream_settling();
    let imp = impact(32, 60.0, 120.0);
    let far = BoxSearchPlaceholder { east_m: [5.0e5, 6.0e5], north_m: [5.0e5, 6.0e5], min_area_m2: 0.0, q: 0.9 };
    let r = stream_impact(&s, &imp, None, &far, &StreamPolicy { pilot_draws: 16, max_draws: 128, ..StreamPolicy::default() }).unwrap();
    assert_eq!((r.draws, r.converged, r.mean, r.half_width_95), (16, true, 1.0, 0.0));
}

#[test]
fn stream_refines_by_doubling_and_its_converged_flag_matches_its_numbers() {
    let s = stream_settling();
    let imp = impact(33, 60.0, 120.0);
    let c = half_box();
    for (abs_tol, rel_tol) in [(0.02, 0.2), (0.2, 0.5), (1e-6, 1e-6)] {
        let p = StreamPolicy { pilot_draws: 16, max_draws: 128, abs_tol, rel_tol, keep_rows: false };
        let r = stream_impact(&s, &imp, None, &c, &p).unwrap();
        assert!([16, 32, 64, 128].contains(&r.draws), "{}", r.draws);
        let tol = abs_tol.min(rel_tol * r.mean.abs());
        assert_eq!(r.converged, r.half_width_95 <= tol || r.half_width_95 == 0.0, "{r:?}");
        // Stops at the first doubling that meets the target, or at the maximum unconverged.
        assert!(r.converged || r.draws == 128);
        assert!((0.0..=1.0).contains(&r.mean));
    }
    // The half box genuinely varies between draws, so an unreachable target ends UNCONVERGED.
    let tight = stream_impact(&s, &imp, None, &c, &StreamPolicy { pilot_draws: 16, max_draws: 128, abs_tol: 1e-6, rel_tol: 1e-6, keep_rows: false }).unwrap();
    assert!(!tight.converged && tight.draws == 128 && tight.half_width_95 > 0.0, "{tight:?}");
}

#[test]
fn stream_kept_rows_carry_the_final_draw_weight_and_policy_is_checked() {
    let s = stream_settling();
    let imp = impact(34, 60.0, 120.0);
    let c = half_box();
    let p = StreamPolicy { pilot_draws: 8, max_draws: 16, abs_tol: 1e-12, rel_tol: 1e-12, keep_rows: true };
    let r = stream_impact(&s, &imp, Some(1), &c, &p).unwrap();
    assert_eq!(r.rows.len() as f64, r.rows_per_draw * r.draws as f64);
    assert!(r.rows.iter().all(|e| e.draw_weight == 1.0 / 16.0 && e.family == 1));
    assert!(stream_impact(&s, &imp, None, &c, &StreamPolicy { pilot_draws: 1, ..p }).is_err());
    assert!(stream_impact(&s, &imp, None, &c, &StreamPolicy { max_draws: 4, ..p }).is_err());
}

/// Cost probe, not a test: wall time of one impact's pilot (512 draws) through the run.toml
/// settling with every term on, single-threaded. `cargo test --release -p mh370-hypotheses
/// settling::tests::stream_cost -- --ignored --nocapture`.
#[test]
#[ignore]
fn stream_cost() {
    let table: toml::Table = toml::from_str(include_str!("run.toml")).unwrap();
    let s = Settling::from_params(&table["hypotheses"]["settling"]).unwrap();
    let imp = impact(35, 60.0, 120.0);
    let p = StreamPolicy { pilot_draws: 512, max_draws: 512, ..StreamPolicy::default() };
    let t = std::time::Instant::now();
    let r = stream_impact(&s, &imp, None, &half_box(), &p).unwrap();
    let dt = t.elapsed().as_secs_f64();
    println!("stream_cost: {} draws {:.3} s ({:.2} ms per draw), rows per draw {:.1}, mean {:.4} +- {:.4}", r.draws, dt, 1e3 * dt / r.draws as f64, r.rows_per_draw, r.mean, r.half_width_95);
}

// ---------------------------------------------------------------------------------------------
// Shared products adopted 9 Oct (ocean transport items 3 and 4).
// ---------------------------------------------------------------------------------------------

#[test]
fn each_floater_stops_at_its_own_sink_time() {
    // Float times spread over 0.5-2 h in one draw, a uniform surface current, nothing else: each
    // element leaves the surface at current x its own float time (Particle.end_time), then sinks
    // straight down through still water.
    let mut o = stub();
    o.spec.surface_current_mps = [0.25, -0.04];
    let mut b = one_floater(1.0, 0.0);
    for row in b.elements.iter_mut() {
        for e in row.iter_mut() {
            e.float_s = Range { lo: 1800.0, hi: 7200.0, log: false };
        }
    }
    let s = settling(b, o, &["float", "current"]);
    let rows = s.emit(&impact(41, 60.0, 120.0), 2).unwrap();
    let floats: Vec<f64> = rows.iter().map(|r| r.float_s).collect();
    assert!(floats.iter().any(|&t| t < 3000.0) && floats.iter().any(|&t| t > 6000.0), "{floats:?}");
    for r in &rows {
        assert_eq!(r.fate, Fate::Settled);
        assert!((r.east_m - 0.25 * r.float_s).abs() < 1e-6 * r.float_s && (r.north_m + 0.04 * r.float_s).abs() < 1e-6 * r.float_s, "{r:?}");
    }
}

#[test]
fn near_bottom_band_acts_only_within_its_height_above_the_seabed() {
    // Error only in the near-bottom band (factors [0, 0, 0, 1], 200 m), identical sinkers at W:
    // each draw's offset is that band's velocity x 200 / W, so E|offset|^2 = 2 sigma^2 (200/W)^2.
    let mut o = stub();
    o.error = OceanErrorModel { kind: ErrorKind::UniformOffset { sigma_m_s: 0.05 }, vertical: VerticalStructure::Banded { surface_to_m: 100.0, upper_to_m: 1000.0, near_bottom_m: 200.0, factors: [0.0, 0.0, 0.0, 1.0] } };
    let s = settling(one_sinker(0.0, 1.0), o, &["ocean-error"]);
    let draws = 400;
    let rows = s.emit(&impact(42, 60.0, 120.0), draws).unwrap();
    let mut ms = 0.0;
    for d in 0..draws as u32 {
        let r = rows.iter().find(|r| r.draw == d).unwrap();
        ms += r.east_m * r.east_m + r.north_m * r.north_m;
    }
    ms /= draws as f64;
    let expected = 2.0 * 0.05f64.powi(2) * (200.0 / W).powi(2);
    assert!((ms / expected - 1.0).abs() < 0.2, "{ms} vs {expected}");
    // With the band height zero the same error moves nothing.
    let mut o0 = stub();
    o0.error = OceanErrorModel { kind: ErrorKind::UniformOffset { sigma_m_s: 0.05 }, vertical: VerticalStructure::Banded { surface_to_m: 100.0, upper_to_m: 1000.0, near_bottom_m: 0.0, factors: [0.0, 0.0, 0.0, 1.0] } };
    let s0 = settling(one_sinker(0.0, 1.0), o0, &["ocean-error"]);
    assert!(s0.emit(&impact(42, 60.0, 120.0), 8).unwrap().iter().all(|r| r.east_m.abs() < 1e-9 && r.north_m.abs() < 1e-9));
}

#[test]
fn density_levels_interpolate_and_hold_at_the_ends() {
    let c = RhoColumn::Levels { depth_m: vec![0.0, 1000.0, 3000.0], rho_kg_m3: vec![1025.0, 1032.0, 1042.0] };
    assert_eq!((c.at(-5.0), c.at(0.0), c.at(500.0), c.at(2000.0), c.at(3000.0), c.at(6000.0)), (1025.0, 1025.0, 1028.5, 1037.0, 1042.0, 1042.0));
}

#[test]
fn bands_and_efold_are_exclusive_and_bands_are_checked() {
    let parse = |t: &str| -> Result<OceanErrorModel, String> { toml::from_str::<ErrorSpec>(t).map_err(|e| e.to_string())?.model() };
    let bands = "kind = 'uniform-offset'\nsigma_m_s = 0.1\n[bands]\nsurface_to_m = 100.0\nupper_to_m = 1000.0\nnear_bottom_m = 200.0\nfactors = [1.0, 0.5, 0.2, 0.3]\n";
    assert!(matches!(parse(bands).unwrap().vertical, VerticalStructure::Banded { .. }));
    assert!(parse(&format!("efold_m = 500.0\n{bands}")).is_err());
    assert!(parse(&bands.replace("upper_to_m = 1000.0", "upper_to_m = 50.0")).is_err());
}

/// Needs the shared products on disk (run.toml [shared]); run with `-- --ignored`.
#[test]
#[ignore]
fn shared_products_load_and_answer() {
    let table: toml::Table = toml::from_str(include_str!("run.toml")).unwrap();
    let s = Settling::from_params(&table["hypotheses"]["settling"]).unwrap();
    assert!(matches!(s.ocean.seabed, Seabed::Shared(_)) && matches!(s.ocean.density, Density::Woa23(_)));
    let imp = impact(43, 60.0, 120.0);
    let z = s.ocean.seabed.depth_at([imp.longitude_deg, imp.latitude_deg]).unwrap();
    let rho = s.ocean.density.column(&imp).unwrap();
    println!("shared: seabed at 92E 35S {z:.0} m; rho 0 m {:.3}, 1000 m {:.3}, 4000 m {:.3} kg/m3", rho.at(0.0), rho.at(1000.0), rho.at(4000.0));
    assert!((1000.0..7000.0).contains(&z));
    assert!((1022.0..1028.0).contains(&rho.at(0.0)) && (1040.0..1050.0).contains(&rho.at(4000.0)));
    // Outside the loaded window: no seabed, never a default depth.
    assert!(s.ocean.seabed.depth_at([115.0, -35.0]).is_none());
    // An impact in another month is refused, not given March water.
    let mut feb = impact(44, 60.0, 120.0);
    feb.unix_s -= 30.0 * 86_400.0;
    assert!(s.emit(&feb, 1).is_err());
    let rows = s.emit(&imp, 16).unwrap();
    let settled: Vec<_> = rows.iter().filter(|r| r.fate == Fate::Settled).collect();
    assert!(!settled.is_empty() && settled.iter().all(|r| (1000.0..7000.0).contains(&r.depth_m)));
}
