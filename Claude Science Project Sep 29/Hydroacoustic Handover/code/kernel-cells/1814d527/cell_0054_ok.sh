set -e
cd repo && export GIT_CONFIG_GLOBAL=/dev/null && git fetch -q origin claude-science-sep29 2>/dev/null || true
R="Claude Science Project Sep 29/results/hydroacoustics-kadri-package-v2.md"
cat > "$R" <<'EOF'
# Hydroacoustics: Kadri collaboration package v2 (work order 2026-10-21, block 12) — PREPARE ONLY

*Hydroacoustic Module (Kadri-package track), 22 Oct 2026 ~05:00 UTC. Unattended overnight run. Module commits `f2b678c`, `a58c3c5`
(`prepare/kadri_package/v2-2026-10-22/` on `hypothesis/hydroacoustics`). Zip-ready copy: `/Users/pete/Downloads/mh370-exchange/hydroacoustics/kadri-package-v2/`
(39 MB with the synthetic waveforms; the zip itself 18.6 MB; SHA256SUMS). **Nothing has been sent. Pete approves before anything leaves the project.**
No statistic on hydrophone data was computed in this block (nothing to pre-register); every number is PREDICTIVE, NOT CALIBRATED with
caveats C1 (propagation slope misfit, +10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling efficiency not calibrated; η over four decades,
F-35A upper anchor 2.1e-4). Both Kadri times carried everywhere: text time 00:52:03 and caption time 00:54:30.*

## Contents and provenance (one line per file; SHA-256 in `MANIFEST.txt`)

| file | provenance |
|---|---|
| `predictions.csv` (1,720 rows × 81 columns), `predictions_meta.json` | `build_predictions_v2.py`: whole-arc grid of block 2 (`run-j-tl-grid/tables`, 41–20°S × {−60, −30, 0, +30, +60} NM × 8 receivers, 10 m source); run J mass per cell from all 74 seeds (313.6 M rows) + northern supplement (1,277,785 rows, share 0.105–0.125), weights as `run_j_windows.py` (bc99b07) for D0′ (p = 0, 0.5, 1), D2, D3, D4; impact-time and energy quantiles per cell; SOFAR/AGW windows; TL per band as the chain uses it (IMS raw KRAKEN − RAM delta; IMOS RAM-corrected) with `adiabatic_suspect`, `ridge_source`, `ramcorr_extrapolated` flags; 5–40 Hz exposure and 1 s SPL at η ∈ {1e-2, 1e-3, 2.1e-4, 1e-4, 1e-5}; per-band level at the anchor; noise proxy and SNR; `module_likelihood = 0.0`. Run time 503 s, one process. |
| `windows.csv` (97 rows) | `build_windows_v2.py` from `run-j-windows/request_windows.csv` + `windows.csv` (block 3): request rows per receiver × branch × p (union over options, −10/+20 min) with the D0′ 90/99 % quantiles beside them; 13 reference rows (both Kadri times, six poster boxes, Table 1 rows 00:49:58 and 00:53:31, H08S 01:05–01:20, Royer H01W picks). |
| `reference_measure.py` | the 9 Oct draft (bands, peak/RMS/exposure, pre-event noise, SNR, plane-wave bearing) + the M1b envelope matched filter as an optional detector (`--m1b templates_envelope.npz`), self-contained numpy + scipy. |
| `templates_envelope.npz/.csv`, `templates_meta.json`, `pulse_runj.npz` | `make_templates.py` from the weak-signal track's KRAKEN synthesis (`run-j-weak-signal/templates/templates_raw.npz`, 78c7e88): 32 envelope templates (8 ranges 1,800–3,703.5 km × τ {0.1, 1, 3.06, 10} s), and the run J pulse model (2,200 km, τ = pooled median tau90 3.06 s, 5–40 Hz, 250 Hz). |
| `synth_triad.py`, `selftest.py`, `selftest_results.csv`, `selftest_summary.json`, `stations.csv` | synthetic H01W triad set regenerated with the run J pulse (2 bearings × 6 SNR × 3 seeds, 180 s, coloured noise) + 60 noise-only runs for the M1b null; waveforms only in the exchange copy (`synthetic_triad/`, 19 MB). |
| `REQUESTS.txt` (`.md` in the zip) | ask list A–E with reasons and windows; F: the parallel Royer request; G: what is not asked. |
| `CALIBRATION_STATUS.txt` | rewritten from tonight's notes (blocks 1, 2, 3, 5, 7, 8, 9), with the block-7 gate verdict that landed at ~04:45 UTC. |
| `README.txt`, `COVER_NOTE_FOR_PETE.txt` | one page on running the script unchanged on IMS triad data; the approval list and removal suggestions for Pete. |

