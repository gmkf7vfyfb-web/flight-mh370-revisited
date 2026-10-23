set -e; export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd repo; B=claude-science-sep29
python3 - <<'EOF'
p="Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j.md"; s=open(p).read()
s=s.replace("**PROVISIONAL** until that track's note is published)", "**PROVISIONAL**: pass A was read from disk while that track ran; its note `hydroacoustics-tl-grid-run-j.md` landed concurrently and should be read with this one)")
s=s.replace("TL grid pass A is provisional.", "TL grid pass A was used from disk before its note landed (`hydroacoustics-tl-grid-run-j.md`, same night); not re-run against the published tables.")
open(p,"w").write(s)
EOF
git fetch -q origin $B 2>/dev/null; export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j.md"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C3=$(git -c user.name="Hydroacoustic Module (block 7 injection-recovery)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 7 note: TL grid provenance wording (pass A read from disk; tl-grid note landed concurrently).")
git push -q "$URL" $C3:refs/heads/$B 2>/dev/null && echo "PUSHED $C3"
cp "Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j.md" "Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j-pd.png" "Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j-eta.png" ../