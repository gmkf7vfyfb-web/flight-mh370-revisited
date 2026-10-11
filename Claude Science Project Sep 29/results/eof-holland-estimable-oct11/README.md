# End of flight: making 00:19 Holland H1 and H2 estimable (architecture 10:50 -0600, 11 Oct 2026; Pete confirmed 11:00)

**SMOKE SCALE, PROVISIONAL. Not evidence.** Section 1 is N = 1 child x 4 descents on core run D `next-d-free` seed 1 (m0011
look-ahead hand-off, read with `handoff::read_corrected`), constraint `unpowered` (the reference). Section 2 (full N = 8 x 4, seeds
1 and 2) is added when the run ends. Binary `/tmp/mh370-eof-he` (sha256 b747f8065050a76f), module branch `hypothesis/end-of-flight`.

## What changed (module only; switches off = earlier behaviour; 108 tests pass)

1. **Piloted rapid descent (item 4) widened.** Eligible shapes: powered emergency descent (as before), powered or unpowered
   continuous descent, unpowered best glide (new). Stepped shapes are not eligible (declared gap G-st). Commanded rate
   U[6,500, 40,000] ft/min; upper end from NTSB AAB-02/01 (EgyptAir 990, Boeing 767-300ER: about 39,000 ft/min, load factor
   down to about -0.2 g, Mach 0.99). Load-factor floor U[-1.0, 0.8] g (CS-25.337(c)). New: the target Mach is limited to the Mach
   of VMO = 330 KCAS at the current altitude (777-200 VMO 330 KCAS / MMO 0.87, FAA TCDS T00001SE). Label: `latent:pushover_drawn`
   = 1 is the emergency-descent shape; the base shape code stays in `latent:shape`.
2. **INTERIM parametric pitch-down** in uncontrolled free flight (no intervention from the onset; the free phase after control
   maintained then lost). During the pulse the trim lift is replaced by load factor n ~ U[-0.31, 0.69] g (Boeing no-input
   simulations: peak downward accelerations 0.31-1.31 g below 1 g, SIR App. 1.6E case by case) for U[4, 20] s, starting
   U[0, 900] s after the free phase begins. Prior probability a U[0, 1] hyper-parameter, proposal 0.5 = the marginal; exact
   re-weighting with `latent:pitchdown_eligible` / `pitchdown_drawn`. Labelled INTERIM until the 6-DOF gate passes.
3. **Targeted proposal** (Pete GO). The push-over start (onset + hold) and the pitch-down start are drawn, with probability w,
   uniformly in [00:19:29.416 + a, 00:19:29.416 + b] intersected with the prior support, otherwise from the prior. The exact
   ln(prior/proposal) goes into the profile correction; `terminal.within_parent = "unnormalised"` (core request 9) keeps it exact
   (self-normalisation within a parent cancels it at N = 1). Adopted w = 0.8, [a, b] = [-20, +2] s (table below).
4. Normalisation check (run C free seed 1, N = 1, recipe without these changes): self-normalised against unnormalised weights
   give Held Out ln Z -0.0292 vs -0.0289, families A1 0.119 / A2 0.326 / B 0.554 in both, effective parents 99,030 vs 94,515
   (`n1-normalisation-run-c-free-s1.json`). At 00:11 the proposal corrections are small, so the bias found at 22:41 does not
   move the 00:11 products. Unnormalised weights are used from now on.

## 1. N = 1 smoke, run D free seed 1 (`n1-targeting-*.json`; tool `smoke/holland_ess.py`)

