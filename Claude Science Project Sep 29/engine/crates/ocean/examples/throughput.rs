//! Field-evaluation throughput of the batch integrator on a real gridded product (brief
//! deliverable 5, drift's pilot assumption of 2e7 evaluations per second per core).
//!
//! One evaluation = one `VectorField::sample` of the current: trilinear over 8 nodes with land
//! renormalisation. RK2 makes two per particle-step. Particles are released on a regular grid over
//! drift's source region (92-106 E, 26-40 S) at 12:00 UTC on 8 March 2014 and run at a 6 h step to
//! 12:00 UTC on 29 April 2014, with K = 248 m^2/s diffusion and no coast (product land ends a
//! trajectory as a flagged field gap).
//!
//! cargo run -p mh370-ocean --release --example throughput -- <current> <threads> <particles> [<stokes> <wind>]
//!
//! Each field argument is a part manifest (`*.json`) or a series manifest (`*.series.json`). With Stokes
//! and wind given, every particle carries a_stokes = 1 and c_wind = 0.02, so each RK2 stage samples three
//! fields; the reported evaluations then count all three.

use mh370_ocean::*;
use std::time::Instant;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let manifest = std::path::Path::new(&args[1]);
    let threads: usize = args[2].parse().unwrap();
    let n: usize = args[3].parse().unwrap();
    let open = |p: &std::path::Path| {
        if p.to_string_lossy().ends_with(".series.json") { GridField::load_series(p) } else { GridField::load(p) }.expect("load")
    };
    let t_load = Instant::now();
    let field = open(manifest);
    let extra = (args.len() >= 6).then(|| (open(std::path::Path::new(&args[4])), open(std::path::Path::new(&args[5]))));
    let load_s = t_load.elapsed().as_secs_f64();
    let (a_s, c_w, per_stage) = if extra.is_some() { (1.0, 0.02, 3.0) } else { (0.0, 0.0, 1.0) };
    let t0 = 1_394_280_000.0; // 2014-03-08T12:00:00Z
    let t1 = t0 + 52.0 * SECONDS_PER_DAY;
    let side = (n as f64).sqrt().ceil() as usize;
    let particles: Vec<Particle> = (0..n)
        .map(|i| {
            let p = [92.0 + 14.0 * ((i % side) as f64 + 0.5) / side as f64, -40.0 + 14.0 * ((i / side) as f64 + 0.5) / side as f64];
            Particle::new(p, t0, ObjectResponse::new(a_s, c_w))
        })
        .collect();
    let step_s = 6.0 * 3600.0;
    let spec = RunSpec {
        forcing: Forcing {
            current: &field,
            stokes: extra.as_ref().map(|e| &e.0 as &dyn VectorField),
            wind10: extra.as_ref().map(|e| &e.1 as &dyn VectorField),
        },
        coast: &NoCoast,
        domain: Domain { lon_min: 15.0, lon_max: 120.0, lat_min: -50.0, lat_max: 0.0 },
        step_s,
        output_times: (1..=7).map(|w| t0 + w as f64 * 7.0 * SECONDS_PER_DAY).chain([t1]).collect(),
        diffusion: Diffusion::Diffusivity { k_m2_s: 248.0 },
        ocean_error: OceanErrorModel::none(),
        refloat: Refloat::Off,
        seed: 1,
        leeway_absorbs_stokes: false,
        accept_partial_stokes_overlap: false,
        explicit_residual: false,
        threads,
    };
    let start = Instant::now();
    let out = integrate(&spec, &particles).expect("integrate");
    let wall = start.elapsed().as_secs_f64();
    let mut steps = 0u64;
    let mut afloat = 0usize;
    for tr in &out.tracks {
        let t_end = match tr.events.first() {
            Some(Event::FieldGap { t, .. }) | Some(Event::LeftDomain { t, .. }) => *t,
            Some(Event::NonFinitePosition { t }) => *t,
            _ => t1,
        };
        if tr.fate == Fate::Afloat {
            afloat += 1;
        }
        steps += ((t_end - t0) / step_s).ceil() as u64;
    }
    let evals = 2.0 * per_stage * steps as f64;
    println!(
        "{{\"threads\":{threads},\"particles\":{n},\"afloat_at_end\":{afloat},\"particle_steps\":{steps},\"field_evaluations\":{evals},\"load_s\":{load_s:.2},\"wall_s\":{wall:.3},\"evals_per_s\":{:.4e},\"evals_per_s_per_thread\":{:.4e}}}",
        evals / wall,
        evals / wall / threads as f64
    );
}
