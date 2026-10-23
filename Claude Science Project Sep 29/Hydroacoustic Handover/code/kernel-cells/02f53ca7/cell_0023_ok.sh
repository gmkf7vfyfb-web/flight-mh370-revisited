cd hydro; export GIT_CONFIG_GLOBAL=/dev/null; B=hypothesis/hydroacoustics
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
git fetch -q origin $B 2>&1 | grep -v "failed to store\|config/git"
tail -3 "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | cut -c1-200
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/tl_recal_block9.py"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (TL recal track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 9: PRE-REGISTRATION of the TL recalibration (EW0112 forward source model, F-35A route, air8 under the same source, air7 N x 2D and 3-D proxy); criteria and decision rules fixed before computation")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store\|config/git"; echo "COMMIT $C"; git fetch -q origin $B 2>/dev/null; git log -1 --format='%h %s' origin/$B