## Key numbers (PREDICTIVE; C1, C2)

- Run J mass on the grid by offset (D0′, p = 0.5): −60 NM 4.8 %, −30 NM 9.6 %, 0 NM 40.3 %, +30 NM 30.9 %, +60 NM 14.4 %; 5.1 % of the mass
  lies beyond ±75 NM and is clamped to the outer line (`offset_clamped_share`); 0.006 % outside 41.25–19.75°S. Top cells: 37.0°S/0 NM 17.8 %,
  37.5°S/+30 11.2 %, 37.5°S/0 8.3 %, 38.0°S/+30 7.0 %. Under D4 the 37.0°S/0 cell carries 26.9 %.
- Cells on the arc line hold the early, steep impacts (37.0°S/0: impact q50 00:21:54, E q50 8.5 GJ, τ 1.1 s); the +30 NM cells the later ones
  (37.5°S/+30: 00:30:50, 1.2 GJ, 3.3 s). The pooled medians are E 1.12 GJ and τ 3.06 s.
- Mass-weighted 5–40 Hz 1 s SPL at H01W (q05 / q50 / q95): η 1e-2 99 / 104 / 113 dB; 1e-3 89 / 94 / 103; anchor 2.1e-4 82 / 88 / 97; 1e-4 79 / 84 / 93;
  1e-5 69 / 74 / 83, against the proxy noise median 101.7 dB (+4.8 dB triad gain). H08S: anchor 69 / 77 / 88 against 95.6 dB. At the core cell
  37.0°S/0 NM the anchor gives SNR −0.2 dB at H01W (η for SNR 0: 2.2e-4) and −4.1 dB at H08S (5.4e-4).
- Blockage: H01W, H08S, 3315, 3376 open at every grid point; H08N blocked (all bands) at 192 of 215 points; 3250 blocked at 79, 3274 at 91, 3275 at 91.
- Self-test (code property on model-matched synthetic data): bearing error p50 0.007° / 0.020° / 0.047° at in-pulse SNR +10 / +3 / 0 dB, failing
  below −3 dB with the 50 s dispersed run J pulse (the 9 Oct chirp test reached −6 dB because its 8 s chirp has a sharper cross-correlation peak);
  M1b detected 3/3 at ≥ 0 dB, 2/3 at −3 dB, 0/3 at ≤ −6 dB against the α = 0.01 null threshold ρ = 0.49 (180 noise-only windows). Field bearing error
  remains the demonstrated 3.3°.

## Open approvals (for Pete)

1. Send the package to Dr Kadri (files per `README`, asks A–E).
2. Send the Royer request (F) in the same step (Refresh v2 §4).
3. Decide on the removal suggestions in `COVER_NOTE_FOR_PETE`: (i) our p-values on his figure (H01W 00:52:04, H08S 01:12:49 / 01:07:52);
   (ii) naming Table 1 rows 00:49:58 and 00:53:31; (iii) the Blackman shots / G23 units remark; (iv) the Royer time-base question in the Kadri list;
   (v) the 1,075 IMOS rows in `predictions.csv`.

## COVERAGE

