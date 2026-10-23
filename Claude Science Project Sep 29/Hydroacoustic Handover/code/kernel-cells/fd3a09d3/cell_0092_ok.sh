cd hydro; export GIT_CONFIG_GLOBAL=/dev/null; B=hypothesis/hydroacoustics
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
git fetch -q origin $B 2>&1 | grep -v "failed to store"
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
P="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
git add --sparse "$P/tl_grid_run_j.py" "$P/tl_grid_table.py" "$P/tl_grid_evidence.py" "$P/tl_grid_charts.py" "$P/tl_grid_ram_subset.py" "$P/per_impact_lnl.py"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); echo "$OLD -> $NEW"; [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (tl-grid)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 2: TL grid tables/loader (tl_grid_table.py: drop-in tables, interpolation rule, ridge_source / ramcorr / adiabatic_suspect flags), evidence-alone view, charts, per_impact_lnl amendment 9 (--tl-table arc-grid, default unchanged), exploratory RAM-subset script (committed before its run)")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store"; echo "commit $C"; git fetch -q origin $B 2>&1 | grep -v "failed to store"; git log --oneline -1 origin/$B