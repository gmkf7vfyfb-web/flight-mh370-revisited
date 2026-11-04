# Reverse-sensing methods, 4 November 2026

This folder fixes the reverse-sensing hydroacoustic methods BEFORE any arrival window is opened. Propagation is used for travel time only.

| File | What it holds |
|---|---|
| reverse-methods-specification-2026-11-04.md | Pre-registered specification. It covers 8 single-station detectors (S1-S8, including Pete's energy, persistence, combined and shot-population tests), the cross-station time-slide coincidence (B1) and 4 further reverse methods (C1-C4). For each method it gives the statistic, parameters, data forms, null, p-values, look-elsewhere, known-event handling and the injection-test design. |
| literature/reverse-methods-literature-note-2026-11-04.md | Literature note: the MH370 hydroacoustic work, analogue sources, and detection below the noise in seismology, radar, sonar, GNSS and gravitational-wave work. |
| literature/reverse-methods-references.bib, .csv | 91 references: 87 with a DOI checked against CrossRef or doi.org on 4 Nov 2026, and 4 grey-literature items held by the project. |
| reverse_detectors.py | Reference implementation, version 1.0.0 (numpy, scipy; pyproj optional for geodesics). |
| tests/test_reverse_detectors.py | 25 unit tests on synthetic data. Run with `python -m pytest -q tests`. |
| synthetic_calibration.py, synthetic_calibration.json | Reproduces the synthetic calibration and sensitivity numbers quoted in the specification. |

Main design decisions, with their reasons:
1. **Plot vertices.** The Kadri plot vertices are signed and alternate between the top and bottom of the trace. They are converted to an envelope before any persistence statistic is computed.
2. **Persistence thinning.** The persistence test thins samples to the lag where the null autocorrelation falls below 0.1. On synthetic data the false-alarm rate at a nominal 0.05 is 0.22 without thinning, 0.11 with thinning at the 1/e lag and 0.049 with thinning at the 0.1 lag.
3. **Shot-population p-value.** The shot-population test takes its global p from Monte Carlo pseudo-populations built from the record itself. Parametric tails were anti-conservative on synthetic shot populations.
4. **Network combination.** Stations are combined by non-coherent integration and time slides, not by waveform cross-correlation, because envelopes on different paths are not phase-coherent.
5. **Synthetic sensitivity.** On synthetic envelope noise, the combined test and the cumulative-sum onset test reach about 3 dB lower SNR than energy alone. The values for the real data come from the injection tests in section 11 of the specification.
