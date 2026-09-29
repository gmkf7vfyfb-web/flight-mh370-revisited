# Dr Usama Kadri meeting — visual briefing pack

Generated from the archived MH370 estimator and the Kadri hydroacoustic source-recreation bundle. British English is used throughout. Presentation graphics separate source-reported information, conditional model outputs and diagnostics. Publication-trace correlation receives zero evidential weight.

## 01. MH370 overview: known track → range arcs

**Suggested on-slide takeaway:** Radar substantially constrains the early diversion; the later Inmarsat BTO observations constrain range to the satellite, leaving a family of possible tracks and a final seventh arc rather than a unique point.

**Speaker notes:** Open with the distinction between observations and inference. The left graphic is Figure 2 from Large (2019): the route from Kuala Lumpur through IGARI, across Peninsular Malaysia, past Penang and west towards the final primary-radar region. The right graphic is Figure 77 from the same dissertation and shows how successive BTO arcs admit multiple locations and headings. Both graphics retain their SkyVector background and the original ‘Not for Navigation’ status. This slide is context, not a current posterior result.

**Primary graphic:** `assets/01-mh370-overview-dissertation.png`

**Optional supporting graphics:** `assets/01a-dissertation-route-1642-1822.png`, `assets/01b-dissertation-bto-arcs-and-solutions.png`

## 02. Posterior evolution: 00:11 state to conditional impact

**Suggested on-slide takeaway:** The archived release moves from a 00:11 BTO+BFO posterior (purple), through the corrected 00:19 BTO constraint (teal), to a conditional terminal-flight impact family (orange), shown against the seventh arc and search context.

**Speaker notes:** Emphasise that the states are sequential and dependent. The impact contours are conditional on the selected end-of-flight family; they are not a universal crash posterior. The primary release family has a median impact near 00:37:49 UTC and a mean near 38.16°S, 89.41°E. The figure also shows why the independent location posterior is valuable when screening hydroacoustic geometry: it provides an external compatibility distribution without letting the acoustic candidate define its own prior.

**Primary graphic:** `assets/02-posterior-evolution-search-context.png`

## 03. Impact state, timing, energy and received pressure

**Suggested on-slide takeaway:** Earlier impacts are more likely, on average, to retain high vertical energy; longer glides tend towards gentler families, but this is a tendency—not a deterministic mapping. The current acoustic experiment models vertical contact speed and coupling, not impact attitude.

**Speaker notes:** The estimator’s tested family medians span about 0.59–1.71 GJ total kinetic energy and approximately 00:23–00:50 UTC impact times. The reduced acoustic study instead uses normal kinetic energy E_n = ½mv_z² with 174,369 kg as a fuel-exhaustion mass surrogate. It samples four vertical-speed families and coupling from 10⁻⁸ to 10⁻²; one sensitivity prior is centred near 10⁻⁴. Median pressure proxies span 0.025–0.786 Pa at H01W and 0.014–0.439 Pa at H08S. These are amplitude scales, not detection probabilities. Pitch, roll, yaw, horizontal speed, breakup, contact duration, sea state and path-specific response remain unresolved.

**Primary graphic:** `assets/03b-impact-state-to-pressure.png`

**Optional supporting graphics:** `assets/03a-impact-dynamics-comparison.png`, `assets/03c-impact-pressure-by-station.png`, `assets/03d-simulated-pressure-time-series.png`, `assets/03e-simulated-pressure-spectrograms.png`

## 04. Forward and backward analyses answer different questions

**Suggested on-slide takeaway:** Forward modelling starts with impact hypotheses and predicts station observables; backward analysis starts with a coherent measured event and reconstructs compatible source states. Agreement is powerful only when selection and false alarms are handled end to end.

**Speaker notes:** Use the GPS analogy carefully. We can step a template bank across source position, source time and propagation state, but we do not have a known PRN waveform and the two ocean paths can distort the source differently. A matched-subspace or generalised-likelihood search is therefore more defensible than simple pressure-trace correlation. The archived 5 NM grid contains 5,289 source boxes, 32 unweighted scenario templates, 169,248 source-scenario combinations and 338,496 station predictions. All current publication-trace comparisons have zero estimator weight.

