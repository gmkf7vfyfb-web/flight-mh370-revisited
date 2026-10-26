# Work order — hydroacoustic forward model (coupling, source and propagation) for Monte Carlo simulation

Date: 26 Oct 2026. Issued by the hydroacoustics overview session (8b907e71) at Pete's request. Profile: **Hydroacoustic Module** (version 26 Oct 2026).
Language: ASD-STE100 for work-specific text; standard statistical terms as they are.

## 0. Goal
Make the forward model usable for a Monte Carlo simulation of received signals from the impact posterior. For each simulated impact it must give, at each station: arrival time, bearing, received energy per band, and signal shape in time, each with its error. Write these as simulated-arrivals files that the detection model reads (interface in section 6).
This continues the plan of session c764a583 (26 Oct, phases 1-5, under Pete's rulings P58-P65). Do not repeat its Phase 1. Start from its committed Phase 1 outputs.

## 1. Read first (in this order) and confirm
1. `threads/status/hydroacoustics.md` (governs over older text; lists what is superseded).
2. `results/hydroacoustics/decisions.md`, especially P54, P56, P58-P65.
3. `coordination/HYDROACOUSTICS.md` (inbox).
4. c764a583's Phase 1 outputs in the repository (noise model, airgun level unit audit, bearing check, 777 source physics). If they are not committed yet, stop and tell Pete; do not use artifact-only copies as inputs without saying so.
5. The registry and `hydro_data.sqlite` (read `data_db/README.md`).
Confirm in your first reply: the profile prompt is version 26 Oct 2026; the list of inputs with registry ids (data-readiness rule).

## 2. The propagation grid: what exists, and what must change
What exists (`ex.tl_grid`, results note `results/hydroacoustics-tl-grid-run-j.md`, 22 Oct 2026):
- Source points: 43 rows on the 7th arc from 41.0 S to 20.0 S every 0.5 deg, at cross-arc offsets -30, 0 and +30 NM (passes A and B), plus -60 and +60 NM (supplementary pass C). So it samples up and down the arc and each side of it.
- Receivers: 8 (IMS Cape Leeuwin, Diego Garcia South, Diego Garcia North; IMOS 3315, 3376, 3250, 3274, 3275). 1,032 paths in the mandated grid.
- Method: KRAKEN adiabatic incoherent modes, profiles every 5 km, hard bottom, GEBCO 2026, WOA23 March, third-octave bands 5-40 Hz, source depths 2, 10 and 30 m. RAM correction only for the IMOS rows on ridge paths.
What must change:
- Arc length: extend to the southern end of the arc (43.9 S).
- Receivers: add the OHASISBIO sites (SWAMS, SSEIR, MAD, NCRO, WKER). We hold their published picks and spectrogram bands, so their arrival times and band levels are needed.
- Cross-arc extent: derive it from the run J impact posterior (cover at least 99.9 % of the impact weight on each side). Do not assume +-30 NM. Use a finer latitude step where the loss changes fast (Broken Ridge near 31.5-32 S, the Ninety East Ridge on Diego Garcia South paths).
- Model: the frozen model of step FM2 (P63: no old-model results). Ridge paths use the coupled model (RAM) if Pete has approved that; check decisions.md, and ask him as a lettered question if it is not recorded.
- Outputs: add modal group velocities, so the arrival spread and the signal shape can be predicted. Add the arrival-time error terms and the bearing.
- Source depths: per crash-type family (step FM4), not only 2/10/30 m.
- The acoustic-gravity-wave branch stays separate and is declared deferred, unless Pete rules otherwise.

## 3. Steps
- **FM0 Start-up.** Read section 1. List inputs. Check that the run J impact rows carry the fields the family rules need (speed, flight-path angle, attitude, impact duration tau, energy). If a field is missing, stop that item and report; it is an end-of-flight request through `coordination/architecture.md`.
- **FM1 One forward chain, one definition.** Write the chain: impact energy -> coupling (family prior range) -> source energy spectrum (shape, corner from tau) and source depth -> propagation loss per band -> received energy, arrival time, bearing, shape. Write the unit chain for every quantity (energy, energy spectral density, band level, peak, RMS, exposure, integration time). Two past errors came from this: a 58 dB chart-unit error in the airgun source, and a 7 dB duration error in the South Atlantic check.
- **FM2 Freeze the propagation model.** Take the airgun level fix (c764a583 Phase 1, P65 A1). Improve the ridge case (air7 to Cape Leeuwin: about 55 dB over-blocked by KRAKEN, 18-22 dB by RAM). Possible causes are listed in c764a583: hard bottom with no sediment, no sound around the side of the ridge, coarse bathymetry, airgun position. Freeze one version with a run id.
- **FM3 Re-test all known sources with the frozen version** (P63, P64, P65 C1): Blackman 2001 airguns air1, air7, air8 (negative control), air9; SUS charges 2003; glass spheres 2001/2003; San Juan and FSST shots; F-35A at Wake; Transair 810 (upper limit); Royer event 16. Pool the model error from both oceans with separate parts for level, slope, source and path; ridge paths get their own error until they pass. New caveat text per P65 B1.
- **FM4 Source and coupling per crash-type family** (P59, P65 D1 and F1): source depth range per family from water-entry physics; scaling from 20 t to 200 t (777-200ER); spectrum flat to the corner, then steep (F-35A slope), corner from tau, f^-2 as a second case; implosion branch tested on the glass spheres; coupling prior range per family from all sources with the rules of the coupling-structure note of 24 Oct; remove parameter sets with coupling above 1 (database check K11: 1,420 rows); selection rules from the end-of-flight fields per impact row.
- **FM5 Propagation grid, new version**, as section 2. Give Pete the compute estimate first.
- **FM6 Monte Carlo of received signals.** Sample the run J impact posterior with its weights. For each sample draw family, coupling, source depth and the model-error terms. Write simulated-arrivals files (section 6). Smoke run first (about 1,000 samples), then the full run after Pete approves the compute. Also produce the conditional set for the Kadri locality (P36; the Haixun location is a sensitivity only, P37).
- **FM7 Verify and hand over.** Independent verifier; commit under the repository rule; inbox entry for the detection thread and the overview session.

## 4. Gates and approvals
- Compute: estimate first and wait for Pete (P39, P40). At most 4 threads unless approved.
- No result without an independent verifier and a check table.
- New labels that limit a source need Pete's approval.

## 5. Ownership (two hydro threads run at once)
You own `prepare/forward/` (new), the transmission-loss grids, the source and coupling code, and the simulated-arrivals files. You do not edit `detect/` (the detection thread's package). Data store rebuilds: one at a time; announce in the inbox before and after.

## 6. Interface with the detection model
The detection thread writes `engine/hypotheses/hydroacoustics/interfaces/simulated_arrivals.schema.json` and a validator first (its step D1). The required content is in section 4 of the detection specification (`threads/specs/hydro-detection-model-spec-2026-10-26.md`). Agree it, or ask for changes in the inbox, before FM6. Your files must pass that validator.

## 7. Deliverables
Results notes with check tables and COVERAGE sections; the frozen model version and its known-source re-test; the model-error table; the family source and coupling tables; the new grid; the simulated-arrivals files (smoke, then full); footnoted charts (O-C per known source, received level against noise per station). All committed under the repository rule.
