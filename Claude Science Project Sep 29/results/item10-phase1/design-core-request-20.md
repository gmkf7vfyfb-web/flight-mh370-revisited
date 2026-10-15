# Item 10, Phase 1: the 00:19 two-burst hand-off proposal — design note (core request 20)

Core, 15 October 2026. Order: `threads/work-orders/core-order-2026-10-15b.md` step 4, full specification
`threads/work-orders/item10-order-rev2-2026-10-15.md`. **Design only. Nothing here has been run.** Phase 2
needs Pete's explicit GO.

Name: **core request 20**, "hand-off proposal from pilot descents". It is not core request 9 (`d4e67b09`,
`[terminal] within_parent = "unnormalised"`), and it does not need request 9.

## 1. What the device must do

The hand-off at 00:10:59 (m0011) gives end of flight 100,000 parent states per seed. Under any arm that
scores both 00:19 bursts, very few parents can produce the pair. For both bursts raw, the effective parents
are 38.8 per seed, and one trajectory carries 12.3% of the weight. End of flight's full-scale table
(architecture.md, about line 4590) shows effective impacts equal to effective parents in those arms. In each
surviving parent, one child of 32 carries the weight. The limit is therefore WHICH parents are handed off,
not how their children are drawn.

The device must draw the 00:11 parents in proportion to their probability of producing the 00:19
observations under end of flight's descent model. It must carry the exact prior-to-proposal ratio, so the
target posterior does not change.

## 2. Why request 18 (`handoff-lookahead-d`) did not raise the effective parents

Request 18 at m0011 uses horizon m0019b with `g_source = "smoothing"`. Its g for a candidate is the fixed-lag
smoothed share of that candidate's descendants at 00:19:37 under the CORE filter's own continuation,
divided by its filtered share. Measured from run I's diagnostics on deskstar (descent-climb, repro-radar and
waypoints strata, 8 seeds × 5 modes; table in `lookahead-diagnostics-run-i.csv`, this folder):

| hand-off → horizon | g > 0 (share of candidates) | ESS of g over the 5M candidates, as a fraction |
|---|---|---|
| 22:41 → 00:11 | 0.005–0.039 | 0.0011–0.0215 (very concentrated, so the look-ahead had work to do) |
| **00:11 → 00:19:37** | **0.44–0.49 (magnetic modes), 1.00 (others)** | **0.32–0.78 (nearly flat)** |

1. **g looked at the wrong data.** The core filter flies cruise dynamics from 00:11 to 00:19:37 and excludes
   the 00:19 BFOs, because they belong to end of flight. So g carries only the 00:19 BTO ring. Almost every
   cruise continuation from a state that fits 00:11 reaches the 7th arc within the BTO sd. So g is nearly
   flat (ESS fraction 0.32–0.78), the proposal q ≈ uniform, and the hand-off is the same as without the
   look-ahead. The defensive weight 0.2 makes it flatter still.
