set -e; export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
RES="$PWD/../../../../../../repo/Claude Science Project Sep 29/results"
python tl_recal_block9_charts.py ../results-data/tl_recal_block9 "$RES" "$RES/hydroacoustics-audit/data/air9_residuals.csv" | tail -1
du -sh ../results-data/tl_recal_block9; ls ../results-data/tl_recal_block9
# --- module branch
cd "$OLDPWD/hydro"; B=hypothesis/hydroacoustics
git fetch -q origin $B 2>/dev/null || true
echo "INBOX tail:"; tail -2 "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | cut -c1-160
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/tl_recal_block9.py" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/tl_recal_block9_charts.py" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/tl_recal_block9"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (TL recal track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 9: TL recalibration implementation and results-data (route 1 EW0112 forward model NOT EXPLAINED by level, slope within 3 dB/oct; air8 control still holds; air7 N x 2D and 3-D proxy NOT REPRODUCED); amendments 1-2 recorded")
git push -q "$URL" $C:refs/heads/$B 2>/dev/null && echo "MODULE COMMIT $C" || { git fetch -q origin $B 2>/dev/null; echo "RETRY needed"; }
unset GIT_INDEX_FILE
# --- work branch
cd ../repo; B=claude-science-sep29; git fetch -q origin $B 2>/dev/null || true
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/results/hydroacoustics-blackman-validation.md" "Claude Science Project Sep 29/results/hydroacoustics-air9-ew0112-predicted-vs-measured.png" "Claude Science Project Sep 29/results/hydroacoustics-air9-ew0112-predicted-vs-measured.pdf" "Claude Science Project Sep 29/results/hydroacoustics-air9-ew0112-residual-vs-frequency.png" "Claude Science Project Sep 29/results/hydroacoustics-air9-ew0112-residual-vs-frequency.pdf" "Claude Science Project Sep 29/results/hydroacoustics-air7-corridor-sensitivity.png" "Claude Science Project Sep 29/results/hydroacoustics-air7-corridor-sensitivity.pdf"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C2=$(git -c user.name="Hydroacoustic Module (TL recal track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 9: Blackman validation addendum (TL recalibration: route 1 NOT EXPLAINED under the pre-registered rule, slope within 3 dB/oct; route 2 not available; air8 still holds; air7 ridge path NOT REPRODUCED, G22 still open) with three charts")
git push -q "$URL" $C2:refs/heads/$B 2>/dev/null && echo "WORK COMMIT $C2" || { git fetch -q origin $B 2>/dev/null; echo "RETRY needed work"; }