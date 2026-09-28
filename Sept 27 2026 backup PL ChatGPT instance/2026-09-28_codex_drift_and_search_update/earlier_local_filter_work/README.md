# Reconstructed MH370 v12 with ERA5

This is newly written, executable reconstruction code, **not the recovered historical v12 source**. It uses the recovered project, archived v12 descriptions, and Davey et al. (2015). The original source and its exact particle states were unavailable. Historical validation claims are not treated as tests of this implementation.

The user authorized ERA5 instead of Davey's original weather. All code and inputs live locally, outside the read-only synced `sources/` folder. Every observation produces a weighted checkpoint and a restart checkpoint with all particle states and the random generator state. The runner refuses a restart if its code, input, configuration or weather hashes differ.

## Scientific scope

The Fig. 10.3 analogue concerns the **00:19 airborne latitude**, not the impact distribution. Davey's Table 10.1 includes the two final BTOs but excludes final BFO; this implementation does the same. There is no received-power/AES-gain likelihood, ocean-drift likelihood, search-exclusion likelihood or terminal descent/impact likelihood.

The baseline has five lateral modes (CMH, CTH, CMT, CTT and LNAV), Mach and altitude manoeuvres, a shared per-trajectory log-uniform 0.1–10 hour manoeuvre-time parameter, independent event clocks restarted after manoeuvre completion, and Davey's OU wind/Mach/angle fluctuations. Navigation uses WGS84 geodesics. Cruise steps are at most 10 seconds; manoeuvre steps are at most 1 second, with exact event boundaries. LNAV can switch once into true or magnetic heading; its six-hour switch probability is 0.5.

BFO has **7 Hz measurement SD**, a constant unknown bias with **25 Hz prior SD**, and analytic conditional Gaussian bias updates for every trajectory. Vertical velocity is omitted from BFO as in Davey's Chapter 6 treatment. BTO uses the full two-way satellite/Perth path and message-dependent delays and errors. Systematic resampling occurs below 50% particle ESS; it introduces no unmodelled jitter. This is ordinary sequential Monte Carlo with Rao–Blackwellized bias, not a claim that Davey's original proposal/branching implementation was recovered.

## Frozen inputs and acknowledged differences

* `inputs/mh370_davey_era5.json`: exact raw timestamps selected against Davey Table 10.1; its provenance records original workbook hashes, anomalous BTO corrections and channel classes. C-channel likelihoods use the selected individual records at 18:39:55 and 23:15:02, with 7 Hz noise, not a cluster mean with artificially reduced error.
* The 18:01:49 radar prior mean is reconstructed from earlier project notes: 5.624829°N, 99.048157°E and track 295.66°. This is not the unavailable exact smoothed radar state. Initial Mach is uniform 0.73–0.84. Initial altitude is uniformly selected from 25–43 kft in 1 kft steps (a disclosed reconstruction choice). Position SD is 0.5 arcminute per coordinate and angle SD 1°. The source's 0.5 NM and Table 8.2's 0.4 arcminute specifications are not identical.
* Public STK/SGP4 satellite geometry based on the March 9 TLE replaces the operator ephemeris / earlier project's reported March 7 geometry. Nominal channel-frequency constants are used. This limits exact numerical agreement with Davey.
* Full-path delays are the recovered v11 values −495679 µs for R1200 and −491079 µs for R600. BFO bias prior mean is the published 152.5 Hz. Neither is fitted to the unknown accident trajectory. The AFC/pilot-error reconstruction uses Ashton Fig. 11 through 23:15 and the ATSB −37.7 Hz value at 00:11. Final BFO is excluded.
* ERA5 wind **and temperature** are independently sampled at each simulated position, altitude and time. Public ARCO ERA5 source: `gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3`; documentation: https://github.com/google-research/arco-era5 . Hourly 0.25° source fields were retained on a 0.5° grid, latitudes −60…60°, longitudes 40…160°, 125–500 hPa. Pressure levels are mapped to ICAO pressure altitude; interpolation is linear in time, pressure altitude, latitude and longitude. Queries outside support raise an error; there is no calm-wind fallback. Hours 07–18 form an unqueried gap between validation and accident windows.
* WMM2010 magnetic declination is tabulated on a 1° grid at 10 km for March 2014; fixed altitude is an approximation. The retained independent interpolation check has RMS 0.0106° and maximum 0.122° error.

