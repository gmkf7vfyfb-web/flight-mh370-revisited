//! Brief section 11: analytic displacement, random-walk RMS, the land rule, hand-computed
//! fixtures for the recovery layer, and one synthetic-recovery coverage test. GDP drifter replay
//! (undrogued) belongs here once real transport exists; drogued replay is the shared owner's.

use super::evidence::{days_from_civil, parse, TABLE};
use super::interpolate::{Lookup, Node, Surface};
use super::provisional_analytic_ocean::{AnalyticOcean, Coast, Current, Response};
use super::recovery::{phi, Arrival, Delay, Identification, Observation, Recovery};
use super::rng::Rng;
use super::source_grid::{SourceGrid, WeightedCell};
use super::transport::{Fate, ObjectResponse, Particle, StubTransport, Transport};
use super::{build_stub, node_ln_likelihood, parse_cells, run_ensemble, stringent_intervals, synthetic_finds, ClassParams, Params, REFERENCE_MAP};

fn ocean(current: Current, k: f64, coast: Option<Coast>) -> AnalyticOcean {
    AnalyticOcean { current, current_scale: 1.0, stokes: (0.0, 0.0), wind: (0.0, 0.0), diffusivity_m2s: k, coast }
}
const STILL: Response = Response { a_stokes: 0.0, c_wind: 0.0 };
fn k0(h: f64) -> f64 {
    1.0 / (h * std::f64::consts::TAU.sqrt())
}
fn obs(s: f64, a: f64, b: f64) -> Observation {
    Observation { id: "t".into(), class: 0, s_km: s, t_start_days: a, t_end_days: b }
}
fn rec(edges: Vec<f64>, h: f64, delay: Delay, end: f64) -> Recovery {
    Recovery { ident: Identification::uniform(edges), delay, bandwidth_km: h, window_end_days: end }
}
fn ln_l(r: &Recovery, o: &[Observation], a: &[Arrival], n: usize) -> f64 {
    let q_tot = r.q_total(a, n);
    o.iter().map(|x| r.q(x, a, n).q.ln() - q_tot.ln()).sum()
}

#[test]
fn constant_current_displacement_is_exact() {
    let oc = ocean(Current::Uniform { east: 0.2, north: -0.1 }, 0.0, None);
    let f = oc.integrate(0.0, 0.0, &STILL, 21_600.0, 400, &mut Rng::new(1));
    assert!((f.x_km - 1728.0).abs() < 1e-9 && (f.y_km + 864.0).abs() < 1e-9, "{f:?}");
    assert!(!f.beached && (f.t_days - 100.0).abs() < 1e-12);
}

#[test]
fn random_walk_rms_matches_closed_form() {
    // 2-D isotropic walk: <r^2> = 4 K t. K = 100 m2/s over 30 days -> 1036.8 km2.
    let oc = ocean(Current::Uniform { east: 0.0, north: 0.0 }, 100.0, None);
    let mut rng = Rng::new(7);
    let n = 20_000;
    let mean_r2: f64 = (0..n).map(|_| { let f = oc.integrate(0.0, 0.0, &STILL, 21_600.0, 120, &mut rng); f.x_km * f.x_km + f.y_km * f.y_km }).sum::<f64>() / n as f64;
    let expect = 4.0 * 100.0 * 30.0 * 86_400.0 / 1e6;
    assert!((mean_r2 / expect - 1.0).abs() < 0.03, "{mean_r2} vs {expect}");
}

#[test]
fn solid_body_rotation_keeps_radius_and_phase() {
    let omega = std::f64::consts::TAU / (30.0 * 86_400.0);
    let oc = ocean(Current::SolidBody { omega, cx: 0.0, cy: 0.0 }, 0.0, None);
    let f = oc.integrate(100.0, 0.0, &STILL, 21_600.0, 120, &mut Rng::new(1));
    let r = f.x_km.hypot(f.y_km);
    assert!((r / 100.0 - 1.0).abs() < 1e-3, "radius {r}");
    assert!((f.x_km - 100.0).hypot(f.y_km) < 1.0, "phase error {f:?}");
}

