# The Pléiades / COSMO-SkyMed conditional branch on end of flight's reference-289 impacts, before and after the seabed search

Pléiades module, 9 Oct 2026, under the architecture entry of ~18:30 UTC (Pete's decisions).

**Every PDF here is conditional on H**, "the observed objects are debris from 9M-MRO". There is no Bayes factor and no
P(H | D) (P1).

## Inputs and provenance (run-provenance convention)

| | |
|---|---|
| Impacts | End of flight `eof-289-full`, seeds 1–4: 12,799,968 impacts, read in place from `/Users/pete/Downloads/mh370-exchange/end-of-flight/eof-289-full/seed-<k>/impacts.npy` |
| Run | `reference-289`; prior track **289.7°** at 18:01:49, read from `run.json` |
| 00:19 data option | `none` (held out), as searched areas uses it; weight × exp(loglik:none) |
| Dive class / glide | End of flight's provisional class (b); Boeing-calibrated glide (Pete's reference, ~18:30) |
| Search evidence | The searched-areas module's own per-impact `seabed-search:loglik` (run.toml base: Phase 2 + Bluefin-21, ρ = 0.05), from `mh370 evaluate` on the same impacts. It is never recomputed here |
| Pléiades likelihood | This module's hook: measured spread, GLORYS12 + GlobCurrent at equal weight. Headline arm ρ4 = 0, equal weights |
| COSMO likelihood | This module's new prediction columns (not a likelihood term): F1–F3 (C3) and F1–F4 (C4), equal contact weights, the dawn-20Mar and dusk-21Mar passes equally weighted inside each ocean model |
| Combination | P+C is formed per ocean model, because one ocean drives both, then averaged over the two models |
| Grid | 0.05°, 85–103 E, 43–25 S. Per seed, 1.5–2.0 % of the impact weight lies outside it (north or east) and is not scored |
| Release tables | Enlarged to 85–103 E, 43–25 S. 0.15 % of the grid, along the 25 S edge, is not computed (a track leaves a forcing field); it is treated as zero likelihood |

**Check.** The searched-areas column reproduces that module's own evidence: seed 1 retains Z = 0.7330 of the
unconditional mass, against its pooled 0.7335.

## The conditional PDFs (ocean-model average, pooled over 4 seeds, seed ranges in brackets)

The unconditional flight posterior on this grid has a 90 % HDR of 620,510 km² before the search and 730,426 km²
after it. The HDR grows because the search hollows out the core. The median latitude moves from −36.71 to −36.51
(seed 1, from the impacts), and the search retains 0.729 of the mass.

| Field | Stage | Median lat (°) | Mean lat, lon (°) | Mean shift from the flight posterior, NM | 90 % HDR, km² | Flight mass in the conditional HDR | ln S | Search retained under H |
|---|---|---|---|---|---|---|---|---|
| P | before search | -35.37 | -35.38, 91.59 | 62 (58–71) | 109,681 | 0.34 | 0.77 (0.60 to 0.80) | 1.000 |
| P | after search | -35.24 | -35.22, 91.52 | 62 (59–68) | 99,508 | 0.31 | 1.07 (0.95 to 1.09) | 0.730 |
| C3 | before search | -35.34 | -35.36, 91.85 | 66 (61–76) | 88,138 | 0.27 | 0.83 (0.65 to 0.88) | 1.000 |
| C3 | after search | -35.22 | -35.22, 91.78 | 59 (55–68) | 83,527 | 0.26 | 1.08 (0.95 to 1.10) | 0.704 |
| C4 | before search | -35.42 | -35.46, 91.57 | 57 (54–66) | 104,949 | 0.34 | 0.81 (0.65 to 0.85) | 1.000 |
| C4 | after search | -35.30 | -35.31, 91.48 | 57 (55–63) | 95,241 | 0.31 | 1.09 (0.97 to 1.11) | 0.714 |
| P+C3 | before search | -35.28 | -35.27, 91.83 | 71 (66–82) | 50,821 | 0.16 | 1.01 (0.86 to 1.05) | 1.000 |
| P+C3 | after search | -35.20 | -35.18, 91.66 | 62 (59–71) | 49,925 | 0.17 | 1.30 (1.20 to 1.33) | 0.709 |
| P+C4 | before search | -35.30 | -35.29, 91.72 | 68 (64–79) | 58,900 | 0.18 | 1.00 (0.85 to 1.03) | 1.000 |
| P+C4 | after search | -35.22 | -35.20, 91.54 | 62 (59–70) | 57,306 | 0.20 | 1.31 (1.21 to 1.34) | 0.726 |

