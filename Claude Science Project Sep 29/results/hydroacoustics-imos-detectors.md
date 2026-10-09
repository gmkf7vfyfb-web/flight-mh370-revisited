# Hydroacoustics items 2b and 2c: detectors on the IMOS raw data, the positive controls, Kadri at Perth Canyon - PROVISIONAL

**Pre-registered** at `02bb8d0` (`prepare/imos_detectors.py`). Run at `hypothesis/hydroacoustics` HEAD;
outputs are in `results-data/imos2b/`. Noise, clock and coverage come from item 1d
(`hydroacoustics-imos-noise.md`).

**Detectors** (scored by `imos_detectors.py`):
- **D1, energy ratio** at 5–40 Hz: STA 2 s over the preceding 30 s LTA.
- **D2, band-power exceedance:** 5–20 Hz and 10–40 Hz levels over the background median, 3 s mean.
- **D3, two-site coincidence.**
- **p-values:** from the empirical window-max null of each logger's background recordings, leaving out
  the tested recording.
- **No array bearing is possible on IMOS.** Each logger is a single hydrophone, and the paired loggers
  record in alternating, non-overlapping 5 min slots.

## 1. Positive controls (item 2c, IMOS only): PASS

| control | logger | published arrival | D1 p | D2 p | SNR, dB |
|---|---|---|---|---|---|
| C1 Curtin event (CMST 2014-30 p. 6) | 3315 RCS | 01:33:44 | **0.003** | **0.003** | 14.5 |
| C2 (CMST p. 15) | 3315 RCS | 05:03:01 | **<1/n** | **<1/n** | 19.2 |
| C3, "much lower amplitude" (p. 15) | 3315 RCS | 05:18:13 | **0.015** | 0.108 | 7.9 |
| C4 Curtin event (Scott Reef note p. 1) | 3250 | 01:32:49 | **0.030** | 0.248 | 13.0 |

- **D1 detected all four, at SNR 7.9–19.2 dB.** D2 detected two; it misses the faint RCS event and loses
  Scott Reef's event in that site's impulsive noise.
- **Exploratory:** the arrivals precede 3376's recordings, and their tails were not detected there.
- **No P_D-versus-SNR curve is possible from four events.** Item 3's injections provide it. The IMS
  Blackman raw waveforms are not held, so 2c is IMOS-only.

## 2. MH370 windows: **no detection**, and the test's limit stated plainly

- **Coverage:** 11 recordings overlap the predicted windows on 5 loggers. With every logger considered,
  the stand-in arrival falls inside a D1-scorable stretch with probability **0.94**; Perth Canyon alone,
  its two loggers interleaved, gives **0.77**.
- **Result:** no window reaches the pre-registered Bonferroni level, p < 0.005. The closest is 3376 at
  00:39:15–00:39:28 (D2 p = 0.0054, SNR 11.3 dB), in the early tail of that window. Upper limits, the
  maximum 1 s 5–40 Hz SPL, are 101–109 dB re 1 µPa at Perth Canyon and Portland, and 120–122 dB at Scott
  Reef, where local impulsive noise dominates.
- **Limitation, not anticipated at pre-registration.** For a window as long as a whole recording, the
  null has one value per background recording (25–47), so the smallest attainable p is 1/n_B, about
  0.02–0.04. **The MH370 search could therefore not declare a detection on full-length windows by
  construction.** This is a non-detection by a test of limited power, not evidence of absence. The fix
  is more background: the full IMOS deployments run for months. That is the first task of item 3.
- **D3:** no pairs, so no coincidence was tested.

## 3. Kadri's H01W transients predicted at Perth Canyon

Each transient's source was placed along its bearing (±6.6°, twice the demonstrated sd), 300–3,000 km
from H01W, and its arrival predicted at 3315 and 3376.

- **Coverage:** 26 of the 44 event × logger windows are at least partly covered.
- **Detections at p < 0.05: 1 of 26**, where 1.3 are expected by chance. It is Table 1's 00:40:34
  (303.28°), seen at 3376 at 00:39:28. Its −66 s offset fits any source beyond about 1,000 km along
  303°, which the 2a geometry already disfavours for the core region.
- **The 306° major signal is UNINFORMATIVE at both of Kadri's times.**
  - At 00:52:03, the 3376 window is fully covered and nothing is detected. But the upper limit (104.0 dB
    re 1 µPa) is only 7.8 dB below Kadri's clipped H01W level (≥ 111.7 dB), short of the pre-registered
    20 dB margin for C_site and canyon-floor coupling.
  - At 00:54:30, the window is only partly covered.
  - Perth Canyon therefore neither confirms nor excludes his candidate. The 2a geometry verdict
    (disfavoured) stands on its own.

## 4. Information gain (bits)

- **On impact position, from the non-detection** (exploratory, `imos_nondetection_bits.py`):
  - with an assumed P_D of 0.1 / 0.3 / 0.5: **0.00004 / 0.0006 / 0.003 bit**;
  - even at P_D = 1: **0.21 bit**.
  - Coverage hardly varies with position, so the non-detection says almost nothing about **where**.
- **Its real import is on the source level.** With P_D calibrated against η and C_site (item 3), a
  non-detection at 0.94 coverage bounds **how loud** the impact could have been at these sites. That bears
  on η and on the §8 conditionals.
- **The likelihood the module returns stays 0.0** until the P_D gate passes.

*Hydroacoustics module, 2026-10-09.*

## Addendum, 9 October 2026: Scott Reef is blocked (shared ocean transport, ruling H5; `212e76d`)

The geodesic from every impact quantile (2.5–97.5%) to Scott Reef (3250) crosses the North West Shelf.
- For the southern quantiles it crosses land at North West Cape.
- On every path, 900–1,060 km of track is shallower than 1,000 m.

**So no direct SOFAR arrival from the core region reaches 3250.** Its MH370 windows are not informative,
and its P_D for this source is about zero. The C4 control is unaffected: the Curtin event reached Scott Reef
from the north-west, over open ocean.

**Revised numbers without 3250:**
- **Coverage:** the arrival falls in a scorable recording with probability 0.93 (was 0.94).
- **Positional information** from the non-detection: ≤ 0.003 bit at P_D ≤ 0.5; 0.20 bit at P_D = 1.

**The other sites:**
- **Perth Canyon is open:** the shallowest track before the receiver slope is at least 1,837 m.
- **Portland is open until its shelf.** Its receivers sit at 151–164 m, so they carry a shelf coupling
  loss, to be modelled in stage B.

*Hydroacoustics module, 2026-10-09.*