#[test]
fn coast_crossing_is_located_within_the_step() {
    let coast = Coast::through((-100.0, -1000.0), (-100.0, 1000.0), (0.0, 0.0));
    let oc = ocean(Current::Uniform { east: -0.5, north: 0.0 }, 0.0, Some(coast));
    let f = oc.integrate(0.0, 0.0, &STILL, 21_600.0, 100, &mut Rng::new(1));
    assert!(f.beached);
    assert!((f.t_days - 100_000.0 / 0.5 / 86_400.0).abs() < 1e-9, "{}", f.t_days);
    assert!((f.x_km + 100.0).abs() < 1e-9 && f.y_km.abs() < 1e-12 && f.s_km.abs() < 1e-12);
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
    let Lookup::Value(v) = s.ln_likelihood(1.0, 2.0) else { panic!() };
    assert!((v - 9.0f64.ln()).abs() < 1e-12);
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
    assert_eq!(s.ln_likelihood(-0.01, 1.0), Lookup::OutsideSupport);
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
    let g = SourceGrid::from_posterior(&cells, 0.25, 0.99, 10.0, 30.0, 60.0, false).unwrap();
    let gi = SourceGrid::from_posterior(&cells, 0.25, 0.99, 10.0, 30.0, 60.0, true).unwrap();
    assert!(g.component_mass.len() >= 2);
    assert!(g.component_mass[g.main_component] > 0.9);
    assert!(g.covered_mass >= 0.99);
    assert!(gi.n_active() > g.n_active());
    let g5 = SourceGrid::from_posterior(&cells, 0.25, 0.99, 5.0, 30.0, 60.0, false).unwrap();
    let ratio = g5.n_active() as f64 / g.n_active() as f64;
    assert!((3.0..5.0).contains(&ratio), "halving spacing gave x{ratio}");
}

#[test]
fn reference_extent_cell_counts() {
    // Pilot sizing table from the provisional extent source (00:19:37 core-only posterior).
    let cells = parse_cells(REFERENCE_MAP).unwrap();
    println!("coverage spacing_nm margin_nm main_nodes island_nodes components main_mass covered main_lat_range");
    for (cov, sp, margin) in [(0.5, 10.0, 100.0), (0.9, 10.0, 100.0), (0.95, 10.0, 100.0), (0.99, 5.0, 100.0), (0.99, 10.0, 100.0), (0.99, 20.0, 100.0), (0.99, 10.0, 50.0), (0.99, 10.0, 0.0), (0.98, 10.0, 100.0), (0.999, 10.0, 100.0)] {
        {
            let g = SourceGrid::from_posterior(&cells, 0.25, cov, sp, margin, 40.0, true).unwrap();
            let main = g.component_nodes(g.main_component);
            let lats: Vec<f64> = (0..g.active.len()).filter(|&k| g.component[k] == g.main_component as i32).map(|k| g.node(k).0).collect();
            println!("{cov} {sp} {margin} {main} {} {} {:.4} {:.4} {:.2}..{:.2}", g.n_active() - main, g.component_mass.len(), g.component_mass[g.main_component], g.covered_mass, lats.iter().copied().fold(f64::INFINITY, f64::min), lats.iter().copied().fold(f64::NEG_INFINITY, f64::max));
            if cov == 0.99 && sp == 10.0 && margin == 100.0 {
                assert!((200..20_000).contains(&main), "{main}");
            }
        }
    }
}

