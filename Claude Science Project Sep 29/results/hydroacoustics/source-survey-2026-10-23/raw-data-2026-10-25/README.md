# Raw IMS hydrophone analyses, 25 October 2026 (session c764a583)

Four exploratory analyses on raw IMS hydrophone records (EarthScope FDSN, network IM, channel EDH, StationXML response removed to Pa).
Each analysis has a protocol written before computation. Nothing here is a likelihood. Nothing here changes the end-of-flight posterior.

| folder | what it does | note |
|---|---|---|
| `f35a-raw-ridge/` | F-35A (Misawa, 9 Apr 2019) at Wake (H11N, H11S): raw against digitised levels, the 20 Hz gap, the source spectrum, the coupling ridge (D1, KRAKEN+RAM), the Arons (D2) value, back-azimuth | `f35a-raw-ridge-note.md` |
| `transair-810/` | Transair 810 ditching (2 Jul 2021): detection test in the predicted window, check of Kadri's boxed signal, upper limit on ditching coupling (R3) | `transair810-note.md` |
| `kadri-2024-replication/` | Kadri 2024 (Sci. Rep. 14:10102) panels against raw data; timing and bearing against the crash sites (comparison set, not excluded) | `kadri-replication-note.md` |
| `propagation-level-check/` | ARA San Juan charge and event, and FSST 2016/2021 shots at Ascension (H10N, H10S): absolute level and frequency slope of the propagation chain, sigma_model, real-arrival test of the M1b detector | `propagation-level-check-note.md` |
| `db-rows-merged/` | all new database rows in one import set with unique ids (see below) | `merge_wave3_rows.py`, `id-map.csv` |
| `independent-verification/` | independent recomputation of 12 headline numbers | `wave3-verifier-report.md` |

## Independent verification (clean-up rule: verifier before CURRENT)
A separate agent recomputed 12 headline items from the raw data with its own code. It opened the track scripts only after it had its own number, and only to diagnose a difference.
Result: **9 AGREE, 3 MINOR, 0 DISAGREE, 0 NOT VERIFIED.**

- MINOR F2: the 20 Hz notch is −12.56 to −7.19 dB; the track gives −12.0 to −7.2 dB. It is "present" at 6 of 6 elements in both.
- MINOR K1: the offsets of the Kadri-boxed bursts from the water-path centre depend on route length (see erratum 2).
- MINOR P2: the median effective window is 47.9 s; the track gives 49.6 s. The conclusion of about 7 dB holds.

The verifier did not recompute these items, and they stay as the tracks report them:
- the module M1b p-values for Transair 810 (0.079, 0.095);
- the KRAKEN and RAM runs (F4 is arithmetic from the track's transmission-loss table);
- the 'measured' flags for the background-window spread.

## Errata found by the verifier (the notes are not edited; these corrections apply)
1. **Spectral form wording.** The coupling rows said "one-pole f^-2". The module form is flat to 1/tau, then f^-2 above, normalised over 1–500 Hz (`band_fraction`). A true one-pole form 1/(1+(f/fc)^2) gives coupling 3.4 % lower (2.315e-3 against 2.396e-3 at 10 m). The 31 affected cells in `db-rows-merged/db_coupling_value_wave3.csv` now use the correct wording; the values are unchanged.
2. **Route lengths in the Kadri replication.** `water_route.py` sums 8-neighbour grid steps without smoothing. This makes the routes 1–4 % too long. The reported offsets are therefore too negative by about 26 s (Sriwijaya 182: about −716 s, not −742 s) and about 84 s (AB Aviation 1103: about −1,510 s, not −1,594 s). The conclusions do not change.
3. **AB Aviation 1103 expected bearing.** The reconciliation table gives 254.56° from Kadri's S1 position. The published crash location gives 258.40°, close to Kadri's Fig. 2 value of 258.47°. No result changes, because the burst has no coherent bearing.
4. **F-35A triad values.** The triad exposures (0.284 and 0.0955 Pa² s) are the linear mean of three elements, as pre-registered, not the median. The 1-s RMS peak ranges 0.31–0.38 and 0.20–0.27 Pa are 4–40 Hz values. In 4–64 Hz they are 0.333–0.394 and 0.211–0.291 Pa.
5. **H10S1 at the San Juan charge.** The H10S1 value is a noise maximum, not an arrival. The −27 dB figure is therefore a lower bound on the H10S1 deficit. The event value (−31.9 dB) is a true arrival comparison.
6. **P2 wording.** The implied window in the propagation note (section 3) is raw energy spectral density divided by Nielsen's digitised PSD. It is not a raw Welch PSD against raw energy. A raw 60-s Welch PSD gives 24.5–75.5 s, depending on segment length.
7. **Transair 810 pulse lag.** The H11N−H11S lag is 73.3 s and 71.5 s for the two pulses; the note gives 72–73 s.

## Database rows (for the data-inventory thread)
The three tracks numbered their new rows from CV26 and OB07, so the ids collided. `db-rows-merged/merge_wave3_rows.py` gives each row a unique id after the base package (CV01–CV25, OB01–OB06). Each row keeps its track id in `track_local_id`, and the mapping is in `id-map.csv`.
- Coupling values CV26–CV123 (98 rows). In merge order:
  - propagation check CV26–CV31 (D2, group G4);
  - Transair 810 CV32–CV41 (D1 upper limits, group G9);
  - F-35A raw ridge CV42–CV123 (64 D1, 14 D4, 4 D2, group G1).
- Received observations OB07–OB81 (75 rows).
- Other new or updated rows:
  - new evidence row E18 (Transair 810);
  - update of impact case AC05, with its CV references remapped;
  - update of family element R3 eta_rad;
  - 6 data-availability probes.
- The radiated fractions of the explosions are not written as coupling rows. The `v_module_chain` view would mix them with impact values, so that is a decision for the importer.
- Validator (`validate_coupling_tables.py` of the 25 Oct package) on the base package plus all rows above: **PASS (0 failures)**. Views: v_module_chain 100, v_arons_screen 13, v_envelope 4, v_cross_check 1 (`db-rows-merged/validator_output.txt`).

## Data and paths
- Raw waveforms (about 40 MB F-35A, 66 MB H10 2016–2021, plus Transair and Kadri windows) are not committed. The download scripts in each folder fetch them again from EarthScope, without credentials.
- The Atlantic path sections (27 MB) are not committed either; `propagation-level-check/scripts/s03_paths.py` rebuilds them.
- Scripts read local inputs through environment variables:
  - `MH370_OCEAN_DATA`: GEBCO_2026, WOA23 and the ocean-transport exports;
  - `MH370_EXCHANGE`: the module exchange directory, for the M1b templates;
  - `MH370_HYDRO_ENV_LIB`: the conda library path for KRAKEN and pyram.
- Kadri's published figures (Sci. Rep. 14:10102, doi 10.1038/s41598-024-60529-1) were used for digitisation but are not committed; cite the DOI.

## Standing caveats
1. **Frequency-slope failure.** The propagation model failed the 2001 airgun check (+10 dB/octave at H01W, +7 at H08S). The propagation check finds the chain's slope within ±3 dB/octave on 17 explosion–station pairs at Ascension, and attributes the airgun misfit to the airgun source term. That revised caveat wording waits for Pete.
2. **Detection probability.** It is a proxy unless measured on real data. The detector finds the real San Juan arrival at the p floor, but at 16–24 dB SNR it separates weakly from background windows (gap G11-1).
3. **Kadri 2024.** These results do not show that Kadri erred. "Not consistent with the crash site under our path model" lists possible causes on both sides.
