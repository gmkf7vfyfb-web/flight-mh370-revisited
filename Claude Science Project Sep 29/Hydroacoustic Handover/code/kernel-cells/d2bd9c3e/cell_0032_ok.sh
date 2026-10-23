set -e; cd hydro; export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
B=hypothesis/hydroacoustics
git fetch -q origin $B 2>&1 | grep -v "failed to store" || true
# inbox check on work branch
cd ../repo && git fetch -q origin claude-science-sep29 2>&1 | grep -v "failed to store" || true
git diff --stat HEAD origin/claude-science-sep29 -- "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | tail -2; cd ../hydro
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/run_j_windows.py"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (run J windows track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics: PRE-REGISTRATION run_j_windows.py (block 3 timing half: arrival windows on run J + northern supplement, D0'/D2/D3/D4, p 0/0.5/1, SOFAR+AGW, held-data coverage); committed before any run")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store" || true
git fetch -q origin $B 2>&1 | grep -v "failed to store" || true
echo PREREG_COMMIT $C; git rev-parse origin/$B