
import shutil
det={"definition":"P_D(any of 6 receivers H01W,H08S,3376,3315,3274,3275)=0.5; block 7 M1b fits; block 11 machinery, corrected IMOS RAM-grid TL; +/-10 dB calibration draw; 200,000 rows drawn by option weight from the run J geometry sample; no duty cycle",
     "eta50":{f"{o}|alpha{a}":v[0] for (o,a),v in res50.items()},"pd_any_at_anchor":{f"{o}|alpha{a}":v[1] for (o,a),v in res50.items()},
     "earlier_table_eta50_D0_alpha0.01":6e-4,"anchor":ANCH,"anchor_note":ANOTE,
     "E_quantiles_J":{o:{str(q):v for q,v in d.items()} for o,d in Eq.items()}}
json.dump(det,open(f"{OUTX}/detectability_and_energy.json","w"),indent=1)
README=f"""Ranked hydroacoustic candidates (graphics track, 22 Oct 2026). EXPLORATORY; PREDICTIVE, NOT CALIBRATED; caveats C1, C2.
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
eta_x_F35A = multiple of the F-35A anchor 2.1e-4: {ANOTE}.
The searches' IMOS eta_needed used pass-A TL (e.g. 3275: 158.3 dB); the corrected table gives ~132-143 dB at 37.1 S, so IMOS coupling needs are ~100x lower than the searches' column (still 100s-1000s x the anchor).
Bearing caveat for H01W 00:52:04 x H08S 01:12:49: locus 33.6 S 94.5 E is at 268.9 deg from H01W (1,812 km) and 144.8 deg from H08S (3,660 km); Kadri gives 57 or 306.18 deg for the 00:52 signal
(text p. 9 and Table 1 caption disagree), neither within 37 deg; nearest Table 1 bearing to 268.9 is 00:52:50 at 274.84 deg, 46 s later. Within 30 s of 00:52:04 Table 1 gives 00:51:50 at 320.40 deg.
Both Kadri times: text time 00:52:03, caption time 00:54:30. H01W/H08S rows are from DIGITISED Kadri (2024) Fig. 9 panels.
"""
open(f"{OUTX}/README.txt","w").write(README)
RDOUT=f"{MOD}/results-data/ranked_candidates"; os.makedirs(RDOUT,exist_ok=True)
for f in ["ranked_singles.csv","ranked_pairs.csv","ranked_triples.csv","ranked_multisite.csv","detectability_and_energy.json"]:
    shutil.copy(f"{OUTX}/{f}",RDOUT)
shutil.copy(f"{OUTX}/README.txt",f"{RDOUT}/README.txt")
print({f:round(os.path.getsize(f"{RDOUT}/{f}")/1e6,2) for f in os.listdir(RDOUT)})
