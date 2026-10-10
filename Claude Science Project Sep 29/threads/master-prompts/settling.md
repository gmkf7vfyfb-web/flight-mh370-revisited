# Settling — impact to seabed. Mission and master prompt

Supersedes `ISO Sept 28 Status/threads/master-prompts/settling.txt`, which remains correct on
physics, on the analogue survey and on the first-order scale argument, and is stale on build
status, on the old harness's `/jackbox/home` data paths, on thread identifiers, and on the data
sources. Read `ISO Sept 28 Status/threads/master-prompts/common.txt` first for the four-stage
architecture and the eight composition rules; they are unchanged and binding.

Split deliberately: **§2 is the contract and must not drift. §5 onward is the line of enquiry and
is expected to.** Pete will add prior work and change direction as this progresses; that is
anticipated and is not a conflict.

---

## 1. Mission

Transform each ocean-surface impact into **where its wreckage comes to rest on the seabed**, in
three dimensions: depth set by the ocean floor, horizontal translation integrated along the
descent path through currents that change with depth, position and time.

The module exists because the seabed search is evidence about *wreckage*, not about impact points.
Searched areas must be scored against a wreckage distribution, so this transform sits on the
critical path between end of flight and searched areas. Its map is also what a future seabed
search would plan from.

Act as an expert in the settling and translation of objects through deep water, drawing on the
best available research and on documented cases from aviation, maritime and other fields, from
first principles and current practice. Learn and apply the lessons of AF447 and the other analogue
cases in §8 — including the mistakes made there.

Factor in the **breakup scenarios and their effect on translation**: a largely intact fuselage at
one extreme and many small fragments at the other translate differently, and the difference is
expected to dominate the currents.

---

## 2. The contract — stable; changes need architecture review

1. **You are a transform, not a likelihood.** You return predictions, never a log-likelihood of
   your own. There is essentially no observed MH370 seabed debris to score; the one thing that
   could be scored — the search having found nothing — belongs to searched areas, and scoring it
   in both places would use one observation twice.
2. **Return likelihoods, never posteriors** applies to anything you do emit that enters a
   likelihood: remove any internal reference prior, and declare absolute scale.
3. **Each observation is used exactly once per run**, with declared IDs.
4. **Everything downstream consumes the same samples.** Never smooth privately over position: the
   product of separately smoothed likelihoods is not the smoothed product.
5. **Outputs are smooth, with explicit model error. No floors.** NaN means "not computed", not
   "impossible". Cover the prior's support or refuse.
6. **Be accurate where the other evidence has mass** — roughly 30–40°S along the 7th arc — not
   only near your own peak.
7. **Measure Monte Carlo adequacy and report unconverged as unconverged.** The fix is the sampler,
   never the smoothing. Use `skill("mh370-run-reporting")` for the conventions.
8. **Settle discrete choices by evidence, or carry them as declared alternatives with priors.**
   Never fixed-weight averages of normalised maps. Competing current products are a labelled
   sensitivity, never an average — see §7.
9. **Stop the settling calculation at first seabed contact.** Sliding, rolling, burial and later
   remobilisation are a separate step with their own uncertainty. This also separates the
   bottom-contact acoustic event from the resting place, which matters to two consumers.
10. **One coherent ocean-error realisation per event.** Nearby fragments from the same impact
    experience the same uncertain ocean, not independent random currents. Independent per-fragment
    noise would shrink the field artificially.
11. **One synthetic-recovery test plus hand-computed fixtures.**

### What you consume

`ImpactView` gives you: parent, time, position, ENU velocity, flight-path angle, mass, total and
vertical kinetic energy, descent family, takeover time/place/altitude, mode, alternative, module
latents, and — ruled in and newly added — **attitude at impact (at least heading and bank), the
dissipation duration τ, and a debris class**.

Granularity is settled: the impact sample carries a debris **class**, and *you* generate the object
ensemble from class plus energy and attitude. The impact sample is not variable-length, and end of
flight does not hand you a list of objects.

**Your first pass conditions breakup families on vertical and total kinetic energy plus flight-path
angle only.** Carry attitude and τ through as recorded-but-unused inputs. The reason is in §6 and
it is a measurement, not a preference. Revisit with a sensitivity test, not by assumption.

