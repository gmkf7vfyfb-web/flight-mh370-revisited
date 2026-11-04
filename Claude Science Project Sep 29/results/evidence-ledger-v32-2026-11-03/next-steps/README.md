# Evidence ledger — next steps (4 November 2026)

Status: exploratory, not ruled. Figure: `evidence-ledger-next-steps.png`. Code: `next_steps.py` (reproduces every number here).

## Step 1. What makes up the satellite result (indicative)

The ledger could not split core, because run J carries all core data together. The early-October nested runs add the data in steps.
They use the Davey flight model and the early fuel model, not run J, so these numbers are a guide only.
Bits along the 7th arc, 30 NM bins, 40.25–19.9 S, against uniform along the arc:

| step | bits | 90 % arc length (NM) |
|---|---|---|
| aircraft performance and fuel alone (on the arc) | 0.15 | 1282 |
| + satellite timing to 00:11 | 1.11 | 810 |
| + satellite frequency to 00:11 | 1.86 | 420 |
| + 00:19 data | 2.07 | 360 |
| satellite timing alone, all epochs, no fuel model (separate run) | 1.33 | 600 |

What it shows (STE100):
1. Aircraft performance and fuel alone narrow the arc very little (0.15 bits).
2. The satellite timing gives the largest part.
3. The satellite frequency adds about 0.75 bits, about 40 % of the total. The frequency model is the part where our curve and the
   Davey curve do not agree (results/davey-bto-only-2026-10-18). So a large part of the core precision rests on the least certain model.
4. The 00:19 data add about 0.2 bits.

## Step 2. A check with synthetic cases (no new compute)

The staged end-to-end calibration (30 cases, finished 21 Oct 2026, results on deskstar) puts a true wreck at a known place, makes all the
data from it, and runs the full method. From its stored histograms we measure how much drift + searched areas add to core,
H(core) − H(all), on 0.25° impact-latitude bins. Drift is scored in 8 cases only (the data-only rule). Same measure for the real data:

| case | synthetic search found the wreck | 00:19 held out | 00:19 BTO only | both BFOs as recorded | Holland bias added |
|---|---|---|---|---|---|
| 3008 | yes | +0.33 | +0.27 | +0.20 | +0.20 |
| 3009 | yes | +0.33 | +0.28 | +0.03 | +0.04 |
| 3010 | yes | +0.33 | +0.28 | +0.31 | +0.23 |
| 3015 | no | -0.20 | -0.18 | -0.34 | +0.11 |
| 3018 | no | -0.30 | -0.29 | +0.55 | -0.17 |
| 3021 | no | +0.01 | -0.10 | +0.95 | -0.13 |
| 3027 | yes | +0.75 | +0.57 | +0.62 | +0.48 |
| 3029 | no | +0.06 | -0.02 | +0.23 | +0.11 |
| **real data** | no | **-1.10** | **-1.16** | **-1.39** | **-1.55** |

What it shows (STE100):
1. When the synthetic search finds the wreck, the other evidence adds 0.3–0.75 bits.
2. When the synthetic search does not find it, as in reality, the other evidence changes the result by −0.30 to +0.06 bits. So a no-find
   can make the result wider even when every model is correct. A negative value alone is not a sign of a conflict.
3. With the real data the loss is −1.10 bits (−1.16 to −1.55 with the 00:19 data used). This is more than in any synthetic case.
   It agrees with the disagreement test (about 2 sigma).
4. Limits: only 8 cases, from 4 different true flights (cases 3008, 3009, 3015, 3018, 3027 share one flight). No case is like the real one,
   where the satellite peak is on searched ground and the wreck is not found. So this is a weak check (about 1 in 9), not a proof.

Coverage (does the method claim too much?): the true latitude was inside the 90 % region in 29/30 cases for core,
29/30 for core + searched areas, 8/8 for core + drift and
8/8 for all evidence. Provisional: calibration at reduced depth (30 cases, 16 distinct truth flights).

## Step 3. Hydroacoustics

No hydroacoustic likelihood exists yet; the module is still building the detectability maps. So no column is added.
For scale only: the hydroacoustic value-of-information test (the chart Pete shared on 3 Nov 2026: flat prior along the arc, 41–20 S,
Cape Leeuwin direction error 0.66°; exploratory, unchecked) gave 3.6–4.7 bits for one array direction and 7.6–7.9 bits for all eight
sites, IF a detection exists. Its bins and arc span differ from the ledger, so the numbers are not exactly comparable; but they are of the
same size as the whole satellite result (about 2.3 bits) or larger. Hydroacoustics is the only data type that could give the independent
confluence the ledger looks for. It stays predictive-only.

## Proposed next runs (need Pete's approval of deskstar time)

### A. Satellite result split on the run J model
- **What:** two new runs on the run J flight model (waypoint routes, which carry 0.998 of the mass): (1) aircraft performance and fuel with
  no satellite data, (2) satellite timing only to 00:11. Run J itself gives timing + frequency.
- **Why:** step 1 uses early runs with a different flight model. The paper needs the split on the same model as the results.
- **What you will see:** the same chart as step 1, panel a, with run J numbers.
- **What it will tell us:** how much of the 2.3 bits of the core comes from timing, from frequency and from fuel, on the published model.
- **What it will not tell us:** whether the frequency model is right. It only shows how much the result depends on it.
- **Time:** smoke test about 0.5 h, then about 1.5 h per run at 16 × 3.5 M: about 3.5–4 h on deskstar.

### B. More synthetic cases, with all four combinations stored
- **What:** change the histogram step so it also stores core + drift and core + searched areas, and keeps the per-row file; then run
  cases 3031–3050 on the present pool.
- **Why:** step 2 has only 8 cases with drift, from 4 flights. The per-row files were deleted to save disk, so the 30 cases cannot be re-scored.
- **What you will see:** panel b of the next-steps chart with about 14 drift cases, and the searched-areas effect alone for every case.
- **What it will tell us:** whether the real loss of 1.1 bits is still beyond all synthetic cases.
- **What it will not tell us:** cases like the real one are rare in the pool. A targeted test (select synthetic cases by their data, where the
  satellite peak is on searched ground) is a separate design step.
- **Time:** about 11 h on deskstar (same pool, same seeds, additive).