| Arm | Option | ln Z | Effective impacts | A1 share / eff. | A2 share / eff. | B share / eff. | Push-over share | Pitch-down share | Median latitude |
|---|---|---|---|---|---|---|---|---|---|
| Items 2-4 (run D smoke), self-normalised, no pitch-down | 00:19 Held Out | -0.05 | 177291 | 0.12 / 20707 | 0.32 / 56216 | 0.56 / 100278 | 0.14 | 0.00 | -37.52 |
| Items 2-4 (run D smoke), self-normalised, no pitch-down | 00:19 R600 BTO Only | -5.71 | 227573 | 0.10 / 22770 | 0.31 / 73831 | 0.58 / 130980 | 0.15 | 0.00 | -38.08 |
| Items 2-4 (run D smoke), self-normalised, no pitch-down | 00:19 Holland H1 | -29.36 | 5 | 0.00 / 2 | 0.23 / 1 | 0.77 / 4 | 1.00 | 0.00 | -38.11 |
| Items 2-4 (run D smoke), self-normalised, no pitch-down | 00:19 Holland H2 | -23.28 | 6 | 0.00 / 1 | 0.56 / 3 | 0.44 / 3 | 1.00 | 0.00 | -37.83 |
| New recipe, untargeted | 00:19 Held Out | -0.06 | 139406 | 0.12 / 20549 | 0.32 / 55928 | 0.56 / 67308 | 0.28 | 0.24 | -37.41 |
| New recipe, untargeted | 00:19 R600 BTO Only | -5.73 | 175801 | 0.11 / 22243 | 0.31 / 72388 | 0.58 / 87977 | 0.29 | 0.24 | -37.98 |
| New recipe, untargeted | 00:19 Holland H1 | -29.04 | 9 | 0.15 / 2 | 0.44 / 8 | 0.42 / 2 | 0.85 | 0.24 | -37.87 |
| New recipe, untargeted | 00:19 Holland H2 | -21.84 | 11 | 0.04 / 1 | 0.18 / 11 | 0.78 / 7 | 0.95 | 0.15 | -38.03 |
| New recipe, targeted 0.5 in [-30, +2] s | 00:19 Held Out | -0.06 | 125551 | 0.12 / 16982 | 0.32 / 51032 | 0.56 / 61131 | 0.28 | 0.24 | -37.41 |
| New recipe, targeted 0.5 in [-30, +2] s | 00:19 R600 BTO Only | -5.73 | 159364 | 0.11 / 19612 | 0.31 / 65115 | 0.58 / 80227 | 0.29 | 0.24 | -37.99 |
| New recipe, targeted 0.5 in [-30, +2] s | 00:19 Holland H1 | -28.69 | 76 | 0.06 / 18 | 0.49 / 45 | 0.45 / 26 | 0.93 | 0.31 | -37.80 |
| New recipe, targeted 0.5 in [-30, +2] s | 00:19 Holland H2 | -22.04 | 32 | 0.05 / 13 | 0.34 / 28 | 0.61 / 14 | 0.93 | 0.25 | -37.49 |
| New recipe, targeted 0.8 in [-30, +2] s | 00:19 Held Out | -0.06 | 96156 | 0.12 / 11021 | 0.32 / 39304 | 0.56 / 48091 | 0.28 | 0.24 | -37.40 |
| New recipe, targeted 0.8 in [-30, +2] s | 00:19 R600 BTO Only | -5.73 | 126050 | 0.11 / 14716 | 0.31 / 50529 | 0.58 / 64386 | 0.29 | 0.24 | -37.99 |
| New recipe, targeted 0.8 in [-30, +2] s | 00:19 Holland H1 | -28.71 | 117 | 0.06 / 18 | 0.46 / 66 | 0.48 / 45 | 0.93 | 0.30 | -37.81 |
| New recipe, targeted 0.8 in [-30, +2] s | 00:19 Holland H2 | -22.10 | 33 | 0.04 / 18 | 0.39 / 16 | 0.56 / 16 | 0.92 | 0.30 | -37.36 |
| New recipe, targeted 0.8 in [-20, +2] s (adopted) | 00:19 Held Out | -0.06 | 96182 | 0.12 / 10955 | 0.32 / 39216 | 0.56 / 48197 | 0.28 | 0.24 | -37.40 |
| New recipe, targeted 0.8 in [-20, +2] s (adopted) | 00:19 R600 BTO Only | -5.73 | 126221 | 0.11 / 14415 | 0.31 / 50049 | 0.58 / 64911 | 0.29 | 0.24 | -37.98 |
| New recipe, targeted 0.8 in [-20, +2] s (adopted) | 00:19 Holland H1 | -28.92 | 158 | 0.07 / 17 | 0.49 / 82 | 0.44 / 62 | 0.92 | 0.29 | -37.83 |
| New recipe, targeted 0.8 in [-20, +2] s (adopted) | 00:19 Holland H2 | -21.98 | 49 | 0.05 / 16 | 0.38 / 19 | 0.57 / 25 | 0.92 | 0.26 | -37.59 |

