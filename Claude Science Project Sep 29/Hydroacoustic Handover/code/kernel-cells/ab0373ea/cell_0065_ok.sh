python - <<'PYEOF'
import pathlib, re
p = pathlib.Path("repo/Claude Science Project Sep 29/results/hydroacoustics-imos-ram-grid.md"); s = p.read_text()
T = open("note_tables.txt").read()
def sec(a, b=None):
    i = T.index(a); j = T.index(b, i + 1) if b else len(T); return T[i:j].strip()
delta_tab = sec("| Logger | 10 Hz | 20 Hz | 40 Hz |", "All offsets pooled")
newold_tab = sec("| Logger | 10 Hz | 20 Hz | 31.5 Hz | 40 Hz | all bands 5-40 |", "## new - old TL by latitude band")
levels_tab = sec("| Logger | SNR q10/q50/q90", "power screen new")
R = {}
R["__MODULE_COMMITS__"] = "`4920cc2` (pre-registration), `__CODE_COMMIT__` (code, results-data)"
R["__RESULT_IN_WORDS__"] = """The constant per-logger RAM correction is replaced, on the whole offset-0 arc line and on 70–82 % of the ±30 NM lines, by a
coupled-mode (RAM) transmission loss computed path by path, each logger on its own bathymetry. Four things follow.

1. **The Perth Canyon 40:1 artefact is gone.** With the old table the two loggers 100 m apart had matched-filter detectable shares of
   13.6 % (3315) and 0.2 % (3376) at the F-35A anchor η = 2.1e-4 (D0′, p = 0.5). With the new table they are **0.5 % and 1.9 %**;
   at η = 1e-3 **9.8 % and 17.2 %** (was 29.9 % and 15.4 %). The two loggers now agree to within a factor 2–4 at every η, in the
   direction one expects from their depths (3376 is the deeper, 407 m against 445 m, and sits 13–38 m lower on the canyon wall).
2. **The IMOS numbers that fed block 11 (composition) are superseded.** 3315 and 3275 were the two loudest receivers of the levels
   note and the "best unblocked receiver" statistic was 92 % a 3315 statistic; both rested on the old table. New median SNR at the
   anchor: 3315 −11.2 dB (was −5.8), 3275 −10.6 dB (was −7.5), 3376 −9.9 dB (was −10.9). The matched-filter η₅₀ moves from 4.0e-3 to
   1.4e-2 at 3315 and from 6.0e-3 to 1.2e-2 at 3275 (3376: 1.3e-2 → 1.0e-2): on this chain **no IMOS logger reaches a 50 %
   matched-filter share below η ≈ 1e-2, about fifty times the F-35A anchor** (C2 applies). The power-screen verdicts do not change
   (KEEP 3315, 3376, 3275; DROP 3274, 3250: the rule is the 1e-3 matched-filter share ≥ 0.05, and the three KEEP loggers are at
   9.8 / 17.2 / 16.6 %).
3. **RAM − adiabatic KRAKEN at the seabed receivers is large and strongly frequency- and path-dependent** (offset 0, 10 m source):
   Perth Canyon median −12/−13 dB at 10 Hz, −24/−30 dB at 20 Hz, −60/−70 dB at 40 Hz with a 10–90 % spread of 30–55 dB at 40 Hz;
   Portland −19, −55, −117 to −133 dB; Scott Reef −3, −31, −117 dB. A constant Δ per logger was wrong by ±15–25 dB path by path in
   the southern half of the arc and by 50–120 dB north of 29°S, where rule 2 was extrapolating. The old table also carried an
   impossible value class — 3274/3275 at 29.0°S filled with the imp500 reference path's RAM value (135–150 dB) where the path is in
   fact blocked (RAM 466 dB) — and the uncorrected 3250 rows at 250–630 dB; both are fixed.
4. **What the new table does not settle** (the remainder of G-TL1, §9): the 5–8 Hz bands take the clamped 10 Hz Δ (RAM at 5–8 Hz
   not run); the loudest predicted band at Perth Canyon is now 5 Hz, and a sensitivity run that keeps the old 5–8 Hz values instead
   lowers the 3315 matched-filter share at η = 1e-3 from 9.8 % to 2.8 % (3376: 17.2 → 12.7 %; 3275: 16.6 → 15.5 %). The low bands
   are the next RAM job. Offsets ±30 NM are 70–82 % covered; 31.5 Hz, the 2 m and 30 m sources, and the terminal-profile sensitivity
   G-TL2 are untouched. Everything here is a model prediction (C1, C2); no detection is claimed."""
