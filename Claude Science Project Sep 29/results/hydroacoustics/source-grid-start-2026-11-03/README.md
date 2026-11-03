# Source-grid method: first products (3 Nov 2026)

Session d1ea5f58. Proposal X18, approved by Pete on 3 Nov 2026 (P73, P74). Exploratory; unchecked; no independent verifier yet.
ASD-STE100 for work-specific text.

## 1. What is in this folder
| File | Content |
|---|---|
| corner-frequency-explained.png | What the corner frequency is, and how much energy it puts in the 5-40 Hz band. |
| source-depth-and-sound-channel.png | Sound speed on the arc in March; the ray cone that clears the seabed; illustrative source depths by impact type. |
| value-of-information-test.png, value-of-information-test.csv, value-of-information-impact-time.csv, voi_v2.py | Value-of-information test, second version. |
| calibration-sources-and-data.md / .csv | All known sources and data held for the sound model, with test status. |
| path-sections-index.csv | 154 path sections: 84 known-source paths and 70 sparse arc paths, with path class. |
| profiles-*.png | Seafloor sections for every known-source path and every sparse arc path. |
| arc_ssp.json | Sound-speed profiles at the arc points 20, 25, 30, 35, 40 S (WOA23 2005-2014, March). |
| ram_timing.json, ram_band_test.json | Measured cost of the coupled sound model (RAM) on one arc path. |
| build_sections_now.py, arc_ssp.py, ram_timing.py, ram_band_test.py | Code. It uses the frozen chain tl-chain-2026-10-27 (artifact 9ba75304) unchanged. |

## 2. Results
1. Corner frequency. For a fixed acoustic energy, the share of energy in 5-40 Hz falls by about 21 dB for each tenfold drop of the corner (spectrum above the corner as frequency to the power -3.1). Corner 5 Hz: -5 dB; 1 Hz: -20 dB; 0.2 Hz: -34 dB.
2. Source depth. In March the surface sound speed on the arc (1,507-1,538 m/s) is close to the seabed sound speed. A source in the top 100 m has a ray cone of only 0-5 degrees that clears the seabed; at 30 S the cone is zero. For sources shallower than about 30 m the received level follows the force of the impact, not the depth (RAM check on one path: loss falls by 13.8-14.0 dB from 2 m to 10 m and 8.2-9.5 dB from 10 m to 30 m (single frequencies 5-40 Hz and two full band averages), as 20 log10 of the depth ratio).
3. Value of information (flat prior along the arc). One arrival time: 0.01-1.2 bits (depends on the impact-time error). One array direction: 3.6-4.7 bits. Cape Leeuwin + SSEIR, times only: 5.1 bits, and it does not depend on the impact time. All eight sites: 7.6-7.9 bits. The test does not include detection probability.
4. Path classes. 7th arc (70 sparse paths): clear 10, ridge near the axis 38, ridge above the axis 15, blocked 7. Known sources (84): clear 9, near axis 27, above axis 33, blocked 15. The frozen chain's classifier marks every path COUPLED, so it does not separate the paths.
5. Compute. One RAM frequency on the 1,953 km path takes 1.4 s (5 Hz) to 7.0 s (40 Hz). Full band average (25 or 15 frequencies): sparse set 63 paths, 16.6 CPU-h, about 1.5 h at 12 threads. Five frequencies per band changed the band loss by 0.04-0.54 dB on this path; three frequencies by up to 1.7 dB.

## 3. Limits
- Corner and depth ranges for the 777 are illustrative. No airliner-scale water-entry sound has been measured.
- The value-of-information test has no level term and no non-detection term.
- The RAM timing is one path on the Mac; deskstar speed is not measured.
