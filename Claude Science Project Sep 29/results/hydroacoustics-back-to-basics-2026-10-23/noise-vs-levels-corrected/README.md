# Noise against predicted levels, corrected 23 Oct 2026

Replaces the 22 Oct charts 1-3 and their companions, and the earlier noise-vs-impact / run-j-levels noise charts, which are deleted from the repo.

What changed:
- Cape Leeuwin (H01W): the "2014 noise 6 dB quieter" case is withdrawn. It came from reading Kadri's JPEG spectrogram colours (64 dB colour floor). Two better 2014 sources agree with Blackman 2003 within about 1.5 dB: the Royer 2016 spectrogram, 101.7 dB after a raster-smoothing correction, and the Kadri 2024 trace, 103.1 dB, against 101.7 dB. Blackman stays the noise reference.
- Diego Garcia South (H08S): the conditions on 8 March 2014 are added. Airgun shots raise the noise by +2.6 dB between shots and +7.5 dB with shots included: the measured +4.0 / +8.9 dB on the Kadri Fig. 9d trace, minus the +1.5 dB by which that figure's trace reads high at H01W.
- Coupling efficiency: shown at 0.01, 2.26e-3, 2.1e-4 and 1e-5. NEITHER aircraft value is from an authoritative source. 2.26e-3 is this project's own inversion: F-35A arrival levels digitised from Metz, Obana & Fukao (2023, Pure Appl. Geophys., peer-reviewed; the paper itself gives no energy, source level or coupling) combined with the 900 +/- 200 MJ energy from the Brown et al. (2026) arXiv preprint (not peer-reviewed), the module transmission loss (not calibrated), source depth 10 m and an f^-2 spectrum; single-factor spread 3.4e-4 to 5.4e-2. 2.1e-4 is the Arons-equivalent coupling in the Brown et al. preprint, a different definition. Earlier charts called 2.1e-4 'the F-35A value'; that label was wrong, but the value itself is still plotted. Coupling remains a prior range (Pete's ruling); 2.26e-3 is not adopted.
- Diego Garcia North (H08N) is blocked from every 7th-arc point 20-40 S (see ../noise-2003-vs-2014).

Reproduction: compute_levels_2026-10-23.py, run in the module prepare/ dir with the mh370-hydro env, reproduces the 22 Oct detectable shares exactly (H01W 23.0 % / 2.0 % at 1e-3; H08S 12.5 %; 3315 2.4 %; 3376 8.6 %). It adds the 2.26e-3 coupling level. Charts come from charts_levels_2026-10-23.py and common_2026-10-23.py.
