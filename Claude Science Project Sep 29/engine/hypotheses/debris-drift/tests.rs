//! Brief section 11, drift side: interpolation and the land rule, the source grid, hand-computed
//! fixtures for the recovery layer (D5 with G1 blocks), the transport adapter against closed
//! form, and one synthetic-recovery coverage test. Transport numerics (constant-current
//! displacement, random-walk RMS, drogued replay) are the shared crate's tests.

use super::evidence::{days_from_civil, parse, TABLE};
use super::interpolate::{Lookup, Node, Surface};
use super::recovery::{dot, great_circle_km, phi, Arrival, Delay, Edge, LevelDraws, Observation, Place, Recovery};
use super::rng::Rng;
use super::segments::SegmentMap;
use super::source_grid::{SourceGrid, WeightedCell};
use super::transport::{response, Fate, OceanSetup, TransportParams};
use super::{build, node_ln_likelihood, parse_cells, stringent_intervals, Params, REFERENCE_MAP};
use ocean::{Diffusion, Domain, Particle};

const T0: f64 = 1_394_237_977.0;

fn k0(h: f64) -> f64 {
    1.0 / (h * std::f64::consts::TAU.sqrt())
}
fn on0(s: f64) -> Place {
    Place::on_line(0, s, [0.0, 0.0])
}
fn arr(s: f64, t: f64, seg: usize) -> Arrival {
    Arrival { place: on0(s), segment: Some(seg), t_days: t }
}
fn obs(s: f64, a: f64, b: f64, seg: usize) -> Observation {
    Observation { id: "t".into(), class: 0, place: on0(s), segment: seg, t_start_days: a, t_end_days: b }
}
fn rec(edges: &[f64], breaks: Vec<f64>, h: f64, delay: Delay, end: f64) -> Recovery {
    let e: Vec<Edge> = edges.windows(2).enumerate().map(|(k, w)| Edge { line: 0, start_km: w[0], end_km: w[1], segment: k }).collect();
    Recovery { n_segments: e.len(), breaks_days: breaks, edges: e, delay, bandwidth_km: h, window_end_days: end }
}
/// ln prod_j q_j / Q at fixed levels.
fn ln_l(r: &Recovery, o: &[Observation], a: &[Arrival], n: usize, nu: &[f64]) -> f64 {
    let refs: Vec<&Observation> = o.iter().collect();
    let k = r.coefficients(&refs, a, n);
    let q_tot = dot(&k.big_a, nu);
    k.a.iter().map(|aj| dot(aj, nu).ln() - q_tot.ln()).sum()
}

fn plane_surface() -> Surface {
    // ln of L = 1 + 2 lat + 3 lon on a 3 x 3 unit grid: bilinear interpolation of L is exact.
    let nodes = (0..9).map(|k| Node::Value((1.0 + 2.0 * (k / 3) as f64 + 3.0 * (k % 3) as f64).ln())).collect();
    Surface { lat0: 0.0, lon0: 0.0, dlat: 1.0, dlon: 1.0, nlat: 3, nlon: 3, nodes }
}

#[test]
fn interpolation_is_linear_in_likelihood_and_exact_at_nodes() {
    let s = plane_surface();
    let Lookup::Value(v) = s.ln_likelihood(0.3, 1.6) else { panic!() };
    assert!((v - 6.4f64.ln()).abs() < 1e-12);
    let Lookup::Value(v) = s.ln_likelihood(2.0, 2.0) else { panic!() };
    assert!((v - 11.0f64.ln()).abs() < 1e-12);
}

#[test]
fn land_corners_renormalise_and_missing_corners_flag() {
    let mut s = plane_surface();
    s.nodes[0] = Node::Land;
    let Lookup::Value(v) = s.ln_likelihood(0.5, 0.5) else { panic!() };
    assert!((v - (13.0f64 / 3.0).ln()).abs() < 1e-12, "renormalise across land, never fill with zero");
    s.nodes[0] = Node::NotComputed;
    assert_eq!(s.ln_likelihood(0.5, 0.5), Lookup::OutsideSupport);
    let Lookup::Value(_) = s.ln_likelihood(1.0, 1.0) else { panic!("zero-weight corner must not flag") };
    s.nodes[0] = Node::Unresolved;
    assert_eq!(s.ln_likelihood(0.2, 0.2), Lookup::Unresolved);
    assert_eq!(s.ln_likelihood(1.0, 2.0001), Lookup::OutsideSupport, "never extrapolate");
}

