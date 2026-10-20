# Core requests from the end-of-flight first increment

Raised 7 October by the end-of-flight module session against its first code increment, triaged
here by the architecture session. Nine items: six are code changes in core-owned files, one is held
back as not-yet-justified, and two are corrections to the end-of-flight master prompt rather than
to any code.

The increment itself is **not merged**. It is `eof-dynamics.patch`, 9 files and 4,068 insertions,
all under `hypotheses/end-of-flight/`, with `make scope H=end-of-flight` passing and 57 of 57 tests
green in `mh370-hypotheses` against a 53-test baseline (8 of which were in that crate before).

## Triage

| # | owner | file | priority | what |
|---|---|---|---|---|
| 1 | core estimator / core stages | `crates/mh370/src/terminal.rs:396–416` | **blocker** | pass the fuel state through the hand-off |
| 2 | core stages | `crates/hypothesis/src/lib.rs`, `trait Terminal` | high | let `descend()` see what `takeover_time()` drew |
| 3 | core stages | `crates/hypothesis/src/lib.rs` | high | give the terminal module the core's fuel-flow model |
| 4 | core stages | `crates/hypothesis/src/lib.rs`, `ImpactView` | high | the ruled field additions, plus one more |
| 5 | core stages | `crates/mh370/src/terminal.rs:380` | medium | surface pressure altitude is hard-coded to zero |
| 6 | core stages | `config/integrated.toml` | medium | the module cannot be selected without a core-owned config |
| 7 | — | weather grid extent | **held** | correctly not yet a request |
| 8 | core estimator (`crates/satcom`) | — | **before the paper** | the 17.50 Hz attribution is disputed |
| 9 | architecture (done) | master prompt §11 | done | two test statements were loose by ~10% each |

## 1. The blocker: the hand-off carries no fuel state

`fn flight_state` hard-codes `mass_kg: f64::NAN`, `fuel_kg: f64::NAN` and
`fuel_exhaustion_unix_s: f64::NAN`, although `crates/flight` carries `Aircraft::fuel_kg`
(`lib.rs:229`) and `Aircraft::fuel_exhausted_unix_s` (`lib.rs:540`) and the fuel model is built.

Consequence, and it is the reason to treat everything in this increment as provisional: the
anticipatory and fuel-cue onset mechanisms have no predicted endurance to trigger on, and the
integrator has no wing loading. The module runs on configured fallbacks — 174,000 kg, 2,000 kg and
00:17:30 UTC — and flags each descent in a `mass_kg_assumed` latent.

**This also answers a question the architecture session left open.** We asked whether the hand-off
carries fuel state at adequate precision, so that flame-out time could be derived in the stage
rather than read from the 128-second-quantised `final.npy` column. The answer is that it carries no
fuel state at all. So the 128 s quantisation is not the binding problem; the missing hand-off field
is, and deriving the time in-stage is the right design once the field exists.

One requirement on the field, from the module and endorsed here: `fuel_exhaustion_unix_s` must be
the **predicted** exhaustion under continued cruise at the hand-off, not a realised value.
Triggering onset on a realised flame-out is circular and the brief forbids it. If the core cannot
predict forward at the hand-off, add a separate `predicted_exhaustion_unix_s` and make the two
names say which is which.

## 2. `descend()` cannot see what `takeover_time()` drew

The two hooks have separate uniform streams, so the onset mechanism and the support-truncation
fraction drawn in `takeover_time` are unavailable in `descend`. The module recovers the mechanism
exactly from the conditional posterior p(mechanism | onset lead) — correct, and verified to within
3 percentage points over 90,000 draws — but it costs a density evaluation per descent, and the
truncation fraction cannot be recovered at all. That latent is therefore NaN, which means **the
checkpoint-boundary diagnostic is computed and tested inside `onset.rs` but does not reach
`impacts.npy`.** That diagnostic is the thing that tells us whether the 22:41 boundary is
influencing the answer, so this is not cosmetic.

Either pass `takeover_time`'s return value (or a module-defined latent vector) into `descend`, or
merge the two hooks. Architecture prefers passing the value: merging the hooks would couple two
concerns that are currently separable.

Also in the same request, and accepted: the trait doc comment and the `impacts.npy` column call
`takeover_time` "the first flame-out". Under an anticipatory or fuel-cue onset the takeover is the
descent **onset** and is earlier than any flame-out. Redocument it as the module takeover time.

## 3. A hypothesis cannot reach the fuel tables — and §5 depends on it

A hypothesis may depend only on `hypothesis`, `geo`, `serde` and `toml`, so it cannot read
`data/fuel-tables.json` or call `crates/flight`. The module therefore burns fuel through a swept
TSFC of 1.4×10⁻⁵ to 1.8×10⁻⁵ kg/(N·s) while the cruise burn uses Boeing-calibrated tables.

**This is a genuine architectural conflict, not an inconvenience.** Section 5 of the end-of-flight
brief requires that a trajectory which fitted 00:11 under cruise assumptions be *re-scored, not
extended* — and that cannot be done honestly while the descent burn and the cruise burn come from
different models. Architecture endorses the module's proposed fix because it preserves the
dependency restriction rather than weakening it: expose the flow model behind a trait the runner
implements, exactly as the runner already does for `Atmosphere` —
`fn fuel_flow_kg_h(&self, flight_level: f64, weight_t: f64, mach: f64) -> Option<f64>`.

Note for whoever implements it: the core's own flow lookup returns `None` in cases that have just
been shown to matter (`results/fuel-burn-gap.md`), so the trait's contract must say what a
terminal module is to do with `None`. "Burn nothing" is the behaviour that caused that defect and
must not be the documented answer.

## 4. `ImpactView` additions — confirms the freeze, with one addition

