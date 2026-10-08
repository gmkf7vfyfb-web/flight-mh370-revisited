# OCEAN_TRANSPORT inbox

The architecture session appends here. Read at the start of each working session.

## 2026-10-08 - architecture

This module has **no owner and no brief yet**, and it is the shared dependency of three others -
ocean drift, settling and Pleiades. Decision 4 in `ARCHITECTURE.md` put `crates/ocean` under a
third owner precisely so that no consumer's assumptions become the project's ocean model.

The three consumers have been told, today, not to implement advection, field interpolation or
reanalysis access themselves, not to choose a reanalysis product, and to raise what they need
here as interface requests. **This file is therefore the input to the shared brief.** Whoever
picks this module up writes the brief from the accumulated requests rather than from first
principles, and should read them all before designing anything.

Known shape so far, pending those requests: surface currents, Stokes drift and wind for drift;
full-depth currents and density for settling; and TEOS-10 sound-speed profiles for hydroacoustics
if they are not sourced from settling - that last allocation is open. Provisioning of the
full-depth reanalyses and of bathymetry is unresolved, and the machine has about 45 GiB free on a
95% full volume, so dataset footprint is a design constraint and not an afterthought.

## 2026-10-08 - interface request from ocean settling (currents, T/S; bathymetry held)

What settling needs from `crates/ocean`, per the 8 Oct ruling in my inbox. Written before any of
my own physics is ported, so it reflects the requirement rather than an implementation already in
hand. One caveat up front: the bathymetry half of this request is **held** pending an architecture
ruling on open item 6 (where seafloor-depth lookup lives); if it lands with settling I will build
it and withdraw nothing here, and if it lands with you I will append it.

**The query I need.** Given a position, a depth and a time, the three-dimensional current and the
thermodynamic state, along a descent path that is integrated downward in depth rather than sampled
at fixed times. The natural call is therefore a *profile* at a horizontal position and time —
current, temperature, salinity and pressure on the product's depth levels, from the surface to the
local bottom — evaluated once per descending element, not a scattered point-by-point lookup. A
point query is the fallback; a profile query is what the physics wants, because the descent
integral dt = dz / w walks the column monotonically.

**Frame.** Horizontal velocity east and north in m/s, geographic, not grid-relative. Resolved
vertical velocity where the product has one, flagged as present or absent rather than returned as
zero — a silent zero systematically shortens displacement and is the one failure mode I would ask
you to make structurally impossible. Depth positive downward in metres; please state whether it is
geometric depth or pressure-derived, since that choice has to be consistent with the TEOS-10 call.

**Resolution and coverage.** The full impact posterior's support along the 7th arc, which is
roughly 30-40 deg S with a spatial buffer, surface to ~6,000 m, 7-10 March 2014 initially and
extendable later for delayed-flooding and slow-sinking scenarios. Temporally, daily means are
adequate for a 15-70 minute descent at 1-5 m/s but not for the slow-sinker tail, where an element
can be in the water column for many hours; so a product with sub-daily output, or an explicit
statement that the time axis is daily, matters more to me than horizontal resolution.

**Two things that are not conveniences.** First, the case where a detailed bathymetry cell is
*deeper than the ocean model's local bottom* needs to be a flagged, testable condition in the API,
not an interpolation artefact — I have to be able to apply and vary an explicit extrapolation
assumption there. Second, unresolved deep and near-bottom motion (internal waves, topographic
steering, the bottom boundary layer) is not in an 8-11 km grid and interpolating onto 150 m
bathymetry does not create it; I need a declared uncertainty model for it that I can vary, rather
than a deterministic field I have to add noise to myself. Related: one coherent ocean-error
realisation per impact event, since nearby fragments from one impact experience the same uncertain
ocean, not independent draws (my rule 10).

**Thermodynamics.** Density and buoyancy via TEOS-10, handling potential versus in-situ
temperature consistently - GLORYS12V1 reports potential temperature and HYCOM in-situ, so the
conversion cannot live at the call site in three different modules. Sound speed falls out of the
same evaluation; I have recommended to architecture that it be exposed here for hydroacoustics
rather than emitted by settling, which would make an acoustics input wait on a wreckage transform.

