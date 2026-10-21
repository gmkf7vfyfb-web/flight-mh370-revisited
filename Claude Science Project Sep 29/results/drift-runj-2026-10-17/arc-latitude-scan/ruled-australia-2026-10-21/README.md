# Pete's 17 Oct Australian scheme at the arc-latitude points, offline: STOPPED at the validation gate (21 Oct 2026)

Ocean drift module, 21 Oct 2026, for coordination (Pete, ~01:00Z): no transport, Mac only. The scheme: ABS tiers major city +
inner regional 1, outer regional 0.3, remote/very remote 0, times a 2014 level of 0.3 / 0.5 / 0.65 relative to the find-coast
peak, constant in time. The inputs are the stored node tables of the dedicated run (15ab7c9, 26-40 S) and of the north
extension (181a5fa, 20-26 S), 84 points in each of the two ocean models.

## Verdict
**The gate FAILS.** The stored columns cannot give the module's own value. The best offline emulator reproduces the measured
option B, option C and populated columns to an RMS of 0.07-0.27 ln and a maximum of 0.36-1.32 ln (leave-one-out). This is
larger than the Monte Carlo noise of the measured scheme-minus-off differences (median split-half SD 0.03-0.07). No
validated column for the ruled scheme is delivered, and nothing here should be used for the sea-floor chart without a decision.

## What is missing from the stored tables
For every node, environment realisation and class, the module computes (lib.rs `node_ln_likelihood_zeros`, recovery.rs
`coefficients`):
ln L = ln mean over (4 environments x 256 level draws) of sum_c sum_finds [ln(a_cj . nu) - ln(A_c . nu)].
Here A_c is a vector of delay-weighted arrival coefficients per block (16 segments x 3 awareness periods), a_cj are the find
kernels, and nu is log-normal (block mean, SD 1). A new Australian scheme changes only the Australian blocks of nu inside
A_c . nu. That change needs the following, and none of it is stored:
1. A_c per block: the split by period and the 60-day reporting-delay weighting. The table's `p_<class>_<segment>` is the
   arrival fraction before 30 Jun 2016, averaged over environments, with no period split and no delay weighting.
2. A_c and a_cj per environment realisation (the mean over environments sits outside the log).
3. a_cj per find and period (the find-coast term, which the level draws share with A_c . nu).
4. A_c for the split halves (no `p_` half columns), so the split-half noise of any new scheme cannot be formed exactly.

## What was tried (declared reconstruction, NOT a module computation)
`ruled_australia_offline.py` uses an emulator of the module's form (q / q_tot with log-normal Australian levels), calibrated
per node on the measured columns:
Delta(lambda) = ln mean_d prod_c (1 + sum_AU p_cs lambda_s eps_ds / (kappa G_c))^(-n_c)
- G_c is the find-coast arrivals; n = 1 / 6 / 2 finds per class (stringent nine); eps ~ LN(0, 1), one draw per Australian segment.
- k1: one parameter per node (kappa). k2: kappa plus a factor on the outer + remote levels.
- A deterministic version (eps = 1) fits much worse: leave-one-out RMS 0.3-0.7. The log-normal level spread matters, and its
  per-period structure is not in the tables.

**Gate, per node (180 node values = 2 models x 90 rows, including the 26 S repeats; `gate-summary.csv`, `gate-per-node.csv`):**

| emulator, test | populated max / RMS | option B max / RMS | option C max / RMS |
|---|---|---|---|
| k1, leave-one-out | 0.90 / 0.21 | 1.32 / 0.27 | 0.47 / 0.09 |
| k1, in-sample | 0.77 / 0.18 | 0.49 / 0.10 | 0.36 / 0.07 |
| k2, leave-one-out | 3.61 / 0.98 | 1.07 / 0.20 | 0.63 / 0.11 |
| k2, in-sample (2 parameters, 3 values) | 0.03 / 0.004 | 0.27 / 0.05 | 0.47 / 0.09 |

Noise for comparison (median split-half SD):

| measured column | scheme minus off | column itself |
|---|---|---|
| populated | 0.045 | 0.22 |
| option B | 0.070 | 0.22 |
| option C | 0.034 | 0.22 |

Leave-one-out, k1: 64-79 % of nodes are within 2 SD of the scheme-minus-off noise and 86-94 % within 2 SD of the column
noise. So the gate fails at every node; in RMS it passes only against the column's own noise.

**Gate at the posterior level (run J D0', two models; `gate-posterior-leave-one-out.csv`).** Each measured column was
emulated from the other two. Mean-latitude shift error: C -0.05 (k1) / -0.11 (k2) deg; populated -0.29 / +0.28; B +0.35 / +0.25.
The ruled scheme lies between C and B, on the same ray (ruled level rho is about rho x option B with remote removed).
So its error is probably nearer the C case, about 0.1-0.2 deg, but removing the remote tier is never measured.

**Provisional reconstructed values (NOT validated; `arclat-ruled-australia-posterior-RECONSTRUCTED.csv`,
profile `arclat-ruled-australia-RECONSTRUCTED-gate-failed.csv` with split-half SD):**

| level | shift k1 | split-half diff | shift k2 | median | share N of 33 S |
|---|---|---|---|---|---|
| 0.3 | +2.77 deg | 0.08 | +2.79 deg | -35.15 | 27.6 % |
| 0.5 | +3.51 deg | 0.11 | +3.54 deg | -34.75 | 36.0 % |
| 0.65 | +3.99 deg | 0.13 | +4.01 deg | -34.41 | 41.5 % |

Per model at 0.5 (k1): GlobCurrent +3.23, GLORYS12 +3.82.

Measured, for reference: finds only +1.00, C +3.27, populated only +3.36, B +5.44.

The 17 Oct values (+2.84 / +3.83 / +4.42) came from the saturating law on the run A surface, so they are not comparable
method-for-method.

**Consequence for decision table v2 (provisional).** On the arc-latitude columns, the populated-only column (+3.36) does not
overstate the ruled scheme at 0.5. The reconstruction gives +3.51, a difference of about 0.15 deg, which is within the
reconstruction error. The stated "up to about 0.6 deg" came from the two saturating-law values (+4.44 against +3.83).

## Options to make it exact (each needs transport, which Pete excluded for now)
1. Add the three ruled levels as level alternatives in the arc-latitude configs, with no code change, and re-run the
   84 points in both models: about 15.2 h on deskstar (13.6 h on 18 Oct + 1.6 h on 20 Oct).
2. Preferred for the long term: inside `hypotheses/debris-drift/`, write per-node coefficient sidecars (A_c and a_cj per
   environment, class and block, full and split halves; about 50-250 kB per node with the extra bandwidths). Any future level scheme then becomes an
   offline rescoring (brief rule 12). This needs the same one re-run.
3. Use the reconstruction above as a labelled sensitivity, with its validation error stated.
