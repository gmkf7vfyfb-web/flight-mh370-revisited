# End-of-flight work order (b), 15 Oct 2026 — results

Order: `threads/work-orders/eof-order-2026-10-15b.md`. Source sample for items 1 and 2: run-i-dive, 4 strata x 8 seeds, 127,999,840 impacts, strata mixed at the core family prior 0.9982 / 0.0011 / 0.0004 / 0.0002. No new descents for items 1-2.

> The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all
> three rounds. Impact energy, attitude, flight-path angle and energy-transfer duration from
> this arm are a labelled sensitivity on uncalibrated dynamics, not a physical prediction.

## 1. Decision 4 recorded

The headline uses dive probability p = 0.5; the sweep over p is a declared sensitivity. This is what the run-i-dive configuration already flies (`full/dive-branch.toml`, coin at 0.5, which item 7 showed is identical to the U[0,1] hyper-prior for every reported quantity), so no configuration changes. Every acoustic product carries the p-sweep table of section 2.3.

## 2. D0 redefined: 00:19 values held out, transmission imposed

**Definition used.** D0' = stored weight x 1[airborne at 00:19:37.443, the R1200 acknowledge] x (1 − P(in-flight breakup before that burst)). The survival factor is included because it is the adopted part of the 00:19 data model (architecture 20:55Z 11 Oct): an aircraft that has broken up cannot transmit either.

**What was affected and what was not.** The 00:19 two-factor table (`smoke/option_table_0019.py`) already imposed both facts: its log-on constraint requires the aircraft alive at 00:19:37.443 in every C1 and C2 cell, and every cell carries the survival factor. So **every D0 cell of the two-factor table, and every ln Z, latitude and family share quoted from it (run-i-dive §1, item 8 rule 11), is unchanged.** What used the raw stored weights as the "held out" baseline, and is corrected here: the hydroacoustic loud-tail convention (`run-i-dive/loud_tail_ess.py`), the item 7 p-sweep's held-out rows, and the item 8 impact-condition comparison.

### 2.1 How much of the raw D0 weight was physically impossible — correction to the 32.8 per cent figure

Measured on the full sample: **0.1298 of the raw D0 weight is on the sea before 00:19:37** (every stratum 0.129-0.133; seeds 0.092-0.158). The survival factor removes a further share, so D0' keeps exp(-0.2446) = 0.7830 of the raw mass.

**The 32.8 per cent in the order is not an impact-time share.** On waypoints seed 1, 0.3279 of the weight has no module state at the final burst (`latent:last_burst_latitude_deg` and `latent:state_m0019b_*` are NaN), but those latents are NaN in two different cases: the aircraft was already on the sea (0.1176 of the weight), or its descent had not yet begun and it was still in core cruise at 00:19:37 (0.2099). The second group is airborne and was wrongly counted as impossible. The earlier memory row ("the group carries 32.8 per cent of held-out weight") and `answers-2026-10-15-pm.md` §6 inherited that reading.

### 2.2 D0 shares, raw against transmission imposed

| quantity | raw D0 (old) | D0' transmission imposed |
|---|---|---|
| A1 share | 0.1522 | 0.1401 |
| A2 share | 0.3156 | 0.3410 |
| B controlled share | 0.5312 | 0.5179 |
| B uncontrolled share | 0.0009 | 0.0010 |
| impact latitude q05 / q50 / q95 | -38.79 / -37.02 / -33.98 | -38.92 / -37.16 / -34.00 |
| flight-path angle < 10 / 10-45 / > 45 deg | 0.7374 / 0.1628 / 0.0998 | 0.8302 / 0.0977 / 0.0722 |
| impact energy q05 / q50 / q95 (GJ) | 0.35 / 1.23 / 10.98 | 0.34 / 1.08 / 10.67 |
| effective impacts | 10,837,332 | 9,776,070 |

Removing the impossible early impacts moves the held-out median 0.14 deg south (−37.02 to −37.16) and takes out a third of the 10-45 degree band (0.163 to 0.098): early impacts are disproportionately the acoustically decisive ones.

### 2.3 Loudness on the feasible set

Threshold: 90th percentile of peak radiated power under D0' = 2.947e+10 W (the old raw-D0 threshold was 6.53e+10 W). Against this threshold the raw D0 would read 0.1551.

