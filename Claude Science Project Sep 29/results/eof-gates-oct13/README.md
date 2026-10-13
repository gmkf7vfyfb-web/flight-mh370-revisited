# End of flight — smoke gates and pilot runs before the 22:41 arm, 13 Oct 2026

**Status: SMOKE AND PILOT SCALE. Nothing here is evidence for an impact distribution, a log-evidence, a Bayes factor or a family
share.** Work order `eof-work-order-items-1-2.md` v2 (item 0 and its four gates), contract `threads/master-prompts/end-of-flight.md`
v7.1. Binary `mh370-eof-o13` (sha256 d3221785…), built from `hypothesis/end-of-flight` 10255b6 with `CARGO_TARGET_DIR` outside the
tree. Core run I, stratum `next-i-waypoints` (core P(family) 0.9982), seed 1 for the pilots, seeds 1–8 for gate 3.

## 1. Gates

| gate | result |
|---|---|
| scope (`make scope H=end-of-flight`) | passes on the working tree; the shallow clone had no `origin/claude-science-sep29`, so the base diff was re-run after a fetch before commit |
| 1 `make smoke H=end-of-flight` | **failed as shipped**: with no `[terminal]` block in `run.toml` the module fell into the trajectory role and `main.rs:96` refused it ("declares alternatives, but trajectory strata are not built yet"). Fixed inside the module (`run.toml` now sets `[terminal] module = "end-of-flight"`); passes, 3 min 47 s at 2 threads. Code paths only |
| 2 unit tests (`cargo test -p mh370-hypotheses`) | 116 passed, 0 failed, 6 ignored. Item 1's closed-form tests do not exist yet (item 1 not started) |
| identity | P0011 (N = 4) reproduces the first 4 of 16 children of run-i-dive seed 1 in every physics column to float32 precision (max relative difference 6 × 10⁻⁸; NaN patterns identical; weight ratio exactly 4.000, as the unnormalised within-parent rule requires). **The rebuilt binary is the run-i-dive model** |
| 3 ESS at intended counts | 00:11: measured by subsampling run-i-dive (no new descents), table §2. 22:41: measured on pilot P2241, table §3 |
| 4 reduced 22:41 run | P2241, 100,000 parents × 4 children × 4 descents, 145 s at 12 threads (1.56× the 00:11 cost per descent, against 1.52× predicted). Table §3 |

## 2. Gate 3 at 00:11 — per-seed effective impacts, 8 seeds, all 100,000 parents

Minimum over seeds unless stated. Cells as `option_table_0019.py` (competing causes q = 1/3, C2 silent, survival factor).

| cell | N | ESS min | ESS median | eff. parents min | A1 min | A2 min | B min |
|---|---|---|---|---|---|---|---|
| D0 total | 16 | 68,522 | 115,744 | 14,282 | 22,196 | 31,832 | 27,488 |
| D2 total | 16 | 5,374 | 8,393 | 3,997 | 1,744 | 2,646 | 1,442 |
| D3 total | 16 | 289 | 737 | 286 | **13** | 146 | 121 |
| D3 × C2 silent | 16 | 156 | 352 | 156 | **5** | 115 | 68 |
| D4 total | 16 | 2,570 | 3,925 | 2,238 | 140 | 1,767 | 1,049 |
| D5 total | 16 | 693 | 1,393 | 662 | **43** | 416 | 308 |
| D3 total | 4 | 59 | 205 | 59 | 12 | 40 | 31 |
| D4 total | 4 | 596 | 1,295 | 568 | 32 | 401 | 332 |

ESS rises roughly linearly in N for the held-out and R600 cells, and **much less than linearly for the raw-R1200 cells**, where
effective parents ≈ ESS: those cells are parent-limited, not child-limited. Full grid (P = 10k / 25k / 100k × N = 4 / 8 / 16 × 8
seeds): `g3-0011-waypoints.csv`.

Filter at 00:11 for comparison (core run I, waypoints, seed 1, ESS after the m0011 update, per autopilot mode): 14,000 / 2,363 /
133,305 / 6,485 / 61,560, against 634k / 379k / 1,593k / 360k / 1,600k after m2315 — the filter itself keeps only 0.6–8 % of its
ESS across 00:11.

