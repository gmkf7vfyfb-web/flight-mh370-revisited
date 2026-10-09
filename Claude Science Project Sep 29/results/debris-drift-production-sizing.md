# Drift production sizing (sequence step 4), from the pilot and six diagnostics

Ocean drift module, 9 October 2026, ~10:45 UTC. Every run here is a **sizing run, not evidence**:
- the extent is the 295.66° prior's no-exhaustion map;
- there is one environment realisation per run;
- each run uses 16 to 22 nodes.

**Run provenance (convention of ~16:40 UTC):**
- **Diagnostics:** they reuse the pilot's configuration (base `config/davey2016.toml`) and extent
  (`no-exhaustion-prior`, prior track 295.66).
- **Production configs:** `production-<model>.toml`, base `config/davey2016.toml`. Their extent is
  re-pointed at core's `reference-289` (`run.json`: `config.name` = `reference-289`, `prior.track_deg` =
  289.7, `code_revision` = `4f6487a-dirty`; `a205d05`). On that extent the main band is 367 nodes at
  30 NM.

The pilot is in `results/debris-drift-pilot.md`. The production configs are
`engine/hypotheses/debris-drift/production-glorys12.toml` and `production-globcurrent.toml`, on
`hypothesis/debris-drift`. **They have not been run.** Step 6 waits for the final impact samples, and
any long run is announced before it starts.

## What the pilot left open

At 50 km no node resolved. Rodrigues had zero kernel hits at all 1,709 nodes, and Mossel Bay had
fewer than one effective particle at 76% of them.

## Why Rodrigues was zero: a structural zero, not rarity

On the GLORYS12 1/12° grid, Rodrigues is a single land cell. The shared field renormalises across land,
and it reports a land gap only when every corner of the interpolation stencil is land
(`crates/ocean/src/field.rs`). **A one-cell island can therefore never strand a particle.** No particle
count would have resolved it.

Two diagnostics confirm this:
- Importance splitting on entry within 150 km of Rodrigues (factor 20) raised Mauritius hits ~13×, but
  Rodrigues stayed at zero.
- With Rodrigues as an equal-area disc (108 km², r = 5.9 km; a stub, `bb1a8f6`), it scored a median of
  10 hits per node unsplit, and 207 with splitting and ocean error.

The shared GSHHG 2.3.7 full-resolution coastline (ocean transport deliverable 6, `4eba004`) has since
landed, with Rodrigues as its own ring. **Production uses it** (`transport.gshhg_path`, snap 25 km), and
the disc stub is no longer used.

## Diagnostics

- **Nodes:** 16 of the pilot's chunk-0 nodes, spread evenly in latitude from 40.7°S to 31.2°S, with the
  same seeds and response draws.
- **Particles:** 3,334 per class per node.
- **Common settings:** GLORYS12 + ERA5, K = 248 m²/s, at 2 threads beside core.
- **Ocean error ("oe"):** the shared eddying field with σ = 0.11 m/s, T = 8 d and L = 100 km.
- **Splitting "m20-r150":** Rodrigues and Mossel Bay at 150 km, factor 20, for the two non-flaperon
  classes.

Median kernel hits per node at 50 km, with the fraction of nodes at zero:

| find | pilot config | + split | + oe | + oe + split | disc | disc + oe + split | GSHHG + oe + split (Mossel 300 km) | GSHHG + oe + split (Mossel 500 km, ×100) |
|---|---|---|---|---|---|---|---|---|
| Réunion | 32 / 0% | 32 / 0% | 36 / 0% | 36 / 0% | 30 / 0% | 34 / 0% | 58 / 0% | |
| Mossel Bay | 0 / 75% | 3 / 44% | 0 / 62% | 4 / 6% | 0 / 75% | 4 / 6% | 2 / 25% | 3.5 / 19% |
| Paindane | 0 / 50% | 8 / 0% | 1 / 38% | 11 / 0% | 0 / 50% | 11 / 0% | 10 / 0% | |
| Vilanculos | 6 / 12% | 32 / 0% | 6 / 0% | 37 / 0% | 6 / 12% | 36 / 0% | 36 / 0% | |
| Mauritius | 42 / 0% | 532 / 0% | 60 / 0% | 810 / 0% | 42 / 0% | 771 / 0% | 1,156 / 0% | |
| Rodrigues | 0 / 100% | 0 / 100% | 0 / 100% | 0 / 100% | 10 / 0% | 207 / 0% | 225 / 0% | |
| Chidenguele | 10 / 0% | 62 / 0% | 8 / 0% | 60 / 0% | 10 / 0% | 59 / 0% | 76 / 0% | |
| Antsiraka | 127 / 0% | 1,349 / 0% | 94 / 0% | 955 / 0% | 124 / 0% | 914 / 0% | 1,001 / 0% | |
| Pemba | 62 / 0% | 124 / 0% | 30 / 0% | 84 / 0% | 62 / 0% | 80 / 0% | 112 / 0% | |
| **nodes resolved at 50 km** | 0% | 0% | 0% | 0% | 19% | **94%** | 75% | 81% |
| split-half noise SD of ln L (nodes) | - | - | - | - | - | 1.29 (8) | 2.29 (8) | 1.61 (8) |
| wall, 16 nodes, 2 threads | 220 s | 283 s | 400 s | 556 s | 208 s | 547 s | 512 s | 539 s |