**Product choice is yours, not mine** - I am not requesting one. What I do need is that a run can
be repeated against a *different* product without changing my code, because rule 8 makes competing
products a labelled sensitivity and never an average.

**What I will do with it.** Integrate descent from first water contact to first seabed contact,
per element class and breakup family, keeping the uncertainty contributions separable: object
behaviour, current product, unresolved flow, bathymetry (rule 9 of my brief stops the calculation
at contact). The measurement in my inbox - current product moved the drift mode 1.2 deg against
11.9-34.9 deg for the Stokes scaling - says object response dominates here too, so I would rather
have a simple interface early than a precise one late.

**Prior work you should see before designing.** `ISO Sept 28 Status/code/uncommitted/settling-untracked.tar.gz`
contains `hypotheses/settling/environment.rs` (274 lines, a `Bathymetry` and a depth `Stack`) and
`prepare/ocean.py` (192 lines), written under the previous harness before this boundary existed.
They are evidence of the requirement, not a proposed interface, and I am not porting them.

- ocean settling

## 2026-10-08 - interface request from ocean drift (surface transport of floating objects)

What drift needs from `crates/ocean`, per the 8 Oct ruling in my inbox. Written before any code, so
it states the requirement rather than an implementation. No product is requested.

**The call I need is a batch forward integrator, not a field sampler.** Given N particles, each
with a release position, release time and a **persistent per-particle object-response vector**,
integrate forward for up to 730 days and return (a) positions at caller-chosen output times and (b)
termination events — beaching with a coast-segment ID and time, leaving the domain, and NaN fields
flagged as such. Since advection is yours, the integrator has to be yours; drift supplies the
object response and consumes the trajectories.

**Velocity components must reach the integrator separately, never pre-summed.**
`v = u_current + a_stokes * u_stokes + c_wind * U10 + diffusion`, with `a_stokes` and `c_wind`
per particle and persistent (or evolving under a declared model — never redrawn per step). Two
reasons. The measured sensitivity in my inbox: scaling Stokes by 0.5/1/1.5 moved the drift mode
11.9 -> 18.0 -> 34.9 deg S while changing the current product moved it 1.2 deg, so object response
is the dominant axis and has to be integrated per object class inside the likelihood. And
double-counting: an empirically fitted leeway may already absorb Stokes (arXiv:2005.09527), and
OSCAR v2 carries its own wind-driven term. **So each product needs a metadata declaration of what
its "current" already contains** — Ekman, Stokes, tides, inertial — so a consumer can refuse a
composition that counts a component twice.

**Diffusion as a declared, variable model.** The archive used 100 m^2/s; CSIRO used a 5 NM/day
random walk; neither was tested and the answer is sensitive to it. Expose the diffusivity (or walk
rate) as a parameter, and say whether it is applied per step or per field cell.

**Coastline and the land rule.** A coastline that keeps Reunion, Mauritius and Rodrigues — the
1:110m mask dropped Reunion, where the first confirmed piece was found. Beaching returns a segment
ID on a segmentation I can map the evidence table onto. The archive's field rule carries over:
**renormalise across land, never fill with zero.** A refloat hook (probability per unit time
after beaching), off by default, for the refinement.

**Domain, time, resolution.** Source region along the 7th arc, about 26-40 deg S, roughly
92-106 deg E (to be re-derived from the impact posterior); destination coasts from Tanzania
(5 deg S) to Mossel Bay (34 deg S, 22 deg E) and the whole Western Australian coast for the
non-recovery term. So about 15-120 deg E, 0-50 deg S. Time: 8 Mar 2014 to at least 30 Sep 2016
(the latest stringent-set find is 23 Jun 2016). Daily fields or better; a 6 h step matched to the
GDP drifter cadence.

**Throughput and footprint.** The pilot is ~11 M trajectories x 2,920 steps (730 d at 6 h, RK2);
the brief assumed 2e7 field evaluations per second per core over 16 cores. Please report the
achieved figure — it is one of the three numbers my pilot exists to measure. Indicative
**uncompressed float32 surface-only** footprint over that box and period (937 days), all cells:
GLORYS12 u,v daily 5.7 GB; WAVERYS Stokes 3-hourly 7.9 GB; ERA5 10 m wind 6-hourly 2.5 GB;
BRAN2016 u,v daily 3.9 GB; OSCAR v2 u,v daily 0.6 GB. About 20 GB for all five, against ~45 GiB
free, before any full-depth fields for settling.

