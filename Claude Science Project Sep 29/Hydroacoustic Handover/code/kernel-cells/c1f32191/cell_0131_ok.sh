export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null; URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd hydro; B=hypothesis/hydroacoustics; git -c credential.helper= fetch -q origin $B 2>/dev/null; export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
# the superseded ramgrid/ data must be removed from the tree: read-tree brought it back; remove the path from the index
git rm -r -q --cached --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/composition_run_j/ramgrid" 2>/dev/null
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j/" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/composition_run_j/"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); echo "tree $OLD -> $NEW (ramgrid/ 11 files replaced by v2/ 11 files + 2 scripts + README)"
C1=$(git -c user.name="Hydroacoustic Module (composition)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics block 11 A4/A5: product run-j-gated-v2 written on imos_tl_ram_arc.csv (74 seeds, five columns, READY); results-data/composition_run_j/v2 (consistent-table statistics) replaces ramgrid/ (withdrawn: first stats re-run straddled the table rewrite at 11:29:54Z); B11_OUT product override, addendum generators. PREDICTIVE, NOT CALIBRATED; C1, C2")
git -c credential.helper= push -q "$URL" $C1:refs/heads/$B 2>&1 | grep -v "failed to store\|config/git"; echo "module commit $C1"; unset GIT_INDEX_FILE; cd ..
cd repo; B=claude-science-sep29; git -c credential.helper= fetch -q origin $B 2>/dev/null; git diff --stat HEAD origin/$B -- "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | tail -1
git show origin/$B:"Claude Science Project Sep 29/coordination/architecture.md" > "Claude Science Project Sep 29/coordination/architecture.md"
cat >> "Claude Science Project Sep 29/coordination/architecture.md" <<EOF

## 2026-10-22 ~13:00Z — HYDROACOUSTICS (composition track, block 11, A4/A5) -> architecture, composer, Pete: run-j-gated-v2 is the product for the ruling

- **\`mh370-exchange/hydroacoustics/run-j-gated-v2/\`** (READY 12:34Z, 7.0 GB, SHA256SUMS): the five per-row columns on the corrected IMOS TL table
  \`imos_tl_ram_arc.csv\` (RAM along the grid, 5–40 Hz on all 253 paths, built 05:29:54 local), all 74 seeds in full (the 10 short free-stratum seeds included),
  313,599,968 rows, NaN 0; module commit \`$C1\` (code + results-data/composition_run_j/v2). \`run-j-gated\` is SUPERSEDED (first README line) and kept.
- **A5, disclosed:** the first statistics-only re-run (stats-ramgrid, 09:54–11:34Z, reported at ~12:00Z) straddled the RAM-grid track's table rewrite at 11:29:54Z,
  so its numbers mixed two table versions and are withdrawn; the addendum in \`results/hydroacoustics-composition-run-j.md\` is rewritten from the consistent v2 run.
- **Headline on the final table (D0', p 0.5, alpha 0.05, eta marginal):** ln Z −0.034; median latitude shift +0.05° (old table +0.10°); mass north of 33°S 0.058 → 0.063;
  KL 0.008 nats. 95 % upper limit on eta from the non-detection 5.6e-3 (prior alone 6.3e-3); P(no detection | eta) 0.56 / 0.79 / 0.89 at 1e-2 / 1e-3 / anchor.
  Classical exclusion not reached below 1e-2. D3/D4 p = 1 shifts +0.15° (were +1.4–1.5°; non-detection only −0.02°). Kadri 306.18° row −0.04 at both times;
  Royer B −0.18; Holland p = 1 : p = 0 −0.03 (D0'), +0.01 (D3), −0.02 (D4). Charts re-rendered on v2.
- **Ruling request:** may \`run-j-gated-v2/<stratum>/seed-N/hydro-lnL-imos-margeta.npy\` enter the composer as the module's likelihood (default), with
  \`hydro-lnL-ims-proxy-margeta.npy\` as the labelled sensitivity? Recommendation: admit with the G11-1 label (amplitude-blind matching; D3/D4 p = 1 rows carry it).
  The amplitude-weighted sensitivity on the stable table is being re-run (stats-ramgrid-v2) and will be appended when done.
-- Hydroacoustic Module (composition track), 22 Oct 2026
EOF
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j.md" "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j-evidence.png" "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j-evidence.pdf" "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j-limits.png" "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j-limits.pdf" "Claude Science Project Sep 29/coordination/architecture.md"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C2=$(git -c user.name="Hydroacoustic Module (composition)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 11 A4/A5: addendum rewritten from the consistent run-j-gated-v2 product (first statistics re-run withdrawn: table rewritten under it), charts re-rendered on the corrected table, coordination entry naming run-j-gated-v2 as the product for the ruling. PREDICTIVE, NOT CALIBRATED; C1, C2")
git -c credential.helper= push -q "$URL" $C2:refs/heads/$B 2>&1 | grep -v "failed to store\|config/git"; echo "work commit $C2"
S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/stats-ramgrid-v2; date -u +%H:%MZ; ls $S/_parts | wc -l