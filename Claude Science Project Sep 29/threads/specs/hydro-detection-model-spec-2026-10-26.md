# Hydroacoustic detection model — specification (draft for Pete's review)

Date: 26 Oct 2026. Status: DRAFT, not approved. Written by the hydroacoustics overview session (8b907e71) from Pete's rulings P56, P57, P63, P68-P71. The detection thread (work order `threads/work-orders/hydroacoustics-detection-order-2026-10-26.md`) develops it.
Language: ASD-STE100 for work-specific text. Standard statistical terms are used as they are.

## 0. Why a clean sheet
The old detection chain is not fit for use as evidence:
- The M1b matched filter normalises amplitude. Background windows score 0.93-0.98, so a real San Juan arrival at 16-24 dB signal-to-noise ranks only 2nd to 3rd (gap G11-1).
- Detection probability was measured only for strong arrivals. Below about 15 dB signal-to-noise it is not measured.
- The run J injection used a wrong coupling anchor (defect D01) and a noise stand-in that is about 7 dB too quiet at Cape Leeuwin (D06).
- Candidates that coincide with airgun shots were ranked as detections (D02).
The new model keeps the parts that are sound: the empirical noise data, the same-season false-alarm background (open raw IMS, March 2015-2019), the Royer labelled arrivals (20 events x 42 receivers), the Cape Leeuwin bearing calibration, the Diego Garcia South airgun templates, and the known-events catalogue.

## 1. What the model does (plain statement)
For each simulated impact, the forward model predicts what each station should record: when, from which direction, how loud in each frequency band, and with what shape in time. The detection model asks one question of the data held: **how much more probable are these data if that predicted signal is present, than if only noise and known non-MH370 sources are present?**
The answer is a Bayes factor for each simulated impact. A detection list is a by-product: it lists the times and stations where the data favour a signal.
The same code runs on three kinds of data:
1. the data we hold for 8 March 2014 (raw IMOS loggers; digitised Kadri and Royer panels; published picks);
2. open raw IMS data (EarthScope, Dec 2014 onward), for calibration and tests;
3. Kadri's raw IMS data for 8 March 2014, run by Kadri himself with our code and our simulation files (P70).

