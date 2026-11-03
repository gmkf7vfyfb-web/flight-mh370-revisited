# Sparse sound-model run on the 7th arc (3 Nov 2026)

Session d1ea5f58, proposal X18 step 3 (approved by Pete 3 Nov 2026). Exploratory; unchecked; no independent verifier yet. ASD-STE100.

## What was run
- 64 paths: arc points 20, 25, 30, 35, 40 S (offset 0, run J arc-distance field) to 14 receivers. Six paths cross land and were not run (Portland at 20 and 25 S; Scott Reef at 35 and 40 S). The section index is in source-grid-start-2026-11-03.
- Frozen sound model tl-chain-2026-10-27, unchanged: RAM, reciprocal runs from the hydrophone, seabed L1 (GlobSed v3 sediment over basement), WOA23 2005-2014 March, GEBCO_2026.
- 10 third-octave bands 5-40 Hz; 25 frequencies per band up to 25 Hz, 15 above. Source depths read at the arc end: 2, 5, 10, 30, 100, 300, 1000 m.
- 14,720 single-frequency runs, 0 errors, 2 h 22 min on 12 processes (Mac, heavy lock).

## Results
1. Loss with a 10 m source, median of the 10 bands: Cape Leeuwin 127-140 dB; Diego Garcia South 133-145 dB; Perth Canyon 130-148 dB; Portland 138-147 dB; OHASISBIO 134-138 dB at 40 S, 150-167 dB north of 30 S (ridge paths); Scott Reef above 170 dB (blocked).
2. The loss falls with source depth as 20 log10 of the depth ratio down to about 30 m (the dipole rule), then more slowly.
3. Fewer frequencies per band (paths with loss < 140 dB): 7 frequencies give a random error of 1.1 dB (1 sd), 95 % within 2.2 dB; 5 frequencies give 1.5 dB and 2.9 dB.
4. Measured throughput: 16.8 CPU-h of single-run work in 2.37 h, so 12 processes do the work of about 7 single runs.

## Limits
- Model bias is not removed. On deep Indian Ocean known-source paths this model was too lossy by about 5-14 dB.
- Offset 0 only. No cross-arc points yet.

## Files
tl_sparse_bands.csv (band loss per path, band, source depth, with band sampling SD); per_frequency_runs.jsonl.gz (every single-frequency intensity); subsample_error.csv; paths.csv; sparse-sound-model-results.png; make_jobs.py, launch.py, assemble_sparse.py; run.log.
