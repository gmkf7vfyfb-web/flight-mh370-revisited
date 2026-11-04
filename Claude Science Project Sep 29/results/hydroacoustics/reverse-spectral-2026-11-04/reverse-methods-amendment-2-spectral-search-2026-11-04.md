# Amendment 2 to the reverse-sensing methods specification: spectral-template search (S10) and source classifier

Date: 4 November 2026. Source: Pete Large's request of 4 November 2026. Code: `reverse_spectral.py` version 1.0.0 (the S10 part is fixed by this amendment; its sha256 is given in A2.12). This amendment adds one screening detector (S10) and one source classifier. It changes no other part of the specification (version 1.0) or of Amendment 1.

## A2.0 Status and origin (read this first)

1. **S10 is post hoc in origin.** It was added AFTER the screening track had begun on the arrival windows (detectors S1-S8, frame b63ed0c2). Some screening results were known when S10 was proposed. In particular, the screening reported one short burst at Portland 3275 at about 01:07:40 UTC with a falling spectrum, rich at 10-16 Hz. Therefore S10 is not a blind test in the sense of section 0 of the specification.
2. **The parameters of S10 are fixed BEFORE S10 runs.** This document and the code it names are committed before S10 opens an arrival window. The author of this amendment did not read any arrival-window data for this work. The only data read before this commit were off-window data: same-day records outside each station's arrival window plus a 120 s margin, and background days 1-15 March 2014 (A2.3.4).
3. **Consequence for reporting.** Each S10 result carries the label "post-hoc method (fixed before running)". An S10 result cannot alone meet the detection claim of section 10 of the specification. It can contribute to a ranked candidate, or to a multi-method agreement. The look-elsewhere correction across methods (section 10) counts S10 as one more method.
4. **Steer from Pete Large, 4 November 2026 (applied before S10 or the classifier ran on any arrival window).** The impact definition is NOT centred on the Metz et al. (F-35A) shape. That shape is informative, but it comes from a much smaller and different aircraft (about 20 t, against about 200 t for a 777-200ER). A larger aircraft can have a longer impact and can break up, so its corner frequency and slope can differ a lot. The impact-like class is therefore deliberately LOOSE:
   - broadband (energy spread across the band; no narrow tones, harmonics or frequency sweeps);
   - overall slope anywhere from flat to steeply falling; corner anywhere from below 1 Hz to about 20 Hz;
   - impulsive or fairly fast onset; duration from less than 1 s to about 60 s after channel spreading;
   - no regular repetition; level free.
   The Metz et al. shape is one labelled member of the S10 template bank, not its centre. The bank is widened to span the loose class (A2.3). The steer also sets an asymmetry rule for the classifier (A2.7.5). A known class needs positive evidence of that class's features, and removal needs a combined known-source probability of 0.95 or more. "Impact-like" needs only broadband, impulsive and not a known class. Anything not classified with confidence is "unclassified" and is KEPT. Earthquake and impact overlap is resolved mainly by catalogue timing, then by onset shape and duration. Ambiguous cases are kept.
5. Propagation is used for TRAVEL TIME ONLY. S10 uses no transmission-loss model and predicts no received level. The level is a free parameter.

## A2.1 Data

| Station | Data held | S10 | Classifier |
|---|---|---|---|
| Perth Canyon 3315, 3376; Scott Reef 3250; Portland 3274, 3275 | raw IMOS, 307 s every 900 s, 8 Hz hardware high-pass; used at 250 Hz (6 kHz decimated by `resample_poly(1, 24)`, as the station data package) | yes | full feature set |
| Cape Leeuwin H01W, Diego Garcia South H08S | Kadri 2024 Fig. 9 envelope vertices | no (no spectrum) | envelope (time-shape) features only |
| Cape Leeuwin, SWAMS3, SSEIR | Royer 2016 spectrogram colour readings | timing labels only, NO p-value | no |

