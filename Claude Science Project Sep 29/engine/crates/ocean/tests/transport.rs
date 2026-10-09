//! Tests for the shared ocean transport API. The first two are ported from `transport_core.test.mjs`
//! in the withdrawn Pleiades share (constant-current analytic displacement; random-walk RMS),
//! the second strengthened from a check of the scaling formula to a check of the integrator.

use mh370_ocean::analytic::{SolidBodyGyre, Uniform, UniformColumn};
use mh370_ocean::field::{Component, FieldGap, FieldMeta, GridField, VectorField};
use mh370_ocean::integrate::{CompositionError, Track};
use mh370_ocean::products::{catalogue, Contents, Inclusion, TimeAxis};
use mh370_ocean::profile::{BelowModelBottom, BottomRelation, DepthGap, DepthStatus, ProfileSource, VerticalVelocity};
use mh370_ocean::*;

const T0: f64 = 1_394_236_800.0; // 2014-03-08T00:00:00Z
const DAY: f64 = SECONDS_PER_DAY;

fn open_domain() -> Domain {
    Domain { lon_min: 15.0, lon_max: 120.0, lat_min: -50.0, lat_max: 0.0 }
}

fn spec<'a>(forcing: Forcing<'a>, coast: &'a dyn Coastline, step_s: f64, output_times: Vec<f64>) -> RunSpec<'a> {
    RunSpec {
        forcing,
        coast,
        domain: open_domain(),
        step_s,
        output_times,
        diffusion: Diffusion::None,
        ocean_error: OceanErrorModel::none(),
        refloat: Refloat::Off,
        seed: 37_003_801,
        leeway_absorbs_stokes: false,
        accept_partial_stokes_overlap: false,
        explicit_residual: false,
        threads: 2,
    }
}

fn current_only(c: &dyn VectorField) -> Forcing<'_> {
    Forcing { current: c, stokes: None, wind10: None }
}

fn final_position(track: &Track) -> LonLat {
    match track.snapshots.last().unwrap() {
        Snapshot::Afloat(p) => *p,
        s => panic!("not afloat: {s:?}"),
    }
}

fn particle(lon: f64, lat: f64, a_stokes: f64, c_wind: f64) -> Particle {
    Particle::new([lon, lat], T0, ObjectResponse::new(a_stokes, c_wind))
}

#[test]
fn constant_current_matches_analytic_displacement() {
    // Ported: 0.1 m/s east for one day at 35 S, 3 h steps, displacement 8.64 km within 20 m.
    let c = Uniform::current(0.1, 0.0);
    let out = integrate(&spec(current_only(&c), &NoCoast, 3.0 * 3600.0, vec![T0 + DAY]), &[particle(92.0, -35.0, 0.0, 0.0)]).unwrap();
    let d = distance_m([92.0, -35.0], final_position(&out.tracks[0]));
    assert!((d - 8_640.0).abs() < 20.0, "displacement {d} m");

    // Ported: current and Stokes are distinct terms; a_stokes scales only the Stokes term.
    let c = Uniform::current(0.1, -0.02);
    let s = Uniform::new(Component::StokesDrift, 0.05, 0.02);
    let f = Forcing { current: &c, stokes: Some(&s), wind10: None };
    let parts = [particle(92.0, -35.0, 1.0, 0.0), particle(92.0, -35.0, 0.5, 0.0)];
    let out = integrate(&spec(f, &NoCoast, 3.0 * 3600.0, vec![T0 + DAY]), &parts).unwrap();
    for (track, speed) in out.tracks.iter().zip([0.15, (0.125f64.powi(2) + 0.01f64.powi(2)).sqrt()]) {
        let d = distance_m([92.0, -35.0], final_position(track));
        assert!((d - speed * DAY).abs() < 20.0, "displacement {d} m, expected {}", speed * DAY);
    }
}

#[test]
fn random_walk_reproduces_declared_daily_rms() {
    // 5 NM/day random walk in still water, 20 000 particles: the 2-D RMS after one day is 5 NM
    // whatever the step. Sampling SE of the RMS is 0.35%; tolerance 1.5%.
    let c = Uniform::current(0.0, 0.0);
    let parts: Vec<Particle> = (0..20_000).map(|_| particle(100.0, -30.0, 0.0, 0.0)).collect();
    for step in [3600.0, 6.0 * 3600.0, DAY] {
        let mut sp = spec(current_only(&c), &NoCoast, step, vec![T0 + DAY]);
        sp.diffusion = Diffusion::random_walk_nm_per_day(5.0);
        let out = integrate(&sp, &parts).unwrap();
        let ms: f64 = out.tracks.iter().map(|t| distance_m([100.0, -30.0], final_position(t)).powi(2)).sum::<f64>() / parts.len() as f64;
        let rms_nm = ms.sqrt() / METRES_PER_NM;
        assert!((rms_nm - 5.0).abs() < 0.075, "step {step}: daily RMS {rms_nm} NM");
    }
    // The archive's 100 m^2/s, for the record: 3.17 NM after one day.
    let k = Diffusion::Diffusivity { k_m2_s: 100.0 };
    assert!(((4.0 * 100.0 * DAY).sqrt() / METRES_PER_NM - 3.17).abs() < 0.01);
    assert!((Diffusion::random_walk_nm_per_day(5.0).long_time_diffusivity_m2_s() - 248.1).abs() < 0.1);
    assert_eq!(k.long_time_diffusivity_m2_s(), 100.0);
}

