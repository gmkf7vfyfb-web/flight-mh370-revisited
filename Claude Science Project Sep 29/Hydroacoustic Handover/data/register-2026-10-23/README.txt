Hydroacoustic detection register, 23 Oct 2026 (hydro clean-up run, proposal v6 block 2). EXPLORATORY; PREDICTIVE, NOT CALIBRATED; caveats C1, C2.
It replaces, for reading, graphics-2026-10-22/ranked (registry status KNOWN_DEFECT: D01-D04, D07, D08, D26) and the withdrawn Take 2 feasibility tables.
Every row of ranked_singles / ranked_pairs / ranked_triples is kept. Nothing is ranked, selected or called a candidate here.
Code: module branch hypothesis/hydroacoustics, prepare/gates/gates.py (checks), build_register.py (this table), test_gates.py (9 tests; they
reproduce the review counts 35 / 1,111 below-band, 63 / 2,584 / 11,067 Scott Reef, 44 of 47 airgun coincidences, 201 of 2,000 land points).
Files: register_singles.csv (184), register_pairs.csv (3,321), register_triples.csv (12,331), summary.json (flag counts, energy grid, Royer chance coverage).
Check columns (per member m1.. for pairs/triples): band_check, receiver_check, shot_check / shot_dt_s / shot_residual, land_check / land_points_inner,
known_event; per row: impact_time_check, E_q99 (run J, D0 weights, +/-1 deg), eta_at_q99E, x_old_2.1e-4, x_metz_2.26e-3 (pending ruling), coupling_check,
flags, n_flags. "n_flags = 0" means only that no check fired. It is NOT a detection claim and NOT a feasibility verdict.
Flags: band below / mostly below the receiver corner (IMOS 8 Hz, Kadri panels 5 Hz); no-information receiver (Scott Reef 3250); airgun-shot coincidence
(H08S, +/-1.5 s; NOT an exclusion: shot_residual gives the result of the existing shot-template subtraction, weak-signal test set (c), residual null unknown
G-W3); path crosses land (GEBCO 2026, >10 km from either end); H01W time-consistent with a Royer event (pick bars +/-2 s, arrows +/-20 s; at IMOS and H08S the
Royer windows cover 26-31 % of 00:00-02:00, so matches there are information only); implied impact before 00:19:29; impossible coupling (> 1 at q99 energy);
not assessed (no position; fewer than 20 run J impacts within 1 deg of the locus; or the ranked table gives an infinite loudness-match coupling,
a member receiver with no TL path such as Scott Reef 3250, or NaN). The H01W Royer flag uses the DIGITISED H01W-2 marks, which sit 7.7-16.6 s after Royer's
Table 5 times; against Table 5 alone some matches fail (open question for Royer). Corrected 23 Oct after the independent verifier: the 'not assessed'
reason text was one text for three causes.
Coupling approximations: singles use eta_needed at the reference impact (37.1 S, 1.13 GJ), so TL is at the reference place and energy at the implied place;
pairs/triples scale eta_level_locus (max over members, at the locus median energy) by median/q99 energy. Linear in energy; tau not changed.
Inputs carry their own defects (registry): D05 detector power on model templates, D06 stand-in noise, D24 windows-only search, D25 source depth 10 m, D26 panel p-values.
