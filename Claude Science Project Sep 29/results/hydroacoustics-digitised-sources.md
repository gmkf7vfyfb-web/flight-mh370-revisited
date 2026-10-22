# Hydroacoustics: digitised sources inventory and extraction (work order block 1)

Hydroacoustic Module (digitisation track), 22 October 2026. Brief: `threads/master-prompts/hydroacoustics.md`
(Refresh v2 §4: no raw data from Kadri or Royer is expected, so every dataset rendered in the publications is
extracted and recorded). Work order: `threads/work-orders/hydroacoustics-order-2026-10-21.md`, block 1.

**Everything in this note and in the files it lists is DIGITISED publication data or a raster copy of a published
figure. None of it is a measurement.** Caveats C1 (propagation slope misfit, +10.4/+7.4 dB per octave at H01W/H08S)
and C2 (coupling efficiency not calibrated; η swept over four decades, F-35A upper anchor) apply to every use of these
data downstream. Both Kadri times are carried everywhere: text time 00:52:03 and caption time 00:54:30.

## Deliverables

- Manifest (50 rows: source, year, figure/table, page, what it is, method, resolution, units, verification check,
  file path, gap notes): module branch `engine/hypotheses/hydroacoustics/results-data/digitised/MANIFEST.csv`.
- Extracted data: `engine/hypotheses/hydroacoustics/results-data/digitised/<source>/` (royer-2016, blackman-2004,
  brown-2026, kadri-2024, kadri-2017, ground-truth-cases, cmst-2014), each with `METHOD.json` (script docstring,
  PDF sha256, run summary) and an `overlays/` folder with the extracted series drawn over the source image.
- Scripts (module branch `prepare/`): `digitise_royer_2016.py`, `digitise_blackman_fig23_all.py`,
  `digitise_brown_2026.py`, `digitise_kadri_2024_s1.py`, `digitise_ground_truth_cases.py`, `digitise_cmst_2014.py`.
  The earlier `digitise_duncan_fig3.py` and `digitise_blackman_fig23.py` were verified, not changed.
- Source PDFs used (not committed; copies in `/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-digitisation/sources/`):
  Royer LDO-201608 (project artifact, sha256 2e7190b9…), UCRL-TR-207323 (repo copy = OSTI purl 15011808, sha256
  34a735f7…; OSTI purl 850576 scan also fetched), brown2026.pdf (repo), Kadri 2024 S1 (Europe PMC supplementary,
  PMC11065988), Kadri 2017 (Unpaywall, sha256 6d8adc00…), Nielsen 2021 (Unpaywall, 73aa1d88…), Vergoz 2021
  (Unpaywall, 48afc07d…), CMST 2014-30 (repo).
- Commits on `hypothesis/hydroacoustics`: 9e234b2 (Royer), b8976bd (Blackman), 9854c72 (Brown), 4ec1c07 (Kadri +
  San Juan), d94e295 (CMST), plus the manifest commit recorded in the coordination entry.

## Per-source summary (order of value as in the task)

### 1. Royer (2016), OHASISBIO report LDO-201608, 18 pp
- Download: the public Google Drive link from Wise's Substack redirects to `drive.usercontent.google.com`, which is
  not on the sandbox allowlist (GAP for the link; not a gap for the data, because the project already held the PDF as
  artifact `royer-2016-LDO-201608.pdf`, byte-identical content, used here).
- Tables 1-5 extracted from the text layer: 14 hydrophone positions (8 OHASISBIO incl. the lost NEAMS, 6 IMS),
  sensitivities, 20 located events with standard errors, 143 picked arrivals. Table 2 equals Table 4 for A, B, C1,
  C2, D1, D2. **Verification:** every pick gives an implied path speed between 1.467 and 1.518 km/s (median 1.482),
  so the table, the positions and the origin times are mutually consistent.
