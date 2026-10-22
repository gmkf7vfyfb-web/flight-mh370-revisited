Ranked hydroacoustic candidates (graphics track, 22 Oct 2026). EXPLORATORY; PREDICTIVE, NOT CALIBRATED; caveats C1, C2.
Pre-registration: module branch hypothesis/hydroacoustics commit 9f47cf7, prepare/ranked_candidates/prereg.py (formula and inputs).
Files:
  ranked_singles.csv    184 one-recorder candidates (imos_candidates.csv 133 + panel_candidates.csv 51), ranked by approximate ln LR (D0', p 0.5).
  ranked_pairs.csv      3,321 distinct candidate pairs from coincidence/pairs.csv (3,494 rows; the searches' 3,315 count merges the two Scott Reef 01:32:07 windows).
  ranked_triples.csv    12,331 three-recorder sets whose three pairwise combinations are all lag-consistent rows of pairs.csv; 11,067 contain blocked Scott Reef 3250 and 63 more have no
                        simulated impact matching all three times (ln LR -inf); 1,201 scored. No IMOS x IMOS x IMOS set without Scott Reef exists.
  ranked_multisite.csv  pairs + triples in one ranking.
  detectability_and_energy.json  eta50 recomputed on the corrected IMOS table, run J energy quantiles per 00:19 option.
Score: ln LR = ln N - ln B; N = sum_i w_i mean_eta prod_c [P_D(snr; alpha = p_c) x timing kernel x level consistency (10 dB) x Kadri Table 1 bearing term (H01W, within 30 s, t3 3.3 deg)];
B = prod_c (p_c / 55 s). ln LR < 0 everywhere: no candidate set is favoured over background.
Coupling columns: singles eta_needed = level match at the reference impact (37.1 S, 1.13 GJ, tau90 3.3 s) with the corrected TL (IMOS) or the searches' eta_needed (panels);
pairs/triples eta_pd50_all_a005 = coupling for prod P_D = 0.5 at alpha 0.05 at the arc locus of the lag (block 11 convention; reproduces 0.0692 for H01W 00:52:04 x H08S 01:12:49).
eta_x_F35A = multiple of the F-35A anchor 2.1e-4: provisional - from Brown 2026's quote of Metz 2023; re-derivation from Metz pending.
The searches' IMOS eta_needed used pass-A TL (e.g. 3275: 158.3 dB); the corrected table gives ~132-143 dB at 37.1 S, so IMOS coupling needs are ~100x lower than the searches' column (still 100s-1000s x the anchor).
Bearing caveat for H01W 00:52:04 x H08S 01:12:49: locus 33.6 S 94.5 E is at 268.9 deg from H01W (1,812 km) and 144.8 deg from H08S (3,660 km); Kadri gives 57 or 306.18 deg for the 00:52 signal
(text p. 9 and Table 1 caption disagree), neither within 37 deg; nearest Table 1 bearing to 268.9 is 00:52:50 at 274.84 deg, 46 s later. Within 30 s of 00:52:04 Table 1 gives 00:51:50 at 320.40 deg.
Both Kadri times: text time 00:52:03, caption time 00:54:30. H01W/H08S rows are from DIGITISED Kadri (2024) Fig. 9 panels.
