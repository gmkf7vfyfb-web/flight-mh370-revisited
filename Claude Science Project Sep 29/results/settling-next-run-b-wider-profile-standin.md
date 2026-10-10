# Ocean settling on the wider GLORYS12V1 profile column, core (b) impacts — stand-in STOPPED as superseded

**Labels:** `UNCONVERGED` (core (b) split-half NOT converged) · two-tank bookkeeping only · PROVISIONAL-OVERNIGHT · run by an architecture stand-in on settling's behalf; settling to review.

## Status: the full re-run was not done. Ocean settling did it first.

The stand-in prepared settling's own recipe, using the wider ocean column of ocean transport (75–115° E, 45–10° S; 2f23c39). It then waited for the heavy lock from 20:10 to about 21:50 UTC. Over that time two entries were posted:
- **Ocean settling (~21:50 UTC, `coordination/OCEAN_SETTLING.md`)** published `results/settling-core-set-next-run-b/`. That result is the same item done to the newer rulings: the five core options, `unpowered`, both the fixed and the re-weighted P(family) mixtures, two footnotes, and the widened window (`hypothesis/settling` 5b595bf). The module wrote that the stand-in "can be stopped".
- **Pete's heavy-lock ruling (15:40 -0600)** puts the run C chain first on the lock tonight.

