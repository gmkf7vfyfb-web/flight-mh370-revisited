# Hydroacoustic module: overnight clean-up and registry (proposal v6)

Status: PROPOSAL, not approved. Written in ASD-STE100. Standard statistical and physical terms are used as they are.
Date: 23 Oct 2026. This version replaces v3 (full re-do, 32–49 h of development). Pete rejected v3 because it was too large.

## 1. Scope

1. Keep the 7–20 Oct work in place. Do not archive it. Do not compute it again.
2. Repair only the known defects in the 21–22 Oct products (the overnight tracks, the morning tracks and the Take 2 review).
3. Put all module data, products and constants into one registry.
4. Remove the slop from notes, the brief, the profile and memory.
5. Finish in one overnight run: 12 h end to end, about 1–1.5 h of compute, no 12-thread lock, two agent conversations (one worker, one verifier).

## 2. Data readiness (checked 23 Oct before this proposal)

| Input | Location | Found |
|---|---|---|
| Hydro exchange products (18 folders, run-j-* and others) | ~/Downloads/mh370-exchange/hydroacoustics/ | yes |
| IMOS raw and background records | ~/Downloads/mh370-inputs/hydroacoustics/imos/ (16 GB) | yes |
| GEBCO 2026 grid | ~/Downloads/mh370-ocean-data/gebco/grid/ | yes |
| Metz 2023, EW0112, Gaspin-Shuler PDFs | mh370-exchange/hydroacoustics/sources/ | yes |
| Take 2 review outputs (singles, pairs, triples, Royer cross-ID, signal register) | review session workspace and artifact store | yes |
| Take 2 review check code (airgun, band, land path, Royer) | session cell log, 176 cells (15 airgun/shot, 4 GEBCO, 24 Royer) | yes, as cells, not as scripts |

## 3. What the run does

### Block 1 – Registry (0:00–2:30)

1. Make `REGISTRY.yaml` in the module folder. A script makes the first draft from the exchange READMEs, SHA256SUMS files, module results-data and the source-access ledger. The agent completes it.
2. Each entry has: id, path, sha256, producing commit, units, frequency band, time base, definition (quoted from the README or code, with the line), status and reason.
3. Status values: CURRENT, CORRECTED (old and new values given), SUPERSEDED (pointer to the replacement), KNOWN DEFECT (defect id), UNCHECKED.
4. One constants table. Coupling is recorded as a PRIOR with its sources, not as one constant. The F-35A point from Metz 2023 (2.26e-3, z_s 10 m, with its spread 2.8e-4 to 5.4e-2) is entered as PENDING PETE'S RULING (requested 22 Oct). The value 2.1e-4 is marked "different quantity (Brown/Arons), 10.3 dB low for the module's definition". Other constants: pick sd 10 s ("no located source"); GPS–UTC 16 s; IMOS passband from 8 Hz; Kadri high-pass 5 Hz.
5. A loader (`registry.py`) reads data only by registry id and checks the sha256. A script (`stale.py`) lists each product that uses a RETIRED constant.

### Block 2 – Repair the known 21–22 Oct defects (2:30–6:00)

1. **Checks in code.** Move the Take 2 checks from the cell log into module code, with tests. The tests must reproduce the review numbers: 44 of 47 H08S candidates within 1.5 s of an airgun shot; 1,111 pairs in 2–5 Hz; 201 of 2,000 path points on land from 26.34 S 100.93 E; Kadri 00:52:03 inside Royer's icequake A pick bar. Add: Scott Reef 3250 excluded, earliest-arrival check, coupling ≤ 1.
2. **Airgun shots: a label and an interference test, not an exclusion.** A candidate within 1.5 s of a shot gets the label "coincident with shot" and stays in the register. The test: (a) make a shot template from the neighbouring shots; (b) subtract the scaled template; (c) test the residual for excess energy (constructive), deficit (destructive) and shape distortion (rise, shoulders, decay), against the shot-to-shot variation as the null; (d) test the residual against the predicted impact envelope with the dispersion-aware matched filter. Limit: the H08S data held is Kadri's digitised trace, an envelope at about 14–19 samples/s, not a waveform. The test is therefore on envelope shape. A phase-level separation needs the raw H08S record ("not retrieved — ask Pete"). Use the 10–13 Oct template, shoulder, gap and energy work if it is in the repo. Compute: minutes.
3. **One candidate register.** Run the 21–22 Oct search output through the checks. One file replaces the ranked tables, the potential-signals register and the singles/pairs/triples feasibility files. Compute: about 12 min (recorded ranking time).
4. **Coupling multiples.** Every "× F-35A" multiple gets two columns: against 2.1e-4 (old, different quantity) and against 2.26e-3 (pending ruling). The coupling that each candidate needs is given as a number, so it does not depend on the ruling. This is arithmetic on stored columns (SNR(η) = base + 10 log10 η). Kadri package v3 uses the RAM IMOS table.
5. **Candidates A–F.** Make the summary again from the new register. Keep the corrected candidate A posterior (artifact version 05b063f9) for the verifier to check. Do not make the predicted-loudness charts again.
6. **run-j-gated-v2: no re-run tonight.** Its proposed default column (η marginalised, log-uniform 1e-6 to 1e-2) does not use the anchor. Relabel the fixed 2.1e-4 column. If Pete changes the prior range (section 5a), this column must be made again: about 86 min (recorded composition time).

