# Hydroacoustics work order — 21 October 2026

Issued after Pete's review of 21 Oct 2026. Brief: `threads/master-prompts/hydroacoustics.md` (Refresh v2 governs).
Inbox: `coordination/HYDROACOUSTICS.md`. Reply channel: `coordination/architecture.md`. Module branch:
`hypothesis/hydroacoustics` (head 77b4b49 at issue). Results notes go to `results/hydroacoustics-*.md` on
`claude-science-sep29`; code and data under `engine/hypotheses/hydroacoustics/` on the module branch.

Impact set: **run J** (74 seeds, 313,599,968 rows) plus the northern supplement (`reduced/impacts-ruleB.npz`).
Latitude span for everything: north to 20°S or the 99th-percentile contour, whichever is more northerly.
Both Kadri times everywhere: "text time 00:52:03" and "caption time 00:54:30".
Every statistic on data is pre-registered (commit before the first number). Every result carries caveats C1 and C2.

## Order of work (dependencies are binding; otherwise run in the order given)

| # | Block | Depends on | Compute | Disk | Output |
|---|---|---|---|---|---|
| 0 | Restore the module working copy; read inbox; confirm run J paths on the Mac | — | minutes | < 1 GB | — |
| 1 | **Digitisation inventory and extraction** (brief Refresh §4): Royer 2016 figures and event table; Blackman Fig. 23 at higher resolution (air1–air8); Brown 2026 F-35A waveform/spectrum; Kadri 2017/2019 traces and tables; San Juan papers; CMST 2014. Manifest with source, page, method, resolution, check. | — | light | < 1 GB | `results/hydroacoustics-digitised-sources.md` + manifest CSV |
| 2 | **TL grid to 20°S**, bathymetry-following (GEBCO/WOA23), all receivers, and the whole-arc prediction grid (arrival time, level, spectrum, blockage) — gives the evidence-alone view | 0 | 30–60 min | < 1 GB | `results/hydroacoustics-tl-grid-run-j.md`, grid files |
| 3 | **Run J windows and levels**: per station, per 00:19 option (D0′, D2, D3, D4), p ∈ {0, 0.5, 1}, η over four decades, both branches (SOFAR, AGW); SNR at best unblocked receiver; power screen (drop receivers that cannot detect anything before any recording is read) | 2 | 30–60 min | 1–2 GB | `results/hydroacoustics-run-j-windows.md` |
| 4 | **Pre-registration** of all searches in 5 (windows, bands, detectors, thresholds 0.3/0.1/0.05, background definition, both Kadri times) | 3 | none | — | prereg commit on module branch |
| 5 | **Searches on data held**: IMOS five loggers; digitised H01W panels a, b, c and H08S d, e; Kadri Table 1 (19 rows); the six poster boxes; Royer events B, D1, D2; infrasound as a declared no-information row | 4 | 30–60 min | < 1 GB | `results/hydroacoustics-searches-run-j.md`, candidate table |
| 6 | **Charts** (Refresh §10): noise vs full predicted-level distribution per station with detectable fraction (and after Kadri's 5–40 Hz chain); timelines with 50/90/99% bands, data windows, both Kadri times; updated versions of every earlier chart; math-check fixtures and second implementation | 3, 5 | minutes | MB | PNG+PDF in `results/`, footnoted |
| 7 | **Injection-recovery** across the full η range at every unblocked receiver, with real background; P_D against received level — the gate | 3; compute slot from end of flight | 1.5–2.5 h heavy | 1–2 GB | `results/hydroacoustics-injection-recovery-run-j.md` |
| 8 | **Weak-signal method trials** (Refresh §7) on ground-truth cases first, then H08S airgun suppression; each with false-alarm rate on real background | 1 | 1–3 h | 1–3 GB | `results/hydroacoustics-weak-signal-methods.md` |
| 9 | **TL recalibration** (Refresh §9 a–d): EW0112 + F-35A source spectrum; slope criterion pre-registered; air1–air8 if 1 delivers; air7 N×2D | 1 | 1–2 h heavy | < 1 GB | `results/hydroacoustics-blackman-validation.md` addendum |
| 10 | Optional: background set 98 → 400 realisations (p floor 0.0101 → about 0.0025) | 5 | 1–2 h | < 1 GB | — |
| 11 | **Composition**: two-site coincidence, 95% upper limits, Bayes factors per conditional, coverage table; likelihood columns only if 7 passes the gate, else zero with labels | 5, 7 | 10–20 min | < 0.5 GB | note + exchange columns |
| 12 | **Kadri package update** (prepare only; nothing sent before Pete approves), with the questions: which panel (a) boxes denote; text vs caption time; Royer raw-data request | 3, 5 | none | MB | `prepare/kadri_package/` |

Totals: about 7–12 h compute (3–5 h heavy), roughly 3–4 working days of thread time, about 5–10 GB of new disk.
Blocks 1, 2 and 8 are independent of each other and may interleave. Nothing heavy starts without a compute slot
posted to `coordination/END_OF_FLIGHT.md` and acknowledged, or a 4-thread start as the fallback.

## Rules that apply to every block
- Pre-register before looking; each observation used once per run; declared IDs.
- NaN means not computed. A non-detection where nothing was detectable is not evidence.
- Candidates are generated at the screen level and reported with significance labels and caveats (Refresh §2).
- Every results note has a COVERAGE section (feasible set, model reach, proposal coverage, gaps, ESS).
- Charts: no project jargon in titles, axes or legends; two footnotes (STE100, technical) with source posterior,
  00:19 option, p, η, caveats C1/C2, data provenance (digitised where digitised).
- Report unconverged as unconverged. Smoke runs are never quoted as evidence.
- End every turn with: done / next / blocker. Pull and re-read the inbox before every commit.

## Diagnostic already run (21 Oct, review session; exploratory, not pre-registered, on the digitised Fig. 9 traces)
The 9 Oct fixed detector (STA/LTA on squared pressure, STA 1 s, LTA 20 s) applied to panel (a) at about 19
samples/s: maximum ratio inside the four poster boxes 1.71, 2.70, 2.15, 2.38; RMS inside the boxes +0.0 to +0.4 dB
against the whole panel; maximum outside the boxes 1.94. Panel (c): box (1) 4.69 at 00:52:03; box (2) 2.38 at
00:54:28. So the panel (a) features are below the fixed ratio-3 threshold on the plotted trace, and box (2) of panel
(c), which the author marks, is also below it: a fixed single-station threshold removes an author-marked candidate.
Under the screen-level stance these are carried as candidates with their labels. The digitised traces are the plotted
waveform decimated by the figure, so this test has limited power; the raw-data request to Kadri stands.

## Opening message for the module thread (paste as the first message on the HYDROACOUSTIC_MODULE profile)
Hydroacoustic Module: read `threads/master-prompts/hydroacoustics.md` (Refresh v2 governs), then
`threads/work-orders/hydroacoustics-order-2026-10-21.md`, then `coordination/HYDROACOUSTICS.md`. Work the order
from block 0. Pre-register before any statistic. Post a compute-slot request to end of flight before block 7.
