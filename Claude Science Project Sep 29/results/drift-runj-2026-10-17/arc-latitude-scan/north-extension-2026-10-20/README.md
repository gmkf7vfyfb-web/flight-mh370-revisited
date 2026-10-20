# Arc-latitude dedicated drift run, northern extension to 20 S (overnight order C, 20 Oct 2026)

Ocean drift module, 20 Oct 2026 ~07:00Z. Follows `../` (15ab7c9: 66 points at 26-40 S). Pete approved order C at ~02:50Z.

## What ran
- 18 new release points at 20, 21, 22, 23, 24 and 25 S, each on the run J D0 median-impact track and 50 NM either side.
  Tier: north (3e5 particles per point = 25,000 per class x 3 classes x 4 environment realisations). Both ocean models.
  Settings are identical to `../arclat-<model>-north.toml`, with three exceptions: `margin_nm`, `node_subset` and
  `output_dir`. Release points: `arclat-ext-release-points.csv`.
- **Source grid extended.** The grid did not stop at 25.5 S. Its north edge was **22.0 S** (226 x 210 nodes, lat0 -40.75),
  so 20, 21 S and the 22 S inside point were off the grid. `margin_nm` was raised from 100 to 280, which adds exactly
  36 rows and 36 columns on the SAME 5 NM lattice: dlat and dlon are unchanged, lat0 is now -43.75, the size is 298 x 282
  and the north edge is 19.0 S. Node positions are unchanged (the 26 S nodes match the old positions to 3e-14 deg).
  Node IDs are renumbered; in the merged profile the new nodes carry the prefix `x`. The margin only places releases;
  `node_subset_outside_extent = true` as before.
- Track north of 26 S: the same rule as `../arclat-release-points.csv` (run J D0 histogram, 0.25 deg band medians,
  5-band rolling median), with the band list extended from 21.0 S to 19.0 S. The perpendicular direction comes from the
  cubic fit over the extended range. The 26 S points were re-used exactly; they were not re-derived.
- Overlap check at 26 S: (i) the 3 points re-run inside leg b with the same settings and seeds; (ii) an independent-seed
  repeat (seed 2, env_seeds 5-8), both models, 3 points.
- deskstar, binary `mh370_hypotheses-beedacd1154063da` (sha256 prefix cbe08758811b00aa, checked by the job before it
  started), under `flock ~/.mh370-heavy.lock`, after calibration case 29001. Six legs, all EXIT=0.
  Wall times (GlobCurrent / GLORYS12): 12 points 1,774 / 1,286 s; 9 points 1,402 / 1,187 s; seed checks 459 / 463 s.
  Peak RSS 11.0-11.5 GB (GlobCurrent), 18.8-19.0 GB (GLORYS12) (`run-timings.txt`). Node values: 21 + 21 + 6, all
  `value`, none not computed. Model-error share at most 0.034 % per node. Left-domain share 6-22 % per node, 14-22 % at
  the new 20-25 S points (domain 15-160 E, as before).

## Results
**Profile, finds only (base setting, two-model mixture), relative to the maximum (30 S track), track points:**
25 S -1.16 (split-half SD 0.14); 24 S -1.85 (0.08); 23 S -1.95 (0.14); 22 S -3.04 (0.21); 21 S -3.11 (0.23); 20 S -2.51 (0.76).
The plateau from 26 to 32 S is about -1 (from 18 Oct). **Debris evidence falls north of 25 S.** It is about 2 ln units below
the plateau at 21-22 S. The Australian no-find settings add only +0.1 to +0.3 there, because they barely penalise the north.
Both models give this direction. The mean over the three points per latitude, relative to 30 S, at 20 / 21 / 22 S is
GlobCurrent -4.9 / -3.8 / -4.1 and GLORYS12 -2.3 / -2.6 / -2.9. Per-model and per-option values are in
`arclat-likelihood-profile-20-40S.csv`.

**Posterior on run J D0 (00:19 data not used), two-model mixture, 18 Oct (26-40 S nodes) -> now (20-40 S nodes):**

| setting | mean-latitude shift (deg N) | split-half diff | median | share N of 33 S | share N of 26 S | share N of 22 S |
|---|---|---|---|---|---|---|
| finds only (base) | +1.07 -> **+1.00** | 0.01 | -36.57 -> -36.59 | 11.0 -> 10.5 % | 1.3 % | 0.01 % |
| option C | +3.41 -> **+3.27** | 0.09 | -34.83 -> -34.87 | 34.1 -> 33.2 % | 5.8 % | 0.04 % |
| option B (pre-registered) | +5.51 -> **+5.44** | 0.14 | -31.21 -> -31.23 | 58.3 -> 58.2 % | 13.6 % | 0.10 % |
| populated coast only | +3.46 -> **+3.36** | 0.07 | -34.85 -> -34.87 | 34.8 -> 34.3 % | 6.6 % | 0.05 % |

