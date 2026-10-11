# Gaspin & Shuler (1971): extraction of the small-charge source-level model

Architecture stand-in for hydroacoustics, 11 Oct 2026. Extraction only; the application is in
`../hydroacoustics-audit-sus-absolute.md`. **UNCONVERGED** label carried (core (b) split-half not converged; this file
uses no core output).

**Source.** Gaspin, J. B. & Shuler, V. K. (1971), *Source levels of shallow underwater explosions*, NOLTR 71-160,
Naval Ordnance Laboratory, 13 Oct 1971, DTIC AD0734381. Distribution statement: Approved for Public Release;
Distribution Unlimited. File on the exchange: `hydroacoustics/sources/Gaspin_Shuler_1971_NOLTR_71-160_AD0734381.pdf`,
sha256 `215c3658ee17b48e980f9c8992675b8c664e090e2377e7bea223e4527ee43983`, 57 PDF pages (re-verified).

**Page convention.** Printed page numbers are read from the report's own running headers and page folios. Body
pages: **printed page = PDF page − 7** (checked at printed 5, 8, 9, 10, 12, 13, 15, 17, 18, 20, 22, 23, 25, 27, 44
and 46). The OCR text layer is unusable for numbers; every value below was read from page images. Values read from a
plot are marked DIGITISED.

## 1. What the model is

G&S do **not** give a closed-form spectrum. Their model is a procedure (section 5, printed pp. 7–9):
1. Build an idealised free-water pressure-time history from semi-empirical similitude relations (Table 2, p. 8),
   drawn by hand through the tabulated points with the topology of Fig. 2 (p. 25): shock wave, first negative
   phase, four bubble pulses with negative phases between them.
2. Adjust the hand-drawn curve so the shock and first-bubble positive impulses are within 10 % of Slifko's
   relations and the residual impulse is near zero to the fourth bubble pulse (§5.4, p. 9).
3. FFT (≈ 1 Hz resolution) and integrate in ideal one-third-octave and octave bands (§5.5, p. 9). The surface
   reflection is **not** part of the source level (§6.10 p. 17; §8.7 p. 23).

Outputs: Table 3 (one-third-octave, p. 12), Table 4 (octave, p. 13), detailed spectra Figs. 5–9, depth-variation
Tables 5 (p. 15) and 6 (p. 16).

## 2. Parameters (Table 2, printed p. 8) → `gaspin-shuler/gs1971_table2_similitude.csv`

Units: pressures psi, times s; W = charge weight, lb (TNT); R = slant range, ft; **Z = charge depth + 33 ft**.

| parameter | form | source cited by G&S |
|---|---|---|
| P0 (shock peak) | 2.08 × 10⁴ (W^⅓/R)^1.13 | Slifko (ref. 16) |
| Pmin (first negative phase) | −77 Z^⅓ W^⅓ / R | Slifko |
| P1 (first bubble pulse peak) | 3300 W^⅓ / R | Slifko |
| P2, P3, P4 | 0.22, 0.10, 0.03 × P1 | unpublished NOL data |
| θ (shock decay constant) | 5.8 × 10⁻⁵ W^⅓ (W^⅓/R)^−0.22 | Arons (ref. 18) |
| Tpp, Tnp, Tbp, T1, T2, T3, T4 | K W^⅓ / Z^⅚ with K = 0.555, 3.10, 1.10, 4.34, 3.06, 2.48, 2.31 | Slifko; Arons, Slifko & Carter (ref. 17) |