fn blob(lat: f64, lon: f64, n: i32, mass: f64) -> Vec<WeightedCell> {
    let mut v = Vec::new();
    for i in -n..=n {
        for j in -n..=n {
            v.push(WeightedCell { lat: lat + 0.25 * i as f64, lon: lon + 0.25 * j as f64, mass });
        }
    }
    v
}

#[test]
fn source_grid_separates_main_band_and_island() {
    let mut cells = blob(-37.0, 95.0, 3, 0.95 / 49.0);
    cells.extend(blob(-29.0, 100.0, 1, 0.05 / 9.0));
    let g = SourceGrid::from_posterior(&cells, 0.25, 0.99, 10.0, 30.0, 40.0, false).unwrap();
    let gi = SourceGrid::from_posterior(&cells, 0.25, 0.99, 10.0, 30.0, 40.0, true).unwrap();
    assert!(g.component_mass.len() >= 2 && g.component_mass[g.main_component] > 0.9 && g.covered_mass >= 0.99);
    assert!(gi.n_active() > g.n_active());
    let g5 = SourceGrid::from_posterior(&cells, 0.25, 0.99, 5.0, 30.0, 40.0, false).unwrap();
    let ratio = g5.n_active() as f64 / g.n_active() as f64;
    assert!((3.0..5.0).contains(&ratio), "halving spacing gave x{ratio}");
}

#[test]
fn reference_extent_main_band_is_the_measured_size() {
    let cells = parse_cells(REFERENCE_MAP).unwrap();
    let g = SourceGrid::from_posterior(&cells, 0.25, 0.99, 10.0, 100.0, 40.0, false).unwrap();
    assert_eq!(g.n_active(), 1709, "results/debris-drift-pilot-sizing.md");
}

#[test]
fn recovery_hand_fixture_and_unbeached_particles_cancel() {
    let r = rec(&[-1e6, 1e6], vec![], 5.0, Delay::Uniform { max_days: 10.0 }, 100.0);
    let a = [arr(0.0, 0.0, 0), arr(0.0, 5.0, 0)];
    let o = [obs(0.0, 6.0, 7.0, 0)];
    let k = r.coefficients(&[&o[0]], &a, 2);
    assert!((k.a[0][0] - 0.1 * k0(5.0)).abs() < 1e-12 && (k.n_eff[0] - 2.0).abs() < 1e-12);
    assert!((k.big_a[0] - 1.0).abs() < 1e-9);
    let (l2, l3) = (ln_l(&r, &o, &a, 2, &[1.0]), ln_l(&r, &o, &a, 3, &[1.0]));
    assert!((l2 - l3).abs() < 1e-9, "a particle that never beaches changes q and Q but not q/Q");
}

#[test]
fn lambda_marginal_is_independent_of_q() {
    // integral_0^inf Poisson(N; lambda Q) dlambda / lambda = Gamma(N)/N! = 1/N for every Q.
    for n in [1u32, 9, 41] {
        let ln_nfact: f64 = (1..=n).map(|k| (k as f64).ln()).sum();
        for q in [1e-4, 1.0, 5.0] {
            let du = 1e-3;
            let s: f64 = (0..80_000).map(|i| { let u = -40.0 + i as f64 * du; let v = u.exp() * q; (-v + n as f64 * v.ln() - ln_nfact).exp() * du }).sum();
            assert!((s * n as f64 - 1.0).abs() < 1e-6, "N={n} Q={q}: {s}");
        }
    }
}

fn two_by_two() -> (Recovery, Vec<Arrival>, Vec<Observation>) {
    let r = rec(&[-500.0, 0.0, 500.0], vec![50.0], 30.0, Delay::Exponential { mean_days: 20.0 }, 300.0);
    let a: Vec<Arrival> = (0..40).map(|i| { let s = -400.0 + 20.0 * i as f64; arr(s, 10.0 + 3.0 * i as f64, if s < 0.0 { 0 } else { 1 }) }).collect();
    (r, a, vec![obs(-120.0, 60.0, 61.0, 0), obs(250.0, 30.0, 45.0, 1)])
}

