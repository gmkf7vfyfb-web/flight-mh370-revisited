cd hydro; export GIT_CONFIG_GLOBAL=/dev/null; B=hypothesis/hydroacoustics
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
git fetch -q origin $B 2>/dev/null
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/imos_ram_grid.py" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/run_j_levels.py" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/tl_grid_table.py"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (imos-ram-grid)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics G-TL1: PRE-REGISTRATION of RAM along the arc grid at the five IMOS loggers (imos_ram_grid.py: receivers on own bathymetry, 1.0 deg x {-30,0,+30} NM, 10/20/40 Hz, RAM settings as the 8-path subset, drop-in rule, coverage mask, acceptance 0.5 dB, timing rule, deadline). run_j_levels amendment 2 (--imos-tl-file/--keys/--receivers), tl_grid_table.load_table imos_file. Committed before any RAM value on the grid. PREDICTIVE, NOT CALIBRATED; C1/C2")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store" ; echo "commit $C"; git fetch -q origin $B 2>/dev/null; git rev-parse --short origin/$B