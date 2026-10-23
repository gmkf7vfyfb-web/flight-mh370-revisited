cd hydro; export GIT_CONFIG_GLOBAL=/dev/null; B=hypothesis/hydroacoustics
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
M="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
du -sh "$M/results-data/tl_grid_run_j/imos_tl_ram_arc.csv" "$M/results-data/imos_ram_grid"
git fetch -q origin $B 2>/dev/null
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "$M/prepare/imos_ram_grid.py" "$M/prepare/imos_ram_grid_charts.py" "$M/prepare/run_j_levels.py" "$M/prepare/tl_grid_table.py" "$M/results-data/tl_grid_run_j/imos_tl_ram_arc.csv" "$M/results-data/tl_grid_run_j/imos_ram_minus_kraken_arc.csv" "$M/results-data/tl_grid_run_j/imos_tl_ram_coverage.csv" "$M/results-data/tl_grid_run_j/imos_tl_ram_build.json" "$M/results-data/tl_grid_run_j/imos_ram_acceptance_check.csv" "$M/results-data/tl_grid_run_j/imos_ram_wall.json" "$M/results-data/imos_ram_grid"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (imos-ram-grid)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics G-TL1: RAM along the arc grid at the five IMOS loggers — 212/253 paths (offset 0 complete, +-30 NM 76 %), 10/20/40 Hz; drop-in imos_tl_ram_arc.csv + RAM-KRAKEN delta table + coverage mask; acceptance check exact vs the 8-path subset; amendment 1 (jump_similar donor rule across open/blocked node pairs, disclosed); levels rerun D0' p0.5 five loggers (3315 MF share at anchor 13.6 -> 0.5 %, 3376 0.2 -> 1.9 %; at 1e-3 29.9 -> 9.8 / 15.4 -> 17.2 %); low-band sensitivity; chart script. PREDICTIVE, NOT CALIBRATED; C1/C2")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store"; git fetch -q origin $B 2>/dev/null; echo "pushed $(git rev-parse --short origin/$B) ($C)"