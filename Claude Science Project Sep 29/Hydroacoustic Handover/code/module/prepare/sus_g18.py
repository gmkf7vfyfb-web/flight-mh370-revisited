"""PRE-REGISTRATION (committed before any A1-A5 panel is traced or any A1-A5 TL computed): gap G18 - the 2003 SUS
shots at sites A1, A2, A4, A5 (Blackman et al. 2004 App. B Figs B1, B2, B4, B5; printed pp. 25-28, PDF pp. 27-30),
added to the audit's SUS station-difference test (C2, criteria.md 940f1a3), which covered A6-A11 only.

SHOTS (blackman_2003_events.csv, data of record): A1sus2 (610 m), A1sus3 (915 m), A2sus2, A2sus3, A4sus2, A4sus3,
  A5sus2, A5sus3 (A4sus3 is printed under site label "A3"; position equal to A4's - kept as A4, declared).
TRACING: the audit's sus_spectra.py UNCHANGED (red signal / blue noise, route R, the module's blackman_noise frame
  and calibration code, FDSN 2003 responses), with the figure map extended: B1 = PDF p. 27 (rows sph1, sus2, sus3),
  B2 = p. 28 first image (rows sus2, sus3), B4 = p. 29 (rows sus2, sus3, sph5), B5 = p. 30 first image (rows from its
  caption). Columns H01, H08S, H08N as printed. Map checked by eye against the caption row order before scoring.
TL: the audit's sus_tl.py method UNCHANGED (paths.build GEBCO_2026 + WOA23 95A4, month of the shot = May; KRAKEN hard
  bottom via the module's wrapper; z_s 610 and 915 m; bands 5-63 Hz; receivers H01W1 2003 position, H08S 2002
  centroid, and H08N (module station) for the second difference). A run longer than 10 min goes behind the heavy lock.
SCORING: C2 exactly as the audit (sus_score.py): d_b = r_b(H01W) - r_b(H08S) over bands with signal SNR >= 3 dB at
  both; grades level <= 3/6, slope <= 1.5/3, shape <= 3.5/5; per shot and pooled over shots. ADDED, declared now:
  the same for H08N - H08S where H08N has a traced signal and an open path. Blocked paths give no model value.
VERDICT: reported as the audit's (per-shot grades, pooled verdict, span of bands); it extends the SUS validation
  span. No threshold is changed. Labels: predictive audit, not a likelihood.
"""
