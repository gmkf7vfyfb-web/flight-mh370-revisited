# End-to-end calibration of the composed estimator — pre-registered protocol

**Status: PRE-REGISTERED, 19 Oct 2026, before any case runs.** Written by the composer / architecture role under overnight
work order E (`threads/work-orders/overnight-2026-10-19.md`, Pete approved about 04:00Z). It answers
`results/project-assessment-2026-10-18.md` §4 gap 2 and §6 item 2, and follows the composer thread's three-tier design (tier 1a
strict simulation-based calibration, 1b coverage by latitude band, tier 2 wrong-model stress tests, tier 3 real known-truth links).

**What may change after this commit.** The 5-case smoke (§9) may change the *implementation* (§4–§5: file plumbing, particle counts,
thread counts, bug fixes) and the *scale* (§8). It may NOT change the tiers, the truths' prior, the statistics (§6), the sample sizes
(§7), the pass criteria or the failure actions (§10). Any change of any kind is entered in the amendment log (§12) with its date and
reason BEFORE the full run starts. Smoke cases (seeds 9001–9005) never enter the tier 1a or 1b samples.

**The full run does not start until Pete has reviewed the smoke** (work order E item 3).

---

## 1. Purpose

Rule 8 of the composition rules gives each module a synthetic-recovery test. Nothing yet tests the composed chain
core → end of flight → impact-level factors → composer. This protocol tests whether the composed posterior's stated uncertainty is
correct: whether its 50 / 90 / 95 % regions contain the truth at those rates, and whether its discrete probabilities (route family,
end-of-flight family, 00:19 cause) are reliable. Tier 1 checks the computation (same model generates and infers); tier 2 checks
robustness to known kinds of model error (the "false precision" charge of the 18 September review); tier 3 checks against real
cases with a known answer.

## 2. Tiers

| tier | name | truth drawn from | what a pass shows | cases |
|---|---|---|---|---|
| 1a | strict simulation-based calibration (SBC) | the inference prior, exactly (§3) | the sampler, hand-offs, corrections, factor bookkeeping and composer are computed correctly | 100 |
| 1b | coverage by latitude band | the inference prior conditioned on the impact latitude band (rejection on the drawn truth) | the arc-wide sample set gives honest regions in each band, including the north | 40 = 10 per band × 4 bands |
| 2 | wrong-model stress | a stated departure from the inference model (§3.4) | how much coverage is lost under each named model error | 6 stresses × 20 = 120 (separate approval) |
| 3 | real known-truth links | real data with a known answer (§3.5) | the real-data likelihoods are not mis-specified where an answer is known | as available (separate approval) |

Tier 1b bands (impact latitude): 40–35 S, 35–30 S, 30–25 S, 25–20 S. Bayesian regions are calibrated on average over the prior,
not conditionally on a band, so tier 1b is diagnostic (§10): a low-prior band is expected to under-cover somewhat because the prior
pulls toward the mode. Tier 1b uses tier 1a's statistics and also records the coverage that the model itself predicts for the band
(the mean, over the band's cases, of the posterior mass inside the band), so that under-coverage caused by sampling can be told
apart from prior pull.

## 3. Truth generation (tier 1)

Every truth is one joint draw of all latent quantities, from the same prior and the same model code that the inference uses.

### 3.1 Flight to 00:11 (core)
- Prior: the run J production chain for the route family (`config/sensitivity/run-j/README.md`): 18:01 radar prior (radar-full),
  route family, autopilot mode, Mach / altitude / manoeuvre clocks (Jeffreys τ), turns, speed and altitude changes, fuel model with
  fuel-fixes s1–s8, κ_x ~ N(1.0, 0.046), BFO bias prior per `[bfo_bias]`, BFO bias drift as configured (OFF in run J).
- Route family drawn from its prior share. The fuel record ("powered at every logged burst to 00:11") is DATA, not prior; the truth
  is therefore drawn from p(θ | fuel record), which the engine provides as the fuel-only case (`use_bto = false`, `use_bfo = false`).
- Truth = one weighted draw from that run's 00:11 hand-off rows (weight × exp(log_correction)), with its full state trace.

### 3.2 End of flight (00:11 to impact)
- The truth's 00:11 state is continued by the end-of-flight module with the production recipe (round-3 laws, bank limit
  U[52, 90] deg, dive branch, C2-silent aim, the production overlay list of `results/eof-run-j-waypoints-oct16/README.md`).
  Family (A1, A2, B) and every latent come from the module prior; aimed proposals are undone by their weights.
