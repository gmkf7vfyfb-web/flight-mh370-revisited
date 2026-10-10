# End of flight: the V2 descent envelope at 22:41, broadened, and a uniform-onset arm V2u (10 Oct 2026)

**SMOKE, PROVISIONAL-OVERNIGHT.** The run conditions:
- core hand-off `reference-289`, m2241, prior track 289.7 deg;
- seeds 1 and 2, 100,000 parents x 2 children x 4 descents per arm, 2 threads;
- UNCORRECTED FUEL (the 22:41 fuel state; audit F1-F4);
- PROVISIONAL SAMPLER (the 22:41 population, before core request 17);
- the ICAO EEDB idle floor in the descent burn;
- the binary built from the module tree at `1a5f1689` plus the two hooks below (dirty build).

Answers Pete ~03:50 UTC: the V2 profiles "do not look ... randomly initiated post 22:41", and the 10,000 ft, 4,000 ft and typical level-offs are
undersampled.

## What changed (inside the module, reversible)

- **Two new hooks**, both byte-identical at their defaults (checked at full size, 800,000 x 117, against the previous binary):
  - `envelope.powered_shape_weights` (default [0.4, 0.3, 0.3]);
  - `deliberate_control_weights` (default off). It sets the control mix for anticipatory and fuel-cue onsets that still have thrust.
- **Overlay `smoke/v2-broad.toml`**, applied to both arms so that the comparison stays like for like:
  - deliberate onsets start in control: ditching 0.6, maintained-then-lost 0.4, never free trim;
  - anticipatory lead [0, 9,000] s, truncated exactly at 22:41, so the onset is uniform on [22:41, predicted exhaustion];
  - control loss after U[30, 5,400] s;
  - powered shapes continuous / emergency / stepped 0.25 / 0.5 / 0.25;
  - second level-off p = 0.6;
  - level-off candidates 10,000 ft, 4,000 ft and U[11,000, 30,000] ft.
- **New arm `smoke/arm-v2u.toml`** (with v2-broad): anticipatory onset only, so a deliberate descent at a uniformly random time after 22:41.
- **New script `smoke/prior_diagnostics.py`.** It measures the prior (seed 1): onsets, shapes, and level-offs from `traces-dense.csv`.

## Prior: what the arms propose (seed 1, before any data after 22:41)

| measure | V2 old envelope | V2-broad | V2u |
|---|---|---|---|
| onset in 22:41-22:56 | 4.3% | 6.3% | 18.0% |
| onset in 22:41-23:11 | 12.4% | 14.7% | 36.0% |
| anticipatory onset, median min after 22:41 | 47.5 | 42.0 | 41.8 |
| free trim among powered onsets | 50% | 0% | 0% |
| descents with a level segment (≥2 min) | 16.4% | 39.6% | 46.7% |
| level-off within ±500 ft of 10,000 ft | 2.8% | 9.6% | 11.8% |
| level-off within ±500 ft of 4,000 ft | 1.7% | 8.1% | 10.1% |
| median level duration | 7.0 min | 10.0 min | 10.0 min |

**Why V2's onsets stay late even when broadened.**
- This is structural. Two of V2's three mechanisms, fuel cue and flame-out-associated, are tied to the predicted exhaustion by definition:
  - the predicted exhaustion is 99.5 min after 22:41 (73.6-126.8);
  - fuel-cue onsets have a median of 56.8 min.
- Only the anticipatory third can be early, and with the broad lead it is already uniform over the available window.
- "Randomly initiated after 22:41" is therefore a different hypothesis, so it is run as its own arm, V2u, rather than as a re-tuning of V2.

## Evidence against V1b (ln BF, seeds 1 / 2; old column from `runs/eof-2241-tr-{v1,v2}-s{1,2}`; ≥30 effective parents per seed and seed agreement required)

| data (cause `other`) | V2 old | V2-broad | V2u | eff. parents V1b / V2-broad / V2u |
|---|---|---|---|---|
| 23:15 BFO + 00:11 BTO/BFO | -0.34 / -0.38 | **-0.19 / -0.22** | **-0.70 / -0.70** | 776-826 / 1,115-1,164 / 881-909 |
| 23:15 BFO alone | -0.10 / -0.11 | -0.11 / -0.12 | -0.31 / -0.32 | 84k / 81k / 76k |
| 00:11 BTO alone | -0.13 / -0.19 | -0.06 / -0.11 | -0.50 / -0.52 | 1.2k / 2.0k / 1.7k |
| 00:11 BFO alone | -0.69 / -0.71 | -0.67 / -0.68 | -1.57 / -1.58 | 50-55k / 35-39k / 18-19k |
| R600 as observed | -0.75 / -0.70 | -0.82 / -0.80 | -1.72 / -1.61 | 223-249 / 120-124 / 50-53 |

**Not estimable from 22:41:**
- R600 + `fuel-exhaustion` (V2-broad 23-25 parents, V2u 5-9);
- 00:11 + R600 (13-17 and 7-15).

V1b's lnZ is unchanged by the overlay to two decimals, since V1b is unpowered at onset.

**Reading.**
- Broadening the envelope recovers about 0.15 of V2's deficit (-0.36 to -0.21), mostly at the 00:11 BTO; the 00:11 BFO term is unchanged (-0.70 to -0.68), and R600 as observed moves slightly against V2 (-0.73 to -0.81).
- A deliberate descent at a uniformly random time is disfavoured against V1b by a factor of about 2 (e^0.70). The 00:11 BFO does most of this,
  because it penalises being well into a descent at 00:11.
- These are prior-dependent ratios at smoke scale; earlier prior-sensitivity bounds for V2 were -0.6 to 0.

## Impact latitude, posterior under 23:15 + 00:11 (`other`), weighted median (q05-q95), seeds 1 / 2

| arm | seed 1 | seed 2 | eff. impacts |
|---|---|---|---|
| V1b | 37.43°S (40.62-28.88) | 37.68°S (40.53-28.69) | 3,960 / 4,228 |
| V2 old | 35.50°S (39.83-30.08) | 35.77°S (39.87-30.32) | 2,715 / 2,773 |
| V2-broad | 36.16°S (39.89-30.61) | 36.31°S (39.94-31.34) | 3,123 / 3,200 |
| V2u | 35.75°S (38.92-31.56) | 35.84°S (39.24-33.29) | 1,693 / 1,755 |

The posteriors are parent-limited, with the effective parents in the evidence table. The downstream reference stays the 00:11 hand-off (V1a);
nothing here replaces a delivered product.

## Figures
- `vertical-profiles-2241-broad.png/.pdf`: V2-broad and V2u.
- `vertical-profiles-2241-broad-v1b.png/.pdf`: V1b and V2-broad.

## Question for Pete (PROVISIONAL-OVERNIGHT: the recommended option is taken)

Which envelope defines V2 from 22:41?
- (A) the old envelope;
- (B) the `v2-broad` overlay, with V2u reported beside it as the "random-time deliberate descent" sub-hypothesis. **Recommended**;
- (C) an explicit preferred-level mixture (ATC-style levels with dwell times), not yet built.

B is in force for any further 22:41 runs. Drop the overlay to revert.

Runs: `runs/eof-2241-broad-{v1,v2,v2u}-s{1,2}`.
