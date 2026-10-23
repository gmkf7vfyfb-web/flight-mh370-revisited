cd hydro; export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null; B=hypothesis/hydroacoustics
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
git -c credential.helper= fetch -q origin $B 2>&1 | grep -v "failed to store\|config/git"
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j/"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (composition)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics block 11: code (common.py level/P_D/matching machinery, worker.py per-seed columns + streamed statistics, driver.py 4 processes + finaliser, reduce.py limits/evidence/BFs/coincidence); prereg amendment A1 disclosed (E source order; value check: sidecar = 0.5 m v^2 to 6e-8). Run in progress; no results yet.")
git -c credential.helper= push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store\|config/git"; echo "commit $C"
S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging; tail -2 $S/driver.log; ls $S/_parts | wc -l