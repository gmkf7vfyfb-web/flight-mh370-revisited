set -e
export GIT_CONFIG_GLOBAL=/dev/null; URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
R="Claude Science Project Sep 29"; M="$R/engine/hypotheses/hydroacoustics"
# ---- module branch first
cd hydro; B=hypothesis/hydroacoustics; git fetch -q origin $B 2>/dev/null
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "$M/prepare/imos_ram_grid.py" "$M/prepare/imos_ram_grid_charts.py" "$M/results-data/tl_grid_run_j/imos_tl_ram_arc.csv" "$M/results-data/tl_grid_run_j/imos_ram_minus_kraken_arc.csv" "$M/results-data/tl_grid_run_j/imos_tl_ram_coverage.csv" "$M/results-data/tl_grid_run_j/imos_tl_ram_build.json" "$M/results-data/tl_grid_run_j/imos_ram_wall.json" "$M/results-data/imos_ram_grid"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C1=$(git -c user.name="Hydroacoustic Module (imos-ram-grid)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics G-TL1 addendum: RAM at 5 and 8 Hz on every grid path and the 41 remaining +-30 NM paths — all 253 planned paths now complete at 5/8/10/20/40 Hz; node rule = core bands 10/20/40 with 5/8 used where present; tables rebuilt in place (imos_tl_ram_arc.csv, delta table, mask); levels rerun v2 (3315 MF share at 1e-3 2.4 %, 3376 8.6 %, 3275 5.8 %; 3315 power screen MARGINAL). PREDICTIVE, NOT CALIBRATED; C1/C2")
git push -q "$URL" $C1:refs/heads/$B 2>&1 | grep -v "failed to store" || true; git fetch -q origin $B 2>/dev/null; echo "module $(git rev-parse --short origin/$B)"
unset GIT_INDEX_FILE; cd ..
# ---- addendum
SH=$(cd hydro && git rev-parse --short origin/hypothesis/hydroacoustics)
cat >> "repo/$R/results/hydroacoustics-imos-ram-grid.md" <<EOF

---

## Addendum (22 Oct 2026, 03:52–05:30 local / ~11:30Z; parent's follow-up): 5 and 8 Hz added on every path, ±30 NM completed — G-TL1a and G-TL1b closed