- The 00:19 log-on time is data: the log-on happened at 00:19:29 (R600) and 00:19:37 (R1200). The truth's descent is drawn with
  probability proportional to its prior weight times the log-on-time likelihood under the cause mixture (C1 fuel exhaustion + APU,
  Erlang lag; C2 other, rate q/W, q = 1/3, W = 00:10:58–01:15:56) and the survival factor. The true cause (C1 or C2) is then drawn
  from its conditional probability for that descent.
- The 00:19 BFO measurement model is drawn from its prior: no offset, start-up offset (Holland; R1200 17–130 Hz, R600 0–6 Hz above
  it), inflated (34 Hz), each 1/3.

### 3.3 Synthetic data
- **BTO / BFO at every logged handshake** that the production observation table carries (`data/variants/satcom-observations-bfo432.csv`
  epochs; R1825 held out as in run J): predicted value for the truth's state at the burst time (the satcom crate's equations;
  `report/satcom_model.py` is the checked Python copy) + the truth's bias (+ drift if on) + Gaussian noise with the table's SD
  (BTO per message; BFO 4.3177 Hz). The 00:19 bursts get the truth's 00:19 state and the drawn 00:19 BFO model.
- **00:19 per data option:** one synthetic 00:19 data set per case; D0 (held out), D1 (R600 BTO), D2 (+ R600 BFO), D3 (+ both
  BFOs as recorded), D4 (+ both, Holland transient bias added), D5 (offset on R1200 only) are subsets / treatments of it, exactly as
  for the real data.
- **Debris finds:** forward transport from the truth's impact with the truth's ocean model (GLORYS12 or GlobCurrent, 1/2 each)
  and windage class, through the drift module's own find model; the synthetic find list has the real list's item classes.
- **Seabed search outcome:** the truth's settled seabed position is detected with probability
  1 − [ρ(x) + (1 − ρ(x)) Π_k (1 − c_k(x) q_k(x))] (V1 central field, `results/searched-areas-spatial-detection`). One Bernoulli
  draw. **Detected cases are kept**, and the inference then scores "detected" (not "not detected") for that case. The tier 1
  summary is also reported for the not-detected subset (valid: SBC holds conditionally on any function of the data).
- Hydroacoustics contributes no factor by ruling and is not simulated. Pléiades is conditional on object identity and is not in
  tier 1 (it has its own SBC, `results/pleiades/d5-two-epoch.md`).

### 3.4 Tier 2 stresses (designed now; run only on separate approval)
S1 BFO noise Student-t ν = 4 at the same scale; S2 BFO bias drift at the 18:39 / 23:14 cluster-derived rate, inferred with drift
OFF; S3 the truth's descent from a law outside the module's prior (6-DOF uncontrolled arm, not the parametric pitch-down);
S4 the truth's drift with the other ocean model plus doubled ocean error; S5 true search detection q 0.20 lower than modelled
(the AF447 precedent); S6 a speed / altitude schedule at the edge of the feasible set but outside the prior bounds (coverage gap
probe). For D3 / D4 the matched-model cases are tier 1; the crossed cases (D3 scored on offset truths, D4 on no-offset truths) are
reported as a free tier 2 result.

### 3.5 Tier 3 links (designed now; run only on separate approval)
Core: the MH371 flight (`data/mh371/`) and any other 9M-MRO flight in the Inmarsat record, with the known track as truth. Drift:
GDP drifter replays (`results/ocean-transport-error-*.md`) with the drifter's real release and recovery. Searched areas: the two
19th-century shipwrecks found by the ATSB search as positive controls (register E1).

## 4. Inference per case (same model, same code as production)

1. **Core:** the run J production chain for the family, observation table replaced by the synthetic one; R replicates (seeds).
2. **End of flight:** the production recipe on the case's 00:11 hand-offs; 00:19 two-factor columns D0–D5 × C1 / C2.
3. **Impact factors:** settling (run J recipe) → searched areas (V1 field, the synthetic outcome); drift (the module, synthetic
   find list, both ocean models marginalised jointly).
4. **Composer:** factor stacks **core**; **core + drift**; **core + searches**; **all evidence** (core + drift + searches).
   Australian non-recovery is a labelled sensitivity and is not in "all evidence".
Every stack is computed for each data option D0–D5; results are given per end-of-flight family first, then the mixture.

## 5. Statistics, per case, per factor stack, per data option

