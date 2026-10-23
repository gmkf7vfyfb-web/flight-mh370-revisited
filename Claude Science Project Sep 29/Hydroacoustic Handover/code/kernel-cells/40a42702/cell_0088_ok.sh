OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection
du -sh $OUT; du -sh $OUT/*
cat > $OUT/README.txt <<'EOF'
Hydroacoustics block 7 (work order 2026-10-21): injection-recovery on run J - P_D against received level; eta mapping.
Written 2026-10-22 ~04:30 UTC by the Hydroacoustic Module (block 7 track, unattended). Pre-registration e816313 (prepare/injection_recovery_run_j/prereg.py).
STATUS: PREDICTIVE, NOT CALIBRATED. Caveats C1 (propagation slope misfit +10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling efficiency not calibrated; eta swept over four decades, F-35A upper anchor). H01W/H08S backgrounds are PROXIES (IMOS 3376 shaped to Blackman 2004 App. B, digitised). No likelihood column is written here.
inputs/    inputs.json (run J tau/range/energy quantiles per 00:19 option and p; ESS), subsample.npz (1-in-4 thin of the 8x50k-row chunk subsample of all 74 seeds; lat, lon, E_j, tau90_s, lnw_<option>, push-over flags, dist_<receiver>)
templates/ templates_raw.npz (KRAKEN broadband channel, 75 ranges), template_build.json
run/       thresholds.json, null_maxima_<rx>.npz, proxy_check.json, injection_scores.csv (26,460 rows), pd_vs_level.csv, fits.json, errors.csv, summary.json
eta/       eta_map.json, eta50_by_lat_band.csv
figs/      hydroacoustics-injection-recovery-run-j-{pd,eta}.{png,pdf}
Run J impacts: /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j (74 seeds; SHA256 per seed in the windows track's run.json). TL: IMOS = module results-data/ram_check/imos_tl_ramcorr.csv; H01W/H08S = run-j-tl-grid/raw/passA/tl_grid.csv (block 2 track, PROVISIONAL).
EOF
cd $OUT && find . -type f ! -name SHA256SUMS -exec shasum -a 256 {} \; > SHA256SUMS; wc -l SHA256SUMS
RD="$OLDPWD/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/injection_run_j"; mkdir -p "$RD"
cp $OUT/inputs/inputs.json $OUT/templates/template_build.json $OUT/run/thresholds.json $OUT/run/proxy_check.json $OUT/run/pd_vs_level.csv $OUT/run/fits.json $OUT/run/errors.csv $OUT/run/summary.json $OUT/eta/eta_map.json $OUT/eta/eta50_by_lat_band.csv $OUT/README.txt "$RD/"; du -sh "$RD"
cp $OUT/figs/* "$OLDPWD/repo/Claude Science Project Sep 29/results/"; ls "$OLDPWD/repo/Claude Science Project Sep 29/results/" | grep injection-recovery