The stand-in therefore **stopped while it was still waiting**. It never acquired the heavy lock, it started no settling pass at scale, and it wrote **no element files and no `-wider` wreckage-sample file**. The task's per-option change table and the `-wider` sample file are **not delivered**. **Use settling's own result** (`results/settling-core-set-next-run-b/`; samples by settling's convention under `mh370-exchange/settling/`).

What the stand-in did finish is cheap and does not depend on the lock. It is recorded below, because it answers part of the brief directly and adds an independent check of settling's result.

## 1. Reproduction of the inputs (exact)

- The impact resamples (settling's unchanged `wreckage_field_prep_keys.py`; set A `none__other` 50,000 per seed, Generator 20261010; set B 10,000 per seed, Generator 20261011) **reproduce the previous stand-in's `A_impacts.f64` / `B_impacts.f64` sha256 in all 8 cases** (4 strata × A, B; see `settling-next-run-b-standin/SHA256SUMS-field.txt`).
- The pooled impact ESS also agree. For example, Held Out ESS is 12,337,220 / 12,339,414 / 12,336,817 / 12,325,581 for free / Davey dynamics + radar / descent-climb / routes.
- The mixture sub-sample counts with core (b) P(family) held fixed are 200,000 / 43,955 / 39,609 / 4,289 (Held Out) and 40,000 / 8,791 / 7,922 / 858 (R600). These are identical to the previous stand-in's counts.

## 2. Smoke: old against wider ocean inputs (settling 9823b4e, run.toml diff only)

`run-toml-wider.diff` changes three input lines only: `column_manifest` → the 75–115 E, 45–10 S column, and `bathymetry_window` and `fields_window` → [75, 115, −45, −10]. On 300 impacts from routes set A (200 random interior impacts between 25–40° S and 85–108° E, plus the first 100 rows north of 18° S, of which 43 were found), at 2 threads:
- **Interior: bit-identical** (12,970 element rows, `tobytes()` equal).
- **North of 18° S:** the old inputs return every one of the 43 as not computed (fate −1). The wider inputs compute 39 of the 43 (2,086 settled and 364 afloat element rows). The 4 that remain lie north of 10° S, the new limit (the northernmost impact in this set is at 7.78° S).

This agrees with settling's own check (998 of 1,000 in-window impacts bit-identical; 26 of 36 previously excluded impacts now settle). A smoke of 300 impacts does not show the 2 non-identical in-window impacts. They are probably near the old edge, where a floating piece could leave the old field window. That is not verified.

## 3. Weight share of impacts outside the old window, now inside the new one (exact, full posterior weights)

Share of the option-posterior weight (in %, seed mean) of impacts outside 80–112° E × 45–18° S (the old run.toml window), and outside 75–115° E × 45–10° S (the new one). In brackets: the number of impacts with non-zero weight, summed over 4 seeds. The impact position is used as the test; floating pieces that leave the window are not in these figures. The mixture uses core (b) P(family) 0.6948 / 0.1527 / 0.1376 / 0.0149, **held fixed, UNCONVERGED**. Script and JSON: `settling-next-run-b-wider-profile-standin/window_share.{py,json}`.

| 00:19 option | constraint | free: old → new window, % (impacts) | Davey dynamics + radar | descent-climb | routes | fixed-weight mixture, % |
|---|---|---|---|---|---|---|
| 00:19 Held Out | +alive | 0.0110 → 0.0043 (1,223 → 477) | 0.0373 → 0.0000 (4,224 → 0) | 0.0170 → 0.0002 (1,904 → 26) | 0.0223 → 0.0010 (2,529 → 114) | 0.0160 → 0.0030 |
| 00:19 Held Out | plain | 0.0104 → 0.0043 (1,310 → 544) | 0.0350 → 0.0000 (4,476 → 0) | 0.0155 → 0.0002 (1,936 → 32) | 0.0218 → 0.0010 (2,783 → 121) | 0.0150 → 0.0030 |
| 00:19 R600 BTO Only | +alive | 0.0032 → 0.0003 (1,223 → 477) | 0.0638 → 0.0000 (4,224 → 0) | 0.0027 → 0.0000 (1,904 → 26) | 0.0182 → 0.0004 (2,529 → 114) | 0.0126 → 0.0002 |
| 00:19 R600 BTO Only | plain | 0.0032 → 0.0003 (1,224 → 477) | 0.0638 → 0.0000 (4,229 → 0) | 0.0027 → 0.0000 (1,905 → 27) | 0.0182 → 0.0004 (2,535 → 114) | 0.0126 → 0.0002 |
| 00:19 R600 BTO + Raw BFO | +alive | 0.0063 → 0.0046 (1,221 → 476) | 0.0760 → 0.0000 (4,208 → 0) | 0.0025 → 0.0000 (1,904 → 26) | 0.0138 → 0.0004 (2,515 → 114) | 0.0165 → 0.0032 |
| 00:19 R600 BTO + Raw BFO | plain | 0.0063 → 0.0046 (1,221 → 476) | 0.0760 → 0.0000 (4,208 → 0) | 0.0025 → 0.0000 (1,904 → 26) | 0.0138 → 0.0004 (2,515 → 114) | 0.0165 → 0.0032 |
| R600 BTO + Raw BFO, fuel-exhaustion log-on (previous stand-in's option (b); reproduction only) | +alive | 0.0029 → 0.0003 (653 → 370) | 0.0471 → 0.0000 (693 → 0) | 0.0015 → 0.0000 (86 → 3) | 0.0062 → 0.0002 (892 → 24) | 0.0095 → 0.0002 |
| R600 BTO + Raw BFO, fuel-exhaustion log-on (previous stand-in's option (b); reproduction only) | plain | 0.0029 → 0.0003 (653 → 370) | 0.0471 → 0.0000 (693 → 0) | 0.0015 → 0.0000 (86 → 3) | 0.0062 → 0.0002 (892 → 24) | 0.0095 → 0.0002 |

**Reading.** The wider column brings in 80–100 % of the weight that the old window excluded. What remains outside lies north of 10° S, mainly in the free stratum (0.0043 % under Held Out). In the mixture the excluded weight falls from 0.013–0.017 % to 0.0002–0.003 %. In single strata the old exclusion reached 0.076 % (Davey dynamics + radar under R600 BTO + Raw BFO). The previous stand-in's resampled counts (up to 0.048 % in an estimable panel) and settling's correction (0.02–0.04 % of impact mass outside the old renderer grid) are the same effect. The effect on any 90 % or 99 % area is therefore expected to be well below the Monte Carlo noise of core (b), which is 6–16 % between seed halves (settling ~21:50). Settling's published areas confirm this. This stand-in did not measure it.

## COVERAGE (Pete's rule, 15:45 -0600)

These are the input gaps that every number above inherits. **No option or family is dropped.** A low ESS is reported as a coverage gap.
- **Core free stratum unconverged:** core (b) split-half 0.71–0.88 against 0.896. P(family) and every mixture share are UNCONVERGED.
- **End-of-flight reach:** commanded descent rates capped at 6,500 ft/min (Track); free flight cannot unload (point mass, dive class (b), PROVISIONAL); family B (deliberate descent before fuel exhaustion) onset not yet sampled as its own family. These gaps **bias against rapid descents**. They do not move impacts across 18° S in any obvious way, but this has not been checked.
- **Holland H1 / H2: not yet estimable.** The pooled impact ESS per stratum is free / Davey dynamics + radar / descent-climb / routes: H1 50 / 34 / 125 / 46; H2 67 / 64 / 106 / 73 (set B prep, identical to the previous stand-in). This is a coverage gap of end of flight's descent proposal, **not** evidence against H1/H2. No field was computed for them.
- **ESS of the options reported** (pooled over 4 seeds, plain): Held Out 12.3 M in every stratum; R600 BTO Only 7,451,904 / 6,344,202 / 7,289,576 / 6,949,043 (routes / Davey dynamics + radar / descent-climb / free); R600 BTO + Raw BFO 272,778 / 224,950 / 341,483 / 234,529 (same order). All are estimable.
- **Region:** in the new band (outside the old window and inside the new one), the non-zero-weight impact counts in §3 (for example 4,224 under Held Out `+alive` in Davey dynamics + radar) carry 0.00–0.08 % of the weight. **The band is thinly sampled in weight and must not be read as a separate posterior.** The region ESS was not computed (the post-processing that held it did not run).
- **Ocean:** GLORYS12V1 daily means at label + 12 h, PROVISIONAL (ocean transport). The search evidence is not applied.

## Deviations (declared)

1. **The task was stopped before the settling pass at scale.** The reasons are that the module published the same item first and that the lock priority ruling puts the run C chain first. No change table per option, no `-wider` sample file and no charts. The brief's main deliverables are **not delivered**.
2. One stand-in script outside settling's recipe: `window_share.py` (read-only, 2 threads).
3. The smoke covered 300 impacts of routes set A only. It is provisional as a check of bit-identity. Settling's own 1,000-impact check is the reference.
4. The plan, which did not run, would have used the 00:19-re-weighted P(family) from `summary/family-evidence-next-run-b.json` beside the fixed weights. It also would have reconstructed the old element files by splicing an old-build pass on boundary rows, for an exact sha256 match to the previous stand-in. Settling's result already provides the re-weighted mixture.

— Modular Architecture (stand-in for Ocean Settling)