R["__ACCEPTANCE__"] = """Rule: the IMOS subset paths that lie on this grid (3315 at 36.0°S, 3274 at 38.0°S, 3275 at 40.0°S, 3250 at 24.0°S, offset 0, 40 Hz)
must reproduce `tl_grid_ram_subset.py`'s `tl_ram_db` to 0.5 dB, and 3376 at 38.5°S (not a 1.0° node) is rerun at 31.5 and 40 Hz.
**Result: all six pairs agree to < 0.001 dB** (RAM 124.8269 / 136.1445 / 137.2700 / 187.0321 dB at 40 Hz; 3376 at 38.5°S 128.6889 dB
at 31.5 Hz and 125.8058 dB at 40 Hz; the matched no-absorption KRAKEN values agree equally). The environment builder, the RAM
settings and the receiver-depth rule are therefore identical to the subset run; the only difference between this table and the
subset is coverage. `results-data/tl_grid_run_j/imos_ram_acceptance_check.csv`."""
R["__DELTA_TABLE__"] = f"""RAM − KRAKEN_noabs (dB) at the 1.0° nodes of the offset-0 line; n nodes, min / q10 / **median** / q90 / max. Negative = the
adiabatic model over-states the loss; positive = RAM loses more (the 31.5–33°S ridge-source rows, where adiabatic KRAKEN couples a
shelf source too well into the channel).

{delta_tab}

With ±30 NM pooled: 58 / 58 / 30 / 29 / 43 nodes (3315 / 3376 / 3274 / 3275 / 3250). The per-node values are in
`imos_ram_minus_kraken_arc.csv` (also `tl_ram_db`, `tl_kraken_noabs_db`, `range_km`, `rcv_depth_m`, `wall_s`).

**New − old table** (dB; offset 0, 10 m source, rows where either value is an open path < 230 dB; q10 / **median** / q90):

{newold_tab}

Split by latitude (open rows, offset 0, 10 m; q10/median/q90 of new − old): in the **southern half, 41–33°S, bands ≥ 12.5 Hz**, the new
table is *lossier* at 3315 (+2/+9/+16 dB) and 3275 (−1/+8/+15), about unchanged at 3376 (−12/−1/+8) and 3274 (−2/+3/+9); at 5–10 Hz
it is 1–4 dB *less* lossy at every logger (the clamped 10 Hz Δ against rule 2's 5 Hz Δ). **North of 33°S** the old table was
over-extrapolated: new − old −5 to −10 dB median at Perth Canyon (−24 to −27 dB at q10) and −39 dB median (−104 dB at q10) at Scott
Reef at ≥ 12.5 Hz, i.e. the old table over-stated the loss there by tens of dB. The 3274/3275 rows at 29.0°S go the other way: old
`ram_fill` 135–150 dB → new 412–466 dB (blocked), +285 dB at q90 in the northern 5–10 Hz cell.

Nothing in the table falls below the physical floor 60 + 10 log₁₀(R/km) dB on the offset-0 line; 12 rows do on the −30 NM line
(3315/3376 at 28.5°S, mostly the 30 m source, raw adiabatic KRAKEN 110 dB there), flagged `below_physical_floor = True` so that an
offset-aware consumer can treat them as not covered."""
R["__LEVELS_TABLE__"] = f"""2 M weighted draws, the levels track's subsample and weights unchanged (Kish ESS 1.90 M), T_eff 2.683 s, noise medians as the levels
note, thresholds matched filter 7 dB and baseline (STA/LTA) 15 dB. SNR on the 5–40 Hz total.

{levels_tab}

Per-band medians at η = 1 (3315): the 12.5–40 Hz bands fall by 4–14 dB, the 5–6.3 Hz bands rise by 6–10 dB; at 3376 the 20 Hz band
falls 7 dB and the 31.5–40 Hz bands rise 5–9 dB (the old constant Δ over-corrected the deep 3376 path at high frequency, and
under-corrected the shallower 3315 path: the two tables now cross). `levels_rerun_band_levels_eta1.csv`.

**Low-band sensitivity** (not pre-registered; run after the result, labelled): the same rerun with the 5–8 Hz rows kept at the OLD
values (RAM at 5–8 Hz has not been run; those rows carry the clamped 10 Hz Δ): matched-filter share at η = 1e-3 3315 9.8 → 2.8 %,
3376 17.2 → 12.7 %, 3275 16.6 → 15.5 %, 3274 and 3250 0 → 0; at the anchor 3315 0.5 → 0.1 %, 3376 1.9 → 1.0 %, 3275 0.8 → 0.0 %.
The headline (both Perth Canyon loggers at 0–2 % at the anchor, 3–17 % at 1e-3) holds under either low-band treatment; the exact
share at 1e-3 does not, and is quoted as **3–10 % (3315), 13–17 % (3376), 15–17 % (3275)** until RAM runs at 5–8 Hz.
`levels_rerun_sens_lowband_old_detectable.csv`. The rerun's best-receiver table covers the five loggers only and is not a
replacement of the levels note's eight-receiver statistic."""
R["__COVERAGE__"] = """- **(a) Feasible set.** Every run J impact position (74 seeds + supplement) along the arc from 41°S to 20°S (the brief's span; the
  99th-percentile contour of run J lies south of 20°S), at any cross-arc offset the posterior holds (8.5 % of D0′ mass beyond ±60 NM
  per the levels note), any source depth 2–30 m, 5–40 Hz, received at the five loggers.
- **(b) Model's reach.** RAM (2-D, N×2-D along the geodesic, hard fluid half-space, no shear, no 3-D effects, no absorption inside
  the PE but Francois–Garrison restored through the raw KRAKEN term), at 10/20/40 Hz, source 10 m only; the 5–8 Hz, 12.5–16 Hz, 25
  and 31.5 Hz rows are interpolated or clamped in log f from those three (5–8 Hz = reach gap **G-TL1b**); 2 m and 30 m rows take the
  10 m Δ; the 0.5° rows between nodes are interpolated in Δ, with the amendment-1 donor rule across open/blocked pairs (600 rows,
  10 % of covered rows, `ram_grid_mode = jump_similar`). Paths across land or a < 15 m sill are not modelled (as the grid).
- **(c) Proposal's coverage (what was run).** 218 of 253 planned paths complete in all three bands (647 path × band jobs, 0 failed;
  about 19.7 CPU-hours; 6 processes 23:29–03:35 local, with a 40-minute duplicate-run incident at the start, §8). Offset 0: **all 85
  open paths** (22 + 22 Perth Canyon, 13 + 13 Portland, 15 Scott Reef); −30 NM 66 of 84 (3315 18/22, 3376 18/22, 3274 8/13, 3275
  8/13, 3250 14/16); +30 NM 61 of 84 (17/22, 17/22, 7/13, 7/13, 13/15). Table rows covered: 3315 and 3376 60 % (offset 0 100 %),
  3274 34 %, 3275 33 %, 3250 41 % (offset 0: 100 % of the open rows at every logger; the uncovered offset-0 rows are land /
  shallow-sill rows that keep their grid status). 35 paths not reached at the 03:35 soft deadline (all at ±30 NM; mask
  `imos_tl_ram_coverage.csv`); they keep the old rule-2 value with `ram_grid_covered = False`.
- **ESS.** The levels rerun uses the levels track's subsample unchanged: Kish ESS 1.90 M of 2 M draws for D0′/p0.5; per-receiver
  blocked mass 0 (Perth Canyon), 0.023 (Portland), 0.880 (Scott Reef, was 0.929: rows that were `no_modes` are now finite but at
  300–470 dB, i.e. still zero energy).
- **Gaps.** G-TL1 (constant Δ) **closed on the offset-0 line and 73 % of the ±30 NM lines**; remaining: G-TL1a (35 ±30 NM paths not
  run), **G-TL1b** (RAM at 5–8 Hz not run; sensitivity bounds above; fix = one more pass at 5 and 8 Hz, cheap: a 5 Hz job costs 1/64
  of a 40 Hz job), G-TL1c (31.5 Hz, 2 m / 30 m sources not run; log-f interpolation and the 10 m Δ stand in), G-TL1d (the 0.5° rows
  rest on interpolated Δ; the amendment-1 donor rule is a heuristic; fix = run the 0.5° nodes, 85 paths at offset 0). G-TL2
  (3376 terminal profile), G-TL-X (offset not used by the levels consumer), G-N2/K5 (ridge-source coupling) unchanged. The 12
  `below_physical_floor` rows at −30 NM / 28.5°S are a defect of Δ interpolation at the 30 m source and are flagged, not fixed."""