#[test]
fn random_flight_matches_exact_discrete_dispersion() {
    // OU velocity held over each step: Var(X) = dt^2 sigma^2 [N + 2 sum_{k<N} (N-k) rho^k] per
    // component, exactly. 4 000 particles x 2 components: SE of the variance 1.6%; tolerance 6%.
    let (sigma, tl, dt, days) = (0.1, 2.0 * DAY, 3.0 * 3600.0, 60.0);
    let c = Uniform::current(0.0, 0.0);
    let mut sp = spec(current_only(&c), &NoCoast, dt, vec![T0 + days * DAY]);
    sp.diffusion = Diffusion::RandomFlight { sigma_m_s: sigma, lagrangian_time_s: tl };
    let parts: Vec<Particle> = (0..4_000).map(|_| particle(80.0, -30.0, 0.0, 0.0)).collect();
    let out = integrate(&sp, &parts).unwrap();
    let n = (days * DAY / dt).round() as i64;
    let rho: f64 = (-dt / tl).exp();
    let sum: f64 = (1..n).map(|k| (n - k) as f64 * rho.powi(k as i32)).sum();
    let expected = dt * dt * sigma * sigma * (n as f64 + 2.0 * sum);
    let (mut se, mut sn) = (0.0, 0.0);
    for t in &out.tracks {
        let p = final_position(t);
        se += ((p[0] - 80.0).to_radians() * EARTH_RADIUS_M * (30f64).to_radians().cos()).powi(2);
        sn += ((p[1] + 30.0).to_radians() * EARTH_RADIUS_M).powi(2);
    }
    let var = (se + sn) / (2.0 * parts.len() as f64);
    assert!((var / expected - 1.0).abs() < 0.06, "variance {var} vs exact {expected}");
}

#[test]
fn solid_body_gyre_closes_its_orbit() {
    // One full period of a 10-day gyre: back at the start, distance to the centre conserved.
    let omega = std::f64::consts::TAU / (10.0 * DAY);
    let gyre = SolidBodyGyre::new([95.0, -32.0], omega);
    let start = [96.0, -32.0];
    let times: Vec<f64> = (1..=10).map(|d| T0 + d as f64 * DAY).collect();
    let out = integrate(&spec(current_only(&gyre), &NoCoast, 3600.0, times), &[particle(start[0], start[1], 0.0, 0.0)]).unwrap();
    let r0 = distance_m([95.0, -32.0], start);
    for s in &out.tracks[0].snapshots {
        let Snapshot::Afloat(p) = s else { panic!() };
        assert!((distance_m([95.0, -32.0], *p) - r0).abs() < 0.001 * r0);
    }
    assert!(distance_m(start, final_position(&out.tracks[0])) < 0.002 * r0);
}

fn grid_meta() -> FieldMeta {
    FieldMeta {
        product: "test-grid".into(),
        component: Component::Current,
        contents: Contents::analytic(),
        time_axis: TimeAxis::Mean { interval_s: DAY, stamp: "centre".into() },
        description: "3x3 test grid".into(),
    }
}

#[test]
fn land_is_renormalised_never_filled_with_zero() {
    // 2x2 nodes x 2 times, one land corner. A zero fill would give 0.75 * 0.2 = 0.15 at the
    // cell centre; renormalisation gives 0.2.
    let nan = f32::NAN;
    let slice = [0.2, 0.1, 0.2, 0.1, nan, nan, 0.2, 0.1];
    let data: Vec<f32> = slice.iter().chain(slice.iter()).copied().collect();
    let g = GridField::new(grid_meta(), vec![100.0, 101.0], vec![-31.0, -30.0], vec![T0, T0 + DAY], data.clone(), None).unwrap();
    let v = g.sample(T0 + 0.5 * DAY, [100.5, -30.5]).unwrap();
    assert!((v[0] - 0.2).abs() < 1e-7 && (v[1] - 0.1).abs() < 1e-7, "{v:?}");
    // On the land node itself: still the neighbours' value along the edge, not zero.
    let v = g.sample(T0, [100.2, -30.0]).unwrap();
    assert!((v[0] - 0.2).abs() < 1e-7);
    // All contributing nodes land: flagged, not zero.
    let all_land = vec![nan; 16];
    let g2 = GridField::new(grid_meta(), vec![100.0, 101.0], vec![-31.0, -30.0], vec![T0, T0 + DAY], all_land, None).unwrap();
    assert_eq!(g2.sample(T0, [100.5, -30.5]), Err(FieldGap::Land));
    // With a sea mask, NaN at a sea node is corrupt data, not land.
    let sea = vec![true; 4];
    let g3 = GridField::new(grid_meta(), vec![100.0, 101.0], vec![-31.0, -30.0], vec![T0, T0 + DAY], data, Some(sea)).unwrap();
    assert_eq!(g3.sample(T0, [100.5, -30.5]), Err(FieldGap::NonFinite));
    // Outside the axes: flagged, never clamped.
    assert_eq!(g.sample(T0 + 2.0 * DAY, [100.5, -30.5]), Err(FieldGap::OutsideTime));
    assert_eq!(g.sample(T0, [102.0, -30.5]), Err(FieldGap::OutsideDomain));
}

#[test]
fn integrator_flags_field_gaps_and_domain_exit() {
    // 4 lon nodes x 2 lat x 2 times; the two eastern columns are land in the product mask, so the
    // cell 102-103 E has no sea node at all. Between 101 and 102 E land is renormalised away.
    let nan = f32::NAN;
    let mut d = Vec::new();
    for _ in 0..4 {
        d.extend([0.5f32, 0.0, 0.5, 0.0, nan, nan, nan, nan]);
    }
    let g = GridField::new(grid_meta(), vec![100.0, 101.0, 102.0, 103.0], vec![-31.0, -30.0], vec![T0, T0 + 10.0 * DAY], d, None).unwrap();
    let out = integrate(&spec(current_only(&g), &NoCoast, 3600.0, vec![T0 + 9.0 * DAY]), &[particle(100.2, -30.5, 0.0, 0.0)]).unwrap();
    let tr = &out.tracks[0];
    assert_eq!(tr.fate, Fate::FieldGap);
    assert!(matches!(tr.events[0], Event::FieldGap { gap: FieldGap::Land, component: Component::Current, .. }));
    assert_eq!(tr.snapshots, vec![Snapshot::Ended]);
    // Running past the field's time axis is flagged, not clamped.
    let still = GridField::new(grid_meta(), vec![100.0, 101.0], vec![-31.0, -30.0], vec![T0, T0 + DAY], vec![0.0f32; 16], None).unwrap();
    let out = integrate(&spec(current_only(&still), &NoCoast, 3600.0, vec![T0 + 2.0 * DAY]), &[particle(100.5, -30.5, 0.0, 0.0)]).unwrap();
    let tr = &out.tracks[0];
    assert!(matches!(tr.events[0], Event::FieldGap { gap: FieldGap::OutsideTime, .. }), "{:?}", tr.events);
    // Leaving the domain.
    let c = Uniform::current(0.0, -1.0);
    let out = integrate(&spec(current_only(&c), &NoCoast, 3600.0, vec![T0 + DAY]), &[particle(100.0, -49.9, 0.0, 0.0)]).unwrap();
    assert_eq!(out.tracks[0].fate, Fate::LeftDomain);
}

