# Pléiades module on core run I: H-conditional 00:19 two-factor table (D0-D5 x C1 / C2 silent / total q = 1/3)

Pléiades module. Columns: `mh370-exchange/pleiades/run-i/` (per-stratum READY; top-level READY when all four strata are built).
Scripts: `prepare/build_columns.py`, `prepare/score_runi_summary.py` (end of flight's own D x C weights from
`smoke/option_table_0019.py`, reused term by term; survival factor throughout; C2 silent primary), `prepare/runi_note.py`.

**Labels:**
- **conditional on H**; no identity likelihood; no Bayes factor or P(H | data);
- core run I NOT converged (core waypoints split-half floor 0.916);
- end-of-flight physics PROVISIONAL: piloted-turn model, INTERIM pitch-down, push-over and Boeing sequence, in-flight structural
  outcome (end of flight's run I label list applies in full);
- Pléiades rating 5 + all four COSMO-SkyMed contacts, one debris field;
- D4 is named per the 18:15Z wording rule ("Holland transient bias added").
- Strata mixed by core P(family): next-i-waypoints 0.9982, next-i-free 0.0011, next-i-repro-radar 0.0004, next-i-descent-climb 0.0002. before seabed search.

## Primary: competing-causes total q = 1/3 (C2 silent), proposed headline setting, before seabed search

| D | cause | ESS under H (without H) | mean under H | shift NM | ln S (p) | 90 % km² under H (without H) | ln E[L_H] vs D0 | A1 ESS under H |
|---|---|---|---|---|---|---|---|---|
| D0 held out | total q=1/3 (C2 silent) | 53,022 (823,551) | 35.48 S 91.97 E | 109 | -1.38 (0.16) | 68,890 (146,547) | +0.00 | 11,672 |
| D1 R600 BTO | total q=1/3 (C2 silent) | 64,732 (833,289) | 35.58 S 92.16 E | 127 | -1.65 (0.12) | 58,795 (112,388) | -0.23 | 12,559 |
| D2 R600 BTO + R600 BFO | total q=1/3 (C2 silent) | 5,424 (63,778) | 35.56 S 92.17 E | 117 | -1.61 (0.13) | 47,387 (92,039) | -0.14 | 1,279 |
| D3 R600 BTO + both BFOs (H2 data) | total q=1/3 (C2 silent) | 209 (2,176) | 35.63 S 92.36 E | 139 | -1.07 (0.03) | 11,593 (27,089) | -0.22 | 38 |
| D4 R600 BTO + both BFOs, Holland transient bias added (H1 data) | total q=1/3 (C2 silent) | 959 (10,872) | 35.59 S 92.37 E | 140 | -1.60 (0.09) | 22,089 (41,322) | -0.25 | 148 |
| D5 R600 BTO + R600 BFO + R1200 BFO with offset | total q=1/3 (C2 silent) | 360 (4,070) | 35.62 S 92.37 E | 134 | -1.35 (0.05) | 18,294 (33,634) | -0.22 | 46 |

## Reading (from the tables above; mixture = waypoints 0.9982)
1. **Under H, every D x C cell moves to about 35.5-35.6 S, 92.0-92.4 E.** This is 109-140 NM north-east of the flight-only PDF, which
   on run I sits near 37.1-37.4 S (end of flight's 17:05Z note).
2. **Tension is moderate and stronger than on run D-he.** In the primary column ln S is −1.07 to −1.65, with p 0.03-0.16; D3 has the
   smallest p (0.03). The conditional PDF under H is therefore partly a symptom of tension and must be read with it.
3. **H barely separates the 00:19 treatments.** ln E[L_H] is within −0.25 to 0 of D0 in the primary column. H does not pick D3, D4
   or D5 (Holland's H2 and H1 data, and Pete's offset variant).
4. **D3, D4 and D5 under H are below the 1,000 gate** (209 / 959 / 360). A1 under them has 38 / 148 / 46. See COVERAGE.

## Each cause separately (proposed setting, before search)

| D | cause | ESS under H (without H) | mean under H | shift NM | ln S (p) | 90 % km² under H (without H) | ln E[L_H] vs D0 | A1 ESS under H |
|---|---|---|---|---|---|---|---|---|
| D0 held out | C1 | 52,527 (817,767) | 35.48 S 91.97 E | 109 | -1.38 (0.16) | 68,840 (146,199) | -0.00 | 11,514 |
| D0 held out | C2 silent | 37,079 (343,057) | 35.43 S 92.25 E | 99 | -0.81 (0.24) | 72,448 (214,921) | +0.29 | 15,343 |
| D1 R600 BTO | C1 | 64,112 (827,660) | 35.58 S 92.16 E | 127 | -1.65 (0.12) | 58,794 (112,164) | -0.23 | 12,316 |
| D1 R600 BTO | C2 silent | 36,101 (350,356) | 35.54 S 92.50 E | 123 | -0.98 (0.22) | 49,110 (149,635) | +0.12 | 17,991 |
| D2 R600 BTO + R600 BFO | C1 | 5,398 (63,592) | 35.56 S 92.16 E | 117 | -1.62 (0.13) | 47,411 (91,984) | -0.14 | 1,269 |
| D2 R600 BTO + R600 BFO | C2 silent | 1,204 (10,251) | 35.46 S 92.42 E | 110 | -0.95 (0.22) | 25,086 (63,126) | +0.36 | 313 |
| D3 R600 BTO + both BFOs (H2 data) | C1 | 208 (2,171) | 35.63 S 92.36 E | 139 | -1.07 (0.03) | 11,517 (27,064) | -0.22 | 38 |
| D3 R600 BTO + both BFOs (H2 data) | C2 silent | 65 (275) | 35.54 S 92.57 E | 131 | -0.87 (0.08) | 3,294 (9,463) | -0.12 | 15 |
| D4 R600 BTO + both BFOs, Holland transient bias added (H1 data) | C1 | 956 (10,845) | 35.59 S 92.37 E | 140 | -1.60 (0.09) | 22,038 (41,272) | -0.25 | 147 |
| D4 R600 BTO + both BFOs, Holland transient bias added (H1 data) | C2 silent | 191 (1,426) | 35.52 S 92.50 E | 132 | -0.74 (0.11) | 8,625 (22,011) | +0.16 | 35 |
| D5 R600 BTO + R600 BFO + R1200 BFO with offset | C1 | 358 (4,060) | 35.62 S 92.37 E | 134 | -1.35 (0.05) | 18,245 (33,585) | -0.23 | 46 |
| D5 R600 BTO + R600 BFO + R1200 BFO with offset | C2 silent | 63 (833) | 35.48 S 92.57 E | 139 | -0.25 (n/e) | 4,401 (14,771) | +0.21 | 22 |

## GLORYS12 only at ρ 0.25 (headline in force), total q = 1/3, before search

| D | cause | ESS under H (without H) | mean under H | shift NM | ln S (p) | 90 % km² under H (without H) | ln E[L_H] vs D0 | A1 ESS under H |
|---|---|---|---|---|---|---|---|---|
| D0 held out | total q=1/3 (C2 silent) | 50,683 (823,551) | 35.47 S 92.04 E | 112 | -1.37 (0.16) | 63,392 (146,547) | +0.00 | 10,752 |
| D1 R600 BTO | total q=1/3 (C2 silent) | 61,460 (833,289) | 35.56 S 92.23 E | 130 | -1.63 (0.13) | 54,473 (112,388) | -0.22 | 10,676 |
| D2 R600 BTO + R600 BFO | total q=1/3 (C2 silent) | 5,142 (63,778) | 35.52 S 92.26 E | 122 | -1.61 (0.13) | 44,795 (92,039) | -0.13 | 1,075 |
| D3 R600 BTO + both BFOs (H2 data) | total q=1/3 (C2 silent) | 176 (2,176) | 35.63 S 92.42 E | 141 | -0.91 (0.01) | 9,605 (27,089) | -0.15 | 33 |
| D4 R600 BTO + both BFOs, Holland transient bias added (H1 data) | total q=1/3 (C2 silent) | 846 (10,872) | 35.59 S 92.43 E | 142 | -1.50 (0.09) | 19,414 (41,322) | -0.20 | 125 |
| D5 R600 BTO + R600 BFO + R1200 BFO with offset | total q=1/3 (C2 silent) | 327 (4,070) | 35.61 S 92.42 E | 137 | -1.25 (0.05) | 15,717 (33,634) | -0.18 | 32 |

## After the searches (after /Users/pete/Downloads/mh370-exchange/searched-areas/run-i), total q = 1/3, proposed setting

| D | cause | ESS under H (without H) | mean under H | shift NM | ln S (p) | 90 % km² under H (without H) | ln E[L_H] vs D0 | A1 ESS under H |
|---|---|---|---|---|---|---|---|---|
| D0 held out | total q=1/3 (C2 silent) | 31,135 (328,918) | 35.37 S 91.87 E | 69 | -0.56 (0.26) | 72,907 (257,923) | +0.00 | 3,252 |
| D1 R600 BTO | total q=1/3 (C2 silent) | 42,142 (372,244) | 35.56 S 92.22 E | 104 | -1.07 (0.19) | 64,426 (188,607) | -0.32 | 6,284 |
| D2 R600 BTO + R600 BFO | total q=1/3 (C2 silent) | 4,318 (22,847) | 35.53 S 92.24 E | 66 | -0.71 (0.21) | 51,513 (162,128) | -0.14 | 644 |
| D3 R600 BTO + both BFOs (H2 data) | total q=1/3 (C2 silent) | 115 (656) | 35.68 S 92.55 E | 81 | -0.03 (0.22) | 7,644 (30,278) | +0.11 | 25 |
| D4 R600 BTO + both BFOs, Holland transient bias added (H1 data) | total q=1/3 (C2 silent) | 460 (2,865) | 35.61 S 92.62 E | 73 | -0.23 (0.20) | 16,756 (54,342) | +0.11 | 124 |
| D5 R600 BTO + R600 BFO + R1200 BFO with offset | total q=1/3 (C2 silent) | 143 (526) | 35.65 S 92.61 E | 62 | -0.12 (0.15) | 12,526 (42,024) | +0.11 | 5 |

**Close-ups** (colour and seabed, D0-D5, after the official searches, total q = 1/3): `closeups/` (prepare/runi_closeups.py; maps from per-impact columns; stats in `closeups/closeup-runi-stats.csv`). D3, D4 and D5 are labelled NOT ESTIMABLE on the charts.

## COVERAGE
- **(a) Feasible set and (b) model reach:** end of flight's run I README and COVERAGE apply unchanged; these columns add no sampling.
  Carried gaps: stepped shapes not eligible for push-over; INTERIM pitch-down; core run I not converged.
- **(c) Proposal coverage under H** (effective impacts, proposed setting, before search). Cells and families **below the 1,000 gate (GAP)**:
  A1 under D2 x C2 silent (313); D3 x C1 (208); A1 under D3 x C1 (38); D3 x C2 silent (65); A1 under D3 x C2 silent (15); D3 x total q=1/3 (C2 silent) (209); A1 under D3 x total q=1/3 (C2 silent) (38); D4 x C1 (956); A1 under D4 x C1 (147); D4 x C2 silent (191); A1 under D4 x C2 silent (35); D4 x total q=1/3 (C2 silent) (959); A1 under D4 x total q=1/3 (C2 silent) (148); D5 x C1 (358); A1 under D5 x C1 (46); D5 x C2 silent (63); A1 under D5 x C2 silent (22); D5 x total q=1/3 (C2 silent) (360); A1 under D5 x total q=1/3 (C2 silent) (46).
- These gaps arise because end of flight's proposal targets the 00:19 data, not the Pléiades-compatible end states (near 35.5 S
  92.3 E). The fix is end of flight's to choose: more seeds, or a defensive-mixture component toward those end states, with exact
  re-weighting (the module's L_H surface is available as a proposal density). Every product that uses a GAP cell must name it.
- **Parameter bounds:** windage 0-5 % U10; transport error ~95-120 km per component at 15 d (measured); ρ 0.25 headline (measured
  0.07-0.41), 0 / 0.5 available via `reader.load_rho`; GlobCurrent product-relative offset 0.60-0.75 % U10 (drift audit F1).
