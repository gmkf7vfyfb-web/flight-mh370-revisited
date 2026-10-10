# Correlated Pléiades / COSMO-SkyMed transport errors: sensitivity on core (b)

10 Oct 2026, Pléiades module (`prepare/rho_sensitivity.py`). Labels: core (b) NOT converged; two-tank bookkeeping only; reference
existence constraint `unpowered`; strata re-weighted by the 00:19 evidence (end of flight's `+alive` key); PROVISIONAL-OVERNIGHT.

**Input.** Ocean transport measured the 13 d / 15 d error correlation between nearby undrogued drifters
(`results/ocean-transport-error-pairs.md`):
- central ρ ≈ 0.2-0.3 at 40-80 km separation;
- upper sensitivity 0.5;
- 0.8 not supported.

**Method.**
- Bivariate normal per component between each Pléiades object and each COSMO contact. The variances are the hook's OU variances, and
  the windages of object and contact are independent. This is `audit_closeup`'s joint, on the module's 0.05° grid over 86-98 E, 40-30 S.
- That box holds all of the conditional: share 1.000.
- At ρ = 0 it reproduces the hook's product: the sd of the ln ratio is 2e-5, and the 90 % areas equal the close-ups'.
- Tension columns here are computed inside the box. Compare them across ρ only; the full-grid values are in the close-ups.

After Phase 2 + Bluefin-21 + OI 2018 + 2025-26 (grade C), Pléiades + all four COSMO-SkyMed contacts, GLORYS12 + GlobCurrent equal weight:

| 00:19 option | ρ | 50 % km² | 90 % km² | mean under H | searches leave, under H | ln S (box) | mean shift NM (box) |
|---|---|---|---|---|---|---|---|
| 00:19 Held Out | 0.00 | 9,747 | 71,925 (+0 %) | 35.25 S 91.41 E | 0.557 | -0.02 | 121 |
| 00:19 Held Out | 0.25 | 12,712 | 81,518 (+13 %) | 35.29 S 91.42 E | 0.559 | -0.06 | 119 |
| 00:19 Held Out | 0.50 | 15,442 | 89,321 (+24 %) | 35.33 S 91.43 E | 0.556 | -0.08 | 117 |
| 00:19 R600 BTO Only | 0.00 | 12,668 | 53,594 (+0 %) | 35.78 S 92.19 E | 0.341 | -1.67 | 165 |
| 00:19 R600 BTO Only | 0.25 | 13,274 | 59,578 (+11 %) | 35.85 S 92.22 E | 0.357 | -1.53 | 162 |
| 00:19 R600 BTO Only | 0.50 | 13,735 | 64,665 (+21 %) | 35.91 S 92.24 E | 0.368 | -1.42 | 159 |
| 00:19 R600 BTO + Raw BFO | 0.00 | 10,730 | 47,744 (+0 %) | 35.73 S 92.09 E | 0.303 | -1.36 | 155 |
| 00:19 R600 BTO + Raw BFO | 0.25 | 11,359 | 54,267 (+14 %) | 35.79 S 92.09 E | 0.317 | -1.25 | 152 |
| 00:19 R600 BTO + Raw BFO | 0.50 | 11,750 | 59,720 (+25 %) | 35.85 S 92.10 E | 0.325 | -1.16 | 149 |

**Findings.**
1. **At the measured central ρ = 0.25 the 90 % region widens by 11-14 %. At the upper sensitivity ρ = 0.5 it widens by 21-25 %.**
   The mean moves ≤ 0.12° south and ≤ 0.03° east.
2. The independent-error hook (ρ = 0) is therefore narrower than the transport data support. The headline should carry ρ = 0.25 as its
   central value, or at least show it beside ρ = 0. **This is a choice for Pete** (brief: a scientific choice that changes the headline).
3. Tension changes little with ρ: ln S rises by ≤ 0.25 and the mean shift falls by ≤ 6 NM.
