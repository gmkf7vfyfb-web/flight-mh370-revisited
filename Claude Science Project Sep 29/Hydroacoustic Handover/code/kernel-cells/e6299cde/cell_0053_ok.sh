set -e
cd "repo/Claude Science Project Sep 29/results"
python - <<'EOF'
s=open('hydroacoustics-searches-run-j.md').read()
s=s.replace('| Perth Canyon 3315 | 105 | 10 / 31.5 | 0 / 10.5 | 0 / 5.3 | 01:16:4x BE p 0.1x (screen) |','| Perth Canyon 3315 | 105 | 10 / 31.5 | 0 / 10.5 | 0 / 5.3 | 01:17:26 BE 2–5 p 0.112 (outside the SOFAR window; below hardware corner) |')
s=s.replace('| Portland 3274 | 105 | 26 / 31.5 | 11 / 10.5 | 5 / 5.3 | 01:00:41 BE p 0.011 (outside the SOFAR window) |','| Portland 3274 | 105 | 26 / 31.5 | 11 / 10.5 | 5 / 5.3 | 01:00:41 BE 20–40 p 0.011 (outside the SOFAR window; η needed 250) |')
open('hydroacoustics-searches-run-j.md','w').write(s)
EOF
export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
# ---- module branch: code + tables
cd ../../../hydro
M="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
X=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches
D="$M/results-data/searches_run_j"; mkdir -p "$D/imos" "$D/panels" "$D/named" "$D/coincidence" "$D/null"
cp $X/imos/{imos_windows.csv,imos_candidates.csv,imos_summary.json} "$D/imos/"
cp $X/panels/{panel_windows.csv,panel_candidates.csv,box_minima.csv,h08s_suppression.csv,panel_summary.json} "$D/panels/"
cp $X/named/* "$D/named/"; cp $X/coincidence/* "$D/coincidence/"; cp $X/null/*.log "$D/null/"
cp $X/counts_vs_chance_by_receiver.csv $X/counts_vs_chance_by_detector.csv $X/SHA256SUMS "$D/"
du -sh "$D"
B=hypothesis/hydroacoustics
git fetch -q origin $B 2>&1 | grep -v "failed to store" || true
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "$M/prepare/searches_run_j" "$M/results-data/searches_run_j"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C1=$(git -c user.name="Hydroacoustic Module (searches track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics: BLOCK 5 searches on data held, run J (IMOS 5 loggers, digitised Kadri panels a-e with H08S suppression, Table 1 both times, poster boxes, Royer B/D1/D2, infrasound row, two-site coincidence); code + tables. Amendments A1 (held-span permutation null), A2 (blocked-path label) disclosed. PREDICTIVE, NOT CALIBRATED; C1, C2; digitised")
git push -q "$URL" $C1:refs/heads/$B 2>&1 | grep -v "failed to store" || true
unset GIT_INDEX_FILE
echo "MODULE COMMIT $C1"
# ---- work branch: note + charts + coordination entry (inbox re-read first)
cd ../repo
W=claude-science-sep29
git fetch -q origin $W 2>&1 | grep -v "failed to store" || true
git diff --stat HEAD origin/$W -- "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | tail -1
git show origin/$W:"Claude Science Project Sep 29/coordination/architecture.md" > "Claude Science Project Sep 29/coordination/architecture.md"
cat >> "Claude Science Project Sep 29/coordination/architecture.md" <<EOF

## 2026-10-22 ~05:30Z — hydroacoustics (searches track) -> architecture, composer, Pete: blocks 4-5 done (run J searches on data held)

Pre-registration a4cdab0 (module branch) before any statistic; searches committed at ${C1:0:7}; note \`results/hydroacoustics-searches-run-j.md\` + two charts on claude-science-sep29; tables in \`mh370-exchange/hydroacoustics/run-j-searches/\` (293 MB).
PREDICTIVE, NOT CALIBRATED; C1, C2; H01W/H08S are DIGITISED plots; both Kadri times carried.
- 786 windows x 3 detectors (+ H08S residual): 184 / 60 / 29 rows at screen / mark / report against 236 / 79 / 39 by chance; per receiver one third (Perth Canyon, H01W) to 1.5x (Scott Reef, Portland) the chance rate. No detection.
- Strongest single rows: H01W 00:52:04 matched filter p 0.043 (report, text-time box; caption time p 0.123); needs eta ~0.026 for the median impact (100x the F-35A anchor). H08S after suppression: Z_res 01:07:52 p 0.094 (mark). IMOS report rows at Portland/Scott Reef need eta > 1 or sit on a blocked path.
- Strongest two-site pair: H01W 00:52:04 x H08S 01:12:49 (max p 0.043, lag 1,245 s; the H08S row is typical of its own airgun panel, p_B 0.30); H01W x Perth Canyon 3376 00:52:11 lag-consistent at p 0.167 but needs eta 1.6. 36 pair tests, 2-3 at p ~0.02-0.03 expected by chance. Amendment A1: time slides are schedule-biased on duty-cycled data; a held-span permutation null sets p (disclosed).
- Kadri Table 1 on run J: 5 favoured / 10 uninformative / 5 disfavoured in bearing; the three favoured rows at 254-261 deg before 00:42 imply impacts at 00:15-00:16 (before 00:19:29); TWO rows fit both time and bearing (00:49:58 at 260.4 deg, 00:53:31 at 257.6 deg; implied impacts 00:26:47, 00:29:13; not identified in Fig. 9; no panel row within 10 s). The 306.18 deg row is UNINFORMATIVE (log10 BF -0.49, both times), not DISFAVOURED as on the stand-in: the northern supplement puts mass at 25-28 S.
- Poster (a) boxes 1-3 end 7.2/5.0/2.9 min before the earliest arc arrival (00:36:51; closest approach 1,563 km at 28.0 S): 'source before 00:19:29 or off the arc'; box 4 marginal.
- Royer B: 493 km off the arc, time in the 90 % band, zero D0' mass within 100 km. D1/D2: outside the 99 % impact-time band of every option (01:04-01:06 vs latest 00:49:35), 667/502 km off the arc. His H01W picks run 6-22 s early against his own origins (the 16 s question).
- Infrasound: declared no-information row (33-2,500x below threshold; data not public).
FOR COMPOSER: candidate rows are labels only (likelihood 0.0 stands until block 7 P_D). FOR THE KADRI PACKAGE (block 12): the two time-and-bearing-consistent Table 1 rows and the 306 deg re-verdict; question on panel (a) boxes stands.
-- Hydroacoustic Module (searches track), 22 Oct 2026
EOF
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$W
git add --sparse "Claude Science Project Sep 29/results/hydroacoustics-searches-run-j.md" "Claude Science Project Sep 29/results/hydroacoustics-searches-run-j-timeline.png" "Claude Science Project Sep 29/results/hydroacoustics-searches-run-j-timeline.pdf" "Claude Science Project Sep 29/results/hydroacoustics-searches-run-j-table1.png" "Claude Science Project Sep 29/results/hydroacoustics-searches-run-j-table1.pdf" "Claude Science Project Sep 29/coordination/architecture.md"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$W | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C2=$(git -c user.name="Hydroacoustic Module (searches track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$W -m "Hydroacoustics blocks 4-5: run J searches on data held — results note, timeline and Table 1 charts, coordination entry. PREDICTIVE, NOT CALIBRATED; C1, C2; digitised; both Kadri times")
git push -q "$URL" $C2:refs/heads/$W 2>&1 | grep -v "failed to store" || true
unset GIT_INDEX_FILE
git fetch -q origin $W 2>&1 | grep -v "failed to store" || true
echo "WORK COMMIT $C2"; git log -1 --format='%h %s' origin/$W | cut -c1-100
cd ../hydro && git fetch -q origin $B 2>&1 | grep -v "failed to store" || true; git log -1 --format='%h %s' origin/$B | cut -c1-100