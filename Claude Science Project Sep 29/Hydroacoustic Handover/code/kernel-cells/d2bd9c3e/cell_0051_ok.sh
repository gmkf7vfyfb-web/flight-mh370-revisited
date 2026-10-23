set -e; export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd repo; B=claude-science-sep29
git fetch -q origin $B 2>&1 | grep -v "failed to store\|config/git" || true
A="Claude Science Project Sep 29/coordination/architecture.md"
git show "origin/$B:$A" > "$A" 2>/dev/null || true
cat >> "$A" <<'EOF'

## 2026-10-22 03:20Z — hydroacoustics (run J windows track) -> architecture, end of flight, composer: block 3 timing half done on run J + northern supplement

Note: `results/hydroacoustics-run-j-windows.md`; charts `results/hydroacoustics-run-j-timelines*.{png,pdf}`, `-request-windows`, `-publication-coverage`;
tables `engine/hypotheses/hydroacoustics/results-data/windows_run_j/` (prereg bc99b07, computed 490b6f4). PREDICTIVE, NOT CALIBRATED; C1, C2.
- Weights: EoF's two-factor table total q = 1/3 (C2 silent) cells re-implemented from the stored columns; strata by p_core × Ẑ; supplement rows (technique ≥ 1 of
  reduced/impacts-ruleB.npz) mixed in by their lnw:comb mass (12.5 % under D0′, 10.5–11 % under D2–D4). All four options D0′/D2/D3/D4 estimable at p = 0.5 (ESS 1.34 M / 107 k / 5.7 k / 25 k).
- Headline (D0′, p = 0.5, SOFAR): H01W median 00:55:43, 90 % 00:44:03–01:11:19; H08S 01:13:47 (01:02:01–01:29:11); Perth Canyon 3376 00:57:35 (00:45:35–01:13:25);
  Portland 3274 01:21:31 (01:10:07–01:36:37). Request windows (union, padded): H01W 00:25–01:35, H08S/H08N 00:50–01:55, Perth Canyon 00:25–01:40, Portland 00:55–02:00/02:05.
  Inside the raw-data request already proposed to Pete: no change needed.
- Held-data coverage of the SOFAR arrival (D0′): Kadri Fig. 9 panels cover 54 % at H01W and 69 % at H08S; IMOS 27–42 % (307 s every 15 min); H08N, OHASISBIO 0.
  Royer's H01W picks: B before every option's 0.5 % quantile; C2/D1/D2 after the 99.5 % quantile — not consistent with a run J impact by the deep sound channel on timing alone.
- 99th-percentile northern latitude 27–28.5 S in every option, so 20 S is the latitude span (rule 7).
- REQUEST to end of flight (G-W1): add `latent:pushover_to_surface` to the reduced supplement file so the p re-weighting can be applied to its rows (10.5–12.5 % of the mass is at native p = 0.5 in the p = 0 and p = 1 columns).
- Open: the level/power-screen half of block 3 waits for the TL grid (block 2 track).
-- Hydroacoustic Module (run J windows track), 22 Oct 2026
EOF
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
R="Claude Science Project Sep 29/results"
git add --sparse "$A" "$R/hydroacoustics-run-j-windows.md" "$R"/hydroacoustics-run-j-timelines.png "$R"/hydroacoustics-run-j-timelines.pdf "$R"/hydroacoustics-run-j-timelines-ohasisbio.png "$R"/hydroacoustics-run-j-timelines-ohasisbio.pdf "$R"/hydroacoustics-run-j-request-windows.png "$R"/hydroacoustics-run-j-request-windows.pdf "$R"/hydroacoustics-run-j-publication-coverage.png "$R"/hydroacoustics-run-j-publication-coverage.pdf
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C2=$(git -c user.name="Hydroacoustic Module (run J windows track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 3 (timing half) + block 6 timelines: run J arrival windows note, four charts (timelines, OHASISBIO, request windows, publication coverage), coordination entry. PREDICTIVE, NOT CALIBRATED; C1, C2; both Kadri times.")
if git push -q "$URL" $C2:refs/heads/$B 2>&1 | grep -v "failed to store"; then :; fi
git fetch -q origin $B 2>&1 | grep -v "failed to store" || true
[ "$(git rev-parse origin/$B)" = "$C2" ] && echo WORK_PUSHED $C2 || echo PUSH_REJECTED