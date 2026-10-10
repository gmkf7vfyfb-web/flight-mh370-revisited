# End of flight: impact times against the 00:19:37 burst and the unanswered 01:15:56 handshake (10 Oct 2026)

Answers architecture's ~03:20 UTC question for hydroacoustics. The data are reference-289, `runs/eof-289-full-s1..s4`: core `reference-289`, prior track 289.7 deg,
00:11 hand-off, 4 seeds x 100,000 parents x 8 children x 4 descents. Mac, built 9 Oct (`55c4536-dirty`), single fuel pool, uncorrected fuel. Shares are
seed means of option-posterior weight. The constraints are **PROVISIONAL-OVERNIGHT**: declared, default-off variants (`+alive`, `+silent`). Every plain
option x cause arm, and every number published from one, is unchanged.

## How each case is treated today

1. **Impacts before 00:19:37.443.**
   - Every option that scores a 00:19 BTO or BFO needs the aircraft's state at that burst. A descent already down has none, which scores minus infinity. So
     those options enforce existence for the bursts they use (shares below <= 0.0007).
   - **Held out (`none`) uses no 00:19 burst and so does NOT enforce existence.** Under `other`, 10.2% of its weight lands before 00:19:37.
   - **Defect, mine:** the fuel-exhaustion log-on term (module `impact_log_likelihood`, and the same term in `smoke/*.py`) scores only flame-out before
     00:19:29.416. It does not require the aircraft to be airborne then, so `none__fuel-exhaustion` puts 3.0% of its weight before 00:19:37.
     `r600-bto__fuel-exhaustion` (BTO at 00:19:29 only) puts 0.24% between 00:19:29 and 00:19:37.
2. **Paths flying after 01:15:56** have no constraint today.
   - Held out (`other`): 1.9% impacts after 01:15:56, of which 0.31% are still powered then (engines running, so the SDU would have answered).
   - The paths that are airborne but unpowered at 01:15:56 are glides after a late flame-out.

## The two constraint layers (declared; `smoke/displacement_hist.py: constraint_log_factor`)

- **`+alive`**: airborne at 00:19:37.443. That the 00:19:29/00:19:37 sequence was transmitted is a datum, separate from its BTO/BFO values.
- **`+silent`**: `+alive`, plus two further conditions.
  - **Not powered at 01:15:56** (the handshake went unanswered; Davey et al. 2015 draft, p. 6).
  - **Under `other` only: no APU log-on after a later flame-out.** A flame-out after the observed log-on would start the APU and log the SDU on again,
    and the ground station logged none. The factor is the probability that the aircraft hit the water before that log-on: the Erlang(8, 14.875 s)
    survival of (impact - flame-out). Under fuel-exhaustion the single flame-out IS the 00:19:29 log-on's, so no further log-on is predicted.
  - Single fuel pool. With two tanks the APU log-on belongs to the second flame-out.

## Shares and effects (reference-289, 4 seeds)