| 00:19 treatment | data treatment x transmission x survival | effective impacts | two-factor total (q = 1/3, C2 silent) | effective impacts |
|---|---|---|---|---|
| D0 | 0.1000 | 9,776,070 | 0.1368 | 891,309 |
| D1 | 0.1186 | 8,849,850 | 0.1386 | 857,064 |
| D2 | 0.1538 | 244,850 | 0.2079 | 71,111 |
| D3 | 0.1958 | 8,356 | 0.2096 | 4,653 |
| D4 | 0.1927 | 55,302 | 0.2065 | 33,741 |
| D5 | 0.2365 | 16,004 | 0.2562 | 10,456 |

**Correction to the order's loudness figures (D0 0.100 ... D4 0.317).** Those came from one seed of one stratum. On the full sample the ordering survives in direction — every informative 00:19 treatment is louder than D0' — but the ratio is smaller: D4 is **1.93x** D0' as a data treatment (0.193 against 0.100), not 3.2x, and D3 and D4 are equal within noise (0.196 and 0.193). The loudest treatment is D5 (0.237). With the log-on cause model applied (the two-factor totals) D0 itself rises to 0.137 and the D4/D0 ratio falls to 1.5; the cause model moves weight towards louder impacts in every treatment (why is not established here).

### 2.4 The dive-probability sweep on the feasible set (supersedes item 7's held-out rows)

| 00:19 data | p | FPA < 10 | 10-45 | > 45 | loud decile | energy q50 (GJ) | effective impacts |
|---|---|---|---|---|---|---|---|
| D0' held out, transmission imposed | 0.00 | 0.8934 | **0.0349** | 0.0717 | 0.0786 | 1.00 | 6,479,114 |
| D0' held out, transmission imposed | 0.25 | 0.8619 | **0.0661** | 0.0719 | 0.0893 | 1.04 | 8,650,738 |
| D0' held out, transmission imposed | 0.50 | 0.8302 | **0.0977** | 0.0722 | 0.1000 | 1.08 | 9,776,070 |
| D0' held out, transmission imposed | 0.75 | 0.7981 | **0.1295** | 0.0724 | 0.1108 | 1.13 | 8,687,689 |
| D0' held out, transmission imposed | 1.00 | 0.7657 | **0.1616** | 0.0727 | 0.1217 | 1.18 | 6,462,345 |
| D2 R600 BTO + R600 BFO | 0.00 | 0.8341 | **0.0416** | 0.1244 | 0.1372 | 1.05 | 155,972 |
| D2 R600 BTO + R600 BFO | 0.25 | 0.8119 | **0.0634** | 0.1247 | 0.1455 | 1.08 | 213,763 |
| D2 R600 BTO + R600 BFO | 0.50 | 0.7896 | **0.0853** | 0.1250 | 0.1538 | 1.12 | 244,850 |
| D2 R600 BTO + R600 BFO | 0.75 | 0.7672 | **0.1074** | 0.1254 | 0.1621 | 1.16 | 215,022 |
| D2 R600 BTO + R600 BFO | 1.00 | 0.7447 | **0.1296** | 0.1257 | 0.1705 | 1.20 | 156,269 |
| D4 both BFOs, Holland transient bias added | 0.00 | 0.9094 | **0.0365** | 0.0541 | 0.0656 | 1.06 | 26,495 |
| D4 both BFOs, Holland transient bias added | 0.25 | 0.7080 | **0.2382** | 0.0538 | 0.1286 | 1.25 | 39,977 |
| D4 both BFOs, Holland transient bias added | 0.50 | 0.5030 | **0.4436** | 0.0534 | 0.1927 | 4.94 | 55,302 |
| D4 both BFOs, Holland transient bias added | 0.75 | 0.2943 | **0.6526** | 0.0531 | 0.2580 | 9.80 | 57,913 |
| D4 both BFOs, Holland transient bias added | 1.00 | 0.0818 | **0.8654** | 0.0527 | 0.3245 | 10.19 | 43,658 |

Under D0' the 10-45 degree band runs 0.035 to 0.162 across p (item 7's raw rows read 0.035 to 0.290). Under D4 the range is unchanged, 0.037 to 0.865, because D4 already required the aircraft to be airborne at the bursts. The finding of item 7 stands: under the treatments that use the 00:19 BFOs, the acoustic quantities are governed by a prior the data barely constrain.

## 3. Bank limit sampled per trajectory — design note, smoke and predictions