#[test]
fn recovery_hand_fixture_and_unbeached_particles_cancel() {
    let r = rec(vec![-1e6, 1e6], 5.0, Delay::Uniform { max_days: 10.0 }, 100.0);
    let a = [Arrival { s_km: 0.0, t_days: 0.0 }, Arrival { s_km: 0.0, t_days: 5.0 }];
    let o = obs(0.0, 6.0, 7.0);
    let f = r.q(&o, &a, 2);
    assert!((f.q - 0.1 * k0(5.0)).abs() < 1e-12 && (f.n_eff - 2.0).abs() < 1e-12);
    assert!((r.q_total(&a, 2) - 1.0).abs() < 1e-9);
    // A third particle that never beaches changes q and Q but not q/Q.
    let l2 = ln_l(&r, std::slice::from_ref(&o), &a, 2);
    let l3 = ln_l(&r, std::slice::from_ref(&o), &a, 3);
    assert!((l2 - l3).abs() < 1e-9);
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

#[test]
fn constant_identification_factor_cancels() {
    let mk = |f: f64| Recovery {
        ident: Identification { edges_km: vec![-500.0, 0.0, 500.0], breaks_days: vec![50.0], rel: vec![vec![1.0 * f, 3.0 * f], vec![2.0 * f, 0.5 * f]] },
        delay: Delay::Exponential { mean_days: 20.0 }, bandwidth_km: 30.0, window_end_days: 300.0,
    };
    let a: Vec<Arrival> = (0..40).map(|i| Arrival { s_km: -400.0 + 20.0 * i as f64, t_days: 10.0 + 3.0 * i as f64 }).collect();
    let o = [obs(-120.0, 60.0, 61.0), obs(250.0, 30.0, 45.0)];
    assert!((ln_l(&mk(1.0), &o, &a, 100) - ln_l(&mk(7.0), &o, &a, 100)).abs() < 1e-12);
}

#[test]
fn absence_counts_only_where_identification_was_possible() {
    let a_src: Vec<Arrival> = (0..100).map(|i| Arrival { s_km: if i < 50 { -500.0 } else { 500.0 }, t_days: 10.0 }).collect();
    let b_src: Vec<Arrival> = (0..100).map(|_| Arrival { s_km: 500.0, t_days: 10.0 }).collect();
    let o = [obs(500.0, 15.0, 16.0), obs(500.0, 15.0, 16.0), obs(500.0, 15.0, 16.0)];
    let searched = rec(vec![-1000.0, 0.0, 1000.0], 20.0, Delay::Uniform { max_days: 30.0 }, 200.0);
    let ratio = ln_l(&searched, &o, &b_src, 200) - ln_l(&searched, &o, &a_src, 200);
    assert!((ratio - 8f64.ln()).abs() < 1e-9, "no finds on a searched coast penalises A by 2^3: {ratio}");
    let mut unsearched = searched.clone();
    unsearched.ident.rel = vec![vec![0.0], vec![1.0]];
    let ratio = ln_l(&unsearched, &o, &b_src, 200) - ln_l(&unsearched, &o, &a_src, 200);
    assert!(ratio.abs() < 1e-9, "an unsearched coast carries no information: {ratio}");
}

#[test]
fn time_varying_identification_hand_value() {
    let r = Recovery { ident: Identification { edges_km: vec![-1e6, 1e6], breaks_days: vec![10.0], rel: vec![vec![0.0, 1.0]] }, delay: Delay::Uniform { max_days: 20.0 }, bandwidth_km: 5.0, window_end_days: 100.0 };
    let a = [Arrival { s_km: 0.0, t_days: 0.0 }];
    assert!((r.q_total(&a, 1) - 0.5).abs() < 1e-9);
    assert!((r.q(&obs(0.0, 12.0, 13.0), &a, 1).q - 0.05 * k0(5.0)).abs() < 1e-12);
    assert_eq!(r.q(&obs(0.0, 5.0, 6.0), &a, 1).q, 0.0);
    assert!((phi(0.0) - 0.5).abs() < 1e-7 && (phi(1.959_964) - 0.975).abs() < 1e-6);
}

#[test]
fn shared_environment_is_marginalised_outside_the_product() {
    let r = rec(vec![-1e6, 1e6], 5.0, Delay::Uniform { max_days: 10.0 }, 100.0);
    let env_a = vec![vec![Arrival { s_km: 0.0, t_days: 0.0 }]];
    let env_b = vec![vec![Arrival { s_km: 0.0, t_days: 0.0 }, Arrival { s_km: 100.0, t_days: 0.0 }]];
    let o = [obs(0.0, 1.0, 2.0), obs(0.0, 1.0, 2.0)];
    let (node, _) = node_ln_likelihood(&r, &o, &[env_a, env_b], 2);
    let Node::Value(l) = node else { panic!() };
    let k = k0(5.0);
    assert!((l - (0.006_25 * k * k).ln()).abs() < 1e-9, "(a^2 + b^2)/2");
    assert!((l - (0.075 * k).powi(2).ln()).abs() > 0.1, "not the product of per-object means");
}

#[test]
fn synthetic_recovery_coverage() {
    // Finds generated from a node drawn uniformly from the grid (an independent ensemble), scored
    // with the module's own layers; the 90% HPD set should contain the truth about 90% of the time.
    let grid = SourceGrid::rectangle(-37.5, 94.8, 7, 3, 10.0);
    let plane = super::provisional_analytic_ocean::LocalPlane { lat0: -37.25, lon0: 95.0 };
    let (xc, _) = plane.to_xy(-37.25, 92.0);
    let coast = Coast::through((xc, -5000.0), (xc, 5000.0), (xc + 1.0, 0.0));
    let tr = StubTransport { ocean: ocean(Current::Uniform { east: -0.2, north: 0.0 }, 100.0, Some(coast)), plane, step_s: 21_600.0, segment_km: 500.0, label: "test".into() };
    let class = ClassParams { name: "test".into(), a_stokes: [0.0, 0.0], c_wind: [0.0, 0.0] };
    let edges: Vec<f64> = (0..=40).map(|i| -2000.0 + 100.0 * i as f64).collect();
    let r = rec(edges, 10.0, Delay::Uniform { max_days: 10.0 }, 60.0);
    let (n, t0) = (400, 1_394_237_977.0);
    let t_end = t0 + 60.0 * 86_400.0;
    let nodes: Vec<[f64; 2]> = (0..21).map(|k| { let (la, lo) = grid.node(k); [lo, la] }).collect();
    let ens: Vec<Vec<Vec<Vec<Arrival>>>> = nodes.iter().enumerate().map(|(k, &ll)| vec![vec![run_ensemble(&tr, ll, t0, t_end, &class, n, 5, &mut Rng::derive(&[1, k as u64])).arrivals]]).collect();
    let trials = 60;
    let mut hits = 0;
    let (mut p_truth, mut p_sq) = (0.0, 0.0);
    let mut pick = Rng::new(99);
    for t in 0..trials {
        let truth = (pick.uniform() * 21.0) as usize;
        let o = synthetic_finds(&tr, &r, &class, nodes[truth], t0, t_end, 4, 9_000 + t as u64, &mut Rng::derive(&[777, t as u64])).unwrap();
        let ll: Vec<f64> = ens.iter().map(|e| match node_ln_likelihood(&r, &o, e, n).0 { Node::Value(v) => v, _ => f64::NEG_INFINITY }).collect();
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
    // Calibration: if the posterior is right on average, E[p(truth)] = E[sum_k p_k^2]. HPD
    // coverage on a discrete grid with near-ties can only overshoot 0.9, so this is the sharper test.
    let calib = p_truth / p_sq;
    println!("synthetic-recovery: 90% HPD coverage {cov} ({hits}/{trials}); mean p(truth) {:.3}, mean sum p^2 {:.3}, ratio {calib:.3}", p_truth / trials as f64, p_sq / trials as f64);
    assert!((0.75..=1.0).contains(&cov), "coverage {cov}");
    assert!((0.7..1.3).contains(&calib), "calibration ratio {calib}");
}

#[test]
fn evidence_table_and_dates() {
    let recs = parse(TABLE).unwrap();
    assert_eq!(recs.len(), 41);
    let s: Vec<_> = recs.iter().filter(|r| r.stringent).collect();
    assert_eq!(s.len(), 9);
    assert_eq!(s[0].object_id, "reunion-right-flaperon");
    assert_eq!(days_from_civil(1970, 1, 1), 0);
    assert_eq!(days_from_civil(2000, 3, 1), 11_017);
    // Reunion flaperon: 508 days after 8 March 2014 - Davey's 508 +/- 30 (p. 103).
    assert_eq!(days_from_civil(2015, 7, 29) - days_from_civil(2014, 3, 8), 508);
}

#[test]
fn stringent_intervals_are_days_after_release() {
    let v = stringent_intervals(1_394_236_800.0).unwrap(); // 2014-03-08 00:00 UTC
    assert_eq!(v.len(), 9);
    assert_eq!(v[0].0, "debris:reunion-right-flaperon");
    assert_eq!((v[0].1, v[0].2), (508.0, 509.0));
    assert!(v.iter().all(|x| x.2 > x.1));
}

#[test]
fn run_toml_constructs_and_scores_the_stub() {
    // Smoke check of the full stub path from this module's own run.toml (code path only; never
    // evidence). Particles reduced for test time; production scale is set by the pilot.
    let run: toml::Value = toml::from_str(include_str!("run.toml")).unwrap();
    let mut t = run["hypotheses"]["debris-drift"].clone();
    t.as_table_mut().unwrap().insert("particles_per_case".into(), toml::Value::Integer(100));
    let p: Params = t.try_into().unwrap();
    let b = build_stub(&p).unwrap();
    let mut counts = [0usize; 4];
    for n in &b.surface.nodes {
        counts[match n { Node::Value(_) => 0, Node::Land => 1, Node::Unresolved => 2, Node::NotComputed => 3 }] += 1;
    }
    println!("stub: active {} scored {} land {} unresolved {} outside {}; arrival fraction {:.3}; {:.3e} particle-steps/s (analytic field, 1 thread); ln L scale {:.1} NM; finds {}; min n_eff {:.1}",
        b.grid.n_active(), counts[0], counts[1], counts[2], counts[3], b.arrival_fraction, b.steps_per_second, b.ln_l_scale_nm, b.observations.len(),
        b.min_neff.iter().copied().filter(|x| x.is_finite()).fold(f64::INFINITY, f64::min));
    assert!(counts[0] > 0 && b.observations.len() == p.synthetic.as_ref().unwrap().finds);
}

#[test]
fn stub_transport_reports_fates_in_the_shared_conventions() {
    // [lon, lat], unix seconds, persistent response; a release on land is a model-error fate.
    let plane = super::provisional_analytic_ocean::LocalPlane { lat0: -37.0, lon0: 95.0 };
    let (xc, _) = plane.to_xy(-37.0, 94.0);
    let coast = Coast::through((xc, -5000.0), (xc, 5000.0), (xc + 1.0, 0.0));
    let tr = StubTransport { ocean: ocean(Current::Uniform { east: -0.5, north: 0.0 }, 0.0, Some(coast)), plane, step_s: 21_600.0, segment_km: 500.0, label: "test".into() };
    let r = ObjectResponse { a_stokes: 0.0, c_wind: 0.0, leeway_angle_deg: 0.0 };
    let t0 = 1_394_237_977.0;
    let ps = [Particle { release: [95.0, -37.0], release_time: t0, response: r }, Particle { release: [93.0, -37.0], release_time: t0, response: r }];
    let f = tr.integrate(&ps, 1, t0 + 30.0 * 86_400.0);
    let Fate::Beached { t, at, .. } = f[0] else { panic!("{:?}", f[0]) };
    let dist_km = (95.0 - 94.0) * 111.195 * (-37.0f64).to_radians().cos();
    assert!((t - t0 - dist_km * 1000.0 / 0.5).abs() < 1e-3, "{}", t - t0);
    assert!((at[0] - 94.0).abs() < 1e-9 && (at[1] + 37.0).abs() < 1e-9);
    assert_eq!(f[1], Fate::ReleasedOnLand);
}
