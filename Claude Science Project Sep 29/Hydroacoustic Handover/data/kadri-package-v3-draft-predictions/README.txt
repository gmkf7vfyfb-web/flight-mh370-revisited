Kadri package v3 DRAFT PREDICTIONS ONLY (hydro clean-up run, 23 Oct 2026). NOT FOR SENDING. PREDICTIVE, NOT CALIBRATED; C1, C2.
Code: module branch hypothesis/hydroacoustics, prepare/kadri_package/v3-2026-10-23/build_predictions_v3.py (v2 script plus three changes, listed in its docstring).
Changes from v2 predictions.csv: (1) IMOS TL from imos_tl_ram_arc.csv (RAM along the grid) in place of imos_tl_ramcorr_arc.csv (registry defect D22);
(2) added eta 2.26e-3 columns (exposure, 1 s SPL) and snr_db_eta2.26e-3_metz_pending: the Metz 2023 F-35A value under the module definition, PENDING PETE'S RULING;
(3) labels. The 2.1e-4 columns are kept for comparison; 2.1e-4 is Brown 2026's Arons-equivalent value, not the F-35A value under the module definition (D01).
Check against v2 (v2_v3_comparison.json): same 1,720 keys; on IMS rows (H01W, H08S, H08N) every common column is identical except 'labels' (declared change 3);
on IMOS rows 36 columns change (TL, levels, SNR, blockage, labels); IMOS TL change over the tl_db_5hz..40hz columns q05/q50/q95 -26.9/0.0/10.7 dB;
SNR(2.26e-3) - SNR(2.1e-4) = 10.3 or 10.4 dB (both columns rounded to 0.1 dB; exposure ratio 10.7619; theory 10.32 dB). Run time about 500 s, one process.
Corrected 23 Oct after the independent verifier (the first README overstated the identity check).
The v2 package TEXT is not updated. Errata for it: ERRATA_v2_text.txt. Pete decides on the text before anything is sent to Kadri or Royer.
