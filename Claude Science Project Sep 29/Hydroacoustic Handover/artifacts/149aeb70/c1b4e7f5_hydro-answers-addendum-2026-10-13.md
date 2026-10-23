# Addendum: six checks run on 13 Oct 2026

## 1. Which run the figures used, and how run I and run I dive differ

My figures used **run I** (`mh370-exchange/end-of-flight/run-i`), not run I dive. I took the primary
run without checking whether the dive run suited the question better. It may.

| | run I | run I dive |
|---|---|---|
| Impacts | 102,399,904 (4 strata x 8 seeds) | 127,999,840 (waypoints stratum doubled) |
| Proposal | standard | aimed at the push-over to the surface |
| Differences in config | — | `burst_target_weight` 0.8 to 0.5; adds `burst_target_weight2` 0.35 over a second window −7 to −1 s; adds `pushover_rate_aim` 18,000–40,000 ft/min, `pushover_n_floor_aim` 0.15–0.45 g, `pushover_to_surface_probability` 0.5; sea-level static thrust 415,450 N to 406,800 N |
| Median peak radiated power | 3.474e8 W | 4.013e8 W |
| Loud-decile threshold | 4.678e10 W | 6.428e10 W |
| Effective impacts, both/no-offset | 5,189 | 3,032 |
| Effective impacts, both/startup-offset | 20,753 | 9,003 |
| Effective impacts, loud decile, both/no-offset | 762 | 951 |
| Effective impacts, loudest 1%, both/no-offset | 70 | 250 |
| Effective impacts, loudest 1%, both/startup-offset | 284 | 983 |

The aimed proposal does what it was built to do: it trades overall efficiency for coverage of the
steep push-over class, so the dive run has **fewer** effective impacts overall on the two
both-reading options and **more** in the loud tail, which is the part hydroacoustics needs. The two
runs are different proposals of the same model and must not be pooled without a declared rule.

## 2. What the 00:19 option names mean

From the run's own terminal configuration:

| Option | Satellite data used |
|---|---|
| none | nothing from 00:19 |
| r600 | 00:19:29 range (BTO) and frequency (BFO) |
| r1200 | 00:19:37 frequency (BFO) only |
| both | 00:19:29 range and frequency, plus 00:19:37 frequency |

Holland's two hypotheses are the **both** options. The r1200 option is not a rival hypothesis: it is
the same second-burst reading with the first burst dropped. Probability in the loud decile is 0.110
for r600, 0.121 for r1200 and 0.029 for both, so it is the **conjunction** of the two bursts that
suppresses the loud class, not either burst alone.

## 3. Nothing constrains the impact time

`latent:timed_out` is 0 for every particle checked. Weighted impact times under the held-out
baseline run from 00:18 to 01:40, with quartiles at 00:28 and 00:42 and a median at 00:36. The
median impact time is an outcome of the weights, not a constraint, and my earlier wording was wrong.

## 4. Where the "pulls out of the dive" result comes from

Family codes: A1 = 1 (uncontrolled after fuel exhaustion), A2 = 2 (controlled or arrested),
B-controlled = 3, A-then-lost = 4, B-then-lost = 5, B-uncontrolled = 6.

Share of each family whose dive runs on into the water within 180 s of 00:19:37:

| Family | baseline share | baseline dive-on | both/no-offset dive-on | r1200/no-offset dive-on | r600/no-offset dive-on |
|---|---|---|---|---|---|
| A1 uncontrolled | 0.115 | 0.302 | 0.293 | 0.673 | 0.424 |
| A2 controlled | 0.201 | 0.024 | 0.010 | 0.011 | 0.007 |
| B controlled | 0.272 | 0.032 | 0.005 | 0.002 | 0.001 |
| A then lost | 0.145 | 0.216 | 0.069 | 0.272 | 0.279 |
| B then lost | 0.268 | 0.125 | 0.070 | 0.107 | 0.111 |

The overall figure of 5 to 6 in 100 is therefore **mostly the family prior**, not the 00:19 data: A1
carries only about 11 in 100 of the weight, and the controlled families almost never dive on. Inside
A1, the case the Boeing simulations describe, the both-reading options leave the dive-on fraction
where the prior put it (0.293 against 0.302), while the r1200 reading more than doubles it to 0.673.
Note that both/no-offset has only 746 effective parents in the loud decile, so its loud-tail numbers
are not estimable and are quoted here as diagnostics only.

## 5. Blocked paths by latitude

From the module's own path table, computed at five quantiles of an earlier impact distribution,
imp025 being the southern end and imp975 the northern:

| Path | land crossed (km) | shallowest point (m) | km of path shallower than 1,000 m |
|---|---|---|---|
| imp025 to Scott Reef | 199 | −275 (above water) | 1,060 |
| imp250 to Scott Reef | 198 | −100 (above water) | 1,005 |
| imp500 to Scott Reef | 0 | 1 | 1,002 |
| imp750 to Scott Reef | 0 | 1 | 977 |
| imp975 to Scott Reef | 0 | 35 | 918 |
| all five to Portland 3274 | 0 | 1,470 to 3,248 | 0 |

**Scott Reef has no usable latitude.** Moving north stops the path crossing land but puts it over the
Australian shelf in 1 m of water, and between 918 and 1,060 km of every path lies shallower than
1,000 m, which is above the sound channel. **Portland is clear at every latitude tested**, with no
land and no part of any path shallower than 1,000 m. A continuous latitude sweep needs the module's
bathymetry and is a small job for it.

## 6. What was actually tested on run I

Nothing. On run I the module wrote per-impact columns and ran data checks. The Kadri Table 1 test,
the H01W x H08S pair tests on the digitised Cape Leeuwin and Diego Garcia South traces, the H08S
shot-train tests, the IMOS coincidence test with 98 background realisations and the
injection-recovery study were all run against **earlier** impact sets: an interim end-of-flight set
and an earlier core run. So option A is not "already done" on run I; the machinery exists and has
been exercised, but not against the current impact set.
