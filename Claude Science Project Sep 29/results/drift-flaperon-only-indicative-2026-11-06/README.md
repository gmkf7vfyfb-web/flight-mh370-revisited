# Flaperon-only drift term: indicative diagnostic from stored tables (6 Nov 2026)

**Status: indicative. This is not the drift module's likelihood.** No transport was run. Inputs are the stored arc-latitude node
tables (18 and 20 Oct 2026, both ocean models, 84 release points at 20-40 S) and the evidence-ledger arc masses (3 Nov 2026).

## Why a proxy
The module computes ln L = ln mean over (4 ocean environments x 256 level draws) of the sum over finds of [ln(a_j . nu) - ln(A_c . nu)].
The mean over environments is outside the log, and the per-find terms a_j and A_c are not stored. So a one-item term cannot be cut out
of the stored nine-item ln L. The tables do store, per release point, the flaperon-class arrival share on each coast segment before
30 Jun 2016 (segment 0 is Réunion) and the particle count inside the Réunion find kernel. Three proxies bracket the flaperon-only term.

| proxy | what it keeps | what it leaves out |
|---|---|---|
| conditional on recovery | Réunion share of all find-coast arrivals (the module's conditioning) | find date, reporting delay, block levels |
| unconditional (Davey form) | arrival at Réunion, no conditioning | conditioning on recovery (D5) |
| kernel and timing | particles in the Réunion kernel and window, per find-coast mass | block levels, delay by period |

## Result (00:19 data held out, run J core arc masses, 10 NM bins)
| term | mean latitude shift | median shift | ln R, core vs uniform |
|---|---|---|---|
| flaperon, conditional on recovery | +0.005 deg | +0.6 NM | +0.13 |
| flaperon, unconditional (Davey form) | +0.24 deg | +5.7 NM | -0.05 |
| flaperon, kernel and timing | +0.28 deg | +3.7 NM | -0.28 |
| nine items, module likelihood (ledger) | +1.00 deg | +28 NM | -0.73 |

Davey-method reproduction on the earlier 00:19 map (results/davey-ch11-reproduction.md): median +2.75 NM, mean +10 NM.

## Reading
1. With the flaperon alone, the shift is negligible in all three forms (median under 6 NM). This agrees with Davey et al. (2016).
2. Across 30-40 S the conditional Réunion share changes by less than 0.1 ln unit. Unconditional arrival rises about 0.4 ln unit from 37.5 S to 30-34 S.
   The flaperon alone does not separate latitudes in the satellite band.
3. The nine-item profile rises 1.2 ln units from 37.5 S to 35 S and 2.3 to 30 S. The drift-satellite tension therefore comes from the
   other eight finds (and the Australian term), not from the flaperon.

## To make it exact
Write a_j and A_c per block and per environment in the node tables (a small output-only change). Then any subset of finds and any
detection-level scheme is a re-weighting with no new transport. It also removes the 21 Oct gate failure for the ruled Australian scheme.

Files: `flaperon_only_indicative.py`, `flaperon-proxy-by-latitude.csv`, `flaperon-only-indicative-shifts.csv` (all six 00:19 treatments).
