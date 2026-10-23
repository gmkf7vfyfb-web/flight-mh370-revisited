# Run I: are the loud impacts sampled well enough to be worth testing?
Measured 13 Oct 2026 from the end-of-flight run I output at `mh370-exchange/end-of-flight/run-i`
(4 strata x 8 seeds, 102,399,904 impacts from 3,199,997 parents).

## What was measured and how

The loudness proxy is **peak radiated mechanical power** at impact, `peak_rate_w`, taken from the
energy-transfer sidecar `tau90_v1.npz` that end of flight wrote on 13 Oct at 08:36 and that is present
in all 32 seed directories (`tau90_s`, `t05_s`, `t95_s`, `peak_rate_w`, `energy_transferred_j`,
`decel_g`, `l_eff_m`; method 1, note `results/eof-impact-tau-method-oct11.md`). The matching
`latent:` columns inside `impacts32.npy` are NaN in every row, which is what the module saw.

Weights are the hand-off weight times the exponential of each option's impact log-likelihood,
self-normalised within each stratum, with the four strata then weighted equally. Equal stratum
weighting is a declared simplification of this diagnostic, not the composer's treatment. Effective
sample size is the usual (sum w)^2 / sum w^2, reported both per impact row and per parent, the
parent figure being the one that counts independent draws. The loud tail is the top decile of peak
radiated power under the 00:19-held-out baseline, that is above 4.678e10 W; the median is 3.474e8 W
and the top percentile is above 1.076e11 W.

**Peak radiated mechanical power is not an acoustic source level.** The coupling from impact to
radiated acoustic energy is the hydroacoustic module's own model and nothing here estimates it. This
diagnostic answers only whether the loud end of the impact set is sampled well enough to test.

## Result

| 00:19 option | effective impacts | effective parents | mass in loud decile | effective impacts, loud decile | effective parents, loud decile | effective impacts, top percentile | median peak power (W) | median tau90 (s) |
|---|---|---|---|---|---|---|---|---|
| none (00:19 held out) | 28,600,767 | - | 0.1000 | 3,005,408 | - | 299,788 | 3.474e8 | 4.00 |
| r600/no-offset | 620,235 | 418,292 | 0.1102 | 75,337 | 68,213 | 5,688 | 3.470e8 | 3.91 |
| r600/inflated | 12,996,572 | 1,871,643 | 0.0564 | 724,882 | 443,158 | 58,848 | 3.275e8 | 4.12 |
| r600/startup-offset | 514,862 | 384,723 | 0.1332 | 105,928 | 90,309 | 9,849 | 3.675e8 | 3.93 |
| r1200/no-offset | 61,814 | 59,407 | 0.1208 | 10,849 | 10,709 | 1,183 | 3.856e8 | 4.12 |
| r1200/inflated | 292,263 | 239,394 | 0.1228 | 51,897 | 48,884 | 4,797 | 3.849e8 | 4.11 |
| r1200/startup-offset | 203,306 | 176,586 | 0.1209 | 38,450 | 36,840 | 3,694 | 3.814e8 | 4.10 |
| both/no-offset | 5,189 | 5,304 | 0.0289 | 762 | 746 | 70 | 3.568e8 | 4.38 |
| both/startup-offset | 20,753 | 20,749 | 0.0297 | 2,206 | 2,287 | 284 | 3.571e8 | 4.36 |
| both/inflated | 98,991 | 93,338 | 0.0509 | 14,448 | 14,067 | 1,348 | 3.647e8 | 4.31 |

## Three findings

**1. The two Holland-reading options are estimable on run I.** `both/no-offset` carries 5,304
effective parents and `both/startup-offset` 20,749, both well above the module's threshold of 1,000.
The figures that made them not estimable, 219 and 159, came from core (b) and reference-289, not from
run I. That earlier finding is superseded for run I and the exclusion should be lifted.

**2. They are not the loud scenarios.** Both put about 0.029 of their probability in the loud decile,
against 0.100 for the held-out baseline, that is roughly three times less. The options that favour
loud impacts are r600/startup-offset at 0.133 and the three r1200 options at 0.121 to 0.123. The
loudest impacts are therefore not concentrated in the options that were being excluded, so excluding
them would not have removed the detectable population.

**3. The loud population is amply sampled.** The baseline has 3.0 million effective impacts in the
loud decile. Eight of the nine options have more than 2,000 effective parents there and seven have more than 10,000;
the ninth, `both/no-offset`, has 746. There is no end-of-flight sampling problem standing in the way of
the detectability work, with that one exception noted below.

## Two depth limits to declare

- `both/no-offset` in the loud decile has 746 effective parents, BELOW the 1,000 threshold. It is not
  estimable at loud-decile depth and must be reported as unconverged there, not as a result.
- At the top percentile, `both/no-offset` (70 effective impacts) and `both/startup-offset` (284) are
  not estimable. Any statement restricted to the very loudest percentile must exclude those two.