---

## 3. Build status

| thing | status |
|---|---|
| `ImpactView`, `impact_log_likelihood`, `predict`, `prediction_columns`, `mh370 evaluate` | **built** |
| The three `ImpactView` additions (attitude, τ, debris class) | **ruled in, not yet built** |
| A runner stage that stores a transform's output as samples | **not built** — the core request in §4 |
| Stage-4 composer | **specified** in `core-stages.txt` §D6, **not built**; `main.rs` rejects `[[compose]]`. Use `mh370 evaluate` on an impacts file meanwhile |
| Shared ocean transport (`crates/ocean`) | **not built**; owned by a separate session, and your dependency |
| Searched areas (`hypotheses/seabed-search`) | **not started**; rulings in `ISO Sept 28 Status/decisions/seabed-search-rulings.md` |
| Settling itself | **not started.** `ISO Sept 28 Status/code/uncommitted/settling-untracked.tar.gz` holds uncommitted work from the previous harness — inspect it before writing anything, it may save time |

---

## 4. How you plug in — ruled

**You emit wreckage samples, not summary columns.** Each impact sample fans out into N wreckage
samples, one per element draw, with the parent's weight **split** across them — creating more
descendants must never create more probability. This is the seabed analogue of the end-of-flight
hand-off, and the same weighting rules apply.

This needs a runner stage that calls you at a stage boundary and carries your output forward.
**That is a core request, not your work**: it belongs to the core stages & composer session,
because the code lives in `crates/mh370/src/`. Raise it in `core_requests` and send it to the
architecture session. You remain `hypotheses/settling`, with your own branch and your own session.
Nothing about this puts you inside another module.

Why samples rather than columns: searched areas' detection probability depends on the **extent and
piece sizes of the field**, not only on its centre. Compressing the field to mean offsets and a
spread throws away exactly the quantity it needs. `predict()` also gets no random stream, so the
column form would force you to run your Monte Carlo internally and hand back moments.

**The price, and the smoke test that sets it.** Sample count multiplies as impacts × element
classes × draws. Before committing to a draw count, measure **how many wreckage draws per impact
searched areas actually needs to resolve its coverage polygons** — agree that with the searched-
areas session through the architecture session. If the count proves unaffordable, the fallback is
the column form: `prediction_columns()` and `predict()` returning mean east and north offsets,
their spread or a few quantiles, and depth at rest, with Monte Carlo internal and seeded by the
sample so the result is deterministic. Keep that path working as a cheap diagnostic either way.

---

## 5. The model to start from

From the methodology Pete shared — input, not truth:

```
r_wreck = r_release + ∫ U(z(t), t) dt + ∫ v_rel,h(t) dt + Δr_seafloor
```

- `U` is the three-dimensional current field.
- `v_rel,h` is horizontal motion relative to the water from the element's own sinking, gliding or
  tumbling.
- `Δr_seafloor` is movement after seabed contact — excluded from the first pass by rule 9, but the
  term belongs in the formulation.

For each simulated element the environmental inputs are functions of longitude, latitude, **depth**
and time: horizontal current; temperature and salinity; pressure and seawater density; resolved
vertical current where available; an uncertainty model for unresolved motion; local seabed depth
and slope.

Variables to scope: water depth, bathymetry and slope at the resting place; current speed and shear
with depth; each element's mass, displaced volume, buoyancy, drag, projected area and orientation,
and hence terminal sinking speed; release time and position, including breakup over the water and
how long an element floats before sinking; glide and tumbling; seabed slope and sediment. Flooding
and pressure-induced structural change can alter these properties *during* descent.

---

## 6. Element classes, breakup families, and why sink rate comes first

Define your own small set in **one place**, so it can later become the shared breakup field without
rewriting the physics. That shared field is the same object as the `ImpactView` debris class, and it
will be frozen once settling, drift and hydroacoustics have each stated what they need from it.

At least these classes behave differently and must be separable:

- dense compact components (engines, landing gear);
- large flooded structural assemblies (wing box, centre section, fuselage sections);
- thin panels that can tumble or glide;
- initially buoyant sections that flood before sinking;
- debris that stays afloat and belongs to the surface-drift branch, not to you.

