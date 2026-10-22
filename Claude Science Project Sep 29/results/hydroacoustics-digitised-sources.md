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
  with Table 5. OHASISBIO marks agree with Table 5 to within 5 s. **All H01W marks run later than the Table 5 H01W
  picks: the five map labels by 13.6-16.0 s, the pick bars (Figs 4-8) by 7.7-16.6 s, i.e. 7.7-16.6 s overall.** The evidence-sweep note of 17 Oct recorded
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
  air1, air9 (both panels) and air7 (both panels) trace cleanly; air2 (thick dark grey) is sparse, separable only
  where it leaves air1 (about 20 columns); air3 (dotted) is separable only at
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
  come from Metz et al. (2023), which Pete holds (artifact 7e4d336f); it was digitised by track metz-f35a on 22 Oct 2026 (`results/hydroacoustics-metz-f35a-anchor.md`).** [corrected 22 Oct 2026]
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
- "Kadri 2019 (ARA San Juan)" was a misattribution [corrected 22 Oct 2026]: JASA 146(4):2104 (doi 10.1121/1.5125251, "Source
  triangulation utilizing three-dimensional arrivals") is by Dall'Osto (2019). Kadri (2019) is Sci. Rep. 9:912 (doi
  10.1038/s41598-018-37626-z, sea-bottom elasticity, gold open access); it is held (artifact 133c4968;
  exchange `sources/open-access-fetched-2026-10-22/`) and was extracted by track metz-f35a. The Dall'Osto paper has no
  copy in the project store yet (abstract only); nothing from it has been digitised.

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
  (0.7 Pa peak at 3,300 km, 900 ± 200 MJ, η ~10⁻⁴). Metz et al. (2023) is the source (held, artifact 7e4d336f).

## COVERAGE
- Feasible set (what the publications render): Royer 9 figures + 5 tables; Blackman Fig. 23 (10 curves) + Table I
  (+ Figs 2, 22 and others not rendered as data here); Brown 16 figures (F-35A: none); Kadri 2024 17 figures + Table 1
  + S1 (2 figures); Kadri 2017 10 figures + Table 1; Kadri 2019 (Sci. Rep.; held, extracted 22 Oct); Nielsen 12 figures + Table 1; Vergoz 14
  figures + 2 tables; CMST 14 figures + Table 4; Duncan Fig. 3 (+ Fig. 5 held as PNG, not digitised).
- Model's reach (what the methods here can extract): vector drawings exactly (Kadri S1, Kadri 2017 Fig. 3a, CMST
  Figs 5/7/10/13); text-layer tables exactly; rasters to pixel precision with the stated reading uncertainty
  (Royer spectrograms, Blackman Fig. 23, Brown envelopes); raster waveform panels in the San Juan papers, Kadri PMC
  figures and CMST Figs 1-2 are within reach but not traced in this block.
- Proposal's coverage (what was done): 50 manifest rows; every named source touched except Kadri 2019 (Sci. Rep.; held since 22 Oct), Dall'Osto 2019 (not retrieved — ask Pete) and AF447.
- Gaps and status: (G1) Royer Drive link blocked, artifact copy used — closed; (G2) Royer H01W 16-s figure/table
  offset — open, goes into the raw-data request; (G3) Blackman air8 not separable, air3 partial, air4/air5
  weight-ambiguous zones — closed as a source limit; (G4) F-35A spectrum absent from Brown — open; Metz et al.
  2023 is held (artifact 7e4d336f) and was digitised on 22 Oct by track metz-f35a; (G5) 'Kadri 2019' was Dall'Osto 2019 (JASA, not retrieved — ask Pete); Kadri 2019 (Sci. Rep.) is held — (G6) AF447 hydroacoustic source not in the
  bibliography — open; (G7) Kadri 2024 Figs 1-8 at full resolution not re-extracted (PMC 750-px copies held) — open,
  low priority; (G8) San Juan / CMST Fig 1-2 waveform rasters not traced — open, do when a weak-signal trial needs
  them; (G9) Brown fireball amplitudes are in counts — closed as a source limit.
- ESS: not applicable (no sampling in this block).

done: block 1 — six sources digitised, manifest of 50 rows, overlays and METHOD records committed.
next: trace the San Juan / CMST waveform rasters when block 8 asks; Metz et al. 2023 and Kadri 2019 are held (extracted 22 Oct); ask Pete for Dall'Osto 2019 (JASA) if wanted; add the H01W 16-s question to the Royer raw-data request (block 12).
blocker: none for this block; G4 is closed by the 22 Oct extraction (anchor ruling pending); G5 needs Dall'Osto 2019 only if the San Juan 3-D arrival is to be used.

## Addendum, 22 October 2026 (correction track: items 3, 6, 7 and the AF447 search) — CORRECTION OF RECORD

