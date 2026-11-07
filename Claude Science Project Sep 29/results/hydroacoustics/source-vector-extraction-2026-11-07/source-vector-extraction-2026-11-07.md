# Hydroacoustic source PDFs: vector recovery and coverage (7 Nov 2026)

Folder: `Claude Science Project Sep 29/results/hydroacoustics/source-vector-extraction-2026-11-07/`. Coverage table: `source-figure-coverage.csv` (one row per figure panel, image, table or item; 1,130 rows). Status marks: **[re-run]** = produced by code in this session and read back from the files; **[project record]** = taken from the hydro database or repository; **[not checked]** = stated without a check.

## Summary
- We found 62 distinct PDF files (by sha256) that are hydroacoustic sources or candidates. 18 of them are held in more than one place. [re-run]
- 14 files are 8 March 2014 sources. 22 are calibration or reference sources. 8 are theory or minor items. 18 are not hydroacoustic sources and are excluded. [re-run] Inventory: `source-pdf-inventory.csv`.
- Two cited sources are not held: Duncan and Dall'Osto (2023), JASA Express Letters, article PDF: not retrieved — ask Pete. Dall'Osto and Dahl (2014), APL-UW report on Diego Garcia South: not retrieved — ask Pete. [re-run]
- We classified 504 figure pages in 42 in-scope files: 191 vector panels, 18 mixed panels, 833 raster images, 59 pages with vector content but no numeric axes. [re-run]
- We wrote 120 new CSV files: 99 vector panels, 19 tables, 2 raster digitisations. 90 vector panels calibrate with relative residual at or below 3e-3; 9 are flagged. [re-run]
- 60 of the new files come from 8 March 2014 sources. The largest new sets are Stead (2014), Kadri (2024) Figs 7, 14 and 17, Kadri (2019) Figs 5 and 6, Kadri et al. (2017) Figs 1 and 3b, and the CMST transmission-loss panels. [re-run]
- Kadri 2019 Fig. 4 was not digitised here, by instruction. Our check found that Fig. 4 is raster; the vector panel on that page is Fig. 5. [re-run]

## What is new for 8 March 2014
1. **Stead (2014), LA-UR-14-24972** (also embedded in the ATSB 2017 report, Appendix J; the copies give identical vertex counts). Figs 1, 2 and 5 are vector waveforms: H01 three elements in five octave bands at 3114-3130 s after 00:00 (00:51:54-00:52:10 UTC), the 10-20 Hz cross-correlations (lags -6 to +6 s), and H08 at 3705-3735 s (01:01:45-01:02:15 UTC). The traces carry no amplitude scale, so y is the fraction of axis height. Figs 6, 7 and 9 are Amsterdam Island (AIS) seismic data at 00:23:10-00:24:00 and 00:26:10-00:27:00 UTC, with per-trace amplitude scales from the text layer. None of these were in the database before. [re-run]
2. **Kadri (2024) Fig. 17**: H08S, 7 Mar 19:27-19:29 UTC. Three pressure channels, windowed entropy (right axis) and bearings. Bearing markers are at 210.0 deg, plus one at 63.70 deg at 1.539 min. The figure's own data tip reads X 1.53907, Y 63.6981, which our OCR-calibrated axes reproduce to 0.002 deg. [re-run]
3. **Kadri (2024) Fig. 7** (ARA San Juan, 15 Nov 2017; H03S, H04S, H10N): re-extracted from vectors. The earlier database tables `dg_waveform_rasters_kadri2024_fig7_*` were raster reads. [re-run; earlier tables: project record]
4. **Kadri (2024) Fig. 14**: model curves of distance and time after the 7th arc against average velocity. [re-run]
5. **Kadri (2019) Fig. 5**: raw HA08s data around the restart after 25 min of missing data from 03:07 UTC, 8 Mar. The legend is printed as HA01W1-3, but the caption says HA08s; we report it as printed. **Fig. 6**: PDF of the location of HA_30 (23:57 UTC, 7 Mar). [re-run]
6. **Kadri et al. (2017) Fig. 1**: HA01 channels 1-3 at about 19:45 UTC, 7 Mar, and the water-tank experiment. **Fig. 3b**: EQ1 pressure trace. The mode curves in Fig. 3b are part of the raster; only the arrow is vector. [re-run]
7. **CMST 2014-30 Fig. 13**: the two RAMGeo transmission-loss panels (x10^6 m range). The bathymetry panel was already in the database. [re-run]
8. **Kadri, Crivelli and Parsons (2017), report to the ATSB, Fig. 4** (HA01, three channels, 200 s, caption time 01:34:50 UTC): raster digitisation as a min/max envelope per pixel column, at 0.042 s and 0.0018 Pa per pixel. The caption does not state whether 01:34:50 is the window start or the arrival. [re-run]
9. **Duncan and Dall'Osto (2023) Fig. 5** (figure image held in the repository): seabed and sound-channel-axis depth along their path, digitised from the raster at 7.3 km and 8.2 m per pixel. Their Fig. 3 was already digitised. [re-run; Fig. 3: project record]
10. **Tables now available as files**: CMST 2014-30 Tables 1-3 (Table 4 was already held), Scott Reef Table 1 (least-squares fix), Kadri (2019) Tables 1-3, Brown et al. (2026) Tables 1-3, Blackman et al. (2004) Tables 2-5, Tolstoy et al. (2004) Tables 1-2, the Kadri ATSB report Table 1, and whale-study deployment tables. The Kadri (2019) Table 3 text layer agrees with the database copy, which was typed from a page render. [re-run]

