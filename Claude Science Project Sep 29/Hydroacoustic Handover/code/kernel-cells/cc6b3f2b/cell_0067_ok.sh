set -e
M="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
mkdir -p "$M/results-data/weak_signal"
for f in injection/pd_vs_snr.csv injection/thresholds.json injection/summary.json injection/sr_calibration.csv injection/m2_pairs.csv injection_ext/pd_vs_snr_union.csv injection_ext/summary_ext.json kadri/candidates.csv kadri/box_maxima.csv kadri/m2_cross_station.csv kadri/summary.json h08s/suppression.csv h08s/surviving_candidates.csv h08s/injection_pd.csv h08s/summary.json templates/template_build.json; do d=$(dirname $f); mkdir -p "$M/results-data/weak_signal/$d"; cp out/$f "$M/results-data/weak_signal/$f"; done
cat > "$M/results-data/weak_signal/README.txt" <<'EOF'
Weak-signal method trials (work order 2026-10-21 block 8), prereg 78c7e88, 22 Oct 2026. Small tables only; the full
products (null maxima, injection scores, templates, panel statistics, series, figures) are in
/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-weak-signal/ (SHA256SUMS). Note: results/hydroacoustics-weak-signal-methods.md.
EOF
rm -rf "$M/prepare/weak_signal/__pycache__"
du -sh "$M/results-data/weak_signal" "$M/prepare/weak_signal" "$M/data/kadri_fig9_digitised"
cd hydro; export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"; B=hypothesis/hydroacoustics
git fetch -q origin $B 2>&1 | grep -v "failed to store\|config/git" || true
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
P="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
git add --sparse "$P/prepare/weak_signal" "$P/results-data/weak_signal" "$P/data/kadri_fig9_digitised"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (weak-signal track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics block 8: weak-signal method trials — code (prepare/weak_signal: KRAKEN broadband template bank, 10 detectors, null + injection driver, SNR-grid amendment 1, Kadri panel scan, H08S airgun suppression, charts), digitised Kadri Fig. 9 traces copied into data/, small result tables. Matched filters SNR_50 ~7 dB vs 13-16 dB STA/LTA at 3376 (model-matched upper bound); M3/M5/M6/M7 negative. PREDICTIVE, NOT CALIBRATED; C1, C2.")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store\|config/git" || true
git fetch -q origin $B 2>&1 | grep -v "failed to store\|config/git" || true; echo "module commit $C"; git log --oneline -1 origin/$B