Continuous quantities, as normalised ranks u = P_post(Q < Q_truth) (weighted samples; ties split at random):
1. along-arc position at 00:19 (signed distance along the 7th arc from a fixed reference, the arc's crossing of 30 S);
2. impact latitude;
3. impact time;
4. cross-arc distance of the impact (signed, km from the 7th arc).

Regions: whether the truth's impact cell is inside the 50 / 90 / 95 % HPD region on the equal-area grid (0.25° × equal authalic
steps, 769.3 km² cells); and inside the 1-D 50 / 90 / 95 % HPD interval of impact latitude.

Discrete quantities, reliability: route family (four strata), end-of-flight family (A1, A2, B), 00:19 cause (C1, C2). Per case the
posterior probability of the true class; summarised by log score, Brier score and a reliability table (predicted probability in
deciles against observed frequency).

Monte Carlo noise per case: the between-replicate standard deviation of each u, of each HPD indicator's region mass at the truth,
and of each discrete probability, from R replicates (split-half as a check). ESS per replicate after each factor.

Validity rules: D3 is scored only on truths with the no-offset 00:19 model, D4 and D5 only on truths with the start-up-offset
model; D0–D2 on all truths (D2's R600 BFO is valid only for no-offset truths, so D2 too is scored on no-offset truths). A case with
a not-estimable product (ESS below floor) is reported as not estimable and counted, never dropped silently.

## 6. Tests

- **Rank uniformity** (each continuous quantity × stack × data option): χ² on 10 equal bins (df 9), and the ECDF-difference envelope
  (simultaneous 95 %, Säilynoja et al. 2022). Family-wise α = 0.05 over the 16 primary tests (4 quantities × 4 stacks, data
  option D0); per-test α = 0.003125, χ² critical value 24.86. D1–D5 are secondary, at the same per-test α.
- **HPD coverage**, two-sided 99 % binomial acceptance (n = 100): 50 % region 37–63 cases; 90 % region 82–97; 95 % region 89–100.
  (At n = 100 a true 80 % coverage of a stated 90 % region is rejected with probability 0.64.)
- **Reliability:** log score and Brier score against the prior-only forecast; a reliability-table decile whose observed frequency is
  outside its binomial 99 % band is flagged.
- **Shape diagnosis** (reported, not a separate test): ∪-shaped ranks = over-confident (false precision); ∩-shaped =
  over-dispersed; slope = bias, with its sign.

## 7. Sample sizes

- Tier 1a: 100 cases, seeds 1–100 (case seed s fixes every truth draw and every synthetic noise draw; inference seeds are
  1000·s + r for replicate r).
- Tier 1b: 40 cases, seeds 1001–1040, 10 per band in the band order of §2 (truths drawn until 10 per band are accepted; the
  number of rejected draws per band is reported).
- Smoke: seeds 9001–9005; never pooled with the above.
- Tier 2: 20 cases per stress (seeds 2001–2120); tier 3: as available. Each needs its own approval.

## 8. Scale per case (set by the smoke, recorded in §12 before the full run)

Per case the scale must give, for every stack under D0: at least 1,000 effective parents per replicate after composition (the
composer floor), R ≥ 4 replicates, and a between-replicate SD of each rank u of at most 0.05 (so Monte Carlo noise widens the
rank histogram by under 1 %). The smoke measures ESS and that SD at a reduced scale and the full-run scale is the smallest that
meets them; the cost of 100 + 40 cases at that scale is part of the smoke report.

## 9. Smoke (work order E item 2)

5 cases (seeds 9001–9005) at reduced scale on deskstar under the heavy lock, at most 40 threads, disk cap 10 GB. Purpose:
find pipeline faults, measure per-case wall time and Monte Carlo noise, and give the cost of the full run. The smoke's
statistics are NOT a calibration result: five cases cannot test coverage. Every reduction from §3–§5 is declared in its report.

## 10. Pass criteria and what a failure triggers

| result | criterion | action |
|---|---|---|
| tier 1a PASS | every primary rank test passes at its α; all three HPD coverages in their acceptance bands for every stack under D0; no reliability flag for the end-of-flight family | the stack's stated regions may be quoted in the paper as calibrated (same-model) |
| tier 1a FAIL in core | any core-stack test fails | stop the full run; bisect: hand-off weights and log_correction → look-ahead → tempering → strata pooling; nothing from the core is quoted as calibrated until fixed and re-run |
| tier 1a FAIL in a later stack only | core passes, a stack with factor E fails | the fault is in E's likelihood, its column bookkeeping or the composer's joint marginalisation; E's products carry "calibration failed" until fixed |
| tier 1a FAIL in one data option only | D0 passes, D_k fails | the 00:19 model or its proposal for D_k; D_k products carry "calibration failed" |
| tier 1b band flag | 90 % coverage ≤ 6 of 10, or truth outside the 99 % region in ≥ 2 of 10, AND observed coverage below the model-predicted coverage of §2 by more than its binomial 99 % band | sampling gap in that band (proposal coverage): review the arc-wide sample set for that band; every product carries "band X under-covered" |
| tier 2 | coverage of the 90 % region below 0.80 under stress S | report as "not robust to S"; propose the model-error term that restores it; never down-weight a factor by hand (composer §0) |

A failure is a result: it goes in the headline of the calibration note and in the paper, not in an appendix.

## 11. Outputs

`results/e2e-calibration-<date>/`: per-case table (truth, every u, HPD indicators, discrete probabilities, ESS, Monte Carlo SD, wall
time); rank histograms with envelopes per stack and data option; coverage plot (stated against observed, with binomial bands);
reliability diagrams; a README with a COVERAGE section (composer §0 sampling-coverage rule). Charts follow the project's chart rules.

## 12. Amendment log
- 19 Oct 2026, pre-registration (commit 3010631c). No amendments adopted.
- 19 Oct 2026 ~08:10Z, smoke done (`results/e2e-calibration-smoke-2026-10-19/README.md`). **PROPOSED, NOT ADOPTED (Pete decides):**
  A1 tier 1a strictly from the prior for the core stack only, plus tier 1a′ (truths accepted by a data-only event on the 00:11 and 22:41
  BTO/BFO) for every stack; A2 one shared compacted truth pool of ≥ 300,000 single-particle replicates, accepted ESS ≥ 100 per case;
  A3 scale 4 × 3.5 M particles minimum, first 10 cases at 7 M; A4 drift node scan extended to the truths' span, or drift stacks restricted by a
  data-only rule; A5 a 00:19 position prediction column from end of flight for statistic 1. The smoke itself used a data event (BTO(00:11)
  17,540–18,540 µs, BFO(00:11) 202–302 Hz) and the reductions declared in its note; none of that changes this protocol.
- 20 Oct 2026 ~05:15Z, overnight order D (cases 5 and 1 at 4 × 3.5 M). Implementation defect S2 found in the smoke truth generator: the 00:11
  flight was drawn without its marginal 00:19 log-on likelihood Z(parent). **Implementation fix (allowed by §0, recorded here before any full
  run):** fly the end-of-flight stage for all accepted candidate flights and draw (flight, descent) jointly ∝ fuel-only weight × Z(parent) × descent
  weight. A1–A5 remain PROPOSED, NOT ADOPTED; the order D evidence (case 1: two independent 3.5 M sets disagree, map level 0.79 vs 0.97)
  supports A3 at 7 M.
- 20 Oct 2026 ~17:30Z, **PETE'S RULINGS on A1–A5** (given in chat; this entry records them, no run has started):
  **ADOPTED:** A1 (tier 1a strictly from the prior for the core stack; tier 1a′ with the data-only acceptance event on the 00:11 and 22:41
  BTO/BFO for every stack; 1a′ is reported as a conditional calibration, given the event); A2 (one shared compacted truth pool of ≥ 300,000
  single-particle replicates, drawn with the S2 joint (flight, descent) rule, accepted ESS ≥ 100 per case; pool seed and hash in the README);
  A4 (drift stacks scored only on truths inside the existing drift node scan, by a data-only rule written before the run, excluded share
  reported — the node scan is NOT extended); A5 (00:19 position-prediction column from end of flight, statistic 1 scored at 00:19 as well as
  at impact). **HELD, NOT DECIDED:** A3 (scale) — Pete reviews the smoke note and figures first; options on the table are 4 × 7 M throughout
  (≈ 340 lane-h) or 4 × 3.5 M minimum with the first 10 cases at 7 M (≈ 150–190 lane-h). The full run (§7 tier 1a + 1b) waits for A3.
  Before it starts: implement S2 in the truth generator (pick_truth.py still has the old draw; only parent_check.py exists) and re-run
  smoke case 5 (seed 9005) at 4 × 3.5 M as the check that the fix clears the cross-arc miss.
