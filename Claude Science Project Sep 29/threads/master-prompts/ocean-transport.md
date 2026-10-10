# Shared ocean transport — mission and master prompt

**Status.** Written 8 October 2026 by the architecture session **from the interface requests the
consumers filed** in `coordination/OCEAN_TRANSPORT.md` — settling and drift in full, hydroacoustics and
Pléiades through their inboxes — rather than from first principles. That was deliberate: the brief was
held until the consumers could say precisely what they need. Read those requests in full before
designing anything; this brief summarises them and rules where they conflict, it does not replace them.

**Authority.** This file, plus `ISO Sept 28 Status/threads/master-prompts/common.txt` (shared contract
and eight composition rules) and `Claude Science Project Sep 29/ARCHITECTURE.md` (decision 4 created
this module). There is no ISO predecessor brief; the old drift brief's "Part A" is the closest ancestor
and it is superseded.

**Module location.** `crates/ocean`. Branch `core/ocean-transport`, cut from `claude-science-sep29`. You
are not an impact-level module: you return no likelihood. You are the shared environment that four
modules compute through.

---

## 1. Mission

Own the project's ocean: field access, the forward particle integrator, coastline and beaching,
bathymetry, thermodynamics, product metadata, and the ocean-error model. Do it **once**, so that no
consumer's assumptions become the project's ocean model by default and no result can come from an
ocean nobody can identify.

### Why a third owner

All of settling, drift and Pléiades consume ocean transport, and hydroacoustics and searched areas
consume bathymetry. A crate owned by one consumer acquires that consumer's assumptions. That is the
whole of ARCHITECTURE decision 4.

### The expertise this module is expected to bring

World-class knowledge of ocean reanalysis products and their skill in the Southern Indian Ocean,
Lagrangian particle-tracking practice and its numerics, surface-drift physics (Ekman, Stokes, windage,
inertial motion), drifter-based validation, bathymetric data products and their provenance, and TEOS-10.
Work from the literature that defines world-class practice rather than from this project's prior code;
weight most heavily the drift and search cases where ground truth later became available; review the
prior work on this case critically; and know Bayesian methods well enough to see why the ocean must be a
declared alternative rather than a fixed input.

---

## 2. What the consumers need — summarised, see the requests for detail

| consumer | call | key requirements |
|---|---|---|
| **Ocean drift** | batch forward integrator, up to 730 days | release position/time per particle; **persistent per-particle object response** (`a_stokes`, `c_wind`), never redrawn per step; velocity components reach the integrator **separately**; beaching with coast-segment ID and time; positions at caller-chosen output times; leaving-domain and NaN events flagged |
| **Ocean settling** | **profile query** at (lon, lat, t): current, T, S, p on product levels from surface to local bottom | geographic ENU m/s; **vertical velocity flagged present/absent, never silently zero**; depth convention stated; bathymetry-deeper-than-model-bottom a **flagged, testable condition**; a declared, variable model for unresolved deep motion; sub-daily or explicitly daily time axis |
| **Pléiades** | same integrator as drift | object positions on 21 and 23 March 2014 from different output times of the same call |
| **Hydroacoustics** | bathymetry along great-circle paths of 1,600 to ~8,500 km to H01, H08, H11; TEOS-10 sound speed | GEBCO resolution along path is enough; AusSeabed near source |
| **Searched areas** | bathymetry for terrain masking | per-cell provenance |

---

## 3. Rulings already made — binding

1. **Velocity components are never pre-summed.**
   `v = u_current + a_stokes · u_stokes + c_wind · U10 + diffusion`.
2. **Every product declares what its "current" already contains** — Ekman, Stokes, tides, inertial —
   as machine-readable metadata, so a consumer can refuse a composition that counts a component twice.
   OSCAR v2 carries a wind-driven term; an empirically fitted leeway may already absorb Stokes
   (arXiv:2005.09527).
3. **Diffusion is a declared, variable model.** The archive used 100 m²/s, CSIRO a 5 NM/day random walk;
   neither was tested. Expose it, and state whether it is applied per step or per field cell.
4. **One coherent ocean-error realisation per run** across all particles, and per impact event for
   settling's fragments. Every recovered object travelled through the same ocean; independent error per
   particle lets each object choose its own ocean.
5. **Renormalise across land, never fill with zero.**
6. **Coastline keeps Réunion, Mauritius and Rodrigues.** The 1:110m mask dropped Réunion, where the
   first confirmed piece was found. Segment IDs on a segmentation the drift evidence table can map onto.
   Refloat hook, off by default.
7. **The product is a run argument.** A run must repeat against a different product with no consumer
   code change. The alternative is declared as **`ocean-model`**, by exactly that name, shared across
   drift and Pléiades and marginalised jointly by the composer.
8. **Bathymetry is yours** (ruled 8 October; four consumers). Settling's specification is adopted: one
   surface, **AusSeabed 150 m inside its coverage, GEBCO_2026 outside, a per-cell provenance flag, and
   GEBCO's Type Identifier retained.**