**Code (module only, `make scope` clean).** `envelope.spiral_bank_cap_prior = {core_deg, tail_to_deg, tail_weight}` (`profile.rs` `BankCapPrior`): when set, the divergent-spiral bank limit is drawn per descent from a two-part mixture of uniforms and recorded in the new latent `spiral_bank_cap_deg` (also kept by the compact format). Absent, no uniform is drawn: the new binary (`mh370-eof-ob1`, sha256 dc1f52f8b4345712...) reproduces item 8's round-3 seed to the last bit (next-i-free seed 1, all 42 cells, maximum difference 0.000e+00 nat). Unit test: draws stay on the support, the tail carries its weight to 0.005, the core is uniform; malformed priors are refused. 127 module tests pass.

**Prior (`full/bank-cap-sampled.toml`).** Core U[52, 63] deg with weight 0.8: the maximum track-read bank of Boeing's four spiral-dive cases (3, 4, 6, 10: 54.5, 59.9, 57.3, 53.2 deg, measured by the same code that measures the model's track), widened to cover the leave-one-out fits (57.3-62.4 deg) and the all-data 52.5 deg, rounded outward. Tail U[63, 90] deg with weight 0.2. The tail exists because four no-input cases at one mass and configuration do not bound the bank of a different loss of control, and 90 deg is the cap at which this point mass reaches the published high-rate thresholds. **The tail weight is a declared choice; because the drawn limit is recorded, any tail weight re-weights exactly** (core rows x (1 − t')/0.8, tail rows x t'/0.2).

**Smoke** (round-3 laws, next-i-free seed 1, 3.2 M impacts each, D0' feasible set; labelled sensitivity on uncalibrated dynamics):

| bank limit | FPA < 10 | 10-45 deg | > 45 deg | energy q50 (GJ) | divergent-spiral share | effective impacts |
|---|---|---|---|---|---|---|
| fixed 52.5 deg (item 8) | 0.7926 | **0.2030** | **0.0044** | 0.97 | 0.227 | 510,788 |
| sampled, tail weight 0.2 | 0.7659 | **0.2170** | **0.0171** | 0.93 | 0.205 | 474,545 |
| fixed 90 deg | 0.7474 | **0.1177** | **0.1350** | 0.92 | 0.196 | 483,022 |

Within the sampled arm, by the drawn limit (shares of that bin's weight):

| drawn limit (deg) | share of prior weight | 10-45 deg | > 45 deg |
|---|---|---|---|
| 52-56 | 0.1999 | 0.2130 | 0.0047 |
| 56-60 | 0.1945 | 0.2276 | 0.0048 |
| 60-63 | 0.1460 | 0.2347 | 0.0050 |
| 63-70 | 0.0349 | 0.2447 | 0.0071 |
| 70-80 | 0.0497 | 0.2115 | 0.0476 |
| 80-90 | 0.0491 | 0.1242 | 0.1288 |

Tail weight re-weighted exactly from the same sample:

| tail weight | 10-45 deg | > 45 deg | effective impacts |
|---|---|---|---|
| 0.00 | 0.2241 | 0.0048 | 389,050 |
| 0.10 | 0.2206 | 0.0110 | 454,540 |
| 0.20 | 0.2170 | 0.0171 | 474,545 |
| 0.35 | 0.2116 | 0.0264 | 401,187 |
| 0.50 | 0.2062 | 0.0357 | 284,681 |

**What the smoke shows.** The steep tail is set almost entirely by limits above 70 deg: below 70 deg the share above 45 deg stays at 0.005 whatever the limit, at 70-80 deg it is 0.048 and at 80-90 deg 0.129. So the question the acoustics depends on is not "52.5 or 60" but **how much prior weight sits above 70 deg**, which the Boeing traces do not inform. Under the sampled prior the share above 45 deg is 0.017 (0.005 at tail weight 0, 0.036 at 0.5) against 0.004 at the fixed 52.5 deg and 0.135 at a fixed 90 deg; the 10-45 deg band is 0.21-0.22, close to the 52.5 deg arm. ln Z on the smoke (q = 1/3, C2 silent; production on the same seed in brackets): D0 −7.78 / −7.80 / −7.74 for sampled / 90 / 52.5 (−7.64); D4 −29.08 / −28.48 / −29.22 (−29.19), effective impacts under D4 441 / 399 / 1,532, so the D4 differences are not yet resolved.

**Predictions for the full runs, posted before they start** (round-3 laws, 4 strata x 8 seeds, D0'): sampled arm — 10-45 deg 0.20-0.23, above 45 deg 0.012-0.025, held-out ln Z within 0.2 nat of the 52.5 deg arm; fixed-90 arm — 10-45 deg 0.10-0.14, above 45 deg 0.11-0.15, held-out ln Z within 0.2 nat; under D4 neither arm moves ln Z by more than 1 nat from the 52.5 deg arm (the work order's stop condition carried over). If D4 under the fixed-90 arm moves by more than 1 nat, that is reported as a finding, not averaged away.

## 4. Onset prior for planned descent (B): the uniform-onset sensitivity

**The definition decides the answer, so it is stated first.** Two readings of "uniform onset 22:41-00:11" give opposite results:

- **U1, the onset alone (exact).** For each parent the deliberate onset before 00:11 is uniform in clock time on [22:41, min(00:11, P)], with the parent's fuel-tied pre-00:11 deliberate mass kept, so the core posterior at 22:41 is untouched and only the timing changes. Implemented as an exact per-row factor in the join (`smoke/onset_uniform_reweight.py`); prior recovery checked on every seed (expected 1: 0.9982-1.0019).
- **Binned (the coordination estimate).** Onset bins re-weighted from their pooled prior shares to their clock-time widths. Because 82 per cent of the 22:41 deliberate weight belongs to parents whose own predicted exhaustion is before 00:11 (seed 1; weighted median 23:46), late bins can only be filled by the few parents with more fuel, so the binned factor (up to 6x on 00:00-00:11, where the pooled prior share is 0.020) **re-weights parents by their fuel state**. That changes the core's posterior at 22:41, not just the onset prior.

| 00:19 treatment | B share, fuel-tied (joined V2) | B share, U1 uniform onset | B share, binned (coordination's method) | pre-00:11 share, fuel-tied → U1 | ln Z change, U1 |
|---|---|---|---|---|---|
| D0 | 0.108 (0.062-0.254) | 0.098 (0.056-0.223) | 0.197 (0.108-0.423) | 0.0708 → 0.0618 | -0.010 |
| D2 | 0.077 (0.021-0.119) | 0.076 (0.021-0.119) | 0.078 (0.022-0.121) | 0.0009 → 0.0006 | -0.000 |
| D4 | 0.044 (0.020-0.089) | 0.044 (0.020-0.088) | 0.044 (0.020-0.089) | 0.0000 → 0.0000 | -0.000 |

Median over 8 seeds, range in brackets. Source: run I joined V2 (`results/eof-joined-v2-oct14`), stratum next-i-waypoints, same convention as the coordination figures (two-factor totals, q = 1/3, C2 silent, transmission imposed).

**Reading.** The binned method reproduces the coordination session's doubling (here 0.108 to 0.198; theirs 0.108 to 0.225 — the difference is their bin edges). The exact onset-only sensitivity does the opposite and mildly: B falls from 0.108 to 0.098 under D0. The likely reason, not separately tested: spreading each parent's pre-00:11 onset mass uniformly moves part of the fuel-cue component earlier, and early onsets fit the 23:15 and 00:11 data worst. Under D2 and D4 nothing moves (pre-00:11 share at most 0.004). **So the statement "the B share under D0 depends on the onset prior" is true only if the uniform prior is also allowed to re-weight the aircraft's fuel state at 22:41.** With the core posterior held fixed, B under D0 is 0.10-0.11 under either onset prior, and "00:11 selects cruise" stands.

**Direct run: held for a ruling, not started.** A direct 22:41-arm run is built and tested (`onset.deliberate_proposal_window_unix_s`: a clock-time proposal window with the exact correction back to the fuel-tied prior, so U1 and the fuel-tied prior are both exact from one run; unit test of prior recovery inside the window passes for both deliberate mechanisms). It costs about 3.7 h at 12 threads (eight 22:41-arm seeds at 28 min). It would raise the pre-00:11 effective impacts under U1 (now 94-225 per seed under D0) but **cannot represent the binned version**, which is not a per-parent onset prior. Which definition the paper uses is a scientific choice the order does not settle and it decides whether B under D0 doubles; it is posted to architecture for Pete. Run J does not exist yet (core order b: Pete's explicit GO), so "run-J scale" is read as the joined V2 production scale on run I.

## 5. COVERAGE

**(a) Feasible set.** Item 2 removes from every product the 13.0 per cent of held-out weight that is physically impossible (on the sea before the final transmission) and the in-flight breakups before it. Item 3: a 777-200ER in an uncontrolled divergent spiral can overbank anywhere up to and past 90 deg; the Boeing traces show 53-60 deg in four no-input cases. Item 4: a planned descent may begin at any time before exhaustion.
**(b) Model's reach.** The bank limit is now a sampled parameter with support [52, 90] deg, closing the reach gap of the fixed 52.5 deg cap; limits above 90 deg (overbank) remain outside the reach and are declared. The onset window proposal adds no reach; it changes only where samples land.
**(c) Proposal's coverage.** D0' keeps 9.78 M effective impacts. The tail of the bank-limit prior carries 25,082-31,460 effective impacts per 10-deg bin on one smoke seed, so the tail weight is estimable by re-weighting from 0 to at least 0.5. The pre-00:11 B population under D0 has 140-229 effective impacts per seed under the fuel-tied prior and is a standing coverage gap; under D2 and D4 it has 1-11 and is NOT estimable (reported as such, not as absence).

## 6. Item 3 full runs: the bank limit at run-I scale (round-3 laws, 4 strata x 8 seeds each)

Two sweeps under the heavy lock, binary `mh370-eof-ob1`: sampled limit 20:10-22:28Z, fixed 90 deg 22:28Z-00:49Z (16 Oct). Fixed 52.5 deg is item 8's run. Per-seed files summarised per stratum and removed; tables and subsamples kept on the exchange at `end-of-flight/order-b-bank-cap/`. All three are labelled sensitivities on uncalibrated dynamics.

### 6.1 Impact conditions on the feasible set (D0')

| arm | FPA < 10 | 10-45 deg | > 45 deg | energy q50 (GJ) | tau90 q50 (s) | effective impacts |
|---|---|---|---|---|---|---|
| production (run-i-dive) | 0.8319 | **0.0955** | **0.0726** | 1.08 | 3.90 | 317,414 |
| round-3, fixed 52.5 | 0.7705 | **0.2230** | **0.0065** | 1.02 | 3.85 | 295,342 |
| round-3, sampled limit | 0.7423 | **0.2366** | **0.0210** | 0.97 | 3.48 | 283,982 |
| round-3, fixed 90 | 0.7192 | **0.1243** | **0.1565** | 0.96 | 3.11 | 279,350 |

These supersede item 8's impact-condition table, which used the raw held-out weights (round-3 10-45 deg 0.323 / above 45 deg 0.012 there; 0.223 / 0.0065 on the feasible set).

Sampled arm, tail weight re-weighted exactly, and by drawn limit:

| tail weight | 10-45 deg | > 45 deg | effective impacts |
|---|---|---|---|
| 0.00 | 0.2455 | 0.0072 | 227,993 |
| 0.10 | 0.2411 | 0.0141 | 267,631 |
| 0.20 | 0.2366 | 0.0210 | 283,982 |
| 0.35 | 0.2299 | 0.0315 | 248,705 |
| 0.50 | 0.2232 | 0.0420 | 181,246 |

| drawn limit (deg) | share of weight | 10-45 deg | > 45 deg |
|---|---|---|---|
| 52-56 | 0.2960 | 0.2328 | 0.0068 |
| 56-60 | 0.2886 | 0.2481 | 0.0072 |
| 60-63 | 0.2175 | 0.2593 | 0.0075 |
| 63-70 | 0.0515 | 0.2616 | 0.0101 |
| 70-80 | 0.0737 | 0.2275 | 0.0529 |
| 80-90 | 0.0727 | 0.1304 | 0.1495 |

**Against the predictions posted at 20:10Z.** Sampled arm: 10-45 deg 0.237 against 0.20-0.23 predicted (**outside, by 0.007**; the one-seed smoke ran 0.02 low, as it did for the 52.5 deg arm), above 45 deg 0.021 against 0.012-0.025 (inside). Fixed 90: 10-45 deg 0.124 against 0.10-0.14 (inside), above 45 deg 0.157 against 0.11-0.15 (**outside, by 0.007**). The structural result held: the steep tail is set by limits above 70 deg (above 45 deg: 0.007-0.010 for limits below 70 deg, 0.053 at 70-80, 0.150 at 80-90).

### 6.2 Evidence, latitude and family shares (two-factor totals, q = 1/3, C2 silent; change against the fixed 52.5 deg arm)

| cell | ln Z, 52.5 | sampled (change) | fixed 90 (change) | latitude median 52.5 / sampled / 90 | A1 share 52.5 / sampled / 90 | effective impacts 52.5 / sampled / 90 |
|---|---|---|---|---|---|---|
| D0 | -7.424 | -7.471 (-0.048) | -7.499 (**-0.075**) | -37.13 / -37.17 / -37.21 | 0.180 / 0.178 / 0.169 | 754,291 / 708,703 / 665,660 |
| D1 | -12.858 | -12.898 (-0.040) | -12.927 (**-0.068**) | -37.21 / -37.25 / -37.29 | 0.196 / 0.201 / 0.194 | 812,266 / 771,698 / 724,661 |
| D2 | -19.036 | -19.076 (-0.040) | -19.084 (**-0.048**) | -37.15 / -37.19 / -37.21 | 0.208 / 0.223 / 0.231 | 62,024 / 59,332 / 57,153 |
| D3 | -28.615 | -28.600 (+0.015) | -28.568 (**+0.047**) | -37.35 / -37.35 / -37.33 | 0.062 / 0.066 / 0.105 | 5,586 / 5,146 / 5,317 |
| D4 | -28.703 | -28.576 (+0.127) | -27.885 (**+0.818**) | -37.33 / -37.28 / -37.10 | 0.103 / 0.206 / 0.578 | 33,343 / 18,797 / 8,923 |
| D5 | -29.225 | -29.232 (-0.007) | -29.196 (**+0.028**) | -37.33 / -37.33 / -37.32 | 0.057 / 0.054 / 0.083 | 9,258 / 8,335 / 9,338 |
| D4 x C2 silent | -32.932 | -32.691 (+0.240) | -31.903 (**+1.028**) | — | — | — |

**Finding.** Held out and under D1-D3 and D5 the bank limit changes nothing that matters (|change| at most 0.08 nat, medians within 0.08 deg). **Under D4 — the treatment with Holland transient bias added — it changes the attribution.** With a fixed 90 deg limit the round-3 dynamics produce steep spiral dives that fit the D4 descent rates: ln Z rises 0.82 nat, the D4 x C2-silent cell by 1.03 nat (the only cell past 1 nat), **A1 (uncontrolled after fuel exhaustion) goes from 0.103 to 0.578 of the weight**, and the D4 median moves 0.23 deg north (−37.33 to −37.10). The sampled limit sits between (A1 0.206, +0.13 nat). Under the production dynamics with the same 90 deg cap A1 is 0.145 under D4, so it is the combination of the round-3 laws (fast spiral doubling, 26 s) with a high limit that does it.

**Consequence for the paper.** Under D4, "which family" is decided by how much prior weight the bank limit has above 70 deg, which no Boeing trace informs, on dynamics that failed their calibration gate. The D4 family shares must be reported with the bank-limit prior beside them, and the A1 reading of Holland's Hypothesis 1 is not identified by this sample. The work order's 1-nat stop condition is about the held-out evidence (−0.075 nat, not tripped); the D4 x C2-silent cell exceeds 1 nat and is reported as a finding, not averaged away.

**Coverage, item 3.** The bank-limit reach now spans 52-90 deg (overbank beyond 90 deg remains outside the reach, declared). Effective impacts per 10-deg limit bin above 63 deg: 14,566-20,848 on the feasible set, so the tail weight is estimable from 0 to 0.5. Under D4 the fixed-90 arm has 8,923 effective impacts, above the 1,000 gate.

---

Footnote (ASD-STE100). We removed from the held-out results the aircraft that were on the sea before the last signal. That was 13 per cent of the weight, not 33 per cent. We let the largest bank of an uncontrolled spiral change from flight to flight. Below 70 degrees it has almost no effect. Above 70 degrees it makes steep impacts. With the Holland reading of the last signals, a limit of 90 degrees makes the uncontrolled family the most probable. We do not know the correct limit. The descent physics is not calibrated, so you must not use the energy, the angle or the duration as a prediction.

Footnote (technical). Source: core run I m0011 hand-offs; end of flight run-i-dive (binary mh370-eof-ri3) for items 1-2 and the production row; round-3 arms with `full/round3-laws.toml` (+ `bank-cap-sampled.toml` or `bank-cap-90.toml`), binary mh370-eof-ob1 (sha256 dc1f52f8...), 4 strata x 8 seeds, strata at the core family prior 0.9982 / 0.0011 / 0.0004 / 0.0002. D0' = airborne at 00:19:37.443 x (1 − P(in-flight breakup before it)). Two-factor cells q = 1/3, W = 3,898 s, C2 silent, survival factor. Dive probability 0.5 (Decision 4). Impact conditions from weight-proportional subsamples (50,000 per seed); energy, peak power, tau90 from the tau90_v1 sidecar. Uniform-onset results from run I joined V2 (stratum next-i-waypoints, 8 seeds). Core run I NOT CONVERGED; uncontrolled-arm dynamics NOT CALIBRATED (gate failed in all three rounds).
