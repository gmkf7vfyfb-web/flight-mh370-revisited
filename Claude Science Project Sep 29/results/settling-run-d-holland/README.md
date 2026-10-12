# Where the wreckage is on the seabed under the Holland readings: end of flight's H1/H2 sweep on core run D

Ocean settling, 12 Oct 2026 (~01:45Z). This is overnight plan step 4 (architecture 00:05Z): settling's scoring of
`end-of-flight/next-run-d-he/`, the "make H1/H2 estimable" sweep. Samples: `mh370-exchange/settling/next-run-d-he/` (README, SHA256SUMS,
READY).

**PROVISIONAL, NOT CONVERGED.** Core run D's split-half is below its floor in 3 of 4 strata.

**Labels** (from end of flight's note, `results/eof-holland-sweep-run-d-oct11/`):
- piloted rapid descent to 40,000 ft/min with unloading to -1.0 g;
- INTERIM pitch-down;
- in-flight structural outcome PROVISIONAL (P(breakup) 0.93 / 0.88 under H1 / H2, an upper-side estimate);
- the survival factor is primary, as adopted by architecture 20:55Z;
- P(left) = 0.8 PROVISIONAL;
- the breakup table is PROVISIONAL;
- **breakup rows are settled from the intact impact point** (gap G-bf): settling has no fragment-field input;
- **A1 under H1/H2 is a COVERAGE GAP** (136 / 59 effective impacts).

## Figures

- `settling-seabed-wreckage-run-d-holland-core.{png,pdf}`: the five standard 00:19 options.
- `-family`: A1 / A2 / B by the five options.
- `-sens`: H1 and H2, each as reported, with breakup before 00:19:37 allowed (no survival factor), and with contact speed ≤ 212 m/s.

## Method

- **Row mass.** End of flight's `holland_sweep_summary.py` is reproduced exactly:
  m_i = P_s / K_s × w_i / Σw × exp(ln L_i + lag density (H1) + unpowered) × (1 − P(breakup by 00:19:37)).
  - The strata use the summary's core P(family): 0.594 / 0.235 / 0.153 / 0.019.
  - **Per-seed ln Z equals the summary's in all 16 seeds × 5 options × 2 versions (difference 0.0; asserted).** The effective impacts equal
    end of flight's: H1 4,690, H2 2,234; A1 136 / 59.
- **Resample.** Each product is a systematic resample over every row of the 16 seeds: 40,000 draws for all rows, 20,000 per family. There
  are 30 products in one shared table of 563,649 impacts and 669,925 draws. Each impact gets one settling draw on the real ocean
  (hypothesis/settling 9330d4c), and the output is the mass-weighted settled density. Grid 0.02°, Gaussian 0.1°, HPD; authalic areas.
- **Compute.** Prep 6.5 min at 1 thread; settling pass 14.8 min at 2 threads; both outside the lock (overnight plan).

## Areas (thousand km²)

| product | row ESS (Kish) | share of option | 90 % impact, all rows | 90 %: resampled impacts → seabed | settling adds | 50 %: → seabed | settled offset p50 / p90 / p99 (km) | afloat mass | estimable |
|---|---|---|---|---|---|---|---|---|---|
| 00:19 Held Out | 6.38 M | — | 574.3 | 551.8 → 553.3 | +0.28 % | 84.7 | 0.41 / 4.46 / 21.63 | 17.0 % | yes |
| 00:19 Held Out · A1 | 784,077 | 13 % | 361.9 | 356.5 → 357.4 | +0.25 % | 56.6 | 0.33 / 2.76 / 20.51 | 18.7 % | yes |
| 00:19 Held Out · A2 | 2.84 M | 33 % | 639.8 | 596.6 → 599.2 | +0.43 % | 96.8 | 0.39 / 4.15 / 21.90 | 17.4 % | yes |
| 00:19 Held Out · B | 2.99 M | 53 % | 536.8 | 496.0 → 498.2 | +0.44 % | 71.3 | 0.47 / 4.85 / 21.85 | 16.4 % | yes |
| 00:19 R600 BTO Only | 8.38 M | — | 319.3 | 311.4 → 312.2 | +0.25 % | 63.2 | 0.42 / 4.59 / 22.47 | 17.0 % | yes |
| 00:19 R600 BTO Only · A1 | 982,984 | 12 % | 223.9 | 212.9 → 213.5 | +0.30 % | 38.7 | 0.33 / 2.78 / 21.09 | 18.8 % | yes |
| 00:19 R600 BTO Only · A2 | 3.75 M | 33 % | 373.2 | 355.9 → 357.1 | +0.33 % | 67.1 | 0.40 / 4.41 / 22.73 | 17.2 % | yes |
| 00:19 R600 BTO Only · B | 4.01 M | 56 % | 264.4 | 256.1 → 256.8 | +0.29 % | 53.1 | 0.47 / 5.02 / 22.49 | 16.4 % | yes |
| 00:19 R600 BTO + Raw BFO | 190,237 | — | 227.4 | 226.1 → 226.6 | +0.23 % | 42.9 | 0.41 / 4.51 / 21.68 | 17.1 % | yes |
| 00:19 R600 BTO + Raw BFO · A1 | 21,623 | 15 % | 90.3 | 90.7 → 91.4 | +0.81 % | 13.7 | 0.33 / 2.42 / 20.39 | 19.3 % | yes |
| 00:19 R600 BTO + Raw BFO · A2 | 80,257 | 26 % | 268.9 | 266.6 → 267.5 | +0.32 % | 45.9 | 0.38 / 4.23 / 21.75 | 17.4 % | yes |
| 00:19 R600 BTO + Raw BFO · B | 102,661 | 59 % | 181.4 | 177.8 → 178.3 | +0.26 % | 34.0 | 0.46 / 4.97 / 22.00 | 16.5 % | yes |
| 00:19 Holland H1 | 4,690 | — | 105.3 | 104.5 → 105.1 | +0.54 % | 22.9 | 0.36 / 4.17 / 21.69 | 17.2 % | yes |
| 00:19 Holland H1 · A1 | 136 | 12 % | 52.7 | 52.9 → 53.8 | +1.69 % | 10.2 | 0.33 / 2.48 / 20.35 | 19.0 % | **no (COVERAGE GAP)** |
| 00:19 Holland H1 · A2 | 4,981 | 37 % | 84.2 | 84.0 → 84.5 | +0.57 % | 17.0 | 0.35 / 4.31 / 22.04 | 17.0 % | yes |
| 00:19 Holland H1 · B | 3,520 | 51 % | 82.9 | 83.3 → 83.8 | +0.52 % | 19.4 | 0.37 / 4.44 / 21.80 | 17.0 % | yes |
| 00:19 Holland H1, breakup before 00:19:37 allowed | 4,338 | mass ×1.02 | 105.8 | 105.5 → 106.1 | +0.56 % | 23.2 | 0.36 / 4.19 / 21.70 | 17.2 % | yes |
| 00:19 Holland H1, impacts at or below 212 m/s | 4,765 | 86 % | 98.4 | 98.1 → 98.7 | +0.58 % | 19.0 | 0.37 / 4.47 / 21.90 | 16.8 % | yes |
| 00:19 Holland H2 | 2,234 | — | 112.4 | 112.0 → 112.6 | +0.55 % | 24.1 | 0.36 / 4.23 / 21.96 | 17.2 % | yes |
| 00:19 Holland H2 · A1 | 59 | 12 % | 56.2 | 56.1 → 56.9 | +1.41 % | 9.8 | 0.31 / 2.65 / 20.88 | 18.9 % | **no (COVERAGE GAP)** |
| 00:19 Holland H2 · A2 | 2,186 | 33 % | 85.5 | 85.3 → 85.7 | +0.46 % | 19.0 | 0.36 / 4.34 / 21.93 | 17.0 % | yes |
| 00:19 Holland H2 · B | 1,920 | 55 % | 104.9 | 104.7 → 105.6 | +0.80 % | 21.0 | 0.37 / 4.46 / 22.28 | 17.0 % | yes |
| 00:19 Holland H2, breakup before 00:19:37 allowed | 1,599 | mass ×2.48 | 103.4 | 103.4 → 104.3 | +0.84 % | 21.0 | 0.35 / 4.07 / 21.40 | 17.0 % | yes |
| 00:19 Holland H2, impacts at or below 212 m/s | 2,893 | 85 % | 110.5 | 110.6 → 111.3 | +0.65 % | 20.4 | 0.37 / 4.51 / 22.02 | 16.8 % | yes |


## What it shows

1. **H1 and H2 now have seabed PDFs.** The 90 % seabed area is 105,000 km² (H1) and 113,000 km² (H2). That is about one fifth of Held
   Out (553,000) and one third of R600 BTO Only (312,000), so the Holland readings concentrate the impact along the 7th arc.
2. **Settling adds 0.2-0.8 % to every estimable 90 % area.** Half the settled mass rests within 0.31-0.47 km of the impact and 90 % within
   2.4-5.0 km; p99 is 20-23 km. A1 has the tightest kernel (p90 2.4-2.8 km) and B the widest (4.4-5.0 km). The seabed PDF is the impact
   PDF to under 1 % in area, as in every earlier run.
3. **The survival factor and the speed cap move H1/H2 by at most 8 %.**
   - Allowing breakup before 00:19:37 moves H1 by +1 % (105 → 106) and moves H2 from 113 to 104, -8 % with a mass ratio of 2.48. That is
     end of flight's -0.91 nat.
   - Keeping only contact speeds ≤ 212 m/s gives H1 99 and H2 111, with 86 % / 85 % of the mass retained.
4. **By family under H1/H2:** A2 84 / 86 and B 84 / 106 thousand km². A1 has an area (54 / 57) but is NOT estimable: its effective
   impacts are 136 / 59, the coverage gap end of flight names.
5. **The latitude does not move with the 00:19 option**, as end of flight found. The H1/H2 regions lie inside the southern part of the
   Held Out and R600 regions, along the arc at about 36-40 °S.

## COVERAGE

- **(a) Feasible set:** as end of flight's note: piloted dives to about 39,000 ft/min, unloading to -1.0 g, speeds past VMO/MMO, and
  in-flight structural damage or breakup.
- **(b) Settling's reach:** every row that reaches the water as an intact impact. Two declared reach gaps:
  - **G-bf (in-flight breakup):** under H1/H2, 93 % / 88 % of the posterior mass breaks up in the air before contact. Settling treats each
    such row as an intact impact at end of flight's impact point and applies its energy-based breakup table. The real seabed field would
    be a ballistic fragment field spread along the descent. Its extent is unknown until end of flight's fragment-field columns exist; the
    descent's horizontal scale (km) is the likely order. NOT CLOSED, and named in every footnote.
  - **Attitude-dependent breakup:** declared, as on run C.
  - No impact fell outside the ocean window (0 refused).
- **(c) Proposal coverage:**
  - row ESS 4,690 (H1) and 2,234 (H2) for all rows;
  - per family A1 136 / 59 (**GAP**), A2 4,981 / 2,186, B 3,520 / 1,920;
  - Held Out 6.4 M, R600 BTO Only 8.4 M, R600 BTO + Raw BFO 190,237.
  - Distinct impacts in the 40,000-draw resample are 21,108 (H1) and 15,392 (H2): repeated draws carry the weight concentration.
  - The ESS table above is per option, family and version.
- **Bounds:** settling's breakup table, sinking classes and ocean products are as for core (b) and run C (`breakup.toml`;
  `results/settling-references.md`).

## Reproduce

    python3 wf_rows.py prep   <EoF smoke dir> mh370-exchange/end-of-flight/next-run-d-he <summary/holland-sweep-summary.json> nrd
    SETTLING_FIELD_IN=field/nrd_impacts.f64 SETTLING_FIELD_OUT=field/nrd_elements.f64 cargo test --release -p mh370-hypotheses settling::tests::wreckage_field -- --ignored
    python3 wf_rows.py render <EoF smoke dir> <core reference-289 run.json> nrd run-d-holland 9330d4c 468239ea core|family|sens

- Ocean Settling