9. **TEOS-10 is yours**, including the potential-versus-in-situ temperature conversion — GLORYS12V1
   reports potential temperature and HYCOM in-situ — and sound speed as one more output of the same
   evaluation.
10. **Validation split.** Drogued-drifter GDP replay tests fields and integrator: **yours**. Undrogued
    and windage comparisons test object response: drift's.

---

## 4. Products, and the model-selection question Pete has asked for advice on

Candidate products, from the drift brief: **GLORYS12 with WAVERYS** Stokes; **OSCAR v2 Final**,
observation-based; **BRAN2016** via NCI; **ERA5** 10 m wind. **Native HYCOM is dropped** — it ends July
2015 and performed worse in drifter replay. Drift's measurement sets the stakes: changing the current
product moved the drift mode 1.2°, while scaling Stokes by 0.5/1/1.5 moved it to 11.9/18.0/34.9°S.
**Object response dominates**; product choice is the smaller axis, but it is still a declared one.

**Pete's question, which you own:** the earlier Pléiades work used different transport products for
the local 15-day problem than the long drift used for 16 months. Is that defensible? Give him a written
recommendation in `results/` with the reasoning. The constraint you must satisfy whatever you recommend:
if two modules both depend on the ocean and are composed, they must declare the **same** `ocean-model`
alternative and be marginalised jointly — otherwise the ocean uncertainty is silently treated as resolved.

Credentials are configured: **`COPERNICUS`** (GLORYS12, WAVERYS) and **`NASA_EARTHDATA`** (OSCAR v2).
Declare them on the cells that use them; never print them. BRAN2016 via NCI OPeNDAP is anonymous.

---

## 5. Disk is the binding constraint — rules, not advice

The machine has **one** volume, at 96% full, **38 GiB free on 8 October** and falling while the core run
writes. Drift's estimate for surface fields alone over its full box and period is about 20 GB.

- **Data live in one place:** `/Users/pete/Downloads/mh370-ocean-data/`, a granted host path. Not in the
  repo, and **never saved as artifacts** — every artifact version is a full copy and would double the
  footprint.
- **Floor: never let free space fall below 25 GiB.** Check `df` before each file, not once per session.
- **Subset server-side** — the Copernicus Marine toolbox and OPeNDAP both support it. Store float32.
  Download the **pilot box and period first**, not the full domain.
- **Overnight ceiling on 8–9 October: 6 GiB in total.**
- Maintain `results/ocean-data-manifest.md`: product, version, variables, box, period, file sizes,
  sha256, download date, and what each consumer uses it for.

---

## 6. Deliverables, in order

1. **The API**, in `crates/ocean`, with the analytic fields drift and settling are already stubbing —
   uniform current, solid-body gyre, isotropic random walk of known RMS, straight-line coast — so the
   consumers' stubs can be deleted and swapped onto yours. **This unblocks three modules and comes
   first.**
2. **Tests:** constant-current analytic displacement and random-walk RMS — port the two from
   `transport_core.mjs` in the withdrawn Pléiades share — plus land renormalisation, beaching segment
   IDs, the vertical-velocity-absent flag, and the deeper-than-model-bottom flag.
3. **Product metadata** for each candidate product, as rule 2 above.
4. **One real product for the drift pilot box**, within the disk rules — GLORYS12 surface currents is
   the natural first.
5. **Throughput measurement**, reported to drift: the brief assumed 2 × 10⁷ field evaluations per second
   per core over 16 cores; drift's pilot exists partly to measure the achieved figure.
6. **The coastline and segmentation.**
7. **Bathymetry merge**, AusSeabed and GEBCO with provenance.
8. **TEOS-10 layer.**
9. **Drogued-drifter replay.**
10. **The product-selection recommendation** of §4.

---

## 7. Core boundary

`crates/ocean` is a new crate. Adding it to the workspace `Cargo.toml` members list is the one touch of
a core-owned file; raise it as a core request in `coordination/CORE_STAGES.md` and do not edit it
yourself. Until it lands, build and test with `cargo -p` from your branch with the member line present
on your branch only, and say so.

## 8. Open, needing the architecture session

- Whether sub-daily fields are worth their footprint for settling's slow-sinker tail.
- The ocean-error model's form — settling asked for a declared, variable model of unresolved deep motion;
  drift needs one coherent realisation per run. One model or two?


## Side questions (standing rule, Pete, 10 Oct 2026)

Pete, 10 Oct 2026: when he asks a side question, answer it and then go back at once to the work you were doing. If that work is complete, start the next item in your backlog. Do not end your turn after a side answer while you have work in progress or a backlog. End your turn only when the backlog is empty or every item is blocked on something you cannot do yourself. Before you end it, write here which items are blocked and on what. An approved run whose gates you can execute is not blocked: start it.
