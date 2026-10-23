set -e; cd "repo/Claude Science Project Sep 29/results"; python - <<'EOF'
p='hydroacoustics-blackman-validation.md'; s=open(p).read()
old='''amendment 1 (band counts, no rule changed) and amendment 2 (exploratory +30/+40/+50 km offsets) are recorded in the same
file.'''
new='''amendment 1 (band counts, no rule changed), amendment 2 (exploratory +30/+40/+50 km offsets) and amendment 3 (RAM set) are
recorded in the same file, with a timestamp correction: their headers first carried estimated clock times that were out of
order; they now carry the tool-recorded sequence (pre-registration e949144 → amendment 1 → TL pool complete 02:30:47 UTC →
amendment 2 → first RAM complete 02:43:27 → amendment 3), no number or rule changed.'''
assert old in s; s=s.replace(old,new); open(p,'w').write(s); print('note fixed')
EOF
export GIT_CONFIG_GLOBAL=/dev/null; URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd "$OLDPWD/hydro"; B=hypothesis/hydroacoustics; git fetch -q origin $B 2>/dev/null || true
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/tl_recal_block9.py"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (TL recal track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 9: timestamp correction on amendments 1-3 (estimated clock times replaced by the tool-recorded sequence; no number or rule changed)")
git push -q "$URL" $C:refs/heads/$B 2>/dev/null && echo "MODULE COMMIT $C"; unset GIT_INDEX_FILE
cd ../repo; B=claude-science-sep29; git fetch -q origin $B 2>/dev/null || true
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/results/hydroacoustics-blackman-validation.md"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C2=$(git -c user.name="Hydroacoustic Module (TL recal track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 9 addendum: record the amendment timestamp correction")
git push -q "$URL" $C2:refs/heads/$B 2>/dev/null && echo "WORK COMMIT $C2"
cp "Claude Science Project Sep 29/results/hydroacoustics-blackman-validation.md" ..