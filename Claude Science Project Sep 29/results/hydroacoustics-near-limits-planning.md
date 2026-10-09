# Hydroacoustics: what is detectable near the limits, and what a weak multi-site detection is worth - EXPLORATORY

**Status.** This is a planning analysis, not a test: no recorded data were searched. The scripts are in
`engine/hypotheses/hydroacoustics/prepare/exploratory/` and the outputs in
`results-data/near_limits/` (module commit on `hypothesis/hydroacoustics`).

**Run provenance:** impact positions are the stand-in drawn from run `no-exhaustion-prior` (`b3dd44b`),
prior track 295.66° ± 1.0°, config `config/sensitivity/no-exhaustion-prior.toml`. Not yet reference-289.

**Model:**
- **Source:** η calibrated on the F-35A, RAM-corrected (`hydroacoustics-ram-tl-check.md`).
- **Transmission loss:** IMOS TL RAM-corrected. H01W/H08S TL is KRAKEN on the five impact-quantile paths,
  plus the RAM Δ on the median path. RAM is 2–4 dB *above* KRAKEN to H01W, and 5–8 dB above it to H08S
  over Broken Ridge.
- **Draws:** the same draws as stage C.
- **Two proxies, not measurements:**
  - IMS noise = the Perth Canyon 3376 background median, ±5 dB;
  - IMS P_D = the stage A injection fit at Portland 3274.
- **C_rcv:** for the SOFAR-axis IMS receivers it is a 3 dB term instead of the 10 dB seabed term.

## 1. Detectability under less pessimistic assumptions

### IMOS: P_D(any open logger)

| case | P_D |
|---|---|
| Baseline (stage C, RAM-corrected), Bonferroni false alarm 0.005 | 7.6 % |
| Single pre-registered window, false alarm 0.05 | 32 % |
| C_site = C_rcv = 0 (central coupling), false alarm 0.005 / 0.05 | ≈ 0 / 15 % |
| C_site + C_rcv shifted +10 dB, false alarm 0.005 / 0.05 | 22 % / 56 % |

Recording coverage of the predicted arrival is 0.93 over the open loggers.

### IMS: predicted peak 1 s SNR (5–40 Hz), on the proxy noise

| station | 5 % | median | 95 % | P(SNR > 10 dB) |
|---|---|---|---|---|
| H01W | −11 | **+6.3** | +24 | 37 % (21–55 % for noise ±5 dB) |
| H08S | −20 | **−2.7** | +15 | 12 % (5–24 %) |

### Both H01W and H08S detect (P_D proxy; the shared source term makes the two stations correlated)

| per-station false alarm | no array gain | with +4.8 dB triad gain |
|---|---|---|
| 0.005 | 2.3 % (0.7–6.3 %) | 6.1 % |
| 0.05 | **21 %** (11–36 %) | **36 %** (21–53 %) |

**Reading:**
- **The IMS pair is near the limit,** neither hopeless nor assured.
- **Whether it works is decided by the operating point,** that is, a loose per-station threshold with
  array processing.
- **The noise level is unmeasured and dominates the uncertainty:** ±5 dB of noise moves the joint
  P_D by a factor of 3.

## 2. What a weak detection at two or more sites is worth

**Information measure:** KL(posterior ‖ prior) in bits, median over truths. The likelihood is the honest
mixture (1 − π)·background + π·signal. The background is uniform over the ±1 h window and over bearing,
and π = P(the candidate is the impact).

| sites | pick sd | no bearing | bearing sd 3.3° | 6° | 12° |
|---|---|---|---|---|---|
| H01W alone | 10 s | 0.09 | 0.43 | 0.23 | 0.15 |
| **H01W + H08S** | 5 s | 2.1 | 2.7 | 2.2 | 2.2 |
| **H01W + H08S** | 10 s | 1.8 | 2.4 | 2.0 | 1.8 |
| **H01W + H08S** | 20 s | 1.2 | 1.7 | 1.4 | 1.0 |
| **H01W + H08S** | 40 s | 0.55 | 1.0 | 0.7 | 0.6 |
| 3376 + 3274 (IMOS) | 10 / 20 s | 0.58 / 0.33 | (no bearing) | | |
| H01W + H08S + 3274 | 10 / 20 s | 2.2 / 1.35 | | | |

These values are for π = 1; at π = 0.05 they change by less than 0.3 bit with bearings. They are close to
the 1.70-bit composer-test result.

**Interpretation:**
- **A second site multiplies the value about twentyfold.** The two-site case carries 1.8–2.7 bits at
  pick errors of 5–10 s and 1.0–1.7 bits at 20 s, falling to 0.55–1.0 bit at 40 s. Weak detections lose
  information gradually, through timing.
- **H08S does the work.** It looks along the arc; the IMOS pair looks across it (0.3–0.6 bit).

### The real limit is chance coincidence

A genuine pair must satisfy three conditions set by the prior:
- H08S − H01W time difference within 886–1,313 s (a 427 s span);
- back-azimuth at H01W within 252.6–276.4° (24°);
- back-azimuth at H08S within 140.5–157.9° (17°).

| per-station false alarm | assumed transient rate λ | expected chance pairs, time only | with bearings at both sites |
|---|---|---|---|
| 0.005 | 0.36 /h | 0.031 | 0.0003 |
| 0.05 | 3.6 /h | 3.1 | 0.027 |

The rates λ come from the IMOS stage A null at 50 s windows. They are a proxy, because IMS background
transient rates are unmeasured: Kadri's Table 1 implies about 67 /h at his own threshold.

**Expected gain** ≈ P(both detect) × I(π):
- **Loose thresholds with bearings:** π ≈ 0.9, giving about **0.4–0.7 bit**. A candidate pair would be
  about 10:1 in favour of real.
- **Strict thresholds:** about 0.05–0.12 bit.
- **Without bearings,** loose thresholds are swamped by chance pairs (π ≈ 0.06).

**So operating near the limit is the right strategy, provided three things are true:**
1. bearings are measured on both triads;
2. the joint consistency test is pre-registered;
3. the chance-pair rate is measured empirically by time slides, not assumed.

## 3. What can be tested on data in hand

| data | status | next test |
|---|---|---|
| IMOS raw (5 loggers, plus 14 days of background) | held; single-site searches done (no detection) | the pre-registered loose-threshold **Perth Canyon + Portland coincidence** search, with chance pairs measured by time slides on the 14-day background and its P_D by injection. Worth ≤ 0.1 bit expected, but it is the full protocol rehearsed on real data. Minutes of CPU, so it can run now. |
| H01W / H08S raw | **not held.** EarthScope serves the IM metadata only and returns "no data" for the 2014 waveforms (checked 9 Oct). Access is through the CTBTO vDEC or a national data centre. | the same protocol plus triad bearings, the 0.4–0.7-bit case. It needs the data, which is a decision for Pete. |
| Kadri's published H01W traces (digitised) | used (2a) | none further |
| reference-289 impacts | in `mh370-exchange/end-of-flight/` | rerun this analysis and the AGW regime on them |

*Hydroacoustics module, 2026-10-09. Exploratory; supersedes no pre-registered result.*