**Band.** S10 uses 8-100 Hz. Reasons: (a) below 8 Hz the hardware high-pass removes the ambient field, so content there is not usable; (b) the 250 Hz analysis rate gives a Nyquist of 125 Hz and the anti-alias filter is flat to 100 Hz; (c) the off-window long-range arrivals measured in A2.3.4 have energy to 87-100 Hz, so a lower top would discard signal; (d) above 100 Hz the expected impact spectrum (f^-2.65 or steeper) is more than 30 dB below its 8 Hz level, so little is lost. The full 6 kHz band is not needed.

**Royer spectrogram colours.** The colour readings saturate and have no calibrated offset. For Cape Leeuwin, SWAMS3 and SSEIR (appendix panels, 1.56 s columns), S10 gives only a timing label inside each arrival window. A label is a rise of the 5-40 Hz band of 6 dB or more above the running 120 s median, merged when closer than 5 s. Each label also carries the sign of the change of (10-15 Hz) minus (2-60 Hz) during the rise, as a crude slope sign. Royer labels have NO p-value and do not enter any significance calculation.

## A2.2 Pre-processing (fixed)

1. **Spectrogram.** One-sided PSD in V²/Hz, 1 s Hann frames (1 Hz bins), 0.5 s hop, 8-100 Hz (93 bins). Function `spectrogram`.
2. **Local noise and whitening.** For each 307 s record: rank the frames by their 8-100 Hz power, and keep the lowest 80 %. N(f) is the mean of the kept frames, X = P/N − 1, and σ(f) is the standard deviation of X over the kept frames. Z = X/σ. Under noise, Z has zero mean and unit variance in each bin. The trim stops transients from biasing N. A plain median is not used, because it under-estimates the mean of a periodogram by a factor of about ln 2, which biases Z (found on synthetic noise before this commit). Function `whiten`.
3. **System gain.** The template is converted from a pressure shape to a volts shape by the logger's measured system gain G(f), from the calibration record held for each logger (as in the station data package). The hydrophone sensitivity is a constant and cancels.

## A2.3 Template family (fixed; loose impact-like class)

### A2.3.1 Labelled reference member (not the centre)

The one measured aircraft-impact source spectrum is that of the F-35A crash recorded at H11 (Metz, Obana and Fukao 2022, Pure Appl. Geophys. 180, 1343-1351, doi:10.1007/s00024-022-03117-6). It is flat to a corner of about 4.5-5.75 Hz, then falls as f^-a with a = 2.65-3.5. Above 8 Hz that is −8.0 to −10.5 dB per octave. It enters the bank as three labelled members (rows 0-2: a = 3.1 with f_c = 5.1 Hz, a = 2.65 with f_c = 4.5 Hz, a = 3.5 with f_c = 5.75 Hz; no cut-off inside the band; no ripple). Under the steer of A2.0.4, it does NOT set the centre or the limits of the family.

### A2.3.2 Loose family (randomised)

Received pressure shape: S(f) = [1 / (1 + (f/f_c)^a)] × H_lo(f) × H_hi(f) × M(f).

| Term | Form | Range | Reason |
|---|---|---|---|
| Slope above the corner (source plus path tilt) | f^-a | a ∈ [0, 5], uniform (flat to −15 dB/octave) | steer: "flat to steeply falling". A larger, longer impact or a break-up changes the slope. Path tilt (A2.3.3) is inside this range |
| Corner frequency | f_c | 0.5-20 Hz, log-uniform | steer: "below 1 Hz to about 20 Hz". Corner ≈ 1/(impact duration); the F-35A corner of about 5 Hz lies inside |
| Low-frequency cut-off H_lo | 2nd-order high-pass, (f/f_lo)^4 / (1 + (f/f_lo)^4) | f_lo ∈ [8, 20] Hz | 8 Hz hardware high-pass; shelf and slope mode cut-off at the receiver; the off-window arrivals start at 8-11 Hz |
| High-frequency cut-off H_hi | 2nd-order low-pass, 1 / (1 + (f/f_hi)^4) | f_hi ∈ [15, 120] Hz, log-uniform | scattering and bottom loss at long range; the off-window arrivals end at 87-100 Hz |
| Bandwidth constraint | f_hi ≥ 2 f_lo | at least one octave | steer: broadband. Without it the family could become a narrow-band (whale-call) detector |
| Multipath ripple M | \|1 + r e^{−i(2πfΔ + φ)}\|² | r ∈ [0, 0.6] (r = 0 in one draw in four), Δ ∈ [0.02, 0.5] s log-uniform (ripple spacing 2-50 Hz), φ uniform | path multipath near the source and the receiver. r ≤ 0.6 keeps the ripple shallower than about 12 dB, so it does not become a harmonic series |

