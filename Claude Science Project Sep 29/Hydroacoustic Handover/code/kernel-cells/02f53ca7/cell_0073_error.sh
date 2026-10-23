set -e; cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python - <<'EOF'
s=open('tl_recal_block9.py').read()
reps=[('AMENDMENT 1 (22 Oct 2026 02:50 UTC, before any residual was computed; raised by the reviewer):',
       'AMENDMENT 1 (22 Oct 2026, between the pre-registration commit e949144 at about 02:22 UTC and the first TL run, i.e. before any\n    residual was computed; raised by the reviewer; committed in 150da8d):'),
      ('AMENDMENT 2 (22 Oct 2026 02:45 UTC, after the +/-20 km result was seen; EXPLORATORY, labelled, outside the',
       'AMENDMENT 2 (22 Oct 2026, written after the TL pool finished at 02:30:47 UTC and the +/-20 km result was seen, before 02:35 UTC;\n  committed in 150da8d; EXPLORATORY, labelled, outside the'),
      ('AMENDMENT 3 (22 Oct 2026 02:50 UTC, after the first RAM result; EXPLORATORY, labelled).',
       'AMENDMENT 3 (22 Oct 2026, written after the first RAM result arrived at 02:43:27 UTC, before the extended RAM launch at about\n  02:46 UTC; committed in 48d28b7; EXPLORATORY, labelled).'),
      ('# IMPLEMENTATION is appended after the pre-registration commit',
       '''TIMESTAMP CORRECTION (22 Oct 2026, after the reviewer's finding; no number or rule changed): the three amendment headers first
  carried estimated clock times (02:50, 02:45, 02:50 UTC) that were not read from a clock and were out of order. They are
  replaced above by the tool-recorded sequence: pre-registration commit e949144 (about 02:22 UTC) -> amendment 1 -> TL pool
  complete 02:30:47 -> amendment 2 -> N x 2D complete 02:36:50 -> first RAM complete 02:43:27 -> amendment 3 -> extended RAM
  complete 03:09:36 -> addendum and coordination entry (03:20 UTC header). The order of decisions relative to results is what
  the record supports; the earlier numeric stamps should not be relied on.
# IMPLEMENTATION is appended after the pre-registration commit''')]
for a,b in reps:
    assert a in s, a[:40]; s=s.replace(a,b,1)
open('tl_recal_block9.py','w').write(s); import ast; ast.parse(s); print('fixed')
EOF
cd "$OLDPWD/repo/Claude Science Project Sep 29/results"; python - <<'EOF'
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