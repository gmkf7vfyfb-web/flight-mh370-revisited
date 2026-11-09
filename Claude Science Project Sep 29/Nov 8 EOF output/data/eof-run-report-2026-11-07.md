# End of flight: final run for publication (7 November 2026)

## A reproduction and extension of the Davey et al. (2016) end-of-flight treatment

**Davey plus fuel model and radar, continued from 00:11 to the sea; the no-pilot dives are drawn from real airliner dives and the Boeing 777 simulations; final run for publication, with the planned descent shown on the waypoint route.**

## Summary
- This run replaces all earlier end-of-flight results. It uses 16 seeds of the Davey model with the fuel model and 24 seeds of the waypoint model.
- The no-pilot dives now come from a model built on 15 measured dive build-ups (real airliner dives and the four Boeing 777 alternate-power simulations).
- The dive model passed both pre-registered tests. Test A (case prior, leave one out): 0/15, 1/11 and 0/6 values outside the central 95 %. Test B (against each Boeing simulation): 15/16 values inside the central 90 %. Declared deviation: the pre-registration text says 10 T15 values; 11 were used; Test A was not re-run with 10 (declared, open).
- The median impact latitude is 36.4 to 37.2 deg S in every headline treatment and both route models.
- When both 00:19 frequencies are used, 0.86 to 0.93 of the impacts are within 25 NM of the 7th arc.
- The split between the no-pilot and piloted families is not decided by the data. It changes with the assumptions (see the variants table). Report it only as a conditional result.
- Impact energy and attitude come from a model whose dives reach about Mach 1.0. Their median energy (about 9.2 GJ) is at or above the top of the Boeing range (6.4-9.0 GJ). Use them downstream as a declared sensitivity.

## What was run
- Generator `a1gen_final.py`, dive kernel `dive_kernel.py`, case prior `case_prior.py`, specification [eof-final-spec.json]({{artifact:0a1e7103-a72b-478c-af7f-c902c9b6f7dd}}), pooling `pool_final.py`; all code in [eof-final-code-2026-11-07.tar.gz]({{artifact:529ba938-bb61-46d4-bb5b-e20865f785d9}}) (run folder `Downloads/mh370-exchange/end-of-flight/final-2026-11-07`). Case prior [case-prior.json]({{artifact:23536c22-4cdd-473f-8462-b34af052c8b6}}); pre-registration [prereg-case-prior-and-kernel-2026-11-07.md]({{artifact:7d6d3bb6-220b-4e7f-84a1-fa942dacad91}}); Test B table [test-b-kernel-vs-boeing.csv]({{artifact:7ce153cf-04f0-4742-9f7b-4dabdc406022}}).
- Start: Run J core hand-offs at 00:10:59 (conditional on engine power at 00:11). Davey model + fuel: no pilot and piloted after fuel exhaustion. Waypoints: the same plus the planned descent from 22:41.
- Treatments of the 00:19 data: 9 headline and 6 sensitivity treatments (spec). Log evidence is compared only inside the same data group.
- Independent review before production: verdict no-go with one blocker; all findings fixed or declared ([review-2026-11-07.md]({{artifact:21b5528c-8dcd-46d9-a1fe-49a925dd61e8}})).

