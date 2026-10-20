import json, pathlib
W = pathlib.Path(__file__).resolve().parents[1]; T = json.load(open(W / "abd/tables.json")); FE = json.load(open(W / "abd/family_ess.json")); A = json.load(open(W / "abd/aggregate.json"))
STR = [("next-d-free", "Free"), ("next-d-repro-radar", "Davey dynamics + radar"), ("next-d-routes", "Routes"), ("next-d-descent-climb", "Descent-climb")]
FN = {"1": "A1", "2": "A2", "4": "A, controlled then lost", "3": "B, ditching approach", "5": "B, control lost en route"}
fe = ["| stratum | family cell | prior (no data) | Held Out | R600 BTO Only | R600 BTO + BFO, inflated |", "|---|---|---|---|---|---|"]
for st, lab in STR:
    for arm, cs in (("A", "124"), ("B", "35")):
        for c in cs:
            g = lambda o: f"{FE[f'{st}|{arm}|{c}|{o}']:.0f}"
            fe.append(f"| {lab} | {FN[c]} | {g('none')} | {g('m0011')} | {g('m0011+r600-bto')} | {g('m0011+r600/inflated')} |")
FE_T = "\n".join(fe)
M = A["mixed"]["stop_evidence"]["options"]; mv = lambda k: f"{M[k]['ln_BF_mean']:+.2f} ± {M[k]['seed_se']:.2f}"
note = f"""# End of flight, 22:41 A-against-B on core run D — STAND-IN replay (architecture, 11 Oct 2026, 07:45–10:56 UTC)

**UNCONVERGED.** Core run D is not converged (split-half below the 4-seed floor in three strata; routes above it only on an incomplete
exploration — route 8 not found). **End-of-flight physics PROVISIONAL**: no structural limit (G13), push-over and the Boeing system sequence
not yet in (plan accepted 5e8f13ea, not built). **Rapid descents above 6,500 ft/min and unloading not reachable by the model.** Family
shares within each arm are mostly prior. Run by architecture as a stand-in for the end-of-flight module (ruling 5e8f13ea item 1),
replaying the module's own recipe; **for the module's review.**

![A against B]({{{{figure}}}})

Figure: `eof-a-vs-b-2241-run-d-standin.png` (this folder). Data: `eof-a-vs-b-2241-run-d-standin/` (aggregate, per-seed JSON, stand-in scripts).

## 1. What was run

- **Recipe:** end of flight's `full/sweep_2241_ab.sh` (22:41 hand-off; arms A = `smoke/arm-v1.toml`, B = `full/arm-b-deliberate.toml`; common
  `snapshot-m2241`, `terminal`, `options-m2241`, `children-4`; module overlays `descent-idle-floor`, `v2-broad`, `family-b-ditching`,
  `residual-bank-boeing`; `full/seed-k.toml`). Configs read from the module's workspace at its head ec1e8bf; sha256 of the arm and option
  files equal to the commit, mtimes before the run.
- **Only the input changed:** core run D (`mh370-exchange/core/next-run-d/`, build abd15b6), m2241 look-ahead hand-offs, 4 strata × seeds
  1–4, 100,000 rows × 4 children × 4 descents per arm. Each hand-off's sha256 checked against core's COMPACT.txt (16/16 match).
- **Binary:** the run C binary `/tmp/mh370-eof-runc5` (code 097a5d77), copied. **No rebuild was needed**: its terminal stage already reads
  hand-offs with `handoff::read_corrected` (weight × exp(log_correction); in since core 826f731), and it reads run D's request-18 `[stop]`
  fields (optional). The module's physics files at ec1e8bf differ from 9da3258 by one comment line; the binary records revision 097a5d77, the module's merge used for all of run C.
- **Reproduction check (passed):** run C descent-climb seed 1 re-run with this setup reproduces the module's own numbers exactly
  (00:11: ln Z A −16.455, B −17.174, ln BF +0.72; +R600 inflated: −28.034 / −29.148, ln BF +1.11).
- **Compute:** outside the heavy lock at RAYON_NUM_THREADS = 8 (ruling); 2–7 min per arm at Mac load 16–35; 3 h 11 min in total.
- **Evidence:** the module's `smoke/ab_evidence.py`, unchanged, per stratum-seed. Stand-in companion `standin_ab_summary.py` adds three
  things from the same impacts: R600 BTO Only, the `~v212` version and family shares (section 6, deviations 2–4).

## 2. Result: ln BF (A against B), seed mean ± seed s.e., N = 4 seeds

Positive = favours A (cruise to fuel exhaustion, then A1/A2). Bold = passes the module's gate (≥ 30 effective parents per seed in both
arms) and seed agreement (stand-in definition: seed s.e. ≤ 0.25 nat). n.e. = not estimable (minimum effective parents A/B shown).
Every option includes the 23:15 BFO and the 00:11 BTO + BFO, scored in-stage. Mixture ([stop] evidence) = equal stratum priors × the
evidence to 22:41 from each hand-off's `[stop]` block (core request 18), per seed index. Mixture (README P) = run D's final P(family)
(0.594 / 0.235 / 0.019 / 0.153) as fixed weights, a sensitivity only.

{T['T1']}

**Reading.**
1. **Held Out:** ln BF {mv('m0011')} (mixture), {mv('m0011~v212')} with impacts above 212 m/s removed. Positive in all 16 stratum-seeds (+0.20 to +1.16; ~v212 +0.01 to +0.99).
   On the usual scales (Jeffreys; Kass and Raftery) this is weak evidence for A: a Bayes factor of about 1.7, "not worth more than a bare mention".
2. **R600 BTO Only:** {mv('m0011+r600-bto')} ({mv('m0011+r600-bto~v212')} ~v212). The 00:19:29 BTO adds about +0.45 nat for A.
3. **R600 BTO + Raw BFO: not estimable** (B has 6–11 effective parents per seed). Its means (+1.3 to +1.7) are not evidence.
   With inflated BFO noise (34 Hz) the row is estimable: {mv('m0011+r600/inflated')}.
4. **H1/H2 (both 00:19 bursts, R1200 BFO): not estimable** — 1–9 effective parents in both arms, all three BFO models. Coverage gap G-f.
5. **What drives it:** the BFOs. 23:15 + 00:11 BFOs alone give {mv('m0011-bfo')}, the 23:15 BFO alone {mv('m2315-bfo')}, the 00:11 BTO alone
   {mv('m0011-bto')}. The parts are not additive.
6. **Speed cap:** removing impacts above 212 m/s lowers ln BF by 0.13–0.18 nat (Held Out and R600 BTO Only), because about 20 % of A's posterior weight (Held Out)
   against 4–5 % of B's is above 1.25 VMO. The sign does not change.
7. **Strata agree in sign;** routes gives the largest A preference (+0.94 Held Out), Davey dynamics + radar the smallest (+0.32). The mixture
   is dominated by free (0.57–0.61) and Davey dynamics + radar (0.32–0.36) at 22:41.

## 3. Comparison with the module's run C (descent-climb seeds 1–4)

{T['T4']}

**Reproduction direction: same sign and size.** Run D descent-climb Held Out +0.69 ± 0.17 against run C +0.66 ± 0.15 (the +0.72 quoted
in the brief is run C seed 1 only; the 4-seed mean is +0.66). Run C's R600 BTO Only cannot be compared: its impacts were slimmed without the
BTO residual column.

## 4. Effective sample sizes, posterior medians, speed-cap removal (per arm; minimum over the 4 seeds)

{T['T2']}

Posterior shapes need ≥ 1,000 effective impacts (module rule). **B's impact medians are not estimable as shapes** (eff. impacts 142–770); A's
Held Out medians are estimable in every stratum (1,037–2,736 effective impacts); A's R600 BTO Only medians only in routes and descent-climb. B's impacts lie about 1.5–2.3° north of A's (provisional).

**Look-ahead and this stage.** The corrected hand-off weights have an ESS of about 20,200 of 100,000 rows in every stratum-seed (20 %; core's
README quotes 0.80 for "look-ahead rows" — a different denominator, for core to confirm). After 23:15 + 00:11 are scored in-stage, run D gives
205–593 effective parents per arm (minimum over seeds), which is **not more** than run C descent-climb with uniform rows (877 / 2,058 at seed 1).
Repeated filter particles do not inflate these counts: effective distinct particles are ≥ 98 % of effective parents.

{T['T5']}

## 5. Family shares within each arm (mean over seeds) and effective parents per family cell (minimum over seeds)

{T['T3']}

{FE_T}

**Family shares are mostly prior.** Within A the data move A1/A2/A-then-lost by ≤ 0.04. Within B the data favour the ditching approach
over control lost en route (0.50 → 0.56–0.64). These shares are not an A-against-B test; the Bayes factors in section 2 are.

## COVERAGE

**(a) Feasible set (the 777-200ER from 22:41).** Cruise to fuel exhaustion followed by any end state (uncontrolled spiral dive, glide,
controlled ditching, controlled then lost — A1, A2, A-lost); a deliberate descent begun at any time before exhaustion, including before
22:41, at any rate within the aircraft's limits (beyond 6,500 ft/min to the dive limits; unloading and push-over to the structural limits),
with an approach to ditching or lost en route (B, B-lost); powered or unpowered. Sources: the module's feasible-set notes
(`eof-rapid-descent-oct10`, `eof-same-data-bf-oct10` COVERAGE).

**(b) Model reach (this recipe).** A: onset only at flame-out (`arm-v1`: anticipatory support [0, 0], mechanism weights [0, 0, 1]), so no
descent before exhaustion. B: anticipatory onset with lead U[0, 5,760 s] before predicted exhaustion, or fuel cue (`arm-b-deliberate`
[1, 1, 0]); control 0.5 ditching approach / 0.5 maintained-then-lost (`family-b-ditching`, ruled 15:45 −0600). Commanded descent rates
capped at 6,500 ft/min; free flight cannot unload; no push-over; no Boeing system sequence; no structural speed limit.

**(c) Proposal coverage.** One proposal (the module's) for both arms; ESS per option and arm in section 4, per family cell in section 5.
No declared regions in this test (impact positions not retained after the disk cut, deviation 3).

**Gaps and status.**

| gap | kind | status in this note |
|---|---|---|
| G-a rapid descents above 6,500 ft/min | reach | OPEN; in every label. Module switch exists (default off), not in the recipe |
| G-b unloading / push-over (0.6 g) | reach | OPEN; push-over plan item 4 accepted 5e8f13ea, not built |
| G-c Boeing system sequence on the point mass | reach | OPEN; plan item 2 |
| G13 no structural limit (impacts above 212 m/s) | reach (over-reach) | DECLARED; `~v212` version beside every row |
| G-d B onset before 22:41 | reach | DECLARED CONDITIONAL: B begins after the 22:41 hand-off in this test; earlier altitude changes only via core's descent-climb stratum |
| G-e A cannot descend before exhaustion; outside-B prior 0.002 | definition | by ruling (90ee3eb5, 15:45 −0600) |
| G-f both 00:19 bursts (H1/H2) | proposal | OPEN, not estimable (1–9 eff. parents). Fix: within-parent targeted sampler (core request 9) after items 2/4 and Pete's go |
| G-g R600 Raw BFO and start-up-offset rows in B | proposal | OPEN, not estimable (2–11 eff. parents in B). Fix proposed: more descents per parent in B, or a descent-rate proposal aimed at 00:19:29 with the proposal correction in the weights |
| G-h core not converged | upstream | OPEN; label on every row |
| G-i B control mix 0.5 / 0.5 | prior | declared sensitivity (module); per-cell shares in section 5 |
| G-j log-on cause | model | only cause `other` (as the module's 22:41 recipe); fuel-exhaustion lag not scored here |

**Parameter bounds with sources.** Anticipatory lead [0, 96 min] (module, `arm-b-deliberate.toml`; it spans the 22:41 hand-off to the
predicted exhaustion about 99.5 min later, so it is set by the hand-off, not by physics — see G-d); descent idle floor, ICAO EEDB Trent 892
(module, `descent-idle-floor.toml`); broadened descent envelope (`v2-broad.toml`, PROVISIONAL-OVERNIGHT); residual bank P(left) = 0.8
(Boeing, PROVISIONAL); 212 m/s = 1.25 VMO (ruling 1(C), 20:35 −0600 10 Oct); commanded rate cap 6,500 ft/min — **unsourced as a feasible
bound; it is a reach gap (G-a)**.

## 6. Deviations (stand-in, for the module to review)

1. **No rebuild.** The brief allowed a build from the module branch merged with core; the run C binary already reads corrected rows, so it was
   used unchanged, which keeps physics identical to run C. Verified by the exact run C reproduction.
2. **R600 BTO Only is derived, not scored in-stage.** `options-m2241.toml` has no such option. It is `loglik:m0011` plus the core's Gaussian
   BTO term at m0019a, computed with the module's own `derived_logliks` (`smoke/displacement_hist.py`, imported read-only; sd from
   `data/satcom-observations.csv`). The module checked on 9 Oct that `r600/no-offset` decomposes exactly into this BTO term plus a BFO term.
3. **Disk.** The module's `slim.npz` (192 MB per arm) was replaced by a stand-in `mini.npz` (log-weight, parent, contact speed, family code,
   four option log-likelihoods; ≈ 46 MB per arm), and `impacts.npy` deleted after each seed's JSON was written. **Impact positions were not
   retained**: maps or region ESS need a re-run (about 3 h). Total new data 1.4 GB.
4. **Seed agreement** for 4 seeds was defined by the stand-in as seed s.e. ≤ 0.25 nat (the module's 2-seed rule was agreement to ≤ 0.21).
5. **`~v212`** follows Pléiades' `branch_eof289.py`: rows with |v| > 212 m/s removed, normalised by the unfiltered total, so ln Z includes the
   feasibility conditioning.
6. Peak memory was not measured (the sandbox refuses `/usr/bin/time -l`); no run failed.
7. Run C comparison uses the module's own per-seed JSON for seeds 1–4; only seed 1 was re-run.

## 7. For the module

- Review sections 2–6 and the stand-in scripts in `eof-a-vs-b-2241-run-d-standin/`; adopt, correct or supersede.
- The gap that blocks the Raw-BFO and H1/H2 rows is proposal coverage in B and two-burst coverage (G-f, G-g), not the hand-off ESS.

- Modular Architecture (stand-in for end of flight)
"""
open(W / "standin/eof-a-vs-b-2241-run-d-standin.md", "w").write(note); print(len(note))