## 2. Hypotheses and the statistic (first principles)
- H0: data = noise + known non-MH370 sources.
- H1(theta): data = noise + known sources + the MH370 signal s(theta). theta is one simulated impact with its nuisance parameters: coupling draw, source depth, model-error draws (level, slope, path), timing error, bearing error.
- For a station k and a predicted window w, the detector computes a statistic T_k (section 5). Its distribution under H0, f0(T), comes from real noise (same-season raw data, event-day IMOS records). Its distribution under H1, f1(T | received level), comes from injection of the predicted signal into real noise (the A1 test bench).
- Station Bayes factor: B_k(theta) = integral of f1(T_k | L) p(L | theta) dL / f0(T_k), where p(L | theta) is the predicted received-level distribution with the model error sigma_model.
- Several stations: the stations are combined through the predicted arrival-time differences and bearings, which are fixed by the source position up to their stated errors. This known structure is the main source of gain for weak signals (Pete's analogy: a known code lets GPS track a signal below the noise). The combined factor is not a product of independent station factors when the noise is correlated; the thread measures the correlation on 2015-2019 data and states the rule before it computes.
- Non-detection: when the data favour H0, B < 1. For loud predictions B falls fast, for faint predictions B stays near 1. So the model gives upper limits on the source energy at each location, not exclusions (Pete's rule on absence).
- Known sources enter H0 through the association test of section 7. They reduce the support for H1 in proportion to the probability of the association. They never delete a candidate.

## 3. Data forms and readers
Each reader returns one common object: `Observation(station, elements, t_start_utc, sample_interval, values, band, units, calibration_state, gap_mask, provenance(sha256, registry id))`.
| Form | Data | Reader | Observation model |
|---|---|---|---|
| F1 | Raw continuous IMS hydrophone triads, 250 Hz | miniSEED (EarthScope FDSN), CSS 3.0 (wfdisc plus .w files, as distributed by the IDC), SAC, GSE2 / IMS1.0. Use ObsPy readers; response from StationXML, or calib/calper in wfdisc. Output in Pa. | Pressure time series per element; array processing for bearing, with the Cape Leeuwin calibration (with and without, P65 E1). |
| F2 | Raw IMOS loggers, 6 kHz, 307 s every 15 min | The module's existing .DAT reader; clock correction (true UTC = logger time - e(t)); frequency-dependent gain; 8 Hz hardware high-pass. | Pressure time series with gaps. The likelihood uses only the recorded time. No bearing. |
| F3 | Digitised published traces (Kadri 2024 Fig. 9 and Fig. S1) | CSV tables in hydro_data.sqlite | Envelope of a 5-40 Hz filtered trace at about 15 samples per second. Amplitude scale caveats per panel (for example the +8.8 dB step in Fig. 9 panel e). |
| F4 | Digitised spectrogram band levels and published picks (Royer 2016, CMST 2014) | CSV tables in hydro_data.sqlite | Band energy against time (seconds resolution); picks as point events with timing error. |
A synthetic-data reader (F0) writes and reads the same object, for tests.

## 4. Input from the forward model (interface)
File: one simulated-arrivals set per forward-model run id. Format: Parquet tables plus a JSON schema (`engine/hypotheses/hydroacoustics/interfaces/simulated_arrivals.schema.json`). Units in every column name or in the schema.
Per simulated impact i (with its posterior weight) and station k:
- branch (deep sound channel or acoustic-gravity wave; never blended);
- path class and blocked flag;
- arrival time: mean and standard deviation, with the terms listed (sound speed, path, clock, source time);
- bearing at arrays: mean and standard deviation;
- received energy spectrum per third-octave band, with the sigma_model terms (level, slope, path, source) kept separate;
- envelope shape: onset, rise time, duration (from modal dispersion and the source duration tau), or a template file reference;
- the parameters behind the prediction: family, coupling draw, source depth, energy, tau.
The forward-model thread produces these files. The detection thread writes the schema and a validator first (work order step D1), and the forward-model thread agrees it or asks for changes in the inbox.

## 5. Detector statistics (candidates; the injection test chooses)
Each statistic is written down (pre-registered) before it is run on 8 March 2014 data.
- T1 band-energy excess in the predicted window, relative to the local noise. Amplitude-aware. The robust baseline.
- T2 envelope matched filter with the predicted shape, amplitude kept (not normalised), with a search over the timing error only.
- T3 array coherence and bearing consistency (IMS triads only, F1 data).
- T4 multi-station stack along the predicted arrival-time differences for a source position (a beam over source position). This uses the known structure of section 2.
- T5 airgun-interference residual at Diego Garcia South: subtract the shot template, then test the excess energy (primary), deficit and shape residual (Pete 23 Oct).
- For F3 and F4 data only T1, T2 (on envelopes) and T4 apply.
The old M1b detector runs beside these on the same test bench, as a comparison (not as a candidate).

## 6. Noise and false-alarm input
- Noise levels: the one integrated noise model (c764a583, P61), per station, band and arrival window, with its uncertainty.
- Null distributions f0(T): from same-season raw IMS data (March 2015-2019, Cape Leeuwin and Diego Garcia South), from the IMOS 14-day background records, and from event-day data outside the predicted windows. Time-shift and held-span permutation nulls are both reported.
- For F3 and F4 data, the null comes from the same panels outside the predicted windows. The thread states its power limit (minimum p about 1/n).

## 7. Known-event association (Pete's points 4, P68, P71)
- Catalogue: the data store tables for known events (298 catalogued events 6-10 March 2014: earthquakes, icebergs, volcanoes, surveys, whale-call counts), airgun shots at Diego Garcia South, Royer's located events, island-seismometer associations, and the source-type table (41 types with band, duration and repetition).
- For each candidate (station, time, bearing, band, duration, spectral shape) and each catalogued source: compute the predicted arrival at that station (earthquakes: seismic leg plus water leg, conversion-point error; others: water path), the predicted bearing and the expected band and duration. Then compute a match likelihood from the time, bearing and spectral residuals divided by their errors.
- Output for each candidate: the list of approximate matches, each with its match likelihood, the association probability, and the chance-association rate from a time-shift control.
- Sources without a position (whale choruses, ice noise, ship noise) enter H0 as class models of band, duration and repetition.
- **Unexplained published events are test candidates, not known sources.** Royer's events B, C1-C4, D1, D2 and his other "uncertain" events, the CMST detection at Cape Leeuwin 01:34:50 UTC, and Kadri's transients are scored against H1 like any other candidate. They are never used to explain a candidate away.
- An association is a label with a probability. It is never an exclusion.

## 8. Outputs
- O1: for each simulated impact: log Bayes factor per station and combined, with the terms that make it.
- O2: candidate list with no conservative threshold (P11, P15): every window graded by empirical p (screen, mark, report levels as labels), with its known-event matches.
- O3: detection probability against received level, per station, band, data form and crash-type family (from injection).
- O4: 95 % upper limits on source energy or coupling for each location band, with power.
- O5: input to the composer only when the architect's conditions for a likelihood are met (7 Oct ruling: injection-recovery P_D against received level first). Until then the module returns zero.

## 9. Tests before any use on 8 March 2014 data
- V1 injection into real noise (the A1 bench): Cape Leeuwin and Diego Garcia South March 2015-2019; IMOS background; signal-to-noise from strong down to about 0 dB; all statistics and the old M1b on the same bench.
- V2 real known arrivals: the Royer labelled set; San Juan and FSST shots at Ascension; the F-35A at Wake; Transair 810 (upper limit); Royer event 16 (confirmed by island seismometers); Blackman airguns and glass spheres (published values only).
- V3 negative controls: time-shifted windows; templates for wrong source positions.
- V4 known-event association: correct-association rate on catalogued earthquakes in 2015-2019 raw data; chance rate.
- V5 readers: each format reads a reference file and gives the same Pa values as an independent read (ObsPy and the module reader).
- V6 Kadri package dry run: the package runs from a clean environment on open 2015 raw IMS files in each supported format and returns the R1-R4 products.

## 10. The package for Kadri (P70)
- A standalone Python package inside the module folder (`detect/`), with a plain-text README (no .md files in engine/), a pinned environment file, a command-line runner and a configuration file.
- Inputs: his raw IMS files (any F1 format), our simulated-arrivals files (section 4), the known-events catalogue file, and a run configuration.
- Run modes: (a) injection-recovery on his raw data, giving detection probability against received level (R2); (b) noise percentiles in the predicted windows (R3); (c) scoring of the predicted windows and candidate lists with known-event matches (R1); (d) a record of any parameter he changes (R4).
- Outputs: derived products only (CSV and JSON). The raw data stay with him. It needs no network and no access to our repository. Fixed random seeds.
- Nothing is sent until Pete approves the package (existing rule).

## 11. Sequence (gates)
D0 spec approved by Pete -> D1 interface schema and validator -> D2 readers with tests (V5) -> D3 statistics and nulls -> D4 injection bench with the old detector (V1) -> D5 known-event association (V4) and real arrivals (V2, V3) -> Pete review -> D6 pre-registered run on the 8 March 2014 data held -> D7 Kadri package dry run (V6) -> Pete approval to send.
Compute estimates go to Pete before each run (P39, P40).

## 12. Questions for Pete
**A. Form of the result.**
- A1 (recommended): a Bayes factor for each simulated impact, with the detection list as a by-product. It goes straight into the Bayesian chain and also gives upper limits.
- A2: detection lists with p-values only.

**B. Terms for the package to Kadri.**
- B1 (recommended): an open-source licence (for example MIT) with a citation request. It is simple, and he can run and change it freely.
- B2: shared privately for his use only, with no licence.