| Arm | ln BF H1:H2 at W = 60 / 300 / 900 / 1,775 / 3,600 s | Break-even W (s) |
|---|---|---|
| Items 2-4 (run D smoke), self-normalised, no pitch-down | -1.98 / -0.37 / +0.72 / +1.40 / +2.11 | 436 |
| New recipe, untargeted | -3.10 / -1.49 / -0.39 / +0.29 / +0.99 | 1331 |
| New recipe, targeted 0.5 in [-30, +2] s | -2.55 / -0.94 / +0.16 / +0.84 / +1.54 | 768 |
| New recipe, targeted 0.8 in [-30, +2] s | -2.52 / -0.91 / +0.19 / +0.87 / +1.58 | 745 |
| New recipe, targeted 0.8 in [-20, +2] s (adopted) | -2.85 / -1.24 / -0.14 / +0.54 / +1.25 | 1032 |

H1:H2: "other" (H2) has no log-on-time density, so its likelihood is 1/W over a declared log-on window W; H1 carries the
Erlang(8, 14.875 s) lag density. ln BF(H1:H2) = ln Z_H1 - ln Z_H2 + ln W. The break-even W moves with Monte Carlo noise at these
ESS (436-1,331 s); the full-N value replaces it.

Reading (smoke): targeting raises H1 effective impacts 9 -> 158 and H2 11 -> 49 at N = 1; the other options keep ESS above 96,000.
ln Z of H1/H2 does not move outside Monte Carlo noise (H1 -28.7 to -29.4; H2 -21.8 to -23.3), which is the check that the
proposal correction is exact. 92-95% of the H1/H2 posterior is in push-over rows. Effective impacts equal effective parents for
H1/H2: each contributing impact comes from a different parent, so ESS scales about linearly with children (expected about 32x
at N = 8 x 4).

## COVERAGE

- (a) FEASIBLE set: piloted descents to about 39,000 ft/min and unloading to -1.0 g (NTSB AAB-02/01; CS-25.337(c)); speed to
  VMO/MMO and beyond in a dive (EgyptAir 990 reached Mach 0.99); uncontrolled pitch-downs with peak downward accelerations
  0.31-1.31 g below 1 g and no-input descents to 24,000-58,000 ft/min (SIR App. 1.6E).
- (b) MODEL'S REACH: push-over to 40,000 ft/min, floor -1.0 g, in emergency, continuous and best-glide shapes; interim pitch-down
  in free flight. GAPS: G-st stepped shapes have no push-over (declared, conditional); G-H2 no structural limit (4.5% of impacts
  at or above Mach 1 at sea level in run C; 212 m/s two-version display is the stop-gap; breakup model is item 5, pending);
  the pitch-down is parametric (INTERIM, not the 6-DOF).
- (c) PROPOSAL COVERAGE: table above; per family A1 / A2 / B effective impacts for H1 17 / 82 / 62 and H2 16 / 19 / 25 at N = 1.
  A1 carries 5-7% of the H1/H2 posterior, through the pitch-down only. Full-N ESS per option and family: section 2.
- Bounds and sources: rate U[6,500, 40,000] ft/min (NTSB AAB-02/01); floor U[-1.0, 0.8] g (CS-25.337(c)); hold U[0, 300] s
  (declared reaction time, covers the log-on lag); VMO 330 KCAS (FAA TCDS T00001SE); pitch-down n U[-0.31, 0.69] g (SIR App. 1.6E),
  duration U[4, 20] s and delay U[0, 900] s (declared).