**Time shape (onset and time spread).** g(t) = (1 − e^{−t/t_r}) e^{−t/t_d}, with t_r ∈ {0.25, 1, 3} s (impulsive or fairly fast onset) and t_d ∈ {0.5, 1, 2, 4, 8, 16, 30} s (21 shapes). The support is min(90 s, 3t_r + 4t_d). So the durations run from less than 1 s to about 60 s at the half-peak level (t_d = 30 s gives about 50 s above 10 % of the peak power, and the support reaches 90 s). Long-range T-phases are emergent, with spreads of seconds to tens of seconds (de Groot-Hedlin and Orcutt 1999, doi:10.1029/1999GL900205; Okal 2001, doi:10.1785/gssrl.72.2.186). The off-window arrivals in these data have durations of 6-14 s (A2.3.4).

**Bank.** Rows 0-2 are the Metz et al. members. Rows 3-239 are drawn once with seed 20261104 (`draw_path_params`). Times 21 time shapes, this gives 5,040 templates. The bank is fixed and is not tuned after this commit.

### A2.3.3 Literature basis for the slope range (path part)

Sea-water absorption (Ainslie and McColm 1998, J. Acoust. Soc. Am. 103, 1671, doi:10.1121/1.421258) at 4 °C, salinity 35, pH 8 is about 0.0012 dB/km at 100 Hz and below 0.0001 dB/km at 10 Hz. Over the 1,400-5,100 km paths of the IMOS stations, it adds 1.7-6.3 dB of loss at 100 Hz relative to 10 Hz. That is a steepening of 0.5-1.9 dB/octave, or 0.2-0.6 in the exponent. Absorption alone therefore steepens the slope a little (by 0.2-0.6 in a). Slope conversion, bottom interaction and mode stripping can flatten or steepen it more. These are not modelled (no propagation modelling in this track). The slope range a ∈ [0, 5] contains the source range of the steer and these path effects.

### A2.3.4 Off-window long-range arrivals measured before this commit

All catalogued events (project known-event table, 67 events) with a clear or partly-clear path to an IMOS logger were examined at their predicted arrival (speeds 1.467-1.518 km/s, ± 3σ of the origin time + 15 s). Only arrivals entirely outside the station's arrival window + 120 s were used. 45 record intervals qualified. A spectrogram quick-look showed that most strong time-coincident transients are NOT the catalogued event (Scott Reef local impulsive noise and choruses; 20 Hz tonal whale units). The broadband, emergent arrivals that look like real long-range arrivals are:

| Catalogued event | Logger | Peak (UTC) | Half-peak duration (5 s smoothing) | Excess slope 8-100 Hz (pressure) | Band with excess |
|---|---|---|---|---|---|
| Royer icequake 1 | Portland 3274 | 00:34:52.5 | 14 s | −5.7 dB/octave | 8-100 Hz |
| Royer icequake 1 | Portland 3275 | 00:34:54.4 | 14 s | −4.2 dB/octave | 8-100 Hz |
| Royer event 7/10/12 (ambiguous) | Perth Canyon 3315 | 01:33:44.7 | 8 s | −8.2 dB/octave | 8-97 Hz |
| Royer event 11/12 (ambiguous) | Portland 3274 | 02:01:24.5 | 6 s | −6.2 dB/octave | 8-87 Hz |