| option x cause | impact < 00:19:37 | impact > 01:15:56 | powered at 01:15:56 | impact 5% / 50% / 95% (UTC) | kept by +alive | kept by +silent | median lat plain / +alive / +silent | ESS plain / +alive / +silent |
|---|---|---|---|---|---|---|---|---|
| `none__other` | 0.1016 | 0.0187 | 0.0031 | 00:16:06 / 00:38:34 / 01:05:34 | 0.898 | 0.140 | -36.78 / -36.95 / -35.77 | 12,358,800 / 11,042,105 / 1,872,897 |
| `none__fuel-exhaustion` | 0.0299 | 0.0000 | 0.0000 | 00:20:09 / 00:35:06 / 00:48:40 | 0.970 | 0.970 | -36.94 / -36.96 / -36.96 | 1,069,176 / 1,030,551 / 1,030,551 |
| `r600_no-offset__other` | 0.0001 | 0.0003 | 0.0002 | 00:21:32 / 00:35:13 / 00:48:31 | 1.000 | 0.098 | -37.25 / -37.25 / -36.02 | 197,569 / 197,539 / 24,516 |
| `r600_no-offset__fuel-exhaustion` | 0.0000 | 0.0000 | 0.0000 | 00:21:13 / 00:34:17 / 00:49:05 | 1.000 | 1.000 | -37.28 / -37.28 / -37.28 | 59,512 / 59,511 / 59,511 |
| `both_startup-offset__fuel-exhaustion` | 0.0000 | 0.0000 | 0.0000 | 00:20:07 / 00:27:38 / 00:39:16 | 1.000 | 1.000 | -36.76 / -36.76 / -36.76 | 36 / 36 / 36 |
| `both_no-offset__other` | 0.0000 | 0.0000 | 0.0000 | 00:20:41 / 00:30:23 / 01:00:22 | 1.000 | 0.426 | -36.32 / -36.32 / -35.79 | 82 / 82 / 46 |
| `r600_inflated__other` | 0.0002 | 0.0092 | 0.0017 | 00:22:36 / 00:37:51 / 00:57:29 | 1.000 | 0.131 | -37.58 / -37.58 / -36.66 | 3,055,333 / 3,054,965 / 445,869 |
| `r600_inflated__fuel-exhaustion` | 0.0000 | 0.0000 | 0.0000 | 00:21:39 / 00:35:24 / 00:49:00 | 1.000 | 1.000 | -37.48 / -37.48 / -37.48 | 402,652 / 402,636 / 402,636 |
| `r1200_inflated__other` | 0.0000 | 0.0004 | 0.0002 | 00:20:04 / 00:20:29 / 00:44:18 | 1.000 | 0.355 | -36.15 / -36.15 / -35.69 | 69,079 / 69,079 / 26,300 |
| `both_inflated__other` | 0.0000 | 0.0013 | 0.0007 | 00:20:18 / 00:31:13 / 00:48:13 | 1.000 | 0.279 | -36.65 / -36.65 / -35.84 | 4,784 / 4,784 / 1,186 |
| `r600-bto__other` | 0.0007 | 0.0247 | 0.0040 | 00:23:52 / 00:41:51 / 01:08:13 | 0.999 | 0.115 | -37.71 / -37.71 / -36.72 | 6,471,040 / 6,465,333 / 828,126 |

All option x cause rows: `impact-time-shares-reference-289.json` and `constraints-reference-289.json`.

## Reading, and the PROVISIONAL-OVERNIGHT choice

- **`+alive` is nearly free** for every option that scores a 00:19 burst. It changes only held out and the BTO-only log-on rows: held-out `other`
  36.78 -> 36.95 S, with 10.2% of its weight removed.
- **`+silent` is decisive under `other`**: 10-56% of the weight survives, and the medians move 0.4-1.2 deg **north** (held out 35.77 S, R600 as observed
  36.02 S). Under fuel-exhaustion it changes nothing beyond `+alive`.
  - The reason: under `other` the observed log-on was not caused by the flame-out, so most of those descents flame out later, and a later flame-out
    predicts a second log-on that was not seen.
  - This makes the `other` cause and the silence after 00:19:37 hard to reconcile, unless the aircraft hit the water within about two minutes of a later flame-out.
- **Recommendation, taken provisionally:** downstream modules use **`+alive`** as the reference for every option. **`+silent`** is reported as a labelled
  sensitivity until Pete rules. The `+silent` physics is a stated assumption: the APU auto-starts, and the SDU re-logs on, after a later flame-out.
- **For hydroacoustics:**
  - Under `+alive`, no impact precedes 00:19:37.443 in any option.
  - Impacts after 01:15:56 are 1.9% (held out, `other`) or less, and under `+silent` none is powered at 01:15:56.
  - Derive windows per option and cause from the `+alive` rows, with `+silent` beside them.
