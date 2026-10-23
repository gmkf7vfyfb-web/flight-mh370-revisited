set -e
cd hydro; export GIT_CONFIG_GLOBAL=/dev/null; B=hypothesis/hydroacoustics
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
git fetch -q origin $B
# inbox check on work branch
(cd ../repo && git fetch -q origin claude-science-sep29 && git diff --stat HEAD origin/claude-science-sep29 -- "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | tail -1)
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j/prereg.py"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (block 7 injection-recovery)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics block 7: PRE-REGISTRATION of injection-recovery on run J (receivers, backgrounds incl. IMS proxy, one-pole source with run J tau quantiles, KRAKEN dispersion, level grid -20..+30 dB, M1b/M0a/M0b, alpha 0.3/0.1/0.05/0.01(+0.001), N_INJ 120/60, eta mapping). Committed before any statistic on hydrophone data.")
git push -q "$URL" $C:refs/heads/$B && echo "PUSHED $C" || { git fetch -q origin $B; echo "RETRY"; }