- **(a) Feasible set:** every impact the run J prior reaches (00:19:37–01:15:56; 44.5–10.4°S over strata and supplement; arc distance −390 to +600 NM),
  both log-on causes, both existence constraints; any η over four decades; receivers: the three IMS triads and five IMOS loggers.
- **(b) Model's reach:** the TL grid's reach (KRAKEN adiabatic on one 2-D section, hard bottom, 5–40 Hz, 10 m source; no 3-D, no coupled modes except
  the RAM deltas; AGW branch windowed by an assumed speed, not modelled); geodesic travel time without refraction or blockage; one pulse per impact;
  energy = contact kinetic energy (upper anchor); the M1b templates are flat-profile and model-matched (weak-signal G-W1). The 2–5 Hz band is not in the
  TL grid, so the table gives no level there.
- **(c) Proposal's coverage:** 215 cells × 8 receivers; run J mass inside the latitude span 99.99 %; inside ±75 NM 94.9 % (the remaining 5.1 % clamped,
  per cell in `offset_clamped_share`); 24 of 1,720 rows are cells with no run J mass (pooled medians used, flagged). ESS per option as in the windows
  note (D0′ 1.34 M, D2 107 k, D3 5.7 k, D4 25 k at p = 0.5); per-cell ESS not computed (gap below).
- **Gaps and status:** (G-K1, open) per-cell ESS and seed spread not computed — thin cells (north of 30°S, outer offsets) carry Monte Carlo noise in
  their energy and time quantiles; fix = per-seed accumulation (74 × 215 cells) in a second pass. (G-K2, declared) supplement rows keep native weights at
  p ≠ 0.5 (windows note G-W1) and have no τ (the τ median is strata-only). (G-K3, declared) supplement arc distance from the arc-grid field, nearest
  longitude where the field has no cell (`arc_fallback_rows` in the meta). (G-K4, open) IMS noise and P_D are proxies (block 7 verdict proxy-only at
  H01W/H08S) — this is exactly request B/C. (G-K5, open) G4 Metz 2023 and G5 Kadri 2019 closed access — request D. (G-K6, declared) the request-level
  table quotes cell-median E and τ, not the full per-cell distribution; the full distribution is in `run-j-tl-grid/evidence/`.
- **Parameter bounds with sources:** c 1.482 ± 0.006 km/s (module standard, 55eb191); AGW 1.40–1.50 km/s (assumed); η grid {1e-2 … 1e-5} with anchor 2.1e-4
  (F-35A, RAM-corrected median; `f35a_cal`); T_eff 2.683 s (stage B, T_C2); triad gain 4.8 dB (module rule); TL sd 7.9 dB (air9 RMS); 0.5° × 30 NM cells
  (grid of block 2).

## Deviations from the task text

- Prose files inside `engine/` are `.txt` (project rule: no `.md` inside `engine/`); the exchange zip carries `.md` copies with identical content.
- `predictions.csv` gives per-band received level at the anchor η only (scale by 10 log10(η/2.1e-4)); the five-η sweep is given for the 5–40 Hz total.
- The package was built before the block-7 note existed; its verdict (posted ~04:45 UTC) was folded into `CALIBRATION_STATUS.txt` and request B
  from the coordination entry, not from the note itself.

## done / next / blocker

- done: block 12 — package v2 built, self-tested, committed (`f2b678c`, `a58c3c5`), zip-ready copy in the exchange, this note, coordination entry to Pete.
- next: on Pete's approval, apply his removals and hand him the zip; per-cell ESS pass (G-K1) if the table is to be quoted per cell; when Kadri's derived
  products arrive, run `reference_measure.py` unchanged and the pre-registered searches on them.
- blocker: Pete's approval (nothing is sent without it); G4/G5 closed-access papers.
EOF
A="Claude Science Project Sep 29/coordination/architecture.md"
git show origin/claude-science-sep29:"$A" > "$A"
cat >> "$A" <<'EOF'

## 2026-10-22 ~05:00Z — hydroacoustics (Kadri-package track) -> Pete (cc architecture, composer): block 12 done — collaboration package v2 PREPARED, nothing sent

