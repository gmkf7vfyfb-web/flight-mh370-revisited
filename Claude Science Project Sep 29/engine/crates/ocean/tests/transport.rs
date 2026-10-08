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
    Particle { release: [lon, lat], release_time: T0, response: ObjectResponse::new(a_stokes, c_wind) }
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
    let coast = StraightCoast { a: [100.0, -40.0], b: [100.0, -30.0], segments: 10, first_id: 500, land_left: false };
    assert!(coast.is_land([100.1, -35.0]) && !coast.is_land([99.9, -35.0]));
    let c = Uniform::current(0.5, 0.0);
    let times = vec![T0 + DAY, T0 + 3.0 * DAY];
    let parts = [particle(99.9, -34.55, 0.0, 0.0), particle(99.6, -38.05, 0.0, 0.0), particle(99.2, -25.0, 0.0, 0.0)];
    let out = integrate(&spec(current_only(&c), &coast, 6.0 * 3600.0, times), &parts).unwrap();
    for (tr, (lon, lat, seg)) in out.tracks.iter().zip([(99.9, -34.55, 505), (99.6, -38.05, 501), (99.2, -25.0, 509)]) {
        assert_eq!(tr.fate, Fate::Beached);
        let Event::Beached { t, at, segment } = tr.events[0] else { panic!("{:?}", tr.events) };
        assert_eq!(segment, seg);
        let expected = distance_m([lon, lat], [100.0, lat]) / 0.5;
        assert!(((t - T0) - expected).abs() < 60.0, "beach time {} vs {expected}", t - T0);
        assert!((at[0] - 100.0).abs() < 1e-9 && (at[1] - lat).abs() < 1e-9);
        for (s, &tout) in tr.snapshots.iter().zip(&out.output_times) {
            if tout >= t {
                assert_eq!(*s, Snapshot::Beached { at, segment: seg });
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
    // Pressure: Saunders (1981) gives ~1010 dbar at 1000 m, 30 S.
    let p = mh370_ocean::profile::pressure_dbar_saunders(1000.0, -30.0);
    assert!((p - 1009.6).abs() < 0.5, "{p}");
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
