# Australian non-recovery: the populated-coast restriction (Pete's ruling, 15 Oct 2026)

15 Oct 2026, ocean drift module. Addendum to `debris-drift-australia-sensitivities.md`. No transport was run; the
full 120-160 E run was not started.

> Reach-limited pilot, 15-120 E, GLORYS12 only. Debris that would travel east of 120 E is not tracked, which is
> the population this term is about. Not to be composed until the full pilot runs.

## Pete's ruling

Only coasts where people live can support the statement that debris did not arrive. A deserted beach that received
debris would not have produced a find, so its silence is not evidence. The term should therefore be tested inside
the existing 15-120 E domain on the populated coasts, and the posterior should be modified on that evidence alone.

## What the pilot already says about it

Inside the domain, exactly one populated Australian segment receives debris: **AU-wa-city-inner, the Perth to Augusta coast
(Perth, Rockingham, Mandurah, Bunbury, Busselton, Augusta; 114.8-115.9 E, 31.2-34.7 S), about 1,216 km of coast samples** (ABS RA 2021 major city and inner regional). The south and
north-east city segments lie east of 120 E and receive 0.0 per cent by construction, not by transport.

Arrival probability, mean over the three object classes, per source latitude band:

| source latitude | populated WA coast (Perth to Augusta) | all six coasts where debris was found | all Australian coasts |
|---|---|---|---|
| 37-42 S | 4.94 % | 5.03 % | 18.63 % |
| 34-37 S | 2.73 % | 10.06 % | 11.50 % |
| 31-34 S | 0.96 % | 12.86 % | 4.69 % |
| 28-31 S | 0.46 % | 13.71 % | 2.14 % |
| 25-28 S | 0.13 % | 13.48 % | 0.70 % |
| 20-25 S | 0.02 % | 10.70 % | 0.32 % |

**For sources at 37-42 S, that one populated stretch receives as many floating objects as all six find coasts
combined (4.94 against 5.03 per cent).** Those six coasts produced about twenty identified
pieces. The populated-coast restriction therefore does not weaken the term by much.

## The restriction, reconstructed

The pilot did not store a populated-only column, so this is a **reconstruction, not a run**, and it is post hoc:
the option was defined after the pilot result was seen. The per-node change is predicted by the law the model
implies, Delta = -k ln(1 + W / (c F)), where W is the detection-weighted Australian arrival and F the find-coast
arrival. Fitted to the measured B and C columns: k = 3.50, c = 0.204. Held-out check: fitted on B
alone it predicts C with a residual of +0.07 nat (standard deviation 0.50, against split-half Monte Carlo noise of
0.30-0.45 on the change itself), and it returns the measured shift of B as +2.41 deg against the measured +2.43.
A linear law in the weighted arrival was tried first and rejected: it misses C by 0.60 nat in the mean, because the
response saturates in the detection level.

| variant | drift-only median | 90 per cent interval | shift north of the mean latitude | change in log evidence | change in ln L, 37-42 S |
|---|---|---|---|---|---|
| term off (measured) | 30.2 S | 37.2 to 24.2 S | — | — | — |
| populated coast only (outer regional and remote off) | 28.2 S | 32.7 to 23.7 S | +2.02 deg | -0.61 nat | -6.30 |
| populated and outer regional (remote off) | 27.7 S | 32.2 to 23.7 S | +2.35 deg | -0.76 nat | -7.36 |
| option B, every Australian coast (measured) | 27.6 S | 32.2 to 23.7 S | +2.43 deg | -1.08 nat | -7.55 |

**Switching off every deserted coast keeps 83 per cent of the northward movement.** The term is not a
sum over many weakly watched beaches; it is carried by the one populated coast that southern debris reaches.
This also removes the main objection to the term: it no longer depends on the assumption that remote Australian
shores were watched from March 2014, because under this restriction they are not watched at all.

## What this means for the 120-160 E extension

