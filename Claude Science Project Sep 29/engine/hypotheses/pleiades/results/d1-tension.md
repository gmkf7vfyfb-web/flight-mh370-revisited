# Deliverable 1: two-dimensional tension between H and the unconditional posterior (PROVISIONAL)

2026-10-08, Pléiades module. Script: `prepare/d1_tension.py`. Numbers: `d1-tension-sub5.csv` (primary),
`d1-tension-sub1.csv` (resolution check). This replaces the one-dimensional comparison in brief §4.

**The conditional PDF and these tension numbers are one result. Neither is quoted without the other.**

## Result

| R (NM) | ln R | ln S | unconditional mass in conditional HDR | conditional mass in unconditional HDR | mode shift (NM) | mean shift (NM) | conditional HDR (10³ km²) | unconditional HDR (10³ km²) |
|---|---|---|---|---|---|---|---|---|
| 7.5 | +0.17 | −1.11 | 6.8 % | 63 % | 190 | 157 | 7.1 | 26.8 |
| 15 | +0.13 | −1.08 | 6.4 % | 64 % | 170 | 157 | 9.1 | 36.4 |
| 30 | +0.03 | −1.09 | 5.8 % | 55 % | 180 | 158 | 13.8 | 59.2 |
| 60 | −0.13 | −1.02 | 5.3 % | 61 % | 174 | 155 | 21.4 | 114.1 |
| 103.4 | −0.32 | −0.90 | 5.1 % | 67 % | 165 | 150 | 29.0 | 200.4 |

R is the declared descent reach from the 00:19:37 position (end of flight owns the real kernel).
HDRs are 90 %. Modes: unconditional about 37.1–37.4°S 89.4–89.8°E; conditional about 35.2–35.5°S
92.2–92.4°E.

1. **H relocates the estimate by about 150–160 NM (mean) and 165–190 NM (mode)**, north-east along the
   arc, at every descent reach. That is the headline, and it is stable to within ±1.3 NM (mean) and
   ±10 NM (mode) between the two core resolutions.
2. **The overlap is one-sided.** Only 5–7 % of the unconditional mass lies inside the conditional's HDR.
   55–67 % of the conditional mass lies inside the unconditional's HDR. The conditional sits in the
   unconditional's thin north-eastern tail, not in its bulk. (The second number moves by up to
   12 points with core resolution at R ≤ 30 NM; the first by under 0.2.)
3. **The conditional HDR is narrow because H is narrow, not because the two agree.** 7,100–29,000 km²
   against 26,800–200,400 km² unconditional. Its width is bounded by about H's own 90 % HDR from
   transport alone (28,768 km²): below it for R ≤ 60 NM, and equal to it within 1 % at R = 103.4 NM
   (28,983 km²). Brief §2: a narrow conditional is not precision.
4. **Evidence.** The Bayes ratio R = P(D_H | flight) / P(D_H | flat prior over the grid) is near one,
   e^+0.17 to e^−0.32. It depends on the prior volume (A = 439,028 km², ±100 NM of the arc over the
   grid's along-arc span) and so says only that the flight posterior is about as compatible with the
   Pléiades positions as an impact placed at random in that box. **Suspiciousness ln S** (Handley &
   Lemos 2019), which cancels the prior volume, is −0.9 to −1.1 at every R: a consistent, moderate
   tension. No p-value is attached; the Gaussian calibration it needs does not hold for these
   truncated, non-Gaussian fields.

**Against brief §4.** The 1-D comparison measured something different: how far the
transport-inferred source modes sit beyond the unconditional 90 % *bound* (5–35 NM), with along-arc
impact latitudes set against off-arc source latitudes. The 2-D mode-to-mode shift of 165–190 NM is the
quantity the brief's other figure points at — the clusters sit 121–166 NM north of the reference
median — and is consistent with it. The sign in §4 was right; its 5–35 NM was never a displacement.

## Limits, carried with every number above

- Unconditional = `no-exhaustion-prior`, which **fails split-half** (0.9020 against 0.924). Its pooled 0.25°
  map is the 00:19:37 position, not the impact; no replicate spread. Direction-robust, magnitude unconverged.
- Descent is a declared uniform-disk sweep, not end of flight's distribution.
- H = the prior work's equal-prior three-family mixture grid, unnormalised 10 km kernel (brief §9);
  per-family cell values were not archived, so `ocean-model` is not yet marginalised separately. Rating-5
  objects only. No COSMO-SkyMed.
- Everything is truncated to the grid (±100 NM); 95.3–97.7 % of the unconditional mass lies inside it.
- Searched areas are not applied.

These numbers will be recomputed when the module's own normalised likelihood (deliverable 3) and real
impact samples exist. Until then they bound the module; they are not its answer.