- **Bubble-pulse frequency** f_b = 1/T1 = Z^⅚ / (4.34 W^⅓) Hz (footnote, p. 10: "the reciprocal of the time of the
  first bubble pulse"). For 1.8 lb: 51.5 Hz at 800 ft, 24.0 Hz at 300 ft; at the 2003 SUS depths **108 Hz at 610 m
  (2,001 ft) and 151 Hz at 915 m (3,002 ft)**.
- T2–T4 have K smaller than T1, so they are read as successive bubble **periods** (intervals), not times from
  detonation. This is an inference from the numbers; Fig. 2 draws them from the origin. Stated as an inference.
- The Table 2 relations come mainly from Slifko's 56 charges of 1, 8 and 50 lb at **500 to 14,000 ft** (§5.1, p. 7).
  G&S extrapolate them **upward** to shallow depths.
- Not in Table 2: Slifko's shock and bubble impulse formulas (used in §5.4 but not printed). Fig. 23 (p. 46) gives
  only the ratio of Slifko's to Arons' shock impulse versus charge depth: DIGITISED to
  `gaspin-shuler/gs1971_fig23_impulse_ratio_DIGITISED.csv` (2.29 at 11 ft, 1.62 at 100 ft, 0.88 at 800 ft, 0.64 at
  2,000 ft, 0.56 at 2,990 ft; the curve ends at about 3,000 ft).

## 3. Spectral form and tabulated levels → `gaspin-shuler/gs1971_table3_third_octave.csv`

Table 3 (printed p. 12): one-third-octave band **energy flux spectral density, band average, dB re 1 erg/cm²/Hz at
100 yd**, for 1.8 lb at 800, 300 and 60 ft and 3 lb at 60 and 500 ft, 30 bands 11 Hz–11.2 kHz. Band meaning: the
average energy per Hz in the band, not the energy at the band centre (§6.7–6.8, p. 11).

Form (§6.6, p. 11): energy rises from low values at low frequency to a maximum near the bubble fundamental, falls off
above it, and tends to −6 dB per octave at high frequency (shock-wave dominated). One-third-octave values carry real
peak-and-null structure; G&S warn that interpolation between bands at low frequency is "extremely dubious" (§6.7).

The sub-bubble tail, the part the deep SUS bands use: 1.8 lb at 800 ft, 12.5 → 31.5 Hz (f/f_b 0.24–0.61):
−2.1, 0.5, 4.7, 9.5, 13.1 dB, a rise of about +11.5 dB per octave.

Conversion used downstream (declared): SL at 1 m [dB re 1 µPa²·s/Hz] = E + 10 log10(ρc × 10¹⁰) + 20 log10(91.44 m)
= E + 191.1 dB, with ρc = 1.539 × 10⁵ g cm⁻² s⁻¹ (G&S do not state their ρc; ±0.2 dB). The one-sided spectral
convention was checked: an independent re-implementation of the construction (§5 below) using one-sided
E(f) = 2|P(f)|²/ρc reproduces the 800-ft column to median +0.2 dB, so there is no factor-of-2 (3 dB) mismatch.

## 4. Stated validity range and uncertainty

- **Validity (§8.1, p. 22):** "small charges (weighing up to a few lb) detonated at depths down to about 1000 ft".
  Results for very shallow sources (60 ft) are less reliable (§7.6, §8.1). The **2003 SUS at 2,000 and 3,000 ft are
  outside the stated range** (they are deeper, inside the range of Slifko's input data).
- **Agreement with data:** Christian's octave-band curves, maximum 2.5 dB, mean absolute about 1 dB (§7.3, p. 17);
  three Squaw Mk 61 SUS shots at 800 ft nominal, generally less than 2 dB up to 500 Hz, shot-to-shot scatter 1–2 dB
  (§7.5, p. 18, Fig. 21 p. 44); Turner & Scrimger pentolite, maximum 2.6 dB at 295 ft and nearly 5 dB at 555 ft
  (§7.4, p. 18; §8.3, p. 22, "up to 3 db" against Christian).
- **In the sub-bubble tail specifically** (Fig. 21, DIGITISED by eye, ±0.7 dB,
  `gaspin-shuler/gs1971_fig21_squaw_800ft_DIGITISED.csv`): measured minus idealised is +0.8 to +4.5 dB in the 20 Hz
  band, −0.9 to +1.0 dB at 25 Hz, −1.4 to +0.2 dB at 31.5 Hz. The idealised tail is, if anything, too low and too
  steep at its lowest measured band.
- **Depth error:** ±100 ft about 800 ft changes the 20 Hz band by −2.8 to +3.3 dB (Table 5, p. 15); a SUS depth
  scatter of 700–900 ft can change the 20 Hz band by 6.3 dB at 300 ft nominal (§8.6, p. 23). No simple correction
  for depth variation exists (§8.6).
- **Depth correction G&S themselves apply:** the Squaw shots at 835–907 ft were scaled to 800 ft "by adjusting the
  time scale" (§7.5, p. 18), i.e. bubble-time similitude.

**Summary for C4.** The ±3 dB source uncertainty that criteria.md asked to be cited is supported by G&S for 1.8 lb
in one-third-octave bands **within ~1,000 ft**. It is not supported at 2,000–3,000 ft; see §5.

## 5. Stand-in checks of the extrapolation (not in G&S)

Two routes to the SUS depths, declared before scoring, neither fitted to SUS or hydrophone data:
- **Route A, time similitude** (G&S §7.5 procedure): E(f; z) = E800(f s) + 20 log10 s, s = (833/(z+33))^⅚.
  - Reproduces G&S's own full-method depth variation, Table 5 (700–900 ft), to RMS 0.86 / 0.18 / 0.16 / 0.30 dB over
    12.5–63 Hz (max 2.3 dB).
  - Over a larger step, 800 → 300 ft (s = 2.15) and 1.8 lb/800 ft → 3 lb/500 ft (s = 1.72), it **over-predicts the
    sub-bubble tail by +4.8 to +11.9 dB** (`route_a_similitude_tests.csv`).
  - At the SUS depths s = 0.476 (610 m) and 0.341 (915 m). Bands with f s < 11 Hz are extrapolated at the 12.5–16 Hz
    slope (+7.3 dB per octave); this affects ≤ 25 Hz at 610 m and ≤ 31.5 Hz at 915 m.
- **Route B, construction re-implemented** (`gaspin-shuler/gs_reconstruct.py`): Table 2 at the true depth, with
  declared shapes, because G&S's curves were hand-drawn:
  - shock exponential to 2θ, then a power-law tail carrying Arons × Fig. 23 impulse (the Arons TNT coefficients
    1.46 and 0.89 are quoted from the secondary literature, not read from Arons 1954);
  - exponential-cusp bubble pulses;
  - half-sine or sin² negative phases, scaled so the residual impulse is zero at the end of bubble 4.
  - Option κ = 4 with sin² reproduces Table 3 at 800 ft to median +0.2 dB and RMS 1.3 dB (12.5–1,250 Hz), and the
    tail (12.5–31.5 Hz) within −1.7 to +1.6 dB. It over-predicts the 300-ft and 3-lb/500-ft tails by +5.7 to
    +11.2 dB (`gs_reconstruct_vs_table3.csv`).
  - At 610 and 915 m, P0 θ (1 − e⁻²) already exceeds the Fig. 23 impulse, so the shock tail collapses to zero. The
    parameterisation is strained there.
- **The two routes differ at the SUS depths by +4.3 to +17.1 dB in the scored bands** (route B higher; median
  7.4 dB). That spread, not G&S's ±1–3 dB, is the honest source uncertainty for the 2003 SUS in 16–63 Hz.

*Architecture stand-in for hydroacoustics, 11 Oct 2026. Read-only on module code.*
