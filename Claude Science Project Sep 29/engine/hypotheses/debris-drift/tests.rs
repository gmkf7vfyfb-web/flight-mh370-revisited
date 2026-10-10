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
    Arrival { place: on0(s), segment: Some(seg), t_days: t, w: 1.0 }
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
    let r = rec(&[-500.0, 0.0, 500.0], vec![50.0], 100.0, Delay::Exponential { mean_days: 20.0 }, 300.0);
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
        let z = (o[0].place.s_km - x.place.s_km) / 100.0;
        let f = |t: f64| Delay::Exponential { mean_days: 20.0 }.cdf(t - x.t_days);
        if z.abs() > 6.0 || x.t_days >= 61.0 { return 0.0; }
        k0(100.0) * (-0.5 * z * z).exp() * nu[0 * 2 + 1] * (f(61.0) - f(60.0))
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
    // Keyed by object id, not row order, so the check cannot be satisfied by a reordering.
    let expect = [
        ("reunion-right-flaperon", "S1-reunion"),
        ("mossel-bay-engine-cowling-roy", "S4-south-africa-south-coast"),
        ("paindane-right-flap-fairing", "S3-southern-mozambique"),
        ("vilanculos-horizontal-stabilizer-panel", "S3-southern-mozambique"),
        ("chidenguele-right-fan-cowling", "S3-southern-mozambique"),
        ("mauritius-left-outboard-flap", "S2-mauritius-rodrigues"),
        ("rodrigues-door-closet-panel", "S2-mauritius-rodrigues"),
        ("antsiraka-cabin-interior-panel", "S5-ne-madagascar"),
        ("pemba-right-outboard-flap", "S6-pemba"),
    ];
    for (id, seg) in expect {
        let r = s.iter().find(|r| r.object_id == id).unwrap_or_else(|| panic!("{id} not in the stringent set"));
        let got = map.locate([r.longitude_deg, r.latitude_deg]).map(|k| map.segments[k].name.as_str()).unwrap_or("none");
        assert_eq!(got, seg, "{id}");
    }
    assert!(great_circle_km([55.649150, -20.916180], [39.868086, -5.056071]) > 2400.0);
}

fn analytic(current: [f64; 2], wind: Option<[f64; 2]>, coast_lon: f64) -> OceanSetup {
    let t = TransportParams::Analytic { current_mps: current, wind10_mps: wind, stokes_mps: None, coast_a: [coast_lon, -60.0], coast_b: [coast_lon, 0.0], land_left: true };
    OceanSetup::new(&t, Domain { lon_min: 15.0, lon_max: 120.0, lat_min: -60.0, lat_max: 0.0 }, 21_600.0, 2, true, false, true).unwrap()
}

