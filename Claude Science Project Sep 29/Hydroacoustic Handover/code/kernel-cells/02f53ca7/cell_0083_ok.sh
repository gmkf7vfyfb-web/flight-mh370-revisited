set -e; export GIT_CONFIG_GLOBAL=/dev/null; URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd repo; git fetch -q origin claude-science-sep29 2>/dev/null || true
git show origin/claude-science-sep29:"Claude Science Project Sep 29/coordination/architecture.md" > "Claude Science Project Sep 29/coordination/architecture.md"
cd "Claude Science Project Sep 29/results"; python - <<'EOF'
p='hydroacoustics-blackman-validation.md'; s=open(p).read()
old='*Hydroacoustic Module (TL recalibration track), 2026-10-22.*'
new='''### Follow-up (amendment 4, `337e0a3`; after the Digitisation track finished)
- **Route 2 → gap G4.** One `fetch_article_fulltext` of Metz, Obana & Fukao (2023, doi 10.1007/s00024-022-03117-6) returned
  no full text or figures (closed access). The F-35A spectral route is recorded as **G4** and the block rests on route 1.
- **air7 re-scored on the Digitisation track's Fig. 23 traces** (`results-data/digitised/blackman-2004`, `1cb138a`; bands with
  ≥ 3 columns: 31.5, 40, 63 Hz; no ambiguous columns): observed air7 − air9 = −0.4, −2.0, +0.1 dB (earlier digitisation
  −0.2, −0.7, −0.4). Median excess, model − observed: geodesic **+54.3**, N×2D **+52.7**, least-loss ±20 km **+36.1** dB
  → **NOT REPRODUCED** again; RAM +21.8 / +18.0 / +20.1 dB (geodesic / +20 / +50 km). The conclusion is unchanged by the
  re-digitisation (`air7_corridor_v2.csv`, `air7_verdict_v2.json`).
- **air1 → H08N single-pair check of the EW0112 source model** (descriptive; the confirmatory rule needs ≥ 3 pairs and is not
  re-opened): existing audit-builder TL (1,259 km, 18° off the tow axis), new DGN air1 trace, 6 bands 20–80 Hz (40 Hz
  excluded). Uncorrected slope **−6.4 ± 1.5 dB/oct**; with the EW0112 source **+0.8 ± 1.8 dB/oct (PASS)**, shape 2.6 dB
  (PASS), at every z_s; level −22 dB (units, G23). The same source model that removes the air9 tilt also removes the air1
  tilt on an independent path to a third station, which supports the source attribution — one pair, so still short of the
  pre-registered confirmation (`air1_h08n_check.csv`, `air1_h08n_grades.csv`).

*Hydroacoustic Module (TL recalibration track), 2026-10-22.*'''
assert old in s; s=s.replace(old,new); open(p,'w').write(s); print('addendum updated')
EOF
cat >> "../coordination/architecture.md" <<'EOF'

## 2026-10-22 ~03:45Z — hydroacoustics (TL recalibration track) -> architecture (cc Pete): block 9 follow-up after the Digitisation track — route 2 is gap G4; air7 verdict unchanged on the new Fig. 23 traces; air1 -> H08N supports the EW0112 source model (single pair)
Amendment 4 `337e0a3`. Metz et al. 2023 fetch: closed, no figures -> F-35A spectral route recorded as G4. air7 -> H01W on the
Digitisation track's traces (1cb138a; 31.5/40/63 Hz): excess geodesic +54.3, N x 2D +52.7, +/-20 km +36.1 dB (NOT REPRODUCED,
unchanged); RAM +21.8 / +18.0 / +20.1 dB. air1 -> H08N (descriptive, 1 pair): slope -6.4 +/- 1.5 dB/oct uncorrected -> +0.8 +/- 1.8
(PASS) with the EW0112 source, shape 2.6 (PASS); level -22 dB (G23 units). Rulings (1) and (2) of the 03:20Z entry stand.
done: block 9 incl. follow-up / next: none runnable / blocker: none.
-- Hydroacoustic Module (TL recalibration track)
EOF
cd ../..; B=claude-science-sep29
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/coordination/architecture.md" "Claude Science Project Sep 29/results/hydroacoustics-blackman-validation.md"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C2=$(git -c user.name="Hydroacoustic Module (TL recal track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 9 follow-up: route 2 -> G4, air7 re-scored on the digitised Fig. 23 traces (unchanged), air1 -> H08N single-pair check supports the EW0112 source model; coordination entry")
git push -q "$URL" $C2:refs/heads/$B 2>/dev/null && echo "WORK COMMIT $C2"; unset GIT_INDEX_FILE
cp "Claude Science Project Sep 29/results/hydroacoustics-blackman-validation.md" ..
cd ../hydro; B=hypothesis/hydroacoustics; git fetch -q origin $B 2>/dev/null || true
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/tl_recal_block9.py" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/tl_recal_block9"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (TL recal track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 9 follow-up data: air7_corridor_v2, air7_verdict_v2, air1_h08n_check (amendment 4)")
git push -q "$URL" $C:refs/heads/$B 2>/dev/null && echo "MODULE COMMIT $C"