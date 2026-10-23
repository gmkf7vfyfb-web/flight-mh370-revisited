# Hydroacoustics graphics 22 Oct 2026 — track: ranked candidates and impact energy / coupling

*Hydroacoustic Module (graphics track 3 of 4). EXPLORATORY ranking, pre-registered on the module branch at `9f47cf7`
(`prepare/ranked_candidates/prereg.py`) before any score was computed; not part of the frozen searches (block 5) or the composition (block 11).
**PREDICTIVE, NOT CALIBRATED. No detection is claimed.** Caveats C1 (propagation slope misfit, +10.4/+7.4 dB per octave at H01W/H08S) and C2
(coupling efficiency not calibrated; η swept over four decades). F-35A anchor η = 2.1 × 10⁻⁴: **provisional - from Brown 2026's quote of Metz 2023; re-derivation from Metz pending**. H01W/H08S rows are from the DIGITISED
Kadri (2024) Fig. 9 panels. Both Kadri times: text time 00:52:03, caption time 00:54:30.*

## Result

Every candidate — 184 one-recorder signals, 3,321 two-recorder pairs, 1,201 scorable three-recorder sets — has an approximate ln LR below 0
(signal vs background, 00:19 Held Out (D0′), p = 0.5): **noise explains each of them better than an impact from the run J posterior does.**
Highest values: pair ln LR −0.64, three-recorder set −2.95, single −1.63. Every scored candidate also needs a coupling efficiency of at least 0.008 (singles 0.014–1.7, i.e. 65× to 7,900× the provisional F-35A anchor;
pairs 0.008 to > 1 for P_D = 0.5 at both, 40× upward, and 341 pairs never reach P_D = 0.5 at η ≤ 1), above the coupling at which half of the simulated impacts would be detected
(η₅₀ = 4.0e-03 at α 0.01, recomputed on the corrected IMOS table; 1.1e-03 at α 0.05; the earlier table gave 6 × 10⁻⁴).