#[test]
fn a_global_constant_in_the_levels_cancels_but_block_ratios_do_not() {
    let (r, a, o) = two_by_two();
    let nu = [1.0, 3.0, 2.0, 0.5];
    let scaled: Vec<f64> = nu.iter().map(|v| 7.0 * v).collect();
    assert!((ln_l(&r, &o, &a, 100, &nu) - ln_l(&r, &o, &a, 100, &scaled)).abs() < 1e-12);
    let changed = [1.0, 3.0, 2.0, 5.0];
    assert!((ln_l(&r, &o, &a, 100, &nu) - ln_l(&r, &o, &a, 100, &changed)).abs() > 1e-3, "block levels are not a free constant");
}

#[test]
fn coefficients_are_linear_in_the_levels() {
    // q and Q computed through the coefficients equal a direct sum over arrivals with nu inline.
    let (r, a, o) = two_by_two();
    let nu = [1.0, 3.0, 2.0, 0.5];
    let k = r.coefficients(&[&o[0], &o[1]], &a, 100);
    let direct_q0: f64 = a.iter().map(|x| {
        let z = (o[0].place.s_km - x.place.s_km) / 30.0;
        let f = |t: f64| Delay::Exponential { mean_days: 20.0 }.cdf(t - x.t_days);
        k0(30.0) * (-0.5 * z * z).exp() * nu[0 * 2 + 1] * (f(61.0) - f(60.0))
    }).sum::<f64>() / 100.0;
    assert!((dot(&k.a[0], &nu) - direct_q0).abs() < 1e-15, "{} vs {direct_q0}", dot(&k.a[0], &nu));
}

#[test]
fn absence_counts_only_where_identification_was_possible() {
    let a_src: Vec<Arrival> = (0..100).map(|i| if i < 50 { arr(-500.0, 10.0, 0) } else { arr(500.0, 10.0, 1) }).collect();
    let b_src: Vec<Arrival> = (0..100).map(|_| arr(500.0, 10.0, 1)).collect();
    let o = vec![obs(500.0, 15.0, 16.0, 1); 3];
    let r = rec(&[-1000.0, 0.0, 1000.0], vec![], 20.0, Delay::Uniform { max_days: 30.0 }, 200.0);
    let ratio = ln_l(&r, &o, &b_src, 200, &[1.0, 1.0]) - ln_l(&r, &o, &a_src, 200, &[1.0, 1.0]);
    assert!((ratio - 8f64.ln()).abs() < 1e-9, "no finds on a searched coast penalises A by 2^3: {ratio}");
    let ratio = ln_l(&r, &o, &b_src, 200, &[0.0, 1.0]) - ln_l(&r, &o, &a_src, 200, &[0.0, 1.0]);
    assert!(ratio.abs() < 1e-9, "an unsearched coast carries no information: {ratio}");
}

#[test]
fn time_varying_identification_hand_value() {
    let r = rec(&[-1e6, 1e6], vec![10.0], 5.0, Delay::Uniform { max_days: 20.0 }, 100.0);
    let a = [arr(0.0, 0.0, 0)];
    let nu = [0.0, 1.0];
    let k = r.coefficients(&[&obs(0.0, 12.0, 13.0, 0), &obs(0.0, 5.0, 6.0, 0)], &a, 1);
    assert!((dot(&k.big_a, &nu) - 0.5).abs() < 1e-9);
    assert!((dot(&k.a[0], &nu) - 0.05 * k0(5.0)).abs() < 1e-12);
    assert_eq!(dot(&k.a[1], &nu), 0.0);
    assert!((phi(0.0) - 0.5).abs() < 1e-7 && (phi(1.959_964) - 0.975).abs() < 1e-6);
}

