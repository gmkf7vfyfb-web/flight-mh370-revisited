# Pléiades module on end of flight's run D-he (H1/H2 sweep): H-conditional summary per 00:19 option, BEFORE seabed search

12 Oct 2026, Pléiades module. Architecture overnight plan 00:05Z, step 4.
Columns: `mh370-exchange/pleiades/next-run-d-he/` (READY 00:58Z). Script: `prepare/score_dhe_summary.py`; output: `pleiades-dhe-summary.json`.

**Labels:**
- **conditional on H**; no identity likelihood; no Bayes factor or P(H | data);
- core run D NOT converged; end-of-flight physics PROVISIONAL (end of flight's label list applies);
- survival factor adopted (primary), without it shown as a sensitivity;
- breakup P 0.93 / 0.88 PROVISIONAL;
- **BEFORE seabed search**: searched areas' run D-he columns are not yet published;
- Pléiades rating 5 + all four COSMO-SkyMed contacts, one debris field.

**Method:**
- **Option weights** are end of flight's own, reused unchanged:
  - `holland_sweep_summary.seed_terms`: derived log-likelihoods, the log-on lag term for the fuel-exhaustion cause, and constraint
    `unpowered`;
  - strata are mixed by core P x their own evidence.
- **Under H**, each row is multiplied by L_H, an exact cell lookup in the module's columns.
- **Tension:** the module's measure (`rerun_reference.tension`: ln S, Handley-Lemos p, mean shift) on the wide 0.05° grid.
- **ln E[L_H] vs Held Out** is the H-conditional positional compatibility of each option relative to Held Out, within one setting.
  It is not a Bayes factor for H.

## Results

### primary (survival factor adopted; primary)

| 00:19 option | setting | ESS under H (without H) | mean under H | shift NM | ln S (p) | 90 % region km², before search (without H) | ln E[L_H] vs Held Out | A1 / A2 / B share (ESS) |
|---|---|---|---|---|---|---|---|---|
| Held Out | **ρ 0.25, both models, product-relative (proposed)** | 460,316 (6,378,686) | 35.50 S 91.94 E | 73 | -0.04 (0.39) | 77,853 (556,384) | +0.00 | 0.30 (111,935) / 0.33 (218,319) / 0.37 (156,733) |
| Held Out | ρ 0.25, GLORYS12 only (in force) | 482,303 (6,378,686) | 35.56 S 92.00 E | 71 | +0.09 (0.43) | 65,033 (556,384) | +0.00 | 0.30 (119,597) / 0.32 (222,645) / 0.38 (165,979) |
| Held Out | ρ 0, both models (GlobCurrent as run) | 378,181 (6,378,686) | 35.44 S 91.95 E | 77 | -0.05 (0.39) | 66,516 (556,384) | +0.00 | 0.31 (96,701) / 0.33 (180,369) / 0.36 (123,252) |
| R600 BTO Only | **ρ 0.25, both models, product-relative (proposed)** | 509,039 (8,377,630) | 35.79 S 92.32 E | 104 | -0.48 (0.28) | 46,569 (311,346) | -0.43 | 0.32 (107,076) / 0.30 (240,864) / 0.38 (223,166) |
| R600 BTO Only | ρ 0.25, GLORYS12 only (in force) | 518,252 (8,377,630) | 35.83 S 92.33 E | 103 | -0.25 (0.33) | 38,656 (311,346) | -0.36 | 0.31 (115,633) / 0.29 (236,051) / 0.39 (213,856) |
| R600 BTO Only | ρ 0, both models (GlobCurrent as run) | 401,700 (8,377,630) | 35.72 S 92.34 E | 108 | -0.54 (0.26) | 41,769 (311,346) | -0.47 | 0.34 (89,454) / 0.30 (193,516) / 0.36 (171,784) |
| R600 BTO + Raw BFO | **ρ 0.25, both models, product-relative (proposed)** | 18,173 (190,237) | 35.73 S 92.27 E | 79 | -0.17 (0.34) | 39,411 (196,263) | +0.10 | 0.32 (3,651) / 0.26 (9,942) / 0.42 (8,826) |
| R600 BTO + Raw BFO | ρ 0.25, GLORYS12 only (in force) | 17,923 (190,237) | 35.75 S 92.29 E | 78 | +0.00 (0.39) | 34,153 (196,263) | +0.17 | 0.32 (3,982) / 0.25 (9,666) / 0.43 (7,652) |
| R600 BTO + Raw BFO | ρ 0, both models (GlobCurrent as run) | 14,719 (190,237) | 35.66 S 92.30 E | 83 | -0.19 (0.33) | 35,332 (196,263) | +0.10 | 0.35 (3,297) / 0.26 (8,074) / 0.39 (6,761) |
| Holland H1 | **ρ 0.25, both models, product-relative (proposed)** | 192 (4,690) | 35.81 S 92.36 E | 98 | -0.56 (n/e) | 20,548 (60,469) | -0.12 | 0.32 (22) / 0.24 (398) / 0.44 (456) |
| Holland H1 | ρ 0.25, GLORYS12 only (in force) | 228 (4,690) | 35.81 S 92.40 E | 99 | -0.42 (0.07) | 18,282 (60,469) | -0.04 | 0.30 (24) / 0.24 (384) / 0.46 (399) |
| Holland H1 | ρ 0, both models (GlobCurrent as run) | 142 (4,690) | 35.73 S 92.42 E | 103 | -0.59 (n/e) | 18,507 (60,469) | -0.15 | 0.35 (19) / 0.22 (348) / 0.42 (364) |
| Holland H2 | **ρ 0.25, both models, product-relative (proposed)** | 440 (2,234) | 35.87 S 92.31 E | 92 | -0.73 (0.17) | 19,976 (60,542) | -0.10 | 0.25 (56) / 0.25 (217) / 0.49 (290) |
| Holland H2 | ρ 0.25, GLORYS12 only (in force) | 439 (2,234) | 35.87 S 92.35 E | 93 | -0.58 (0.19) | 18,109 (60,542) | -0.04 | 0.24 (72) / 0.24 (208) / 0.52 (221) |
| Holland H2 | ρ 0, both models (GlobCurrent as run) | 346 (2,234) | 35.79 S 92.36 E | 97 | -0.81 (0.15) | 18,007 (60,542) | -0.15 | 0.28 (49) / 0.24 (179) / 0.48 (241) |

### without survival factor (labelled sensitivity)

| 00:19 option | setting | ESS under H (without H) | mean under H | shift NM | ln S (p) | 90 % region km², before search (without H) | ln E[L_H] vs Held Out | A1 / A2 / B share (ESS) |
|---|---|---|---|---|---|---|---|---|
| Held Out | **ρ 0.25, both models, product-relative (proposed)** | 526,496 (6,918,708) | 35.51 S 91.94 E | 70 | +0.02 (0.40) | 75,123 (531,011) | +0.00 | 0.25 (113,743) / 0.31 (231,580) / 0.44 (205,040) |
| Held Out | ρ 0.25, GLORYS12 only (in force) | 552,413 (6,918,708) | 35.56 S 92.00 E | 69 | +0.16 (0.45) | 63,027 (531,011) | +0.00 | 0.25 (121,597) / 0.31 (237,725) / 0.44 (217,043) |
| Held Out | ρ 0, both models (GlobCurrent as run) | 433,823 (6,918,708) | 35.45 S 91.96 E | 74 | +0.01 (0.40) | 63,856 (531,011) | +0.00 | 0.26 (98,428) / 0.31 (191,458) / 0.43 (163,946) |
| R600 BTO Only | **ρ 0.25, both models, product-relative (proposed)** | 585,199 (8,796,714) | 35.79 S 92.30 E | 102 | -0.33 (0.31) | 43,482 (299,743) | -0.40 | 0.26 (105,326) / 0.29 (244,022) / 0.45 (277,967) |
| R600 BTO Only | ρ 0.25, GLORYS12 only (in force) | 589,056 (8,796,714) | 35.82 S 92.31 E | 100 | -0.12 (0.36) | 36,114 (299,743) | -0.34 | 0.25 (114,041) / 0.28 (238,465) / 0.46 (267,975) |
| R600 BTO Only | ρ 0, both models (GlobCurrent as run) | 466,783 (8,796,714) | 35.72 S 92.33 E | 106 | -0.38 (0.29) | 38,801 (299,743) | -0.43 | 0.27 (88,161) / 0.29 (195,823) / 0.44 (218,805) |
| R600 BTO + Raw BFO | **ρ 0.25, both models, product-relative (proposed)** | 19,282 (196,447) | 35.73 S 92.27 E | 80 | -0.16 (0.34) | 38,254 (191,272) | +0.05 | 0.29 (3,657) / 0.27 (8,076) / 0.44 (9,739) |
| R600 BTO + Raw BFO | ρ 0.25, GLORYS12 only (in force) | 18,809 (196,447) | 35.75 S 92.29 E | 79 | +0.01 (0.39) | 33,225 (191,272) | +0.12 | 0.28 (3,989) / 0.26 (7,777) / 0.45 (8,504) |
| R600 BTO + Raw BFO | ρ 0, both models (GlobCurrent as run) | 15,679 (196,447) | 35.67 S 92.30 E | 84 | -0.18 (0.33) | 34,300 (191,272) | +0.04 | 0.31 (3,302) / 0.26 (6,456) / 0.42 (7,611) |
| Holland H1 | **ρ 0.25, both models, product-relative (proposed)** | 199 (4,338) | 35.81 S 92.36 E | 97 | -0.57 (0.01) | 20,600 (60,448) | -0.17 | 0.32 (22) / 0.24 (377) / 0.44 (450) |
| Holland H1 | ρ 0.25, GLORYS12 only (in force) | 235 (4,338) | 35.81 S 92.40 E | 98 | -0.43 (0.09) | 18,358 (60,448) | -0.10 | 0.30 (25) / 0.24 (369) / 0.46 (400) |
| Holland H1 | ρ 0, both models (GlobCurrent as run) | 148 (4,338) | 35.73 S 92.41 E | 102 | -0.60 (n/e) | 18,557 (60,448) | -0.21 | 0.35 (20) / 0.23 (331) / 0.42 (366) |
| Holland H2 | **ρ 0.25, both models, product-relative (proposed)** | 377 (1,599) | 35.87 S 92.30 E | 87 | -0.66 (0.17) | 16,895 (50,071) | -0.14 | 0.10 (57) / 0.28 (91) / 0.61 (238) |
| Holland H2 | ρ 0.25, GLORYS12 only (in force) | 293 (1,599) | 35.86 S 92.34 E | 88 | -0.43 (0.18) | 14,678 (50,071) | -0.07 | 0.09 (72) / 0.28 (69) / 0.62 (181) |
| Holland H2 | ρ 0, both models (GlobCurrent as run) | 330 (1,599) | 35.81 S 92.36 E | 91 | -0.75 (0.16) | 15,130 (50,071) | -0.20 | 0.11 (49) / 0.28 (81) / 0.61 (204) |

## Reading
1. **Under H, the 00:19 options barely differ in positional compatibility.** ln E[L_H] lies within ±0.5 of Held Out for every option,
   H1 and H2 included. H therefore adds almost nothing to the choice between the 00:19 options, including H1 against H2. The
   Pléiades data move the PDF; they do not pick an option.
2. **Under H, every option moves to about 35.4-35.9 S, 91.9-92.4 E**, 70-110 NM from its flight-only mean. This is the same region as
   run C.
3. **Tension is mild for the standard options** (ln S between −0.54 and +0.09, p 0.26-0.43). It is larger for H1/H2 (ln S −0.42 to
   −0.81). For H1 p is not estimable at two of the three settings: d_shared ≤ 0, because the H1 flight-only histogram rests on 4,690
   effective impacts on a 592,000-cell grid.
4. **H1/H2 under H are NOT CONVERGED.** The effective impacts under H are 142-228 (H1) and 346-440 (H2), against the 1,000 gate.
   A1 under H1/H2 under H has 19-72. Treat every H1/H2 row as indicative only.
   The H1/H2 90 % regions (about 18,000-21,000 km² under H; about 60,000 km² without H, against 556,000 for Held Out) are
   **narrow because the samples are few**: a histogram of a few hundred effective impacts on a 0.05° grid concentrates artificially.
   They are not a measured precision and must not be compared with the standard options' areas.

## COVERAGE
- **(a) Feasible set, (b) model reach:** end of flight's `results/eof-holland-sweep-run-d-oct11` COVERAGE applies; this note adds no
  sampling. Carried gaps:
  - A1 under H1/H2 (136 / 59 effective impacts before H);
  - descents above the piloted envelope and stepped shapes not eligible for push-over (end of flight's declared gap);
  - core run D not converged.
- **(c) Proposal coverage under H** (effective impacts, primary, proposed headline setting):

| 00:19 option | without H | under H | status |
|---|---|---|---|
| Held Out | 6,378,686 | 460,316 | met |
| R600 BTO Only | 8,377,630 | 509,039 | met |
| R600 BTO + Raw BFO | 190,237 | 18,173 | met |
| Holland H1 | 4,690 | 192 | **GAP: below the 1,000 gate** |
| Holland H2 | 2,234 | 440 | **GAP: below the 1,000 gate** |

- **Proposed fix for the H1/H2-under-H gap:** end of flight's H1/H2 proposal concentrates on the burst timing, not on the Pléiades
  region. The options are (i) more seeds of the arm C recipe (ESS scales with parents) or (ii) a defensive-mixture proposal toward
  the Pléiades-compatible end states, with exact re-weighting. Both are end of flight's to choose; the request is raised in
  END_OF_FLIGHT.md.
- **Parameter bounds:** unchanged from run C (windage 0-5 % U10; transport error measured ~95-120 km per component at 15 d; ρ 0 / 0.25 /
  0.5 measured range 0.07-0.41; drift audit F1 offset 0.60-0.75 % U10).