Breakup families span the extremes Pete named: low energy and largely intact, a ditching-like
contact, through to high energy and highly fragmented, a steep dive. The impact fields that select
between them are vertical and total kinetic energy and flight-path angle.

**Why sink rate before attitude.** At 4,000 m against a fixed 0.1 m/s net current, displacement
runs 0.2 km at 2 m/s, 0.8 km at 0.5 m/s, 8 km at 0.05 m/s and 40 km at 0.01 m/s — two orders of
magnitude from the sinking rate alone. The previous brief's own scale argument agrees: at 1–5 m/s
the descent takes 15–70 minutes and deep currents of a few cm/s move an element only a few hundred
metres, while slow sinkers and gliding or tumbling panels may move kilometres. **These are
sensitivity calculations, not estimates of MH370 sinking speeds or of measured regional currents.**
The consequence for ordering is firm: no precision in the current product compensates for an
unsupported sinking-rate assumption, so the first pass spends its complexity there, and attitude
enters later as a measured sensitivity.

---

## 7. Data — the source review, adopted

Adopted from the October source review Pete supplied. Treat the recommendations as implementation
choices, not as findings about accuracy.

**Bathymetry.** Geoscience Australia / AusSeabed MH370 survey inside its measured coverage — a
public 150 m compilation, downloadable without reprocessing the sonar records — with GEBCO_2026
outside it. Combine into one surface and **retain a provenance flag for every cell**; keep GEBCO's
Type Identifier grid, which distinguishes measured cells from interpolated ones. Fifteen arc-seconds
is grid spacing, not measurement density, and is roughly 400–460 m at these latitudes. Use the
surveyed data where it exists rather than averaging it with a coarser compilation that may already
contain the same measurements. Two distinctions matter: backscatter imagery is not a depth grid,
and seabed shape is a different input from the bathymetry that generated the modelled currents. The
regional survey shows ridges, escarpments, channels and mass-transport features
(`doi:10.1016/j.margeo.2017.10.014`), so a single assumed depth or a flat seabed is inadequate
across the candidate region.

**Currents, temperature and salinity.** Three products, compared rather than merged:

| product | coverage | role | qualification |
|---|---|---|---|
| Copernicus **GLORYS12V1** (`doi:10.48670/moi-00021`) | March 2014, ~1/12°, 50 depth levels, daily | baseline | daily means omit shorter-period motion; depth coordinates reach ~5,728 m but local model bathymetry masks deeper cells; potential temperature |
| **HYCOM GOFS 3.1 reanalysis expt 53.X** | 1994–2015, ~1/12°, 3-hourly, 40 depths | separate sensitivity case | archive gaps and documented deep-water problems need regional checks; **in-situ** temperature, not potential; 8 March 2014 is not on the published missing-day list, but verify the actual files |
| CSIRO/BoM **BRAN2020** | March 2014, 0.1°, 51 layers, daily | Australian-provenance comparison | output reaches ~4.5 km, insufficient alone for deeper candidate locations |

**Run HYCOM separately through the same sinking scenarios. Do not average the current fields** —
their disagreement is useful evidence of model sensitivity, and averaging would conceal opposing
flows. It is not a complete uncertainty estimate either, since both assimilate overlapping
observations.

**Observational checks**, none of them fully independent where already assimilated: Argo profiles
and trajectories, remembering that conventional Argo mostly observes the upper 2,000 m and is not
comprehensive at 4–6 km; GO-SHIP/WOCE full-depth hydrography, with the 2016 I08S section near 95°E
the most relevant, which constrains regional deep structure but cannot reproduce conditions two
years earlier; and NOAA World Ocean Atlas 2023 for depth-resolved climatology and fallback
thermodynamic profiles, which supplies neither the day's eddies nor a current reconstruction.

**Three additions the old brief lacked.**

- **Tides.** Daily means do not resolve the tidal cycle. TPXO gives harmonic elevations and
  transports reconstructable for the actual date — **check first that the chosen product does not
  already contain that contribution**, or it will be double-counted. These are barotropic,
  depth-averaged tides, not depth-dependent internal tides.
