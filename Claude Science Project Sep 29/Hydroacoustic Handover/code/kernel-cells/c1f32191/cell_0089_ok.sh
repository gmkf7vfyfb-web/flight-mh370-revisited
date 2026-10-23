cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
p=open("prereg.py").read()
p=p.replace('''   Deviation from the task text, declared before the run: alpha 0.05 primary (report level), screen level 0.3 as a sensitivity.
"""''','''   Deviation from the task text, declared before the run: alpha 0.05 primary (report level), screen level 0.3 as a sensitivity.
A4 (23 Oct 2026, PRE-REGISTERED before the re-run; parent follow-up after the RAM-along-grid track closed G-TL1 on the offset-0 line):
   (a) IMOS TL for the four gated loggers is read from the corrected drop-in table
       /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_tl_ram_arc.csv (RAM - KRAKEN_noabs delta along the
       grid; offset-0 line, 10 m source, same loader rule: linear in latitude, clamped 41-20 S, blocked NaN -> zero energy). Rows the RAM
       grid does not cover keep the old rule-2 value inside that file (ram_grid_covered = False; on the offset-0 line only land / shallow
       rows) and their share is reported. The IMS tables are unchanged.
   (b) ONLY the streamed and subsample statistics are re-run (section 9-11): upper limits two ways, P(no detection | eta), evidence three
       ways, families, Holland and conditional Bayes factors, coincidence. The per-row COLUMNS in run-j-gated are NOT rewritten (disk);
       they stay on the OLD IMOS table and are labelled so in the README; they must be rewritten before any composer use.
       New statistics files go to run-j-gated/stats-ramgrid/ (acc.npz, subsample.npz per seed; < 200 MB each).
   (c) Amplitude-aware match, a labelled SENSITIVITY for gap G11-1 (IMOS receivers only; the digitised panels have no comparable
       band energy): m_r^A(i, eta) = sum_c k_t(c) * exp(-0.5 ((log10 E_c - log10 SE_r(i, eta)) / SIGMA_A)^2), where E_c is the candidate's
       observed excess 5-40 Hz band energy (excess_5_40_pa2s, block 5 table), SE_r(i, eta) = eta F_r T_eff,r 10^(L_cal/10) the predicted
       received band energy (same chain), SIGMA_A = 1.0 decade (10 dB: the block 7 level-recovery error, the +/-3 dB IMOS absolute level
       and the calibration-error spread, generous). The kernel only down-weights a match (it is not a calibrated likelihood ratio: no
       background level density is divided out), so the variant is conservative for matches and lies between the full and the
       non-detection-only likelihoods; labelled "amplitude-consistency-weighted (down-weighting only)". Written as additional streamed
       sums (wL_A per band x eta, half-degree wL_A, Holland and conditional BFs); no column.
   Values from the old table are kept in results-data/composition_run_j/ (old/) beside the new ones; the note's addendum tabulates both.
"""''')
p=p.replace('''N_DRAWS_BF = 20_000''','''N_DRAWS_BF = 20_000
# amendment A4
TL_TABLE_DIR_RAMGRID = pathlib.Path("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables")
IMOS_TL_FILE_RAMGRID = "imos_tl_ram_arc.csv"
SIGMA_A_DECADES = 1.0
STATS_DIR_RAMGRID = EXCHANGE_OUT / "stats-ramgrid"''')
open("prereg.py","w").write(p); print("ok")
EOF
cd ../../../../../..; export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null; URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd hydro; B=hypothesis/hydroacoustics; export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j/prereg.py"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (composition)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics block 11: PRE-REGISTERED amendment A4 — IMOS TL from the RAM-along-grid table imos_tl_ram_arc.csv (G-TL1 closure), statistics-only re-run (columns NOT rewritten, labelled OLD table), amplitude-consistency-weighted match as a labelled G11-1 sensitivity (sigma 10 dB, down-weighting only). Committed before the re-run.")
git -c credential.helper= push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store\|config/git"; echo "commit $C"