Hydroacoustic Module (correction track). Pete's rule of 22 Oct applies: a failed download is recorded as **"not retrieved
— ask Pete"**, never as "closed access", and nothing is left out because of it. Everything below is DIGITISED publication
data or a check against the module's own processing; no measurement is new. Caveats C1 and C2 apply to every use downstream.
Module commits: `5230679` (pre-registration of stage 1b + waveform digitiser + overlay), and the follow-up results commit
named in the coordination entry. Companion note: `results/hydroacoustics-calibration-events-stage1b.md`.

**What was wrong in the record above.**
- **"published-figures" folder.** No folder of that name exists in the archive on any branch (all 19 remote branches
  searched by tree listing on 22 Oct; the only hits are the module's own `published-figures-pmc/`). The 2,008-px rasters
  the text above refers to are the embedded images of the **publisher PDF of Kadri (2024)**, which Pete holds on the
  project Drive (`Underwater_acoustic_analysis_reveals_unique_pressu-2.pdf`, Drive id 1ZxR_3Y6Ryn-OXyRJ0tjOPSjassZn8ioW,
  16.2 MB). **Not retrieved — ask Pete:** the file exceeds the Drive connector's 10 MB download limit, and the PMC PDF route
  returns a browser challenge page. Please drop it into `Downloads/mh370-inputs/hydroacoustics/papers/`.
- **Kadri 2017** is held at full resolution (Unpaywall/Drive/`fetch_article_fulltext` copies are byte-identical, sha256
  6d8adc00…); its native-resolution figures were already extracted (`ground-truth-cases/figures/kadri2017_p*.png|jpeg`,
  1,000–1,618 px). The G7 wording "Kadri 2017 PMC JPEGs only" was wrong.
- **G7 (Kadri 2024 Figs 1–8 at full resolution): OPEN, not retrieved — ask Pete** (publisher PDF above). The PMC rasters
  (669–799 px; re-fetched 22 Oct from cdn.ncbi.nlm.nih.gov, identical to the held copies) were used for every trace below,
  at a declared 1-px resolution.
- **G8 (San Juan / CMST waveform rasters): CLOSED** — traced (`results-data/digitised/waveform-rasters/`, 33 summary rows,
  overlays for every panel; `prepare/digitise_waveform_rasters.py`):
  - Kadri 2024 Fig. 8 (calibration charge, pressure axes): peak 3.44 Pa = 130.7 dB re 1 µPa at H10N (Vergoz printed
    130 dB: +0.7 dB), 1.06 Pa = 120.5 dB at H04S (Vergoz 122 dB: −1.5 dB), 15.0 Pa at H03S (via land).
  - Kadri 2024 Fig. 7 (San Juan event): 8.57 Pa = 138.7 dB at H10N (Vergoz 139 dB), 5.43 Pa = 134.7 dB at H04S (Vergoz
    134 dB), 0.92 Pa at H03S.
  - Vergoz 2021 Fig. 2 and Nielsen 2021 Fig. 3 carry no pressure scale: times and normalised envelopes only. Peak times
    agree across the three papers within 3 s (charge at H10N: 21:12:06 Kadri, 21:12:04 Vergoz, 21:12:03–06 Nielsen nodes
    1–3; San Juan at H10N: 14:59:17.6, 14:59:16.0, 14:59:13.6–16.5). Nielsen's H10N/H10S Dec-1 panels also show the earlier
    arrival at about 21:05:27 / 21:03:58 discussed in the paper.
  - CMST 2014-30 Fig. 1 (Pa axis): peak 1.42 Pa at 01:33:44.3 UTC. **Overlay check against our own read of the same IMOS
    recording** (3315, 531A728A.DAT, pre-registered clock correction −25.82 s; `prepare/cmst_fig1_imos_overlay.py`):
    1–120 Hz peak −0.7 dB, noise −0.4 dB, time +2.4 s. The module's IMOS calibration chain and clock correction reproduce
    CMST's published trace.
  - CMST Fig. 2 (HA01 spectrograms, no time series in the held raster): colour scale inverted; 5–40 Hz peak at
    01:34:50–52 on all three hydrophones (CMST text 01:34:50 ± 3 s), 5–8 dB above the panel median.
- **G6 (AF447 hydroacoustic source): CORRECTED.** The bibliography lacked an AF447 entry, but the source is held: Kadri
  (2024) Fig. 5a (H10S, 10-min window after 02:41 UTC, 1 Jun 2009), Fig. 3 (2,211 km, 306.46°), text p. 3 ("pressure values
  reaching 75% of that observed for F-35a ... over a distance of 2200 km") and S1 (impact around 02:14 UTC, 3°03′57″N
  30°33′42″W, about 282 km/h, belly first). Search of the literature (web, 22 Oct) found no other published hydroacoustic
  analysis of AF447 with times, positions and levels. Secondary, not peer-reviewed: 370location.org (Sep 2017) reports
  that CTBTO Ascension data were examined during the 2009 search with no signal, and that Atlantic island seismometers
  show no T-phase match. AF447 search literature held on the Drive (`AF447/` folder: BEA final report, Stone et al. 2014,
  Metron reports) contains no hydroacoustic impact analysis. Nothing is "not retrieved" for AF447.
  - **New finding (EXPLORATORY, `prepare/kadri_crash_timing.py`):** the sound-channel arrival from the AF447 site at H10S
    is 02:39:19 ± 6 s (BEA impact 02:14:28; 2,209.7 km; 1.482 ± 0.006 km/s). Kadri's Fig. 5a window starts at 02:41:00 and
    his box is 02:44:58–02:46:27, 6.4 min after the predicted arrival. The panel therefore cannot show the AF447 impact by
    the water path, and the AF447 coupling upper bound (stage 1b) is **not applicable**. The same check passes for the
    F-35A (−2 / +3 s) and Lion Air 904 (−35 / +8 s), and fails for Yemenia 626 (+5.6 / +8.9 min), Transair 810 (+4.3 /
    +5.8 min) and Sriwijaya 182 (−11.8 min; a shallow-water source, possibly a land-coupled path). Some S1 times are
    given only to the minute. Added as question E6 for Kadri (REQUESTS.txt addendum).
- **Kadri's processing chain (brief §5).** Confirmed from the texts, with two refinements: Kadri 2017 (Sci. Rep. 7:13949,
  p. 7) high-passes below 5 Hz with a Butterworth IIR and detects by windowed entropy (window 4 s, step 0.5 s, threshold
  2.3·10⁴, peaks within 2 s across the three channels); the **2–40 Hz band-pass is added in Kadri 2024** (p. 11: "in
  addition to the CTBTO high pass filter"; filter order not stated; log-energy entropy, "a few seconds" window, same
  threshold, TOA cross-correlation bearing ±0.4° at 99.5 %). The SnT 2025 poster (held as text) states the same chain.
  Kadri 2019 (Sci. Rep. 9:912) is a theory paper with no processing chain. So "Kadri (2017, 2019, 2024) high-passes at
  5 Hz and band-passes 2–40 Hz" should read "Kadri 2017 high-passes at 5 Hz; Kadri 2024 adds a 2–40 Hz band-pass"; the
  effective passband of the 2024 chain is 5–40 Hz, as the module's comparison charts already use. Request to the
  architecture session to amend §5 (not edited here).