- **Unresolved deep and near-bottom motion.** Internal waves, topographically steered flow and the
  bottom boundary layer are not represented by an 8–11 km horizontal grid, and interpolating that
  grid onto 150 m bathymetry does not create the missing physics. A detailed seabed cell can be
  *deeper than the ocean model's local bottom*: flag that case and test explicit extrapolation
  assumptions. **Never silently substitute zero** for a missing current — that systematically
  shortens displacement.
- **TEOS-10** for all conversions, handling potential versus in-situ temperature consistently. This
  also yields sound-speed profiles, which hydroacoustics needs, so treat it as a cross-module
  deliverable and tell the architecture session when it exists.

Cache a regional environmental subset rather than reading the global fields repeatedly: 7–10 March
2014 initially, extended for delayed-flooding and slow-sinking scenarios, with a spatial buffer
around the full impact posterior. Precompute descent results over representative locations and
object classes, falling back to direct integration where interpolation is unreliable.

**Provisioning is not yet done and is a blocker, not a detail.** The previous harness's paths are
gone. Bathymetry and the reanalyses must be provisioned here, and the earlier drift work may have
retained surface levels only — you need depth levels. Raise this with the shared ocean transport
session through the architecture session before downloading anything large.

---

## 8. Calibration and defensibility — the standard Pete set

There will be no perfect calibration. The standard is therefore: review the literature and the
science, **recommend assumptions defensible to someone familiar with the field**, state them
explicitly, and report sensitivity across those assumptions and across the uncertainty. Educated
estimates are acceptable when declared as such. An undeclared one is not.

That is also what satisfies rule 8: labelled sensitivities, never a fixed-weight average.

**The analogue survey**, as source data and code comments plus a small CSV of cases with their
sources in your module directory — not as a markdown report (§12). Cite primary sources.

- **AF447 (2009).** BEA final report (July 2012) with its account of the search phases, and Stone
  et al. (2014), "Search for the wreckage of Air France Flight AF 447", *Statistical Science*
  29(1):69–80 — the Bayesian analysis that led to the find. The main wreckage lay about 6.5 NM from
  the last transmitted position, with seabed debris concentrated in roughly 600 m × 200 m at about
  3,900 m. Check two lessons against the sources rather than inheriting them: the 6.5 NM **includes
  flight after the last transmitted position**, so it is not sinking drift; and the earlier phases
  failed partly through over-trusting reverse drift and assuming the underwater beacons had worked
  — which is exactly why the searched-areas module carries an undetectable-wreck probability ρ.
- **Other deep-water aircraft wreck fields**, recording for each the depth, the impact type where
  known, the size of the wreck field, and the distance between surface debris and seabed wreckage
  where known: SAA295 (1987, Indian Ocean, ~4,400 m), Air India 182 (1985, ~2,000 m), EgyptAir 804
  (2016, ~3,000 m), Adam Air 574 (2007), Flash Airlines 604 (2004), Yemenia 626 (2009).
- **Non-aircraft cases**: MV Derbyshire (1980, ~4,200 m, well-surveyed debris field), Titanic
  (3,800 m, bow and stern at rest apart), El Faro (2015, ~4,600 m), the submarines Thresher and
  Scorpion, and the two nineteenth-century shipwrecks the MH370 seabed search found inside its own
  search area.
- **Models**: the naval mine fall-through-water models (NPS IMPACT25/28/35; Chu and Fan);
  falling-plate dynamics, fluttering and tumbling (Andersen, Pesavento and Wang 2005; Field et al.
  1997); and the offshore *dropped object* literature, which models trajectories and landing
  envelopes from hydrodynamic forces, orientation and currents — a useful methodological analogue
  whose coefficients for pipes and cylinders **cannot be transferred to aircraft sections**.

---

## 9. Sampling and uncertainty

Keep the uncertainty contributions **separate and separately reportable**: object behaviour, the
current product, unresolved flow, and bathymetry. A single pooled error bar hides which of them is
worth reducing.

Weighting rules are not optional: a parent's weight is split across its descendants; correct for
any deliberately oversampled class or interval; retain family evidence *before* normalising any
within-family map; and preserve parameters shared with the common history. Equal Monte Carlo
allocation across element classes is a **computational** choice, not a statement of equal prior
probability — say which is which.

