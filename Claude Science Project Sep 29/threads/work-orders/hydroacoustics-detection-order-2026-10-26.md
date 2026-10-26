# Work order — hydroacoustic detection model (clean sheet), known-event association and the package for Kadri

Date: 26 Oct 2026. Issued by the hydroacoustics overview session (8b907e71) at Pete's request (P57, P68-P71). Profile: **Hydroacoustic Module** (version 26 Oct 2026).
Language: ASD-STE100 for work-specific text; standard statistical terms as they are.

## 0. Goal
Build the detection model in the specification `threads/specs/hydro-detection-model-spec-2026-10-26.md`. It tests simulated received signals against the data, gives a Bayes factor for each simulated impact, checks every candidate against known non-MH370 events, runs on the data held and on raw data, and becomes a package that Kadri can run on his raw IMS data with our simulation files.
The specification is a draft. Step D0 is to develop it with Pete until he approves it. Do not write production code before D0 is approved; small reader and format tests are allowed in D0 if they inform the spec.

## 1. Read first (in this order) and confirm
1. `threads/status/hydroacoustics.md` (governs over older text; section 5 lists what is superseded, including the old detectors).
2. `results/hydroacoustics/decisions.md`, especially P11, P15, P56-P72.
3. `coordination/HYDROACOUSTICS.md` (inbox).
4. The specification.
5. The registry and `hydro_data.sqlite` (read `data_db/README.md`): noise tables, the known-events and source-type tables, the Royer labelled set, the airgun shot templates, the Cape Leeuwin bearing calibration, the false-alarm tables (the import of 26 Oct adds the last five; if they are not there yet, say so).
Confirm in your first reply: the profile prompt is version 26 Oct 2026; the list of inputs with registry ids (data-readiness rule).

## 2. Steps (gates as in section 11 of the specification)
- **D0 Specification.** Go through the specification with Pete. Put open choices to him as single lettered decisions, recommendation first (questions A and B are already in the spec). Check the raw formats Kadri may hold: support all of miniSEED, CSS 3.0 (wfdisc), SAC and GSE2 / IMS1.0, so that we need to ask him nothing. Pete approves -> D1.
- **D1 Interface.** Write `engine/hypotheses/hydroacoustics/interfaces/simulated_arrivals.schema.json` and a validator, from section 4 of the spec. Post it in the inbox for the forward-model thread. Record the agreed version in the inbox; the overview session records it in the status file.
- **D2 Readers** (forms F0-F4) with test V5. Use open EarthScope IMS files (Dec 2014 onward) as references; convert one to CSS 3.0, SAC and GSE2 with ObsPy and check that every reader gives the same Pa values.
- **D3 Statistics and nulls.** T1-T5 as in the spec. Null distributions from March 2015-2019 raw IMS, the IMOS background records and off-window event-day data. Pre-register each statistic.
- **D4 Injection test bench** (this is Pete's approved A1 test, P58). Inject predicted signals into real noise at Cape Leeuwin and Diego Garcia South (March 2015-2019) and into the IMOS background, from strong to about 0 dB signal-to-noise, at the noise levels of the one noise model (c764a583) and its sources (Blackman 2003, 2015-2019, Kadri 2014). Until the forward model delivers shapes, use the measured F-35A shape and parametric shapes, and say so. Run the old M1b detector on the same bench as a comparison.
- **D5 Known-event association** (spec section 7; test V4) and real known arrivals and negative controls (V2, V3).
- **Pete review.** Then **D6**: pre-registered run on the 8 March 2014 data held (raw IMOS, Kadri and Royer panels, picks), with simulated arrivals from the forward model.
- **D7 Kadri package dry run** (V6) from a clean environment. Nothing is sent until Pete approves.

## 3. Gates and approvals
- Compute: estimate first and wait for Pete (P39, P40). At most 4 threads unless approved.
- Pre-register before computing any statistic on 8 March 2014 data. Label anything added afterwards as post hoc.
- No result without an independent verifier and a check table.
- No conservative thresholds (P11, P15). An airgun coincidence and a known-event match are labels with probabilities, never exclusions.
- Absence wording: "no transient exceeded the pre-registered false-alarm level, with limited power", with injection power, 95 % upper limits and the Bayes factor.

## 4. Ownership (two hydro threads run at once)
You own `detect/` (new package, inside the module folder; plain-text README, no .md in engine/), the interface schema and validator, the injection bench and the known-event association. You do not edit `prepare/forward/` or the transmission-loss grids (the forward-model thread's). The old `prepare/gates/` and M1b code stay as they are, for comparison. Data store rebuilds: one at a time; announce in the inbox before and after.

## 5. Deliverables
The approved specification; the schema and validator; the readers with tests; the statistics, nulls and injection results (detection probability against received level, per station, band, data form and family); the known-event association with its test; the 8 March 2014 run (after Pete's review); the Kadri package with its dry-run record. All committed under the repository rule, with footnoted charts and check tables.
