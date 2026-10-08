//! Brief section 11: a hand-computed terminal velocity; the limiting case (no current, no glide:
//! directly below); closed-form checks (uniform current at constant sink speed, a two-layer
//! current, a sloping seabed); one synthetic-recovery coverage test; plus the weighting, mass,
//! coherence and determinism fixtures that the sample contract depends on.

use super::*;
use physics::{terminal_speed, Range, GRAVITY};

fn stub() -> AnalyticStub {
    AnalyticStub {
        label: "test stub".into(),
        reference_latitude_deg: -35.0,
        reference_longitude_deg: 92.0,
        seabed_depth_m: 4000.0,
        seabed_slope_deg: 0.0,
        seabed_slope_azimuth_deg: 0.0,
        surface_current_mps: [0.0; 2],
        wind_mps: [0.0; 2],
        upper_current_mps: [0.0; 2],
        deep_current_mps: [0.0; 2],
        layer_depth_m: 1000.0,
        model_bottom_m: 7000.0,
        surface_density_kg_m3: 1025.0,
        density_gradient_kg_m3_per_km: 0.0,
        error: ErrorModel { surface_mps: 0.0, upper_mps: 0.0, upper_depth_m: 1000.0, deep_mps: 0.0, near_bottom_mps: 0.0, near_bottom_m: 0.0 },
    }
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

fn settling(b: Breakup, ocean: AnalyticStub, terms: &[&str]) -> Settling {
    let terms: Vec<String> = terms.iter().map(|s| s.to_string()).collect();
    Settling::with(b, Box::new(ocean), &terms, 1.0, 50.0, 64).unwrap()
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
    o.upper_current_mps = [0.1, -0.05];
    o.deep_current_mps = [0.1, -0.05];
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
    o.upper_current_mps = [0.2, 0.0];
    o.deep_current_mps = [0.0, 0.02];
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
    o.seabed_slope_deg = 10.0;
    o.seabed_slope_azimuth_deg = 180.0;
    o.upper_current_mps = [0.0, 0.3];
    o.deep_current_mps = [0.0, 0.3];
    let s = settling(one_sinker(0.0, 1.0), o, &["current"]);
    for r in s.emit(&impact(4, 50.0, 80.0), 2).unwrap() {
        assert!((r.depth_m - 3931.17).abs() < 0.5 && (r.north_m - 390.36).abs() < 0.5, "{r:?}");
    }
}

#[test]
fn below_model_bottom_is_extrapolated_explicitly_and_recorded() {
    // Model bottom 3,000 m over a 4,000 m seabed, deep current 0.1 m/s east.
    let mut o = stub();
    o.model_bottom_m = 3000.0;
    o.deep_current_mps = [0.1, 0.0];
    let terms: Vec<String> = vec!["current".into()];
    let hold = Settling::with(one_sinker(0.0, 1.0), Box::new(o.clone()), &terms, 1.0, 50.0, 8).unwrap();
    let zero = Settling::with(one_sinker(0.0, 1.0), Box::new(o), &terms, 0.0, 50.0, 8).unwrap();
    let (a, b) = (hold.emit(&impact(5, 50.0, 80.0), 1).unwrap(), zero.emit(&impact(5, 50.0, 80.0), 1).unwrap());
    // The deep layer starts at 1,000 m in the stub, smeared over 950-1,000 m by the level
    // interpolation (effective interface 975 m, see the two-layer test). Hold:
    // 0.1 x (4000 - 975) / w = 100.1274 m; explicit zero: 0.1 x (3000 - 975) / w = 67.0274 m.
    assert!((a[0].east_m - 100.1274).abs() < 0.001 && (b[0].east_m - 67.0274).abs() < 0.001, "{:?} {:?}", a[0], b[0]);
    assert!((a[0].below_model_bottom_m - 1000.0).abs() < 1e-9);
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
    let s = settling(Breakup::parse(include_str!("breakup.toml")).unwrap(), stub(), &["carry", "float", "current", "glide", "ocean-error"]);
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
    let s = settling(Breakup::parse(include_str!("breakup.toml")).unwrap(), stub(), &["carry", "float", "current", "glide", "ocean-error"]);
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
    o.error = ErrorModel { surface_mps: 0.0, upper_mps: 0.05, upper_depth_m: 1000.0, deep_mps: 0.05, near_bottom_mps: 0.0, near_bottom_m: 0.0 };
    o.upper_current_mps = [0.0; 2];
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
    o.upper_current_mps = [0.05, 0.02];
    o.deep_current_mps = [0.02, 0.01];
    o.error = ErrorModel { surface_mps: 0.1, upper_mps: 0.05, upper_depth_m: 1000.0, deep_mps: 0.02, near_bottom_mps: 0.03, near_bottom_m: 200.0 };
    let s = settling(Breakup::parse(include_str!("breakup.toml")).unwrap(), o, &["carry", "float", "current", "glide", "ocean-error"]);
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
fn run_toml_constructs_and_predict_fills_or_refuses() {
    let text = include_str!("run.toml");
    let table: toml::Table = toml::from_str(text).unwrap();
    let params = &table["hypotheses"]["settling"];
    let h = new(params).unwrap();
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