- **IMOS 3315 / 3275 backgrounds (stand-in note of the injection track): CORRECTED to a fact.** The public IMOS archive
  (`imos-data.s3-ap-southeast-2.amazonaws.com/IMOS/ANMN/Acoustic/`, listed 22 Oct for all six sites, not truncated)
  holds **no deployment 3315 or 3275**: PAPCA has 3376 (from 28 Nov 2013) and 3318 (from 28 Nov 2014); PAPOR has 3274 but no
  3275. The 8 March 2014 files we hold for 3315/3275 come from the MH370 release (`IMOS_MH370_DataOverview.doc`,
  `IMOSFilesLocation3315.txt`). So nothing was fetched, the stand-in (own 8 March recordings outside the request window,
  with the co-located 14-day sets as cross-check) is the only background available from the public archive, and the
  1–15 March 2014 data for 3315/3275 are **not retrieved — ask Pete** (CMST/Curtin may hold them). Recorded in
  `data/imos_background/MANIFEST.json` (`not_in_public_archive`).

**Coverage (this addendum).** (a) Feasible set: every rendered dataset in the named sources plus the AF447 literature.
(b) Reach: vector and raster tracing at the held resolution (PMC 669–799 px for Kadri 2024; 1,539–1,870 px for the San
Juan papers; 561 px for CMST). (c) Coverage: all Kadri 2024 waveform panels with pressure axes for the San Juan event and
charge (Figs. 7–8) and AF447 (Fig. 5a); all six Nielsen Fig. 3 panels (18 node traces, two dead channels flagged); the
four Vergoz Fig. 2 strips; CMST Figs. 1–2. Gaps: G7 open (publisher PDF not retrieved — ask Pete); Dall'Osto 2019 (JASA
146:2104) not retrieved — ask Pete; 3315/3275 March backgrounds not retrieved — ask Pete; Kadri Fig. 4/6 panels were not
re-traced (the module's 11 Oct peaks stand).

done: G6 and G8 closed, G7 re-stated as not retrieved, Kadri chain confirmed with refinements, 3315/3275 archive status fixed.
next: score Kadri Fig. 4/6 panels for timing with BEA/NTSB times to the second; trace Kadri 2024 Figs 4–8 again from the
publisher PDF when Pete provides it.
blocker: none in this module; the publisher PDF, Dall'Osto 2019 and the 3315/3275 March data need Pete.
