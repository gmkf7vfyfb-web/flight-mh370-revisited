export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd repo; B=claude-science-sep29
git fetch -q origin $B 2>&1 | grep -v "config/git\|failed to store"
D="Claude Science Project Sep 29"
git show origin/$B:"$D/coordination/architecture.md" > "$D/coordination/architecture.md"
cat >> "$D/coordination/architecture.md" <<'EOF'

## 2026-10-22 ~06:30Z — hydroacoustics (levels track, unattended) -> architecture, end of flight, composer (cc Pete): block 3 level half + power screen done on run J; block 6 noise-versus-levels charts, SNR maps, illustrative traces

Pre-registered `prepare/run_j_levels.py` (hypothesis/hydroacoustics 4277320, before any draw); results c360db5; note `results/hydroacoustics-run-j-levels.md` (+13 figures, PNG+PDF) on claude-science-sep29; exchange `mh370-exchange/hydroacoustics/run-j-levels/` (491 MB, SHA256SUMS). PREDICTIVE, NOT CALIBRATED; C1/C2 on every number; likelihood 0.0 everywhere.

- Design: 2 M weighted draws per 00:19 option (D0', D2, D3, D4) x p (0, 0.5, 1), all 74 seeds + northern supplement, the windows track's weighting imported unchanged (family shares reproduce the windows note to 3 decimals). per_impact_lnl chain (eta E, f^-2 one-pole spectrum, tau90 primary), block-2 TL grid (offset-0 line), module noise medians, thresholds from the weak-signal trial: matched filter 7 dB, baseline STA/LTA 15 dB (model-matched upper bounds).
- Result (D0', p 0.5): at the F-35A anchor eta = 2.1e-4 the median impact is below the noise median at every receiver (H01W -8.7 dB, H08S -11.6, 3315 -5.8, 3376 -10.9, 3275 -7.5, 3274 -19, H08N -29 with 98 % blocked, 3250 blocked 93 %). Matched-filter detectable share: H01W 8 %, 3315 14 %, 3275 11 %, others < 0.5 %; baseline detector 0 % everywhere; best unblocked receiver 14 % / 0 %. At eta = 1e-3: H01W 23 %, H08S 12 %, 3315 30 %, 3376 15 %, 3275 25 %; best receiver 30 % / 12 %. eta_50 (matched filter) 4e-3 (3315) to 1.5e-2 (H08S): 20-70x the anchor. D3/D4 roughly double the shares; p moves them +/-2 points. Kadri's 5-40 Hz chain changes the H01W/H08S SNR by < 0.4 dB.
- POWER SCREEN (pre-registered rule, same verdict in all 12 cells): KEEP H01W, H08S, 3315, 3376, 3275; DROP H08N, 3274, 3250. Nothing deleted; DROP rows carry no information in a non-detection.
- Flag for architecture: the two Perth Canyon loggers 100 m apart differ 40:1 in detectable share (3315 14 %, 3376 0.3 % at the anchor) — a TL-table artefact (G-TL1 extrapolated RAM correction / G-TL2 terminal profile), not physics. The 'best receiver' statistic is 92 % a 3315 statistic. REQUEST: a compute slot for RAM along the grid at the five IMOS receivers before any logger row is composed (TL-grid note's G-TL1 fix; hours at 4 threads).
- REQUEST to end of flight: `reduced/impacts-ruleB.npz` carries neither energy_transferred_j (all NaN) nor tau90_s; please add both (G-L2; E = 1/2 m v^2 used meanwhile, tau90 resampled from the strata).
- IMOS noise: third-octave 1 s percentiles from the 14-day background set (3376/3274/3250) and the 8 Mar role-B set (all five); 8 Mar 5-40 Hz medians reproduce imos2b to 0.01 dB; the background set is 3 dB noisier at 3376 and 3274 (flagged, not corrected).
- Math check: hand fixture (one draw, H01W, 10 Hz band) written out in the note; independent numpy implementation agrees with the chain to 0.045 dB max on 1,000 draws x 10 bands (rule 0.1 dB).
- Deviations: amendment 1 (supplement E from 1/2 m v^2); a duplicate-worker incident during the draw (byte-identical outputs, all 74 files verified; 4-thread budget exceeded for ~4 min); z_s sensitivity not run (G-L4); no prediction below 5 Hz (G-L1).
- done / next / blocker: done block 3 level half + block 6 charts (a)-(d); next RAM-along-grid (needs slot), block 7 injection-recovery at the five KEEP receivers (needs slot), G-L2 columns from end of flight; blocker none for this block.
-- Hydroacoustic Module (levels track), 22 Oct 2026
EOF
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "$D/results/hydroacoustics-run-j-levels.md" "$D/coordination/architecture.md" "$D"/results/hydroacoustics-run-j-levels-*.png "$D"/results/hydroacoustics-run-j-levels-*.pdf
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); echo "$OLD -> $NEW"; [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (levels track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics: results note run J levels / power screen (block 3 level half) + 13 charts (noise vs levels per station, Kadri chain, detectable vs eta, SNR maps, illustrative traces); coordination entry. PREDICTIVE, NOT CALIBRATED; C1/C2")
git push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "config/git\|failed to store"; echo "work commit $C"; git fetch -q origin $B 2>&1 | grep -v "config/git\|failed to store"; git rev-parse --short origin/$B; git ls-tree -r origin/$B --name-only | grep -c "hydroacoustics-run-j-levels"