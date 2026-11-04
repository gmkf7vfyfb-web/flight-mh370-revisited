# Boeing dive fits to the 00:19 satellite data: impact times and outer bound

Date: 4 November 2026. Branch claude-science-sep29, folder results/hydroacoustics/reverse-dive-window-2026-11-04/.
Purpose: give the hydroacoustic reverse search an impact (source) time window, conditional on the Boeing dive cases.

## Result

1. The four alternate-configuration Boeing dives (runs 3, 4, 6, 10) reach the sea at **00:19:58 to 00:22:18 UTC**. This span covers both treatments of the 00:19 frequencies and every alignment within a misfit of 4 of each run's best.
2. The ruled source-time window, 00:19:38 to 00:29:44, contains all these fits. The margin is **20 s** at the early end and **7 min 26 s** at the late end.
3. Only run 3 fits well (misfit 4.0 with Holland transient bias added, 5.9 as observed). Its impact is 00:19:58 to 00:20:05. Run 3 needs a power loss 390 to 397 s before 00:19:29, which is in the far tail of the log-on delay model (95 % range 51 to 215 s).
4. Runs 4 and 10 fit marginally with Holland transient bias added (misfit 21 and 27) and poorly as observed (32 and 35). Their impacts are 00:21:57 to 00:22:18, at a delay of 157 to 167 s.
5. Run 6 fits poorly under both treatments (misfit 93 and 116). Its impacts are 00:20:08 to 00:21:06.
6. Adding the log-on delay model to the misfit does not move any best delay or impact-time range (table rows marked 'gamma(8, 14.875 s) used').
7. Run 5 (normal configuration, sensitivity) has no fit: misfit 296 to 356 under every treatment and every one-engine phase of 4 to 14 min, with the 00:19:37 point at the 19.5 S grid limit. Its 'best' impact, 00:29:12 to 00:29:15, is 29 s inside the window end. This number comes from a non-fit and has no weight.

## Impact time and offset per run and treatment (log-on delay model not used)

Offsets are from the 00:19:37 position to the sea contact. Along-track is positive in the direction of the 00:10:59 track. Cross-track is positive to the right of that track.

| Run | 00:19 frequencies | Misfit | Delay to 00:19:29, s (best; range) | Impact UTC (best; range) | Along-track NM (best; range) | Cross-track NM (best; range) | 00:19:37 latitude |
|---|---|---|---|---|---|---|---|
| 3 | Holland transient bias added | 4.0 | 391; 390-397 | 00:20:04; 00:19:58-00:20:05 | -0.2; -0.2 to -0.0 | -0.2; -0.2 to -0.2 | 32.96 S |
| 3 | as observed | 5.9 | 390; 390-390 | 00:20:05; 00:20:05-00:20:05 | -0.2; -0.2 to -0.2 | -0.2; -0.2 to -0.2 | 33.88 S |
| 4 | Holland transient bias added | 20.8 | 162; 158-165 | 00:22:00; 00:21:57-00:22:04 | -4.8; -5.3 to -4.4 | -4.5; -4.6 to -4.3 | 38.89 S |
| 4 | as observed | 32.1 | 157; 157-158 | 00:22:05; 00:22:04-00:22:05 | -5.4; -5.4 to -5.3 | -4.2; -4.3 to -4.2 | 38.50 S |
| 6 | Holland transient bias added | 93.2 | 150; 149-152 | 00:21:05; 00:21:03-00:21:06 | -6.6; -6.7 to -6.6 | -4.2; -4.3 to -3.9 | 35.60 S |
| 6 | as observed | 115.9 | 207; 207-207 | 00:20:08; 00:20:08-00:20:08 | -2.0; -2.0 to -2.0 | 2.4; 2.4 to 2.4 | 19.95 S |
| 10 | Holland transient bias added | 26.6 | 162; 161-167 | 00:22:16; 00:22:11-00:22:17 | -2.0; -2.1 to -1.3 | -7.1; -7.2 to -7.0 | 39.09 S |
| 10 | as observed | 34.8 | 160; 160-161 | 00:22:18; 00:22:17-00:22:18 | -2.2; -2.2 to -2.1 | -7.0; -7.0 to -7.0 | 38.99 S |
| 5 | Holland transient bias added | 331.7 | 437; 436-438 | 00:29:13; 00:29:12-00:29:14 | 22.7; 22.7 to 22.7 | 6.4; 6.3 to 6.4 | 19.49 S |
| 5 | as observed | 310.1 | 436; 435-437 | 00:29:14; 00:29:13-00:29:15 | 22.7; 22.7 to 22.7 | 6.4; 6.4 to 6.5 | 19.51 S |

The full table, with residuals, descent rates, Holland transient bias values, positions and the delay-model rows, is dive-impact-time-fits.csv. The impact time for any delay without the satellite data is in dive-impact-time-vs-delay-no-fit.csv.

