# Nov 8 EOF output

End-of-flight (EoF) results for the Results section of the Journal of Navigation (JON) paper on MH370.
The folder is self-contained: every number, map and figure here can be rebuilt from the files in `data/` with the scripts in `code/`
and `descent-0019/data-and-code/`. Nothing outside this folder is read.

Built 9 November 2026 from the final end-of-flight run of 7 November 2026 and the ocean-settling energy-transfer sidecar of 8 November 2026.
Default route model: **Davey model with the fuel model** (Pete's ruling, 8 Nov 2026). The waypoint model is given where it differs.

## 1. What was asked
The requests are in `request/`, verbatim:
- `request/01-request-2026-11-08.md` - the original request (results summary, table, candidate JON graphics, six example attachments).
- `request/02-postscript-2026-11-08.md` - default to the Davey model with fuel; note where the waypoint model differs materially.
- `request/03-feedback-on-first-round-2026-11-09.md` - rejection of the first round; this folder is the response and the hand-over.

Pete's six example graphics are in `examples-from-pete/` (attachment 1 = 00:19 descent-rate chart; 2 = overlay map; 3 = small multiples;
4 = core map with wider latitude; 5 = peak-power dot maps; 6 = energy dot maps). They are examples, not mandates.

## 2. Rebuild
```
pip install numpy scipy pandas matplotlib pillow
python code/make_figures.py          # all 12 map/energy figures + results/eof-results-metrics-davey-fuel.csv (about 25 s)
python code/make_tables.py           # results/eof-results-summary-table.csv (adds waypoint-model areas)
python descent-0019/data-and-code/descent0019_charts.py   # the seven 00:19 descent-rate chart candidates
```
Fonts: Times New Roman (falls back to the matplotlib serif font if absent). `python code/make_figures.py overlay` builds only the figures whose name contains `overlay`.

## 3. Folder layout
| Path | Content |
|---|---|
| `data/` | Inputs (see section 5). |
| `code/eofmaps.py` | Library: loading, weights, 7th-arc frame, density, highest-probability regions, areas, searched-area coverage, Mercator map helpers. |
| `code/make_figures.py` | Builds figures eofn-01 to eofn-12 and the metrics table. Captions (JON) and footnotes (working) are defined in it. |
| `code/make_tables.py` | Builds the paper summary table. |
| `figures/` | For each figure `<name>`: `<name>-word.png` (JON graphic, 600 dpi, 127 mm wide, no title, no notes), `<name>.pdf` (vector), `<name>-proof.png` (graphic with its JON caption beneath), `<name>-caption.txt`, `<name>-working.png` (title and full footnote of data, parameters and assumptions). |
| `descent-0019/figures/` | The seven candidates for the 00:19 descent-rate chart (attachment 1), same five files each. |
| `descent-0019/data-and-code/` | Data and script for those charts; its own README defines every column. |
| `descent-0019/descent-0019-candidates-JON-proofs.pdf` | Booklet of the seven descent-chart proofs. |
| `eof-results-candidates-JON-proofs.pdf` | Booklet of all 19 candidates (12 map/energy figures + 7 descent charts) with a contents page. |
| `results/` | Computed tables (section 7). |

## 4. Treatments of the 00:19 satellite data
All treatments re-weight the **same** 501,102 simulated impact rows (16 seeds) by the likelihood of the data each uses.
Effective sample size (ESS) must be taken from `data/eof-treatments.csv` (column `ess`), not from the hand-off weights, because the hand-off rows were thinned.
Rule (project): treatments with ESS below 1,000 are not mapped; ln B is compared only between treatments that use the same data (both BTOs and both BFOs: D9, D10, D14, D11, D12).

| Code | Paper wording | ESS (Davey + fuel) | Median latitude |
|---|---|---|---|
| D13 | No 00:19 data used (nothing after 00:11) | 2,032,841 | 36.59 S |
| D0 | Log-on event only | 328,957 | 36.42 S |
| D7 | BTO only (both 00:19 BTOs) | 499,760 | 36.82 S |
| D8 | BTO and 00:19:29 BFO (R600) as observed; replicates the 18:25 log-on | 22,056 | 36.73 S |
| D9 | BTO and both BFOs as observed (provisional; not mapped) | 508 | 36.56 S |
| D10 | BTO and both BFOs, Holland transient bias added (17 Hz floor) | 3,347 | 36.51 S |
| D14 | As D10, zero floor | 4,056 | 36.52 S |
| D11 | BTO and both BFOs, Holland transient bias added to the 00:19:37 BFO only (17 Hz floor) | 1,357 | 36.64 S |
| D12 | As D11, zero floor | 1,815 | 36.64 S |

