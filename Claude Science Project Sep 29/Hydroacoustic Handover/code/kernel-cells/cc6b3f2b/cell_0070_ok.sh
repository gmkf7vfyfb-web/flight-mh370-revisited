set -e
python3 - <<'EOF'
import csv
rows=[r for r in csv.DictReader(open("out/h08s/surviving_candidates.csv")) if r["stage"]=="c1+c2" and r["lag_consistent_with"]!="none"]
n_off=sum(r["off_cadence"]=="True" for r in rows); print(len(rows), n_off)
assert (len(rows), n_off)==(9,4)
for p in ["hydroacoustics-weak-signal-methods.md","repo/Claude Science Project Sep 29/results/hydroacoustics-weak-signal-methods.md"]:
    s=open(p).read(); assert "5 of those 9\nare off-cadence" in s; s=s.replace("5 of those 9\nare off-cadence","4 of those 9\nare off-cadence"); open(p,"w").write(s)
EOF
cd repo; export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"; B=claude-science-sep29
git fetch -q origin $B 2>&1 | grep -v "failed to store\|config/git" || true
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/results/hydroacoustics-weak-signal-methods.md"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (weak-signal track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 8 note: correct off-cadence count among the 9 lag-consistent H08S survivors (4, not 5; matches surviving_candidates.csv and the note's own table)")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store\|config/git" || true
git fetch -q origin $B 2>&1 | grep -v "failed to store\|config/git" || true; echo "fix commit $C"; git log --oneline -1 origin/$B