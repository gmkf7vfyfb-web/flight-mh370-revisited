# End of flight: fuel burn in the descent (Pete, architecture ~21:00 UTC, 9 Oct 2026)

**SMOKE SCALE, not evidence. Uses the UNCORRECTED core fuel model** (audit findings F1-F4 pending core request 16).

The runs are all seed 1, with no 00:19 data (option `none`, hand-off weights only):
- V1 and V2: the 22:41 hand-off (`runs/snap-m2241`, the `reference-snapshots` chain, 295.66° prior; superseded if core re-runs it),
  BTO-only options, NOT THE ARM, N = 4 children x 4 descents;
- the 00:11 reference-289 hand-off, N = 1 child x 4 descents.

Build: hypotheses/end-of-flight at this commit. Floor-off output is byte-identical to the reference-289 build (sha256 68ee1469...).

## 1. Does the descent burn at the cruise rate? No, and it did not before this change

- **Onset uses the cruise prediction, by design.** `takeover_priced` draws the onset on the endurance predicted under continued cruise: that is what
  "anticipatory" and "fuel cue" mean, the crew's own cue. Core request 3, landed, prices that prediction with the core's tables.
- **The exhaustion itself is not inherited.** After onset the module integrates the burn at the descent's own thrust,
  flow = thrust x (core table flow / level-flight drag) (`integrator.rs`). The realised flame-out comes from that integration.
- **The weakness was idle**, where that scaling understates the flow. Added: an **idle floor**, so a running engine never
  burns less than its idle flow.
  - Source: ICAO Aircraft Engine Emissions Databank, Trent 892, UID 2RR027 (9M-MRO's engine type), idle mode 0.30 kg/s per engine
    at sea-level static ISA (EASA download 131424, sha256 57a9ff57...).
  - Altitude scaling, drawn per descent: between corrected-flow scaling (delta sqrt(theta), about 0.061 kg/s per engine at FL350 M0.80) and the Boeing Fuel Flow Method 2
    form (delta / theta^3.8 exp(-0.2 M^2), about 0.177 kg/s; DuBois & Paynter 2006, SAE 2006-01-1987).
  - Off by default; enabled by `full/descent-idle-floor.toml`.

## 2. How far the descent moves exhaustion against the cruise prediction

The measure is the ratio R = (onset to realised flame-out) / (cruise-predicted endurance at onset), over descents powered at onset.
It is a weighted Kaplan-Meier estimate, censored at impact for descents that reach the sea with fuel left. The censoring matters: only
fast-burning descents run dry before the sea, so the uncensored median (V2: flame-out 662 s earlier than predicted) is biased early.

| run | R 25% | **R median** | R 75% | continuous | emergency + approach | stepped level-offs | free trim |
|---|---|---|---|---|---|---|---|
| V2, floor off | 0.69 | **1.15** | 1.99 | 1.16 | 0.53 | 0.88 | 2.22 |
| V2, floor on | 0.69 | **1.14** | 1.98 | 1.14 | 0.53 | 0.88 | 2.19 |
| 00:11 ref-289, floor off | 1.14 | **2.19** | 3.51 | 2.35 | 0.47 | 1.49 | 3.20 |
| 00:11 ref-289, floor on | 1.14 | **2.19** | 3.52 | 2.37 | 0.47 | 1.49 | 3.23 |

Reading:
- **On the median, the descent pushes exhaustion out**, as Pete expected: by about 15% in V2, where the cruise-predicted
  endurance at onset is up to 96 min.
- **The effect is strongly profile-dependent.** Profiles that come down fast and then fly a long low-altitude approach
  (emergency-then-transition) burn about twice the cruise rate, R = 0.53. Low and fast costs fuel. This class pulls exhaustion
  **earlier**.
- **The idle floor is immaterial at this scale:** <= 0.03 in R; flame-out-before-impact share and the share in the log-on lag window change by < 0.3 points. The
  thrust-scaled burn already sat above idle almost everywhere the descents fly.
- V1 (flame-out-associated only) has no powered descent and so no burn question.

**For H1 against H2 (Pete's link):** in V2 at smoke scale, only 1.6% of the powered-at-onset weight flames out in the log-on lag window
[00:19:29 - 250 s, - 20 s], against 8.5% at the 00:11 hand-off. That is why V2 is where the `other` log-on cause is natural.

## 3. Status
- Adopt the floor at the next announced re-sweep, together with the 6-DOF fast model. It does not justify a re-run alone.
- Every FE time here uses the uncorrected core fuel model. Re-measure when core request 16 lands.