**Ranges over every object-rating × cluster-weight arm, ocean model and stage:**
- ln S is +0.46 to +1.36;
- the χ² tension probability is 0.63–1.0;
- the search retains 0.674–0.742 of the conditional mass.

## Reading

1. **Every conditional sits at about 35.2–35.4° S, 91.5–91.9° E.**
   - That is 57–71 NM north-east of the flight posterior's mean (54–82 NM across seeds), near the northern of its two
     modes.
   - The Pléiades-only, COSMO-only and combined conditionals agree to within about 0.15° in median latitude.
   - Combining P with C3 roughly halves the conditional HDR, from 109,681 to 50,821 km².
2. **No tension.** ln S is positive in every field, arm, seed and stage: the flight posterior and each observation
   set agree.
3. **Under H, the seabed search removes about the same share as without it.**
   - It retains 0.67–0.74 of the conditional mass, against 0.73 unconditionally.
   - The conditional moves about 0.1° north after the search (P median −35.37 → −35.24).
   - The conditional region straddles the Phase 2 corridor (figure, row 2), so the search hollows it rather than
     relocating it.
   - **Under H, the unsearched remainder lies on both flanks of the Phase 2 corridor**, within the same
     region.
4. **Common origin.** P against C, on a flat prior over the grid, each likelihood alone (`common-origin.csv`):
   - ln S is +1.04 to +1.09 for C3 and +1.05 to +1.08 for C4;
   - the H-alone means lie 1–17 NM apart;
   - 98 % of the joint mass lies inside the COSMO-alone 90 % HDR.

   **The two independently observed sets are therefore consistent with a common origin, conditional on their being
   debris.** But the test has little power:
   - each contact lies 49–81 km from its nearest rating-5 Pléiades cluster;
   - both sets are back-tracked 15–17 days through the same ocean, with errors of about 100 km per component.

   Only origins separated by much more than about 200 km would register as inconsistent. Adding F4 (50 km from the
   nearest cluster) changes little.

## Hydroacoustics under H (for the hydroacoustics module; `h01w-arrivals-under-H.csv`)

The table gives the great-circle range and bearing from H01W to the source, taking H01W at 114.142637 E, 34.890303 S
(Cape Leeuwin, the coordinates used in `crates/ocean/examples/ocean_paths.rs`).
- Each impact's own time comes from end of flight.
- Arrival times are computed at 1.48 km/s; 1.49 km/s gives arrivals about 10 s earlier.
- Values are 5 / 50 / 95 % after the search, with the ocean-model average and the ρ4 = 0, equal-weight arm.
- They come from a 25 % subsample of each seed.

| Field | Range, km | Bearing from H01W (°) | Impact UTC | Arrival UTC at H01W |
|---|---|---|---|---|
| uncond | 1483 / 2069 / 2347 | 247.8 / 258.0 / 297.8 | 00:15:19 / 00:40:51 / 01:08:20 | 00:38:44 / 01:03:58 / 01:30:42 |
| P | 1897 / 2061 / 2219 | 258.2 / 262.4 / 266.9 | 00:14:04 / 00:31:11 / 00:56:13 | 00:37:18 / 00:54:18 / 01:19:23 |
| C3 | 1880 / 2043 / 2170 | 258.3 / 262.5 / 266.6 | 00:14:03 / 00:31:03 / 00:56:17 | 00:37:12 / 00:53:51 / 01:19:05 |
| P+C3 | 1915 / 2057 / 2146 | 259.5 / 262.6 / 265.7 | 00:13:57 / 00:29:23 / 00:55:24 | 00:37:14 / 00:52:17 / 01:18:23 |

Under H, the source bearing narrows from 248–298° to about 258–267°, and the range narrows to 1,900–2,200 km. The
impact time is not narrowed, because it comes from end of flight's glide and descent, which H does not constrain.

## Caveats

- **Dive class.** The impacts carry end of flight's provisional dive class. Pete has called its implementation
  poor against Boeing's set, and end of flight is rebuilding it.
- **Search case.** This is the base case: point-target placeholder, ρ = 0.05, as searched areas uses it. The Ocean
  Infinity 2018 variant is not applied here.
- **OSCAR comparison** is to be run once ocean transport provisions OSCAR as a comparison product.
- **Earlier results.** The rerun_reference-based results (`rerun-289/`) used core's 00:19:37 particles convolved
  with a descent kernel, on a smaller domain. These impact-based results supersede them for reference-289.

