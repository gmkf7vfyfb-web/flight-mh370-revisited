du -sh out/*; du -sh out
EX=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-weak-signal; mkdir -p "$EX"; df -k /System/Volumes/Data | tail -1 | awk '{print $4/1048576 " GiB free"}'
cp -R out/injection out/injection_ext out/kadri out/h08s out/templates out/figs "$EX/"; rm -rf "$EX/templates/kraken_tmp"
cat > "$EX/README.txt" <<'EOF'
Hydroacoustics weak-signal method trials (work order 2026-10-21 block 8), 22 Oct 2026, unattended overnight track.
Pre-registration: module branch commit 78c7e88 (prepare/weak_signal/preregistration.py). Code: prepare/weak_signal/.
injection/      test set (a): null_maxima_<logger>.npz, thresholds.json, injection_scores.csv, pd_vs_snr.csv, m2_pairs.csv, summary.json
injection_ext/  amendment 1 (SNR 15-30 dB): injection_scores_ext.csv, pd_vs_snr_union.csv, summary_ext.json
kadri/          test set (b): candidates.csv, box_maxima.csv, m2_cross_station.csv, panel_statistics.npz, null_panel_maxima.npz
h08s/           test set (c): suppression.csv, surviving_candidates.csv, injection_pd.csv, injection_raw.csv, series.npz
templates/      KRAKEN broadband templates (templates_raw.npz, template_build.json)
figs/           the three charts (PNG + PDF); copies in results/ on claude-science-sep29
All digitised Kadri data are digitised plots; caveats C1 and C2 apply to every number.
EOF
(cd "$EX" && find . -type f -exec shasum -a 256 {} \; > SHA256SUMS); du -sh "$EX"