- Figures: 34 spectrogram panels (Fig. 2 two 45-min H01W-2 panels; Figs 4-8 twenty 3-min panels for events A, B,
  C1, C2, D2; appendix twelve ~33-min strips for SWAMS-3, SSEIR, H01W-2 covering 00:00-02:00 UTC) converted to dB
  grids (colour→dB on the printed 70-100 dB 'jet' bar, ±1.5 dB; levels above 100 dB clipped) with 5-40 Hz, 10-15 Hz
  and 2-60 Hz band-mean series per pixel column (0.28 s per column on the 3-min panels, 1.56 s on the strips).
  The appendix strips are not 30 min wide: the printed labels sit 192 px per 5 min apart and the frame runs on, so
  the time axis is tick-calibrated (8 strips) or uses that fixed geometry (4 SWAMS-3 strips crossed by shot lines).
  The MAD panel of Fig. 8 is labelled 01:58 on the right; by tick spacing it is 01:48 (typo).
- Author marks: 19 arrival labels on the maps and 47 pick bars/arrows on the panels converted to UTC and compared
  with Table 5. OHASISBIO marks agree with Table 5 to within 5 s. **All H01W marks (map labels and pick bars for A,
  B, C1, C2, D2) run 13.6-16.6 s later than the Table 5 H01W picks.** The evidence-sweep note of 17 Oct recorded
  this inconsistency; it is now quantified. The offset equals the 2014 GPS-UTC leap-second count (16 s) that the
  report says was applied to the OHASISBIO clocks, which suggests one of the two H01W time bases was not corrected.
  Which is right is not decidable from the report (GAP, listed for the Royer raw-data request; it does not change
  the inferred path speeds by more than 0.011 km/s). The NCRO label on the D2 map (01:49:48) differs from Table 5
  (01:50:28.57) by 40 s; treated as a figure error.

### 2. Blackman et al. (2004), UCRL-TR-207323
- Source resolution: both public OSTI copies were fetched. purl 15011808 is byte-identical to the repo copy and
  holds Fig. 23 as a 351×458 px raster (153 dpi); purl 850576 is a bilevel 200-dpi page scan in which Fig. 23 is
  about 190×270 px. Rendering at 600 dpi only upsamples the 351×458 raster. **The limit is the source.**
- All ten curves traced with a grey-window + line-weight + dotted-duty tracer (overlay PNG per curve). Separability:
  air1, air9 (both panels), air7 (both panels) and the thick air2 trace cleanly; air3 (dotted) is separable only at
  5-18 Hz where it peaks at 140 dB; air8 (dotted) lies on the thick air7 curve and is NOT separable; air4 and air5
  differ by one grey step and are separated only by line weight, so air4 below 20 Hz and air5 above 40 Hz are flagged
  weight-ambiguous (the report text puts air4 with air1-air3 at 130-135 dB in the 5-8 Hz band, so the 120-130 dB
  light-grey curve there is air5). The new air9 traces reproduce the module's existing air9 digitisation column
  for column (median difference 0.0 dB).
- Appendix A Table I (shot lines: 14 segments, air1-air9, positions, times, intervals, seafloor depth) parsed.

### 3. Brown et al. (2026), Icarus, F-35A
- **The paper contains no F-35A waveform or spectrum.** The F-35A enters only as text (pp. 18-19): impact energy
  900 ± 200 MJ, observed peak pressure 0.7 Pa at H11 (Wake Island), range 3,300 km, Arons relation (Eq. 2) giving a
  coupling efficiency to the SOFAR channel "of order 10⁻⁴, an upper bound", with the signal one order of magnitude
  above background per Metz, Obana & Fukao (2022/2023, Pure Appl. Geophys. 180:1343-1351, doi
  10.1007/s00024-022-03117-6). Regenerating Eq. 2 with the text values gives a SOFAR yield of 0.045 kg TNT and
  η = 2.1 × 10⁻⁴ for 900 MJ. **The F-35A source spectrum needed by the TL-recalibration track therefore has to
  come from Metz et al., which is closed access and not held (GAP).**
- What the paper does render was extracted: the Arons relation (Fig. 3, analytic), the 2 Sep 2003 fireball at H03N
  (Fig. 7: waveform envelope, 4-9 Hz; wavelet scalogram 2-15 Hz relative; bar spectrum) and the 7 Oct 2004 fireball
  at H08S (Fig. C.10 one-hour pixel envelopes; Fig. C.12 stacked waveform envelope and 0-40 Hz spectrogram). The
  waveform axes read "Pa" but span ±5×10⁴ and ±4×10⁶, i.e. uncalibrated counts; only relative levels are usable.

