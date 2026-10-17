# End of flight: overnight summary, 16–17 Oct 2026 (run J)

Prepared at about 13:50Z on 17 Oct for Pete. Every item is committed to branch `claude-science-sep29` and posted in
`coordination/architecture.md`. Core run J's split-half convergence is accepted as a pass by project ruling (16 Oct 2026). The
precision statements below are about end of flight's own sampling.

![Run I against run J]({{artifact:art_35e9f14a-b26d-45ad-b449-495d0115abe9}})

## What finished

| item | result | note in the repo |
|---|---|---|
| Run-J production end-of-flight set, all 4 strata (74 seeds) | READY. The mixture is the waypoints stratum (core P 0.9982). D0': A1/A2/B 0.17/0.34/0.48, median latitude −37.12 | `results/eof-run-j-oct17/` |
| Both-burst supplementary pass (8 waypoints seeds, 256 descents per parent, thinned) | D4 ESS 44k (production 21k). D4 A1/A2/B 0.25/0.32/0.43. The two independent passes agree within 0.05 nat and 0.05 in shares | `results/eof-run-j-waypoints-oct16/` §3b |
| Joined V2 with the 22:41 onset window (your item 4 direct run), 16 seeds | **B under D0' 0.196 fuel-tied, 0.168 U1** (run I 0.108 / 0.098). Pre-00:11 ESS 2,091 pooled. Stable from 8 to 16 seeds | `results/eof-run-j-joined-v2-oct17/` §2c |
| Bank-limit prior (uniform 52–90 deg, recorded per row) | Under D4, A1 is 0.08 (Boeing-weighted), 0.13 (uniform) and 0.21 (80–90 deg). Steep impacts with no 00:19 data: 0.035 / 0.088 / 0.223 | waypoints note §3 |
| Consumer products for downstream modules | impact-time shares, family evidence and shares, same-data Bayes factors, 00:19 posterior predictive, H1/H2, tau sidecar | `run-j/summary/` |
| D3-aimed selection smoke | D3 ESS rises by 5.8 times, but **the A1 sub-population under D3 stays at about 60 per seed**. Its share (0.06–0.09) is stable; its distribution shape is a declared gap | waypoints note §3c |

## Corrections I made overnight
- **The aimed-selection "defect" is withdrawn.** The prior-recovery deviations are within the ESS-scaled 95 % band (at most 0.63 of
  it). The fixed 0.0030 standard does not scale with ESS. The acceptance script now reports the scaled band.
- **Thinned files:** ln Z must be normalised by `thinning.weight_sum_in`. The first version of the summary got this wrong by a
  constant (+2.16 nat). It is fixed, and seed 1 is corrected.
- **Bank-prior variants:** the "80–90 deg only" ln Z needed the prior's mean (10/38) in its normaliser. It is fixed.
- **Wording:** D3 is now described as "an end-of-flight coverage gap (low ESS)", not "not converged", to follow core's ruling.
- **Two free-disk figures in architecture.md posts were wrong** (I wrote 12 and 7 GiB; the measured values were 20 and 15).
  Both are corrected.

## What it means for the paper
1. **The latitude is stable.** Every treatment's median impact latitude moves by at most 0.11 deg from run I to run J.
2. **Planned descent from 22:41 is more likely on run J:** 0.17–0.20, against 0.10–0.11 on run I. "00:11 selects cruise" still
   holds, but more weakly: A1 + A2 is 0.77 against B 0.19 with no 00:19 data.
3. **Under the transient-bias treatment (D4), the bank-limit prior decides the A1 share** (0.08–0.21), and it decides the
   steep-impact share for hydroacoustics. D4 must be given as a range over that prior.
4. The run I → J differences combine new core inputs and new descent laws. Neither can be credited alone.

## Open, and why
- **Joined V2 seeds 17–24:** these would add about 30 % to the pre-00:11 sample. They need about 24 GB, and the Mac has 15 GiB free.
  Waiting for disk.
- **The A1 sub-population under D3:** no current proposal reaches it. It needs a new A1-aimed descent proposal (module design work),
  and is a declared coverage gap meanwhile.
- **The pre-00:11 planned-descent sample is limited by the 22:41 parents** (121 effective parents per seed), not by onset sampling.
  The structural fix is a larger or aimed 22:41 hand-off from core.

> The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all
> three rounds. Impact energy, attitude, flight-path angle and energy-transfer duration from
> this arm are a labelled sensitivity on uncalibrated dynamics, not a physical prediction.