These have slopes of f^-1.4 to f^-2.7, durations of 6-14 s and emergent onsets. The loose family covers their slopes and durations. Their onsets are slower than the fastest templates. Therefore S10 will also respond to natural long-range arrivals, and the classifier and the catalogue timing must separate them (A2.7.5). The lesson for the classifier (A2.7) is that timing alone mislabels, so the training labels need stated signal criteria as well as timing.

## A2.4 The S10 statistic

For spectral shape s, the whitened spectral weight is w(f) = S(f) G(f) / (N(f) σ(f)), normalised so that ||w|| = 1. The template is h(t, f) = g(t) w(f).

1. **Matched-filter SNR (level free):** ρ(t0) = ⟨Z, h(· − t0)⟩ / ||g||. Under noise, ρ is approximately unit normal for each template. The fitted level is A = ρ/||g||, and only A > 0 is accepted.
2. **Shape consistency** (Allen 2005, doi:10.1103/PhysRevD.71.062001, adapted to an incoherent power spectrogram). Split the bins of w into P = 4 contiguous sub-bands of equal Σw², and project onto each, giving ρ_i. A noise-like signal of fitted level has a signal-to-noise power ratio in each cell of s_cell = A g w σ. It raises the cell variance to (1 + s_cell)². So
   V_i = [Σg² Σw_i² + 2A Σg³ Σ(w_i³σ) + A² Σg⁴ Σ(w_i⁴σ²)] / Σg²,
   χ² = Σ_i (ρ_i − ρ e_i)² / V_i,  e_i = Σw_i²,  χ²_r = χ² / (P − 1).
   This term scores the SHAPE. A source whose spectrum differs from the template (for example a 20 Hz tonal call, or energy in one sub-band only) gives a large χ²_r.
3. **Re-weighted SNR** (Babak et al. 2013, doi:10.1103/PhysRevD.87.024033): R = ρ if χ²_r ≤ 1, otherwise R = ρ / [(1 + χ²_r³)/2]^{1/6}.
4. **Decision statistic:** R(t0) = maximum of R over all 5,040 templates, at every frame onset t0 (0.5 s step). Onsets with less than 60 % of the template energy inside the record are not scored. Function `s10_scan`.
5. **Candidates:** local maxima of R(t0) at least 10 s apart inside the station's run window, with local p ≤ 0.05. This is the generous rule of section 5. The best template gives the onset time, the time spread and the path parameters as labels.

## A2.5 Nulls and p-values (same maximisation in every null trial)

| Level | Definition |
|---|---|
| Null records | Perth Canyon 3376, Scott Reef 3250, Portland 3274: N2, the background days 1-15 March 2014 at the same clock hours ± 2 h (22:30-03:35 UTC). Perth Canyon 3315 and Portland 3275 (no background days held): N1, all same-day records outside the run window ± 60 s. The same-site N2 (3376 for 3315, 3274 for 3275) is run as a second null and reported beside it. |
| Local p | Empirical exceedance of R(t0) against R at all null frames of the same station (`empirical_p`; minimum 1/(n+1); GPD tail above the null range, labelled "extrapolated"). |
| Station-global p | The run window at a station covers pieces of 1-4 records. A pseudo-window has the same number of pieces, each of the same length, placed at a random null record and a random start. Its value is the maximum R over all frames in all pieces. 5,000 pseudo-windows. The station-global p of a candidate is P(pseudo-window max ≥ candidate R). Look-elsewhere over templates, onsets and records is therefore inside the maximum. |
| Method-global p | Šidák over the five loggers: 1 − (1 − p_station-global)^5. Perth Canyon 3315/3376 and Portland 3274/3275 share sites, so this is conservative. |
| Time-slide null | Not needed for single-station S10, because the pseudo-windows are drawn from other times. Network association of S10 triggers is left to the association track (B1, C1), which takes S10 triggers in the same way as S3 triggers. |

