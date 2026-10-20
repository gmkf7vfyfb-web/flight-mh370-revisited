# Routes audit arms — turn-point scan and matched volume (11 Oct 2026)

36 routes: VAMPI–MEKAR–NILAM–PTxx–END. PTxx are pseudo-fixes on the ANOKO→NILAM great circle at −15…+40 NM (+ = east,
toward NILAM). END ∈ {ISBIX, ISBIX 5 NM west, ISBIX 5 NM east}. 4 seeds × 200k particles per route, ad50 tempering
(the same as the route pilot it is compared with), `turn_backs`, run C stack, binary 3c2747e, deskstar job 56cc5d6f.
Table: `audit-arms-turn-point-scan.csv` (ln Z mean and sd over seeds, 00:19 median, split-half per arm).

| Prediction (posted before the run) | Result |
|---|---|
| Scan peaks at +5 to +15 NM, about −125.2 | **holds:** peak +10 NM, ln Z −125.27 (seed sd 0.18); +5 −125.88, +15 −125.96 |
| Matched-volume ln Z (log-mean-exp over 36 arms) −131.5 ± 1.0 | **missed:** −128.07 (3.4 nats higher). Over the 12 ISBIX-end arms only it is −126.97 |

- At the true ISBIX the scan is smooth: −128.51 at ANOKO (0 NM), peak at +10, −133.2 at +40, −140.5 at −15.
- Moving the end point 5 NM east or west costs 10–14 nats at every turn point. Route mode has no lateral freedom on the
  southbound leg, so the 19:41 BTO/BFO pin the leg to within a few NM of the published ANOKO–ISBIX line.
- The 00:19 median moves with the turn point: −36.68 (0 NM), −37.07 (+5), −37.37 (+10), −37.65 (+15).
- Per-arm split-half at this size is not converged (ISBIX-end arms 0.60–0.93), so the 00:19 values are indicative only.
  ln Z sd ≤ 0.46 on the ISBIX-end arms. The ±5 NM arms are noisier (sd up to 2.4).
- Interpretation (hypothesis, under test): the engine's route turn is fly-over plus direct-to (`steer`, sequence within
  2 NM, 15° bank, no anticipation). A fly-by at ANOKO would start ≈ 14 NM before the fix, so the +10 NM peak may be a
  fly-by surrogate. See CORE_STAGES 17:35Z.

## 00:19 label (Pete's ruling, CORE_STAGES 21:20Z, 11 Oct 2026)

Every 00:19 latitude, position or map in this folder is taken from a core run's full posterior (final.npy) and is labelled **"core, Davey both-BTO no-BFO 00:19 treatment"**. Tables carry it in the column `label_0019`. Design 00:19 positions and impacts come only from end of flight, under a named standard 00:19 option.
