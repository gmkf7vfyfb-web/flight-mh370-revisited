# Run D (core): look-ahead hand-offs at 22:41 and 00:11

- **Job** 53d0d251 on deskstar, build abd15b6, 11 Oct 2026, 03:55-06:02 UTC; all four strata exit 0.
- **Stack**: run C exactly (driver COMMON + fuel-fixes s7-single-engine + s8-hold-taper + inop-flow-fix:
  internal-v1 with `inop_flow_scale = 0.5`, two tanks, Inmarsat ephemeris, radar in the likelihood)
  plus `config/sensitivity/handoff-lookahead-d.toml` (look-ahead at m2241 with horizon m0011 and at m0011
  with horizon m0019b, oversample 50, defensive 0.2). 100,000 hand-off rows per seed.
- **Strata**: next-d-free (7M particles per seed), next-d-repro-radar, next-d-routes, next-d-descent-climb
  (3.5M each); seeds 1-4.

## How to read the hand-offs

- `handoff-m2241/` and `handoff-m0011/` in each seed. **Look-ahead rows: multiply each row's weight by
  exp(log_correction)** (column 14 of handoff.npy; the `[lookahead]` block of handoff.toml states the rule).
  In Rust use `handoff::read_corrected`; `handoff::read` refuses these files.
- `[stop]` carries (core request 18) per-mode log-evidence, mode probabilities and replicate log-evidence
  **to that epoch only**, and the satcom observations used and not used. A composer must take evidence from
  here, not from the final mode probabilities. The same values are in run.json `replicates[].handoffs`.
- handoff.toml is gzipped (`handoff.toml.gz`); tanks.npy is `tanks32.npy` (float32; the three time columns
  are seconds after 2014-03-08 00:00:00 UTC). See COMPACT.txt.

## Look-ahead effect (Davey dynamics + radar, from run.json)

| Hand-off | ESS fraction, uniform rows | ESS fraction, look-ahead rows | Candidates with g > 0 |
|---|---|---|---|
| m2241 | 0.0016-0.0048 | 0.801-0.803 | 1.0 % |
| m0011 | 0.34-0.77 | 0.88-0.98 | 100 % |

## First results (canonical split-half: mean over all balanced partitions; 4-seed floor 0.896)

| Stratum | Split-half (range) | Median 00:19 | P(family), equal priors |
|---|---|---|---|
| Davey dynamics + radar | 0.882 (0.869-0.908), not converged | -36.48 | 0.235 |
| free | 0.889 (0.857-0.919), not converged | -36.95 | 0.594 |
| routes | 0.941 (0.934-0.953), above floor **but see caveat** | -37.22 | 0.019 |
| descent-climb | 0.837 (0.821-0.865), not converged | -37.18 | 0.153 |

Mixture medians: -37.01 at 00:19, -36.18 at 00:11 (run C: -36.97 / -36.13).
**Routes caveat:** none of seeds 1-4 found route 8 (VAMPI-MEKAR-NILAM-ANOKO, open-ended), which run C seed 7
found with +1.1 nats; routes agreement here is agreement on an incomplete exploration, not convergence.