### 4. Kadri (2024) with S1; Kadri (2017); Kadri (2019)
- Fig. 9 panels a-e: confirmed held as PDF-vector traces on the module branch (five CSVs, ~8,700 rows each, ~19
  vertices/s). Not re-extracted.
- S1 Figure S1 (7 March 2014 first-route window): five pressure traces extracted from the PDF vector paths with the
  archive's method: (a) H08S from 17:49, (b) H08S 18:44, (c) H08S 19:00, (d) H11S 19:35, (e) H11S 19:41 UTC; 15,400
  to 28,200 vertices per panel (41-82 vertices/s); the plotted series start about 15 s before the axis and vertices
  outside the printed axes are flagged. Spectrogram panels saved as rasters.
- Figs 1-8, 10-17 of Kadri 2024 and Figs 1-10 of Kadri 2017: Europe PMC published JPEGs (750-800 px wide) held as
  raster copies. nature.com is blocked in the sandbox; the full-resolution embedded rasters (2,008 px) of Figs 4-8
  exist in the archive's `published-figures` folder, which was not opened (it is outside the two folders this task
  names in the private `.sources` tree).
- Kadri 2017: EQ1/EQ2 validation earthquakes, the 7 Mar 2014 20:30 UTC impact at 65.5°S 32.5°E (6,150 km), E1/E2
  candidates (301.4° ± 0.4°, 1,900 ± 200 km, arrival 01:34:40; 234.6° ± 0.4°, 1,940 ± 200 km, arrival 00:50:00), HA01
  channel coordinates and depths, Table 1, and Fig. 3a distance pdfs from the vector outlines (peaks 2,504 / 5,504 /
  6,254 km against the text's 2,500 / 5,500 / 6,250).
- Kadri 2019 (ARA San Juan): the paper is Kadri, Wang et al., JASA 146 (2019), doi 10.1121/1.5125251, "Source
  triangulation utilizing three-dimensional arrivals" — closed access; `fetch_article_fulltext` was not attempted
  because Europe PMC lists it as not open access. **GAP.**

### 5. ARA San Juan and AF447
- Nielsen et al. (2021), PAAG 178:2557 (CTBTO): Table 1 (ground truth vs CTBTO estimates, error ellipses, origin
  times 13:51:00 and 20:04:55 UTC), text times (arrivals ~14:58 HA10, ~15:20 H04S; ranges ~6,000 and ~7,700 km),
  12 figure rasters at 1,870 px (waveforms, calibrated spectra and spectrograms, cepstra, PE transmission-loss
  sections, PMCC panels with azimuths 223.6°/207.8° at H04S).
- Vergoz et al. (2021), PAAG 178:2527 (CEA): Table 1 (13 H10N reflectors), Table 2 (cepstral doublet delays), text
  values (origin 13:51:05 ± 9 s; grenade 20:04:30 ± 14 s; speeds 1.460-1.485 km/s; relocation 3.5 km), 14 rasters.
- Waveform and spectrum panels of both San Juan papers are 1,600-1,870 px screen renders with printed axes; they are
  held as rasters and are traceable with the module's raster method if the weak-signal trials need them (next step,
  not done here).
- AF447: `hydroacoustics-references.bib` lists no AF447 hydroacoustic paper (the Kadri 2024 Fig. 5a AF447 panel is
  the only rendering held, as a 750-px PMC raster). **GAP: no AF447 source identified in the bibliography.**

### 6. Duncan & Dall'Osto (2023) and CMST (2014)
- Duncan Fig. 3: existing CSVs verified (both paths 12.5-3,487.5 km in 25-km bins, 140 bins each; depth and
  DSC-axis series 702 columns each; MH370-path level falls 21 dB per decade from 100 to 3,000 km, F-35 path 4 dB).
  The geometry caveat in the file header stands: the "MH370" path is the 301.6° HA01 bearing, not a core-region path.