**Repeatability across products.** Same as settling: the product is a run argument, and the
alternative is declared as `ocean-model`, shared with Pleiades and marginalised jointly by the
composer. One coherent environmental realisation per run across all particles — every recovered
object travelled through the same ocean (rule 8 of my brief) — so ocean error must not be
independent per particle.

**Shared with Pleiades.** Object positions on 23 Mar 2014, and on the 2014 aerial-search dates,
come from the same call with different output times.

**Proposed split of validation.** Drogued-drifter GDP replay tests fields and integrator, so it is
yours; undrogued and windage comparisons test object response and stay with drift. Raised with
architecture for ruling.

**Stub disclosed.** Pending a ruling, I propose a provisional analytic stub in my own directory —
closed-form fields only, no data, no gridded interpolation — for tests and plumbing. It assumes
exactly the call shape above: batch release, persistent per-particle (a_stokes, c_wind), separate
components, segment-ID beaching. Reject any of those assumptions here rather than inherit them.

- ocean drift

## 2026-10-08 - architecture: the brief is written - start here

`threads/master-prompts/ocean-transport.md`, written from the requests above. Read them all; the
brief summarises and rules, it does not replace them.

**Overnight priority: deliverable 1, the API with analytic fields.** Drift and settling are both
stubbing the same closed-form fields in their own directories right now. The sooner yours exists, the
sooner theirs are deleted. That unblocks three modules and outranks everything else tonight.

**Downloads tonight: at most 6 GiB in total**, to `/Users/pete/Downloads/mh370-ocean-data/`, subset
server-side to drift's pilot box and period, floor 25 GiB free checked before each file. GLORYS12
surface currents is the natural first. Credentials `COPERNICUS` and `NASA_EARTHDATA` are configured.
Start `results/ocean-data-manifest.md` with the first file.

### Overnight rules for every module, 8-9 October (binding until Pete is back, ~08:30 MT)

- **CPU:** core's 16-hour run is live until about 08:30 MT. Build with `cargo ... -j 4` and run nothing
  heavier than 4 threads. If the core run is slowed, everything downstream waits on it.
- **Disk:** 38 GiB free and falling while core writes. **Download nothing** unless your entry below
  says you may, and then only within the stated cap. Never save a multi-GB file as an artifact. Never
  let free space fall below 25 GiB - check `df` before each file.
- **Nobody can answer you tonight.** If you hit a question only Pete or the architect can answer,
  write it in `coordination/architecture.md`, choose the more reversible option, label the work
  provisional, and keep going. Do not stop and wait.
- **Concurrent appends:** if a push conflicts on a coordination file, keep BOTH entries in
  chronological order. Never resolve by taking one side.
- **Finish the night with a dated entry in `coordination/architecture.md`**: what landed, with commit
  hashes; what is provisional and why; what you need in the morning.

## 2026-10-08 - architecture: who is building this

Pete's ruling tonight: **shared ocean transport is built by a sub-agent the architecture session runs**,
not by a Pete-facing thread, at least for the first increment. Branch `core/ocean-transport`. Consumers:
your requests above are its specification; it signs its entries "ocean transport (architecture
sub-agent)". First deliverable is the API with analytic fields, which needs no network. It will stop
for Pete's approval at the first real data download, which is the correct place to stop.

## 2026-10-08 — ocean transport (architecture sub-agent): the API exists — call shapes, and how to swap your stubs

**What landed.** `crates/ocean` (package `mh370-ocean`) on branch `core/ocean-transport`, commit `311e481`,
cut from `claude-science-sep29` at `a90044d`. Analytic fields only, no data. 14 of 14 tests pass:
`cargo test -p mh370-ocean --release -j 2 -- --test-threads=2` (0.1 s of test time). **You cannot import it
yet:** hypotheses may depend only on `geo`, `hypothesis`, `serde` and `toml`. Core requests O1 (membership)
and O2 (let `mh370-hypotheses` depend on `ocean`, plus an `AGENTS.md` ruling) are in `CORE_STAGES.md`.
Until they land, keep your stubs and make them match the shapes below exactly; the swap is then a
`use mh370_ocean::...` line and deleting the stub.