Code and tables \`$SH\` (hypothesis/hydroacoustics; \`imos_ram_grid.py\` build rule: a node counts on the core bands 10/20/40 Hz and
uses 5 and 8 Hz where present — all nodes now have them). Three further passes, same settings, 6 processes (1-minute load 1.1 at the
first launch; other tracks raised the machine load to 150–260 during the second pass, see the parent's query and the reply in
the coordination entry): (i) 5 and 8 Hz on the 85 offset-0 paths (170 jobs, 5 min); (ii) 10/20/40 Hz on the 41 incomplete ±30 NM paths
(112 jobs, 77 min); (iii) 5 and 8 Hz on the 168 ±30 NM paths (336 jobs, 15 min). **All 253 planned paths are complete at
5/8/10/20/40 Hz** (1,265 path × band jobs, 0 failed, 31.8 CPU-hours in total). Tables rebuilt in place (\`imos_tl_ram_arc.csv\`,
\`imos_ram_minus_kraken_arc.csv\`, \`imos_tl_ram_coverage.csv\`; the old rule-2 file still untouched). Row coverage: 3315/3376 60 %,
3250 42 %, 3274 34 %, 3275 33 % of all rows (every uncovered row is land, a < 15 m sill or a ±60 NM line); 100 % of the open rows on
every line that was run. \`band_extrapolated\` is now False everywhere (no band below 5 Hz in the table); \`jump_similar\` 630 rows;
the 12 \`below_physical_floor\` rows at −30 NM / 28.5°S remain flagged.

**RAM − KRAKEN at 5 and 8 Hz is small** (offset 0, q10 / median / q90): Perth Canyon −7/−3.5/−0.3 dB at 5 Hz and −12/−6/−1 dB at 8 Hz
(both loggers alike); Portland −19/−11/−6 dB at 8 Hz (at 5 Hz adiabatic KRAKEN has no trapped mode on any Portland path: those rows are
\`ram_fill\` = RAM + Francois–Garrison); Scott Reef −2/−1/+2 and −2/−1/+1 dB. The clamped 10 Hz Δ (−12 to −19 dB) used in the first
issue therefore over-corrected the low bands by 6–12 dB, exactly as the low-band sensitivity of §5 suggested, and the loudest predicted
band at Perth Canyon falls back by 7–9 dB (5 Hz median received level at η = 1: 3315 116.2 → 106.9 dB, 3376 116.6 → 107.5 dB;
Portland −10 to −12 dB).

**Levels rerun v2** (D0′, p = 0.5; \`results-data/imos_ram_grid/levels_rerun_v2_*.csv\`; the §5 table of the first issue is superseded
by this one):

| Logger | SNR q10/q50/q90 at η = 2.1e-4, old → v2 | share MF / base at 2.1e-4, old → v2 | share MF / base at 1e-3, old → v2 | η₅₀ MF old → v2 | η₅₀ base old → v2 |
|---|---|---|---|---|---|
| Perth Canyon 3315 | −11.0/−5.8/+9.7 → −21.9/−15.1/−2.8 | 13.6 % / 0.0 % → **0.1 %** / 0.0 % | 29.9 % / 12.4 % → **2.4 %** / 0.1 % | 4.0e-3 → 3.4e-2 | 2.5e-2 → 2.2e-1 |
| Perth Canyon 3376 | −16.0/−10.9/+4.6 → −20.1/−12.3/−0.1 | 0.2 % / 0.0 % → **1.0 %** / 0.0 % | 15.4 % / 0.0 % → **8.6 %** / 0.5 % | 1.3e-2 → 1.8e-2 | 8.1e-2 → 1.1e-1 |
| Portland 3274 | −24.1/−19.0/−4.2 → −29.1/−22.9/−7.9 | 0 → 0 | 0 → 0 | 8.4e-2 → 2.1e-1 | 0.53 → > 1 |
| Portland 3275 | −12.6/−7.5/+7.3 → −23.5/−16.1/−1.3 | 11.3 % / 0.0 % → **0.0 %** / 0.0 % | 25.4 % / 2.2 % → **5.8 %** / 0.0 % | 6.0e-3 → 4.3e-2 | 3.8e-2 → 2.7e-1 |
| Scott Reef 3250 | blocked (0.88 of mass) | 0 → 0 | 0 → 0 | > 1 → > 1 | > 1 → > 1 |

Against the first issue (v1, 10 Hz Δ clamped to 5–8 Hz): 3315 at η = 1e-3 9.8 → 2.4 %, 3376 17.2 → 8.6 %, 3275 16.6 → 5.8 %; at the
anchor 0.5 → 0.1, 1.9 → 1.0, 0.8 → 0.0 %. The v1 sensitivity bracket (3–10 / 13–17 / 15–17 %) contained v2 only for 3315; the old
rule-2 low-band Δ was itself too generous at Portland and 3376. **Power screen (rule: 1e-3 matched-filter share ≥ 0.05 KEEP, 0.01–0.05
MARGINAL):** 3315 **MARGINAL** (0.024; was KEEP), 3376 KEEP (0.086), 3275 KEEP (0.058), 3274 and 3250 DROP — the first verdict change
of the night, and it goes against the logger the old table made the loudest. Median SNR at the anchor is now −12 to −16 dB at the
three open loggers; η₅₀ (matched filter) 1.8e-2 to 4.3e-2, i.e. 85–200 times the F-35A anchor (C2). The chart has been re-drawn with v2.

**What remains of G-TL1:** G-TL1a and G-TL1b are closed. G-TL1c (31.5 Hz, the 2 m and 30 m source rows — the latter take the 10 m Δ)
and G-TL1d (0.5° in-between rows on interpolated Δ, 630 \`jump_similar\` rows) stay open; G-TL2, G-TL-X and G-N2/K5 unchanged. Also
disclosed: the 5 Hz Portland rows have no adiabatic reference at all (RAM alone), and 3250 at 5–8 Hz south of 30°S remains blocked in
both models. Coverage, ESS and labels otherwise as §7. Deviations of this addendum: none beyond those of §8 (the node rule for the
added bands is a clarification, recorded in the docstring); hard stop 13:30Z respected (finished ~11:30Z).

- **done:** 5/8 Hz on all 253 paths; ±30 NM completed at 10/20/40 Hz; tables, mask, levels v2, chart, this addendum, coordination entry.
- **next:** consumers reload (\`imos_file="imos_tl_ram_arc.csv"\`) — levels note IMOS rows, block 11 IMOS component, Kadri package
  \`predictions.csv\`; then 31.5 Hz and the 0.5° nodes (G-TL1c/d), G-TL2 with RAM.
- **blocker:** none.
EOF
# ---- coordination entry
cat >> "repo/$R/coordination/architecture.md" <<EOF

## 2026-10-22 ~11:30Z — hydroacoustics (imos-ram-grid track) -> architecture, composer, levels/composition consumers (cc Pete): G-TL1 addendum — 5 and 8 Hz added on every grid path, ±30 NM completed; 3315 drops to MARGINAL

Code/tables \`$SH\` (hypothesis/hydroacoustics), addendum in \`results/hydroacoustics-imos-ram-grid.md\` + re-drawn chart (claude-science-sep29). PREDICTIVE, NOT CALIBRATED; C1/C2.
- All 253 planned paths now complete at 5/8/10/20/40 Hz (1,265 jobs, 0 failed, 31.8 CPU-h). \`imos_tl_ram_arc.csv\`, the delta table and the mask were rebuilt IN PLACE in \`run-j-tl-grid/tables/\` and \`results-data/tl_grid_run_j/\` (same file names as the 10:00Z issue; the old rule-2 file untouched). G-TL1a/G-TL1b closed; G-TL1c (31.5 Hz, 2/30 m) and G-TL1d (0.5-degree rows) open.
- RAM − KRAKEN at 5/8 Hz is small (Perth Canyon −3.5/−6 dB medians; Portland −11 dB at 8 Hz, no adiabatic mode at 5 Hz), so the first issue's clamped 10 Hz Δ had over-corrected the low bands by 6–12 dB. Levels v2 (D0', p 0.5): matched-filter share at eta 1e-3 3315 2.4 % (old table 29.9 %, first issue 9.8 %), 3376 8.6 % (15.4 / 17.2), 3275 5.8 % (25.4 / 16.6); at the F-35A anchor 0.1 / 1.0 / 0.0 %. eta_50 (MF) 1.8e-2–4.3e-2. **Power screen: 3315 MARGINAL (0.024), 3376 KEEP, 3275 KEEP, 3274/3250 DROP.**
- SUPERSEDED: the 10:00Z numbers of this track (table and levels v1) as well as the IMOS rows of the levels note and the block-11 IMOS component; consumers should reload the in-place file now, not the 10:00Z version.
- On the load query (parent, ~10:50Z): one parent + 6 workers + resource tracker, no duplicate; OMP/OPENBLAS=1 set at launch and in every worker (MKL/NUMBA=1 added on the last pass); with the same 6 workers the load was 6–10 whenever other tracks were quiet, so the 150–260 came from elsewhere. Per-process thread counts cannot be read from this sandbox.
- done / next / blocker: done as above; next consumers reload, then 31.5 Hz + 0.5-degree nodes, G-TL2 with RAM; blocker none.
-- Hydroacoustic Module (imos-ram-grid track), 22 Oct 2026 ~11:30Z
EOF
cd repo; B=claude-science-sep29; git fetch -q origin $B 2>/dev/null
# re-base our local architecture.md on the latest origin head to keep others' entries
git show origin/$B:"$R/coordination/architecture.md" > /tmp/arch_head.md; python3 - <<'EOF'
import pathlib
loc=pathlib.Path("Claude Science Project Sep 29/coordination/architecture.md").read_text(); head=pathlib.Path("/tmp/arch_head.md").read_text()
mark="## 2026-10-22 ~11:30Z — hydroacoustics (imos-ram-grid track)"
mine=loc[loc.index(mark)-1:]
if mark not in head: head=head.rstrip("\n")+"\n"+mine
pathlib.Path("Claude Science Project Sep 29/coordination/architecture.md").write_text(head); print("arch merged", len(head))
EOF
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "$R/results/hydroacoustics-imos-ram-grid.md" "$R/results/hydroacoustics-imos-ram-grid-old-vs-new.png" "$R/results/hydroacoustics-imos-ram-grid-old-vs-new.pdf" "$R/coordination/architecture.md"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C2=$(git -c user.name="Hydroacoustic Module (imos-ram-grid)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics: G-TL1 addendum (5/8 Hz on every path, +-30 NM complete; 3315 MARGINAL) in results note + re-drawn chart; coordination entry. PREDICTIVE, NOT CALIBRATED; C1/C2")
git push -q "$URL" $C2:refs/heads/$B 2>&1 | grep -v "failed to store" || true; git fetch -q origin $B 2>/dev/null; echo "work $(git rev-parse --short origin/$B)"; date