Work order 2026-10-21 block 12 is complete and committed on `hypothesis/hydroacoustics` (`f2b678c`, `a58c3c5`; `prepare/kadri_package/v2-2026-10-22/`).
Zip-ready copy: `/Users/pete/Downloads/mh370-exchange/hydroacoustics/kadri-package-v2/` (zip 18.6 MB; SHA256SUMS). Note:
`results/hydroacoustics-kadri-package-v2.md`. PREDICTIVE, NOT CALIBRATED; C1, C2 on every number; both Kadri times carried.

1. **predictions.csv** on the whole-arc grid (41–20°S × −60…+60 NM × 8 receivers, 1,720 rows): run J mass per cell (74 seeds + supplement) under D0′
   p = 0.5 with D2/D3/D4 and p = 0/1 beside it; impact-time and energy quantiles; SOFAR and AGW windows; TL per band with adiabatic_suspect / ridge /
   RAM-extrapolation flags; blockage; 5–40 Hz level for η ∈ {1e-2, 1e-3, 2.1e-4, 1e-4, 1e-5}; noise proxy and SNR; likelihood 0.0.
2. **windows.csv** from the block-3 request windows (both branches, union over options), with both Kadri times, the poster boxes, the two Table 1 rows
   and the H08S 01:05–01:20 interval as reference rows.
3. **reference_measure.py** + M1b envelope matched filter (optional, 32 templates) + run J pulse model; synthetic triad set regenerated and self-tested
   (bearing p50 ≤ 0.05° down to 0 dB in-pulse SNR; fails below −3 dB with the 50 s dispersed pulse — a code property, not field accuracy).
4. **REQUESTS** (A–G): derived products in the windows with ±6 h and 1–14 March controls; injection-recovery with his detector unchanged at received
   levels 70–115 dB (H01W) / 55–105 dB (H08S); noise percentiles 22:00–02:00; F-35A / San Juan / Blackman shots; the five questions (which time carries
   306.18°; what the panel-(a) boxes denote; Table 1 rows 00:49:58 and 00:53:31; H08S 01:05–01:20; the 16 s time base). Items needing Royer are marked;
   the Royer letter (S-SEIR, MAD, SWAMS 01:00–01:35 UTC; NEAMS loss acknowledged; 16 s question) is drafted in section F.
5. **CALIBRATION_STATUS** rewritten from tonight's notes, including the block-7 verdict (real-background P_D at the IMOS loggers; PROXY-ONLY at H01W/H08S).
6. **COVER_NOTE_FOR_PETE** lists what is being approved and five things Pete may want to remove (our p-values on his figure; naming the two Table 1 rows;
   the G23 units remark; the Royer time-base question in the Kadri list; the IMOS rows).

Open: Pete's approval of (i) the Kadri package, (ii) the Royer request, (iii) the removals. Gaps declared in the note (G-K1 per-cell ESS not computed;
G-K2/K3 supplement weights and arc distance; G-K4 IMS proxies = request B/C; G-K5 Metz 2023 / Kadri 2019 closed access). Prose files inside engine/
are .txt by the no-.md-in-engine rule; the zip carries .md copies. No private material from the Kadri bundle is quoted or included.
-- Hydroacoustic Module (Kadri-package track), 22 Oct 2026 ~05:00Z
EOF
B=claude-science-sep29; URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "$R" "$A"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); echo "$OLD -> $NEW"; [ "$NEW" -ge "$OLD" ] || { echo TREE SHRANK; exit 1; }
C=$(git -c user.name="Hydroacoustic Module (kadri-package track)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics block 12: Kadri collaboration package v2 results note (PREPARE ONLY, nothing sent) + coordination entry to Pete (approval items, removal suggestions, gaps). PREDICTIVE, NOT CALIBRATED; C1, C2.")
git push -q "$URL" $C:refs/heads/$B && echo "PUSHED $C" || { git fetch -q origin $B; echo "RETRY needed"; }