#[test]
fn beaching_reports_segment_and_time() {
    // Meridian coast at 100 E from 40 S to 30 S, ten 1-degree segments numbered 500..509, land to
    // the east. A 0.5 m/s eastward current carries particles onto it.
    let coast = StraightCoast { a: [100.0, -40.0], b: [100.0, -30.0], segments: 10, first_id: 500, land_left: false, line: 7 };
    assert!(coast.is_land([100.1, -35.0]) && !coast.is_land([99.9, -35.0]));
    let c = Uniform::current(0.5, 0.0);
    let times = vec![T0 + DAY, T0 + 3.0 * DAY];
    let parts = [particle(99.9, -34.55, 0.0, 0.0), particle(99.6, -38.05, 0.0, 0.0), particle(99.2, -25.0, 0.0, 0.0)];
    let out = integrate(&spec(current_only(&c), &coast, 6.0 * 3600.0, times), &parts).unwrap();
    for (tr, (lon, lat, seg)) in out.tracks.iter().zip([(99.9, -34.55, 505), (99.6, -38.05, 501), (99.2, -25.0, 509)]) {
        assert_eq!(tr.fate, Fate::Beached);
        let Event::Beached { t, at, segment, line, chainage_m } = tr.events[0] else { panic!("{:?}", tr.events) };
        assert_eq!(segment, seg);
        assert_eq!(line, 7);
        // Chainage along the meridian from 40 S: R * (lat + 40 deg), continuous across segments.
        let expected_chainage = EARTH_RADIUS_M * (lat + 40.0f64).to_radians();
        assert!((chainage_m - expected_chainage).abs() < 1e-6 * expected_chainage, "{chainage_m} vs {expected_chainage}");
        let edges = coast.segments();
        let e = edges.iter().find(|e| e.segment == seg).unwrap();
        assert!(chainage_m >= e.start_m && chainage_m < e.end_m);
        let expected = distance_m([lon, lat], [100.0, lat]) / 0.5;
        assert!(((t - T0) - expected).abs() < 60.0, "beach time {} vs {expected}", t - T0);
        assert!((at[0] - 100.0).abs() < 1e-9 && (at[1] - lat).abs() < 1e-9);
        for (s, &tout) in tr.snapshots.iter().zip(&out.output_times) {
            if tout >= t {
                assert_eq!(*s, Snapshot::Beached { at, segment: seg, line, chainage_m });
            } else {
                assert!(matches!(s, Snapshot::Afloat(_)));
            }
        }
    }
    // Released on land: flagged.
    let out = integrate(&spec(current_only(&c), &coast, 3600.0, vec![T0 + DAY]), &[particle(100.5, -35.0, 0.0, 0.0)]).unwrap();
    assert_eq!(out.tracks[0].fate, Fate::ReleasedOnLand);
    // Refloat hook: with a very high rate the particle refloats and beaches again.
    let mut sp = spec(current_only(&c), &coast, 3600.0, vec![T0 + DAY]);
    sp.refloat = Refloat::RatePerDay(1e4);
    let out = integrate(&sp, &[particle(99.9, -34.55, 0.0, 0.0)]).unwrap();
    let ev = &out.tracks[0].events;
    assert!(ev.iter().filter(|e| matches!(e, Event::Refloated { .. })).count() >= 2, "{ev:?}");
}

#[test]
fn output_times_and_late_release() {
    // Pleiades' use: one call, several output times; a particle released after the first
    // output time is NotReleased there.
    let c = Uniform::current(0.1, 0.0);
    let times = vec![T0 + DAY, T0 + 3.0 * DAY, T0 + 5.0 * DAY];
    let mut late = particle(92.0, -35.0, 0.0, 0.0);
    late.release_time = T0 + 2.0 * DAY;
    let out = integrate(&spec(current_only(&c), &NoCoast, 6.0 * 3600.0, times), &[particle(92.0, -35.0, 0.0, 0.0), late]).unwrap();
    let d: Vec<f64> = out.tracks[0].snapshots.iter().map(|s| match s { Snapshot::Afloat(p) => distance_m([92.0, -35.0], *p), _ => f64::NAN }).collect();
    for (di, days) in d.iter().zip([1.0, 3.0, 5.0]) {
        assert!((di - 0.1 * days * DAY).abs() < 20.0 * days);
    }
    assert_eq!(out.tracks[1].snapshots[0], Snapshot::NotReleased);
    let Snapshot::Afloat(p) = out.tracks[1].snapshots[1] else { panic!() };
    assert!((distance_m([92.0, -35.0], p) - 0.1 * DAY).abs() < 20.0);
}

