# Run J proposal (core) — DRAFT, 15 October 2026

Status: **draft for Pete's GO. Nothing is submitted. Run J needs Pete's own explicit GO; no delegated GO
applies.** The change list is `results/run-j-change-list.md`. This draft adds items 6–8 (core order
2026-10-15b step 5). Size, ETA, disk and the final predictions will be re-posted at submission. They depend
on the item 5 smoke (core request 20) and on the gate references of 15 Oct.

## Items and where each acts

| # | Item | Acts in | Core change | State |
|---|---|---|---|---|
| 1 | Waypoint and free-flight convergence (split-half 0.916 / 0.830 against floor 0.924) | core | more particles, 2.2–5× (the only tested remedy) | size to be set with item 5 |
| 2 | Aimed proposal for the northern arc, about 34–25 S | core | not designed | not in run J unless designed |
| 3 | 18:25:27 R600 epoch (BFO 142 Hz sd 7; BTO 12,520 µs sd 62, flagged) | core | `obs-r600-1825.toml` (4297f3bc) | ready |
| 3a | BER and C/N0 of the 18:25:27 burst | record | — | open |
| 4 | Wording rules | reports | — | applies |
| 5 | 00:19 two-burst hand-off proposal (item 10) | core + EoF | **core request 20** (`results/item10-phase1/design-core-request-20.md`) | design posted; Phase 1 smoke needs Pete's GO |
| **6** | **BFO sd 4.32 Hz in production; 7 Hz as a declared sensitivity; plus a check of why our 4 Hz shoulder (0.2931) is close to Davey's 7 Hz shoulder (0.2406)** | core | new observations variant with BFO sd 4.32 Hz (Davey Table 5.1, 4.3177 Hz) on every cruise BFO; the 7 Hz sensitivity is the current file | **see the correction below** |
| **7** | **Uniform-onset prior for planned descent (B), as a sensitivity** | EoF (order b, item 4) | none. The hand-off is unchanged; EoF reweights or redraws the onset | EoF |
| **8** | **D0 = 00:19 values held out, transmission imposed (airborne at 00:19:37)** | EoF (order b, item 2) | none in the filter. If request 20 is used, D0's g includes the airborne-at-00:19:37 indicator so that the proposal is aimed at the right set | EoF |

## Item 6: correction to the stated cause, and the check core proposes instead

The answers note (§1) lists "our bias-drift term adds 5.4 Hz²" as a candidate cause, and proposes a 7 Hz run
with the bias-drift term off. **No bias-drift term is active in the production stack.** `[bfo_bias]
drift_hz2_per_s` is not set in `davey2016.toml`, `davey2016-inmarsat.toml`, `no-exhaustion-prior.toml`, the
fuel fixes, `reference-snapshots`, `radar-full` or `next-run/`, so the F4 drift is off in run I (handover §7).

The 5.4 Hz² is the **posterior variance of the marginalised constant bias**. The filter's BFO residual sd is
√(bias variance + BFO sd²) (filter.rs, about line 974): 7.3755² − 7² = 5.40 and 4.63² − 4² = 5.44, the same
bias variance in both. Davey et al. marginalise a constant bias per particle in the same way (sec. 5.3 and 8.1),
so this term is common to both methods and cannot explain the shoulder.

**Proposed check instead (1 seed × 7M each, about 12 min each on deskstar):** `davey2016-inmarsat.toml` alone
(the pure reproduction, with no fuel, speed envelope, radar or families) at 7 Hz, 4.32 Hz and 4 Hz.
- If the reproduction at 7 Hz gives Davey's shoulder (about 0.24) and 4 Hz gives about 0.29, the closeness is
  a coincidence of the stack.
- If the reproduction at 7 Hz already gives about 0.17, the deficit lies in the reproduction itself, and
  the shoulder deficit "already present in the BTO-only case" (bfo-4hz.toml) points to the BTO side.

## Size, ETA, disk (provisional; re-measured at submission)

- **Strata as run I** (free, waypoints, descent-climb, repro-radar), 8 seeds. Item 1 asks 2.2–5× the particles
  for free and waypoints.
- **Run I measured times at 88 threads:** repro-radar 48 min (8 × 3.5M). The other strata are estimated in
  the run I proposal at about 2.0 h (free), 2.2 h (waypoints) and 0.6 h (descent-climb).
  - At 2.2× for free and waypoints: about 10–11 h of filter time.
  - At 5×: about 20 h, which needs more than one night and a split across days.
- **Core request 20 pilots** (if adopted): about 5 min per seed per stratum at L = 32, so about 3 h for
  32 seed-strata.
- **Memory.** Seeds run in sequence inside one process, so peak memory scales with particles PER SEED. The run I
  proposal puts 7M per seed at about 26 GB, so 2.2× per seed (about 57 GB) would exceed the 36 GiB cap.
  - Item 1's extra particles must therefore come as **more seeds at 7M** (for example 16–24 seeds), not as
    more particles per seed.
  - More seeds also change the split-half floor (8 replicates: 0.924). This is a design choice for Pete.
  - One stratum at a time; peak memory to be measured on a smoke first.
- **Disk.** 17 GB free on deskstar today, and run I was about 34 GB in total. Stage each stratum to
  `~/Downloads/mh370-exchange/core/run-j/` and delete it on deskstar before the next stratum writes.
- **Not byte-comparable with run I** (item 3 adds an epoch). Compare statistically.

## Predictions (provisional)

1. Item 6 at 4.32 Hz moves weight into the magnetic-heading and magnetic-track modes. The 7th-arc shoulder
   rises toward about 0.29 (the 4 Hz sweep moved it 0.1739 → 0.2931). ln Z changes by about 1.5 nat
   (the 4 Hz sweep records "+1.52 nat").
2. Item 3 moves the early-turn timing only, and the 00:19 median moves by < 0.3°.
3. Items 7 and 8 change no core output.