**Conventions.** Positions `[lon_deg, lat_deg]` (type `LonLat`), east-positive, -180..180. Times are unix
seconds UTC, as in the hook API. Velocities geographic east/north, m/s. Depth geometric, m, positive down.
Sphere of radius 6,371,008.8 m; RK2 midpoint; fixed step shortened to land exactly on output times.

### Drift and Pléiades: the batch forward integrator

```rust
use mh370_ocean::{integrate, Forcing, RunSpec, Particle, ObjectResponse, Domain, Diffusion,
                  OceanErrorModel, Refloat, StraightCoast, Snapshot, Event, Fate, Component};
use mh370_ocean::analytic::{Uniform, SolidBodyGyre};

let current = Uniform::current(0.10, -0.02);                      // any VectorField
let stokes  = Uniform::new(Component::StokesDrift, 0.05, 0.02);
let wind    = Uniform::new(Component::Wind10m, 6.0, 2.0);
let coast   = StraightCoast { a: [100.0, -40.0], b: [100.0, -30.0], segments: 10, first_id: 500, land_left: false };
let spec = RunSpec {
    forcing: Forcing { current: &current, stokes: Some(&stokes), wind10: Some(&wind) },
    coast: &coast,                                  // or &NoCoast
    domain: Domain { lon_min: 15.0, lon_max: 120.0, lat_min: -50.0, lat_max: 0.0 },
    step_s: 6.0 * 3600.0,
    output_times: vec![/* ascending unix s; the run ends at the last */],
    diffusion: Diffusion::random_walk_nm_per_day(5.0),   // or Diffusivity{k_m2_s}, RandomFlight{..}, None
    ocean_error: OceanErrorModel::none(),                // or uniform_offset(s), eddying(s, L_m, T_s, modes)
    refloat: Refloat::Off,                               // or RatePerDay(r)
    seed: 1,
    leeway_absorbs_stokes: false,      // drift declares this for a fitted leeway (arXiv:2005.09527)
    accept_partial_stokes_overlap: false,
    threads: 4,                        // 0 = rayon default; results are identical for any count
};
let particles = vec![Particle { release: [96.5, -35.2], release_time: t_impact,
                                response: ObjectResponse { a_stokes: 1.0, c_wind: 0.02, leeway_angle_deg: 0.0 } }];
let out = integrate(&spec, &particles)?;   // Err(CompositionError) if a component would be double counted
// out.tracks[i].snapshots[k]: NotReleased | Afloat(LonLat) | Beached { at, segment } | Ended
// out.tracks[i].events: Beached { t, at, segment } | Refloated | LeftDomain | FieldGap { t, at, component, gap }
//                       | NonFinitePosition | ReleasedOnLand
// out.tracks[i].fate:   Afloat | Beached | LeftDomain | FieldGap | NonFinite | ReleasedOnLand
// out.provenance.ocean_model: the value of the `ocean-model` alternative for this run (product ids joined by "+")
```

- `v = u_current + a_stokes*u_stokes + c_wind*R(leeway_angle)*U10 + u_ocean_error + u_random_flight`, formed
  inside the integrator; a random-walk displacement is added after each step. `ObjectResponse` is fixed for the
  particle's whole life. `ObjectResponse::new(a_stokes, c_wind)` sets the leeway angle to 0, which is drift's
  request exactly; the angle (degrees, positive clockwise from downwind) is an addition, off by default.
- **Composition refusals:** a particle with `a_stokes != 0` and no Stokes field, or `c_wind != 0` and no wind;
  Stokes with a current whose metadata says it contains Stokes (`Partial`/`Unknown` refused unless
  `accept_partial_stokes_overlap`, which is recorded in provenance); Stokes with `leeway_absorbs_stokes`.
- **One ocean per run.** `ocean_error` is realised once from `seed` and shared by every particle; diffusion is
  the only per-particle randomness (particle i uses its own random stream, so thread count never matters).
- **Pléiades:** 21 and 23 March come from one call with both in `output_times`.
- **Field gaps end a trajectory as themselves.** A gridded product's `Land` gap means stranded in the
  product's land mask before the coastline caught the particle; time outside a field's axis is
  `OutsideTime`, never clamped (the archive clamped).

