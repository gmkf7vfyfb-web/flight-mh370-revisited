cd hydro; export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
B=hypothesis/hydroacoustics
git fetch -q origin $B 2>&1 | grep -v "failed to store"
# inbox check on fresh fetch of work branch
(cd ../repo && git fetch -q origin claude-science-sep29 2>&1 | grep -v "failed to store"; git diff --stat HEAD origin/claude-science-sep29 -- "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | tail -1)
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal/preregistration.py"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (weak-signal track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics: PRE-REGISTRATION of weak-signal method trials (work order 2026-10-21 block 8, brief Refresh v2 s7): test sets a/b/c, methods M0-M7, scoring and verdict rules, before any statistic on data")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store"; echo "commit $C"; git fetch -q origin $B 2>&1 | grep -v "failed to store"; git log --oneline -1 origin/$B