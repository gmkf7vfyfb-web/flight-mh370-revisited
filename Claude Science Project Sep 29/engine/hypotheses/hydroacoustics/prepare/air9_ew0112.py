"""PRE-REGISTRATION (committed before any EW0112 value is digitised or any residual is re-scored): the air9 source
reference from the R/V Maurice Ewing cruise report EW0112 (Oct 2001), architecture request 11 Oct 2026 17:50Z.

SOURCE. EW0112 chief scientist's cruise report (MGDS doc_uid 3671), 13 pp. scanned (200 dpi, no text layer),
  sha256 eb00bc3abfc91c98da611f0b38d411af87e6423eb87f1c380ba32c12b56ac280. Values READ from the page images (printed
  page numbers "EW0112 n" in the footer equal the PDF page numbers):
  - p. 5: air9 = shots 317-340 at 57 s (jd 292 02:10:59.915-02:32:50.915) and 345-350 at 127 s (02:35:54.918-
    02:46:29.918), 27 33.22-34.04 S, 98 51.58-53.94 E, water 2718-2837 m. Gun tow depth: "11-12 m ... some being as
    shallow as 9 m" (15 m intended). [READ]
  - p. 6, Fig. 2: two air9 shots (deployment 9, 292 02:17:38 and 02:18:35) on the "slacked Ball hydrophone" and the
    ship's shot phone: time series "Pa @ receiver" and "Pa @ 1M", spectra "Pa^2/Hz @ receiver" (linear, 1-1e5 Hz).
  - p. 7: Ball hydrophone calibrated, "no gain"; "about 30 meters ahead of the trailing array" (an estimate; line
    "payed out fast"); hydrophone DEPTH NOT STATED. Shot phone uncalibrated, about 8 m ahead. [READ]
  - p. 2, Fig. 1: array plan; at 200 dpi most gun labels are ILLEGIBLE (transcription ledger graded per label).
  Blackman et al. (2004) do not state the source spectrum behind Fig. 23 "observed TL"; they quote the array peak as
  "230-240 dB re 1 uPa (adjusted to 1 meter range)" (source-class table), the same quantity as Fig. 2 "Pa @ 1M".

QUESTION. The module/audit air9 residual r_b = TL_obs(Fig. 23) - TL_model has slope +10.4 dB/oct (H01W) and +7.4
  dB/oct (H08S), level within 3 dB, station difference PASS (audit d225b80). TL_obs = SL_B(f) - RL(f) with an
  unstated SL_B. The module TL includes the surface image at z_s (KRAKEN), so for a correct model
  r_b = SL_B(f) - S0(f), S0 = the far-field notional (monopole) source spectrum level. Two hypotheses, fixed now:
  H-ref: SL_B(f) = the Ball near-source spectrum scaled to 1 m (Fig. 2 "@ 1M"). Then r_b = Delta_ref(f), the
     near-field reference factor 10 log10( <|e^{ik r1}/r1 - e^{ik r2}/r2|^2>_b * R1m^2 ), r1/r2 = direct/surface-image
     paths from the array to the Ball hydrophone, R1m = the range Fig. 2 uses for "@ 1M" (the ratio of its
     "@ 1M" to "@ receiver" peaks, DIGITISED), <>_b = third-octave band mean.
  H-flat: SL_B(f) is flat (the quoted peak level). Then r_b = C - S0(f), with S0(f) = Ball(f) - Delta_ref(f) + const
     from the digitised Fig. 2 Ball spectrum.
GEOMETRY PRIOR (declared; EW0112 p. 5/p. 7): z_s in {9, 10, 12} m (the module's air9 rows); horizontal offset of the
  Ball ahead of the array centre x_h in {20, 30, 40} m; Ball depth z_h in {5, 10, 15, 20, 30} m (not stated: the
  whole plausible range for a slacked line payed out fast); nominal (x_h, z_h) = (30, 15) m. Array: point source at
  the array centre (primary); a proxy 4 x 5 grid over the Fig. 1 extent as a sensitivity (gun volumes ILLEGIBLE ->
  equal strengths, declared).
TEST. corrected residual r'_b = r_b - Delta_ref,b (H-ref) or r_b - [C - S0,b] (H-flat, C = median), per station,
  on the audit's air9 rows (results/hydroacoustics-audit/data/air9_residuals.csv, model M1, each z_s), bands inside
  the Fig. 23 span where Fig. 2 is readable, graded with C1 (criteria.md 940f1a3): slope |s| <= 1.5 / 3 dB/oct;
  shape RMS <= 3 / 5 dB; level (H-ref only, R1m from Fig. 2) <= 3 / 6 dB.
  VERDICT per hypothesis, fixed now: SUPPORTED if, at the nominal geometry, both stations are PASS or PARTIAL in slope
  AND >= 50 % of the geometry grid is; NOT SUPPORTED otherwise. Both may be supported (then not separable, said so),
  or neither (then the tilt is not a source-reference artefact; it stays at the near-surface end as the SUS C4
  stand-in found). The grid spread is reported in full. Nothing is tuned to Fig. 23.
DIGITISATION RULE (Fig. 2, fixed now): the two Ball spectrum panels and the two Ball time-series panels; axis ticks
  located on the native 200-dpi raster; trace = the darkest pixel per column inside the panel; third-octave means;
  a band is READABLE if its mean is >= 5 % of full scale (about +/- 1 px resolution gives <= 1 dB there), else marked
  BELOW-READ and excluded. Values labelled DIGITISED. Both shots are digitised; their dB mean is used, their
  difference is reported as the reading + shot-to-shot spread.
LABELS: predictive audit, not a likelihood; hydroacoustics stays PREDICTIVE; UNCONVERGED inputs not used.
"""
