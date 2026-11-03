# Dense sound-model grid, 7th arc 41–20 S (3 November 2026)

Part of the source-grid hydroacoustics method (proposal X18, decisions P73–P74). Pete approved an overnight run on the Mac.

## What was run
- 43 arc points, every 0.5 degrees from 41.0 to 20.0 S, on the 7th-arc line of the run J searched-area grid (arc-grid.npz).
- 14 listening stations: Cape Leeuwin and Diego Garcia South (IMS arrays); IMOS loggers 3315 and 3376 (Perth Canyon), 3250 (Scott Reef), 3274 and 3275 (Portland); OHASISBIO SWAMS1–3, SSEIR, MAD, NCRO and WKER.
- 602 paths. 48 cross land and were not run, which leaves 554.
- Sound model: RAM (pyram 1.3.0) parabolic equation, run in reverse from each station. Frozen chain tl-chain-2026-10-27, layered seabed (GlobSed v3 sediment), GEBCO 2026 seabed depth, WOA23 March sound speed.
- 10 one-third-octave bands, 5–40 Hz, with 7 frequencies in each band. Outputs at source depths 2, 5, 10, 30, 100, 300 and 1,000 m.
- 38,780 frequency runs. 3,968 were reused from the sparse run (same section and same frequency). No errors.
- Wall time 5 h 45 min with 14 processes and one thread per worker. Other programs on the Mac held the load at about 20–85.

## Checks
- Where the dense and sparse runs overlap (loss below 140 dB), dense (7 frequencies) minus sparse (25 or 15 frequencies) is +0.17 dB on average, sd 1.15 dB, with 95 % of cases within 2.35 dB.
- Band sampling sd (three interleaved subsets): median 2.3 dB, 95th percentile 5.3 dB.
- Fix made before the run: importing build_sections_now.py had blanked the GlobSed sediment lookup. The lookup was restored and the sections were rebuilt. All 554 water paths have full sediment coverage.

## Results (10 m source, median over the 10 bands)
| Station | least loss, dB | median, dB | most loss, dB |
|---|---|---|---|
| Cape Leeuwin | 123.9 | 134.1 | 143.1 |
| Perth Canyon 3315 | 124.8 | 138.2 | 146.7 |
| Diego Garcia South | 124.7 | 140.1 | 149.9 |
| OHASISBIO south-east ridge | 115.2 | 144.1 | 172.0 |

All stations are in station-loss-summary.csv.

- Over all 14 stations, Cape Leeuwin has the least loss at 19 of the 43 arc points and a Perth Canyon logger at 18.
- Scott Reef is blocked from every arc point. Portland is blocked by land north of 28.5 S.
- The OHASISBIO paths lose 10–30 dB more north of about 31 S, where they cross ridges.
- **Raised seabed under the source:** at 32.0 S (Broken Ridge flank, seabed 1,035 m, falling to 2,326 m within 5 km) and at 22.0 S (seabed 2,516 m among points at about 5,000 m), the loss is 16 dB and 9.7 dB lower than at the points beside them, at 12 and 9 of the 14 stations. A shallow source over a steep slope couples into the deep sound channel. This is local, and the 0.5-degree spacing does not resolve it. Per-point values are in arc-point-seabed-and-loss.csv.

## Caveats
- The model's bias is not yet removed. On deep Indian Ocean known-source paths it lost 5 to 14 dB too much.
- Losses above about 200 dB are blocked-path floor values (up to 607 dB at Scott Reef). Treat them as "no signal".
- One section per path along the 7th-arc line. Cross-arc offsets are not sampled.

## Files
tl_dense_bands.csv (path, band centre, source depth, loss, band sd, number of frequencies, range, station, source position, receiver depth), paths.csv, arc-point-seabed-and-loss.csv, station-loss-summary.csv, dense-sound-model-results.png, scripts make_jobs.py, launch_dense.py, assemble_dense.py, plot_dense.py.
