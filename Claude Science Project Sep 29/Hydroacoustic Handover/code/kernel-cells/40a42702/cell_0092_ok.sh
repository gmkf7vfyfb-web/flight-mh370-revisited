set -e
export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd repo
git ls-tree -r --name-only origin/claude-science-sep29 "Claude Science Project Sep 29/results/" 2>/dev/null | grep -i "tl-grid" || echo "no tl-grid note yet"
cd ..
# ---- module branch: results-data + updated charts.py/eta_map.py
cd hydro; B=hypothesis/hydroacoustics; git fetch -q origin $B 2>/dev/null
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j/" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/injection_run_j/"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C1=$(git -c user.name="Hydroacoustic Module (block 7 injection-recovery)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics block 7: results-data/injection_run_j (P_D vs level tables, fits, thresholds, errors, eta map, proxy check, summaries) + eta_map.py as pre-registered (IMOS RAM table; grid pass A for IMS) + charts.py. PREDICTIVE, NOT CALIBRATED; C1, C2.")
git push -q "$URL" $C1:refs/heads/$B 2>/dev/null && echo "PUSHED module $C1" || { echo RETRY-module; exit 1; }
unset GIT_INDEX_FILE
cd ../repo; B=claude-science-sep29; git fetch -q origin $B 2>/dev/null
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
# re-apply my coordination append on top of the fetched head to avoid clobbering concurrent entries
git show origin/$B:"Claude Science Project Sep 29/coordination/architecture.md" > /tmp/arch_head.md
python3 - <<'EOF'
mine=open("Claude Science Project Sep 29/coordination/architecture.md").read()
entry=mine[mine.index("\n## 2026-10-22 ~04:45Z — hydroacoustics (block 7 track)"):]
head=open("/tmp/arch_head.md").read()
open("Claude Science Project Sep 29/coordination/architecture.md","w").write(head.rstrip("\n")+"\n"+entry)
EOF
git add --sparse "Claude Science Project Sep 29/coordination/architecture.md" "Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j.md" "Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j-pd.png" "Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j-pd.pdf" "Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j-eta.png" "Claude Science Project Sep 29/results/hydroacoustics-injection-recovery-run-j-eta.pdf"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C2=$(git -c user.name="Hydroacoustic Module (block 7 injection-recovery)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 7: injection-recovery on run J note (P_D vs received level at six receivers; eta_50 ~ 6e-4 under D0' p 0.5; gate verdict yes/IMOS, proxy-only/IMS; likelihood form) + 2 charts + coordination entry. PREDICTIVE, NOT CALIBRATED; C1, C2; both Kadri times.")
git push -q "$URL" $C2:refs/heads/$B 2>/dev/null && echo "PUSHED work $C2" || { echo RETRY-work; exit 1; }