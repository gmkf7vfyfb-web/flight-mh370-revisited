set -e; export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd repo; git fetch -q origin claude-science-sep29 2>/dev/null || true
# refresh coordination files from the new head before appending (other tracks post concurrently)
git show origin/claude-science-sep29:"Claude Science Project Sep 29/coordination/architecture.md" > "Claude Science Project Sep 29/coordination/architecture.md"
echo "INBOX tail:"; git show origin/claude-science-sep29:"Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | tail -2 | cut -c1-160
cat >> "Claude Science Project Sep 29/coordination/architecture.md" <<'EOF'

## 2026-10-22 03:20Z — hydroacoustics (TL recalibration track) -> architecture (cc end of flight, Pete): block 9 done — route 1 NOT EXPLAINED under the pre-registered rule (slope now within 3 dB/oct), route 2 not available, air8 holds, air7 ridge is an adiabatic artefact (G22 partly explained); PREDICTIVE, NOT CALIBRATED, C1/C2

Pre-registration `e949144`; implementation and data `150da8d` + this commit (module branch, `prepare/tl_recal_block9.py`,
`results-data/tl_recal_block9/`); addendum in `results/hydroacoustics-blackman-validation.md` with three footnoted charts.
(a) Route 1, EW0112 near-source source spectrum forward to H01W/H08S (shared sections; pipeline check 0.0 dB vs audit M1):
  slope −2.3 ± 1.7 dB/oct (H01W, PARTIAL) and +0.5 ± 1.3 (H08S, PASS), shape 3.1/3.9 (PARTIAL), 78 % of the 45-point geometry
  grid passes slope at both stations; common-mode slope after the source −1.2 ± 1.8 dB/oct (was about −9). LEVEL fails at
  every SL_B 230–240 (−11 to −16 dB) → verdict NOT EXPLAINED as registered. Post hoc, labelled: the level test mixes a peak
  level with a spectrum level and is uninterpretable; declared as gap G23. C1 unchanged. Disclosure: not blind (post hoc
  result of 11 Oct known); fit-consistency on the training case only.
  RULING REQUESTED (1): may route 1 be re-registered with slope + shape only (level test dropped as uninterpretable), with the
  verdict then "PARTLY CALIBRATED in slope, conditional on the EW0112 source model, training case"? Not applied here.
(a) Route 2, F-35A: NOT AVAILABLE — Brown et al. 2026 (arXiv:2604.12723) has no F-35A waveform/spectrum (text only: 0.7 Pa at
  H11); the Digitisation track found the same (9854c72). Source spectrum would need Metz et al. 2023 (closed) — GAP.
(b) air8 under the same source model (descriptive; registered condition not met): H01W −39.0 dB FOLLOWS, H08S −1.2 dB
  CONSISTENT → still holds (array factor differs by ≤ 0.65 dB at H01W).
(d) air7 → H01W: adiabatic KRAKEN excess over the observed air7 ≈ air9 level, median 31.5–63 Hz: geodesic +56.8, N×2D
  Fresnel corridor +55.3, least-loss ±20 km +36.5 dB → NOT REPRODUCED as registered; exploratory +40/+50 km (ridge cleared)
  still +25 dB. RAM (coupled modes, exploratory amendment 3): +19.1 (geodesic), +15.7 (+20 km), +18.1 (+50 km) dB — the
  ridge costs only a few dB under mode coupling; the adiabatic chain overstates sill blockage by 35–55 dB here (air8: 39 vs
  18 dB). A path-wide 15–20 dB excess remains in both models (likely a noise-selected ceiling in Fig. 23 and/or near-source
  loss at the air7 site).
  PROPOSED G22 STATUS LINE for ARCHITECTURE.md (not edited by me): "G22 partly explained, still open: the air7 → H01W ridge
  loss is an adiabatic-model artefact (KRAKEN 57 dB excess, N×2D 55, ±20 km proxy 37; RAM 19 dB on the geodesic, 16–18 dB
  beside/clear of the ridge); a path-wide 15–20 dB excess over the observed air7 ≈ air9 level remains in both models, most
  likely a noise-selected ceiling in Fig. 23 and/or near-source loss at the air7 site. Consequence: adiabatic ridge/sill
  blockage is an upper bound on loss; RAM Δ is the correction. Next: Kadri's archive (air7 SNR); RAM on sill-crossing paths."
  RULING REQUESTED (2): adopt RAM in place of adiabatic KRAKEN on sill-crossing MH370 paths (blockage flags and TL), as the
  ram_tl_check Δ already does for stage C? Cost: about 3–14 min per band per path at 31.5–63 Hz single-threaded.
Compute: 110 + 21 KRAKEN runs (3 processes, 2.5 min), N×2D 119 runs (1 process, 7.6 min), 16 RAM runs (3–4 processes,
about 50 min); scratch in mh370-exchange/hydroacoustics/run-j-tlrecal deleted except sections (13 MB). Threads ≤ 4.
done: block 9 (a), (b), (d) / next: nothing in block 9; rulings (1) and (2) above / blocker: none for this block.
-- Hydroacoustic Module (TL recalibration track)
EOF
B=claude-science-sep29
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/coordination/architecture.md" "Claude Science Project Sep 29/results/hydroacoustics-blackman-validation.md" "Claude Science Project Sep 29/results/hydroacoustics-air7-corridor-sensitivity.png" "Claude Science Project Sep 29/results/hydroacoustics-air7-corridor-sensitivity.pdf" "Claude Science Project Sep 29/results/hydroacoustics-air9-ew0112-predicted-vs-measured.png" "Claude Science Project Sep 29/results/hydroacoustics-air9-ew0112-predicted-vs-measured.pdf" "Claude Science Project Sep 29/results/hydroacoustics-air9-ew0112-residual-vs-frequency.png" "Claude Science Project Sep 29/results/hydroacoustics-air9-ew0112-residual-vs-frequency.pdf"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C2=$(git -c user.name="Hydroacoustic Module (TL recal track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 9: RAM coupled-mode check added to the Blackman addendum (air7 ridge loss is an adiabatic artefact; 15-20 dB path-wide excess remains; G22 partly explained), route 2 final status, coordination entry with two rulings requested")
git push -q "$URL" $C2:refs/heads/$B 2>/dev/null && echo "WORK COMMIT $C2" || { git fetch -q origin $B 2>/dev/null; echo "RETRY work"; }
unset GIT_INDEX_FILE
# module branch: updated scripts + RAM data
cd ../hydro; B=hypothesis/hydroacoustics; git fetch -q origin $B 2>/dev/null || true
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/tl_recal_block9.py" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/tl_recal_block9_charts.py" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/tl_recal_block9"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (TL recal track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 9: amendment 3 (RAM coupled-mode check on air7 geodesic, +20 and +50 km paths, 31.5-63 Hz) with results; chart script final")
git push -q "$URL" $C:refs/heads/$B 2>/dev/null && echo "MODULE COMMIT $C" || { git fetch -q origin $B 2>/dev/null; echo "RETRY module"; }