**Primary graphic:** `assets/04-two-complementary-directions.png`

**Optional supporting graphics:** `assets/04b-forward-reverse-release-diagnostic.png`

## 05. Signals and intersections already discussed

**Suggested on-slide takeaway:** Two Table 1 bearings cross independent spatial-PDF support, but neither time is a q99 peak in the published H01W trace. The preferred 306.18° candidate meets the seventh arc far north of high posterior density. All H08S examples remain airgun-confounded.

**Speaker notes:** Keep the candidate identities separate. Kadri Figure 9 rectangle 1 is approximately 00:52 UTC at 57°. Rectangle 2 is the preferred approximately 00:54:30 UTC at 306.18°; the prose appears to conflate them. Table 1 includes 00:49:58 at 260.41° and 00:53:31 at 257.58°; their arc crossings lie near 35.88°S and 36.74°S and within 64% and 40% HPD respectively, but the signals are not visually recovered as high local-energy peaks from the published trace. The visually interesting OSCAR pair implies about 00:29:40 UTC, but the H08S feature is boundary/periodic-airgun affected and has a matched-window empirical p-value of 0.632.

**Primary graphic:** `assets/05-potential-signals-summary.png`

**Optional supporting graphics:** `assets/05b-candidate-bearing-and-timing-overview.png`

## 06. Backward method: measured event → source constraints

**Suggested on-slide takeaway:** H01W alone can yield a conditional bearing–arc intersection and source-time distribution. H08S adds a strong independent test through arrival-time difference and a second bearing—provided the airgun field is controlled.

**Speaker notes:** A rigorous backward pipeline begins with raw calibrated triad channels, not digitised plot lines. Detection and beamforming should jointly return arrival time, bearing, coherence and uncertainty. Travel-time and acoustic/AGW model families then map the arrival back to a source-time and spatial band. The seventh-arc intersection and independent location posterior are compatibility tests. When H08S is added, the H01W candidate predicts a narrow arrival/bearing family at Diego Garcia; non-observation can be informative only after station sensitivity and interference-dependent detectability are calibrated.

**Primary graphic:** `assets/06-backward-reconstruction-workflow.png`

## 07. Forward method: impact ensemble → both arrays

**Suggested on-slide takeaway:** Carry each complete impact particle through water-entry, coupling, path and station-response families. Search the raw arrays with the resulting uncertain template subspace and calibrate the maximum over the whole bank.

**Speaker notes:** The first lean spoke already predicts station-specific arrival intervals, coupled-energy, pressure-squared exposure and RMS pressure without reading an observed trace. The next useful scientific increment is to propagate complete weighted impact particles—not a uniform source grid—and replace the range-only pressure law with a source emulator and path transfer functions. Model families must remain explicit: ordinary acoustic versus acoustic–gravity propagation, alternative ocean states, bathymetric coupling and station response are structural alternatives, not ordinary sampling error.

**Primary graphic:** `assets/07-forward-prediction-workflow.png`

## 08. Correlation idea: interesting alignment, failed association control

**Suggested on-slide takeaway:** A visually close H01W–H08S source-time alignment exists near 00:29:40 UTC for an OSCAR-conditioned location, but H08S is dominated by periodic structure and the apparent match is not unusual under matched controls.

**Speaker notes:** This is a useful example of why the complete search matters. The H01W feature is strong in the digitised panel, while the apparent H08S partner sits at the cropped boundary of a 9.93-second airgun train. The boundary-aware matched-window control gives p = 0.632. Across 5,289 cells and 41 propagation offsets, the rank-8 filtered maximum correlation is r = 0.109 versus an IAAFT null q95 of 0.160, scan-adjusted p = 0.964; the unfiltered maximum is r = 0.120, scan-adjusted p = 1.000. The plots therefore motivate a raw-data search but do not establish a common event or source location.

**Primary graphic:** `assets/08a-oscar-source-time-alignment.png`

**Optional supporting graphics:** `assets/08b-oscar-boundary-aware-audit.png`, `assets/08c-filtered-complete-acquisition-scan.png`

## 09. Airgun interference: predict, beamform and subtract