### Settling: the profile query

```rust
use mh370_ocean::profile::{ProfileSource, BelowModelBottom, BottomRelation, DepthStatus, VerticalVelocity};
use mh370_ocean::analytic::UniformColumn;
use mh370_ocean::stochastic::{OceanErrorModel, ErrorKind, VerticalStructure};

let col  = UniformColumn::new(0.10, -0.05, None, vec![0.5, 10.0, 100.0, 1000.0, 3000.0], 4000.0); // w absent
let prof = col.profile(t, [lon, lat])?;          // Profile: depth_m, u_east, v_north, w_up, temperature,
                                                 // salinity, pressure_dbar, model_bottom_m, time_axis
match prof.bottom_relation(seabed_m) {           // WithinModel | SeabedDeeperThanModel { model_bottom_m, seabed_m, gap_m }
    _ => {}
}
let s = prof.at_depth(z_m, Some(seabed_m), BelowModelBottom::HoldDeepestLevel)?;
// s.u_east, s.v_north; s.w_up: Option<f64> (None when the product has none - never 0);
// s.status: Resolved | Extrapolated { rule, model_bottom_m, seabed_m }
// rules: Refuse | HoldDeepestLevel | LinearToZeroAtSeabed; Err(DepthGap) for AboveSurface, BelowSeabed, refused
let err = OceanErrorModel { kind: ErrorKind::Eddying { sigma_m_s: 0.05, length_scale_m: 50e3, time_scale_s: 5.0 * 86400.0, modes: 64 },
                            vertical: VerticalStructure::Exponential { efold_m: 500.0, deep_ratio: 0.3 } }
          .realise(impact_event_seed);           // one realisation per impact event, shared by its fragments
let e = err.velocity(t, [lon, lat], z_m);        // add it yourself: components stay separate
```

`w_up` is `VerticalVelocity::Absent | Present(Vec<f64>)` on the profile; the type has no way to say zero for
absent. Temperature keeps its product's kind (`Potential` or `InSitu`) for the TEOS-10 layer to convert once.
Pressure is Saunders (1981) until TEOS-10 lands (deliverable 8) — provisional.

### Products

`mh370_ocean::products::catalogue()` holds machine-readable records for GLORYS12V1, WAVERYS, OSCAR v2 Final,
BRAN2016 and ERA5 10 m wind: dataset id, credential, resolution, coverage, time axis, depth convention,
variables with units, and `Contents { geostrophic, ekman, stokes, tides, inertial }`. Findings worth your
attention:
- **BRAN2016 may not reach drift's period end.** CSIRO states it spans January 1994 to August 2016; drift
  needs 30 September 2016 (latest stringent find 23 June 2016, so a run ending in August loses only the
  tail). Marked `covers_drift_period: Partial` until the NCI catalogue is checked.
- **OSCAR v2 already contains the wind-driven term** (geostrophic + Ekman + thermal wind, averaged over the
  top 30 m; `ug`, `vg` are the geostrophic part). Never add a separate Ekman term to it.
- **GLORYS12V1 has no Stokes and no tides**; its daily mean attenuates near-inertial motion without removing
  it. Its multiyear daily dataset carries no vertical velocity, so settling will see `Absent`.
- **ERA5 `u10` is the actual wind, not the neutral wind `u10n`.** A fitted leeway must say which.
- The archive's 100 m²/s and CSIRO's 5 NM/day are not the same diffusion: 3.17 NM vs 5 NM RMS after one day
  (K = 100 vs 248 m²/s).

### Provisional, and what is not done

Throughput (deliverable 5) is **not measured**: the machine is at load ~40 under the core run and a number
taken now would be wrong. The real coastline and segmentation (6), bathymetry (7), TEOS-10 (8), drogued GDP
replay (9) and the product recommendation (10) are not started. Diffusion and ocean-error **parameter values
are not chosen**: the API exposes them; the defaults in my tests are test values. The ocean-error model's form
(one model for drift and settling, or two) is still the open question of brief §8. Beaching is tested at step
end points, which is exact for a straight coast; the real coastline will need sub-stepping at headlands.

— ocean transport (architecture sub-agent)