#[test]
fn adapter_beaching_time_and_chainage_match_closed_form() {
    let s = analytic([-0.5, 0.0], None, 94.0);
    let p = [Particle::new([95.0, -37.0], T0, response(0.0, 0.0, 0.0, 0.0, 0.0))];
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
    let p = [Particle::new([95.0, -37.0], T0, response(0.0, 0.0, 0.0, -16.0, 0.10))];
    let (f, _) = s.run(&p, 1, Diffusion::None, T0 + 200.0 * 86_400.0).unwrap();
    let Fate::Beached { t, at, .. } = f[0] else { panic!("{:?}", f[0]) };
    let days = (t - T0) / 86_400.0;
    let south_km = (-37.0 - at[1]) * 111.195;
    assert!((south_km / days - 8.64 * 16f64.to_radians().sin()).abs() < 0.05, "{} km/day south", south_km / days);
    let bad = [Particle::new([95.0, -37.0], T0, response(1.0, 0.0, 0.0, -16.0, 0.10))];
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
fn node_csv_is_rectangular_and_hits_bound_n_eff() {
    // The sizing diagnostics (hits per find, split halves and effective sizes at the extra
    // bandwidths) are appended to every row; a find with zero hits has zero effective size, and
    // the Kish size never exceeds the hit count.
    let run: toml::Value = toml::from_str(include_str!("run.toml")).unwrap();
    let dir = std::env::temp_dir().join(format!("drift-csv-{}", std::process::id()));
    let p = small(run["hypotheses"]["debris-drift"].clone(), &[("particles_per_class", toml::Value::Integer(60)), ("node_subset", toml::Value::Array((0..6).map(|i| toml::Value::Integer(4000 + 37 * i)).collect())), ("output_dir", toml::Value::String(dir.to_string_lossy().into()))]);
    build(&p).unwrap();
    let text = std::fs::read_to_string(dir.join("nodes.csv")).unwrap();
    let mut lines = text.lines();
    let head: Vec<&str> = lines.next().unwrap().split(',').collect();
    let col = |name: &str| head.iter().position(|h| *h == name);
    let mut rows = 0;
    for l in lines {
        let v: Vec<&str> = l.split(',').collect();
        assert_eq!(v.len(), head.len(), "row width");
        for (k, h) in head.iter().enumerate() {
            if let Some(id) = h.strip_prefix("hits_") {
                let hits: f64 = v[k].parse().unwrap();
                let ne: f64 = v[col(&format!("n_eff_{id}")).unwrap()].parse().unwrap();
                assert!(ne <= hits + 1e-9, "{id}: n_eff {ne} > hits {hits}");
                if hits == 0.0 {
                    assert_eq!(ne, 0.0);
                }
            }
        }
        rows += 1;
    }
    assert!(rows > 0);
    assert!(head.iter().any(|h| h.starts_with("ln_l_h") && h.ends_with("_half_a")));
    std::fs::remove_dir_all(&dir).ok();
}

#[test]
fn splitting_is_unbiased_and_resolves_a_rare_target() {
    // Uniform westward current onto a straight coast at 92 E with K = 100 m2/s: arrivals spread
    // along the coast by diffusion alone. The rare event is beaching inside a 0.1-degree window
    // 40 km north of the release latitude. Splitting on entry to a 30 km disc upstream of the
    // window must give the same weighted rate as brute force (within Monte Carlo error) and more
    // trajectories in the window per released particle.
    let setup = analytic([-0.2, 0.0], None, 92.0);
    let loc = super::Locator { map: None, edges: vec![] };
    let (lat0, lon0) = (-37.5, 94.8);
    let lat_w = lat0 + 40.0 / 111.195;
    let t_end = T0 + 40.0 * 86_400.0;
    let diff = Diffusion::Diffusivity { k_m2_s: 100.0 };
    let rate = |n: usize, seed: u64, split: Option<&super::SplittingParams>| {
        let resp: Vec<_> = (0..n).map(|_| response(0.0, 0.0, 0.0, 0.0, 0.0)).collect();
        let (e, _) = super::run_ensemble(&setup, &loc, [lon0, lat0], T0, t_end, &resp, seed, diff, split).unwrap();
        // Per released particle (children summed into their parent): the estimate is the mean of
        // these, and its standard error is their standard deviation over sqrt(n).
        let mut per = vec![0.0; n];
        let mut k = 0;
        for (i, a) in &e.arrivals {
            if (a.place.lonlat[1] - lat_w).abs() < 0.05 {
                per[*i] += a.w;
                k += 1;
            }
        }
        let m = per.iter().sum::<f64>() / n as f64;
        let se = (per.iter().map(|x| (x - m).powi(2)).sum::<f64>() / (n * (n - 1)) as f64).sqrt();
        let total: f64 = e.arrivals.iter().map(|(_, a)| a.w).sum::<f64>() + e.left_domain + e.model_error;
        (m, se, k, total / n as f64, e.split)
    };
    let sp = super::SplittingParams { targets: vec![super::SplitTarget { name: "w".into(), lon_deg: 92.6, lat_deg: lat_w, radius_km: 30.0, factor: None }], factor: 20, snapshot_hours: 24.0, classes: vec![] };
    let (p_b, se_b, k_b, tot_b, _) = rate(40_000, 11, None);
    let (p_s, se_s, k_s, tot_s, n_split) = rate(4_000, 12, Some(&sp));
    println!("splitting: brute {p_b:.3e} +- {se_b:.1e} ({k_b} hits), split {p_s:.3e} +- {se_s:.1e} ({k_s} hits, {n_split} parents split)");
    assert!(k_b >= 10, "brute force too few hits to compare: {k_b}");
    assert!((p_b - p_s).abs() < 4.0 * (se_b * se_b + se_s * se_s).sqrt(), "brute {p_b} vs split {p_s}");
    assert!((tot_b - 1.0).abs() < 1e-9 && (tot_s - 1.0).abs() < 1e-9, "weights must conserve mass: {tot_b} {tot_s}");
    assert!(k_s as f64 / 4_000.0 > 3.0 * k_b as f64 / 40_000.0, "splitting should raise hits per released particle");
}

#[test]
fn ocean_error_config_changes_the_ensemble_and_is_seeded() {
    // `[ocean_error]` parses, and the error field reaches the integrator: the same release and
    // seed give different arrivals with it on, and identical arrivals twice (one realisation per
    // seed).
    let run: toml::Value = toml::from_str(include_str!("run.toml")).unwrap();
    let oe: toml::Value = toml::from_str("sigma_m_s = 0.1\nlength_scale_km = 100.0\ntime_scale_days = 8.0").unwrap();
    let p = small(run["hypotheses"]["debris-drift"].clone(), &[("ocean_error", oe)]);
    let o = p.ocean_error.clone().unwrap();
    let mut setup = analytic([-0.2, 0.0], None, 92.0);
    let loc = super::Locator { map: None, edges: vec![] };
    let resp: Vec<_> = (0..300).map(|_| response(0.0, 0.0, 0.0, 0.0, 0.0)).collect();
    let t_end = T0 + 40.0 * 86_400.0;
    let diff = Diffusion::Diffusivity { k_m2_s: 100.0 };
    let lats = |s: &OceanSetup| super::run_ensemble(s, &loc, [94.8, -37.5], T0, t_end, &resp, 7, diff, None).unwrap().0.arrivals.iter().map(|x| x.1.place.lonlat[1]).collect::<Vec<f64>>();
    let off = lats(&setup);
    setup.ocean_error = ocean::OceanErrorModel::eddying(o.sigma_m_s, o.length_scale_km * 1000.0, o.time_scale_days * 86_400.0, o.modes);
    let (on1, on2) = (lats(&setup), lats(&setup));
    assert_eq!(on1, on2, "one realisation per seed");
    assert_ne!(off, on1, "the error field must change the ensemble");
}

#[test]
fn island_disc_crossing_is_exact() {
    // A track due east 2 km south of a 5.9 km disc's centre enters at x = -sqrt(r^2 - y^2); a track
    // 7 km south misses; a track starting inside is not a crossing.
    use ocean::Coastline;
    let d = super::transport::IslandDisc { name: "rodrigues".into(), lon_deg: 63.428, lat_deg: -19.728, radius_km: 5.9 };
    let c = super::transport::IslandDiscs { discs: vec![d.clone()] };
    let k = 6_371_008.8 * std::f64::consts::PI / 180.0;
    let dy = 2_000.0 / k;
    let h = c.first_crossing([63.0, d.lat_deg - dy], [63.6, d.lat_deg - dy]).expect("hit");
    let x = -((5_900.0f64).powi(2) - 2_000.0f64.powi(2)).sqrt();
    let lon_expect = d.lon_deg + x / (k * d.lat_deg.to_radians().cos());
    assert!((h.point[0] - lon_expect).abs() < 1e-9, "{} vs {}", h.point[0], lon_expect);
    assert!((h.point[1] - (d.lat_deg - dy)).abs() < 1e-12);
    assert_eq!(h.line, 1000);
    let dy7 = 7_000.0 / k;
    assert!(c.first_crossing([63.0, d.lat_deg - dy7], [63.6, d.lat_deg - dy7]).is_none());
    assert!(c.first_crossing([d.lon_deg, d.lat_deg], [63.6, d.lat_deg]).is_none());
    assert!(c.is_land([d.lon_deg + 0.05, d.lat_deg]) && !c.is_land([d.lon_deg + 0.06, d.lat_deg]));
}

#[test]
fn class_angles_reach_their_own_terms() {
    // Ruling D-f: `wind_angle_deg` rotates c_wind, `leeway_angle_deg` the constant-speed term;
    // a class that omits `wind_angle_deg` is downwind.
    let c: super::ClassParams = toml::from_str("name = \"x\"\na_stokes = { dist = \"fixed\", value = 0.0 }\nc_wind = { dist = \"fixed\", value = 0.012 }\nwind_angle_deg = { dist = \"fixed\", value = 20.0 }\nleeway_angle_deg = { dist = \"fixed\", value = -16.0 }\nleeway_speed_mps = { dist = \"fixed\", value = 0.1 }").unwrap();
    let r = super::draw_response(&c, &mut Rng::new(1));
    assert_eq!((r.c_wind, r.wind_angle_deg, r.leeway_angle_deg, r.leeway_speed_mps), (0.012, 20.0, -16.0, 0.1));
    let d: super::ClassParams = toml::from_str("name = \"y\"\na_stokes = { dist = \"fixed\", value = 0.0 }\nc_wind = { dist = \"fixed\", value = 0.012 }\nleeway_angle_deg = { dist = \"fixed\", value = -16.0 }\nleeway_speed_mps = { dist = \"fixed\", value = 0.1 }").unwrap();
    assert_eq!(super::draw_response(&d, &mut Rng::new(1)).wind_angle_deg, 0.0);
}

#[test]
fn a_zero_environment_enters_the_mean_but_all_zero_is_unresolved() {
    use super::recovery::Coefficients;
    let lv = LevelDraws::new(1, &[0.0], 0.0, 1, 1);
    let k = |a: f64| Some(Coefficients { a: vec![vec![a]], big_a: vec![0.5], n_eff: vec![1.0], hits: vec![(a > 0.0) as usize] });
    let by_class = vec![vec![0usize]];
    let (n, zf) = super::node_ln_likelihood_zeros(&[vec![k(0.2)], vec![k(0.0)]], &by_class, &lv);
    assert_eq!(n, Node::Value((0.4f64 / 2.0).ln()));
    assert_eq!(zf, 0.5);
    assert_eq!(super::node_ln_likelihood(&[vec![k(0.0)]], &by_class, &lv), Node::Unresolved);
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
    let resp: Vec<_> = (0..n).map(|_| response(0.0, 0.0, 0.0, 0.0, 0.0)).collect();
    let nodes: Vec<[f64; 2]> = (0..21).map(|k| { let (la, lo) = grid.node(k); [lo, la] }).collect();
    let loc = super::Locator { map: None, edges: r.edges.clone() };
    let t_end = T0 + 60.0 * 86_400.0;
    let ens: Vec<Vec<Arrival>> = nodes.iter().map(|&ll| super::run_ensemble(&setup, &loc, ll, T0, t_end, &resp, 5, Diffusion::Diffusivity { k_m2_s: 100.0 }, None).unwrap().0.arrivals.into_iter().map(|x| x.1).collect()).collect();
    let trials = 60;
    let (mut hits, mut p_truth, mut p_sq) = (0, 0.0, 0.0);
    for t in 0..trials {
        let truth = (rng.uniform() * 21.0) as usize;
        let gen = super::run_ensemble(&setup, &loc, nodes[truth], T0, t_end, &resp[..200], 9_000 + t as u64, Diffusion::Diffusivity { k_m2_s: 100.0 }, None).unwrap().0;
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

#[test]
fn candidate_selection_extension_flag() {
    use super::select_candidates;
    let active = [true, false, true, true, false, true];
    // Default striding over active nodes is unchanged.
    assert_eq!(select_candidates(&active, &[], 2, 0, false), vec![0, 3]);
    assert_eq!(select_candidates(&active, &[], 2, 1, false), vec![2, 5]);
    // A subset keeps only active nodes by default; out-of-range indices are dropped.
    assert_eq!(select_candidates(&active, &[1, 2, 4, 9], 1, 0, false), vec![2]);
    // With the extension flag, any in-grid node may be named.
    assert_eq!(select_candidates(&active, &[1, 2, 4, 9], 1, 0, true), vec![1, 2, 4]);
}

#[test]
fn product_windage_offset() {
    use super::{draw_response, draw_response_offset};
    let pilot: toml::Value = toml::from_str(include_str!("production-globcurrent.toml")).unwrap();
    let p: Params = pilot["hypotheses"]["debris-drift"].clone().try_into().unwrap();
    for c in &p.classes {
        let (mut r0, mut r1, mut r2) = (Rng::new(7), Rng::new(7), Rng::new(7));
        for _ in 0..200 {
            let a = draw_response(c, &mut r0);
            let b = draw_response_offset(c, &mut r1, 0.0);
            let d = draw_response_offset(c, &mut r2, -0.006);
            // Offset 0 is identical; a negative offset shifts c_wind, floors at 0, and leaves the other terms.
            assert_eq!(format!("{a:?}"), format!("{b:?}"));
            assert!((d.c_wind - (a.c_wind - 0.006).max(0.0)).abs() < 1e-15);
            assert_eq!((d.a_stokes, d.wind_angle_deg, d.leeway_angle_deg, d.leeway_speed_mps), (a.a_stokes, a.wind_angle_deg, a.leeway_angle_deg, a.leeway_speed_mps));
        }
    }
}

#[test]
fn product_windage_offset_range() {
    use super::class_responses;
    let run: toml::Value = toml::from_str(include_str!("production-globcurrent.toml")).unwrap();
    let mut p: Params = run["hypotheses"]["debris-drift"].clone().try_into().unwrap();
    p.particles_per_class = 2000;
    let base = class_responses(&p, 1);
    p.c_wind_product_offset_range = Some([-0.0075, -0.0060]);
    let drawn = class_responses(&p, 1);
    let mut offs = Vec::new();
    for (a, b) in base.iter().zip(&drawn) {
        // Only c_wind moves; every other response term is the same draw.
        assert_eq!((a.a_stokes, a.wind_angle_deg, a.leeway_angle_deg, a.leeway_speed_mps), (b.a_stokes, b.wind_angle_deg, b.leeway_angle_deg, b.leeway_speed_mps));
        if b.c_wind > 0.0 {
            offs.push(b.c_wind - a.c_wind);
        }
    }
    assert!(offs.iter().all(|d| *d >= -0.0075 - 1e-12 && *d <= -0.0060 + 1e-12));
    let mean = offs.iter().sum::<f64>() / offs.len() as f64;
    assert!((mean + 0.00675).abs() < 0.0001, "mean offset {mean}");
    // Both forms together are refused.
    p.c_wind_product_offset = -0.006;
    assert!(super::validate(&p).is_err());
}