R["__DEVIATIONS__"] = """1. **Amendment 1 (after the interim build at 01:40 local, before the levels rerun; disclosed):** across an open/blocked node pair the
   pre-registered linear-in-latitude Δ gave physically impossible values (3275 at 29.5°S, 6.3–10 Hz: 74–83 dB over 4,000 km, because
   the 29.0°S node has Δ = +104 dB). Where the two node Δs differ by more than 20 dB the row now takes the Δ of the node whose raw
   adiabatic value in that band is the closer to the row's own (`jump_similar`, 600 rows = 10 % of covered rows; `delta_jump_db`
   recorded on every interpolated row). Rows below the physical floor on the offset-0 line: 0 after the amendment.
2. **Partial nodes.** A node counts only when all three bands are done (3 partial nodes at the deadline are 'not covered'); the
   pre-registration did not say this explicitly.
3. **Duplicate run (23:29–00:08 local).** The first launch was started twice (a `pkill` that the sandbox refused left the first
   process alive); for 40 minutes two 6-process pools computed the same jobs. Both were stopped by withholding their inputs; the
   81 duplicated rows were byte-identical and were dropped; the single run restarted at 00:13 from the 92 finished rows. Thread
   budget exceeded (12 processes) for those 40 minutes; no result depends on it.
4. **Process count 6, not 4.** The 1-minute load was 80.6 at the very first check (23:10, other tracks), 5.9 at the launch (23:29);
   the pre-registered rule (6 if ≤ 10) was applied at launch. During the run the machine load reached 460–490 from other tracks for
   about an hour (23:45–00:45); nothing was done about it.
5. **Disk.** Free space fell to 11.9 GiB at 01:18 and 12.9–13.1 GiB at 02:35 (Time Machine snapshots, per the parent's message), below
   the operating note's 20 GiB write floor; the run's own writes were small (551 MB in total, almost all per-path bathymetry/sound-speed
   CSVs) and the parent's revised floor of 9 GiB was never reached (watchdog at 30 s; minimum seen 11.9 GiB). No file was deleted.
6. **Soft deadline 03:35** rather than the pre-registered 03:50, to leave time for the build, the rerun, the note and the commits
   inside the six-hour block budget; 112 of 667 queued jobs (35 paths, all ±30 NM) were not reached.
7. **31.5 Hz not run** (timing rule); **low-band sensitivity** added after the result (labelled, §5).
8. The levels rerun used `run_j_levels.py` amendment 2 (file-name, key and receiver switches only; committed with the
   pre-registration before the rerun)."""