#[test]
fn ocean_error_is_coherent_across_particles_within_a_run() {
    let c = Uniform::current(0.05, 0.0);
    let parts = [particle(95.0, -33.0, 0.0, 0.0), particle(95.0, -33.0, 0.0, 0.0), particle(95.1, -33.0, 0.0, 0.0)];
    let times = vec![T0 + 10.0 * DAY];
    let run = |error: OceanErrorModel, seed: u64| {
        let mut sp = spec(current_only(&c), &NoCoast, 6.0 * 3600.0, times.clone());
        sp.ocean_error = error;
        sp.seed = seed;
        let out = integrate(&sp, &parts).unwrap();
        out.tracks.iter().map(final_position).collect::<Vec<_>>()
    };
    let eddy = OceanErrorModel::eddying(0.1, 100_000.0, 20.0 * DAY, 64);
    let a = run(eddy, 1);
    let none = run(OceanErrorModel::none(), 1);
    // Same release, same run: identical (one ocean), and moved by the error.
    assert_eq!(a[0], a[1]);
    assert!(distance_m(a[0], none[0]) > 1_000.0);
    // A particle 9 km away sees nearly the same error displacement (L = 100 km).
    let shift = |x: LonLat, y: LonLat| [x[0] - y[0], x[1] - y[1]];
    let (s0, s2) = (shift(a[0], none[0]), shift(a[2], none[2]));
    let mag = (s0[0].powi(2) + s0[1].powi(2)).sqrt();
    assert!(((s0[0] - s2[0]).powi(2) + (s0[1] - s2[1]).powi(2)).sqrt() < 0.3 * mag);
    // A different run seed draws a different ocean.
    let b = run(eddy, 2);
    assert!(distance_m(a[0], b[0]) > 100.0);
    // Ensemble variance of each component at a point is sigma^2 (2000 realisations; SE 3.2%).
    for model in [eddy, OceanErrorModel::uniform_offset(0.1)] {
        let vs: Vec<[f64; 2]> = (0..2000).map(|s| model.realise(s).velocity(T0, [95.0, -33.0], 0.0)).collect();
        for k in 0..2 {
            let var = vs.iter().map(|v| v[k] * v[k]).sum::<f64>() / vs.len() as f64;
            assert!((var / 0.01 - 1.0).abs() < 0.13, "component {k} variance {var}");
        }
    }
}

#[test]
fn composition_refuses_double_counted_stokes() {
    let stokes_in_current = Contents { stokes: Inclusion::Included, ..Contents::analytic() };
    let c = Uniform::current(0.1, 0.0).with_contents(stokes_in_current);
    let s = Uniform::new(Component::StokesDrift, 0.05, 0.0);
    let f = Forcing { current: &c, stokes: Some(&s), wind10: None };
    let r = integrate(&spec(f, &NoCoast, 3600.0, vec![T0 + DAY]), &[particle(92.0, -35.0, 1.0, 0.0)]);
    assert!(matches!(r, Err(CompositionError::DoubleCount(_))));
    // a_stokes = 0 for every particle: nothing is double counted, so it runs.
    assert!(integrate(&spec(f, &NoCoast, 3600.0, vec![T0 + DAY]), &[particle(92.0, -35.0, 0.0, 0.0)]).is_ok());
    // A leeway declared to absorb Stokes refuses a separate Stokes term.
    let c2 = Uniform::current(0.1, 0.0);
    let mut sp = spec(Forcing { current: &c2, stokes: Some(&s), wind10: None }, &NoCoast, 3600.0, vec![T0 + DAY]);
    sp.leeway_absorbs_stokes = true;
    assert!(matches!(integrate(&sp, &[particle(92.0, -35.0, 1.0, 0.0)]), Err(CompositionError::DoubleCount(_))));
    // Missing component and wrong component.
    let r = integrate(&spec(current_only(&c2), &NoCoast, 3600.0, vec![T0 + DAY]), &[particle(92.0, -35.0, 0.0, 0.03)]);
    assert_eq!(r.err(), Some(CompositionError::MissingComponent(Component::Wind10m)));
    // Every catalogue product declares its Stokes content.
    for p in catalogue() {
        assert_ne!(p.contents.stokes, Inclusion::Unknown, "{}", p.id);
    }
}

#[test]
fn leeway_rotates_clockwise_from_downwind() {
    let c = Uniform::current(0.0, 0.0);
    let w = Uniform::new(Component::Wind10m, 0.0, 10.0);
    let f = Forcing { current: &c, stokes: None, wind10: Some(&w) };
    let mut p = particle(92.0, -35.0, 0.0, 0.02);
    p.response.leeway_angle_deg = 90.0;
    let out = integrate(&spec(f, &NoCoast, 3600.0, vec![T0 + DAY]), &[p]).unwrap();
    let q = final_position(&out.tracks[0]);
    // Northward wind, leeway rotated 90 degrees clockwise: due east at 0.2 m/s.
    assert!(q[0] > 92.0 && (q[1] + 35.0).abs() < 1e-6);
    assert!((distance_m([92.0, -35.0], q) - 0.2 * DAY).abs() < 20.0);
}

#[test]
fn vertical_velocity_absent_is_flagged_never_zero() {
    let levels = vec![0.5, 10.0, 100.0, 1000.0, 3000.0];
    let col = UniformColumn::new(0.1, -0.05, None, levels.clone(), 4000.0);
    let prof = col.profile(T0, [95.0, -33.0]).unwrap();
    assert_eq!(prof.w_up, VerticalVelocity::Absent);
    let s = prof.at_depth(500.0, Some(3900.0), BelowModelBottom::Refuse).unwrap();
    assert_eq!(s.w_up, None);
    assert_eq!(s.status, DepthStatus::Resolved);
    assert!((s.u_east - 0.1).abs() < 1e-12);
    let col = UniformColumn::new(0.1, -0.05, Some(-1e-4), levels, 4000.0);
    let s = col.profile(T0, [95.0, -33.0]).unwrap().at_depth(500.0, None, BelowModelBottom::Refuse).unwrap();
    assert_eq!(s.w_up, Some(-1e-4));
    // Pressure is TEOS-10 p_from_z: 1008.321764487538 dbar at 1000 m, 15 deg (GSW-rs doc value).
    let p = mh370_ocean::teos10::pressure_dbar(1000.0, 15.0);
    assert!((p - 1008.321764487538).abs() < 1e-9, "{p}");
}