Known natural transients are NOT removed from the null records, so the null carries the natural transient rate and is conservative.

## A2.6 Injection sensitivity (null records only; never into an arrival window)

1. Signal: Gaussian noise shaped to S(f)G(f) and modulated by √g(t). S(f) and g are drawn at random from the S10 family (`random_impact_draw`, the same ranges, t_r and t_d log-uniform over their ranges, an independent seed 7). This is the INSIDE-family sensitivity. The Metz et al. member alone (a = 3.1, f_c = 5.1 Hz) is reported as a separate row.
2. An OUTSIDE-family check uses 100 injections per SNR, on Perth Canyon 3376 and Portland 3274 null records only, and is reported separately. The injected signals have a = 6-7 (steeper than the family), or t_r = 8 s with t_d = 60 s (slower and longer than the family).
3. SNR as specification section 11.4: the mean signal power (8-100 Hz) over the first 10 s after onset, divided by the median 1 s frame power of the host record. Grid −12 to +12 dB in 3 dB steps; 200 injections per logger and SNR; onset uniform in 20-250 s of the record.
4. Detection: the maximum R within ±5 s of the true onset reaches (a) local p ≤ 0.05, and (b) station-global p ≤ 0.05. Outputs: detection probability against SNR, SNR50 from a logistic fit, and onset error. The false-alarm rate is from the null records with no injection.

## A2.7 Source classifier

### A2.7.1 Classes

Known classes: whale call; ship; earthquake sound arrival; ice event; airgun shot. Other classes: impact-like (LOOSE, A2.0.4); background noise only; and unclassified (none of these; open set). "Background noise only" is added to the requested list, because weak S10 candidates are often noise fluctuations. Without that class, the classifier would force them into a source class.

The impact-like training class is synthetic. It uses the whole loose family of A2.3 (not the Metz et al. shape alone), injected into real noise.

### A2.7.2 Features (one window = onset to onset + duration, with the rest of the record as context)

Spectral (raw IMOS only; excess spectrum = mean over the window of P − N, corrected to pressure by G(f)):
1. spectral slope, dB/octave (weighted least squares over the bins with excess SNR > 0.25);
2. centroid, octaves above 8 Hz;
3. bandwidth, weighted standard deviation of log2 f;
4. spectral flatness of the excess ratio (Wiener entropy);
5. tonality: the maximum, over 10-100 Hz, of the fine-resolution (0.25 Hz) excess over its 5 Hz running median, in dB;
6. frequency sweep rate: slope of the per-frame peak frequency against time, Hz/s (signed);
7. harmonic or ripple structure: the maximum normalised autocorrelation of the fine excess spectrum at lags 4-40 Hz;
8. low-band fraction: fraction of excess power below 20 Hz.

Time-shape (also computable on envelope-only data):

9. duration, log10 s (half-peak extent of the 8-100 Hz excess envelope, or of the envelope);
10. rise time, log10 s (10-90 % of peak);
11. decay rate, dB/s, from the peak to the end of the window;
12. repeat strength: the maximum normalised autocorrelation of the record envelope at lags 4-120 s;
13. repeat interval, log10 s (the lag of that maximum);
14. envelope kurtosis over the window ± 10 s.

Context (raw IMOS only):

15. record level: the median 8-100 Hz power of the record, in dB, above the station's median over all records used;
16. persistent tonal lines: the number of narrow lines ≥ 6 dB above the smoothed record-mean spectrum.

### A2.7.3 Labelled training data and stated criteria (all outside the arrival windows)

Generic transient finder for labelling (L0): the 8-100 Hz excess envelope with 5 s smoothing; local maxima with robust z ≥ 6 against the record, at least 20 s apart.

