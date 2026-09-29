# Status

Updated 2026-09-25.

## Current result

`make report` reproduces Davey et al. (2016) Fig. 10.3: the aircraft latitude
pdf at 00:19 UTC. It takes ~93 min on 6 threads, 4.5 GB peak memory.

- BTO + BFO: median 38.16°S, 95% interval 35.91–39.53°S. The book gives
  37.53°S and 34.90–39.38°S; the two curves overlap by 71%.
- Seed stability: split-half overlap 93% over 8 replicates of 7M particles.
- BTO only: a narrow northern mode at 44.7°N holds 7% of probability. The book
  shows one near 45°N.
- Every quantile above moved 0.025° north on 2026-09-25. The cumulative density
  is now read against the upper edge of each 0.05° bin instead of its centre,
  which had put every quantile half a step south, the published curve's included.
  Densities, overlaps and the shoulder mass are unaffected.

## Known defect (fix pending)

- final.npy rows are weighted, and summary.json pools them, by each particle's
  current autopilot mode instead of the mode run (stratum) it belongs to
  (filter.rs, summary.rs). Lateral-navigation particles that reverted to heading
  hold (4–9% of each replicate's mass) got the heading modes' posterior, and the
  replicate weights summed to 0.92–0.96 instead of 1.
- Reweighting the stored particles by stratum barely changes anything (4 seeds):
  base shoulder 3.5% → 3.6%, median −38.21 unchanged, overlap 71.2% → 71.6%;
  complex-manoeuvres 17.7% → 17.9%; mach-wide 10.6% → 11.1%. By stratum,
  P(shoulder | mode) is TH 26%, MH 52%, TT 1.0%, MT 54%, LNAV 1.7% (by current
  mode: 24/51/1.0/54/0.8%). No conclusion below changes.
- These corrected numbers are an exact stratum reweighting of the stored base run;
  the full `make report` is pending disk (needs at least 11 GB free).
- The fix (a stratum column, weighting and pooling by it) lands after the core/stages
  merge and before the fuel work and the MH371 control. It is checked at smoke scale
  against the pre-fix output of the same seed reweighted by stratum: identical
  particles, weights equal to rounding.
- A pre-fix MH371 control run was stopped during its first replicate, unscored; no
  summary was written or read. The control runs once, after the fix.

## Open problems

1. **Missing northern shoulder.** The book has 25% of probability at
   34.5–36.5°S; this recreation has 3.5%. Diagnosis from the base posterior:
   - The shoulder comes from heading-hold and magnetic modes flown at low
     Mach. Given the mode, P(shoulder) is 24% for true heading, about 50% for
     the magnetic modes, and about 1% for true track and lateral navigation.
     The last two carry 91% of our posterior.
   - Reweighting our particles to equal mode weights gives a shoulder of 27%
     and 86% overlap with Davey, but too long a northern tail.
   - Where the weight is lost: the modes match true track to within 0.3 in
     log-evidence through 21:41. They lose it at the 22:41, 00:11 and 00:19
     BTO arcs, with or without BFO: true heading −2.2, magnetic heading −5.1,
     magnetic track −3.6. Over a million shoulder-bound paths are generated,
     so it is weighting, not generation.
   - Ruled out:
     - BFO treatment: the deficit is already present in the BTO-only case.
     - Altitude prior: `altitude-prior`, 3.2% vs 3.5%.
     - Initial Mach: `initial-mach`, 3.5% vs 3.5%.
     - Declination grid errors: it matches IGRF-14 exactly.
   - Comparison basis for the sensitivities below: replicates 1–4 of each run
     and the median of the smoothed latitude density, so their medians
     (base −38.22) compare with one another, not with Current result
     (all 8 replicates, bin-edge quantiles: 38.16).
   - Wind sensitivity (`make sensitivity S=wind-off`, nominal ERA5 wind off,
     wind-error noise kept; 4 × 7M particles):
     - True heading's late-arc penalty vanishes (−2.3 → −0.1) and its weight
       rises from 6% to 31%. Wind is what penalises true heading.
     - The shoulder does not return (3.2% vs 3.5%) and the median barely
       moves (−38.12 vs −38.22). Without wind, true-heading paths fly like
       true-track paths and only 1.8% reach the shoulder, against 24% with
       ERA5 wind.
     - The magnetic modes are still penalised (−3.0, −2.8). That comes from
       the declination swing, not the wind.
   - Weather model: NCEP FNL (operational analysis, the closest public
     analogue of ACCESS-G) and NASA MERRA-2 give the same result as ERA5.
     - Shoulder: 3.3% and 2.9% vs 3.5%.
     - Median: −38.25 and −38.22 vs −38.22.
     - Late-arc penalties (TH/MH/MT): −2.5/−5.1/−3.8 and −2.5/−5.0/−3.7 vs
       −2.3/−5.1/−3.5.
     - Their winds differ from ERA5 by 2–2.4 m/s RMS (bias < 0.4 m/s) at
       cruise altitude, less than the model's wind-error s.d. (2.9 m/s).
       Weather is ruled out.
     - The MERRA-2 run was killed (out of memory) before writing run.json;
       all four BTO+BFO replicates are complete.
   - Satellite ephemeris: ours (STK/SGP4 from a later TLE) differs from
     Inmarsat's published states (Ashton et al. 2015, Table 4) by 2–4 km, a
     BTO error of −1 µs at 19:41 rising to +10 µs at 00:11–00:19. With
     Inmarsat's states (`make sensitivity S=inmarsat-ephemeris`): shoulder
     2.9% vs 3.5%, median −38.21 vs −38.22, penalties −2.4/−5.3/−3.8.
     No effect: the offset moves each arc almost uniformly, so all modes
     shift together. Inmarsat's states are still the correct input and are
     consistent with the −495,679 µs calibration, so the base should adopt
     them (a small, intended change to the estimate).
   - Residual diagnostics (branch `core/residual-diagnostics`, through 00:11,
     00:19 excluded): heading and magnetic paths arrive 200–350 µs beyond the
     22:41 arc and 450–600 µs beyond the 00:11 arc (westerly drift and the
     declination swing both carry them east, away from the satellite). The
     typical shoulder-bound path still overshoots at Mach 0.73. About 1% fit
     within ±29 µs, using speed and altitude changes or late turns.
   - Declination sign reversed: no shoulder. Magnetic modes fit worse (BTO+BFO
     MH −6.3 and MT −7.5 vs −4.3 and −2.9); the band share at 00:11 is 17.7%
     vs 20.3%.
   - Recovered Drive work: a sibling Davey-style Rust filter, unconverged
     with about 11 root ancestors, put 20–56% in 34.5–36.5°S depending on the
     seed. A sparse filter can produce Davey's shoulder by chance; Davey's
     Fig. 10.6 also shows only a few Mach bands. This is now the leading
     explanation.
   - Sparse-filter test (base model, 50 seeds per size, branch
     `core/residual-diagnostics`). Shoulder share ≥25% occurs in 14% of runs
     at 7k particles (about 8 surviving root draws), 8% at 35k (about 21),
     and 0% at 140k (about 67). The median is 3–4.5% at every size. A sparse
     filter reproduces Davey's shoulder by chance in about 1 run in 7–12,
     which is plausible but not the expected outcome.
   - Mode mix needed (fit of our five per-mode latitude curves to Davey's):
     the best mix reaches 92% overlap (ours 71%) with TH 22%, MH 4%, TT 44%,
     MT 22%, LNAV 8%, median −37.50 (Davey −37.56). This needs heading and
     magnetic modes to gain +1.6 to +2.8 in log-evidence relative to true
     track, which is almost exactly the late-arc penalty we measure. No mix
     reproduces Davey's northern edge (fitted 97.5% at −28.1 vs −34.9).
   - Manoeuvre frequency (`complex-manoeuvres`, τ restricted to 0.1–1 h):
     shoulder 17.7% (seeds 17.3–18.1%), median −37.31, overlap 81%, but
     10.8% north of 34.5°S (Davey 0.8%) and a 97.5% point of −27.9°. The
     shoulder is sensitive to how often paths manoeuvre; this overshoots.
   - Wide Mach range (`mach-wide`, 0.50–0.86 instead of 0.73–0.84):
     shoulder 10.6% (seeds 9.2–11.4%), median −37.98, overlap 76%, 5.0%
     north of 34.5°S. 84% of the shoulder weight is at Mach < 0.73 (median
     0.69); south of 36.5°S only 9%. Late-arc penalties shrink (TH/MH/MT
     −1.6/−3.0/−2.1). Fuel endurance is not modelled, so slow cruise is not
     penalised.
   - Davey's sampler and turn counts. Davey et al. (ch. 8) branch each root trajectory
     depth-first and prune; τ is drawn once per root. Their posterior (Fig. 10.4) has
     ≥2 turns in 49% of paths; ours has 12% with the same dynamics (uniform ±180° turns,
     Jeffreys τ). Smaller filters give more turns (7k 30%, 35k 18%, 140k 14%), and the
     35k seeds with a ≥25% shoulder have the turn histograms closest to Davey's. The
     shoulder and the excess turns are both what a filter with few surviving roots
     produces (report/northern_paths.py for the frequent-manoeuvre paths).
   - Early path (report/early_path_fit.py): the 18:25–18:28 BTOs want
     336–400 kt (Mach 0.57–0.68) against 516 kt at the last radar point;
     N571, NILAM–SAMAK and MEKAR–SAMAK fit equally (χ² 3.2–3.4 of 14) if
     the final turn starts ≥20 NM before IGOGU or ≥40 NM before SAMAK
     (by about 18:37). A level turn at SAMAK is rejected (Δχ² +56 to +64,
     the 18:39:55 BFO) unless descending about 2,100–2,600 fpm.
   - Conclusion: under ERA5, the paths that would form the shoulder are the
     wind-drifted heading paths and the magnetic paths, and the late arcs
     reject both. Davey's shoulder needs either a wind field under which
     drifted heading paths fit 22:41–00:19 (ACCESS-G is the direct test;
     requested), or more weight on the magnetic modes than the data give
     here.
2. **Run time.** The hourly BTO arcs keep ESS at 1–15%, so each replicate
   needs 7M particles. A better proposal at 18:39 and 19:41 would cut the
   run substantially.
3. **Environment grids are outside git.** `data/*.bin` (~350 MB) are ignored.
   A fresh clone must rebuild or copy them before `make report`.

## Hypotheses

Each hypothesis records its own status in `hypotheses/<name>/hypothesis.toml`.

- `altitude-prior`: not supported (shoulder 3.2% vs base 3.5%).
- `initial-mach`: not supported (shoulder 3.5% vs base 3.5%).

## Next steps

- ACCESS-G comparison if the data can be obtained: convert it to the ERA5
  grid format and set `inputs.era5` in a sensitivity config. No code change.
- MH371 known-flight control (7 March 2014, Beijing to Kuala Lumpur), run prospectively.
  Built and committed before any run (`make control`; config/control/mh371.toml,
  report/mh371_score.py): five hourly R1200 BTOs by rule, BTO only (no satellite+EAFC
  terms for MH371), regional ERA5 weather (FNL in the first version, replaced before the run). Code paths checked at smoke scale only; the full-scale
  run waits for disk space. The first prior rule (bearing between the last two ACARS
  reports) was replaced before any run by the reported heading, because that pair spans
  the 01:58 turn shown in Davey's Fig. 9.7.
  - Fix the window, config and scoring before anyone looks at the truth track. The window is
    Davey's validation segment (Fig. 9.7), not one chosen by us.
  - Only the scorer reads the ACARS truth. Rows 01:33–02:59 UTC (altitude, Mach, weight, fuel;
    no positions) were seen on 2026-09-25 while identifying the file.
  - Its 5-minute ACARS fuel-on-board reports are an in-flight test of the fuel model,
    independent of Boeing's tables.
- Only after that, add further evidence as hypotheses compared against this
  base: fuel, end-of-flight kernel, drift. Fuel needs a path-accumulator hook
  (a core change).