R["__REMAINS__"] = """**Superseded by this table, once consumers reload it:** every IMOS row of the levels note (`results/hydroacoustics-run-j-levels.md`
§4, the per-option/p table, the τ sensitivity rows for 3315/3376/3275, the best-receiver statistic, the power-screen shares — the
verdicts stand), the IMOS rows of the TL-grid note's evidence-alone tables, and the IMOS component of block 11 (composition), which
consumed `imos_tl_ramcorr_arc.csv`; the Kadri package's `predictions.csv` IMOS TL columns and flags. The consumers' switch is one
file name (`tl_grid_table.load_table(..., imos_file="imos_tl_ram_arc.csv")`, `run_j_levels.py --imos-tl-file`); the old file is
kept unchanged beside the new one. Rows with `ram_grid_covered = False` (none on the offset-0 line except land/shallow rows) and
`below_physical_floor = True` (12 rows at −30 NM) should be treated as not covered by an offset-aware consumer.

**What remains of G-TL1:** the 5–8 Hz bands (G-TL1b: the single largest residual, 3315 share at 1e-3 between 2.8 and 9.8 %), the 35
±30 NM paths (G-TL1a), 31.5 Hz and the 2/30 m sources (G-TL1c), the 0.5° in-between rows (G-TL1d). One further overnight pass at
5, 8 and 31.5 Hz on the 85 offset-0 paths plus the 35 missing ±30 NM paths (10/20/40 Hz) would close a, b and most of c; about 6
CPU-hours at the rates seen tonight."""
R["__PROVENANCE__"] = """- Code (module branch `hypothesis/hydroacoustics`): `prepare/imos_ram_grid.py` (pre-registration + run / build / accept),
  `prepare/imos_ram_grid_charts.py`, `prepare/run_j_levels.py` (amendment 2), `prepare/tl_grid_table.py` (`imos_file` argument);
  RAM and KRAKEN wrappers reused unchanged from `tl_grid_ram_subset.py`, `kraken_tl.py`, `tl_grid_run_j.py`, `air9_tl_validation.py`.
- Tables (exchange, `mh370-exchange/hydroacoustics/run-j-tl-grid/tables/`, new files beside the old): `imos_tl_ram_arc.csv` (drop-in,
  32,250 rows), `imos_ram_minus_kraken_arc.csv` (654 node × band rows), `imos_tl_ram_coverage.csv` (330 planned paths incl. land),
  `imos_tl_ram_build.json`. Compact copies in `results-data/tl_grid_run_j/` (+ `imos_ram_acceptance_check.csv`, `imos_ram_wall.json`)
  and the levels rerun tables in `results-data/imos_ram_grid/`.
- Raw: `mh370-exchange/hydroacoustics/run-j-imos-ram-grid/` — `ram_grid_rows.csv` (every job: tag, band, TL_RAM, TL_KRAKEN_noabs,
  Δ, wall), `plan.csv`, `paths_meta.csv`, `paths/` (bathymetry, sound speed, info per path: 218 + 35 built), `accept38p5/`,
  `levels-rerun/`, `levels-rerun-sens-lowband-old/`, logs, `SHA256SUMS`. 551 MB; not in git.
- Inputs: run J impacts via the levels track's draws (`run-j-levels/draws`, prereg c360db5, code_revision as its run.json), the
  TL-grid tables (fc825c0..894a9e4; `imos_tl_ramcorr_arc.csv` for the raw adiabatic KRAKEN and the row schema), GEBCO 2026 15″,
  WOA23 March, `data/ocean_paths/request.json` logger positions, Acoustics Toolbox arm64 build (KRAKEN/FIELD), pyram 0.68.0.
- Chart: `results/hydroacoustics-imos-ram-grid-old-vs-new.{png,pdf}` (claude-science-sep29)."""
R["__DNB__"] = """- **done:** G-TL1 closed on the offset-0 line (all 85 open paths, three bands) and on 73 % of the ±30 NM lines; acceptance check
  passed exactly; drop-in table, Δ table and coverage mask issued beside the old files; levels rerun for the five loggers (D0′, p 0.5);
  one comparison chart; this note; coordination entry.
- **next:** (i) RAM at 5 and 8 Hz on the offset-0 paths (G-TL1b; cheap) and the 35 missing ±30 NM paths; (ii) consumers reload with
  `imos_tl_ram_arc.csv` — levels note IMOS rows, block 11 IMOS component, Kadri package `predictions.csv`; (iii) the 0.5° nodes
  (G-TL1d); (iv) G-TL2 terminal-profile check at 3376 with RAM.
- **blocker:** none for this block; the consumers' reload is theirs to run."""
for k, v in R.items(): s = s.replace(k, v)
assert "__" not in s.replace("__CODE_COMMIT__", ""), re.findall(r"__[A-Z_]+__", s)
p.write_text(s); print(len(s))
PYEOF