**Suggested on-slide takeaway:** Treat the seismic survey as a moving, directional nuisance source. A vessel/shot navigation log can predict each shot’s emission and station arrival, while the triad geometry provides an independent directional discriminator.

**Speaker notes:** The nearly fixed 9.9-second station cadence probably varies because shots are triggered by distance rather than by a perfect clock and because the vessel and path move. Interpolated high-rate AIS or, preferably, the original navigation/shot log can reconstruct emission times. From the moving source we predict travel time and bearing to each H08S element. Three complementary filters should be compared on held-out shots: a directional beamforming null; cycle-synchronous multi-channel template subtraction; and tightly predicted masks followed by analysis of only genuinely observed, uncontaminated channels/time-frequency bins. Hourly AIS is enough to locate the survey, not to time individual shots.

**Primary graphic:** `assets/09-airgun-nuisance-source-model.png`

**Optional supporting graphics:** `assets/09b-airgun-cycle-energy-distribution.png`, `assets/09c-subsecond-mask-comparison.png`

## 10. Bayesian use: conditional hypotheses now, likelihood later

**Suggested on-slide takeaway:** Use hydroacoustics now as a predictive/conditional layer with zero weight. Promote it to an observable only after raw-array processing, interference modelling, injection recovery and complete-search false-alarm calibration define p(y|x,H₁) and p(y|H₀).

**Speaker notes:** Route A is already defensible: for each existing impact particle, report predicted arrival, bearing and amplitude/waveform intervals and ask whether named source candidates are conditionally compatible. This can guide data requests and experimental design without changing the posterior. Route B is a formal update. It must include the probability of detecting—or failing to detect—each impact family, event association uncertainty, airgun and background processes, and the same selection rule applied to real and null data. Ocean-drift products can remain explicit conditional alternatives; present searched-area geometry is context rather than negative evidence until target-specific probability of detection is calibrated. A named observed-signal model is the firewall between an interesting diagnostic and evidential weighting.

**Primary graphic:** `assets/10-bayesian-integration-routes.png`

## 11. Proposed collaboration and next decisions

**Suggested on-slide takeaway:** Start with a small raw-data pilot that can fail cleanly: reproduce one station/window, recover injected directions and quantify complete-search false alarms before attempting a two-station MH370 association.

**Speaker notes:** Suggested requests for Dr Kadri: raw calibrated three-channel H01W and H08S arrays plus adjacent control windows; channel coordinates, response and clock metadata; the exact Figure 9 processing chain and complete candidate catalogue; an extended reception window covering longer post-00:19 flight; and any available path Green functions or preferred acoustic–gravity propagation model. The first joint deliverable could be a blinded H01W bearing-recovery and false-alarm benchmark. If that works, add the H08S nuisance-source model and two-station association. Even a null result can constrain very high-energy/coupling end-of-flight families if detectability is calibrated.

**Primary graphic:** `assets/11-collaboration-roadmap.png`

## Core equations for an appendix or methods slide

Normal-impact energy surrogate: $E_n=\tfrac12mv_z^2$.

Reduced coupling: $E_a=\eta E_n$, with explicit coupling-family uncertainty.

Forward station model: $\mu_j(f\mid z_k,m,\theta,\phi)=H_{j,m}(f\mid\mathbf{x}_k,\theta)S_m(f\mid z_k,\phi)\exp[-2\pi i f\tau_{j,m}(\mathbf{x}_k,\theta)]$.

A future evidential update requires a named observed-signal model, for example $w_i'\propto w_i\,p(y\mid x_i,H_1)/p(y\mid H_0)$, with association, detectability, interference, selection and false-alarm correction included.

## Source boundaries

- Large (2019) dissertation, Figures 2 and 77; SkyVector backgrounds are credited in the original captions and are not for navigation.
- Kadri (2024) paper and Figure 9 source-reporting bundle: `.sources/kadri-2024-hydroacoustics/`.
- MH370 release posterior and impact products: `runs/mh370/release-v0.1/`.
- Impact pressure values are conditional sensitivity scales, not calibrated detection probabilities.
- The current impact model does not recover attitude or contact duration; schematic impact angles are illustrative only.
- The publication traces are filtered and digitised figure vectors, not raw CTBTO data.
