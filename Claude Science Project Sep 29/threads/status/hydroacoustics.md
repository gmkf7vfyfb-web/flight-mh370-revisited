# Hydroacoustics — current state (status file)

Version: 26 Oct 2026, written by the hydroacoustics overview session (8b907e71). ASD-STE100 for work-specific text.
Owner of this file: the hydroacoustics overview session. Threads do not edit it; they send changes to their inbox entry and the overview session updates this file.

**Rule.** This file governs over older text. Where the brief (`threads/master-prompts/hydroacoustics.md`), the inbox history (`coordination/archive/HYDROACOUSTICS-2026-10-07-to-2026-10-26.md`), an old note, an old profile prompt or a memory row differs from this file, this file is correct. If you find a conflict that this file does not settle, stop that item and ask in your inbox.

## 1. Read order for every hydroacoustic thread
1. This file.
2. `results/hydroacoustics/decisions.md` (Pete's rulings in his words; P01-P72). `proposals.md` holds proposals, not rules.
3. `coordination/HYDROACOUSTICS.md` (the inbox; started again on 26 Oct 2026) and your work order in `threads/work-orders/`.
4. The registry (`results/hydroacoustics/INDEX.md`, `registry/README.md`, the module registry) and the data store `engine/hypotheses/hydroacoustics/registry/data_db/hydro_data.sqlite` (read `data_db/README.md` first).
5. The brief, for background and the contract. Its superseded parts are in section 5.

## 2. Where things are (the one repository)
- Data: `hydro_data.sqlite` on branch `hypothesis/hydroacoustics`. It is the data source of record (P53). It changes only through its build scripts. Since 26 Oct 2026, new data are added through `registry/data_db/imports.yaml` (one block per source file) and a rebuild.
- Results: `results/hydroacoustics/<run id>/` on `claude-science-sep29`, and `results-data/<run id>/` on the module branch, each with `manifest.json`.
- Status of every item: the project registry (`registry/REGISTRY.json`, module `hydroacoustics`, ids `hydro.<id>`) and the module registry. Read the registry, not memory.
- Repository rule for all threads: `coordination/architecture.md`, entry of 2026-10-26 (P62, P66).
- Import of 26 Oct 2026 (done; sub-agent d8445a3f): 24 import blocks in `imports.yaml` (stage 3, `build_imports.py`) and the noise caveat fixes C1-C3 (stage 4, `build_noise_fixes.py`); one command rebuilds all stages (`rebuild_all.sh`, about 1 min). Data store SHA-256 e0442acebc6c112e4b062a97349dda80af70f4b2253f7b56f19bba40645caf91, 182 checks (179 PASS, 3 REVIEW: K09, K11, I08c). Commits: module branch 8a65657 and 4452f265; project branch 573a4588. Run folders: `repository-import-2026-10-26` (inventory of 1,399 items), `noise-caveat-fixes-2026-10-26`, `kadri-independent-review-2026-10-26`, `status-review-2026-10-26`, `source-survey-supplement-2026-10-26`, `site-noise-review-supplement-2026-10-26`. Not imported: 248 c764a583 artifacts made after its Phase 1 dispatch (19:03:40Z), which that session commits itself.
- Independent verification (session bfafba88, run folder `import-verification-2026-10-26`): V1-V6 AGREE; one MINOR: the C1 1-sigma (0.34 / 0.40 dB) is too small; use about 1 dB. Status changes to CURRENT wait for Pete (section 6).
- 8 March 2014 IMS noise, 5-40 Hz, from the Kadri traces (preferred row): Cape Leeuwin 104.3 dB re 1 uPa, Diego Garcia South 100.4 dB between airgun shots (100.3-101.2 dB with other shot guards), each about +-1 dB. IMOS levels already include the logger gain (C2). IMOS 3315 agrees with CMST Fig. 1 within 0.7 dB (C3 i). OHASISBIO SSEIR and SWAMS3 by transfer from Cape Leeuwin: about 104.0-104.8 dB +-1.6 dB, with the caveat that the transfer assumes the same colour bias at both sites (C3 iii).

## 3. Active threads and work orders (overview kept by session 8b907e71, P72)
| Thread | Profile | Work order | State on 26 Oct 2026 |
|---|---|---|---|
| c764a583 "Aircraft Impact Acoustic Source Survey" | default | its own plan of 26 Oct (phases 1-5, under P58-P65) | Phase 1 running: one noise model, airgun level unit audit, bearing check, 777 source physics. It commits its Phase 1 outputs under the repository rule, then hands over to the forward-model thread. |
| Repository import (sub-agent d8445a3f) and verifier (bfafba88) | default | task text in session 8b907e71 | Done 26-27 Oct. See section 2. |
| Forward model (new) | Hydroacoustic Module | `threads/work-orders/hydroacoustics-forward-model-order-2026-10-26.md` | Not started. Starts when c764a583 Phase 1 is committed. |
| Detection model (new) | Hydroacoustic Module | `threads/work-orders/hydroacoustics-detection-order-2026-10-26.md`, spec `threads/specs/hydro-detection-model-spec-2026-10-26.md` | Not started. Can start now (steps D0-D2 need no forward-model output). |

Ownership, so that two threads do not write the same files:
- Forward model: `prepare/forward/` (new), the transmission-loss grids, source and coupling code, and the simulated-arrivals files.
- Detection model: `detect/` (new package), the known-event association, the injection test bench, the Kadri package.
- Shared: the interface schema `interfaces/simulated_arrivals.schema.json` (new). The detection thread proposes it, the forward-model thread agrees or asks for changes in the inbox, and the overview session records the agreed version here.
- Data store rebuilds: one at a time; announce in the inbox before and after.

## 4. In force (summary; the rulings are in decisions.md)
- Approach: first principles, step by step, do not race ahead (P56).
- Detection model: clean sheet (P57, P69). Known non-MH370 events are part of the detector. Unexplained published events are test candidates, not known sources (P68, P71). The code must run on the data held and on raw data, and Kadri must be able to run it on his raw IMS data with our simulation files (P70).
- Noise: one integrated best-estimate noise model with uncertainty (P61), using Blackman 2003, open raw IMS March 2015-2019, Kadri 2014 traces and the IMOS event-day records (P58). c764a583 builds it.
- Propagation model: find and fix the airgun level error (P65 A1). Model error from all known-source tests in both oceans, and improve the model with all data (P65 C1). Use the new model only; do not use old-model results (P63). Glass spheres are a test case (P64).
- Source and coupling: crash-type families R1 steep, R2 shallow, R3 ditching, I implosion, X break-up (P59). Coupling is a prior range per family from all sources, not one anchor value (P54; Pete 24 Oct). Spectrum "flat to the corner, then steep", F-35A slope, corner from the end-of-flight impact duration, f^-2 kept as a second case, informed by physics for the 777-200ER and tested where possible (P65 D1). Calibration order for crash types: source depth per type, scaling from 20 t to 200 t, glass-sphere implosion test, coupling sampled for each impact row (P65 F1).
- Direction: apply the Cape Leeuwin bearing calibration with its error, show results with and without it, widen the direction error where calibration events are few, show the error ellipse on the arc, cross-check with other source types (P65 E1).
- Swissair 111: a seismic-only cross-check case (P60).
- Data: only data held or directly downloadable; no requests to people or agencies (P65 G1; Pete 23 Oct).
- Diego Garcia North: dropped; blocked from every 7th-arc point (Pete 23 Oct).
- Airgun shots at Diego Garcia South: a label and an interference test, never an exclusion (Pete 23 Oct).
- Kadri: his claimed aircraft detections are a comparison set. The package to him is a give, not an ask; nothing is sent until Pete approves. Defensible wording from the independent review of 26 Oct (session 880dfd82): "Kadri's boxed signals for Transair 810 and Sriwijaya 182 are not arrivals from those crash sites, under water or land-crossing propagation at his own stated speeds." "Kadri erred" is not defensible.
- Compute: estimate first and wait for Pete's approval (P39, P40). Independent verifier before Pete sees a result.

## 5. Superseded or outdated — do not follow these
| Where you may read it | What it says | What is correct now |
|---|---|---|
| Inbox 2026-10-07, item 4; brief §5 | The correlation search must clear about 5.3 sigma per trial | No arbitrary conservative thresholds. Report weak candidates with empirical p-values and caveats (P11, P15). |
| HYDROACOUSTIC_MODULE prompt of 23 Oct, rule 6; registry notes with defect D01 | "Metz-derived 2.26e-3 is pending Pete's ruling" | No ruling is needed. 2.26e-3 is one point on a curve inside the coupling prior range (P54; Pete 24 Oct). |
| Notes and products that use the IMOS 3376 stand-in null for Cape Leeuwin (defect D06) | Cape Leeuwin noise about 96 dB | The stand-in is about 7 dB too quiet. Use the one noise model when c764a583 delivers it. Until then use Blackman 2003 as primary with the open March 2015-2019 levels beside it. |
| Data store rows `noise_estimate`, source kadri2024, 8 Mar 2014, spectrogram colour | Cape Leeuwin and Diego Garcia South 2014 noise | Biased low (colour floor, JPEG). The import of 26 Oct adds trace-based rows and marks the preferred row. |
| Old detection products: M1b matched filter, D1 STA/LTA screens, weak-signal trials of 22 Oct, injection-recovery of run J | Detection probability and candidate lists | Comparison only. The clean-sheet detector replaces them (P57, P69). M1b is amplitude-blind (gap G11-1). |
| `prepare/run_j_levels.py` (reported 26 Oct, not corrected) | Source shape: corner 1/tau90, f^-2 tail | The F-35A raw data imply a corner near 0.19/tau90 and about f^-3.1. At fixed coupling the old shape puts 6-10 dB more energy in 5-40 Hz. Do not use run J levels for results. |
| Transmission-loss grid of 22 Oct (`ex.tl_grid`) | The whole-arc grid | Usable as a starting point only. The forward-model work order lists its gaps (no OHASISBIO receivers, ends at 41 S, adiabatic model on ridge paths). Re-run with the frozen new model (P63). |
| Inbox entries before 23 Oct about candidates A-F and the 21-22 Oct overnight products | Candidate lists, "strongest pair" | Withdrawn (registry D10 and the 23 Oct clean-up). |
| Memory rows that call decisions B-F "still open" | Open decisions | Decided on 26 Oct (P65). |
| Kadri replication note of 25 Oct, AirAsia 8501 | "517 s early" | The timing argument does not hold under land-crossing propagation. Only the 220 degree bearing remains (review of 26 Oct, 880dfd82). |

## 6. Open items for Pete (lettered questions are put to him by the thread that owns the item)
- Detection model specification: review of the draft (questions A and B in the spec).
- Decision C (put to Pete 26 Oct): c764a583 commits Phase 1 and stops, the forward-model thread takes phases 2-5 and the detection thread takes the detection test (recommended); or c764a583 continues to phase 5.
- Import follow-ups (from the import and its verifier): accept the trace rows as the preferred 8 March 2014 level with about 1 dB uncertainty; set the verified import items to CURRENT; whether the OHASISBIO transfer needs a second calibration point; whether hydro_data.sqlite (now 41 MB, a new git blob at every rebuild) moves to the large-file host; check the 1-s start-time anomaly of IMOS record 531A728A and the 3315 160-240 Hz gain-table row; base-package coupling row CV01 still says 'one-pole f^-2' (check I08c, for the forward-model thread).
- c764a583 Phase 1 results: to be reported by that session.
- Brief consolidation: the brief has layered amendments (8 Oct, 9 Oct, 21 Oct, 23 Oct). The overview session proposes one consolidated brief after the two new threads start. Not yet approved.