## 3. Gate 4 — the 22:41 pilot (P2241), seed 1, N = 4

V2 with all three onset mechanisms sampled, so V1b (flame-out-associated subset) and families A1, A2 and B are all estimable from
one sample set. Rows below use run-i-dive's deliberate-control prior [0.5, 0.5, 0, 0] (`family-b-ditching.toml`), recovered exactly by
re-weighting; the all-four sampling is in `gate4-p2241.csv`. Families are `family4_code` per ruling 6: B = code 3; code 6
(deliberate onset, then no intervention) is **outside B** and has zero weight under this prior.

| cell | family | share | ESS | eff. parents | top-1 | onset within 60 s of 22:41 | median onset, min after 22:41 |
|---|---|---|---|---|---|---|---|
| prior | A1 / A2 / B | 0.11 / 0.24 / 0.65 | 30,145 / 53,337 / 57,810 | | | 0.7 % / 0.6 % / **11.8 %** | 60 / 60 / 25 |
| D0 (23:15 + 00:11) | A1 / A2 / B | 0.24 / 0.51 / 0.24 | 921 / 1,804 / **26** | 527 / 1,181 / 26 | | 0.0 % all | 97 / 97 / 76 |
| D1 R600 BTO | A1 / A2 / B | 0.26 / 0.60 / 0.15 | 1,051 / 2,086 / **40** | | | 0.0 % all | 97 / 97 / 95 |
| D2 R600 BTO + BFO | A1 / A2 / B | 0.27 / 0.68 / 0.04 | 85 / 286 / 41 | | | 0.0 % all | 97 / 97 / 95 |
| D3 both raw | A1 / A2 / B | 0.22 / 0.69 / 0.10 | **3** / 17 / **11** | | 0.48 (A1) | 0.0 % all | 97 / 97 / 95 |
| D4 both, start-up offset | A1 / A2 / B | 0.20 / 0.63 / 0.18 | 14 / 86 / 25 | | | 0.0 % all | 97 / 97 / 96 |

Support truncation (`latent:onset_support_truncated_fraction`) **is populated** (finite in 100 % of rows; the work order's NaN column
is not present in this build). Weighted mean 0.30 for B under the prior, 0.21–0.34 posterior. Per-trajectory onset window
(hand-off to predicted exhaustion): 2,604 / 5,558 / 5,884 / 6,234 / 6,927 s at the 5th–95th percentiles of rows; posterior
median ~5,830 s (97 min).

**What the pilot shows, at this scale.** (i) The 22:41 boundary is not where supported mass sits: 0.0 % of posterior weight
within 60 s of 22:41 in every family and every cell, against the 5 % gate; supported B onsets sit at a median 76 min after 22:41
under the held-out treatment and ~95 min (about 00:16) once the R600 BTO is scored. That is the work order's late-end prediction.
(ii) It is **not estimated**: B carries 11–40 effective impacts per seed, A1 3–14 under the R1200 cells.

## 4. Findings to act on

1. **The 22:41 arm is sampling-limited at 00:11, not at the boundary.** Scoring 23:15 + 00:11 in-stage leaves 0.5 % of the
   prior ESS (218,635 → 1,074 effective impacts, 836 effective parents, in the D0 cell with the log-on cause and survival terms; the bare m0011 column in `terminal.json` gives 1,475 and 968). Scaling the pilot by N = 16 and 8 seeds gives roughly B ≈ 90 and A1 under the raw
   R1200 cells ≈ 10 per seed. The arm as sized in the work order would not support the R1200 cells or family B. Options for the
   fix are in `coordination/architecture.md` (13 Oct entry).