On 18 Oct the cells north of 25.4 S borrowed the 26 S values; the shift was then about 0.1 deg too far north. The real
nodes are lower there. Mass north of 22 S falls from 0.55 % to 0.10 % (option B). The split-half spread of the share north
of 26 S is 0.2 to 2.6 percentage points: noise is larger in the north. Per model (`arclat-posterior-summary-20-40S.csv`):
finds only GlobCurrent +0.91, GLORYS12 +1.08; option B GlobCurrent +4.94, GLORYS12 +6.12.

**Overlap at 26 S (`arclat-overlap-26S.csv`; 24 comparisons per repeat = 3 points x 4 settings x 2 models):**
- Same settings and seeds: the result is NOT bit-identical, even though particle streams key on (environment seed,
  index). The cause was not traced; scheduling inside the integrator is the most likely one. RMS difference
  0.17 (GlobCurrent) / 0.29 (GLORYS12) ln; RMS z 1.1 against the split-half SD; 2 of 24 have |z| > 2.
- Independent seeds: RMS difference 0.51 / 0.52 ln; RMS z 1.5; 4 of 24 have |z| > 2. After the common offset per point
  set is removed, the RMS is 0.30 ln.
- Verdict: the 26 S values are reproduced within Monte Carlo noise, if that noise is about 1.5 x the split-half SD.
  **The split-half SD understates the independent-seed noise by about 1.5x** (provisional: only 24 comparisons at
  3 points, correlated within a point). This agrees with the 18 Oct finding (item 7) that independent-seed noise per node
  exceeds split-half noise. The northern fall (about 2 ln) is several times either noise level.

**Detection settings (as before):** finds only = base; options B and C and populated coast only are labelled
sensitivity settings. The columns keep their 18 Oct names (`B (primary)` = option B, pre-registered) so that readers do
not break.

## COVERAGE
- (a) Feasible set: impact anywhere along the 7th arc that the flight-path evidence allows. Run J D0 has impacts from
  about 19 to 42 S. The arc and the aircraft's reach go further north than 19 S.
- (b) Model's reach (drift): release nodes now cover 19.9-40.25 S (84 points, 3 per latitude). The source grid itself
  spans 19.0-43.75 S. Cells outside 19.6-40.4 S borrow the nearest nodes: 0.0066 % of run J D0 mass (0.0032 % north of
  19.6 S, 0.0033 % south of 40.4 S). **Gap: impacts north of 19.6 S have no drift node.** It is negligible for run J D0;
  it is open for any hypothesis that puts mass there. Remedy: the same recipe, one more leg (20 min per model).
- (c) Proposal coverage: run J D0 puts 0.50 % of its mass at 20-26 S and 0.020 % north of 22 S. Drift raises the 20-26 S
  share to 1.3 % (finds only) and 13.6 % (option B). These northern masses rest on few flight paths. ESS per band is not
  assessed at this depth here: the histogram has no per-sample weights. The run J northern supplement (end of flight,
  order A) is the remedy; it is NOT included in this note.
- Parameter bounds: unchanged from `../` and brief section 4 (K log-uniform 100-1,000 m2/s; ocean-error length scale
  100 km assumed; windage priors per class; provisional detection levels).

## Files
`arclat-likelihood-profile-20-40S.csv` (84 points: mixture profile per setting, split-half SD, per-model ln L, state,
model-error and left-domain shares, source), `arclat-posterior-summary-20-40S.csv`, `arclat-overlap-26S.csv`,
`arclat-ext-node-tables.zip` (6 node tables, summaries, logs), configs `arclat-ext-*.toml`, `job_arclat_ext.sh`,
`merge_arclat.py`. With the 18 Oct inputs alone, `merge_arclat.py` reproduces the 18 Oct profile and posterior to 6e-6.
`fig_arclat.py` draws the figure `arc-latitude-dedicated-run-20-40S.png/pdf`, which redoes panels a and b for 20-40 S and
adds the Davey et al. (2016) Fig. 10.3 curve. Exchange copy: `mh370-exchange/debris-drift/arclat-north-2026-10-20/`.

Not evidence for the headline: this is a labelled sensitivity on run J D0 without the northern supplement.
