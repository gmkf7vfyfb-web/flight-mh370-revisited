# Run-J northern supplement — results (core, 18 Oct 2026)

Approved by Pete 18 Oct 2026 00:41Z, including the run (architecture.md item 1). Design, measurement and predictions were
posted before the run: `DESIGN.md` (CORE_STAGES 2026-10-18 01:45Z). Run J convergence: PASS by project ruling (16 Oct 2026);
this supplement adds northern detail and does not re-open that ruling.

Staged outputs: `mh370-exchange/core/run-j-supplement/` (236 files, 1.4 GB, SHA256SUMS verified, READY). The staged README
gives the combination rules; they are repeated in section 5.

## 1. What limited the north (measured on all 74 run J seeds; `DESIGN.md` section 1)

- Effective distinct 00:11 states (identical resampled copies merged), impact band, D0': 35-30 S 17.5k, **30-25 S 1.41k,
  25-20 S 378.** Under D2/D4 in 30-25 S only about 500 / 430 states can fit at all (Poisson-hit estimate).
- Under D3 the band ESS rises about linearly with descents per parent and with parents: D3 is descent-limited.
- The magnetic modes carry the north but held only about 45-53 effective distinct states per seed in 30-25 S.

## 2. Design used (cheapest that the measurement says can reach the target)

(a) + (b) on 16 NEW waypoint seeds 1001-1016: (b) particles re-allocated to [TH, MH, TT, MT, LN] = [1.2, 1.3, 1.1, 2.2, 1.2]M
(run J [1.0, 0.5, 2.5, 0.5, 2.5]M), and (a) a latitude-tilted second 00:11 hand-off, `handoff-m0011-supplement/`, 100,000 rows
per seed, defensive share 0.1, flag `output.handoff_supplement` (off by default; code in handoff.rs `supplement`, filter.rs, config.rs).
(a) alone on the existing populations was rejected: re-drawing run J seed 1's own population gave 4x the distinct states in
00:11 30-25 S (1,699 against 408) but only 193 against 175 effective states (posterior-weighted) — the population is the limit.
(c), an evidence-tilted filter, was not needed.

## 3. Gates and checks

| Check | Result |
|---|---|
| Unit tests (incl. new: exact alone and by MIS; rho; config) | 36 + 41 passed (deskstar) |
| Gates B and C vs `gates-2026-10-15`; regress-seed1 | byte-identical; -97.51251428262529 equal |
| FLAG OFF: run J repro seed 1 at 3bf0801 | byte-identical to run J (8 files) |
| FLAG ON: run J waypoints seed 1 | all 11 normal outputs byte-identical to run J; supplement written |
| Prior recovery, same population (seed 1): corrected supplement vs normal hand-off | max abs z 1.35 (13 means) |
| Prior recovery, new seeds vs run J 24 seeds (seed-level z) | supplement max abs z 0.89; normal hand-offs 0.82 |
| Re-allocation exactness, final.npy vs run J | max abs z 1.28 (median, north of 33 / 30 S, shoulder, mean) |
| Combined (rule B) vs production | max abs z 1.59 (production seed SE only) |

All |z| < 3: no latitude band changes the target.

## 4. What the supplement adds (00:11 hand-off level; `mis-check.json`)

| 00:11 band | Effective distinct states, production | Combined (rule B) | Distinct states |
|---|---|---|---|
| 35-30 S | 106,678 | 190,778 | 461k -> 825k |
| 30-25 S | 3,987 | **13,746** (x3.4) | 15.4k -> 90.0k (x5.8) |
| 25-20 S | 518 | **1,049** (x2.0) | 1,966 -> 13,705 (x7.0) |

Rows: 92 % north of 34.5 S at 00:11 (prediction P3: 0.92). Per-mode effective states in 30-25 S, production -> combined: TH
1,650 -> 3,735; MH 1,314 -> 3,423; TT 670 -> 802; MT 1,094 -> 4,992; LN 1,333 -> 1,608.

**Mode-allocation side result (P6).** ln Z seed sd by mode, new seeds against run J: TH 0.236 / 0.196, MH 0.144 / 0.248,
TT 0.507 / 0.343, MT 0.284 / 0.376, LN 0.709 / 0.431; replicate 0.353 / 0.255. MH, TT and LN move as sqrt(particles) predicts
(x0.62, x1.51, x1.44 predicted; x0.58, x1.48, x1.65 seen); MT partly (x0.48 predicted, x0.76 seen). The mode-probability noise
is therefore mostly particle-limited. Mean ln Z per mode agrees with run J within 0.1 nat.

## 5. Hand-off to end of flight (exact rules; also in the staged README)

- **Standalone:** each supplement row's weight x exp(log_correction) (`handoff::read_corrected`); the production recipe unchanged.
- **Combined with run J production (rule B, recommended):** u1 = w exp(lc)/24 for run J rows, u2 = w exp(lc)/S for supplement
  rows (x k if only every k-th row is flown); n1, n2 = rows flown; r = r_hat(00:11 latitude) from `r_hat.csv` (0.1 outside);
  beta1 = n1/(n1 + n2 r), beta2 = n2 r/(n1 + n2 r); row mass = u_t beta_t x the per-descent terms as now. Exact for any r_hat
  (partition of unity); r_hat only sets the efficiency.
- **Same replicate (rule C, optional):** rho from `mis.npy` / `production-mis.npy`.
- **Then report:** band ESS per treatment (rows / parents / distinct states) against 1,000; D0' band masses from rule B
  against production alone; northern masses with a seed-bootstrap interval over both techniques.
- **Predictions to test (P5, from `DESIGN.md`):** D2 >= 1,000 in 35-30, 30-25 and 25-20 S; D4 30-25 S 0.8k-2.5k, 35-30 S
  0.6k-1.5k; D3 35-30 S and 30-25 S 0.5k-1.5k. **Where D3 (or D4) is short, fly more descents per supplement parent** (exact;
  the measurement shows D3 linear in descents); no new core run is needed for that.
- Cost to end of flight (its own rate): all 1.6M rows at 64 rows per parent is about 4-6 h at 14 threads and about 45 GB;
  a fixed every-k-th-row subset is valid. The Mac had 25 GiB free at staging.

## 6. Cost actually used

deskstar: preflight 44a979f5 (light: nice, 8 threads, 11 min); job b6389957 waited 11 h 56 min for the drift chain (01:45Z-13:41Z,
no pre-emption), then 6 h 47 min under the heavy lock (13:41Z-20:28Z): build and tests 2.5 min, gates 3.5 min, flag-off 6.5 min,
flag-on 22 min, 16 seeds x 21.5-24 min. Peak cgroup memory 35 GiB of 36, no OOM. deskstar disk 34 GB in the job dir
(left in place: `J/b6389957-…/runs/`, final.npy etc. of all seeds). Mac: 1.4 GB staged.

## 7. Deviations and limits

- The 1,000 target under D2-D4 is defined on impacts; core can only measure 00:11 counts. Whether each D2-D4 band reaches
  1,000 is open until end of flight flies the supplement (P5 are predictions, not results).
- Waypoints only (99.8 % of the posterior); free, descent-climb and repro have no supplement.
- The northern mass under rule B rests mainly on the 16 supplement seeds' mode probabilities (16 against run J's 24).
- The drift chain ended at 13:41Z, not about 12:00Z on 18 Oct as planned; nothing was pre-empted.
