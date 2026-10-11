# Hydroacoustics: the air9 source reference from the Ewing EW0112 cruise report

Hydroacoustic Module, 11 Oct 2026. Pre-registration `ecbca309` (`prepare/air9_ew0112.py`); implementation and data
`5b522802` (`results-data/air9_ew0112/`). Chart: `hydroacoustics-air9-source-reference.png` / `.pdf`.
Labels: predictive audit, not a likelihood; hydroacoustics stays PREDICTIVE.

## Transcription (ledger: `ew0112_transcription_ledger.csv`; printed page = PDF page)
- p. 2: the "standard" Ewing array of 20 airguns; total volume 8,465 in³ (READ). Fig. 1 gun sizes and positions:
  mostly ILLEGIBLE at the 200-dpi scan; a few labels INFERRED. **The array geometry is not recovered from this copy.**
  A published layout of the same standard array is the next lead.
- p. 5: air9 = shots 317–340 (57 s) and 345–350 (127 s), 19 Oct 2001 (jd 292) 02:10:59.9–02:46:29.9 UTC,
  27°33.2′–34.0′ S, 98°51.6′–53.9′ E. Tow depth 11–12 m, as shallow as 9 m (15 m intended). The module's z_s rows
  (9, 10, 12 m) span this.
- p. 6, Fig. 2: two air9 shots (02:17:38, 02:18:35) on the calibrated Ball hydrophone. DIGITISED:
  - scaling to 1 m: 24.7 and 26.8 m;
  - 1-m peak: 232.6–233.0 dB re 1 µPa, which matches Blackman's "230–240 dB (adjusted to 1 meter)";
  - 1/3-octave spectra, 5–80 Hz, with a shot-to-shot spread of up to 5.7 dB.
- p. 7: Ball hydrophone "about 30 m ahead of the trailing array" (an estimate), depth not stated. Imploder imp6 at the
  air9 site (27°27.07′ S, 98°33.90′ E, 1,230 m?, about 2 × 10⁵ Pa re 1 m).
- p. 13: DAT tape T6 (airgun shots) is the archive lead. Not re-read here; architecture's citation is kept.

## Test (pre-registered)
The module/audit air9 residual r = Fig. 23 observed TL − module TL has a slope of +10.4 dB/oct at H01W and +7.4 dB/oct
at H08S. Blackman does not state the source spectrum behind "observed TL", so two hypotheses were registered:
- **H-ref:** Blackman used the Ball near-source spectrum, scaled to 1 m. Then r = the near-field reference factor
  (direct path minus the surface image at the Ball, band-averaged, × R1m²).
- **H-flat:** Blackman used a flat source level. Then r = C − S0, where S0 is the Ball spectrum minus that factor.

Grid: z_s 9/10/12 m × Ball offset 20/30/40 m × Ball depth 5–30 m (45 geometries); nominal geometry 30 m ahead, 15 m
deep.

| | H01W slope (min / median / max over grid) | H08S slope | both stations slope ≤ 3 dB/oct | verdict |
|---|---|---|---|---|
| no correction (z_s 10 m) | +10.4 | +7.4 | – | – |
| H-ref | +4.7 / +5.7 / +9.4 | +2.1 / +2.9 / +5.2 | 0 % | **NOT SUPPORTED** |
| H-flat | +2.4 / +3.5 / +7.4 | −0.5 / +0.3 / +2.8 | 31 % | **NOT SUPPORTED** |

A 20-gun proxy array (4 × 5, equal strengths) makes H-ref worse (+13 to +15 dB/oct at H01W).

**Reading.**
- A source-reference artefact can remove 3–7 dB/oct of the tilt. H-flat is the better of the two: under H-flat, H08S
  passes at every geometry.
- At Cape Leeuwin, however, the slope still exceeds the 3 dB/oct limit at the nominal geometry under either
  hypothesis.
- The station slope difference (about 3 dB/oct) is untouched by any source term, because a source term cancels
  between stations.
- So **air9 is still not an absolute or slope calibration**, and the remaining H01W tilt is unexplained.
- This agrees with the SUS C4 stand-in: the tilt is not a deep-path error. Part of it is a near-surface source term,
  now partly accounted for.

## What would settle it
1. The array geometry from a legible copy, or from a publication of the standard Ewing 20-gun array.
2. The Ball depth.
3. The DAT T6 raw recordings, which would give the far-field signature directly.

The imploder imp6 at the same site is a deep source (about 1,230 m) with a stated level. Whether it was received at
H01/H08 is not stated in Blackman, so it cannot be used yet.

## COVERAGE
- **Feasible set:** every geometry consistent with EW0112 pp. 5 and 7.
- **Model reach:** a point source or a proxy array; the Ball depth is unconstrained (5–30 m), so this is a declared
  reach gap.
- **Coverage:** a full 45-point grid, reported in full; no sampling.
- **Bounds:**
  - z_s: p. 5;
  - offset: p. 7 ± 10 m (declared);
  - Ball depth: the whole plausible range (declared).
- No impact posterior is used, so the options and families are not applicable.
