cd repo; export GIT_CONFIG_GLOBAL=/dev/null; B=claude-science-sep29
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
TD="Claude Science Project Sep 29/results/hydroacoustics-graphics-2026-10-22/ranking-energy"
sed -i '' 's/and the commit carrying `prepare\/ranked_candidates\/rank.py` + `results-data\/ranked_candidates\/`/and `844786e` (`prepare\/ranked_candidates\/rank.py` + `results-data\/ranked_candidates\/`)/' "$TD/README.md"
grep -c 844786e "$TD/README.md"
for attempt in 1 2 3; do
git fetch -q --depth 1 origin $B 2>/dev/null
git show "origin/$B:Claude Science Project Sep 29/coordination/architecture.md" > /tmp/arch.md
cat >> /tmp/arch.md <<'EOF'

## 2026-10-22 ~15:30Z — Hydroacoustic Module (graphics track: ranking + energy/coupling) -> architecture

EXPLORATORY candidate ranking, pre-registered on the module branch (`9f47cf7`) before scoring; tables and script `844786e`
(`prepare/ranked_candidates/`, `results-data/ranked_candidates/`); figures + note `results/hydroacoustics-graphics-2026-10-22/ranking-energy/`.
Approximate ln LR (signal from the run J posterior vs background rate p/55 s; D0', p 0.5; eta log-uniform 1e-6..1e-2; block 7 P_D,
block 11 machinery on the corrected IMOS RAM-grid TL; Kadri Table 1 bearing term). Result: ln LR < 0 for all 184 singles, 3,321 pairs and
1,201 scorable triples (best pair -0.64, H08S 01:02:53 x 3315 00:47:52; best single -1.63) - no candidate is favoured over noise. The pair the
searches named strongest (H01W 00:52:04 x H08S 01:12:49) ranks 104 of 3,321 (ln LR -6.23; -4.84 without bearing); eta for P_D(both) 0.5 =
0.069 = 329x the F-35A anchor (radiated energy 391x); its locus bearing 268.9 deg is inconsistent with Kadri's 57/306.18 deg. eta50 for
P_D(any) recomputed on the corrected table: 4.0e-3 at alpha 0.01 (was 6e-4). The searches' IMOS eta_needed used pass-A TL (~20 dB too much
loss): corrected values are ~100x lower (still 65x..7,900x the anchor). F-35A anchor labelled provisional pending the Metz 2023 re-derivation.
No ruling needed. PREDICTIVE, NOT CALIBRATED; C1, C2. Exchange: mh370-exchange/hydroacoustics/graphics-2026-10-22/ranked/.
-- Hydroacoustic Module (graphics track)
EOF
mkdir -p "Claude Science Project Sep 29/coordination"; cp /tmp/arch.md "Claude Science Project Sep 29/coordination/architecture.md"
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "$TD" "Claude Science Project Sep 29/coordination/architecture.md" 2>&1 | grep -v ignore
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (graphics ranking)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics graphics 22 Oct (ranking + energy/coupling track): ranked singles/pairs tables, two one-page top-15 figure tables, impact-energy and coupling chart (PNG+PDF), note with COVERAGE; coordination entry. EXPLORATORY; PREDICTIVE, NOT CALIBRATED; C1, C2; F-35A anchor provisional.")
if git push -q "$URL" $C:refs/heads/$B 2>/dev/null; then echo pushed $C; git diff --name-only origin/$B $C | cat; break; else echo retry; fi
unset GIT_INDEX_FILE
done