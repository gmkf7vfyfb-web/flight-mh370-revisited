# End of flight: how many effective parents could any terminal-stage proposal reach? (brief section 8)

9 October 2026. **SMOKE SCALE, PROVISIONAL.** Seeds 1 and 2, N = 4 children per parent, 20,000 parents per
seed (the `reference-snapshots` hand-off at 00:11, 295.66° prior; superseded if core re-runs). Code
`87509d9` (requests 3b/5 adopted, section 6 log-on likelihood). Script
`engine/hypotheses/end-of-flight/smoke/ess_limit.py`; JSONs in this directory.

## What is measured

A parent j contributes π_j L̄_j to the posterior: its hand-off weight times the mean likelihood of its
descents. The effective number of parents is (Σ π L̄)² / Σ (π L̄)². With finite N the estimate L̂_j is
noisy, and that noise inflates the denominator. Splitting each parent's children into independent halves A
and B gives E[L̂_A L̂_B] = L̄², so

    ESS_inf = (Σ π L̂)² / Σ π² L̂_A L̂_B

estimates the limit with the Monte Carlo part removed. **This limit is a property of the posterior over
the hand-off parents, not of the proposal.** A targeted proposal can at best move the observed value up to
it. If the limit is below the target, only more parents can close the gap.

## Result

| log-on cause | option | effective parents observed, seed 1 / 2 | N→∞ limit, seed 1 / 2 | top-100-parent share | reading |
|---|---|---|---|---|---|
| other | none | 20,000 / 19,999 | 20,000 / 19,999 | 0.01 / 0.01 | resolved at N=4 |
| other | r600/inflated | 13,454 / 13,615 | 15,281 / 15,435 | 0.02 / 0.02 | resolved at N=4 |
| other | r600/no-offset | 3,650 / 4,262 | 7,439 / 8,189 | 0.08 / 0.07 | resolved at N=4 |
| other | r600/startup-offset | 2,401 / 2,688 | 4,371 / 4,801 | 0.10 / 0.09 | resolved at N=4 |
| other | r1200/inflated | 486 / 555 | 1,605 / 1,560 | 0.32 / 0.31 | limit >= 1,000: Monte Carlo, proposal can help |
| other | r1200/no-offset | 111 / 95 | 862 / 885 | 0.88 / 0.90 | limit < 1,000: posterior concentration |
| other | r1200/startup-offset | 151 / 160 | 726 / 1,029 | 0.65 / 0.64 | straddles 1,000 |
| other | both/inflated | 83 / 98 | 1,733 / 255 | 0.79 / 0.68 | straddles 1,000 |
| other | both/no-offset | 4 / 3 | unresolved / 747 | 1.00 / 1.00 | not assessed at N=4 |
| other | both/startup-offset | 7 / 7 | unresolved / unresolved | 1.00 / 1.00 | not assessed at N=4 |
| fuel-exhaustion | none | 4,754 / 5,623 | 5,901 / 6,834 | 0.06 / 0.04 | resolved at N=4 |
| fuel-exhaustion | r600/inflated | 3,083 / 4,110 | 4,131 / 5,378 | 0.09 / 0.06 | resolved at N=4 |
| fuel-exhaustion | r600/no-offset | 1,219 / 2,020 | 2,677 / 3,986 | 0.18 / 0.12 | resolved at N=4 |
| fuel-exhaustion | r600/startup-offset | 932 / 1,275 | 1,665 / 2,323 | 0.22 / 0.19 | limit >= 1,000: Monte Carlo, proposal can help |
| fuel-exhaustion | r1200/inflated | 151 / 207 | 389 / 508 | 0.66 / 0.54 | limit < 1,000: posterior concentration |
| fuel-exhaustion | r1200/no-offset | 38 / 36 | 305 / 578 | 1.00 / 0.99 | limit < 1,000: posterior concentration |
| fuel-exhaustion | r1200/startup-offset | 36 / 51 | 293 / 732 | 1.00 / 0.99 | limit < 1,000: posterior concentration |
| fuel-exhaustion | both/inflated | 35 / 54 | 262 / 435 | 0.86 / 0.78 | limit < 1,000: posterior concentration |
| fuel-exhaustion | both/no-offset | 2 / 1 | unresolved / 22,609 | 1.00 / 1.00 | not assessed at N=4 |
| fuel-exhaustion | both/startup-offset | 4 / 2 | unresolved / unresolved | 1.00 / 1.00 | not assessed at N=4 |

"Resolved at N = 4" means at least 1,000 effective parents are already observed in both seeds.

## Reading

1. **R600, every BFO interpretation: no proposal is needed.** It is resolved at N = 4 in both seeds under
   either log-on cause, apart from r600/startup-offset with log-on = fuel exhaustion. That case observes
   932 / 1,275 against a limit of 1,665 / 2,323, so N = 16 will very likely clear 1,000 on its own.
2. **R1200 with the log-on taken as fuel exhaustion: the shortfall is posterior concentration.** The
   limit is about 290–730 per seed for raw, Holland and inflated alike. **No terminal-stage proposal can
   reach the brief's 1,000 per seed.** The log-on lag and the R1200 BFO together select a narrow set of
   00:11 states.
3. **R1200 with log-on = other:**
   - inflated: limit about 1,600, a Monte Carlo shortfall; a targeted proposal is the remedy;
   - raw (no-offset): limit about 870, which is posterior concentration;
   - Holland (startup-offset): limit 726 / 1,029, straddling the target.
4. **`both`: not assessed at this depth.** With two children per half, the product L̂_A L̂_B is almost
   always zero for the few parents carrying the weight. The estimator's denominator then collapses: values
   of 10¹⁴ to 10¹⁹ and a seed-to-seed spread of 255 against 1,733 for both/inflated. This is an N = 4
   artefact, not a finding.
5. **Caveat on every limit above:** the split-half estimate at N = 4 is itself noisy; seed 1 and seed 2
   differ by up to 2×. The N = 16 run of seed 1 (8 against 8) is queued behind the heavy lock and replaces
   this table when it lands.

## Consequence for the section 8 targeted proposal

- **Build it for the Monte Carlo cases:** r1200/inflated (log-on other) and r600/startup-offset (log-on
  fuel exhaustion). Its acceptance test is that observed effective parents rise to within about 10% of the
  limit.
- **It cannot reach the target for R1200 under fuel exhaustion.** Those cases need more parents per seed.
  That is a core question (hand-off rows per seed), raised in `coordination/architecture.md` of this date.
  An alternative is to rule the target on effective parents pooled across 8 seeds: about 2,300–5,800
  pooled at these limits.
