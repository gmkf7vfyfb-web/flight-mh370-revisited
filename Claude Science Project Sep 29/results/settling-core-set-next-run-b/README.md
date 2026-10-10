# Where the wreckage is on the seabed, for each use of the 00:19 satellite data (core run (b))

Ocean settling, 10 Oct 2026. This is settling's standard result on end of flight's next-run impacts (core (b)), rebuilt to the
rulings of today:
- the core 00:19 option set and its plain names (~16:30 UTC);
- the chart language, with two short footnotes in at most the bottom quarter of the image (~19:10 UTC, A);
- the two observed facts after 00:19, airborne at 00:19:37 and not powered at 01:15:56 (end of flight's `unpowered`, ~19:10 UTC B(b));
- strata re-weighted by the 00:19 data, with the fixed-weight mixture beside it (~19:10 UTC, C).

It replaces the stand-in's four-option result for this run (`results/settling-next-run-b-standin.md`), which used the earlier option set.

**Labels.** core (b) split-half NOT converged; two-tank bookkeeping only; internal-v1 one-engine flow 2x; dive class (b) and Boeing glide
PROVISIONAL-OVERNIGHT; breakup table PROVISIONAL; prior track 289.7°; deskstar (core) and Mac (end of flight, settling).

## Figures

- `settling-seabed-wreckage-next-run-b-reweighted.{pdf,png,json}` uses flight families weighted by the flight model, then by the 00:19 data.
  This is the ruled view.
- `settling-seabed-wreckage-next-run-b-fixed.{pdf,png,json}` uses flight families at the flight model's fixed weights.

Every panel shows the settled-mass seabed density in grey, at 50 / 90 / 99 %, and the impact PDF as dashed orange lines.

## Method

- **Impacts.** `mh370-exchange/end-of-flight/next-run/<stratum>/seed-<1..4>/impacts.npy`: four strata x four seeds. Weights come from end of
  flight's `option_posteriors` with `constraints=("unpowered",)`, imported at 43262c31.
- **Options.**

  | # | name | arm |
  |---|---|---|
  | 1 | 00:19 Held Out | `none` x other |
  | 2 | 00:19 R600 BTO Only | `r600-bto` x other |
  | 3 | 00:19 R600 BTO + Raw BFO | `r600_no-offset` x other |
  | 4 | 00:19 Holland H1 | `both_startup-offset` x fuel exhaustion |
  | 5 | 00:19 Holland H2 | `both_no-offset` x other |

- **Strata.** Fixed weights are core's P(family): 0.695 / 0.153 / 0.138 / 0.015 (free / repro-radar / descent-climb / routes).
  - Re-weighted values come from end of flight's `family-evidence-next-run-b.json`, `p_family_reweighted` for the `+alive` keys.
  - 00:19 R600 BTO + Raw BFO: 0.639 / 0.140 / 0.204 / 0.018.
  - 00:19 R600 BTO Only: 0.697 / 0.139 / 0.148 / 0.016.
  - Held Out is unchanged. H1 and H2 are not re-weighted (end of flight).
  - The factor for not being powered at 01:15:56 is applied within each stratum but is not in the family weights. It removes at most 0.3 % of
    weight in any stratum.
- **Sampling.** Each option, stratum and seed gets a systematic resample of ceil(N max(P_fixed, P_reweighted) / 4) impacts, where N is 200,000
  for Held Out and 40,000 otherwise. Each mixture is a stride sub-sample at N P / 4, so no new draws are needed. Every resampled impact is
  settled once on the real ocean.
- **Ocean.** Settling `hypothesis/settling` 5b595bf: the window is now 75-115 °E, 45-10 °S, on ocean transport's wider GLORYS12V1 column.
- **Map.** 0.02° grid sized to all impacts (79-115 °E, 46-2 °S), Gaussian 0.1°, HPD on the smoothed density, areas on the authalic
  sphere. Mixture impact ESS is the Kish combination; the not-estimable threshold is 1,000.
- **Cost.** Two settling passes of 200,156 and 162,981 draws took 3.7 and 3.9 min at 2 threads, outside the heavy lock, which was held by others.

## Areas (thousand km²)

| option | impact ESS (re-weighted) | 90 % impact, all impacts | 90 %: same impacts → seabed (re-weighted) | settling adds, 90 % / 99 % | 90 %: same impacts → seabed (fixed) | 90 % impact, seeds 1-2 / 3-4 | 90 % impact by stratum: free / repro-radar / descent-climb / routes | estimable |
|---|---|---|---|---|---|---|---|---|
| (a) 00:19 Held Out | 20,980,512 | 582.1 | 578.7 → 579.4 | +0.12 % / +0.16 % | 578.7 → 579.3 | 592.9 / 558.6 | 573.9 / 657.1 / 484.7 / 328.8 | yes |
| (b) 00:19 R600 BTO Only | 13,004,630 | 371.4 | 363.8 → 364.9 | +0.28 % / +0.68 % | 366.0 → 367.1 | 391.4 / 337.7 | 362.5 / 437.2 / 290.1 / 209.3 | yes |
| (c) 00:19 R600 BTO + Raw BFO | 509,632 | 239.1 | 238.8 → 239.4 | +0.24 % / +0.44 % | 241.7 → 242.3 | 253.6 / 215.6 | 240.5 / 289.5 / 171.3 / 140.2 | yes |
| (d) 00:19 Holland H1 | 86 | 67.2 | 67.2 → 69.4 | +3.29 % / +4.76 % | 67.2 → 69.4 | 48.3 / 49.5 | 42.3 / 42.4 / 35.1 / 28.8 | **not yet estimable - targeted sampler in progress** |
| (e) 00:19 Holland H2 | 124 | 68.6 | 68.7 → 70.7 | +2.96 % / +4.54 % | 68.7 → 70.7 | 54.3 / 50.9 | 50.2 / 52.9 / 43.6 / 37.6 | **not yet estimable - targeted sampler in progress** |

| option | settled offset from impact p50 / p90 / p99 (km) | settled mass > 5 km | afloat mass (no seabed position) | impacts not computed |
|---|---|---|---|---|
| (a) 00:19 Held Out | 0.36 / 3.62 / 21.35 | 7.4 % | 18.0 % | 6 of 200,000 |
| (b) 00:19 R600 BTO Only | 0.36 / 3.87 / 22.27 | 7.8 % | 18.2 % | 0 of 40,000 |
| (c) 00:19 R600 BTO + Raw BFO | 0.36 / 3.83 / 21.57 | 7.7 % | 18.2 % | 1 of 40,000 |
| (d) 00:19 Holland H1 | 0.34 / 2.98 / 21.84 | 6.5 % | 18.2 % | 0 of 40,000 |
| (e) 00:19 Holland H2 | 0.36 / 3.27 / 21.43 | 6.9 % | 18.2 % | 0 of 40,000 |

## What it shows

1. **Settling still adds under 1 % to every estimable area:** +0.12 to +0.28 % at 90 %, and +0.16 to +0.68 % at 99 %. The settled-offset kernel
   is unchanged: p50 0.36 km, p90 3.6-3.9 km. The seabed PDF of the main wreckage is the impact PDF to under 1 % in area, as on reference-289.
2. **The 00:19 treatment sets the area.** The 90 % region is 579,000 km² with the 00:19 data held out, 364,000 km² with the R600 BTO alone, and
   239,000 km² with the R600 BTO and its raw BFO. These differences come from end of flight and core, not from settling.
3. **Re-weighting by the 00:19 data changes little.** It moves R600 BTO + Raw BFO from 242,000 to 239,000 km² (descent-climb's weight
   0.138 → 0.204) and R600 BTO Only from 367,000 to 365,000 km².
4. **These areas are not converged.**
   - The two seed halves differ by 6-16 % (relative to their mean). For Held Out, the 90 % area is 593,000 against 559,000 km².
   - The four strata span 329,000-657,000 km² for Held Out.
   - Both come from core (b)'s split-half failure and P(family), not from settling. Quote the areas as unconverged.
5. **Holland H1 and H2: not yet estimable - targeted sampler in progress.** Their mixture impact ESS is 86 and 124, on 832 and 1,033 distinct impacts.
   - Their panels show where a few hundred impacts lie, not a posterior.
   - The cause is measured: within-parent sampling of the 00:19 push-over (end of flight ~20:15; `results/settling-h1h2-estimability.md`).
   - Pete has asked first for an investigation of whether the low push-over share is physical or an artefact of the descent model (architecture
     ~17:30). Any sampler change waits on that and on his approval.
6. **Not computed:** 6 of 200,000 Held Out impacts and 1 of 40,000 R600 BTO + Raw BFO impacts lie north of 10 °S, at 6.7-8.8 °S. They are outside
   the widened window and are excluded, not treated as impossible.

## COVERAGE (ruling ~15:45 -0600)

Settling is a transform. Its coverage question is whether its physics and parameter ranges reach every way wreckage can come to rest,
given an impact. Whether the impacts cover the aircraft's feasible flight space is end of flight's and core's coverage; it is inherited
here and stated per option.

**(a) Feasible set: where wreckage can come to rest.** Every piece either sinks soon after contact, floats and then sinks, or stays afloat
beyond any search. A sinking piece descends through the real current column to its first seabed contact. Afterwards it can slide or tumble
on slopes, be buried, or be moved by bottom currents and turbidity flows. Breakup can happen at water contact (one release point) or in
flight (several release points, as for SAA295 [margo1990, pp. 45-47]). Sealed sections can implode at depth.

**(b) Model's reach.**
- One release point per impact.
- Six classes, each drawn from wide declared ranges (`breakup.toml`):
  - areal density 5-1,300 kg/m²;
  - glide ratio 0-1.0;
  - float time 1 min to 6 h for sections (6 h for intact ones), up to 2 h for flat panels and up to 24 h for cabin contents, inside the 48 h float/sink cut-off; beyond it a share stays afloat (cabin contents 0.4, flat panels 0.2);
  - leeway 1-5 %.
- Three breakup families, chosen by impact energy.
- The real ocean in 75-115 °E × 45-10 °S, 7-14 March 2014.
- First seabed contact only.
- Declared alternatives, off in the baseline: implosion at depth, occupants, floating share x0.5 / x1.5.

**(c) Proposal coverage.** One settling draw per resampled impact. The settled-offset statistics (p50 0.36 km, p90 3.6-3.9 km, 7-8 % of mass beyond
5 km) are stable to two figures across the four estimable options and across strata. Monte Carlo halves of the D6 pages differ by a median of
2.7 % in p90. Inherited impact ESS per option: see the area table. H1 and H2 are below 1,000.

**Gaps and status.**

| gap | kind | status | effect on this result |
|---|---|---|---|
| in-flight breakup (two or more release points) | reach | declared conditional: "single release point at water contact" | none on areas at 6 NM; a second release point 1-3 km away is below the kernel |
| post-contact movement (sliding, burial, turbidity) | reach | declared conditional: "first seabed contact" (methods §8). Burial is searched areas' ρ | none on areas; matters for detectability, not position |
| floating > 48 h | reach, by design | handed to drift (afloat share 18 %, excluded from the seabed density) | excluded mass is reported per panel |
| ocean window 75-115 °E × 45-10 °S | reach | closed today for all but 7 of 280,000 impacts (north of 10 °S); those are excluded and counted | under 0.003 % per panel |
| breakup table and family selection | parameter bounds | PROVISIONAL, from 3 calibration points; bounds sourced in `data/analogues.csv` and the ledger | the dense/floated split sets the 5-7 % tail; floating-share x0.5 / x1.5 bracket it |
| H1 / H2 impacts (inherited) | proposal and reach, end of flight | coverage gap: "not yet estimable - targeted sampler in progress"; descent model and sampler await Pete | panels (d), (e) not posteriors |
| core (b) not converged (inherited) | proposal, core | labelled; seed halves differ 6-16 % in 90 % area | quote the areas as unconverged |

## Corrections to earlier settling maps

- Until today, settling's renderer drew its densities on a fixed 80-112 °E, 46-20 °S grid. Impact mass north of 20 °S or east of 112 °E was left off
  the map: 0.03-0.04 % of Held Out weight (0.02 % of R600 + BFO on reference-289), so those HPD areas were computed on 99.96 % of the mass.
- The effect is below Monte Carlo noise at 90 %; the 99 % areas were slightly low.
- The new renderer sizes the grid to the impacts and checks that no mass is lost. Published reference-289 results keep their numbers until they
  are next re-run.
- Earlier panels were titled with arm codes and stamped "NOT ESTIMABLE"; they are re-labelled at their next re-run, as the ruling allows.

## Reproduce

    python3 wf_standard.py prep   <EoF smoke dir> <mh370-exchange/end-of-flight/next-run> <summary/family-evidence-next-run-b.json> nrb
    SETTLING_FIELD_IN=field/nrbA_impacts.f64 SETTLING_FIELD_OUT=field/nrbA_elements.f64 cargo test --release -p mh370-hypotheses settling::tests::wreckage_field -- --ignored   (and B)
    python3 wf_standard.py render <EoF smoke dir> <core runs/reference-289/run.json> nrb next-run-b 5b595bf 43262c31

`wreckage_map_standard.py` is the renderer. The element files (1.2 GB) stay in settling's workspace and are not committed.