The last column was run only to measure Mossel Bay; its other finds are left blank. The disc and
GSHHG runs differ at more than Rodrigues: GSHHG beaches on the real shore and turns off land-gap
beaching. That is why the island and Pemba arrival rates rise under it.

**A meridional transect** ran at 95.5°E, 22 nodes from 35.5 to 32.0°S at 10 NM, with the disc stub,
ocean error, and splitting (Mossel 300 km). It resolved every node at 50 km. Every find had hits at
every node; Mossel Bay's median was 28.
- Split-half noise SD of ln L at 10⁴ particles per node: **1.55** at 50 km (19 nodes with both halves)
  and 1.38 at 100 km.
- Noise-corrected semivariogram at 100 km: about 1-1.6 out to 120 NM, then 4.6 at 160 NM. Each estimate
  is uncertain by about ±1 with ~20 pairs.
- At 50 km a single marginal node (35.33°S, ln L −147.7, one half unresolved) dominates the variogram.
- So the surface changes by **at most ~2 ln units over ~100 NM**. The pilot measured the same, by its
  variogram nugget, at 100 and 200 km.

## What the diagnostics decide (module decisions, recorded; reversible)

1. **Coastline:** the shared GSHHG coastline, with land-mask strandings snapped within 25 km (transport's
   default). A land gap that remains is model error, not beaching (`land_gap_is_beaching = false`).
2. **Importance splitting** (`fbaad33`, `84b6f85`, `ec20f78`; unbiased, tested), for the
   low-exposure and high-windage classes:
   - Rodrigues: within 150 km, ×20.
   - Mossel Bay: within 500 km, ×100. This barely improves the southern nodes, where Mossel hits stay at
     0-5, because few particles from south of ~36°S reach the South African coast in the window.
     That is physics: the likelihood there is genuinely small. The Monte Carlo can bound it but not
     resolve it.
3. **Zero environment terms** (`ec20f78`):
   - A realisation whose product is zero enters the environment mean as zero, which is its unbiased
     estimate.
   - A node is Unresolved only when every realisation is zero.
   - The fraction of zero realisations is written per node (`zero_env_fraction`), so nothing is
     floored or hidden.
4. **Particles: 10⁵ per node,** as 4 environment realisations × 3 classes × 8,334. On the transect's
   noise, and assuming variance scales as 1/N, that gives a split-half SD of about 0.5 in ln L. This is
   the brief's "a fraction of a unit" target.
5. **Spacing: 30 NM**: 193 main-band nodes on the 295.66 extent (against 1,709 at 10 NM), and **367 on
   the reference-289 extent** that production uses (`a205d05`; 819 at 20 NM).
   - The correlation length is not resolved, but the change is at most ~2 ln units over ~100 NM, so
     linear interpolation in likelihood at 30 NM costs well under one unit.
   - The 5 NM refinement in step 6 covers the high-density region.
6. **Environment realisations:** each draws its own ocean-error field and its own K.
7. **Cost estimate:** 34 s per node at 10⁴ and 2 threads (diagnostic), so about 340 s per node at 10⁵.
   - That is about 1 min per node at 12 threads under the lock, if scaling is near-linear (unmeasured).
   - **About 6 h per ocean model and about 12 h for both on the 367 reference-289 nodes** (about 3 h
     and 6 h on the superseded 193), with the refinement on top.
   - This sits behind core's run, and it is announced before it starts.

## Choices taken under the overnight rule (PROVISIONAL-OVERNIGHT; for Pete in the morning)

- **Ocean-error length scale: 100 km, assumed.**
  - The replay measures σ and T per drifter, not a spatial scale.
  - It is asked of ocean transport, from GDP pair separations.
  - Sensitivities: 50 and 200 km.
- **Ocean-error amplitude and time scale per product,** from the replay's search-box, March-May,
  undrogued values:
  - GLORYS12 + 1% ERA5: σ 0.117 m/s, T 5.1 d.
  - GlobCurrent, run without wind in the replay (a declared approximation): σ 0.0885 m/s, T 10 d.
  - **Combination with K, not double-counted:** σ_eff² = σ² − K_ref/T, with K_ref = 248 m²/s. This gives
    0.1146 and 0.0869 m/s, so the single-particle spread at the reference K equals the replay's. K is
    4% of σ²T.
- **K prior:** log-uniform, 100-1,000 m²/s. It is the sub-mesoscale part only, one draw per environment
  realisation (ruling 4). The range spans the old code's 100 and CSIRO's 248.
- **Splitting settings:** as in item 2.
- **S6 box west edge moved from 39.3 to 39.45°E** in the production configs only, so the block is
  Pemba alone. Transport reported that the pilot box took in ~25 km of the Tanzanian mainland. The
  Pemba find is at 39.87°E.

## What production still does not have

- the final impact samples (core phase A, about 18:00 UTC 10 Oct);
- an ocean-error length scale that is measured rather than assumed;
- a separate leeway angle for the windage classes beyond their provisional N(0, 10°) and N(0, 15°)
  priors, now on `wind_angle_deg` (D-f landed, `07cced0`; adopted in `d126258`);
- the Western Australian non-recovery term and the 2014 surface-search observation (deferred).

- Ocean drift
