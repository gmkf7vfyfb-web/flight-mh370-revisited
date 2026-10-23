set -e; export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
N="repo/Claude Science Project Sep 29/results/hydroacoustics-run-j-windows.md"
python - "$N" <<'EOF'
import sys; p=sys.argv[1]; s=open(p).read()
s=s.replace("event B 00:35:45–00:35:55 falls before the 0.5 % quantile of every option's H01W arrival (00:38–00:39)","event B 00:35:44–00:35:55 falls before the 0.5 % quantile of every option's H01W arrival (00:37:57–00:40:07 over options and p)")
s=s.replace("fall after the 99.5 % quantile (01:14)","fall after the 99.5 % quantile (01:14:23 under D0′, earlier in the other options)")
open(p,'w').write(s)
EOF
# inbox check
cd repo; git fetch -q origin claude-science-sep29 2>&1 | grep -v "failed to store\|config/git" || true
git diff --stat HEAD origin/claude-science-sep29 -- "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | tail -1
git log --oneline HEAD..origin/claude-science-sep29 | head -5
cd ..
# ---- module branch commit: code amendment + charts script + results-data
cd hydro; B=hypothesis/hydroacoustics
git fetch -q origin $B 2>&1 | grep -v "failed to store\|config/git" || true
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
P="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
git add --sparse "$P/prepare/run_j_windows.py" "$P/prepare/run_j_windows_charts.py" "$P/results-data/windows_run_j"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C1=$(git -c user.name="Hydroacoustic Module (run J windows track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics: run J arrival windows computed (amendment 1 plumbing only: subprocess workers); results-data/windows_run_j (windows, coverage, request windows, ESS, run.json); chart script. PREDICTIVE, NOT CALIBRATED; C1, C2")
git push -q "$URL" $C1:refs/heads/$B 2>&1 | grep -v "failed to store" || true
git fetch -q origin $B 2>&1 | grep -v "failed to store" || true; [ "$(git rev-parse origin/$B)" = "$C1" ] && echo MODULE_PUSHED $C1
unset GIT_INDEX_FILE; cd ..
echo ok