D1-D6 in `eof-treatments.csv` are sensitivities that use the 00:19:29 BTO only; they are not used in the figures.

Measurement values: 00:19:29 R600 BTO 18,400 µs (sd 63 µs); 00:19:37 R1200 BTO 18,380 µs with the empirical offset applied (sd 43 µs);
BFO 182 Hz (00:19:29, R600) and −2 Hz (00:19:37, R1200), sd 4.32 Hz. Holland transient bias added: 17–136 Hz on 00:19:29 and 17–130 Hz on 00:19:37.
R600 and R1200 are the 600 and 1200 bit/s channels.
"Outer limit of the bias treatments" in the figures = union of the highest-probability regions of D10, D14, D11 and D12 at the stated level (D9 excluded by the ESS rule).

## 5. Data files (`data/`)
| File | Content |
|---|---|
| `eof-handoff-davey-fuel.npz` / `.json` | 501,102 impact rows, Davey model with fuel. Columns and codes in the `.json`: `latitude_deg`, `longitude_deg`, `arc_distance_nm_signed` (distance from the 7th arc, positive to the south-east), `impact_s_after_001929`, `kinetic_energy_j`, `vertical_speed_001929_fpm`, `vertical_speed_001937_fpm`, `family_code` (1 no pilot after fuel exhaustion, 2 piloted, 3 planned descent), `electrical_configuration_code`, `seed`, and `log_weight_<code>` for each treatment. Weight: w = exp(log_weight − max), normalised to sum 1. |
| `eof-handoff-waypoints.npz` / `.json` | The same for the waypoint model. |
| `settling-energy-transfer-davey-fuel.npz` / `.json` (and `-waypoints`) | Row-aligned sidecar (`row_index` = hand-off row). `energy_transfer_peak_rate_w` = **peak impact power** (W), the peak mechanical rate of energy transfer to the water. October charts called it "peak radiated power"; it is not radiated acoustic power. Not yet independently checked. |
| `eof-treatments.csv` | Run table, both route models: ln Z, ESS, family shares, latitude and arc-distance quantiles, within 10/25/50 NM, time to impact, kinetic energy quantiles, 90 % seed intervals. |
| `eof-variants.csv`, `eof-run-specification.json`, `eof-run-report-2026-11-07.md` | Variant runs, the run specification and the run report. |
| `bfo-0019-frequency-evidence.csv` | ln Z and posterior probabilities of the BFO treatments; ln B with 90 % seed intervals. |
| `bfo-1825-treatment-test.csv` | Each BFO treatment applied to the 18:25 log-on. |
| `arc7-001929-sea-level.csv`, `arc6-001059-35000ft.csv` | 7th arc (00:19:29, sea level) and 6th arc (00:10:59, 35,000 ft) as latitude/longitude points. |
| `searched-area-coverage-0p01deg.npz` | Previously searched area on a 0.01° grid: `atsb_phase2_percent`, `ocean_infinity_2018_percent`, `ocean_infinity_2025_26_percent`, `union_percent` (uint8, percent of the cell covered), `south_edge_deg` (−40.2), `west_edge_deg` (85), `step_deg`. Row 0 is the south edge. Ocean Infinity 2025–26 is inferred from vessel tracks (grade C). Coverage only, no detection probability. |

Source wording inside some data files is older than the paper wording: "as recorded" = **as observed**; "Holland offset"/"start-up offset" = **Holland transient bias added**; "timings" = **BTO**; "frequencies" = **BFO**. Use the paper wording.

## 6. Methods used for maps and areas
- Probability density: weighted histogram in a frame aligned with the 7th arc (5 NM along × 2 NM across), smoothed with a Gaussian kernel of 12 NM along and 3 NM across, then sampled to a 0.025° latitude/longitude grid (−45 to −20, 84 to 108). The grid holds at least 99 % of the probability for every treatment.
- Highest-probability regions: smallest set of grid cells holding the stated share. Areas: sum of the cell areas, each (1.5 NM)² × cos(latitude) with 1 NM = 1 minute of arc, converted at 1.852 km/NM. The density is normalised over the grid.
- Distance from the arc: the hand-off column `arc_distance_nm_signed` for tables; the maps use the library's spherical nearest-point frame (differs by about 1.5 % at 100 NM, under 0.4 NM within 25 NM).
- Inside the previously searched area: Σ w × coverage fraction of the cell (coverage only).
- Maps: Mercator projection; graticule 2° major and 0.5° minor (4° and 1° in overview panels); 7th arc solid, 6th arc dash-dot.
- Previously searched area drawn as one hatched outline at half coverage, after removing gaps and strips narrower than about 3 km (area change −0.07 %).
- Energy dot maps: systematic resample of 3,000 rows per treatment. Energy classes under 1, 1–4 and at least 4 GJ. Peak-power classes at the weighted 50th and 90th percentiles under BTO only (0.5 and 54 GW).

