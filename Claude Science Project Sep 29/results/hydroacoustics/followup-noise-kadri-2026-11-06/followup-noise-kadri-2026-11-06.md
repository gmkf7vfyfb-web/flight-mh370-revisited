# Follow-up: station spectra, noise distribution, catalogue tail removal, Kadri-seeded windows (6 Nov 2026)

No 8 March 2014 signal values were read. The Kadri check uses only times, bearings, path classes and data coverage.

## 1. Why the gallery dive looks different at the two stations
The two gallery dives are different random draws (q1.py replay): Cape Leeuwin case corner 1.05 Hz, slope 3.63,
range 1,623 km; Diego Garcia South case corner 11.67 Hz, slope 2.03, range 4,493 km. The injection test drew the range
at random (1,500-4,500 km) for both stations, so it does not model station-specific paths.
Median noise (dB re 1 uPa^2/Hz at 5/10/20/40 Hz): Cape Leeuwin 83.1/85.1/86.9/79.6; Diego Garcia South 82.8/79.8/78.9/75.9.
Real arc distances: Cape Leeuwin 1,470-2,968 km; Diego Garcia South 3,554-3,893 km. Extra absorption over 1,500 km is
0.02 dB at 10 Hz, 0.29 dB at 40 Hz and 0.65 dB at 60 Hz (Thorp), so path length alone changes the received shape very little.

## 2. Noise distribution (noise_distribution_fit.csv)
30 s band energy, 5-40 Hz, over the 10 min running median, random records 2015-2025 (11,278 / 14,142 windows):
core Gaussian in dB, sd 0.355 / 0.342 dB (stationary Gaussian theory 0.132 dB); 8.1 % / 6.9 % of windows beyond
core + 3 sd (Gaussian 0.13 %); 99th percentile 5.3 / 5.0 dB; 99.9th 13.0 / 15.6 dB; maximum 23.1 / 30.5 dB.
Generalised Pareto above the 95th percentile (1.69 / 1.38 dB): shape 0.186 / 0.451, scale 1.95 / 1.49 dB.
Sample kurtosis in 30 s windows (5-40 Hz): median 3.03 / 3.05 (Gaussian 3.0); 95th percentile 3.8 / 5.5; 99th 7.0 / 10.6.

## 3. Tail removal by the USGS catalogue (tail_removal_by_catalogue.csv)
USGS events M>=3.5 within 70 deg, 2015-2025 (93,182 / 57,715). Sound window per event: distance/1.52 km/s - 30 s to
distance/1.45 km/s + 180 s. No path blocking applied. Values are Cape Leeuwin / Diego Garcia South, M>=3.5:
time flagged 11.1 % / 8.7 %; flagged share of the top 5 % band-energy looks 23 % / 19 %, top 1 % 24 % / 32 %, top 0.2 % 60 % / 40 %.
Thresholds before -> after removing flagged looks: band energy 99.8 % 19.2 -> 16.7 dB / 22.4 -> 19.8 dB;
correlation with the impact pattern 99 % 49.3 -> 35.7 / 34.1 -> 31.2; combined 99 % 57.4 -> 44.1 / 35.6 -> 34.8.

## 4. Kadri Table 1 transients seeded onto the arc (kadri_seeded_windows.csv)
Bearing within +-3 deg of the grid bearing from Cape Leeuwin; speeds 1.45-1.52 km/s; ruled impact window 00:19:38-00:29:44.
6 of 19 transients give an impact time inside the window (00:39:02, 00:40:34, 00:41:43, 00:45:36, 00:49:58, 00:53:31);
2 bearings miss the arc grid (343.16, 234.67 deg); 11 give impact times outside the window. The main candidate 00:54:30
(306.18 deg, arc 25-26 S) implies impact 00:34:55-00:38:07; the grid's latest Cape Leeuwin arrival for 25-26 S is
00:48:24-00:51:01, and an impact by 00:29:44 would need 1.0-1.15 km/s. Predicted windows and data held at the other sites
are in the table (Diego Garcia South Kadri envelope, IMOS loggers raw; Scott Reef 3250 blocked from all these points).
