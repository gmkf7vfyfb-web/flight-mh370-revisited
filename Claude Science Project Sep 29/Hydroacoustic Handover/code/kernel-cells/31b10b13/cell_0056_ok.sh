D="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
rm -f "hydro/$D/results-data/ranked_candidates/"*_raw.csv
cd repo; python - <<'EOF'
p="Claude Science Project Sep 29/results/hydroacoustics-graphics-2026-10-22/ranking-energy/README.md"
s=open(p).read()
old="3. `prepare/ranked_candidates/rank.py` is the consolidated form of the interactive session; the committed tables come from the session (verification noted in\n   the coordination entry)."
new="3. `prepare/ranked_candidates/rank.py` is the consolidated form of the interactive session; the committed tables come from the session. Verified by a full\n   re-run of the script (22 Oct, ~10 min): every finite ln LR (singles, pairs, triples) agrees to < 3e-14; the coupling columns agree to within 2.3 % (the session\n   cached the ±1° latitude mask at 0.01° rounding; one step of the 601-point η grid is 2.3 %)."
assert old in s; open(p,"w").write(s.replace(old,new))
EOF
cd ../hydro; export GIT_CONFIG_GLOBAL=/dev/null; B=hypothesis/hydroacoustics
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
git fetch -q --depth 1 origin $B 2>/dev/null
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "$D/prepare/ranked_candidates/rank.py" "$D/results-data/ranked_candidates" 2>&1 | grep -v ignore
git diff --cached --name-only origin/$B | cat
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); echo $OLD $NEW; [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (graphics ranking)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics graphics track: EXPLORATORY ranked candidates (prereg 9f47cf7): rank.py + results-data/ranked_candidates (184 singles, 3,321 pairs, 12,331 triples; ln LR < 0 for all; strongest searches pair H01W 00:52:04 x H08S 01:12:49 ranks 104/3,321, eta 0.069 = 329x provisional F-35A anchor, bearing inconsistent). Script re-run reproduces ln LR to <3e-14. PREDICTIVE, NOT CALIBRATED; C1, C2")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "ignore\|store"; git fetch -q --depth 1 origin $B 2>/dev/null; echo head $(git rev-parse origin/$B) mine $C
git diff --name-only 9f47cf7 $C 2>/dev/null | grep -v "engine/hypotheses/hydroacoustics/" | head