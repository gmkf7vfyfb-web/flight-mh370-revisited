# End of flight: the dive class, PROVISIONAL-OVERNIGHT, first smoke

9 October 2026, 05:39 UTC. **SMOKE SCALE, not evidence.** 00:11 hand-off, seed 1, N = 4, 295.66° prior
(superseded by `reference-289`). Code `cb4f56d`.

**PROVISIONAL-OVERNIGHT** (overnight rule, `architecture.md` ~06:00 UTC; Pete reviews in the morning).

## The choice taken

- **The question** (`architecture.md`, my entry stamped 05:39 UTC and the one before it) is how the
  Boeing uncontrolled-dive class enters the module, whose fixed-C_L point mass cannot reproduce it
  consistently (`results/eof-boeing-calibration-oct09`, addendum 2).
- **Recommended option (b), taken:** a declared empirical dive class tied only to published values.
  - Free dynamics diverge with Pete's 0.5 prior weight.
  - Bank doubles every U[60, 120] s, up to a 90° cap.
  - The 90° cap is where this model meets the published high-rate thresholds (above 15,000 ft/min and
    0.67 g, Iannello 2018).
- **Declared misfit:**
  - these dives end 1.0–2.7 NM after first passing 15,000 ft/min, against the published 4.7–7.9 NM;
  - they read 78–80° of bank on the track, against 53–60° for Boeing's validation-only files.
- **Reversible:** `smoke/spiral-off.toml` restores the pre-calibration model, bit-identically.
  Sensitivities are `smoke/spiral-weight-0.25.toml` and `-0.75.toml`.

## First smoke: the same seed and hand-off, dive class off (`runs/eof-s6-n4-s1`) and on (`runs/eof-dive-n4-s1`)

- **Overall:** P(peak descent ≥ 15,000 ft/min) rises from 0.071 to 0.326. The divergent share of the
  prior weight is 0.499.

| option | log-on | effective parents, off → on | impact latitude 5/50/95%, off | on | divergent share of the posterior |
|---|---|---|---|---|---|
| r600/inflated | other | 13,395 → 13,398 | −39.46 / −38.04 / −35.10 | −39.46 / −38.03 / −35.24 | 0.49 |
| r600/inflated | fuel exhaustion | 3,094 → 3,153 | −39.33 / −37.81 / −35.03 | −39.33 / −37.81 / −35.14 | 0.49 |
| r1200/inflated | other | **487 → 1,744** | −39.24 / −37.36 / −30.09 | −38.59 / −37.06 / −33.14 | **0.84** |
| r1200/inflated | fuel exhaustion | 146 → 527 | −39.33 / −37.68 / −32.64 | −38.81 / −37.15 / −32.64 | 0.86 |
| r1200/no-offset | other | 111 → 413 | −39.23 / −37.36 / −29.75 | −38.59 / −37.11 / −33.26 | 0.85 |
| r1200/no-offset | fuel exhaustion | 38 → 122 | −39.33 / −37.44 / −32.64 | −38.76 / −37.23 / −33.26 | 0.87 |
| r1200/startup-offset | other | 149 → 1,032 | −38.53 / −37.04 / −29.57 | −37.96 / −36.95 / −33.29 | 0.91 |
| r1200/startup-offset | fuel exhaustion | 37 → 293 | −38.70 / −37.34 / −27.15 | −37.96 / −37.03 / −33.46 | 0.94 |
| both/inflated | other | 87 → 121 | −39.43 / −37.74 / −35.12 | −39.30 / −37.38 / −35.14 | 0.51 |
| both/inflated | fuel exhaustion | 34 → 56 | −39.39 / −37.91 / −36.09 | −39.32 / −37.76 / −35.47 | 0.55 |
| both/no-offset | other | 3 → 4 | (not resolved) | (not resolved) | – |

## Reading (one seed, N = 4, so indicative only)

1. **R600 is unaffected,** as expected: its BFO does not discriminate the late descent.
2. **The R1200 BFO (−2 Hz at 00:19:37) selects the dive class.** 84–94% of the R1200 posterior is
   divergent against a 0.5 prior, a Bayes factor of roughly 5–15 in its favour.
   - Effective parents rise 3.2–7×. Part of the R1200 concentration measured in
     `results/eof-ess-limit-oct09` came from the model's **missing dive class**, not only from the data.
   - The N = 16 limits there were measured with the dive class off.
3. **Impact latitude moves modestly** under R1200. The median moves about 0.3° north, and the northern
   95% tail tightens from about −30° to −33°.
4. **`both` stays essentially unresolved,** under either log-on cause.
5. **The chord misfit matters for location at the few-NM level.** The dives end 2–7 NM short of
   Boeing's published distances, which is small against the impact PDF's 50–100 NM extent.


## Addendum (05:48 UTC): effective parents with the dive class on, N = 8, seed 1

Run `runs/eof-dive-n8-s1`, about 8.5 min at 2 threads outside the lock. N = 8 instead of 16 keeps it under
the 10-minute threshold while core holds the lock.

| log-on | option | dive off, N = 16: observed (limit) | dive on, N = 8: observed (limit) |
|---|---|---|---|
| other | r600/inflated | 14,772 (15,302) | 14,340 (15,404) |
| other | r600/startup-offset | 3,751 (4,600) | 3,331 (4,629) |
| other | r1200/inflated | 989 (1,496) | 2,863 (8,131) |
| other | r1200/no-offset | 283 (645) | 776 (6,411) |
| other | r1200/startup-offset | 391 (783) | 1,830 (10,049) |
| other | both/inflated | 198 (329) | 181 (523) |
| other | both/no-offset | 12 (26) | 7 (unresolved) |
| other | both/startup-offset | 9 (11) | 21 (7,557) |
| fuel-exhaustion | r600/inflated | 3,797 (4,120) | 3,587 (4,196) |
| fuel-exhaustion | r600/startup-offset | 1,396 (1,693) | 1,375 (1,926) |
| fuel-exhaustion | r1200/inflated | 224 (301) | 821 (2,506) |
| fuel-exhaustion | r1200/no-offset | 66 (107) | 220 (2,727) |
| fuel-exhaustion | r1200/startup-offset | 80 (131) | 555 (2,914) |
| fuel-exhaustion | both/inflated | 100 (206) | 88 (351) |
| fuel-exhaustion | both/no-offset | 4 (68) | 2 (unresolved) |
| fuel-exhaustion | both/startup-offset | 7 (36) | 7 (61,206) |

**Reading:**
1. **R1200 is no longer concentration-limited once the dive class is in the model.**
   - With log-on = other: 2,863 effective parents for r1200/inflated and 1,830 for Holland, per seed, at
     N = 8. Raw is at 776.
   - Under fuel exhaustion: 821, 555 and 220.
   - Pooled over 8 seeds (ruling E2), every R1200 case clears 1,000.
   - **The concentration measured in `results/eof-ess-limit-oct09` was largely an artefact of the
     missing dive class.**
2. **`both` does not improve:** 2–181 effective parents. It stays concentration-limited, and both/no-offset
   and both/startup-offset are unresolved.
3. **The limits here are not trustworthy yet.** At N = 8 the split is 4 against 4, which proved biased
   upward for concentrated cases (`results/eof-ess-limit-oct09`, addendum 2). Treat the observed column
   as the result.
4. **Everything above is conditional on the PROVISIONAL-OVERNIGHT dive class.**
