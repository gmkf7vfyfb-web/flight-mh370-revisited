# Amendment 1 to the reverse-sensing methods specification: spectral-shape weight (W1)

Date: 4 Nov 2026. Source: Pete Large's proposal, 4 Nov 2026. This amendment is fixed BEFORE any arrival window is opened. It adds one weighting factor (W1). W1 is NOT a screening detector: it creates no candidates and removes none (Pete, 4 Nov 2026). It changes no other part of the specification.

## W1 Spectral-shape weight against the expected impact spectrum

**Data forms.** Raw IMOS records only (full spectrum, 8 Hz hardware high-pass, band used 8-100 Hz). The Kadri digitised traces carry one 5-40 Hz band and no spectrum, so W1 is not computed for them (weight = 1, stated as 'not available'). The Royer spectrogram colours (Cape Leeuwin, SWAMS3, SSEIR) saturate and are not calibrated; W1 uses them for the sign of the slope only, as a label, never as a weight.

**Reference shape.** The one measured aircraft-impact source spectrum (Metz et al., F-35A at H11): flat to a corner of about 4.5-5.75 Hz, then a power law f^-a with a = 2.65-3.5. Above 8 Hz the expected received shape is therefore a falling power law. The propagation path changes the shape. To allow for this without the transmission-loss model, the test allows a slope a from 1.0 to 4.5 and allows a smooth path-response term (a second-order polynomial in log f with a fixed prior width). The level is free. Only the shape is scored.

**Weight.** For each candidate that a screening detector (S1-S8) or an association method (B1, C1-C4) has produced on raw data, and for each 2 s spectrogram column in the candidate's window, compute the excess spectrum over the local noise spectrum (median of the ring windows, as for S1). Fit log excess power against log f, 8-100 Hz, with (a) the impact-shape model above and (b) the best of the alternative source-class models below. W1 = the log-likelihood ratio of (a) against the noise-only model, maximised over slope and start time inside the candidate window, then converted to a calibrated weight by its rank in the null distribution below. W1 multiplies the candidate's ranking score. It never sets a threshold.

**Null (calibration of the weight).** The same statistic on off-window noise windows from the same logger and day (ring and time-slide windows, as in section 3), with the same maximisation.

**Classification feature (for the 0.95 known-event screen).** For every candidate from any detector on raw data, compute the likelihood of each source class from its spectral shape and time signature:
- earthquake sound arrival: energy concentrated at the low end of the band, slow emergent onset, long coda;
- airgun shot: broadband, with a periodic ripple in frequency from the bubble pulse, regular repeat interval;
- whale call or ship: narrow tonal lines or a slowly gliding tone;
- ice event: narrow-band or harmonic, repeated;
- impact-like: falling power law, impulsive onset, no tonal lines.
The class likelihoods enter the association probability of section 8 as a multiplier on the timing term. The spectral class is one factor only; it cannot remove a candidate alone. A candidate is removed only if the combined probability of a known source (timing x spectral class x other features) is 0.95 or more. Airgun-coincident candidates at Diego Garcia South stay under the 23 Oct rule (label and interference test, never removed).

**Injection test.** As section 11, with the injected signal given the reference shape filtered by a random smooth path response inside the allowed range.

**Limit.** The assumption is that propagation does not change the spectral shape beyond the allowed range. Multipath and mode stripping can change it more. W1 therefore only raises or lowers rank; a poor spectral fit never removes a candidate.
