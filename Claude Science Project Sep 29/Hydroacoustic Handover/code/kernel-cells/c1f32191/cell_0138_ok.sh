S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/stats-ramgrid-v2; H="$PWD/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/composition_run_j"; cp $S/reduce/*.csv $S/reduce/*.json "$H/v2/" && cp $S/reduce/addendum_tables.md "$H/v2/addendum_tables.txt" && ls "$H/v2" | wc -l
RES="repo/Claude Science Project Sep 29/results"; grep -o "Amplitude-weighted (A4c, σ = 10 dB, down-weighting only): ln Z [^.]*\.[0-9]*, shift [^,]*, KL [0-9.]*" "$RES/hydroacoustics-composition-run-j.md" | head -1
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null; URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd hydro; B=hypothesis/hydroacoustics; git -c credential.helper= fetch -q origin $B 2>/dev/null; export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j/" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/composition_run_j/"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C1=$(git -c user.name="Hydroacoustic Module (composition)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics block 11 A5: statistics re-run on the stable table (stats-ramgrid-v2; accumulators identical to run-j-gated-v2 to machine precision) adds the amplitude-weighted G11-1 sensitivity; results-data/composition_run_j/v2 updated. PREDICTIVE, NOT CALIBRATED; C1, C2")
git -c credential.helper= push -q "$URL" $C1:refs/heads/$B 2>&1 | grep -v "failed to store\|config/git"; echo "module commit $C1"; unset GIT_INDEX_FILE; cd ..
cd repo; B=claude-science-sep29; git -c credential.helper= fetch -q origin $B 2>/dev/null; git show origin/$B:"Claude Science Project Sep 29/coordination/architecture.md" > "Claude Science Project Sep 29/coordination/architecture.md"
cat >> "Claude Science Project Sep 29/coordination/architecture.md" <<EOF

## 2026-10-22 ~13:45Z — HYDROACOUSTICS (composition track, block 11, A5 close-out) -> architecture, composer, Pete
The stable-table statistics re-run (stats-ramgrid-v2) finished; its accumulators equal run-j-gated-v2's to machine precision (max relative difference 0), so the v2
product and the addendum numbers are one consistent set. Amplitude-weighted G11-1 sensitivity on the final table (D0', p 0.5): see the addendum (module \`$C1\`);
D3/D4 p = 1 shifts +0.10° under it (full +0.15°, non-detection only −0.02°). Nothing else changes; run-j-gated-v2 remains the product for the ruling.
-- Hydroacoustic Module (composition track), 22 Oct 2026
EOF
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j.md" "Claude Science Project Sep 29/coordination/architecture.md"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C2=$(git -c user.name="Hydroacoustic Module (composition)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 11 A5 close-out: addendum with the amplitude-weighted sensitivity on the stable table (stats-ramgrid-v2 = run-j-gated-v2 accumulators); coordination entry. PREDICTIVE, NOT CALIBRATED; C1, C2")
git -c credential.helper= push -q "$URL" $C2:refs/heads/$B 2>&1 | grep -v "failed to store\|config/git"; echo "work commit $C2"; cd ..
mkdir -p deliver3 && cp "repo/Claude Science Project Sep 29/results/hydroacoustics-composition-run-j.md" "repo/Claude Science Project Sep 29/results/hydroacoustics-composition-run-j-evidence.png" "repo/Claude Science Project Sep 29/results/hydroacoustics-composition-run-j-limits.png" deliver3/ && cp $S/reduce/addendum_tables.md deliver3/composition-addendum-A4-old-vs-new.md && cp $S/reduce/upper_limits.csv deliver3/upper_limits_v2.csv && ls deliver3; date -u +%H:%MZ