— Pléiades module


## Across the 00:19 options (added 9 Oct ~20:30 UTC; Pete's priority order, architecture ~19:50)

The options are shown side by side and are **never mixed by evidence**, because they use different data.
- Priority (1), held out, is the headline above.
- Priority (2), R600 only (raw), is `r600/no-offset`. Its ESS is 197,569, so its contours are noisier.
- Holland H1 and H2, priorities (3) and (4), use both bursts. They stay "not estimable" until end of flight
  settles the hand-off question.
- `inflated` is the project's sensitivity.

The table shows the ρ4 = 0, equal-weight arm, averaged over both ocean models and pooled over the seeds
(`branch-by-0019-option.csv`; full tables in `r600-no-offset-branch.csv` and in `runs/` for the inflated options).

| 00:19 option | Field | Stage | Median lat | Mean lat, lon | Shift, NM | Conditional 90 % HDR, km² | Flight 90 % HDR, km² | ln S | Search retained under H |
|---|---|---|---|---|---|---|---|---|---|
| none (held out) | P | before search | -35.37 | -35.38, 91.59 | 62 | 109,681 | 620,510 | 0.77 | 1.000 |
| none (held out) | P | after search | -35.24 | -35.22, 91.52 | 62 | 99,508 | 730,427 | 1.07 | 0.730 |
| none (held out) | P+C3 | before search | -35.28 | -35.27, 91.83 | 71 | 50,821 | 620,510 | 1.01 | 1.000 |
| none (held out) | P+C3 | after search | -35.20 | -35.18, 91.66 | 62 | 49,925 | 730,427 | 1.30 | 0.709 |
| r600/no-offset (R600 only, raw) | P | before search | -35.72 | -35.78, 91.95 | 63 | 65,069 | 235,099 | 0.14 | 1.000 |
| r600/no-offset (R600 only, raw) | P | after search | -35.83 | -35.79, 92.08 | 21 | 74,270 | 296,548 | -0.21 | 0.392 |
| r600/no-offset (R600 only, raw) | P+C3 | before search | -35.52 | -35.53, 92.22 | 83 | 34,543 | 235,099 | 0.39 | 1.000 |
| r600/no-offset (R600 only, raw) | P+C3 | after search | -35.57 | -35.61, 92.24 | 33 | 41,724 | 296,548 | -0.34 | 0.346 |
| r600/inflated | P | before search | -35.84 | -35.86, 92.03 | 85 | 72,394 | 339,856 | 0.01 | 1.000 |
| r600/inflated | P | after search | -35.98 | -35.89, 92.22 | 73 | 83,537 | 426,730 | -0.45 | 0.435 |
| r600/inflated | P+C3 | before search | -35.58 | -35.60, 92.28 | 105 | 39,205 | 339,856 | 0.16 | 1.000 |
| r600/inflated | P+C3 | after search | -35.71 | -35.70, 92.35 | 86 | 46,492 | 426,730 | -0.64 | 0.385 |
| r1200/inflated | P | before search | -35.36 | -35.36, 91.66 | 24 | 52,538 | 171,654 | 0.52 | 1.000 |
| r1200/inflated | P | after search | -35.22 | -35.15, 91.62 | 59 | 49,557 | 204,819 | 1.18 | 0.559 |
| r1200/inflated | P+C3 | before search | -35.28 | -35.23, 91.93 | 39 | 22,888 | 171,654 | 0.77 | 1.000 |
| r1200/inflated | P+C3 | after search | -35.19 | -35.12, 91.74 | 53 | 22,364 | 204,819 | 1.34 | 0.546 |

**Reading.**
- **The 00:19 option changes the post-search answer under H much more than any Pléiades or COSMO choice does.**
- **With R600 scored (raw):**
  - The flight posterior is narrower (90 % HDR 235,000 against 621,000 km²).
  - The seabed search removes **61–65 %** of the conditional mass under H, against 27–29 % when the 00:19 messages
    are held out. Retained: 0.35–0.39, against 0.71–0.73.
  - ln S turns slightly negative after the search (−0.21 for P, −0.34 for P+C3). This is not significant tension,
    but it is the only option in which the search pushes H against the flight posterior.
- **With R1200 inflated:** the search retains 0.55–0.56, and ln S stays positive.
- So whether "Pléiades debris, not yet found" is still plausible on unsearched ground depends chiefly on how the
  00:19:29 R600 message is treated.
