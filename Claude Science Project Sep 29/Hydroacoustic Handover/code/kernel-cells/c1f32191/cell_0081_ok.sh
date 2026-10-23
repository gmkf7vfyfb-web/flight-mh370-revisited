export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null; URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
cd repo; git -c credential.helper= fetch -q origin claude-science-sep29 2>&1 | grep -v "failed to store\|config/git"; git diff --stat HEAD origin/claude-science-sep29 -- "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | tail -1
# bring architecture.md to the current head before appending (blobless: read from origin)
git show origin/claude-science-sep29:"Claude Science Project Sep 29/coordination/architecture.md" > "Claude Science Project Sep 29/coordination/architecture.md"
cat >> "Claude Science Project Sep 29/coordination/architecture.md" <<'EOF'

## 2026-10-22 ~07:10Z — HYDROACOUSTICS (composition track, block 11) -> architecture, composer, Pete: gated likelihood columns written; RULING REQUESTED

Block 11 of work order 2026-10-21 is done; note `results/hydroacoustics-composition-run-j.md` (two charts beside it); pre-registration
`90d7181`, code `dddfbd0`; data `results-data/composition_run_j/`; exchange `mh370-exchange/hydroacoustics/run-j-gated/` (READY).
PREDICTIVE, NOT CALIBRATED; C1, C2; no detection claimed. The composer default `lnL_gated = 0.0` in `run-j/primary-tau-eof` is unchanged.

- **Columns (float32, row-aligned with run J impacts32, 74 seeds, 313.6 M rows, NaN = not computed, 0 rows; 0.0 = no information):**
  `hydro-lnL-imos-eta1e-3`, `-eta2.1e-4`, `-eta1e-4`, `hydro-lnL-imos-margeta` (η log-uniform [1e-6, 1e-2]; PROPOSED DEFAULT) and
  `hydro-lnL-ims-proxy-margeta` (SENSITIVITY: adds H01W/H08S on proxy backgrounds). Form L_r = (1 − P_D,r) + P_D,r m_r/β_r, M1b, α 0.05,
  P_D from block 7 on own IMOS backgrounds (3376, 3315, 3274, 3275), TL block 2 arc grid, E = contact KE, τ = tau90, cal. error N(0, 10 dB).
  GATE PASSED AT IMOS ONLY; IMS PROXY = SENSITIVITY. 10 of 18 free-stratum seeds (0.13 % of mass) carry only the marginalised column (another
  process held the disk below 20 GiB; top-up recipe in the exchange README).
- **Headline (D0′, p 0.5):** ln Z_hydro = −0.066; median latitude shift +0.10° (37.08 → 36.98°S); mass north of 33°S 0.058 → 0.072; KL 0.019 nats.
  Non-detection only: +0.02°, 0.058 → 0.067, KL 0.002. 95 % upper limit on η from the non-detection (posterior quantile, declared prior) 4.6e-3
  against 6.3e-3 for the prior alone; classical 95 % exclusion not reached below 1e-2 anywhere (P(no detection | η = 1e-2) = 0.37). Bayes
  factors per conditional all |ln BF| ≤ 0.15 on the gated term (Kadri 306.18° row −0.004 at both times; Royer B −0.14; D1/D2 and poster boxes
  1–3 no information; Holland p = 1 vs p = 0: −0.08 D0′, −0.15 D3/D4). Two-site pair H01W 00:52:04 × H08S 01:12:49: arc locus 33.6°S, implied
  impact 00:31:41 (inside the run J 50 % band), but P_D at both proxies needs η ≈ 0.069 (330× the anchor); p 0.019 over 36 tests is chance-level.
- **New gap G11-1 (matters):** the pre-registered match term is amplitude-blind. Two Portland 3275 candidates (01:07:47, 01:20:35; η needed
  19–30, louder than any impact) match early Holland-type impacts in time, and under D3/D4 at p = 1 they shift the combined median by
  +1.4–1.5° (KL 0.31); with the non-detection likelihood alone every shift is ≤ 0.05°. At p ≤ 0.5 under D0′/D2 the effect is ≤ 0.1°.
- **RULING REQUESTED:** may `hydro-lnL-imos-margeta` enter the composer as the module's likelihood (default), with `hydro-lnL-ims-proxy-margeta`
  as the labelled sensitivity? Module recommendation: either admit it with the G11-1 label (D3/D4 p = 1 shifts not yet trustworthy), or wait one
  pre-registered amendment for an amplitude-aware match / non-detection-only column (changes nothing at p ≤ 0.5 under D0′/D2).
- Also for end of flight: the reduced supplement file carries no tau90 (G11-3, stand-in used) and no pushover_to_surface (G-W1).
-- Hydroacoustic Module (composition track), 22 Oct 2026
EOF
B=claude-science-sep29; export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j.md" "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j-evidence.png" "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j-evidence.pdf" "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j-limits.png" "Claude Science Project Sep 29/results/hydroacoustics-composition-run-j-limits.pdf" "Claude Science Project Sep 29/coordination/architecture.md"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (composition)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 11 note: composition on run J (IMOS-gated likelihood columns, 95% upper limits on coupling two ways, evidence three ways with non-detection-only control, Bayes factors per conditional, two-site coincidence, COVERAGE) + 2 charts; coordination entry with the ruling request. PREDICTIVE, NOT CALIBRATED; C1, C2; both Kadri times; new gap G11-1 (amplitude-blind matching)")
git -c credential.helper= push -q "$URL" $C:refs/heads/$B 2>&1 | grep -v "failed to store\|config/git"; echo "work commit $C"; unset GIT_INDEX_FILE; cd ..
cd hydro; B=hypothesis/hydroacoustics; git -c credential.helper= fetch -q origin $B 2>&1 | grep -v "failed to store\|config/git"
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE; git read-tree origin/$B
git add --sparse "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j/" "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/composition_run_j/"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C2=$(git -c user.name="Hydroacoustic Module (composition)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "hydroacoustics block 11: results-data/composition_run_j (upper limits, evidence three ways + ND-only control, families, Holland BF, conditional BFs, coincidence, summaries, tables) + tables.py, charts.py; amendments A2 (B11_TOPUP re-run mode after a disk-floor short write) and A3 (merged subsample not written) disclosed. PREDICTIVE, NOT CALIBRATED; C1, C2")
git -c credential.helper= push -q "$URL" $C2:refs/heads/$B 2>&1 | grep -v "failed to store\|config/git"; echo "module commit $C2"
git -c credential.helper= fetch -q origin $B 2>&1 | grep -v "failed to store\|config/git"; git log --oneline -1 origin/$B