Under the ruling, the extension is worth much less than it was. The coast immediately east of 120 E — the eastern
south coast of Western Australia and the Nullarbor shore of the Great Australian Bight — is remote or very remote
and would carry no weight. But the ruling does not remove the question entirely: **Adelaide, Melbourne and Hobart
are populated and lie east of 120 E** (segment AU-south-city-inner, about 1,629 km). Debris that leaves the domain
near 120 E in the Leeuwin and South Australian current system could reach them.

So one question survives, and it is narrow: does debris that crosses 120 E reach the populated south-east coast
within the window, or does it stay in the Bight and the Southern Ocean? That does not need a 30-34 hour both-model
run at all 710 nodes. Two cheaper routes, in order of cost:

1. **Global Drifter Program check, no model run, no heavy lock.** The GDP data are already on disk. Count the
   undrogued drifters that cross 120 E south of Australia and ask where and when they beach. If almost none reach
   populated south-eastern coast within about two years, the reach limit is closed by observation and the
   populated-only term is complete as it stands.
2. **A targeted eastern run**, only if (1) is ambiguous: the 160 E fields are already on disk, and a run restricted
   to the southern nodes that actually export particles east of 120 E is a fraction of the full pilot.

## The drifter check, run 15 Oct 2026: the coast east of 120 E is not all deserted

Global Drifter Program 6-hourly quality-controlled drifters, undrogued rows only, from the module's existing
20-140 E set joined to a 138-156 E extract downloaded today. Cohort: the first eastward crossing of 120 E between
30 and 45 S, followed for 845 days, the length of the MH370 window; n = 196 crossings over 1995-2025. Arrival is a
position inside the module's own coastal segment boxes, the same proxy the drift model uses, not a beaching test.

| coast reached within 845 days of crossing 120 E | share of the 196 |
|---|---|
| populated south-east (Adelaide, Melbourne, Hobart) | 12 of 196, 6.1 % |
| southern outer regional | 13 of 196, 6.6 % |
| southern remote, including the Bight | 25 of 196, 12.8 % |
| Western Australia remote | 35 of 196, 17.9 % |

Of the 112 that were still tracked east of 138 E, 12 — 10.7 per cent — entered the populated south-east boxes.
Median transit from 120 E to first entry was 236 days (range 135 to 813), comfortably inside the window, and the
crossing latitudes of those that arrived were 38.5 to 44.9 S, median 41.0 S: the southernmost exits, which is
exactly where the term acts. These are **lower bounds**: tracking after crossing lasted a median of 170 days
against the 845-day horizon, so arrivals after a drifter stopped reporting are not counted. Undrogued drifters
carry roughly 1-2 per cent windage, less than high-windage debris, so they are an imperfect analogue.

**This reverses the expectation.** At 37-42 S, 41.9 per cent of modelled particles leave the domain; at the
observed 6.1 per cent arrival rate that adds 2.6 percentage points of populated arrival to the 4.94 per cent
already counted on the Perth to Augusta coast, multiplying the populated-coast term by about 1.5; on the
conditional rate it is about 1.9. The Nullarbor and the Bight are deserted, as expected, and carry nothing — but
Adelaide, Melbourne and Hobart are populated, they are reached from the southern exits within the window, and no
debris was found there either. **Extending the domain east would therefore strengthen the populated-coast term and
move the estimate further north, not weaken it.** A targeted eastern run on the southern nodes is now justified on
this evidence; the full 710-node both-model run still is not.

## COVERAGE

(a) Feasible set: impacts as in run I (NOT CONVERGED). (b) Model reach: 175 scored pilot nodes; populated Australian
coast inside the domain is one segment of 1,216 km; populated coast east of 120 E is unreachable (GAP, now the only
part of the reach gap that matters under the ruling); refloat not modelled (GAP). (c) Proposal: the pilot's 1e5
particles per node; the populated-only and populated-plus-outer rows are RECONSTRUCTIONS with a held-out error of
+0.07 nat (standard deviation 0.50), not runs, and are post hoc. Parameter bounds: the pre-registered levels for the
measured rows; the reconstructed rows set outer regional and remote to zero, which is a bound, not a measurement.
