cd hydro; export GIT_CONFIG_GLOBAL=/dev/null; B=hypothesis/hydroacoustics
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
git fetch -q --depth 1 origin $B 2>&1 | grep -v "ignore\|store"
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/ranked_candidates/prereg.py"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); echo $OLD $NEW; [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (graphics ranking)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics graphics track: pre-register EXPLORATORY candidate ranking (approximate ln LR signal vs background; singles, pairs, triples) before any score is computed. Not part of the frozen searches. PREDICTIVE, NOT CALIBRATED; C1, C2")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "ignore\|store"; git fetch -q --depth 1 origin $B 2>/dev/null; git rev-parse origin/$B; echo $C