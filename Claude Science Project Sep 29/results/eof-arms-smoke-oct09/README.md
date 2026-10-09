# End of flight: the three arms at smoke scale, dive class on (PROVISIONAL-OVERNIGHT)

9 October 2026, 06:03 UTC. **SMOKE SCALE, not evidence.** Seed 1, N = 4, 295.66° prior (superseded by
`reference-289`), dive class PROVISIONAL-OVERNIGHT (`results/eof-dive-provisional-oct09`).

**Runs:**
- **V1a:** `runs/eof-v1a-dive-n4-s1`, the 00:11 hand-off with `arm-v1` (flame-out-associated onset only;
  00:11 scored inside the filter).
- **"V2 at 00:11":** `runs/eof-dive-n4-s1`. This is none of the brief's three arms; it is shown for
  reference.
- **V1b and V2:** `runs/eof-2241-bto-dive-v{1,2}-s1`, from 22:41. Only the BTOs after 22:41 are scored
  inside this stage: **NOT THE ARM**, because the 00:11 and 23:15 BFOs wait on core request 14.

A negative onset value means onset after 00:19:37: a descent that never flew through the last
transmission, unscored under `none`.

| arm (hand-off; onset model) | option | effective parents | impact latitude 5/50/95% | onset, min before 00:19:37, 5/50/95% |
|---|---|---|---|---|
| V1a 00:11 dive (arm-v1) | none | 20,000 | -39.74 / -37.59 / -33.36 | -18.0 / 1.9 / 8.0 |
| V1a 00:11 dive (arm-v1) | r600/inflated | 11,053 | -39.59 / -38.12 / -35.60 | -10.1 / 3.3 / 7.8 |
| V1a 00:11 dive (arm-v1) | r1200/inflated | 1,452 | -38.83 / -37.20 / -33.26 | 0.7 / 2.6 / 7.5 |
| V1a 00:11 dive (arm-v1) | both/inflated | 99 | -39.53 / -37.72 / -35.29 | 0.7 / 0.9 / 7.0 |
| V2-at-00:11 dive (default) | none | 20,000 | -39.48 / -37.28 / -33.19 | -10.7 / 5.1 / 8.6 |
| V2-at-00:11 dive (default) | r600/inflated | 13,398 | -39.46 / -38.03 / -35.24 | -4.0 / 4.5 / 8.6 |
| V2-at-00:11 dive (default) | r1200/inflated | 1,744 | -38.59 / -37.06 / -33.14 | 0.7 / 3.7 / 8.6 |
| V2-at-00:11 dive (default) | both/inflated | 121 | -39.30 / -37.38 / -35.14 | 0.7 / 2.1 / 8.6 |
| 22:41 v1 dive | none | 19,999 | -39.79 / -36.03 / -21.16 | -25.1 / 1.8 / 25.5 |
| 22:41 v1 dive | m0011.bto | 504 | -39.68 / -37.35 / -27.60 | -22.1 / 1.2 / 8.0 |
| 22:41 v1 dive | m0011+r600.bto | 301 | -39.86 / -38.15 / -27.74 | -22.1 / 0.1 / 7.2 |
| 22:41 v2 dive | none | 19,999 | -38.74 / -32.47 / -23.03 | -15.0 / 29.7 / 82.2 |
| 22:41 v2 dive | m0011.bto | 650 | -39.33 / -36.06 / -27.80 | -12.7 / 6.5 / 38.8 |
| 22:41 v2 dive | m0011+r600.bto | 225 | -39.74 / -37.88 / -26.69 | -13.2 / 1.2 / 29.9 |

## Onset-mass boundary diagnostic (brief section 1), V2 from 22:41

Share of posterior onset within 5, 10 and 20 min after the 22:41 checkpoint:

```
none onset within 5/10/20 min of the 22:41 boundary: [0.0121, 0.0271, 0.0695] prior share <5 min 0.0121
m0011.bto onset within 5/10/20 min of the 22:41 boundary: [0.0, 0.0, 0.0] prior share <5 min 0.0121
m0011+r600.bto onset within 5/10/20 min of the 22:41 boundary: [0.0, 0.0, 0.0] prior share <5 min 0.0121
```

**No mass accumulates against the boundary.** Under `none` the share equals the prior's. With the 00:11
BTO scored it is zero within 20 min, because early onsets cannot reach the 00:11 arc. So the 22:41
checkpoint is not shaping the answer at this scale; repeat this check on the arm proper.

## What each comparison does and does not establish (brief section 1)

1. **V1b against V2** (same 22:41 hand-off, same scoring): with nothing scored, V2's median impact lies
   **3.6° north of V1b's** (−32.47 against −36.03). With the m0011 and m0019a BTOs scored, the gap is
   **0.3°** (−37.88 against −38.15).
   - This difference **is** attributable to the descent hypothesis.
   - It is **not yet the arm's result**: the 00:11 BFO, which sets the autopilot-mode mixture, is not
     scored.
2. **V1a against V1b is not computed here.** V1a has the 00:11 BFO scored in the filter, and V1b cannot
   score it yet. A comparison now would mix where 00:11 is scored with **whether** it is scored. It
   waits for request 14.
3. **V1a against "V2 at 00:11"** is not one of the brief's comparisons. It is reported only to show that
   flame-out-only onset moves the 00:11-hand-off result by 0.1–0.3° in median latitude.