- CMST report 2014-30: the detection plots are vector drawings. Fig. 5 (HA01, 00:00-08:00 UTC): 270 detections
  with bearing and time; the orange-arrow detection is at 01:34:10 UTC, 302.3° (the text says 01:34:50, 301.6°, so
  the plotted point is 40 s and 0.7° off the text; both carried). Fig. 7 (HA08S, 00:00-03:00): 802 detections plus
  CMST's expected-bearing line for the 01:34:50 source; Table 4 attributes the bands to a Sri Lanka/Bay of Bengal
  survey (34.9-35.4°), the TGS survey off NW Australia (113.0-113.6°), one unknown at 168.05° (00:11-00:12 UTC)
  and a Java Trench earthquake (92.5-93.5°, 01:59-02:00). Fig. 10: 593 TGS detections and the navigation bearing.
  Fig. 13: bathymetry along 301.61° ± 0.75° from HA01. Figs 1-2 (the 01:34:50 signal, 561×420 px) held as rasters.

## Inputs for the TL-recalibration track (cc)
- air1-air8: `results-data/digitised/blackman-2004/fig23_<panel>_<site>_DIGITISED.csv` with the SEPARABILITY line in
  each header; usable without qualification: air1 (DGN), air7 (DGS, CL), air9 (DGS, CL); with qualification: air2
  (sparse), air4 above 20 Hz, air5 below 40 Hz, air3 at 5-18 Hz; not usable: air8.
- F-35A source spectrum: not in Brown et al. (2026). The only F-35A numbers are the text values above
  (0.7 Pa peak at 3,300 km, 900 ± 200 MJ, η ~10⁻⁴). Metz et al. (2023) is the source to obtain.

## COVERAGE
- Feasible set (what the publications render): Royer 9 figures + 5 tables; Blackman Fig. 23 (10 curves) + Table I
  (+ Figs 2, 22 and others not rendered as data here); Brown 16 figures (F-35A: none); Kadri 2024 17 figures + Table 1
  + S1 (2 figures); Kadri 2017 10 figures + Table 1; Kadri 2019 (closed); Nielsen 12 figures + Table 1; Vergoz 14
  figures + 2 tables; CMST 14 figures + Table 4; Duncan Fig. 3 (+ Fig. 5 held as PNG, not digitised).
- Model's reach (what the methods here can extract): vector drawings exactly (Kadri S1, Kadri 2017 Fig. 3a, CMST
  Figs 5/7/10/13); text-layer tables exactly; rasters to pixel precision with the stated reading uncertainty
  (Royer spectrograms, Blackman Fig. 23, Brown envelopes); raster waveform panels in the San Juan papers, Kadri PMC
  figures and CMST Figs 1-2 are within reach but not traced in this block.
- Proposal's coverage (what was done): 50 manifest rows; every named source touched except Kadri 2019 and AF447.
- Gaps and status: (G1) Royer Drive link blocked, artifact copy used — closed; (G2) Royer H01W 16-s figure/table
  offset — open, goes into the raw-data request; (G3) Blackman air8 not separable, air3 partial, air4/air5
  weight-ambiguous zones — closed as a source limit; (G4) F-35A spectrum absent from Brown — open, needs Metz et al.
  2023 (closed access); (G5) Kadri 2019 closed access — open; (G6) AF447 hydroacoustic source not in the
  bibliography — open; (G7) Kadri 2024 Figs 1-8 at full resolution not re-extracted (PMC 750-px copies held) — open,
  low priority; (G8) San Juan / CMST Fig 1-2 waveform rasters not traced — open, do when a weak-signal trial needs
  them; (G9) Brown fireball amplitudes are in counts — closed as a source limit.
- ESS: not applicable (no sampling in this block).

done: block 1 — six sources digitised, manifest of 50 rows, overlays and METHOD records committed.
next: trace the San Juan / CMST waveform rasters when block 8 asks; obtain Metz et al. 2023 and Kadri 2019 through
Pete or the Kadri collaboration; add the H01W 16-s question to the Royer raw-data request (block 12).
blocker: none for this block; G4/G5 need closed-access papers that only Pete or a collaborator can supply.
