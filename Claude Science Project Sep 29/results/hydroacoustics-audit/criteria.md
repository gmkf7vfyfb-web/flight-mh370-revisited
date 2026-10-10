# Hydroacoustics audit: pre-registered calibration criteria

Independent audit for Modular Architecture, commissioned at Pete's request (10 Oct 2026, ~17:45 -0600).
Written and committed **before** any audit comparison is computed. Thresholds are not edited after results are seen;
any later change is an amendment with its own commit and reason.

**What the auditor had seen before writing this file (disclosed).** The module's own summary numbers for air9
(median residual −0.2 dB at H01W and +3.2 dB at H08S, RMS 7.9 dB, and its later note of a +12.7 / +7.4 dB per
octave tilt), Blackman et al. (2004) Fig. 23 and Fig. 2 (printed pp. 21 and 7), and Appendix B Figs B1 and B4
(printed pp. 25 and 27). So the air9 criteria are **not blind**; the SUS, source-substitution and sensitivity
criteria are blind (no SUS prediction and no substituted-source residual had been computed).

## Definitions

- Band b: third-octave band centre f_b (Hz). The observed value in a band is the dB mean of the digitised
  observation inside the band edges f_b·2^(±1/6).
- Residual: **r_b = observed − model** (dB). For transmission loss (TL), r_b > 0 means the model **under-predicts
  loss**, so it **over-predicts** the received signal. For received level (RL), r_b > 0 means the model
  under-predicts the signal.
- LEVEL: the median of r_b over the bands with data.
- SLOPE: the ordinary-least-squares slope s of r_b on log2(f_b), in dB per octave, with its standard error.
- SHAPE: the RMS of r_b after the level-and-slope fit is removed (detrended RMS).
- SPAN: the lowest to highest band with data. A verdict applies **only inside the span**. A band more than half an
  octave outside the span is **not calibrated** by that test, whatever the verdict inside it.

## C1. Absolute TL or RL, per station and per test (air9 at H01W and H08S; each SUS station)

| quantity | PASS | PARTIAL | FAIL |
|---|---|---|---|
| LEVEL, abs(median r_b) | ≤ 3 dB | ≤ 6 dB | > 6 dB |
| SLOPE, abs(s) | ≤ 1.5 dB/oct | ≤ 3 dB/oct | > 3 dB/oct |
| SHAPE, detrended RMS | ≤ 3 dB | ≤ 5 dB | > 5 dB |

Overall per station: PASS if all three pass; FAIL if any fails; PARTIAL otherwise.

**Why these thresholds.**
- **Level.** The observed curves are read from charts: Fig. 23 at about ±2 dB, and a median over shots adds 1–2 dB.
  Combined, that is about 2.5 dB, so 3 dB is the smallest bias that the data can show. 6 dB is a factor of 4 in
  energy, and it moves a detection-probability curve across most of its transition width (a few dB).
- **Slope.** The air9 span is about 2 octaves (13–63 Hz). 1.5 dB per octave gives 3 dB from end to end, the same
  as the level tolerance. 3 dB per octave gives 6 dB from end to end, the same as the partial level.
- **Shape.** 3 dB is the chart reading plus the band-to-band scatter of a median over shots; 5 dB allows the
  multipath interference that a band-centre model cannot reproduce.

## C2. Station difference (cancels the source term): d_b = r_b(H01W) − r_b(H08S), over the shared bands

| quantity | PASS | PARTIAL | FAIL |
|---|---|---|---|
| LEVEL, abs(median d_b) | ≤ 3 dB | ≤ 6 dB | > 6 dB |
| SLOPE, abs(s_d) | ≤ 1.5 dB/oct | ≤ 3 dB/oct | > 3 dB/oct |
| SHAPE, detrended RMS of d_b | ≤ 3.5 dB | ≤ 5 dB | > 5 dB |

The shape threshold is larger than in C1 by about √2 for the two chart readings. C2 tests the **path** part of the
model only. A PASS in C2 with a FAIL in C1 places the error in a **shared** term: the source spectrum, or the coupling
of a near-surface source into the sound channel.

## C3. Source-spectrum substitution (air9, both stations; blind)

The module's hypothesis is that the shared tilt comes from Blackman's assumed airgun source spectrum. The test:
replace the flat source spectrum with each independent, published or physics-based airgun-array source model
(declared in the audit before it is run, no parameter fitted to Fig. 23), apply the same model at both stations, and
recompute C1.
- **SUPPORTED** if at least one such model brings the SLOPE at **both** stations to PARTIAL or better
  (abs(s) ≤ 3 dB/oct), and does not make the LEVEL fail.
- **NOT SUPPORTED** if no such model does. The tilt is then attributed to near-source coupling of a near-surface
  source (model physics, which an aircraft impact shares), not to the source spectrum.
- A model whose parameters were tuned to Fig. 23 can only be reported as a fit, never as support.

## C4. SUS charges, 2003 (Blackman Appendix B; blind)

The source spectrum of a 1.8 lb (0.82 kg) SUS charge comes from published explosive-source models, with ±3 dB
source uncertainty (to be cited). The source is deep (610 or 915 m), so this test checks **propagation**, not the
coupling of a near-surface source.
- Received-level or SNR residuals per station: C1 thresholds with the LEVEL thresholds widened by the source
  uncertainty: PASS ≤ 4 dB, PARTIAL ≤ 7 dB.
- Detection consistency per shot and station: a reported non-detection where the model predicts band SNR ≥ +6 dB,
  or a reported detection where it predicts ≤ −6 dB in every band, is an **inconsistency**. PASS if ≤ 10 % of the
  scored shot-station pairs are inconsistent; PARTIAL if ≤ 25 %; FAIL otherwise.
- The frequency extent validated is the span of bands in which observed SNR ≥ 3 dB.

## C5. F-35A calibration of η (arithmetic)

PASS if the audit reproduces η_cal from the module's stated inputs within 0.5 dB (a factor of 1.12). Separately,
the audit states the direction and size of each bias the module lists (band, peak-to-exposure ratio, site), and
whether the calibration constrains the MH370 bands below 13 Hz.

## C6. What counts as "calibrated" for use in a likelihood

A propagation-plus-source chain is **CALIBRATED** for a likelihood in band b only if:
1. C1 is PASS at **both** stations for every band the likelihood uses, the bands lie inside the span, and C2 is PASS; and
2. the source model used for the aircraft impact has been checked by an independent event with a known source
   (C4 for propagation, C5 or a successor for the source and coupling).

It is **PARTLY CALIBRATED** if C1 and C2 are PARTIAL or better. The likelihood may then be used only with an
explicit error model whose frequency structure is at least as large as the measured level **and** slope residuals,
with the result labelled "conditional on the calibration error model".

It is **NOT CALIBRATED** if any of these is FAIL, or if the band lies outside every span. It may then enter only as a
predictive or sensitivity calculation, not as a likelihood that moves the posterior.

## Sensitivities (task 4; blind)

The stand-in's power check and R_hyd are re-run in the audit's own directory, with TL replaced by (i) the module
± the calibration error found here, and (ii) the best-calibrated alternative, if one exists. Reported: E[ln R],
P(abs(ln R) ≥ 1) and ln R_hyd. The stand-in's results are not overwritten.

*Architecture audit, 2026-10-10.*