#[test]
fn environment_and_levels_are_marginalised_outside_the_product() {
    let r = rec(&[-1e6, 1e6], vec![], 5.0, Delay::Uniform { max_days: 10.0 }, 100.0);
    let o = [obs(0.0, 1.0, 2.0, 0), obs(0.0, 1.0, 2.0, 0)];
    let refs: Vec<&Observation> = o.iter().collect();
    let ka = r.coefficients(&refs, &[arr(0.0, 0.0, 0)], 2);
    let kb = r.coefficients(&refs, &[arr(0.0, 0.0, 0), arr(100.0, 0.0, 0)], 2);
    let Node::Value(l) = node_ln_likelihood(&[vec![Some(ka)], vec![Some(kb)]], &[vec![0, 1]], &LevelDraws::fixed(vec![1.0])) else { panic!() };
    let k = k0(5.0);
    assert!((l - (0.006_25 * k * k).ln()).abs() < 1e-9, "(a^2 + b^2)/2, not the product of per-object means");
    assert!((l - (0.075 * k).powi(2).ln()).abs() > 0.1);
}

#[test]
fn level_draws_are_common_and_declared() {
    let a = LevelDraws::new(6, &[-2.3, -0.7, 0.0], 1.0, 256, 3);
    let b = LevelDraws::new(6, &[-2.3, -0.7, 0.0], 1.0, 256, 3);
    assert_eq!(a, b);
    let mean_ln_i1: f64 = a.draws.iter().map(|d| (0..6).map(|s| d[s * 3].ln()).sum::<f64>() / 6.0).sum::<f64>() / 256.0;
    assert!((mean_ln_i1 + 2.3).abs() < 0.15, "{mean_ln_i1}");
}

#[test]
fn evidence_table_dates_and_segments() {
    let recs = parse(TABLE).unwrap();
    assert_eq!(recs.len(), 41);
    let s: Vec<_> = recs.iter().filter(|r| r.stringent).collect();
    assert_eq!(s.len(), 9);
    assert_eq!(days_from_civil(2015, 7, 29) - days_from_civil(2014, 3, 8), 508, "Davey's 508 +/- 30 (p. 103)");
    let v = stringent_intervals(1_394_236_800.0).unwrap();
    assert_eq!((v[0].0.as_str(), v[0].1, v[0].2), ("debris:reunion-right-flaperon", 508.0, 509.0));
    // Every stringent find lies in exactly the segment the find-episode draft assigns it.
    let pilot: toml::Value = toml::from_str(include_str!("pilot.toml")).unwrap();
    let p: Params = pilot["hypotheses"]["debris-drift"].clone().try_into().unwrap();
    let map = SegmentMap::new(p.segments.clone()).unwrap();
    let names: Vec<&str> = s.iter().map(|r| map.locate([r.longitude_deg, r.latitude_deg]).map(|k| map.segments[k].name.as_str()).unwrap_or("none")).collect();
    assert_eq!(names, ["S1-reunion", "S4-south-africa-south-coast", "S3-southern-mozambique", "S3-southern-mozambique", "S2-mauritius-rodrigues", "S2-mauritius-rodrigues", "S3-southern-mozambique", "S5-ne-madagascar", "S6-pemba"]);
    assert!(great_circle_km([55.649150, -20.916180], [39.868086, -5.056071]) > 2400.0);
}

fn analytic(current: [f64; 2], wind: Option<[f64; 2]>, coast_lon: f64) -> OceanSetup {
    let t = TransportParams::Analytic { current_mps: current, wind10_mps: wind, stokes_mps: None, coast_a: [coast_lon, -60.0], coast_b: [coast_lon, 0.0], land_left: true };
    OceanSetup::new(&t, Domain { lon_min: 15.0, lon_max: 120.0, lat_min: -60.0, lat_max: 0.0 }, 21_600.0, 2, true, false, true).unwrap()
}

