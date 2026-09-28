# Blackman et al. (2004) Indian Ocean Hydroacoustic Calibration - Structured Data Extraction

This directory is represented in the parent backup by `Blackman_2004_extracted_data_2026-09-27.zip.b64`. Restore instructions are in `../BINARY_RESTORE.md`.

The archive contains machine-readable data transcribed from Donna K. Blackman et al., *Methods for Calibrating Basin-Wide Hydroacoustic Propagation in the Indian Ocean*, Final Report, September 2004, UCRL-TR-207323 (OSTI 850576), plus explicitly reported detection/spectral observations from the report and closely related 2004 JASA paper.

## Files in the ZIP

- `blackman_2001_airgun_shot_lines.csv` - Appendix A Table I line segments for air1-air9: JD/time, endpoint coordinates, seafloor depth, shot interval and shot ranges. ISO times and decimal degrees are derived.
- `blackman_2001_airgun_site_summary.csv` - derived representative air1-air9 locations/time bounds.
- `blackman_2001_nonairgun_source_events.csv` - Appendix A Tables 2-4: 20-L triggered cylinder shots, single 22-L sphere shots and five-sphere clusters.
- `blackman_2003_source_events.csv` - Appendix A Tables 3-5: 2003 single-sphere, five-sphere and SUS events.
- `blackman_2003_site_summary.csv` - derived A1-A11 site summary.
- `blackman_source_class_characteristics.csv` - airgun/sphere/cylinder/SUS source properties recovered from report text.
- `blackman_receiver_observations.csv` - conservative positive/negative receiver evidence explicitly recoverable from published text.
- `blackman_extraction_manifest.json` and `SHA256SUMS.json`.

## Provenance rules

Direct table values are preserved separately from derived decimal coordinates/calendar timestamps. Empty cells mean “not recovered confidently,” not zero. Detection status is not inferred from silence.

One indexed Table 5 row is deliberately flagged `A3?`: the JD144 10:54:57.77 event is labelled A3 in the indexed text but its coordinates are essentially A4 and inconsistent with the separately tabulated A3 location. This must be checked against the original PDF page image before publication.

## Important limitation

This is a report-level calibration catalogue, not raw waveform data. Full array reprocessing, AGW/elastic precursor searches, inter-hydrophone coherence and matched filtering require the original H01/H08/H04 recordings from CTBTO/Scripps/LLNL.

Primary records:
- https://www.osti.gov/biblio/850576
- https://www.osti.gov/servlets/purl/850576
- https://digital.library.unt.edu/ark:/67531/metadc787884/