### Block 3 – Remove the slop (6:00–8:30)

1. Each 21–22 Oct note gets one status header from the registry. Wrong statements are corrected in place, with the old value and the new value. Do not delete text that has history.
2. Make one generated index, `results/hydroacoustics/INDEX.md`, from the registry. It shows what is current and what replaces what.
3. Brief and profile: remove old and conflicting rules (for example, "never ask; record gaps and continue"). Add the registry rule and the stop-on-missing-input rule. Make the profile short.
4. `decisions.md`: only Pete's rulings, quoted, with date and message. `proposals.md`: agent proposals that Pete has not approved.
5. Memory: replace or remove the hydro rows that are wrong or superseded. List each change in the morning report.
6. Write one entry in the coordination inbox.
7. Kadri crash-panel timing check (`kadri_crash_timing_EXPLORATORY.csv`): set its registry status to "EXPLORATORY – model incomplete". Remove every statement in the notes that says or suggests that Kadri's panel times are wrong. Replace it with: "Our straight-path, single-speed arrival model does not agree with some of Kadri's panel times. The cause is not known. It can be an error in our model or inputs." The known limits of our check are: straight geodesic paths; one water speed; no seismic (T-phase) path from shallow sites; impact times and positions not checked against primary investigation reports; H10S position not from the IMS station list; Transair 810 and Lion Air 904 times assumed from the window centre, not read from a marked box.

### Block 4 – Independent verification (8:30–10:30)

1. One verifier agent with a fresh context. It gets only the registry, the register, the notes and the raw files.
2. It checks every registry path, sha256 and quoted definition with a script.
3. It recomputes about 15 key numbers with its own code from the raw files. Examples: the Metz anchor; the IMOS 3315 reproduction of CMST 2014 Fig. 1; the airgun count; the land-path count; Royer A and event 5; the candidate A posterior; P_D at the new anchor; the Pléiades-conditional shares.
4. It reports differences. It does not correct them without a record.

### Block 5 – Morning report (10:30–12:00)

1. One STE100 page: old value, new value and verifier result for each key number.
2. The list of registry entries by status, the open rulings, and the items that the run stopped on.
3. The rest of this block is buffer time.

## 4. Rules for the unattended run

1. Do only the work in this plan.
2. If an input is missing or a test fails, stop that item, record it, and go on to the next item that does not depend on it. Do not use a stand-in.
3. Do not delete files. Do not archive the 7–20 Oct work.
4. Commit after each block. Rebuild coordination files from the fetched branch head before each commit.

## 5. Not in this run (next work cards)

These items are new science, not clean-up. The registry makes each one smaller.

- Validation of the detector and timing on Royer's events and the CMST 01:34 event.
- Search of all held IMOS records, not only the windows.
- The San Juan real-arrival test.
- The amplitude-aware likelihood.
- A pre-registered crash-panel timing test that removes the limits in Block 3 item 7, before any question goes to Kadri.

## 5a. Decisions for Pete (open; no ruling is in the record)

1. Adopt the Metz-derived F-35A point (2.26e-3 with its spread) in place of 2.1e-4. Requested by the module on 22 Oct. Not ruled.
2. The coupling prior range. The brief (amendment 3, 9 Oct; approved with the brief on 21 Oct) says only: log-uniform over at least four decades, with the F-35A value as the upper anchor. The bounds 1e-6 to 1e-2 were the agent's choice. The Metz work shows that the "upper bound" reason does not hold (+2.9 dB, not supported). With 1e-6 to 1e-2, the F-35A point is 0.65 decade below the top, and the 2 m source-depth value (5.4e-2) is outside the range.

## 6. Risks

- The registry quotes the READMEs. If a README is wrong, the registry is also wrong, unless the verifier's sample finds the error.
- Profile update: the platform has refused to CREATE new unrestricted profiles from a session (SEARCHED_AREAS_MODULE, OCEAN_TRANSPORT_MODULE, early October). Updates to existing profile prompts have worked (21 and 22 Oct). If an update is refused, the text is saved as an artifact for Pete to paste in Customize.
- Development times are estimates. Compute times come from recorded run times on 22 Oct.

## 7. Before Pete leaves

1. Approve this plan (or change it).
2. Approve the GitHub credential for commits.
3. No new network or folder access is necessary.