## Results: Davey model with the fuel model (main configuration)
| 00:19 treatment | ln Z vs first of same data group (90% seed interval) | No pilot | Piloted | Planned | Latitude 5/50/95 % | Arc distance 50/95/99 % (NM) | Within 25 NM | Impact after 00:19:29, 50 % (min) | Energy 50 % (GJ) | No-pilot effective paths |
|---|---|---|---|---|---|---|---|---|---|---|
| Nothing used after 00:11 | reference | 0.50 | 0.50 | 0.000 | 39.0 / 36.6 / 30.3 S | 28 / 139 / 221 | 0.45 | 17.8 | 1.2 | 1293770 |
| Log-on event only (cause term, airborne at 00:19:37; no 00:19 measurement) | reference | 0.50 | 0.50 | 0.000 | 38.4 / 36.4 / 30.5 S | 15 / 74 / 110 | 0.67 | 16.7 | 1.2 | 341557 |
| Both 00:19 timings (Davey) | reference | 0.51 | 0.49 | 0.000 | 38.5 / 36.8 / 33.0 S | 13 / 69 / 96 | 0.73 | 17.2 | 1.1 | 507547 |
| Both timings + 00:19:29 frequency | reference | 0.72 | 0.28 | 0.000 | 38.1 / 36.7 / 32.0 S | 12 / 44 / 68 | 0.87 | 15.8 | 1.2 | 21362 |
| Both timings + both frequencies as recorded | reference | 0.52 | 0.48 | 0.000 | 38.2 / 36.6 / 32.7 S | 8 / 38 / 52 | 0.88 | 1.7 | 9.2 | 156 (provisional) |
| Both timings + both frequencies, Holland start-up offset (17 Hz floor) | +0.31 (+0.18 to +0.46) | 0.70 | 0.30 | 0.000 | 38.1 / 36.5 / 33.5 S | 6 / 31 / 46 | 0.93 | 1.8 | 9.2 | 1672 |
| Both timings + both frequencies, Holland start-up offset (zero floor) | +0.28 (+0.13 to +0.42) | 0.68 | 0.32 | 0.000 | 38.1 / 36.5 / 33.5 S | 6 / 32 / 46 | 0.92 | 1.8 | 9.2 | 1945 |
| Both timings + 00:19:29 frequency as recorded + offset on 00:19:37 only, 17 Hz floor (Ashton premise with Holland's acknowledge bounds) | -0.43 (-0.60 to -0.27) | 0.55 | 0.45 | 0.000 | 38.1 / 36.6 / 32.1 S | 7 / 34 / 47 | 0.90 | 1.4 | 9.2 | 489 (provisional) |
| Both timings + 00:19:29 frequency as recorded + offset on 00:19:37 only, zero floor (Ashton premise with Holland's acknowledge bounds) | -0.38 (-0.56 to -0.21) | 0.54 | 0.46 | 0.000 | 38.1 / 36.6 / 32.2 S | 7 / 34 / 47 | 0.89 | 1.5 | 9.2 | 644 |

## Results: waypoint model
| 00:19 treatment | ln Z vs first of same data group (90% seed interval) | No pilot | Piloted | Planned | Latitude 5/50/95 % | Arc distance 50/95/99 % (NM) | Within 25 NM | Impact after 00:19:29, 50 % (min) | Energy 50 % (GJ) | No-pilot effective paths |
|---|---|---|---|---|---|---|---|---|---|---|
| Nothing used after 00:11 | reference | 0.42 | 0.41 | 0.168 | 38.9 / 36.8 / 32.2 S | 28 / 119 / 182 | 0.46 | 16.7 | 1.1 | 1596225 |
| Log-on event only (cause term, airborne at 00:19:37; no 00:19 measurement) | reference | 0.46 | 0.43 | 0.111 | 38.3 / 36.9 / 32.9 S | 15 / 75 / 105 | 0.68 | 16.4 | 1.0 | 904714 |
| Both 00:19 timings (Davey) | reference | 0.50 | 0.45 | 0.048 | 38.4 / 37.0 / 34.6 S | 13 / 69 / 94 | 0.73 | 18.0 | 1.1 | 1001693 |
| Both timings + 00:19:29 frequency | reference | 0.79 | 0.19 | 0.019 | 37.8 / 37.0 / 34.8 S | 12 / 40 / 65 | 0.90 | 16.1 | 1.0 | 70082 |
| Both timings + both frequencies as recorded | reference | 0.45 | 0.53 | 0.026 | 38.0 / 37.2 / 34.1 S | 9 / 39 / 50 | 0.86 | 1.8 | 9.2 | 261 (provisional) |
| Both timings + both frequencies, Holland start-up offset (17 Hz floor) | +0.23 (+0.04 to +0.39) | 0.60 | 0.38 | 0.018 | 37.9 / 37.2 / 34.4 S | 7 / 34 / 47 | 0.90 | 1.9 | 9.2 | 6062 |
| Both timings + both frequencies, Holland start-up offset (zero floor) | +0.21 (+0.01 to +0.37) | 0.59 | 0.39 | 0.019 | 37.9 / 37.2 / 34.4 S | 7 / 35 / 47 | 0.90 | 1.9 | 9.2 | 6849 |
| Both timings + 00:19:29 frequency as recorded + offset on 00:19:37 only, 17 Hz floor (Ashton premise with Holland's acknowledge bounds) | -0.49 (-0.68 to -0.30) | 0.43 | 0.54 | 0.027 | 37.9 / 37.2 / 34.6 S | 8 / 38 / 48 | 0.86 | 1.6 | 9.2 | 1521 |
| Both timings + 00:19:29 frequency as recorded + offset on 00:19:37 only, zero floor (Ashton premise with Holland's acknowledge bounds) | -0.43 (-0.60 to -0.24) | 0.43 | 0.54 | 0.027 | 37.9 / 37.2 / 34.5 S | 9 / 38 / 49 | 0.86 | 1.7 | 9.2 | 1923 |

## Sensitivity: only the 00:19:29 timing value (Davey model + fuel)
| 00:19 treatment | ln Z vs first of same data group (90% seed interval) | No pilot | Piloted | Planned | Latitude 5/50/95 % | Arc distance 50/95/99 % (NM) | Within 25 NM | Impact after 00:19:29, 50 % (min) | Energy 50 % (GJ) | No-pilot effective paths |
|---|---|---|---|---|---|---|---|---|---|---|
| Sensitivity: 00:19:29 timing only | reference | 0.51 | 0.49 | 0.000 | 38.5 / 36.8 / 32.0 S | 13 / 71 / 101 | 0.71 | 16.6 | 1.2 | 509756 |
| Sensitivity: 00:19:29 timing + frequency (Ashton) | reference | 0.68 | 0.32 | 0.000 | 38.1 / 36.7 / 31.2 S | 12 / 48 / 69 | 0.84 | 15.8 | 1.1 | 19596 |
| Sensitivity: 00:19:29 timing + both frequencies as recorded | reference | 0.58 | 0.42 | 0.000 | 38.2 / 36.5 / 32.9 S | 9 / 36 / 52 | 0.89 | 1.8 | 9.2 | 322 (provisional) |
| Sensitivity: 00:19:29 timing + both frequencies, Holland offset | +0.36 (+0.23 to +0.50) | 0.74 | 0.26 | 0.000 | 38.1 / 36.5 / 32.9 S | 7 / 29 / 46 | 0.94 | 1.8 | 9.2 | 2735 |
| Sensitivity: 00:19:29 timing + offset on 00:19:37 only (17 Hz floor) | -0.41 (-0.57 to -0.27) | 0.60 | 0.40 | 0.000 | 38.1 / 36.5 / 32.2 S | 8 / 34 / 48 | 0.90 | 1.4 | 9.2 | 385 (provisional) |
| Sensitivity: 00:19:29 timing + offset on 00:19:37 only (zero floor) | -0.36 (-0.54 to -0.20) | 0.60 | 0.40 | 0.000 | 38.1 / 36.5 / 32.2 S | 8 / 34 / 48 | 0.90 | 1.5 | 9.2 | 528 |

## Variants (each one a re-weighting of the same paths)
| Route | Variant | 00:19 treatment | No pilot | Piloted | Planned | Latitude 50 % | Arc distance 95 % (NM) | Within 25 NM | Impact 50 % (min) | High-energy share |
|---|---|---|---|---|---|---|---|---|---|---|
| Davey model + fuel | headline | Both 00:19 timings (Davey) | 0.51 | 0.49 | 0.000 | 36.82 S | 69 | 0.73 | 17.2 | 0.27 |
| Davey model + fuel | headline | Both timings + both frequencies as recorded | 0.52 | 0.48 | 0.000 | 36.56 S | 38 | 0.88 | 1.7 | 0.78 |
| Davey model + fuel | headline | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.70 | 0.30 | 0.000 | 36.51 S | 31 | 0.93 | 1.8 | 0.86 |
| Davey model + fuel | cause prior 0.5 | Both 00:19 timings (Davey) | 0.52 | 0.48 | 0.000 | 36.82 S | 71 | 0.72 | 17.0 | 0.28 |
| Davey model + fuel | cause prior 0.5 | Both timings + both frequencies as recorded | 0.54 | 0.46 | 0.000 | 36.56 S | 37 | 0.88 | 1.7 | 0.78 |
| Davey model + fuel | cause prior 0.5 | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.70 | 0.30 | 0.000 | 36.51 S | 30 | 0.93 | 1.8 | 0.87 |
| Davey model + fuel | two-stage log-on delay | Both 00:19 timings (Davey) | 0.52 | 0.48 | 0.000 | 36.81 S | 68 | 0.73 | 17.1 | 0.27 |
| Davey model + fuel | two-stage log-on delay | Both timings + both frequencies as recorded | 0.49 | 0.51 | 0.000 | 36.51 S | 38 | 0.87 | 1.8 | 0.76 |
| Davey model + fuel | two-stage log-on delay | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.68 | 0.32 | 0.000 | 36.49 S | 31 | 0.92 | 1.9 | 0.86 |
| Davey model + fuel | include lost-control piloted paths | Both 00:19 timings (Davey) | 0.46 | 0.54 | 0.000 | 36.80 S | 68 | 0.71 | 16.4 | 0.27 |
| Davey model + fuel | include lost-control piloted paths | Both timings + both frequencies as recorded | 0.52 | 0.48 | 0.000 | 36.57 S | 38 | 0.87 | 1.7 | 0.78 |
| Davey model + fuel | include lost-control piloted paths | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.68 | 0.32 | 0.000 | 36.51 S | 31 | 0.93 | 1.8 | 0.84 |
| Davey model + fuel | 00:21:06 entertainment-system factor | Both 00:19 timings (Davey) | 0.52 | 0.48 | 0.000 | 36.80 S | 68 | 0.74 | 16.3 | 0.32 |
| Davey model + fuel | 00:21:06 entertainment-system factor | Both timings + both frequencies as recorded | 0.57 | 0.43 | 0.000 | 36.51 S | 33 | 0.92 | 1.4 | 0.85 |
| Davey model + fuel | 00:21:06 entertainment-system factor | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.71 | 0.29 | 0.000 | 36.49 S | 24 | 0.95 | 1.4 | 0.91 |
| Davey model + fuel | piloted push-over from cases | Both 00:19 timings (Davey) | 0.53 | 0.47 | 0.000 | 36.81 S | 70 | 0.73 | 17.5 | 0.26 |
| Davey model + fuel | piloted push-over from cases | Both timings + both frequencies as recorded | 0.49 | 0.51 | 0.000 | 36.60 S | 38 | 0.87 | 1.7 | 0.76 |
| Davey model + fuel | piloted push-over from cases | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.67 | 0.33 | 0.000 | 36.53 S | 32 | 0.92 | 1.8 | 0.85 |
| Davey model + fuel | onset delay log-uniform 10-300 s | Both 00:19 timings (Davey) | 0.52 | 0.48 | 0.000 | 36.83 S | 69 | 0.72 | 17.1 | 0.27 |
| Davey model + fuel | onset delay log-uniform 10-300 s | Both timings + both frequencies as recorded | 0.44 | 0.56 | 0.000 | 36.60 S | 39 | 0.85 | 1.8 | 0.74 |
| Davey model + fuel | onset delay log-uniform 10-300 s | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.63 | 0.37 | 0.000 | 36.53 S | 33 | 0.91 | 1.8 | 0.83 |
| Davey model + fuel | arrest probability 0.2 | Both 00:19 timings (Davey) | 0.55 | 0.45 | 0.000 | 36.81 S | 67 | 0.74 | 17.9 | 0.26 |
| Davey model + fuel | arrest probability 0.2 | Both timings + both frequencies as recorded | 0.47 | 0.53 | 0.000 | 36.67 S | 38 | 0.86 | 1.3 | 0.75 |
| Davey model + fuel | arrest probability 0.2 | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.67 | 0.33 | 0.000 | 36.58 S | 32 | 0.92 | 0.9 | 0.85 |
| Davey model + fuel | arrest probability 0.9 | Both 00:19 timings (Davey) | 0.50 | 0.50 | 0.000 | 36.82 S | 70 | 0.72 | 16.9 | 0.27 |
| Davey model + fuel | arrest probability 0.9 | Both timings + both frequencies as recorded | 0.54 | 0.46 | 0.000 | 36.53 S | 37 | 0.88 | 1.8 | 0.79 |
| Davey model + fuel | arrest probability 0.9 | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.70 | 0.30 | 0.000 | 36.49 S | 30 | 0.93 | 2.0 | 0.86 |
| Waypoints | headline | Both 00:19 timings (Davey) | 0.50 | 0.45 | 0.048 | 37.03 S | 69 | 0.73 | 18.0 | 0.24 |
| Waypoints | headline | Both timings + both frequencies as recorded | 0.45 | 0.53 | 0.026 | 37.22 S | 39 | 0.86 | 1.8 | 0.74 |
| Waypoints | headline | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.60 | 0.38 | 0.018 | 37.19 S | 34 | 0.90 | 1.9 | 0.82 |
| Waypoints | cause prior 0.5 | Both 00:19 timings (Davey) | 0.51 | 0.44 | 0.048 | 37.04 S | 70 | 0.73 | 17.8 | 0.25 |
| Waypoints | cause prior 0.5 | Both timings + both frequencies as recorded | 0.46 | 0.52 | 0.025 | 37.22 S | 39 | 0.86 | 1.8 | 0.75 |
| Waypoints | cause prior 0.5 | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.61 | 0.37 | 0.018 | 37.19 S | 34 | 0.91 | 1.9 | 0.82 |
| Waypoints | two-stage log-on delay | Both 00:19 timings (Davey) | 0.50 | 0.45 | 0.043 | 37.02 S | 69 | 0.74 | 18.1 | 0.24 |
| Waypoints | two-stage log-on delay | Both timings + both frequencies as recorded | 0.41 | 0.57 | 0.026 | 37.22 S | 41 | 0.84 | 1.8 | 0.73 |
| Waypoints | two-stage log-on delay | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.55 | 0.43 | 0.018 | 37.20 S | 35 | 0.89 | 1.9 | 0.80 |
| Waypoints | include lost-control piloted paths | Both 00:19 timings (Davey) | 0.46 | 0.48 | 0.054 | 37.04 S | 68 | 0.72 | 17.1 | 0.26 |
| Waypoints | include lost-control piloted paths | Both timings + both frequencies as recorded | 0.44 | 0.53 | 0.026 | 37.22 S | 40 | 0.85 | 1.8 | 0.74 |
| Waypoints | include lost-control piloted paths | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.59 | 0.39 | 0.020 | 37.19 S | 34 | 0.90 | 1.9 | 0.81 |
| Waypoints | 00:21:06 entertainment-system factor | Both 00:19 timings (Davey) | 0.51 | 0.45 | 0.047 | 37.05 S | 68 | 0.74 | 17.1 | 0.28 |
| Waypoints | 00:21:06 entertainment-system factor | Both timings + both frequencies as recorded | 0.50 | 0.47 | 0.023 | 37.19 S | 35 | 0.90 | 1.5 | 0.82 |
| Waypoints | 00:21:06 entertainment-system factor | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.61 | 0.37 | 0.017 | 37.19 S | 29 | 0.93 | 1.5 | 0.88 |
| Waypoints | piloted push-over from cases | Both 00:19 timings (Davey) | 0.52 | 0.43 | 0.049 | 37.02 S | 70 | 0.73 | 18.3 | 0.24 |
| Waypoints | piloted push-over from cases | Both timings + both frequencies as recorded | 0.41 | 0.56 | 0.024 | 37.23 S | 40 | 0.85 | 1.8 | 0.73 |
| Waypoints | piloted push-over from cases | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.57 | 0.41 | 0.017 | 37.20 S | 35 | 0.90 | 1.9 | 0.81 |
| Waypoints | onset delay log-uniform 10-300 s | Both 00:19 timings (Davey) | 0.51 | 0.45 | 0.048 | 37.04 S | 69 | 0.73 | 17.9 | 0.25 |
| Waypoints | onset delay log-uniform 10-300 s | Both timings + both frequencies as recorded | 0.37 | 0.60 | 0.029 | 37.24 S | 40 | 0.84 | 1.8 | 0.71 |
| Waypoints | onset delay log-uniform 10-300 s | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.52 | 0.46 | 0.022 | 37.21 S | 36 | 0.88 | 1.9 | 0.78 |
| Waypoints | arrest probability 0.2 | Both 00:19 timings (Davey) | 0.55 | 0.41 | 0.043 | 36.99 S | 67 | 0.75 | 18.8 | 0.24 |
| Waypoints | arrest probability 0.2 | Both timings + both frequencies as recorded | 0.38 | 0.59 | 0.029 | 37.26 S | 40 | 0.84 | 1.6 | 0.71 |
| Waypoints | arrest probability 0.2 | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.58 | 0.40 | 0.019 | 37.24 S | 35 | 0.90 | 1.1 | 0.81 |
| Waypoints | arrest probability 0.9 | Both 00:19 timings (Davey) | 0.48 | 0.47 | 0.050 | 37.05 S | 70 | 0.72 | 17.6 | 0.24 |
| Waypoints | arrest probability 0.9 | Both timings + both frequencies as recorded | 0.47 | 0.51 | 0.025 | 37.20 S | 39 | 0.86 | 1.9 | 0.75 |
| Waypoints | arrest probability 0.9 | Both timings + both frequencies, Holland start-up offset (17 Hz floor) | 0.61 | 0.37 | 0.018 | 37.18 S | 34 | 0.91 | 2.1 | 0.82 |

## Figures
- [eof-final-impact-maps-working.png]({{artifact:98ce3c6d-053b-419d-bb53-0eb197884c4f}})
- [eof-final-arc-distance-working.png]({{artifact:950ba7f2-efec-4c6f-a3e9-795f4dff4740}})
- [eof-final-latitude-and-time-working.png]({{artifact:72ebf880-3ea1-439e-913c-7c8edcb37078}})
- [eof-final-family-split-working.png]({{artifact:b83fc334-06a8-4af3-ba4a-bd2ac86d8b98}})
- [eof-final-energy-working.png]({{artifact:ae69c077-dfb7-4331-9897-d14c0afa9964}})

## Key assumptions and modelling choices
| Item | Value | Status |
|---|---|---|
| Main configuration | Davey model + fuel; planned descent on waypoints only | Pete's ruling (31 Oct, 3 Nov) |
| Engine power at 00:11 | At least one engine running at 00:10:59 | Project convention |
| 00:19 timing values | Both BTOs in every headline treatment (R1200 corrected to 18,380 us, sd 43 us) | Agreed table (1 Nov) |
| BFO noise | 4.32 Hz, as in the core | Pete's ruling (6 Nov) |
| Holland offset | 17 Hz floor and zero floor, both shown | Own choice (zero floor added) |
| Log-on cause prior | 0.75 fuel exhaustion (q = 1/3); 0.5 as a variant | Agreed 3.2 wording (1 Nov); not otherwise ruled |
| Log-on lag | Gamma(8, 14.875 s), mean 119 s; two-stage N(60,15) + N(60,10) s as a variant | Project convention; sd 42 s unsourced |
| Break-up | Not applied to any weight | Pete's ruling (to settling) |
| Withdrawn uncontrolled law | Piloted paths that lost control and descents begun before exhaustion with no intervention are excluded in the headline; included in a variant | Own choice |
| Piloted push-over | Engine prior (rate U[6,500, 40,000] ft/min, floor U[-1, 0.8] g, hold U[0, 300] s); case-informed floor as a variant | Pete's ruling (11 Oct) |
| No-pilot dive kernel | Case-informed 3-DOF point mass; build-up from the hierarchical case prior; Boeing-based arrest | Own design from Pete's request (7 Nov); tests passed |
| Case classes | No effective crew input vs active crew input during the build-up | Draft labels; not yet reviewed by Pete |
| Onset delay (no pilot) | Case predictive (median 35 s); log-uniform 10-300 s as a variant | Own choice from the case data |
| Arrest probability | Beta(5, 2) from Boeing 4/4 and Adam Air 0/1; 0.2 and 0.9 as variants | Own choice |
| Outcome labels | High-energy impact >= 4 GJ; fast descent at 00:19:37 >= 10,000 ft/min | Own choice; Pete's family table not yet ruled |
| Thinning | Unbiased Russian roulette to about 300,000 rows per seed | Own choice |

## What this run does not settle
- The family split (no pilot or piloted) is conditional on the behaviour priors.
- The energy of the no-pilot dives is at the top of the Boeing range (median about 9 GJ against Boeing 6.4-9.0 GJ). The pre-onset peak descent in Test B is biased high.
- Cells marked provisional have fewer than 500 effective no-pilot paths after pooling.
- The case classes and Pete's dive/non-dive family table are not yet ruled.

## Hand-off files
- [eof-final-handoff-df.npz]({{artifact:4d45eed1-578b-46d8-90d9-0d5d87fbbd04}}) and [eof-final-handoff-wp.npz]({{artifact:b919b696-b0da-4041-9364-accf33a71f6f}}), with their json descriptions. Columns: position, signed arc distance, impact time, kinetic and vertical kinetic energy, mass, flight-path angle (positive in descent), bank, ground track, ground speed, peak Mach, peak EAS, load factors, vertical speeds at 00:19:29 and 00:19:37, family, electrical configuration, flame-out times, seed and one log weight per headline treatment.
