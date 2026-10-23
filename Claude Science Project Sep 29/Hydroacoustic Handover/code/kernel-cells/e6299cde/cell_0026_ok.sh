set -e
export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
# inbox check
cd repo && git fetch -q origin claude-science-sep29 2>&1 | grep -v "failed to store" || true; git log -1 --format=%h origin/claude-science-sep29; git diff --stat HEAD origin/claude-science-sep29 -- "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | tail -1; cd ..
cd hydro
M="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
mkdir -p "$M/results-data/searches_run_j/geometry"
cp /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/geometry/{lags.csv,bearing_h01w.csv,energy.json,arrival_check.csv,run.json} "$M/results-data/searches_run_j/geometry/"
B=hypothesis/hydroacoustics
git fetch -q origin $B 2>&1 | grep -v "failed to store" || true
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "$M/prepare/searches_run_j/preregistration.py" "$M/prepare/searches_run_j/geometry.py" "$M/results-data/searches_run_j"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (searches track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics: BLOCK 4 PRE-REGISTRATION of the run J searches (windows union over options/p, bands, detectors M1b/D1/BE + H08S suppressed residual, thresholds 0.3/0.1/0.05, backgrounds, two-site rule, candidate format, Table 1/poster/Royer/infrasound tests); geometry sample (model only). Committed BEFORE any statistic on data. C1, C2; both Kadri times")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store" || true
git fetch -q origin $B 2>&1 | grep -v "failed to store" || true
echo "PREREG COMMIT $C"; git log -1 --format='%h %s' origin/$B | cut -c1-120
unset GIT_INDEX_FILE