## Outer bound as a sensitivity against the ruled window (00:19:38 to 00:29:44)

| Case | Impact span UTC | Inside ruled window? |
|---|---|---|
| Alternate runs, all fits (misfit within 4 of best) | 00:19:58 to 00:22:18 | Yes; margins 20 s early, 446 s late |
| Alternate runs, misfit 30 or less | 00:19:58 to 00:22:17 | Yes |
| Alternate runs, misfit 11.1 or less (run 3 only) | 00:19:58 to 00:20:05 | Yes |
| Run 5 (normal), no fit | 00:29:12 to 00:29:15 | Yes, by 29 s |
| Alternate runs, delay model only (no satellite data), 95 % | 00:20:01 to 00:25:43 | Yes |
| Normal runs 1, 2, 5, 7, 8, 9, any delay 30-510 s (no satellite data) | 00:28:00 to 00:43:07 | Mostly no |

Judgement: the ruled window contains every dive that fits the 00:19 frequencies, under both treatments. The early margin (20 s) is small but physical: the aircraft must still transmit at 00:19:37, and the earliest fitted contact is 21 s after that. The late end has wide spare margin for the alternate configuration. The window would not contain normal-configuration glides if the 00:19 frequencies were held out: those reach the sea at 00:28:00 to 00:43:07. So the window is conditional on the 00:19 frequencies (either treatment), which exclude the normal configuration.

## Method (reused, not rebuilt)

1. Code: the 2 Nov 2026 configuration-fit functions, copied verbatim (dive_fit_lib.py). Parity check: the earlier best misfits (run 3: 5.9 / 4.6; run 4: 34.3 / 20.8; run 6: 131.1 / 93.2; run 10: 34.8 / 26.6) reproduce exactly on the earlier grid.
2. Each Boeing trace (1 s X, Y, altitude) is placed with its 00:10:59 point on the 00:10:59 timing arc, then turned through -30 to +30 degrees of track. Main power is lost at the first engine stop (alternate) or the second (normal). The power loss is set 30 to 510 s before 00:19:29.4 in 1 s steps.
3. Changes from 2 Nov: the 00:10:59 latitude grid is widened from 30-40 S to 19.5-41 S, and the delay grid from 40-400 s (2 s steps) to 30-510 s (1 s steps). 510 s is a hard limit: the satellite unit answered at 00:10:59, so main power was on then.
4. Misfit = chi-squared on the burst timing offsets at 00:19:29 (sigma 63 us) and 00:19:37 (43 us, empirical offset applied) and the burst frequency offsets at 00:10:59, 00:19:29 and 00:19:37 (sigma 7 Hz). The frequency bias is fitted under a 150 +/- 5 Hz prior.
5. Treatment (a), Holland transient bias added: a transient bias is fitted within Holland's 17 to 136 Hz at 00:19:29 and is 0 to 6 Hz smaller at 00:19:37 (Holland 2017, arXiv:1702.02432). Treatment (b): both frequencies as observed.
6. Pete's 18 Oct rule: an alignment that puts the first engine stop before 00:10:59 is kept only if the descent rate at 00:10:59 is 800 ft/min or less. For the alternate runs no fitted alignment puts the first engine stop before 00:10:59. For run 5 (as flown, delay 30-510 s) the rule removes 682 of 14,911 alignment cells (delay x track turn).
7. Sea contact = end of record (473 to 1,131 ft) plus the remaining height at the mean descent rate of the last 10 s (at least 1,000 ft/min). The horizontal offset continues at the last 10 s ground velocity. Simulator wind is kept as flown.
8. Ranges: all delays with a profile misfit within 4 of the run's best. At each delay, the best latitude and track turn are used.

## Checks and caveats

1. Track-turn limit. Runs 4 and 10 reach the -30 degree limit (00:10:59 track 149 degrees). A test with -60 to +60 degrees lowers their misfit by at most 1.5 and moves their delay ranges by no more than 3 s. So impact times do not change by more than about 3 s.
2. Run 6 as observed and run 5 put the 00:19:37 point at the 19.5 to 20.0 S grid limit, north of the ruled 20-41 S arc span. Both are poor fits.
3. Run 3 reaches the sea only 27-28 s after 00:19:37, at 0.3 NM from the 00:19:37 point (0.52 NM of path in a steep spiral from 15,668 ft).
4. Dive speeds near Mach 1.0 are outside Boeing's simulator data. The late-dive timing is therefore indicative.
5. The fits use the six data items only. The misfit levels (dof about 2) say that only run 3 matches both 00:19 frequencies well. Runs 4 and 10 need Holland transient bias added to approach an acceptable fit.
6. The 'misfit' bound of 11.1 (about 95 % for 5 items) is the reference used on 2 Nov. It is a rough guide only.