#[test]
fn adapter_beaching_time_and_chainage_match_closed_form() {
    let s = analytic([-0.5, 0.0], None, 94.0);
    let p = [Particle::new([95.0, -37.0], T0, response(0.0, 0.0, 0.0, 0.0))];
    let (f, _) = s.run(&p, 1, Diffusion::None, T0 + 30.0 * 86_400.0).unwrap();
    let Fate::Beached { t, at, line, chainage_km } = f[0] else { panic!("{:?}", f[0]) };
    let dist_m = 6_371_008.8 * 1f64.to_radians() * (37f64).to_radians().cos();
    assert!(((t - T0) - dist_m / 0.5).abs() / ((t - T0)) < 2e-3, "{} vs {}", t - T0, dist_m / 0.5);
    assert!((at[0] - 94.0).abs() < 1e-6 && line == Some(0));
    assert!((chainage_km - 6_371.008_8 * 23f64.to_radians()).abs() < 1.0, "{chainage_km}");
}

#[test]
fn flaperon_response_and_the_e1_refusal() {
    // 0.10 m/s constant-speed leeway, 16 deg left of a westward wind, nothing else: drift is
    // 8.64 km/day, with a southward share sin 16 deg (left of westward is south).
    let s = analytic([0.0, 0.0], Some([-8.0, 0.0]), 85.0);
    let p = [Particle::new([95.0, -37.0], T0, response(0.0, 0.0, -16.0, 0.10))];
    let (f, _) = s.run(&p, 1, Diffusion::None, T0 + 200.0 * 86_400.0).unwrap();
    let Fate::Beached { t, at, .. } = f[0] else { panic!("{:?}", f[0]) };
    let days = (t - T0) / 86_400.0;
    let south_km = (-37.0 - at[1]) * 111.195;
    assert!((south_km / days - 8.64 * 16f64.to_radians().sin()).abs() < 0.05, "{} km/day south", south_km / days);
    let bad = [Particle::new([95.0, -37.0], T0, response(1.0, 0.0, -16.0, 0.10))];
    let t = TransportParams::Analytic { current_mps: [0.0, 0.0], wind10_mps: Some([-8.0, 0.0]), stokes_mps: Some([0.05, 0.0]), coast_a: [60.0, -60.0], coast_b: [60.0, 0.0], land_left: true };
    let s = OceanSetup::new(&t, Domain { lon_min: 15.0, lon_max: 120.0, lat_min: -60.0, lat_max: 0.0 }, 21_600.0, 2, false, false, true).unwrap();
    assert!(s.run(&bad, 1, Diffusion::None, T0 + 86_400.0).is_err(), "constant leeway with explicit Stokes is the transplanted system (E1)");
}

fn small(mut t: toml::Value, entries: &[(&str, toml::Value)]) -> Params {
    for (k, v) in entries {
        t.as_table_mut().unwrap().insert((*k).into(), v.clone());
    }
    t.try_into().unwrap()
}

#[test]
fn run_toml_builds_and_scores_synthetic_finds() {
    let run: toml::Value = toml::from_str(include_str!("run.toml")).unwrap();
    let p = small(run["hypotheses"]["debris-drift"].clone(), &[("particles_per_class", toml::Value::Integer(60)), ("node_subset", toml::Value::Array((0..20).map(|i| toml::Value::Integer(4000 + 37 * i)).collect()))]);
    let b = build(&p).unwrap();
    assert_eq!(b.observations.len(), 9);
    assert!(b.ocean_model.starts_with("analytic"), "{}", b.ocean_model);
    let released: usize = b.summary.iter().find(|x| x.0 == "nodes_released").unwrap().1.parse().unwrap();
    assert!(released > 0);
}