| Class | Source | Stated criteria | Group for cross-validation |
|---|---|---|---|
| Earthquake sound arrival | USGS M ≥ 4 events, 28 Feb-16 Mar 2014, 75° S-20° N, 15-180° E (downloaded 4 Nov 2026), plus project catalogue earthquakes | L0 peak within [origin + D/1.53 − 30 s, origin + D/1.44 + 60 s]; tonality < 8 dB; bandwidth ≥ 0.25 octave (weighted sd); duration ≥ 3 s | event |
| Ice event | Royer 2016 icequakes (project catalogue) | the same timing and criteria | event |
| Whale call | N1 and N2 records | no catalogued arrival in its timing interval; tonality ≥ 10 dB; ≥ 60 % of excess power in 14-32 Hz OR harmonic score ≥ 0.5 with fundamental 15-30 Hz; duration 0.5-60 s. Band criteria from published call descriptions: Antarctic blue whale (Gavrilov, McCauley and Gedamke 2012, doi:10.1121/1.4707425), pygmy blue whale (Gavrilov et al. 2011, doi:10.1121/1.3651817), fin whale 20 Hz pulses (Watkins et al. 1987, doi:10.1121/1.395685) | record |
| Airgun shot | N1 and N2 records; H08S Kadri envelope shots (envelope model only, re-measured by `segment_shots`) | ≥ 6 L0 impulses in one record, interval CV ≤ 0.10, median interval 5-30 s, each duration ≤ 6 s, bandwidth ≥ 0.25 octave (Caldwell and Dragoset 2000, doi:10.1190/1.1438744; Nieukirk et al. 2004, doi:10.1121/1.1675816) | record (raw), shot train (envelope) |
| Ship | N1 and N2 records | record level ≥ 6 dB above the station median AND ≥ 3 persistent tonal lines | record |
| Impact-like | synthetic: S10 family injected into N1/N2 records at SNR 0-12 dB (uniform), independent seed 11 | by construction | host record |
| Background noise only | N1/N2 records, random 10 s windows with no L0 peak within ± 30 s | by construction | record |

Caps: at most 3 examples per record and 150 per class. The whale, airgun and ship labels use criteria that overlap the features, so cross-validated accuracy for those classes is OPTIMISTIC. This is stated with the results. An open labelled library of baleen whale sounds exists (Miller et al. 2021, doi:10.1038/s41598-020-78995-8; AADC doi:10.26179/5e6056035c01b). It is served as one archive of about 2,000 hours through a JavaScript download application. It is not used in this track, and is recorded as an open issue.

### A2.7.4 Model, validation and calibration

1. **Model.** Features are robust-standardised (median, IQR); missing values are set to the training median plus a missing-flag. Multinomial logistic regression with L2 penalty, C = 1.0, balanced class weights. The two models (raw, and envelope-only) are fitted with the same rules.
2. **Validation.** Leave-one-group-out cross-validation (groups as A2.7.3). Report the confusion matrix, per-class recall and precision, the Brier score (Brier 1950) and the expected calibration error (10 bins) of the cross-validated probabilities (Niculescu-Mizil and Caruana 2005).
3. **Calibration rule (fixed).** If the cross-validated expected calibration error exceeds 0.10, one temperature parameter is fitted on the cross-validated outputs and applied to the final model. Otherwise, no change is made.
4. **Open set.** A Gaussian class model with a shared Ledoit-Wolf covariance (Ledoit and Wolf 2004, doi:10.1016/S0047-259X(03)00096-4) gives the squared Mahalanobis distance d² to the nearest class mean. If P(χ²_k > d²) < 0.001 (k features), the window is labelled "none-of-these". Its class probabilities are still shown.
5. **Function.** `classify(candidate_window)` returns the class probabilities, the open-set flag and the features. It takes the record waveform (raw) or the envelope (envelope form), the window start and end, and the station gain.

### A2.7.5 Decision rule and use of the class scores (asymmetry rule, steer of A2.0.4)