2. **Defect: fuel-cue onsets are CLAMPED to the hand-off, not truncated.** `onset.rs` `draw()`: `(onset.max(earliest_unix_s), 0, 0)`
   for `FuelCue`, and the truncated fraction is recorded as 0. This puts an atom at the hand-off epoch (11.8 % of B's prior weight
   within 60 s of 22:41) and is a likely mechanism of the 21.6 % onset-boundary statistic at 00:11, where the 30–70 min cue window
   lies almost wholly before the hand-off. The anticipatory mechanism is truncated exactly. Fix: exact truncation behind a config
   flag (legacy clamp kept for reproduction), with the truncated fraction emitted.
   **Fixed (13 Oct, binary `mh370-eof-o13b`, sha256 abeb4c2f…):** `onset.fuel_cue_truncation = "exact"`
   (`smoke/fuel-cue-exact.toml`; default stays `"clamp"` so earlier runs reproduce), with two new unit tests (Irwin–Hall CDF against
   closed forms and the density; the clamp's atom equals the closed-form cut and the exact draw has none). Re-run of P2241 with it:
   B's prior weight within 60 s of 22:41 falls from 11.8 % to 3.7 % (what remains is the truncated prior's own density just after
   the hand-off, not an atom); **rule 11 before/after: every scored cell is unchanged** — D0 shares 0.242 / 0.515 / 0.243 and ESS
   921 / 1,804 / 26 both ways, m0011 log-evidence increment −16.718 both ways — because the boundary rows carry no posterior weight
   from 22:41. Not prompted by a fit failure. `gate4-p2241-cueexact.json`.

3. **Withdrawn (13 Oct, same session).** An earlier version of this note said `option_table_0019.py` wrongly left family code 6
   out of B. That was my misreading: under ruling 6, code 6 is *deliberate onset, then no intervention*, which is **outside B**,
   and the table is correct. What is new is that the all-four control sampling (finding 4) gives code 6 real weight for the first
   time (16 % of the 22:41 prior, 2 % after 00:11), so every 22:41 summary must report it as its own row rather than omit it.
4. **Coverage fix applied in the pilot:** deliberate-onset control outcomes sampled over all four (contract §4 change E). The
   run-i-dive prior [0.5, 0.5, 0, 0] is recovered exactly by re-weighting on `latent:control_requested`. Under the all-four
   sampling, deliberate onsets split into B (code 3, incl. upset-then-recovery and control lost en route) and outside B (code 6,
   no intervention). Whether code 6 should be a named family is a question for the architecture session, not settled here.
5. **D5 at 22:41 is not computable from stored columns**: the bias variance after the in-stage 23:15 and 00:11 updates is not
   emitted. Gap until the stage emits it or D5 gets its own `loglik` column.

## 5. COVERAGE

**(a) Feasible set.** As in `eof-run-i-dive-oct13` §3: any 777-200ER descent from cruise within its performance and structural
limits, initiated from 22:41 onward by anticipation, a fuel cue or flame-out, with two, one or no engines, under all four control
outcomes. Sources as there.

**(b) Model's reach.** Unchanged from run-i-dive (dive branch closed; INTERIM pitch-down; no transonic drag rise; provisional turn
model; symmetric point mass in single-engine flight — item 1). Additional reach gaps found today: the fuel-cue clamp (finding 2)
moves cue onsets earlier than the hand-off onto the hand-off; deliberate-onset control outcomes "no intervention" and "upset then
recovery" were unreachable under v2-broad / family-b-ditching (now sampled in the pilot only).

**(c) Proposal's coverage.** Tables §2 and §3. Below 1,000 effective impacts per seed: at 00:11, every raw-R1200 cell for A1 (5–43)
and B (68–308), D3 total (289); at 22:41 (pilot), B and outside-B in every scored cell, and every family under D2–D4. Status: reported as gaps;
fix proposals in `coordination/architecture.md`.

**Onset-boundary gate (named row).** 00:11 hand-off: 21.6 % (13 Oct audit, deliberate family) — FAILED. 22:41 pilot: 0.0 % in
every family under every cell — PASSES AT PILOT SCALE ONLY, with B at 11–40 effective impacts, so the statistic is unconverged.

**Parameter bounds.** Unchanged from run-i-dive; deliberate-onset control sampling [1,1,1,1] in the pilot (`smoke/deliberate-control-all4.toml`).