#[test]
fn seabed_deeper_than_model_bottom_is_flagged() {
    let col = UniformColumn::new(0.2, 0.0, None, vec![0.5, 100.0, 1000.0, 3500.0], 4000.0);
    let prof = col.profile(T0, [95.0, -33.0]).unwrap();
    assert_eq!(prof.bottom_relation(3800.0), BottomRelation::WithinModel);
    assert_eq!(
        prof.bottom_relation(4500.0),
        BottomRelation::SeabedDeeperThanModel { model_bottom_m: 4000.0, seabed_m: 4500.0, gap_m: 500.0 }
    );
    assert_eq!(prof.at_depth(4200.0, Some(4500.0), BelowModelBottom::Refuse), Err(DepthGap::BelowModelBottom { model_bottom_m: 4000.0 }));
    let hold = prof.at_depth(4200.0, Some(4500.0), BelowModelBottom::HoldDeepestLevel).unwrap();
    assert_eq!(hold.u_east, 0.2);
    assert!(matches!(hold.status, DepthStatus::Extrapolated { rule: BelowModelBottom::HoldDeepestLevel, .. }));
    let lin = prof.at_depth(4250.0, Some(4500.0), BelowModelBottom::LinearToZeroAtSeabed).unwrap();
    assert!((lin.u_east - 0.1).abs() < 1e-12);
    assert_eq!(prof.at_depth(4600.0, Some(4500.0), BelowModelBottom::HoldDeepestLevel), Err(DepthGap::BelowSeabed { seabed_m: 4500.0 }));
    // Between the deepest level and the model bottom the deepest level is held, unflagged.
    assert_eq!(prof.at_depth(3800.0, Some(4500.0), BelowModelBottom::Refuse).unwrap().status, DepthStatus::Resolved);
}

#[test]
fn results_do_not_depend_on_thread_count() {
    let c = Uniform::current(0.05, 0.02);
    let parts: Vec<Particle> = (0..200).map(|i| particle(95.0 + 0.01 * i as f64, -33.0, 0.0, 0.0)).collect();
    let run = |threads| {
        let mut sp = spec(current_only(&c), &NoCoast, 6.0 * 3600.0, vec![T0 + 5.0 * DAY]);
        sp.diffusion = Diffusion::random_walk_nm_per_day(5.0);
        sp.ocean_error = OceanErrorModel::eddying(0.05, 150_000.0, 30.0 * DAY, 32);
        sp.threads = threads;
        integrate(&sp, &parts).unwrap().tracks.iter().map(final_position).collect::<Vec<_>>()
    };
    assert_eq!(run(1), run(2));
}

#[test]
fn segment_edges_are_continuous_in_chainage() {
    // An oblique coast: edges are contiguous, increasing, and the interior edges sum to the
    // along-line arc length; a parallel coast gives R cos(lat) dlon exactly.
    let oblique = StraightCoast { a: [40.0, -25.0], b: [35.0, -34.0], segments: 9, first_id: 0, land_left: true, line: 1 };
    let e = oblique.segments();
    assert_eq!(e.len(), 9);
    for w in e.windows(2) {
        assert_eq!(w[0].end_m, w[1].start_m);
        assert!(w[1].start_m > w[0].start_m || w[0].start_m == f64::NEG_INFINITY);
    }
    let parallel = StraightCoast { a: [20.0, -34.0], b: [30.0, -34.0], segments: 2, first_id: 0, land_left: true, line: 2 };
    let exact = EARTH_RADIUS_M * 34f64.to_radians().cos() * 5f64.to_radians();
    assert!((parallel.segments()[0].end_m - exact).abs() < 1e-6 * exact);
}

#[test]
fn diffusivity_is_one_eta_draw_per_run() {
    let prior = DiffusivityPrior::provisional("glorys12v1");
    let ks: Vec<f64> = (0..4000)
        .map(|s| match prior.draw(s) {
            Diffusion::Diffusivity { k_m2_s } => k_m2_s,
            d => panic!("{d:?}"),
        })
        .collect();
    assert!(ks.iter().all(|&k| (30.0..=1000.0).contains(&k)));
    // Log-uniform: the fraction below the geometric mean of the bounds is one half (SE 0.8%).
    let below = ks.iter().filter(|&&k| k < (30.0f64 * 1000.0).sqrt()).count() as f64 / ks.len() as f64;
    assert!((below - 0.5).abs() < 0.03, "{below}");
    assert_eq!(prior.draw(17), prior.draw(17));
    assert!(prior.ln_density(5.0).is_infinite());
    // Drift's question: with no ocean error and no diffusion, the run seed changes nothing.
    let c = Uniform::current(0.05, 0.02);
    let parts = [particle(95.0, -33.0, 0.0, 0.0)];
    let run = |seed| {
        let mut sp = spec(current_only(&c), &NoCoast, 6.0 * 3600.0, vec![T0 + 5.0 * DAY]);
        sp.seed = seed;
        final_position(&integrate(&sp, &parts).unwrap().tracks[0])
    };
    assert_eq!(run(1), run(2));
}

