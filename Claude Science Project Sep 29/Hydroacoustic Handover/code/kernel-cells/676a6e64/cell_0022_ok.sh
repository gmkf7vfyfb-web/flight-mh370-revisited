cat >> "repo/Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md" <<'EOF'


---

## Refresh v2 — 21 October 2026 (Pete's rulings of 21 Oct; governs where it differs from the text above)

Written by the review session of 21 Oct 2026 after Pete reviewed the brief, the materials and the prior work.
The contract (§2) is unchanged except for the latitude-span note under rule 8. Everything below is binding.

### 1. Impact set, inputs and run names
- **Run J** is the impact set (accepted as a pass by project ruling, 16 Oct). Run I and run-i-dive are superseded.
  The module's run J per-impact columns exist (`mh370-exchange/hydroacoustics/run-j/`, 17 Oct, both τ versions,
  likelihood 0.0 in every row, labelled). The run J northern supplement (`end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz`)
  is part of the set.
- **Inputs confirmed by end of flight (17 Oct):** τ from the `tau90` sidecar is primary; the assumed log-uniform τ is a
  sensitivity. `attitude_v1.npz` carries `bank_deg`, `bank_source` (1 = wings level by model assumption, about half the
  rows) and `n_pulses` (1 in every row). `w_steep` is a diagnostic, never a weight. "Energy transferred" equals total
  kinetic energy: an upper anchor, not an estimate.
- **Sensitivities to carry beside every headline:** the 00:19 option (D0′ primary, D2, D3, D4 beside it), the D4
  energy dependence (P(E ≥ 10 GJ) = 0.50 under D4, all faster than 212 m/s), the 212 m/s speed-limit sensitivity,
  the bank-limit prior, dive probability p (0.5 primary; 0 and 1 beside it), and coupling efficiency η over at least
  four decades.
- Impacts are selected for prediction by predicted SNR at the best unblocked receiver, not by source loudness.

### 2. Reporting and thresholds
- Report the module's evidence three ways: alone on a prior uniform along the arc; combined with the core; and the
  size of the disagreement (ARCHITECTURE.md rule 5; composer.md §0).
- Thresholds: screen at p = 0.3, mark at 0.1, report at 0.05 (ruling, 13 Oct). The floor is set by the background set
  size; enlarge the set, never lower the threshold.
- **Candidate stance (Pete, 21 Oct).** The module works at the limit of detectability. Do not apply conservative
  thresholds to the *generation* of candidates. Generate and report weakly supported candidates at the screen level,
  each with its significance label, its background rate, the receivers that saw nothing, and the caveats C1
  (propagation slope misfit) and C2 (coupling not calibrated). A candidate is a row for other modules to test against,
  not a claim. A claim of detection still needs the §5 arithmetic and two-site coincidence.
- Significance labels travel with every candidate into every table, chart and note.

### 3. Latitude span
Every TL table, prediction grid, window table and chart extends north to **20°S or the 99th-percentile contour of the
prior, whichever is more northerly**. The present TL table (38.46–31.64°S) is a declared coverage gap until extended.

### 4. Data: no raw data from Kadri or Royer is expected
- Test, validate and calibrate on what can be extracted from publications, and on the raw IMOS data held.
- **Digitisation deliverable.** Extract every usable dataset rendered in the PDFs of Kadri (2017, 2019, 2024 with S1,
  and the SnT 2025 poster), Royer (OHASISBIO LDO-201608), Blackman et al. (2004; obtain a higher-resolution scan of
  Fig. 23 so air1–air8 become traceable), Brown et al. (2026; F-35A waveform and spectrum figures), Duncan &
  Dall'Osto (2023), CMST (2014), and the ground-truth cases (ARA San Juan: Nielsen 2021, Vergoz 2021, Kadri 2019;
  AF447; the earthquake calibration events). Keep a manifest with source, page, method, resolution and a
  verification note per row. Label every such dataset as digitised (§2 rule 10).
- Raw IMS data reach the project only through the Kadri collaboration, as derived products, and nothing is sent to
  Kadri until Pete approves it. Request Royer's 2014 raw data (address printed in the report) as part of the same
  approval step.

### 5. Kadri's processing chain
Kadri (2017, 2019, 2024) high-passes at 5 Hz and band-passes 2–40 Hz, then detects by windowed entropy above a fixed
threshold. Every comparison with his traces, and every detectability chart that mentions them, shows predicted
levels **after the same 5–40 Hz chain**, and separately for the bands the module uses itself. His filter removes the
AGW band entirely; his "no signal" therefore says nothing about the AGW branch.

### 6. Named test sets
- **Kadri Table 1** (19 rows, 18 distinct times, 00:38:29–00:55:07 at H01W): test every row against run J windows,
  at both of Kadri's times for the 306.18° row, with the demonstrated bearing-error distribution.
- **The six H01W signals boxed on the SnT 2025 poster.** Panel (c): box (1) about 00:51:10–00:52:50 (text time
  00:52:03); box (2) about 00:53:50–00:55:20 (caption time 00:54:30). Panel (a), labelled "weak": four boxes at about
  00:28:12–00:29:42, 00:30:24–00:31:54, 00:32:30–00:34:00 and 00:35:24–00:36:54. The 7th arc's closest approach to
  H01W is about 1,580 km (about 17.8 min at 1.48 km/s), so panel (a) boxes 1–3 cannot be a post-00:19:29 arc impact by
  the deep sound channel and box 4 is marginal for a source near 28–30°S; score them anyway, report the arithmetic,
  and carry them as a declared "source before 00:19:29 or off the arc" row. Ask Kadri what his panel (a) boxes denote.
