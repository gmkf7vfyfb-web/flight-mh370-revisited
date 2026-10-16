# Run J (core) — results, 16 October 2026

Definition: `engine/config/sensitivity/run-j/README.md`. Tag `run-j` = 1244b7c, bin-1244b7c
(sha256 dc18d927…). Pete pre-approved 02:15Z; smoke 4de50044 passed; launched 02:44Z; finished 21:21Z.
Every job re-checked gates B/C (byte-identical) and regress-seed1 (equal) before running. MANIFEST-*.txt
hold the chains and the sha256 of every config and data file.

| Stratum (job) | Seeds x particles | Wall | ln Z (seed sd) | Split-half | Median | 2.5% | 97.5% | Shoulder 34.5–36.5 S |
|---|---|---|---|---|---|---|---|---|
| waypoints (241336ad) | 24 x 7M | 8 h 37 min | −127.815 (0.26) | 0.907 | −37.097 | −37.650 | −33.045 | 0.167 |
| free (87214725) | 18 x 7M | 3 h 56 min | −134.493 (0.34) | 0.840 | −36.881 | −38.231 | −28.951 | 0.374 |
| descent-climb (1a210a80) | 16 x 3.5M | 1 h 52 min | −136.138 (0.39) | 0.884 | −36.974 | −38.144 | −33.260 | 0.339 |
| repro (ab0d0171) | 16 x 3.5M | 1 h 33 min | −135.834 (0.16) | 0.924 | −36.448 | −38.124 | −27.882 | 0.427 |

Family posterior at equal prior: **waypoints 0.9982**, free 0.0013, repro 0.0003, descent-climb 0.0002.
ln BF waypoints over free 6.68 nat (run I 6.78). ln Z is not comparable with run I (BFO sd differs).

## Convergence — PASS by project ruling (Pete, 16 Oct 2026)

The split-half column in the table above is the engine's single first-half/second-half value. The project
statistic is the mean over balanced partitions (a fixed random sample of 20,000 when there are more):

| Family | All-partition mean (all seeds) | Random 8-seed subsets (8-replicate floor 0.924) | Run I (8 seeds) |
|---|---|---|---|
| waypoints (24) | 0.934 (0.852–0.978) | 0.892 (5–95% 0.860–0.920) | 0.916 |
| free (18) | 0.873 (0.748–0.950) | 0.819 (0.774–0.867) | 0.830 |
| descent-climb (16) | 0.871 (0.742–0.950) | 0.824 (0.797–0.852) | 0.794 |
| repro (16) | 0.921 (0.841–0.964) | 0.890 (0.879–0.902) | 0.891 |

**Pete accepted the free-flight value as a PASS; free is the lowest family, so the ruling covers all of run
J.** Do not label run J "not converged". No floor is calibrated beyond 8 replicates; floors are project
conventions (Davey et al. published none). The thin northern detail (prediction 5) is a separate limitation.

## Held-out 18:25:27 R600 burst (companion 9ba45948, repro, seeds 1–8 matched)

| Quantity | Run J (4.32 Hz) | Best attainable | Implied residual |
|---|---|---|---|
| ln p(BFO \| all other data) | −2.952 (SE 0.051) | −2.509 (sigma_eff 4.91 Hz, approximate) | about 0.9 sigma |
| ln p(BTO \| all other data, BFO) | −5.764 (SE 0.067) | −5.046 (sd 62 us) | about 1.2 sigma |

The burst is predicted well (Pete's expectation). **Sensitivity:** if the burst WERE used, the repro PDF moves
south: matched seeds 1–8 median −36.394 → −36.618 (BFO only) → −36.849 (BTO and BFO); shoulder 0.445 → 0.395
→ 0.336; overlap 0.924 / 0.874. Half-to-half Monte Carlo noise is 0.13 deg in the median, so this is a real
effect, larger than the proposal's "< 0.3 deg". Holding it out is Pete's ruling; this is its declared sensitivity.

## Predictions (written before the run) against results

| # | Prediction | Result |
|---|---|---|
| 1 | Waypoints keeps > 99% | **Holds**: 0.9982 |
| 2 | 4.32 Hz raises the shoulder by about the reproduction's +0.07 | **Holds** for waypoints: 0.109 → 0.167. Free unchanged (0.372 → 0.374) |
| 3 | kappa_x moves the FE median < 1 min | Not assessed in run J (no kappa_x-off arm); smoke −25 s |
| 4 | Split-half meets the floor for each seed count | **PASS by project ruling** (Pete, 16 Oct 2026; see below) |
| 5 | Pooled northern lineages north of 33 S: waypoints about 450, free about 420 | **Fails**: waypoints 119.8, free 80.7 (see below) |
| 6 | The held-out R600 burst scores close to the best attainable | **Holds** (0.9 sigma BFO, 1.2 sigma BTO) |

**Prediction 5.** Waypoints: one lineage in seed 15 carries 8.4% of all northern (r-weighted) mass over 24
seeds; without it the pooled count is 645. Per-seed mean 40.8 (run I 38.5). Free: per-seed mean 19.6 (run I
35.9), pooled 80.7, 129.9 without its top lineage. The bootstrap from run I's 8 seeds did not capture this
heavy tail. The northern mass itself is estimated with relative SE 8.6% (waypoints) and 9.1% (free) between
seeds. The SHAPE of the PDF north of 33 S remains Monte-Carlo-limited; the evidence-tilted proposal is the
remedy that targets this, if Pete wants it.

## Where the outputs are

`mh370-exchange/core/run-j/`: run-j-waypoints (291 files, 46 GB), run-j-free (183, 22 GB),
run-j-descent-climb (163, 10 GB), all SHA256SUMS-verified; run-j-repro-radar (147 files, 6.9 GB), run-j-repro-r600 and run-j-repro-r600bfo (75 files each), all
verified (16 Oct 22:30Z). Deskstar copies deleted.