1. **Known class (whale call, ship, earthquake sound arrival, ice event, airgun shot).** The window is assigned to known class k only if BOTH: (a) the calibrated probability p_k ≥ 0.5, and (b) there is positive evidence of that class's features, as follows:
   - earthquake sound arrival or ice event: a catalogue timing match (association probability of section 8 ≥ 0.5 with a catalogued event of that class);
   - whale call: tonality ≥ 8 dB, or |sweep rate| ≥ 0.2 Hz/s with ≥ 60 % of the excess power in 14-32 Hz, or harmonic score ≥ 0.5;
   - ship: record level ≥ 6 dB above the station median and ≥ 3 persistent tonal lines;
   - airgun shot: repeat strength ≥ 0.5 with a repeat interval of 5-30 s, or a measured shot train (H08S).
2. **Impact-like.** The window is labelled impact-like if it is broadband (bandwidth ≥ 0.25 octave and tonality < 8 dB), its onset is fast (rise time ≤ 3 s), it does not repeat regularly (repeat strength < 0.5), and it is not assigned to a known class by item 1. No more is needed. The impact-like probability is reported beside the label.
3. **Unclassified.** Everything else, including the open-set rejects (A2.7.4 item 4), is "unclassified" and is KEPT.
4. **Earthquake against impact.** Their spectra overlap. The order of evidence is: catalogue timing first, then onset shape (rise time) and duration. If the catalogue timing does not match and the onset and duration do not decide, the window is ambiguous and is kept.
5. **What the scores may do.** Class scores feed only (a) the known-event probability, as the spectral-class factor of Amendment 1 (timing × class), and (b) the ranking weight (impact-like probability). A class score NEVER removes a candidate on its own. Removal needs ALL of: an assigned known class under item 1 (so with positive feature evidence), and a combined known-source probability ≥ 0.95. For catalogued classes, the combined probability is the section 8 timing probability with the class factor applied to its odds: odds = [P_timing / (1 − P_timing)] × [p_k / p_impact-like]. For classes with no catalogue (whale call, ship, airgun shot at IMOS), it is the calibrated p_k, and the positive-evidence criterion of item 1 is the independent second factor.
6. Airgun-coincident candidates at Diego Garcia South stay under the 23 October rule: they are labelled and given the interference test, and they are never removed.

## A2.8 Outputs

1. S10 candidate table in the section 12 schema, plus: best template parameters, ρ, χ²_r, R, null source, the class probabilities and the open-set flag.
2. S10 null and injection tables.
3. Classifier validation table, confusion matrix chart, and reliability (calibration) chart.
4. Classification of every S10 candidate and of every catalogued-event window (IMOS raw model; H01W/H08S envelope model).
5. Royer timing labels (no p-values).
6. A spectrogram gallery of the top S10 candidates and of one example per class.

## A2.9 Relation to the other detectors

S10 is a time-frequency detector, like S6 (excess power). S6 sums whitened power in rectangular tiles. S10 projects onto a physically shaped family and penalises shape mismatch. Agreement of S6 and S10 is therefore not independent evidence. The across-methods correction (section 10) treats them as separate methods. That correction is conservative, because they are positively correlated.

## A2.10 Limits

1. The F-35A is one measured case, of a much smaller and different aircraft. Under the steer of A2.0.4, the family is widened so that it does not depend on that shape. The price is specificity: S10 also responds to broadband natural arrivals (earthquake sound arrivals, ice events), and the classifier and the catalogue timing must carry the separation.
2. The family assumes that propagation keeps the shape inside the stated ranges. Stronger distortion (for example strong mode stripping) is tested only by the outside-family injections (A2.6.2).
3. The training sets for earthquake and ice classes from these data are small. The rules in A2.7.5 limit what the classifier can do with them.
4. IMOS duty cycle: an arrival can fall in a recording gap. The coverage of each run window is reported with each result.

## A2.11 Deviations

None at the time of fixing. Any later change is recorded here with its date and reason, and results are reported with and without it.

## A2.12 Fixed code

`reverse_spectral.py` version 1.0.0. The S10 part (from the start of the file to the line `# ------------------------------------------------------------------ features`) has the sha256 given in `amendment-2-fixed-code.json`, committed with this document.