#[test]
fn gridded_product_loads_from_manifest() {
    let dir = std::env::temp_dir().join(format!("mh370-ocean-test-{}", std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    let vals: Vec<f32> = [0.3f32, -0.1].iter().copied().cycle().take(2 * 2 * 2 * 2).collect();
    std::fs::write(dir.join("g.f32"), vals.iter().flat_map(|v| v.to_le_bytes()).collect::<Vec<u8>>()).unwrap();
    let manifest = format!(
        r#"{{"product":"glorys12v1","component":"Current","description":"test","lon":[100.0,101.0],"lat":[-31.0,-30.0],"time_unix_s":[{T0},{}],"data_file":"g.f32"}}"#,
        T0 + DAY
    );
    std::fs::write(dir.join("g.json"), manifest).unwrap();
    let g = GridField::load(&dir.join("g.json")).unwrap();
    let v = g.sample(T0 + 0.3 * DAY, [100.4, -30.2]).unwrap();
    assert!((v[0] - 0.3).abs() < 1e-6 && (v[1] + 0.1).abs() < 1e-6);
    assert_eq!(g.meta().contents.stokes, Inclusion::Excluded);
    std::fs::remove_dir_all(&dir).unwrap();
}

#[test]
fn constant_magnitude_leeway_follows_rotated_downwind() {
    // CSIRO flaperon form: 0.10 m/s, 16 deg left of downwind (angle -16), independent of wind speed.
    let c = Uniform::current(0.0, 0.0);
    for wind in [5.0, 15.0] {
        let w = Uniform::new(Component::Wind10m, 0.0, wind);
        let f = Forcing { current: &c, stokes: None, wind10: Some(&w) };
        let mut p = particle(92.0, -35.0, 0.0, 0.0);
        p.response.leeway_speed_mps = 0.10;
        p.response.leeway_angle_deg = -16.0;
        let q = final_position(&integrate(&spec(f, &NoCoast, 3600.0, vec![T0 + DAY]), &[p]).unwrap().tracks[0]);
        assert!((distance_m([92.0, -35.0], q) - 0.10 * DAY).abs() < 20.0, "wind {wind}");
        // Left of a northward wind: westward component sin(16 deg) of the displacement.
        let east = (q[0] - 92.0).to_radians() * EARTH_RADIUS_M * (35f64).to_radians().cos();
        assert!((east + 0.10 * DAY * 16f64.to_radians().sin()).abs() < 30.0, "east {east}");
    }
    // Both wind terms share the angle: 1.2% of 10 m/s plus 0.10 m/s, at -16 deg, is 0.22 m/s.
    let w = Uniform::new(Component::Wind10m, 0.0, 10.0);
    let f = Forcing { current: &c, stokes: None, wind10: Some(&w) };
    let mut p = particle(92.0, -35.0, 0.0, 0.012);
    p.response.leeway_speed_mps = 0.10;
    p.response.leeway_angle_deg = -16.0;
    let q = final_position(&integrate(&spec(f, &NoCoast, 3600.0, vec![T0 + DAY]), &[p]).unwrap().tracks[0]);
    assert!((distance_m([92.0, -35.0], q) - 0.22 * DAY).abs() < 30.0);
    // Calm: below the declared threshold the constant-magnitude term is zero.
    let calm = Uniform::new(Component::Wind10m, 0.0, 0.4 * LEEWAY_CALM_WIND_MPS);
    let f = Forcing { current: &c, stokes: None, wind10: Some(&calm) };
    let mut p = particle(92.0, -35.0, 0.0, 0.0);
    p.response.leeway_speed_mps = 0.10;
    let q = final_position(&integrate(&spec(f, &NoCoast, 3600.0, vec![T0 + DAY]), &[p]).unwrap().tracks[0]);
    assert_eq!(q, [92.0, -35.0]);
}

#[test]
fn transplanted_response_is_refused_unless_explicit_residual() {
    let c = Uniform::current(0.0, 0.0);
    let s = Uniform::new(Component::StokesDrift, 0.05, 0.0);
    let w = Uniform::new(Component::Wind10m, 0.0, 10.0);
    let f = Forcing { current: &c, stokes: Some(&s), wind10: Some(&w) };
    let mut p = particle(92.0, -35.0, 1.0, 0.0);
    p.response.leeway_speed_mps = 0.10;
    let mut sp = spec(f, &NoCoast, 3600.0, vec![T0 + DAY]);
    assert!(matches!(integrate(&sp, &[p]), Err(CompositionError::DoubleCount(_))));
    sp.explicit_residual = true;
    let out = integrate(&sp, &[p]).unwrap();
    assert!(out.provenance.explicit_residual);
    // Constant-magnitude leeway without a wind field is a missing component.
    let mut q = particle(92.0, -35.0, 0.0, 0.0);
    q.response.leeway_speed_mps = 0.1;
    let r = integrate(&spec(current_only(&c), &NoCoast, 3600.0, vec![T0 + DAY]), &[q]);
    assert_eq!(r.err(), Some(CompositionError::MissingComponent(Component::Wind10m)));
}

#[test]
fn per_particle_end_time_stops_each_particle_at_its_own_time() {
    // Settling's float phase: each element stops at its own sink time; the state there equals a
    // run with that single output time, and later outputs are PastEnd.
    let c = Uniform::current(0.1, 0.0);
    let times = vec![T0 + DAY, T0 + 2.0 * DAY];
    let mut a = particle(92.0, -35.0, 0.0, 0.0);
    a.end_time = Some(T0 + 0.37 * DAY); // before the first output
    let mut b = particle(92.0, -35.0, 0.0, 0.0);
    b.end_time = Some(T0 + 1.5 * DAY); // between outputs
    let mut d = particle(92.0, -35.0, 0.0, 0.0);
    d.end_time = Some(T0 + 3.25 * DAY); // after the last output
    let out = integrate(&spec(current_only(&c), &NoCoast, 6.0 * 3600.0, times.clone()), &[a, b, d]).unwrap();
    for (tr, days) in out.tracks.iter().zip([0.37, 1.5, 3.25]) {
        let Some(Snapshot::Afloat(q)) = tr.end else { panic!("{:?}", tr.end) };
        assert!((distance_m([92.0, -35.0], q) - 0.1 * days * DAY).abs() < 20.0, "{days}");
        for (s, &tout) in tr.snapshots.iter().zip(&times) {
            if tout > T0 + days * DAY {
                assert_eq!(*s, Snapshot::PastEnd);
            } else {
                assert!(matches!(s, Snapshot::Afloat(_)));
            }
        }
    }
    // Same ocean as a call with that single output time (one seed, one realisation).
    let eddy = OceanErrorModel::eddying(0.1, 100_000.0, 10.0 * DAY, 32);
    let mut sp = spec(current_only(&c), &NoCoast, 6.0 * 3600.0, times.clone());
    sp.ocean_error = eddy;
    let with_end = integrate(&sp, &[b]).unwrap();
    let mut sp2 = spec(current_only(&c), &NoCoast, 6.0 * 3600.0, vec![T0 + 1.5 * DAY]);
    sp2.ocean_error = eddy;
    let single = integrate(&sp2, &[particle(92.0, -35.0, 0.0, 0.0)]).unwrap();
    assert_eq!(with_end.tracks[0].end, Some(single.tracks[0].snapshots[0]));
    // No end time: no end state.
    let out = integrate(&spec(current_only(&c), &NoCoast, 6.0 * 3600.0, times), &[particle(92.0, -35.0, 0.0, 0.0)]).unwrap();
    assert_eq!(out.tracks[0].end, None);
}

#[test]
fn banded_error_keys_the_bottom_band_to_height_above_seabed() {
    use mh370_ocean::stochastic::{ErrorKind, VerticalStructure};
    let model = OceanErrorModel {
        kind: ErrorKind::Eddying { sigma_m_s: 0.05, length_scale_m: 50e3, time_scale_s: 5.0 * DAY, modes: 64 },
        vertical: VerticalStructure::Banded { surface_to_m: 50.0, upper_to_m: 1000.0, near_bottom_m: 200.0, factors: [1.0, 0.6, 0.3, 0.5] },
    };
    let p = [95.0, -33.0];
    let n = 2000;
    let (mut surf_deep, mut ss, mut dd, mut deep_var, mut nb_var) = (0.0, 0.0, 0.0, 0.0, 0.0);
    for seed in 0..n {
        let r = model.realise(seed);
        let s = r.velocity_with_seabed(T0, p, 10.0, Some(4000.0))[0];
        let d = r.velocity_with_seabed(T0, p, 3000.0, Some(4000.0))[0];
        let nb = r.velocity_with_seabed(T0, p, 3850.0, Some(4000.0))[0];
        // Without a seabed, 3850 m is in the deep band.
        assert_eq!(r.velocity(T0, p, 3850.0), r.velocity_with_seabed(T0, p, 3000.0, Some(4000.0)));
        surf_deep += s * d;
        ss += s * s;
        dd += d * d;
        deep_var += d * d;
        nb_var += nb * nb;
    }
    let corr = surf_deep / (ss * dd).sqrt();
    assert!(corr.abs() < 0.1, "surface and deep bands correlated: {corr}");
    // Amplitudes: deep 0.3 x 0.05, near-bottom 0.5 x 0.05 (SE of a variance from 2000 draws ~3%).
    assert!(((deep_var / n as f64).sqrt() / 0.015 - 1.0).abs() < 0.08);
    assert!(((nb_var / n as f64).sqrt() / 0.025 - 1.0).abs() < 0.08);
    // Within a band one realisation: identical at two depths of the same band, scaled by nothing.
    let r = model.realise(7);
    assert_eq!(r.velocity_with_seabed(T0, p, 1500.0, Some(5000.0)), r.velocity_with_seabed(T0, p, 2500.0, Some(5000.0)));
}

#[test]
fn teos10_matches_official_gsw() {
    // Fixtures from the official Python gsw 3.6 (GSW-C), computed independently of this crate.
    for (sa, ct, p, rho, c) in [
        (35.0, 2.0, 4000.0, 1045.8327375098308, 1525.9684690292324),
        (34.7, 1.2, 5500.0, 1052.1128078615443, 1548.8752390707841),
        (35.5, 20.0, 10.0, 1025.0580725951668, 1521.983199212616),
    ] {
        let (r, s) = mh370_ocean::teos10::rho_and_sound_speed(sa, ct, p).unwrap();
        assert!((r - rho).abs() < 1e-9 && (s - c).abs() < 1e-9, "{r} {s}");
    }
    // A GLORYS-like column (potential temperature 2 C, SP 34.7) at 3000 m, 33 S.
    let col = UniformColumn::new(0.0, 0.0, None, vec![10.0, 3000.0], 4000.0);
    let t = col.profile(T0, [95.0, -33.0]).unwrap().teos10().unwrap();
    assert!(!t.sa_anomaly_included);
    assert!((t.absolute_salinity_g_kg[1] - 34.863625371428576).abs() < 1e-9);
    assert!((t.conservative_temperature_c[1] - 1.9995246765942478).abs() < 1e-9);
    assert!((t.pressure_dbar[1] - 3043.0970905327536).abs() < 1e-6);
    assert!((t.in_situ_density_kg_m3[1] - 1041.5723776365178).abs() < 1e-6);
    assert!((t.sound_speed_m_s[1] - 1508.9855407336497).abs() < 1e-6);
    assert!((t.rho_at(1505.0) - 0.5 * (t.in_situ_density_kg_m3[0] + t.in_situ_density_kg_m3[1])).abs() < 1e-9);
}

fn write_bathy(dir: &std::path::Path) -> std::path::PathBuf {
    // 0.01-degree grid over 99-101 E, 31-29 S: 4000 m everywhere, a ridge at 100.03 E (-500 m, TID 11).
    std::fs::create_dir_all(dir).unwrap();
    let (n, lon0, lat0) = (201usize, 99.0, -31.0);
    let mut z = Vec::new();
    let mut tid = Vec::new();
    for _j in 0..n {
        for i in 0..n {
            let ridge = i == 103;
            z.extend_from_slice(&(if ridge { -500i16 } else { -4000i16 }).to_le_bytes());
            tid.push(if ridge { 11u8 } else { 40u8 });
        }
    }
    std::fs::write(dir.join("z.i16"), z).unwrap();
    std::fs::write(dir.join("t.u8"), tid).unwrap();
    let m = format!(r#"{{"source":"gebco_2026","lon0":{lon0},"lat0":{lat0},"step_deg":0.01,"nlon":{n},"nlat":{n},"elevation_file":"z.i16","elevation_dtype":"i16","tid_file":"t.u8"}}"#);
    std::fs::write(dir.join("b.json"), m).unwrap();
    dir.join("b.json")
}

#[test]
fn bathymetry_path_reports_track_tid_and_corridor_maximum() {
    use mh370_ocean::bathy::{BathySource, Bathymetry};
    let dir = std::env::temp_dir().join(format!("mh370-bathy-{}", std::process::id()));
    let m = write_bathy(&dir);
    let b = Bathymetry::load(&[m.as_path()], None).unwrap();
    let s = b.at([99.5, -30.0]).unwrap();
    assert_eq!((s.depth_m, s.tid, s.source), (4000.0, Some(40), BathySource::Gebco2026));
    // Northward along 100.0 E: the ridge is 0.03 deg (about 2.9 km) to the east, i.e. to the right.
    let wide = b.path([100.0, -30.8], [100.0, -29.2], 250.0, 4000.0);
    assert!(wide.iter().all(|x| x.is_some()));
    for x in wide.iter().flatten() {
        assert_eq!(x.track.depth_m, 4000.0);
        assert_eq!((x.corridor_max.elevation_m, x.corridor_max.tid), (-500.0, Some(11)));
        // The ridge cell spans 100.025-100.035 E, 2.41-3.37 km east at 30 S; the first cross-track
        // sample inside it is reported.
        assert!(x.corridor_max_offset_m >= 2410.0 && x.corridor_max_offset_m <= 3370.0, "{}", x.corridor_max_offset_m);
    }
    let narrow = b.path([100.0, -30.8], [100.0, -29.2], 250.0, 2000.0);
    assert!(narrow.iter().flatten().all(|x| x.corridor_max.elevation_m == -4000.0));
    // A window load answers the same inside the window and nothing outside it.
    let w = Bathymetry::load(&[m.as_path()], Some([99.9, 100.1, -30.1, -29.9])).unwrap();
    assert_eq!(w.at([100.03, -30.0]).unwrap().elevation_m, -500.0);
    assert!(w.at([99.5, -30.0]).is_none());
    // WGS84 geodesic air9 to H01W: 1,662.8 km, as computed in ruling H1 (the stub's 1,662.5 km is
    // its last 0.5 km sample, not the geodesic length).
    let (d, _) = b.inverse([98.8821, -27.5612], [114.142637, -34.890303]);
    assert!((d / 1000.0 - 1662.83).abs() < 0.01, "{d}");
    std::fs::remove_dir_all(&dir).unwrap();
}

#[test]
fn sound_speed_climatology_interpolates_without_filling() {
    use mh370_ocean::soundspeed::{woa23_period, SoundSpeedClimatology};
    let dir = std::env::temp_dir().join(format!("mh370-woa-{}", std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    // 2 x 2 grid, 3 levels; the deepest level exists only at one corner of four... then at none.
    let (nlat, nlon, nz) = (2usize, 2usize, 3usize);
    let mut cm = vec![0f32; nlat * nlon * nz];
    for j in 0..nlat {
        for i in 0..nlon {
            for k in 0..nz {
                cm[(j * nlon + i) * nz + k] = 1500.0 + 10.0 * i as f32 + k as f32;
            }
        }
    }
    cm[(0 * nlon + 0) * nz + 2] = f32::NAN;
    cm[(0 * nlon + 1) * nz + 2] = f32::NAN;
    cm[(1 * nlon + 0) * nz + 2] = f32::NAN;
    let mut cm_all_nan = cm.clone();
    cm_all_nan[(1 * nlon + 1) * nz + 2] = f32::NAN;
    let bytes = |v: &Vec<f32>| v.iter().flat_map(|x| x.to_le_bytes()).collect::<Vec<u8>>();
    for (name, v) in [("c.f32", &cm), ("sd.f32", &vec![2f32; 12]), ("sa.f32", &vec![35f32; 12]), ("ct.f32", &vec![3f32; 12])] {
        std::fs::write(dir.join(name), bytes(v)).unwrap();
    }
    let man = r#"{"product":"woa23","decade":"A5B4","month":3,"lon0":95.5,"lat0":-33.5,"step_deg":1.0,"nlon":2,"nlat":2,"depth_m":[0.0,100.0,1000.0],"c_mean_file":"c.f32","c_sd_file":"sd.f32","sa_file":"sa.f32","ct_file":"ct.f32"}"#;
    std::fs::write(dir.join("m.json"), man).unwrap();
    let w = SoundSpeedClimatology::load(&dir.join("m.json")).unwrap();
    let p = w.profile([96.0, -33.0]).unwrap();
    assert!((p.c_mean_m_s[1] - 1506.0).abs() < 1e-4); // midway in lon: 1500 + 5 + 1
    assert!((p.c_mean_m_s[2] - 1512.0).abs() < 1e-4); // only the (96.5, -32.5) corner has data: renormalised to it
    assert!((p.pressure_dbar[2] - mh370_ocean::teos10::pressure_dbar(1000.0, -33.0)).abs() < 1e-12);
    std::fs::write(dir.join("c.f32"), bytes(&cm_all_nan)).unwrap();
    let w = SoundSpeedClimatology::load(&dir.join("m.json")).unwrap();
    assert!(w.profile([96.0, -33.0]).unwrap().c_mean_m_s[2].is_nan());
    assert!(w.profile([99.0, -33.0]).is_none());
    std::fs::remove_dir_all(&dir).unwrap();
    // Epochs: Blackman 2001 and 2003 in 95A4, MH370 in A5B4, later events in B5C2.
    assert_eq!(woa23_period(1_002_499_200.0), ("95A4", 10)); // 2001-10-08
    assert_eq!(woa23_period(1_054_339_200.0), ("95A4", 5)); // 2003-05-31
    assert_eq!(woa23_period(T0), ("A5B4", 3));
    assert_eq!(woa23_period(1_577_836_800.0), ("B5C2", 1)); // 2020-01-01
}