## 7. Results (`results/`)
- `eof-results-summary-table.csv` - the paper summary table (below).
- `eof-results-metrics-davey-fuel.csv` - all treatments: ESS, ln B, latitude 5/50/95 %, areas of the 50/90/95/99 % regions, distance quantiles, within 25 NM, inside the previously searched area, time to impact, energy quantiles, share at 4 GJ or more, peak power median, no-pilot share.
- `area90-km2-waypoint-model.json` - 90 % region areas for the waypoint model.
- `eof-high-energy-share-by-region.json` - share of impacts at 4 GJ or more inside the 50 % region, between 50 % and 95 %, and outside 95 % (D7, D8, D10).

| Treatment of the 00:19 data | Effective samples | ln B against both BFOs as observed (90 % seed interval) | Median impact latitude (°S) | Median impact latitude, waypoint model (°S) | 90 % region area (km²) | 90 % region area, waypoint model (km²) | Within 25 NM of the 7th arc (%) | 95th percentile distance from the 7th arc (NM) | Median time from 00:19:29 to impact (min) | Median impact kinetic energy (GJ) | Inside the previously searched area (coverage only, %) | Mapped |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| No 00:19 data used | 2,032,841 | not compared (different data) | 36.6 | 36.8 | 418,000 | 328,000 | 45 | 139 | 17.9 | 1.2 | 56 | yes |
| BTO only | 499,760 | not compared (different data) | 36.8 | 37.0 | 162,000 | 100,000 | 73 | 69 | 17.2 | 1.1 | 83 | yes |
| BTO and 00:19:29 BFO (R600) as observed | 22,056 | not compared (different data) | 36.7 | 37.0 | 104,000 | 56,000 | 87 | 43 | 15.8 | 1.2 | 93 | yes |
| BTO and both BFOs as observed | 508 | 0 (reference) | 36.6 | 37.2 | 74,000 | 49,000 | 88 | 38 | 1.7 | 9.2 | 95 | no (effective samples below 1,000) |
| BTO and both BFOs, Holland transient bias added | 3,347 | +0.31 (+0.18 to +0.46) | 36.5 | 37.2 | 62,000 | 40,000 | 93 | 31 | 1.8 | 9.2 | 98 | yes |
| BTO and both BFOs, Holland transient bias added to the 00:19:37 BFO only | 1,357 | −0.43 (−0.60 to −0.27) | 36.6 | 37.2 | 72,000 | 45,000 | 90 | 34 | 1.4 | 9.2 | 97 | yes |

## 8. Caveats
- BTO and both BFOs as observed (D9) has 508 effective samples: provisional, not mapped. D11 has 1,357 (489 in the no-pilot family).
- All ln B values are below 1 nat: the evidence does not choose between the BFO treatments.
- Impact kinetic energy is a sensitivity result: the no-pilot dives reach about Mach 1.0, and the median under both BFOs (about 9.2 GJ) is at or above the top of the Boeing 777 simulation range (6.4–9.0 GJ).
- Peak impact power is a mechanical rate from the settling module (method 1); not yet independently checked.
- The 7 November maps (window 30.5–43 S, 84–98 E) dropped 3.9–6.3 % of the probability; their areas are superseded by the areas here.

## 9. Wording and figure rules for the paper
- JON figures: greyscale; 127 mm wide; serif (Times) at 8 pt or more; no title, notes or footnotes on the image; panel labels are letters only, "(a)"; all description in the caption beneath. Tables: caption above. Line art 1200 dpi, combination 800 dpi, halftone at least 300 dpi (JON instructions). Colour must not carry meaning.
- Terms: BTO, BFO; "as observed"; "Holland transient bias added" (never "correction"); "previously searched area"; "empirical offset applied" for the 00:19:37 BTO (never "corrected"); x_Impact with an upright full-word subscript; "AirAsia 8501"; "Boeing 777 simulations"; ICAO terms where they apply. No internal codes (D7, D10 ...) on any image.
