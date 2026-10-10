# Residual roll direction of free flight: defect found and corrected (end of flight, 10 Oct 2026, ~22:40 UTC)

**SMOKE SCALE. PROVISIONAL.** Seed 1, N = 1 child x 4 descents, core next-run (b) `next-free` hand-off at 00:11 (seed 1,
100,000 parents), run C module recipe (eof-289-full + descent idle floor + v2-broad + family-b-ditching). Binary built from
32aa6ce0 + this change. Reach-gap label (architecture 15:45 -0600): rapid descents above 6,500 ft/min and unloading are not
reachable by the model.

## Defect
`envelope.residual_bank_deg` is U[0, 35] deg and was used with its sign as drawn: always positive, and positive bank is a
RIGHT turn. So **every free-flight (uncontrolled) descent turned right.** Boeing's no-input simulations (SIR App. 1.6E p. 8):
the right engine runs dry first, TAC applies left rudder, about 0.2 deg of left rudder remains after the left engine spools
down and the autopilot disconnects, and the aircraft rolls slowly left. 8 of Boeing's 10 cases turned left (cases 4 and 10
turned right).

## Change (module only)
- `envelope.residual_bank_left_probability` (Option; absent = the old behaviour exactly, with no extra draw).
- Overlay `full/residual-bank-boeing.toml`: P(left) = 0.8 (Boeing's 8 of 10; PROVISIONAL - options posted to Pete).
- New latent `residual_bank_sign` (-1 left, +1 right, NaN when the profile has no free phase), also in the compact format, so
  any other P(left) is an exact re-weighting afterwards: factor q/p for left rows, (1-q)/(1-p) for right rows.
- Test added (103 pass). With the switch absent, output equals the run C binary (`/tmp/mh370-eof-runc3`) in every one of the
  106 existing columns (`np.array_equal`, NaN-aware); the only difference is the appended column.
- Left share drawn with P = 0.8: 0.7998 of the rows with a free phase (60.9 % of rows have one).

## Effect: cross-track displacement from the takeover track (NM, + = right of track), weighted median latitude (deg)
00:19 Held Out with the `alive` constraint:

| family | weight | mean cross-track, before | after | share right, before | after | median lat before | after |
|---|---|---|---|---|---|---|---|
| A1 | 0.10 | +7.5 | -13.2 | 0.78 | 0.16 | -36.72 | -36.78 |
| A controlled then lost | 0.14 | +0.5 | -4.0 | 0.53 | 0.28 | -37.93 | -37.95 |
| A2 | 0.19 | +2.2 | -8.1 | 0.35 | 0.26 | -37.77 | -37.79 |
| B | 0.29 | -1.0 | -1.0 | 0.38 | 0.38 | -37.78 | -37.78 |
| B, control lost en route | 0.28 | +0.4 | -2.3 | 0.51 | 0.39 | -37.38 | -37.39 |
| all | 1.00 | +1.1 | -4.4 | 0.47 | 0.33 | -37.56 | -37.57 |

00:19 R600 BTO Only (+alive): all families -5.0 NM after (+0.3 before); A1 -14.7 (+7.0). Full table:
`cross-track-by-family-n1-seed1.json`.

Reading: the change moves uncontrolled impacts about 20 NM across track for A1 and about 5 NM for the whole mixture. The
latitude moves by at most 0.06 deg. The shift is not symmetric (+7.5 against -13.2) because the left and right turns are
flown with the same wind and not mirrored. B is unchanged, because B flies no free phase except after a loss en route.

## COVERAGE
(a) Feasible set: both roll directions are feasible after a dual flame-out with residual rudder or aileron trim.
(b) Model reach: before this change, only right turns could be reached (a silent gap, now closed). Now both directions.
(c) Proposal coverage: P(left) = 0.8 in run C. Re-weighting to P(left) = 0.5 keeps ESS at 0.64 of the free-phase rows (1/E[w^2])
(factors 0.625 / 2.5); to the old always-right prior keeps only the right rows (20 %). Bounds: |bank| U[0, 35] deg (module
envelope, unchanged); P(left) source Boeing SIR App. 1.6E p. 8 (8/10). Not covered: the correlation between roll direction
and which engine flames out first (the module does not yet carry it). Declared.

Run C: included (watcher re-armed on the corrected binary before core's READY).

- End of flight