2. **A cruise continuation cannot represent the binding constraint.** The pair 182 Hz → −2 Hz in 8 s needs
   a descent with loss of control 0–160 s before 00:19:29, at 19–57 kft/min and Mach 0.8–1.0 (end of
   flight's survivor diagnosis, architecture.md about line 4760). Under cruise dynamics the predicted
   00:19:37 BFO stays near the cruise value. So no cruise-based g can tell a parent that can make the dive
   from one that cannot.
3. **The zero-g candidates in the magnetic modes are smoothing noise, not information.** About 55% of
   candidates there have g = 0 because their descendants were lost to resampling between 00:11 and
   00:19:37. That is not evidence that they cannot fit the data.
4. **Oversampling 50× a flat g only adds duplicates.**

The 22:41 look-ahead did work (ESS fraction 0.80 after the draw against 0.001–0.02 before), because its
horizon data (23:15 BFO, 00:11 BTO and BFO) are cruise data, which the core models.

## 3. The proposal law and its importance correction

**g must come from the descent model itself.** The quantity to aim at is the parent-level marginal
likelihood of the 00:19 data:

    ℓ_a(x) = ∫ p(y_0019 | x, θ, arm a) p(θ | x) dθ,

where x is the parent state at 00:10:59 (position, velocity, altitude, Mach, fuel state and factor, tanks,
BFO bias mean and variance), θ is end of flight's latents (takeover, family, descent laws), and arm a is a
00:19 treatment (`both_no-offset`, `both_startup-offset`, `both_inflated`, the R1200 arms, and so on).

**Step A — candidates (unchanged).** At m0011 the filter draws M = oversample × rows candidates by systematic
resampling of its posterior (stream 5100+k, as today). Candidates are grouped by their filter particle index;
D ≤ N_mode distinct particles result.

**Step B — pilot g.** For each distinct particle u, fly L pilot children with end of flight's terminal module,
exactly as `terminal::children_of` flies production children. Pilots run on NEW streams that are disjoint
from the production children's: purpose codes 8, 9 and 10 in the `0xF000 | purpose` space, row = filter
particle index, child = pilot index. Score each pilot under every configured option. For each arm, the
unbiased estimate is

    ĝ_u^a = (1/L) Σ_l exp(q_ul) · L_a(pilot_ul),

where q_ul is the pilot's own ln(prior/proposal) correction. Two refinements are allowed, because ANY
non-negative g that does not depend on the production children leaves the target exact:
- **Smoothing.** g̃_u^a = the mean of ĝ_v^a over the k nearest distinct particles v in a parent-feature
  space: predicted time of the second flame-out, altitude, Mach, track, BFO bias mean, and the 00:19:29 BTO
  residual of a straight continuation. This shares pilot hits between neighbours when hits are rare.
- **Arm mixture.** g_u = Σ_a α_a g̃_u^a / mean_v(g̃_v^a). Each arm is normalised by its own mean, so each
  targeted arm gets share α_a of the proposal and no arm is starved.

**Step C — row draw and correction (existing code).** Candidate c of particle u(c) gets g_c = g_u(c). Rows are
drawn with `lookahead_plan` (stream 5150+k):

    q_c = ((1 − ε) g_c + ε) / (M Z),    Z = (1/M) Σ_c ((1 − ε) g_c + ε),
    log_correction_c = ln Z − ln((1 − ε) g_c + ε).

Every consumer multiplies the row weight by exp(log_correction), as it does for run I's hand-offs today
(`handoff::read_corrected`).

**Exactness.** Conditional on the candidates and on g, E_q[exp(log_correction) f] = (1/M) Σ_c f(x_c) for any f.
That is the uniform mean over the candidates, which is the hand-off without any look-ahead. The production
children are drawn on streams independent of the pilots, so the 00:19 likelihood is applied once, in the
final weights. g only changes the variance. The defensive term ε keeps every candidate in the support, so
arms that are not targeted (`none`, `r600_no-offset`) stay estimable. Their ESS falls by at most a factor of
about 1/ε.

**Within-parent weights.** These are unchanged (self-normalised by default). Request 20 acts between parents,
and request 9 is not needed.

## 4. Predicted gain in effective parents

**The ceiling.** No hand-off proposal can create parents that the filter population does not hold. The
attainable effective parents are at most the ESS of ℓ_a over the D distinct filter particles of each mode,
rather than over 100,000 uniformly drawn rows. The ceiling ratio is therefore about D / rows per mode. This
is Searched Areas' point (iii), now made precise.

- In run I, N_mode = 0.25–1.25M (repro, descent-climb) and 1–2.5M (free, waypoints), with rows = 100,000 per
  mode. If D ≈ N_mode, the ceiling is ×2.5–×25. D is lower than N_mode, because the hand-off is drawn after
  the m0011 resample. D was not recorded in run I.
- **Prediction, per seed, per stratum:** the realised gain is about 0.8 (the defensive term) × D/rows ×
  pilot efficiency (0.3–0.7).
  - **Both raw: 38.8 → about 60–390 effective parents, central about 150.**
  - **Both with the transient bias: 170 → about 250–1,700, central about 700.**
- **The 1,000-effective-impacts target is probably NOT reachable for both-raw by a hand-off proposal
  alone.** If the smoke confirms that, the escalation is §6. It is likely reachable for `both_inflated` and
  for the bias-added arm.

## 5. Phase 1 smoke (deskstar, under the deskstar heavy lock, about 1 h, no new draw in any existing stream)

The `g_files` hook (request 10 hook 5) already draws rows from a per-candidate g file, with the same stream
and the same correction. So the smoke runs in two passes, without the in-process pilot code:

1. **Pass 1.** One stratum (repro-radar: the fastest, 48 min for 8 × 3.5M), 2 seeds, production particle
   count per seed, hand-off at m0011 only (the m2241 look-ahead off; the filter path is unchanged, because
   hand-offs are output-only). Write the m0011 candidate list per mode in draw order, with the filter
   particle index.
   - This needs one output-only addition: `[output] handoff_dump_candidates = true`. It makes no draw and is
     gated by B and C.
   - Size: with smoke rows 10,000 and oversample 50, 500,000 candidates per mode, about 170 MB per mode
     per seed in f64.
2. **Pilots.** End of flight's `mh370 terminal` rerun over the distinct candidates, L = 32 pilots, pilot
   streams disjoint from production. Cost at 1,179 µs per descent: about 0.6M distinct × 32 × 1.3 ms ≈
   7 CPU-h, about 5 min at 88 threads per seed.
3. **Pass 2.** Same seeds and config with `g_files = { m0011 = ".../g-{seed}-{mode}.npy" }`. Then end of
   flight's standard scoring, 32 children per row.
4. **Report**, per stratum per seed:
   - effective parents and effective impacts for `both/no-offset` and `both/startup-offset`, before and
     after;
   - D, and the ESS of ĝ over the distinct particles (the ceiling);
   - pilot hit counts;
   - the same with and without the smoothing (computed offline from the pass-1 pool, because the
     target is exact for any g).
5. **Prior recovery** (the order's standard). Likelihood off and aimed latents uniform on their support: the
   corrected hand-off reproduces the uncorrected candidate-pool means of latitude, longitude, altitude,
   Mach, fuel and bias to a maximum standardised deviation of 0.0030. A unit test of `lookahead_plan` with an
   arbitrary g completes this.

**Stop condition (from the order).** If pass 2 does not raise the effective parents, the hand-off constraint
cannot be addressed by a proposal. That is a finding, and it will be reported as one.

## 6. If the ceiling is too low: escalation, not part of Phase 1

To go past D, the hand-off must hold NEW distinct parents in the feasible region. The exact tool is a
pseudo-marginal resample-move step at m0011 that targets π(x) ℓ_mix(x):
- re-fly the 23:15 → 00:11 segment from each particle's ancestor with refreshed manoeuvre latents (the
  machinery of `rejuvenate_epochs`, steps 9100/9200/9500+);
- accept with the cruise-likelihood ratio times ĝ(new)/ĝ(old), with ĝ an unbiased pilot estimate (Andrieu
  and Roberts 2009);
- correct back to π by 1/ℓ_mix for the untargeted arms, with the tilt's normaliser estimated by the pool mean
  of ĝ.

This changes the filter's particle population after 00:11 only through a new tag. It needs L chosen so that
the sd of ln ĝ is about 1–1.7 (Doucet et al. 2015). Its cost is pilots × moves, so it is a Phase 2b design
for Pete to rule on.

## 7. Code needed for production (Phase 2, on GO)

- `[output.handoff_lookahead] g_source = "terminal-pilot"`, with keys `pilots`, `neighbours`,
  `arm_weights`, and `dump_candidates` (output only).
- In `filter.rs`, at the m0011 slot, call `terminal::Stage::pilot(...)` on the distinct candidates before
  `lookahead_draw`. New streams only: purposes 8–10. No existing tag is touched.
- Gates B and C byte-identical with the feature off. A unit test of the exact correction with an arbitrary
  g. The prior-recovery smoke above.
- The pilots use end of flight's current module. A later module change leaves the target exact, because g
  is only a proposal.
