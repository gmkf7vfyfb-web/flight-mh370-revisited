export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null; URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd hydro; B=hypothesis/hydroacoustics; git -c credential.helper= fetch -q origin $B 2>/dev/null; export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j/" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/composition_run_j/"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C1=$(git -c user.name="Hydroacoustic Module (composition)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics block 11 A4: code (RAM-grid IMOS TL option, amplitude-consistency-weighted match sensitivity, statistics-only mode, B11_IMOS_RAMGRID rewrite flag, addendum tables) + results-data/composition_run_j/ramgrid (statistics on imos_tl_ram_arc.csv; old tables kept beside). Columns in run-j-gated NOT rewritten (OLD table; README warning). PREDICTIVE, NOT CALIBRATED; C1, C2")
git -c credential.helper= push -q "$URL" $C1:refs/heads/$B 2>&1 | grep -v "failed to store\|config/git"; echo "module commit $C1"; unset GIT_INDEX_FILE; cd ..
cd repo; B=claude-science-sep29; git -c credential.helper= fetch -q origin $B 2>/dev/null; git diff --stat HEAD origin/$B -- "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | tail -1
git show origin/$B:"Claude Science Project Sep 29/coordination/architecture.md" > "Claude Science Project Sep 29/coordination/architecture.md"
cat >> "Claude Science Project Sep 29/coordination/architecture.md" <<EOF

## 2026-10-22 ~12:00Z — HYDROACOUSTICS (composition track, block 11, amendment A4) -> architecture, composer, Pete: statistics re-run on the corrected IMOS TL table; EXCHANGE COLUMNS ARE ON THE OLD TABLE

Follow-up to the 07:10Z entry after the RAM-along-grid track closed G-TL1 (imos_tl_ram_arc.csv). Pre-registered amendment A4 (\`e13a32e\`), code/data \`$C1\`,
addendum in \`results/hydroacoustics-composition-run-j.md\`. PREDICTIVE, NOT CALIBRATED; C1, C2; no detection claimed.
- **Columns not rewritten (disk).** \`mh370-exchange/hydroacoustics/run-j-gated/\` per-row columns were computed with the OLD IMOS table and MUST BE REWRITTEN
  before any composer use (README warning added; READY kept, columns consistent with their README; recipe \`B11_IMOS_RAMGRID=1 python driver.py\`, needs >= 28 GiB).
  Corrected STATISTICS (all 313.6 M rows + supplement) are in \`run-j-gated/stats-ramgrid/\` and \`results-data/composition_run_j/ramgrid/\`.
- **Corrected headline (D0', p 0.5, alpha 0.05, eta marginal):** ln Z −0.037 (was −0.066); median latitude shift +0.06° (was +0.10°); mass north of 33°S 0.058 → 0.064
  (was 0.072); KL 0.011 nats (was 0.019). 95 % upper limit on eta from the non-detection 5.2e-3 (was 4.6e-3; prior alone 6.3e-3); P(no detection | eta) 0.48 / 0.72 / 0.85
  at 1e-2 / 1e-3 / anchor (were 0.37 / 0.61 / 0.75) — the corrected table lowers the predicted levels at 3315/3275 by 5–6 dB for the southern impacts. Classical exclusion
  still not reached below 1e-2. D3/D4 p = 1 shifts fall from +1.4–1.5° to +0.3° (G11-1 narrowed, not closed). Bayes factors: Kadri 306.18° −0.03 at both times;
  Royer B −0.18; Holland p = 1 : p = 0 −0.04 (D0'), −0.01 (D3), −0.03 (D4). Coincidence locus unchanged (IMS chain untouched).
- **G11-1 sensitivity added:** amplitude-consistency-weighted match (sigma 10 dB, down-weighting only, labelled): ln Z −0.084, shift +0.04° (D0' p 0.5); D3/D4 p = 1
  shift +0.13°. Non-detection only: −0.185, −0.03°. A calibrated amplitude likelihood ratio still needs the background level density of screen-level candidates.
- **Ruling request (updated):** wait for the column rewrite on imos_tl_ram_arc.csv, then admit \`hydro-lnL-imos-margeta\` with the G11-1 label (or the amplitude-weighted
  variant as a conservative default); IMS proxy stays a sensitivity. New gap G11-6: exchange columns on the old table until rewritten.
-- Hydroacoustic Module (composition track), 22 Oct 2026
EOF
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j.md" "Claude Science Project Sep 29/coordination/architecture.md"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C2=$(git -c user.name="Hydroacoustic Module (composition)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 11 addendum A4: statistics re-run on the corrected IMOS TL table (RAM along the grid), old vs new tables, amplitude-weighted G11-1 sensitivity; exchange columns declared ON THE OLD TABLE (must be rewritten before composer use); coordination entry. PREDICTIVE, NOT CALIBRATED; C1, C2")
git -c credential.helper= push -q "$URL" $C2:refs/heads/$B 2>&1 | grep -v "failed to store\|config/git"; echo "work commit $C2"; git -c credential.helper= fetch -q origin $B 2>/dev/null; git log --oneline -1 origin/$B | cut -c1-80