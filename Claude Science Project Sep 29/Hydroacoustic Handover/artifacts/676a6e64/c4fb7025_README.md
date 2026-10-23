# Pair G updates of the seven example charts (22 Oct 2026)

Hydroacoustic Module, graphics track "pair-g". PREDICTIVE, NOT CALIBRATED; caveats C1 (propagation slope misfit, +10.4/+7.4 dB per
octave at H01W/H08S) and C2 (coupling efficiency not calibrated; eta swept over four decades, F-35A upper anchor) apply to every number.
Source posterior: run J, 00:19 Held Out (D0'), dive probability p 0.5. Digitised data are labelled DIGITISED.

## The pair (G)

Cape Leeuwin H01W 00:52:04 UTC (DIGITISED Kadri 2024 Fig. 9 panel c; envelope matched filter M1b p 0.043; Kadri's "text time 00:52:03",
"caption time 00:54:30") x Diego Garcia South H08S 01:12:49 (DIGITISED panel e, raw, M1b p 0.039; the airgun-suppressed residual does not
keep it, p_B 0.30). Lag 1,245 s inside the predicted 809-1,536 s. 19 lag-consistent pairs against 8.8 expected, permutation p 0.019 over
36 receiver-pair tests: a chance level (a smallest p this low arises about half the time). Arc locus 33.6 S 94.5 E, implied impact
00:31:41. Coupling for P_D(both stations) = 0.5: eta = 0.069 = 330 x the F-35A anchor 2.1e-4.

Bearing caveat: the locus lies at 269.0 deg from H01W (1,812 km) and 144.8 deg from H08S (3,657 km) (WGS84, triad centroids; the brief
quoted 268.9 deg / 3,660 km). Kadri publishes 57 deg (text p. 9) or 306.18 deg (Table 1 caption) for the 00:52 signal; neither is within
37 deg of 269.0 deg. The nearest Table 1 bearing is 00:52:50 at 274.84 deg, 46 s later. The 57 deg ray never meets the arc; 306.18 deg
meets it at 25.7 S (locus D).

## Charts (PNG + PDF)

| # | file | what it shows |
|---|---|---|
| 1 | chart1-geometry-pair-g | receivers, paths to G with open/blocked status at the 33.5 S node, Kadri's 57 / 306.18 deg and the Table 1 274.84 deg rays, OHASISBIO sites, impact cloud, arc span searched |
| 2 | chart2-trajectory-pair-g | stored route after 18:22 + neighbourhood of G for the highest-weight impact within 150 km (impact 00:20:57, 11 min before 00:31:41) |
| 3 | chart3-hpd-maps-pair-g | composer HPD maps (core; core + drift) with A, B, D, E, F, G and the top 5 ranked pairs |
| 4 | chart4-bearings-pair-g | bearing rays from H01W with arc ranges R; H08S path to G |
| 5 | chart5-latitudes-pair-g | arc-crossing latitudes against the run J latitude density and Davey et al. (2016) Fig. 10.3 |
| 6 | chart6-neighbourhood-pair-g | three stored trajectories near G: highest weight, highest weight within 2 min of 00:31:41, closest |
| 7 | chart7-paths-track-speed-pair-g | run J paths with impact within 150 km of G against the rest; track and speed after 22:41 |

Tables: pair-g-loci.csv (loci, density, mass within 0.5 deg, HPD level at the point in both composer maps), pair-g-trajectories.csv,
pair-g-track-speed-bands.csv. Code: common.py, extract_seed.py (per-seed weights and per-parent sums), charts_pair_g.py.

## Key numbers

- Latitude density at G 0.031 per degree (5 % of the run J peak 0.57 at 37.15 S); mass within 0.5 deg of latitude 0.033; mass within
  150 km 0.061 (sample) / 0.045 (waypoints stratum, all 24 seeds).
- HPD level at G: 0.91 (core), 0.78 (core + drift). At D: 0.97 / 0.89.
- Within 150 km of G (waypoints stratum): weighted impact time 5/50/95 % 00:20:31 / 00:31:21 / 00:45:25; 0.181 of the weight within 2 min
  of 00:31:41; families A1 0.13, A2 0.28, B 0.59.
- Ranking track (graphics-2026-10-22/ranked/ranked_pairs.csv): G is rank 104 by lnLR (-6.23), rank 54 by p, bearing INCONSISTENT. Top 5
  by lnLR are all H08S x Perth Canyon 3315 secondary rows (lnLR -0.64 to -3.42), loci 36.5-37.2 S 89.6-90.6 E.
- Paths with impact within 150 km of G fly about 10 deg further east of south (median track 173-180 deg vs 185.5 deg) and 30-50 kt slower
  after 22:41 than the other paths (1,842 of 48,000 stored routes have f >= 0.5).

## COVERAGE

- Feasible set: inherited from run J (core + end of flight); this track adds no sampling. The end-of-flight labels of run J apply
  (provisional push-over, pitch-down, piloted turns; see end-of-flight README).
- Model reach: the arrival model is straight-line WGS84 geodesic at c = 1.482 km/s; no refraction or path lengthening. Path status uses the
  block 2 TL grid (KRAKEN, IMS) and the RAM-corrected IMOS table. OHASISBIO sites are not modelled (no recordings held).
- Proposal coverage: impact cloud and densities from searches geometry/sample.npz (waypoints seeds 1-8 stride 6 + northern supplement,
  Kish ESS 110k overall, 6.4k within 150 km of G). Trajectory charts use the waypoints stratum, all 24 seeds (0.998 of the mixture), 8.55 M
  rows within 150 km of G, Kish ESS 57k (13k for the 2-min time-consistent subset). Other strata and the supplement are not in charts 2, 6, 7.

### Gaps and their status

1. Routes and impacts are joined by POSITION at 00:10:59 (stored route samples carry no row identity): a route takes the share f of the
   impact weight of hand-off rows within 10 km of it. OPEN; an engine change (route identity in the hand-off) would close it (core request).
2. Locus C of the original charts is not legible and is not redrawn. OPEN (needs the original definition).
3. Searched-area outlines (charts 2, 3, 6 originals) and 5th/6th-arc contours (chart 7 original) are not drawn. OPEN.
4. Mass of run J D0' within +/-1 deg of the locus latitude: 0.072 from sample.npz here, against 0.226 in
   results-data/composition_run_j/v2/coincidence_locus.csv. UNRESOLVED; the composition note's definition should be checked.
5. Two arc fits: drawn arc = composer small circle (arc-line.npz), loci solved on the TL-grid arc fit; they differ by about 0.13 deg of
   longitude (12 km) at 33.6 S. DECLARED.
6. The composer key 'D0' is read as 00:19 Held Out (D0'). DECLARED.
7. Track and speed come from 600 s chords, not instantaneous values. DECLARED.