## Calibration sources (new vector extractions)
Harben et al. (2002) Figs 1, 5 and 6 (implosion waveforms and spectra; the labels are stroked glyphs, read by OCR); Blackman et al. (2004) Fig. 9 (SUS shots at IMS stations) and Fig. 1 (source map, georeferenced, with a Mercator latitude fit); Tolstoy et al. (2004) Fig. 4 (all paths; the x axis is log10 of frequency); Tian and Kadri (2017) Figs 2-4 (theory; two copies with different content hashes); whale studies (Leroy 2021 Figs 3 and 6-8; ESR 37:289 Fig. 4). [re-run]

## Checks made
- Kadri 2024 Fig. 9a re-extracted with the same code: 8,712 trace vertices, against 8,706 in the database. The values agree within 2e-4 Pa and 0.006 s. [re-run]
- CMST Fig. 5: the tick spacing alternates between 41.48 and 42.11 pt, a quantisation in the source file. This gives a residual of about 0.007 h on the time axis, which is the resolution limit of that figure. [re-run]
- Every panel CSV header gives the source sha256, page, axis transform, label values, residuals, units per point and coordinate quantum. Each folder has a METHOD.json with the file sha256 values. [re-run]
- We checked rendered pages against re-plots for all 8 March panels and for a sample of calibration panels. [re-run]

## Raster-only items still open (8 March sources)
CTBTO IDC infrasound report Figs 2-5 (166-200 dpi); Stead Figs 3, 4 (H01 spectrograms near 00:52 UTC, 165 dpi) and Fig. 8; Kadri ATSB report Figs 2, 5, 6 and 7 (Fig. 6: Scott Reef, and the raw records are held); Kadri et al. 2017 Figs 2, 4, 5 and 6; Kadri 2024 S1 spectrograms and Fig. S2; Fenimore et al. (2014) Figs 1-6 (148 dpi, noise-source maps on the arc); ATSB 2015 Fig. 35; ATSB 2017 Figs 87 and 88 and the Scott Reef appendix blocks 100-105 (raw records held); Scott Reef report Figs 1-3 (raw records held). The full list with resolutions is in the coverage table (`open_items` = 'raster only; not digitised'). [re-run]

## Second pass (text and tables)
`text-values-second-pass.csv` lists 182 sentences with UTC times and bearings from the 8 March sources. For 61 of them, the time string was not found in the text columns of the database. This check is crude, because a value can be stored as a number, so the count is provisional. Items of note: Stead reports an AIS Rg surface wave at about 00:26:25 UTC, 8 Mar, and uses the 2 Mar 2014 M6.5 Japan event (20:11:23 UTC) for the station orientation. Kadri 2024 S1 gives H08S signals at 17:54, 18:49 and 19:05 UTC and H11S signals at 19:40 (143 deg) and 19:46 (269 deg) UTC, all on 7 Mar. Royer notes similar events at 23:47 UTC, 7 Mar, and after 02:00 UTC, 8 Mar. [re-run; database presence: provisional]

## Items that look unused
These items are not used in any analysis or result in the repository text files that we searched (a sparse clone of the .md, .py and .json files). Kadri 2024 Fig. S1 traces, CMST Fig. 10 and CMST Fig. 13 bathymetry appear only in the digitising scripts and the database build. Royer appendix spectrograms appear only in the noise-fix database build. Tolstoy Fig. 4 appears nowhere. All files new in this folder are unused so far. The search covered file names and table names, not data flow, so this is provisional. [re-run, provisional]

## Key assumptions and modelling choices
- Calibration acceptance: relative residual at or below 3e-3 = ok; up to 2e-2 = flagged; above that = failed. Proposed here.
- Multipliers printed as glyph outlines (x10^5, x10^6, x10^7) were read from the rendered page and are stated in each header. Proposed here; [not checked] against a second reader.
- Panels with no printed amplitude scale (Stead, Harben Fig. 6, Blackman Fig. 9 traces) give y as the fraction of axis height. Proposed here.
- Chu and Fan (2024) histograms and one Miller et al. (2021) panel were not extracted: the automatic axis pairing was not reliable. Open.
- Excluded files: project drafts and presentations, accident reports, flight-path and debris material, and items that mention hydroacoustics only in passing (see the inventory). Proposed here.
- Kadri IMOS figure times are logger time. The database applies the segment clock errors. Pete's ruling; no IMOS figure was re-timed here.
- Where our results differ from a published list, our check does not reconcile them; the cause is not known, and it can be our error.