Confirmed missing, from this module's own attempt to emit them: attitude beyond
`flight_path_angle_deg` (bank and pitch at contact), the dissipation duration τ, a debris class, a
sink-versus-float flag, and **`realised_flameout_unix_s`**, which the architecture session's
proposed freeze did not list and should.

The first four match the ruled freeze. The fifth is new and belongs: with onset triggered on
*predicted* endurance, the realised flame-out is an output of the trajectory rather than an input
to it, and nothing downstream can recover it.

The module has implemented debris class and sink-versus-float as **latents**, always NaN, which
only its own impact hook can read — so hydroacoustics, settling and drift cannot see them. That is
the correct holding position and it is exactly what the request is for.

## 5. Every impact terminates at ISA sea level

`impl Atmosphere for Weather` hard-codes `surface_pressure_altitude_ft = 0.0`, although the
`hypothesis::Air` doc comment says it comes from ERA5 mean-sea-level pressure where the grid
carries it — and a descent ends there. A 10 hPa anomaly is about 280 ft, so the error is small but
it is a **systematic** bias on impact time and vertical speed, in the same direction everywhere.
Either wire the MSLP field in or change the doc comment to say the surface is ISA sea level. Do not
leave the code and the comment disagreeing.

## 6. The module cannot be selected without a core-owned config

Selecting it needs `[terminal] module = "end-of-flight"` plus a `[hypotheses.end-of-flight]` block
in a core-owned config. This is why the `Terminal` implementation is exercised by unit tests rather
than through the runner, which was the correct response to the scope rule rather than a shortcut.
`hypotheses/end-of-flight/run.toml` carries the parameter block ready to be lifted verbatim.

## 7. Held back, correctly

The weather grid stops at 43,000 ft and 02:00 UTC, and a free-dynamics phugoid from a high-speed
upset can climb above 43,000 ft. The module records `max_altitude_ft` and carries the runner's
`Air::clamped` flag into a `weather_clamped` latent rather than hiding it, but **no run has been
made, so there is no measured rate of clamped descents to justify the cost of a larger grid.**
That is the right way to raise a request that is not yet justified, and it stays held until there
is a number.

## 8. The 17.50 Hz attribution is disputed — core estimator to settle

Two computations disagree about which arc the figure belongs to, by 1.8%, and the disagreement is
about attribution rather than physics.

- Previously recorded in this project: 17.50 Hz per 1,000 ft/min **at the 00:11 geometry**
  (38.16°S 88°E, satellite elevation 38.8°).
- Computed by the end-of-flight session from `data/satellite-ephemeris.csv` with the engine's own
  `UPLINK_HZ` and `SPEED_OF_LIGHT_KM_S`: **17.81 at the 00:11 arc** (BTO 18,040 µs) and **17.52 at
  the 00:19a arc** (BTO 18,400 µs), nearly constant along each arc — 17.800–17.813 from 30°S to
  40°S at 00:11, 17.515–17.528 at 00:19a — because the BTO fixes the slant range and hence the
  elevation angle.

The architecture session is not adjudicating this: `crates/satcom` is core-owned and the core
session settles it. Until then the master prompt quotes the range 17.5–17.8 and cites neither
attribution. The §7 argument is unaffected in substance — a ±20 Hz excursion matches 1,123 ft/min
at 00:11 against 1,143 at 00:19 — but the figure is heading for the paper and the attribution must
be right before it gets there.

## 9. Two test statements in the brief were loose — corrected

Both already fixed in `threads/master-prompts/end-of-flight.md` §11, recorded here because they
must reach the paper's methods in these terms rather than being quietly right in the code.

- **Phugoid period.** Lanchester's π√2·V/g assumes constant density. Under the ISA gradient the
  same equations give a period about 10% shorter, because climbing into thinner air removes lift
  and stiffens the oscillation. Test the closed form under a frozen atmosphere; record the ISA
  figure (81.8 s in this configuration) separately.
- **Still-air glide distance.** `altitude × L/D` is exact only in the energy-height form
  `R = (L/D)(E₀ − E_f)` with `E = h + V²/2g`. From 35,000 ft the altitude term is 93.7 NM and the
  kinetic energy traded into denser air adds 9.7 NM, for 103.4 NM.

Asserting either as first written would have asserted a ten per cent error.

## What the increment does not contain, carried forward verbatim

The module's own declaration, which travels with every number from it: **no evidential run has been
made.** There is one smoke-scale code-path run (`runs/smoke-end-of-flight`, seeds 1–2) whose
terminal module was still `arc-kernel` — confirmed from `run.json` — so its `impacts.npy` carries
nothing from this model, and whose ESS lines are the core filter's own diagnostics. There is no
impact PDF, no impact area, no energy distribution, no split-half agreement and no V1/V2
comparison.

Three substitutions and omissions to carry with the aerodynamic model:

- the **Poll–Schumann coefficient set was not used** — the polar has PS *form* with its constants
  pinned to the PS-derived calibration targets the brief quotes (clean (L/D)max 20.8–21.4 at 174 t),
  because `pycontrails`' `ps_model` and the `ps_*.py` scripts are not in the tree. Replacing it is
  a one-file change;
- the **NASA Common Research Model shaping was not used** — Lock's fourth-power law stands in with
  a swept coefficient, labelled extrapolated, with time above the crest Mach recorded per descent;
- **calibration against the ten Boeing engineering-simulator runs was not done** — that data is not
  in the tree, so deliverable 1 of §10 does not yet exist.

The baseline itself needed a substitution: 10 of 53 tests failed on the gitignored
`data/fuel-tables.json`, which the source bundle does not contain, and the session restored it and
the two `.bin` weather grids from the `engine-data.tar.gz` artifact to get a green baseline. That is
a provisioning gap in how the tree was handed over, not a defect in the engine.