---

## 10. Deliverables, in order

1. A short plan, as your first reply.
2. Inspection of `settling-untracked.tar.gz` — report what is reusable before writing new code.
3. The analogue survey and the model survey, as source data and comments, with the cases CSV.
4. First-pass physics in `hypotheses/settling/`: element classes and breakup families; sinking with
   drag and buoyancy; glide and tumbling as bounded lateral motion with stated uncertainty;
   currents by depth; seabed contact and slope. The `lib.rs` doc comment states every assumption
   and its source.
5. The tests of §11.
6. A report page — PNG with the PDF alongside: resting-offset distributions by element class and
   family at representative 7th-arc depths, and **how much each variable matters**: sinking rate,
   currents, glide, release time, current product.
7. `core_requests` in `hypothesis.toml` — at minimum the runner stage of §4 — and a message to the
   architecture session when the branch is ready for review.

## 11. Tests

A hand-computed terminal velocity. A limiting case: no current and no glide lands the element
directly below the release point. A closed-form check in a simple case — uniform current, constant
sinking speed. One synthetic-recovery test: generate the data from a known impact and element set
and check coverage. Plus hand-computed fixtures.

## 12. Scope and reporting rules, from `engine/AGENTS.md`

Not advisory. `make scope H=settling` fails if the branch touches anything outside
`hypotheses/settling/` and must pass before you hand back: no core crates, no `config/`, no
`report/`, no `README.md` or `status.md`. Changing the hook API in `crates/hypothesis` is a core
change. Iterate with `make smoke H=settling`, about a minute; **`make hypothesis H=settling` runs
at full scale** and is not a smoke test. Wrap anything expected to exceed ~10 minutes or ~4 GB in
`lockf -k /tmp/.mh370-heavy.lock <command>` so heavy jobs queue instead of competing.

Write **no new `.md` files inside `engine/`** — that tree allows exactly three. Assumptions and
sources go in the `lib.rs` doc comment; status goes in `hypothesis.toml` as a `status` field plus a
one-line `summary` quoting the numbers; longer write-ups go to the project's `results/` directory,
a sibling of `engine/`.

## 13. Deferred, by decision — and to be raised again

- **An implosion event at depth.** Trapped air in a sinking section can implode under pressure, and
  the ARA San Juan implosion (2017) was detected by CTBTO hydrophones, so such an event is
  detectable at range. Deferred to keep the first pass simple. It is architecturally interesting
  because the sink time puts it **tens of minutes after the 7th arc** rather than at it, which is a
  timing signature nothing else in the evidence set provides. When it arrives it is a *predicted
  event* — time, depth, position, energy class, with explicit model error — and the acoustics stay
  entirely with the hydroacoustics module. The sink-time integration is being computed anyway, so
  the marginal cost is small.
- **Sink-versus-float prediction** as a secondary input to drift and recovered-debris analysis.
  Deferred; build the hook. It is the natural output of the same element-class physics.
- **The shared breakup field.** Your provisional set becomes it, once drift and hydroacoustics have
  stated their requirements.
- **Post-contact movement** — sliding, rolling, burial, remobilisation. Rule 9.

**The first two are to be put back in front of Pete once a stable first pass exists.** That is an
instruction: he asked to be reminded, not to have them quietly dropped.

## 14. Open, needing the architecture session

1. The runner stage of §4, including how many wreckage draws per impact searched areas needs.
2. The freeze of the shared breakup field, once three consumers have stated requirements.
3. Provisioning of bathymetry and full-depth reanalyses, with the shared ocean transport session.
4. Whether TEOS-10 sound-speed profiles are emitted here for hydroacoustics or built there.


## Side questions (standing rule, Pete, 10 Oct 2026)

Pete, 10 Oct 2026: when he asks a side question, answer it and then go back at once to the work you were doing. If that work is complete, start the next item in your backlog. Do not end your turn after a side answer while you have work in progress or a backlog. End your turn only when the backlog is empty or every item is blocked on something you cannot do yourself. Before you end it, write here which items are blocked and on what. An approved run whose gates you can execute is not blocked: start it.
