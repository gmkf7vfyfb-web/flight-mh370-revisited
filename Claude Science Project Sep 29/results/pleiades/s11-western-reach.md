# §11 — is the western lobe flight-reachable? (PROVISIONAL)

2026-10-08, Pléiades module. Script: `prepare/s11_western_reach.py`. Numbers: `s11-western-reach.csv`,
`s11-western-reach-context.json`.

## Answer

**The 00:19 flight and fuel posterior does not decide it. The descent reach does.** 35°S 91°E is
65 NM inside the 7th arc. The nearest core 00:19 cell with mass ≥ 1e-4 is 48 NM from it. Core 00:19
mass within 45 NM of it is 1.5e-6, within 60 NM 1.6 %, within 75 NM 10.9 %, within 105 NM 22.7 %.

Share of the H × flight mass (H transport compatibility times core impact density) in each region,
against a declared descent reach R from the 00:19 position:

| region | H transport alone | R = 7.5 | 15 | 30 | 45 | 60 | 80 | 103.4 NM |
|---|---|---|---|---|---|---|---|---|
| H 90% HDR, ≥ 30 NM inside arc | 38.1 % | 0.002 % | 0.03 % | 5.9 % | 19.0 % | 28.7 % | 35.4 % | 38.6 % |
| H 90% HDR, ≥ 50 NM inside arc | 20.5 % | 0 | 0 | 0.002 % | 1.1 % | 8.3 % | 16.0 % | 20.4 % |
| 35°S 91°E ± 0.5° box | 19.5 % | 0 | 0.003 % | 0.3 % | 3.3 % | 9.8 % | 17.4 % | 21.2 % |

- If the impact lies within about 15 NM of the 00:19 position, the western lobe is **unreachable**:
  under 0.03 % of the conditional mass survives there.
- At the 103.4 NM still-air glide bound the flight evidence removes **nothing** from the lobe; the
  lobe's share is the same as under transport alone.
- The H × flight mode stays at 35.2–35.4°S, 92.1–92.3°E, 10–15 NM inside the arc, for every R. The
  conditional's core is near the arc; it is the western residual that needs a glide.

So whether most of the residual mass under H disappears is a question for end of flight: what
weight the posterior puts on descents that carry the aircraft 30 NM or more north-west of its 00:19
position.

## Limits, carried with every number above

- Core posterior is `no-exhaustion-prior`, which **fails split-half** (0.9020 against 0.924). Its
  pooled 0.25° map is the **00:19:37 position, not the impact**; no replicate spread is available
  because per-seed `final.npy` files are not to hand. Read the table as direction-robust, magnitude
  unconverged.
- Descent is not modelled here. R is a declared sweep; the uniform-disk kernel is a stand-in for
  end-of-flight's impact distribution. 103.4 NM is a support bound, not a distribution.
- H transport compatibility is the prior work's three-family mixture grid, built with an unnormalised
  10 km kernel (brief §9). Per-family cell values were not archived.
- Searched areas are not applied.