- **Royer (OHASISBIO) events B (35.224°S 99.922°E, 00:21:30) and D1/D2 (D2 27.856°S 93.460°E, 01:06:05):** test
  against prediction, power and coverage outputs; NEAMS, nearest the arc, has no data. Add the report to the
  prior-work critique.
- **Infrasound:** a declared "carries no information" row (impact energy 33–2,500 times below IMS infrasound
  thresholds; IS06 March 2014 data not public).

### 7. Weak-signal methods (exploration is in scope; each trial is pre-registered as a detector)
The known structure that replaces the GPS PRN is the propagation model: a dispersion-aware template built from the
modal arrival structure. Methods to try, on the ground-truth cases first (San Juan, F-35A, Blackman shots), then on
MH370 data: predicted-waveform matched filtering; cross-station coherent stacking at predicted lags; cepstral and
modal-dispersion fingerprints; spectral kurtosis and higher-order statistics; time-frequency reassignment and
synchrosqueezing; Bayesian change-point or hidden-Markov detection on band power; stochastic resonance as an
exploratory check. For H08S under the airgun survey: shot-train template subtraction (shot template and pulse-energy
scripts exist), cyclostationary gating on the shot cadence, and the off-cadence residual. Report each method's
false-alarm rate on real background before any MH370 statistic.

### 8. Success and the confluence role
Success includes a genuine, defensible candidate, not only a detectability statement. Hydroacoustics alone will not
locate the aircraft; one weak signal becomes valuable when it coincides with other evidence types (the
Kadri-preferred / Haixun / white-objects confluence is the type sought, not itself a solution). The module therefore
supplies candidate rows with time, locus, weakness label and caveats so that other modules can be asked what they see
there. Hydroacoustics stays labelled predictive-only until the P_D gate is passed.

### 9. Transmission-loss calibration: state and plan
State: KRAKEN adiabatic along the GEBCO/WOA23 path (bathymetry-following, which stays the method), hard bottom, 10 m
source, RAM cross-check. air9: level right (median residual −0.2 dB H01W, +3.2 dB H08S; RMS 7.9 dB, 8.05–8.17 dB on
the shared transport, so NOT VALIDATED against the ≤ 8 dB rule by 0.05–0.17 dB); slope +10.4 ± 0.9 dB/oct (H01W) and
+7.4 ± 0.7 (H08S), common to both stations (1.7 dB RMS each after removing it). air8 explained (ridge, +38 dB). air7 →
H01W 55 dB too lossy (G22). SUS absolute 4–17 dB unsettled (G16, declared-conditional). G17–G19 open.
Plan, in order: (a) air9 source spectrum from the EW0112 near-source calibrated recordings and the F-35A spectral
figures, to separate source from path; (b) re-run the validation under the audit's level, slope and shape criteria,
slope criterion pre-registered; (c) higher-resolution Fig. 23 so air1–air8 become usable; (d) N×2D or 3-D on
ridge-crossing paths, air7 first; (e) extend the TL grid to the §3 latitude span. Every result carries C1 and C2
until (a)–(b) pass.

### 10. Charts (Pete's standing requests; chart rule of 10 Oct applies: no jargon in titles, axes or legends; two
footnotes, STE100 and technical)
- Per station (H01W, H08S, H08N, Perth Canyon 3315 and 3376, Portland 3274 and 3275, Scott Reef): background noise
  percentiles against the **full distribution** of simulated received levels from run J, per band, with the
  detectable fraction stated, per 00:19 option, p and η; a version after Kadri's 5–40 Hz chain.
- Per station: timeline of impact time against arrival window, with the 50/90/99% impact-time bands, the data windows
  actually held (Kadri Fig. 9 panel spans, IMOS 307 s records every 15 min, OHASISBIO sites marked "no data held"),
  and both Kadri times marked.
- Updated versions of every chart the module has produced before (TL predicted vs measured; the Kadri table; the
  loudness maps; the illustrative traces) on run J.
- Math check before publication: a hand-computed fixture for the per-impact writer, the window script and the noise
  conversion, and a second independent implementation of the received-level equation.

### 11. Compute and coordination
The `lockf` rule is retired. Heavy steps (injection-recovery, TL recalibration) need a slot agreed with end of flight;
start at 4 threads and expand as cores free. Keep the 14 GB IMOS background on the Mac. Check `df -k
/System/Volumes/Data` before any write over 1 GB; floor 5 GB free.

### 12. Items of the text above that this refresh supersedes
§2 rule 8 first sentence (core reference values); §3 "three decades"; §4 IMOS inventory; §5 as a reporting threshold;
§7 steps 3–4 where they name run I or stand-ins; §8 Kadri's single time; §9 insofar as raw IMS data were assumed
reachable; §12 lock rule; §13 "IMOS analysis not first pass" (it is now in the main sequence); amendment 1 stands
(Duncan & Dall'Osto's 20–30 dB is not a prior).
EOF
wc -c "repo/Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md"