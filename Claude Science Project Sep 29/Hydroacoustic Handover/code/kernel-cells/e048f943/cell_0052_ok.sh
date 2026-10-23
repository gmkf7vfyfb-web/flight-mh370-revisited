export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd repo; git fetch -q origin claude-science-sep29 2>&1 | grep -v "config/git\|failed to store"; git diff --stat HEAD origin/claude-science-sep29 -- "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | tail -1
git show origin/claude-science-sep29:"Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | grep -n "^## 2026-10-2[12]" | tail -3
cd ..
cd hydro; B=hypothesis/hydroacoustics
git fetch -q origin $B 2>&1 | grep -v "config/git\|failed to store"
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
P="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
git add --sparse "$P/prepare/run_j_levels.py" "$P/prepare/run_j_levels_charts.py" "$P/results-data/levels_run_j"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); echo "$OLD -> $NEW"; [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (levels track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics: block 3 level half + power screen on run J — run_j_levels.py amendment 1 (supplement E = 1/2 m v^2; tau90 absent, G-L2), charts script, results-data/levels_run_j (detectable, band levels, eta_50, power screen, best receiver, coverage, sensitivities, IMOS third-octave noise percentiles, math check). PREDICTIVE, NOT CALIBRATED; C1/C2")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "config/git\|failed to store"; echo "module commit $C"; git fetch -q origin $B 2>&1 | grep -v "config/git\|failed to store"; git rev-parse --short origin/$B