set -e
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
python - <<'EOF'
s=open('charts.py').read()
s=s.replace('"Candidate rows at every receiver, at one third to 1.5 times the rate chance gives on other days; none is a detection"','"Candidate rows at every receiver, at 0.1 to 1.5 times the rate chance gives on other days; none is a detection"')
s=s.replace('The counts of dots are within a factor of about 1.5 of what chance gives on other days (fewer at Perth Canyon and Cape Leeuwin, more at Scott Reef and Portland); no dot is a detection.','The counts of dots run from one tenth of what chance gives on other days (Cape Leeuwin) and one fifth to one third (Perth Canyon) up to 1.5 times (Scott Reef; Portland 0.8-0.9); no dot is a detection.')
open('charts.py','w').write(s)
EOF
python charts.py /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches "$PWD/../../../../../../../repo/Claude Science Project Sep 29/results" | tail -1
cd "../../../../../../../repo/Claude Science Project Sep 29/results"
python - <<'EOF'
s=open('hydroacoustics-searches-run-j.md').read()
old1="Per receiver the observed count lies between one third (Perth Canyon, Cape Leeuwin) and 1.5 times (Scott Reef, Portland 3275) the chance count."
new1="Per receiver the observed screen-level count runs from 0.11 of the chance count (Cape Leeuwin H01W, 4 vs 36), 0.22 and 0.32 (Perth Canyon 3376, 3315), 0.83 and 0.89 (Portland 3274, 3275), 1.31 (H08S, airgun-dominated) to 1.5 (Scott Reef 3250, 63 vs 42)."
assert old1 in s; s=s.replace(old1,new1)
old2="Every row falls inside the H01W union window; 17 of 20 inside the D0' 99 % window."
new2="Every row falls inside the H01W union window; 18 of 20 inside the D0' 99 % window (00:38:29 and 00:39:02 fall before it)."
assert old2 in s; s=s.replace(old2,new2)
open('hydroacoustics-searches-run-j.md','w').write(s)
EOF
grep -c "0.11 of the chance count\|18 of 20" hydroacoustics-searches-run-j.md
cp hydroacoustics-searches-run-j.md hydroacoustics-searches-run-j-timeline.png ../../../
# commit the corrections: charts.py on module branch, note+charts on work branch
export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd ../../../hydro; M="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; B=hypothesis/hydroacoustics
git fetch -q origin $B 2>&1 | grep -v "failed to store" || true
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "$M/prepare/searches_run_j/charts.py"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C3=$(git -c user.name="Hydroacoustic Module (searches track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics: searches charts — correct the chance-ratio wording (0.1 to 1.5x; H01W 0.11, Scott Reef 1.5) after review")
git push -q "$URL" $C3:refs/heads/$B 2>&1 | grep -v "failed to store" || true; unset GIT_INDEX_FILE; echo "MODULE FIX $C3"
cd ../repo; W=claude-science-sep29
git fetch -q origin $W 2>&1 | grep -v "failed to store" || true
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$W
git add --sparse "Claude Science Project Sep 29/results/hydroacoustics-searches-run-j.md" "Claude Science Project Sep 29/results/hydroacoustics-searches-run-j-timeline.png" "Claude Science Project Sep 29/results/hydroacoustics-searches-run-j-timeline.pdf"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$W | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C4=$(git -c user.name="Hydroacoustic Module (searches track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$W -m "Hydroacoustics searches note: review corrections (per-receiver chance ratios 0.11-1.5 with the right receivers; 18 of 20 Table 1 rows in the D0' window); timeline chart re-rendered")
git push -q "$URL" $C4:refs/heads/$W 2>&1 | grep -v "failed to store" || true; unset GIT_INDEX_FILE
git fetch -q origin $W 2>&1 | grep -v "failed to store" || true; echo "WORK FIX $C4"; git log -1 --format=%h origin/$W