#[test]
fn synthetic_recovery_coverage() {
    // Finds generated from a node drawn uniformly from a small grid (independent ensembles),
    // scored with the module's own layers and level marginalisation; the 90% HPD set should
    // contain the truth about 90% of the time, and E[p(truth)] / E[sum p^2] should be near 1.
    let grid = SourceGrid::rectangle(-37.5, 94.8, 7, 3, 10.0);
    let setup = analytic([-0.2, 0.0], None, 92.0);
    let r = rec(&(0..=40).map(|i| 2000.0 + 100.0 * i as f64).collect::<Vec<_>>(), vec![30.0], 10.0, Delay::Uniform { max_days: 10.0 }, 60.0);
    let levels = LevelDraws::new(r.n_segments, &[-1.0, 0.0], 0.5, 16, 5);
    let n = 400;
    let mut rng = Rng::new(17);
    let resp: Vec<_> = (0..n).map(|_| response(0.0, 0.0, 0.0, 0.0)).collect();
    let nodes: Vec<[f64; 2]> = (0..21).map(|k| { let (la, lo) = grid.node(k); [lo, la] }).collect();
    let loc = super::Locator { map: None, edges: r.edges.clone() };
    let t_end = T0 + 60.0 * 86_400.0;
    let ens: Vec<Vec<Arrival>> = nodes.iter().map(|&ll| super::run_ensemble(&setup, &loc, ll, T0, t_end, &resp, 5, Diffusion::Diffusivity { k_m2_s: 100.0 }).unwrap().0.arrivals.into_iter().map(|x| x.1).collect()).collect();
    let trials = 60;
    let (mut hits, mut p_truth, mut p_sq) = (0, 0.0, 0.0);
    for t in 0..trials {
        let truth = (rng.uniform() * 21.0) as usize;
        let gen = super::run_ensemble(&setup, &loc, nodes[truth], T0, t_end, &resp[..200], 9_000 + t as u64, Diffusion::Diffusivity { k_m2_s: 100.0 }).unwrap().0;
        let mut o = Vec::new();
        for (_, a) in gen.arrivals {
            if o.len() == 4 { break; }
            let tt = a.t_days + 10.0 * rng.uniform();
            if tt >= 60.0 { continue; }
            let s = a.place.s_km + 10.0 * rng.normal();
            let Some(e) = r.edges.iter().find(|e| s >= e.start_km && s < e.end_km) else { continue };
            let top = levels.draws[0].iter().copied().fold(0.0, f64::max);
            if rng.uniform() * top >= levels.draws[0][e.segment * 2 + r.period(tt)] { continue; }
            o.push(Observation { id: "s".into(), class: 0, place: on0(s), segment: e.segment, t_start_days: tt.floor(), t_end_days: tt.floor() + 1.0 });
        }
        let refs: Vec<&Observation> = o.iter().collect();
        let ll: Vec<f64> = ens.iter().map(|a| match node_ln_likelihood(&[vec![Some(r.coefficients(&refs, a, n))]], &[(0..o.len()).collect()], &levels) { Node::Value(v) => v, _ => f64::NEG_INFINITY }).collect();
        let m = ll.iter().copied().fold(f64::NEG_INFINITY, f64::max);
        let w: Vec<f64> = ll.iter().map(|v| (v - m).exp()).collect();
        let tot: f64 = w.iter().sum();
        p_truth += w[truth] / tot;
        p_sq += w.iter().map(|x| (x / tot).powi(2)).sum::<f64>();
        let mut idx: Vec<usize> = (0..21).collect();
        idx.sort_by(|&a, &b| w[b].partial_cmp(&w[a]).unwrap());
        let mut c = 0.0;
        for &k in &idx {
            c += w[k] / tot;
            if k == truth { hits += 1; break; }
            if c >= 0.9 { break; }
        }
    }
    let cov = hits as f64 / trials as f64;
    let calib = p_truth / p_sq;
    println!("synthetic-recovery: 90% HPD coverage {cov} ({hits}/{trials}); calibration ratio {calib:.3}");
    assert!((0.75..=1.0).contains(&cov), "coverage {cov}");
    assert!((0.6..1.4).contains(&calib), "calibration ratio {calib}");
}

/// The pilot (brief section 5). Heavy: run only under the machine lock, e.g.
/// `DRIFT_CONFIG=hypotheses/debris-drift/pilot.toml lockf -k /tmp/.mh370-heavy.lock cargo test
/// --release -p mh370-hypotheses debris_drift::tests::pilot -- --ignored --nocapture`.
#[test]
#[ignore]
fn pilot() {
    let path = std::env::var("DRIFT_CONFIG").expect("set DRIFT_CONFIG to a run.toml with [hypotheses.debris-drift]");
    let run: toml::Value = toml::from_str(&std::fs::read_to_string(&path).unwrap()).unwrap();
    let p: Params = run["hypotheses"]["debris-drift"].clone().try_into().unwrap();
    let b = build(&p).unwrap();
    for (k, v) in &b.summary {
        println!("{k} = {v}");
    }
}
