set -e
cd hydro; export GIT_CONFIG_GLOBAL=/dev/null
B=hypothesis/hydroacoustics; URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
P="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/composition_run_j"
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
BLOB=$(git rev-parse "origin/$B:$P/tables.md")
git update-index --add --cacheinfo 100644,$BLOB,"$P/tables.txt"
git update-index --force-remove "$P/tables.md"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); echo "old=$OLD new=$NEW"; [ "$NEW" -eq "$OLD" ]
C=$(git -c user.name="Hydroacoustic Module" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics: rename results-data/composition_run_j/tables.md -> tables.txt (no .md inside engine/; content unchanged)")
git push -q "$URL" $C:refs/heads/$B && echo "PUSHED $C"
git diff --name-only 77b4b49 $C | grep '/engine/.*\.md$' || echo "no .md inside engine/"