These differences mean **Davey-model/ERA5 analogue** is the appropriate label; an exact Fig. 10.3 reproduction is not established merely by a similar plot.

## Validation and interpretation

`test_core.py` checks OU stationary variance, analytic bias likelihoods, full-path BTO, a published BFO fixture, navigation wind triangles, preservation of joint states during resampling and bit-exact checkpoint restarts. Tests do not establish convergence or complete source fidelity.

MH371 calibration is frozen using 20 records from 03:29 through 03:59:01; subsequent SATCOM updates are withheld from calibration. Truth is used to score the outputs, not to steer their likelihoods. The ERA5 comparison against withheld ACARS gives RMS discrepancies of 4.23 kt north wind, 3.82 kt east wind and 0.95 K temperature. This is a weather cross-check, not a fitted weather correction.

The dense 100,000-particle ERA5 validation runs use seeds 101, 202 and 303. Their final truth HPD ranks with 25 km spatial smoothing are 0.494, 0.258 and 0.053, respectively; mass within 100 km is 0.875, 0.982 and 0.596. The final retained initial ancestors number 50, 36 and 47. The truth is retained, but run-to-run variability and limited ancestry prevent a strong convergence claim. HPD rank depends on the smoothing convention: see `assessment/mh371_validation.csv` for 10/25/50 km results. These ranks are not directly interchangeable with the historical implementation's ranks.

The 5,000-particle oracle-weather diagnostic loses the truth (final HPD rank 1); that illustrates depletion at small particle count. It is neither independent-weather validation nor evidence that the oracle itself is inaccurate. Dense known-flight tests do not replace the still-unperformed complete sparse-schedule validation suite.

Accident PDFs are computed directly from saved weighted particle coordinates, with a fixed 0.35° Gaussian display bandwidth. No fitted refined-mixture proposal enters these runs. Separate seeds are plotted, not hidden by averaging. Full latitude support is retained, including the northern BTO-only solution. `assessment/posterior_summary.json` records effective particle count, effective initial-ancestor count, dominant-ancestor weight, quantiles, southern probability and between-run distances. A high final particle ESS alone cannot show path diversity or convergence.

The optional comparison is at **00:11 for both curves**. The older refined output is the recovered no-drift summary reconstruction, which includes different upstream modelling and evidence. It is not the missing original checkpoint and is not a Davey-only posterior. See `BFO_AND_CHECKPOINT_NOTES.md`.

## Reproducible execution

The installed environment is `.venv` (Python 3.14); `requirements-lock.txt` freezes package versions. In a new environment install that file, then run from this directory:

```sh
python -m pytest -q test_core.py
python run_filter.py --particles 100000 --seed 101 --output runs/mh371_era5_100000_101
python run_filter.py --input inputs/mh370_davey_era5.json --particles 100000 --seed 101 --output runs/mh370_era5_100000_101_bto_bfo
python run_filter.py --input inputs/mh370_davey_era5.json --particles 100000 --seed 101 --bto-only --output runs/mh370_era5_100000_101_bto
python assess_validation.py
python plot_posteriors.py
```

Repeat with other seeds / larger particle counts and fresh output names. Existing outputs are protected: append `--resume` to restart the identical run. `--stop-after N` supports staged execution. The frozen inputs suffice to run without re-downloading ERA5 or regenerating satellite/magnetic data. Preparation scripts record their original external source paths; those paths are not required by the filter itself.

Each `weighted_NN.npz` contains state immediately after weighting and before possible resampling. `resume.npz` contains the restart state after resampling (except the final update, which is not resampled). Checkpoint metadata holds configuration, RNG state, observation index, time, diagnostic history and identity hashes. Observation 10 is 00:11 and observation 12 is 00:19 for MH370. Store these whole files: a latitude CSV is not a substitute for a complete checkpoint.