**The pair the searches named strongest** (Cape Leeuwin H01W 00:52:04, M1b p 0.043, text-time box × Diego Garcia South H08S 01:12:49, M1b p 0.039,
raw panel e, p_B 0.30) ranks **104 of 3,321** pairs by ln LR (-6.23; -4.84 without the bearing term) and 54 by max p.
Lag 1,245 s inside [809, 1536] s; arc locus 33.6°S 94.5°E, implied impact 00:31:41;
coupling for P_D(both) = 0.5 at α 0.05 = **0.0692 = 329× the anchor** (reproduces the composition's 0.0692);
radiated acoustic energy 7.39e+07 J = **391× the F-35A's 900 MJ × 2.1 × 10⁻⁴** (because the run J median
energy at the locus, 1.07 GJ, is 1.19× the F-35A's). **Bearing caveat:** the locus is at 268.9° from H01W (1,812 km) and 144.8° from H08S
(3,660 km); Kadri publishes 57° or 306.18° for the 00:52 signal (text p. 9 and Table 1 caption disagree), neither within 37° of 268.9°; the nearest
Table 1 bearing to 268.9° is 00:52:50 at 274.84°, 46 s later; within 30 s of 00:52:04 Table 1 gives 00:51:50 at 320.40°.
The H01W 00:52:04 single ranks 105 of 184 (-6.48; -2.75 without the bearing term); the caption-time row 00:54:29 ranks 104 (-6.47).

### Top 5 two-recorder pairs (ranked_pairs.csv)

| | rank ln LR | ln LR | rank max p | signals | lag s [predicted] | arc locus, impact | η for P_D(both) = 0.5 (× anchor, provisional) |
|---|---|---|---|---|---|---|---|
| P1 | 1 | -0.64 | 437 | Diego Garcia S. H08S 01:02:53 (M1b 1-9 (plot), p 0.0704; p_B 0.12) × Perth Canyon 3315 00:47:52 (BE 2-5, p 0.122) | -900 [-1573, -698] | 36.88°S 90.00°E, 00:21:21 | 0.871 (4,147×) |
| P2 | 2 | -2.51 | 1198 | Diego Garcia S. H08S 01:03:13 (D1 1-9 (plot), p 0.193; p_B 0.29) × Perth Canyon 3315 00:47:52 (BE 2-5, p 0.122) | -921 [-1573, -698] | 36.65°S 90.36°E, 00:21:44 | 0.55 (2,617×) |
| P3 | 3 | -2.73 | 2214 | Diego Garcia S. H08S 01:02:53 (M1b 1-9 (plot), p 0.0704; p_B 0.12) × Perth Canyon 3315 00:47:16 (BE 2-5, p 0.239) | -936 [-1573, -698] | 36.48°S 90.62°E, 00:21:25 | 0.38 (1,810×) |
| P4 | 4 | -2.83 | 2968 | Diego Garcia S. H08S 01:04:52 (D1 1-9 (plot), p 0.276; p_B 0.78) × Perth Canyon 3315 00:49:48 (M1b 5-40, p 0.219) | -905 [-1573, -698] | 36.83°S 90.08°E, 00:23:21 | 0.0562 (268×) |
| P5 | 5 | -3.42 | 1988 | Diego Garcia S. H08S 01:04:23 (BE 5-9, p 0.224; p_B 0.5) × Perth Canyon 3315 00:49:48 (M1b 5-40, p 0.219) | -875 [-1573, -698] | 37.16°S 89.57°E, 00:22:48 | 0.166 (790×) |

All five are H08S raw-panel rows (airgun-dominated, G-S9) with Perth Canyon 3315 (null from 3376, G-S4; three use 2–5 Hz band energy, below the 8 Hz hardware corner).
They rank first because the ln LR's time term favours the D0′ bulk near 36.5–37°S and impact 00:21–00:23, not because any row is unusual.

### Top 5 one-recorder signals (ranked_singles.csv)

| | rank ln LR | ln LR | rank p | recorder, time UTC | detector, band | p | η level match (× anchor, provisional) | kernel-weighted source, impact |
|---|---|---|---|---|---|---|---|---|
| S1 | 1 | -1.63 | 40 | Diego Garcia S. H08S 01:02:53 | M1b 1-9 (plot) | 0.0704 (p_B 0.12) | 0.287 (1,365×) | 37.02S 90.02E, 00:21:07 |
| S2 | 2 | -1.67 | 2 | Portland 3275 01:20:35 | M1b 5-40 | 0.00823 | 0.235 (1,119×) | 36.52S 90.81E, 00:31:02 |
| S3 | 3 | -2.68 | 4 | Portland 3275 01:07:46 | D1 5-40 | 0.0093 | 0.148 (704×) | 33.68S 94.44E, 00:20:34 |
| S4 | 4 | -2.82 | 149 | Perth Canyon 3315 00:47:16 | BE 2-5 | 0.239 | 0.153 (726×) | 36.92S 90.12E, 00:20:52 |
| S5 | 5 | -2.83 | 13 | Portland 3275 01:07:47 | M1b 5-40 | 0.0163 | 0.148 (704×) | 33.69S 94.43E, 00:20:34 |

## Figures

- `impact_energy_and_coupling.png/.pdf` — (a) run J impact kinetic energy per 00:19 option (median, 25–75 %, 5–95 %); (b) coupling η vs energy with
  iso-lines of radiated energy η·E, the η prior [10⁻⁶, 10⁻²], the F-35A point (900 ± 200 MJ, η 2.1 × 10⁻⁴, upper bound, provisional), the half-detected
  line (corrected table; earlier table dashed grey), and for the top 5 pairs, top 5 singles and the strongest searches pair the band η(E) = R/E over the
  D0′ 5–95 % energy range; (c) the same as a multiple of the F-35A radiated energy. **What 330× means:** the coupling needed at the run J energies is
  about 330 times the F-35A's η; the radiated acoustic energy needed is about 390 times the F-35A's 900 MJ × 2.1 × 10⁻⁴ = 1.9 × 10⁵ J (the ratio of the
  two is the energy ratio 1.07 GJ / 0.9 GJ).
- `ranked_multisite_top15.png/.pdf` — one-page table, top 15 two- and three-recorder sets + the strongest searches pair.
- `ranked_singles_top15.png/.pdf` — one-page table, top 15 one-recorder signals + the two Kadri-time Cape Leeuwin rows.

## Method (as pre-registered; deviations below)

ln LR = ln N − ln B. N = Σᵢ wᵢ meanη Π_c [P_D(snrᵢ(η); α = p_c) · K_t · A · G]; B = Π_c (p_c / 55 s). Rows: run J geometry sample (`run-j-searches/geometry/sample.npz`,
8.85 M rows, 7.24 M with weight; D0′ ESS 110,383); η on the block 11 41-point log-uniform grid [10⁻⁶, 10⁻²]; snr from `composition_run_j/common.Machinery(imos_ramgrid=True)`
(corrected IMOS RAM-grid TL, IMS grid KRAKEN − RAM Δ, +4.8 dB triad gain, N(0, 10 dB) calibration draw per row); P_D block 7 fits for the candidate's
detector with L50 and slope interpolated in log α; K_t the block 11 Gaussian timing kernel (joint kernel = lag-consistency density for pairs/triples);
A the A4(c) level-consistency weight (σ 10 dB); G the Kadri Table 1 bearing term (t3, 3.3°) for H01W rows within 30 s. Arc locus: crossing of the
observed lag on the 7th-arc grid (block 11 method), the crossing with most D0′ mass within ±1°. Sensitivity columns: D2/D3/D4 weights, p_B in place of p
for panel rows, no bearing term.

## COVERAGE

- **(a) Feasible set.** Every run J impact (all strata) plus the northern supplement; all four 00:19 options; coupling over the declared prior.
- **(b) Model reach.** The geometry sample omits the free / descent-climb / repro-radar strata (0.2 % of the mixture, searches G-S7) and keeps the supplement at
  p = 0.5 only; arc loci are limited to the 41–20°S arc grid; TL clipped to 41–20°S; Scott Reef 3250 has no TL path or P_D fit (blocked: ln LR −inf by construction).
- **(c) Proposal coverage.** Kish ESS of the sample: D0′ 110,383 / D2 6,431 / D3 403 / D4 2,031 (D3 thin; its sensitivity column is noisy). Every candidate in the
  source tables is scored (no subsampling of candidates); 63 triples have no sample row matching all three times.
- **Gaps.** (R1) amplitude term for panel rows uses the searches' η_needed at the reference impact (no 5–40 Hz band on the plots) — open, needs Kadri's raw data.
  (R2) the level-consistency and bearing terms are unnormalised weights (≤ 1 and density ratio), so ln LR is an approximate ratio for ordering, not a calibrated
  Bayes factor — declared. (R3) η needed for singles is at one reference source; for pairs at the median E and τ within ±1° of the locus; τ dependence along the
  energy bands ignored. (R4) the composition's prior mass within ±1° of the 33.6°S locus was 0.226 on its subsample; this geometry sample gives 0.072
  (different subsample of run J) — the η requirement is unaffected. (R5) F-35A anchor provisional pending the Metz 2023 re-derivation.
  (R6) η₅₀ recomputation ignores the recorders' duty cycle (geometric detectability, as the injection-recovery definition).

## Deviations from the pre-registration

1. pairs.csv grouped on (receiver, time, detector, band, p) gives 3,321 distinct pairs, not 3,315: two Scott Reef windows share 01:32:07 M1b with different p.
2. Locus for triples: the (a, b) crossing kept only if the third arrival is within 60 s (not pre-registered; needed to define one locus).
3. `prepare/ranked_candidates/rank.py` is the consolidated form of the interactive session; the committed tables come from the session. Verified by a full
   re-run of the script (22 Oct, ~10 min): every finite ln LR (singles, pairs, triples) agrees to < 3e-14; the coupling columns agree to within 2.3 % (the session
   cached the ±1° latitude mask at 0.01° rounding; one step of the 601-point η grid is 2.3 %).

## Provenance

Module branch: `9f47cf7` (prereg), and `844786e` (`prepare/ranked_candidates/rank.py` + `results-data/ranked_candidates/`). Exchange:
`mh370-exchange/hydroacoustics/graphics-2026-10-22/ranked/` (ranked_singles.csv, ranked_pairs.csv, ranked_triples.csv, ranked_multisite.csv, README.txt,
detectability_and_energy.json).

- done: ranked tables (singles, pairs, triples, combined), two one-page figure tables, energy/coupling chart (PNG + PDF).
- next: re-label the anchor when the Metz re-derivation lands; re-rank with Kadri raw data if it arrives (G-S2).
- blocker: none.
