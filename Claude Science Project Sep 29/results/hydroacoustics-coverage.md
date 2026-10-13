# Hydroacoustics: COVERAGE (Pete's sampling-coverage rule, 10 Oct 2026)

*Hydroacoustic Module, 11 Oct 2026 ~00:05 UTC. One place for the coverage of every hydroacoustic result. Each results
note carries a short COVERAGE section that points here and adds its own gaps.*

## (a) Feasible set (what the aircraft and ocean can produce at the receivers)
- **Impacts:** every end-of-flight impact (position, time, speed, entry angle, energy) inside the 777-200ER envelope.
  That includes steep high-speed dives (EoF reference-289 dive branch: 270-360 m/s, 30-58 deg), controlled
  glides/ditchings (60-150 m/s, 1-4 deg), and Holland-type rapid descents ending soon after 00:19.
- **Signals:** sound in the deep sound channel (SOFAR, about 2-100 Hz), and full-water-depth low-order modes
  ("acoustic-gravity waves", below about 2 Hz).
- **Receivers:** IMS H01W, H08S, H08N; IMOS 3315, 3376, 3274, 3275, 3250.

## (b) Model's reach
- **SOFAR branch (5-40 Hz):** KRAKEN/RAM TL on ocean_paths sections, with the F-35A-calibrated coupling η, applied to
  total or vertical kinetic energy (both reported).
  - **Reach gap R1:** absolute TL and its slope are NOT validated (air9: tilt +12.7/+7.4 dB per octave). Only the
    station difference is validated (3.4 dB RMS). Below 13 Hz at H01W nothing is measured.
  - **Reach gap R2:** η is calibrated on one near-vertical event (the F-35A). Shallow-angle ditching coupling is an
    extrapolation (±10 dB declared).
  - **Reach gap R3:** horizontal momentum is not a source term.
- **Low-frequency branch (0.03-5 Hz):** an order-of-magnitude normal-mode estimate only
  (`hydroacoustics-agw-scenarios.md`). Modes below 0.24/0.27 Hz cannot reach H01W/H08S. This is physics, not a
  model cap.
- **Blocked paths (physics, not gaps):** H08N (Great Chagos Bank) and IMOS 3250 (Scott Reef).
- **Detection side:**
  - **Data gap D1:** raw H01W/H08S/H08N waveforms are not held. Only Kadri's published traces (5 Hz high-passed)
    and Table 1 are used.
  - **D2:** IMOS covers the arrival with 0.93 recording coverage.

## (c) Proposal's coverage (where the samples land), ESS per option and family
- **Impact samples:** end of flight's next-run core (b), 4 families × 4 seeds.
- **Hydro weights:** importance weights carry the proposal correction. Hydroacoustics adds no proposal of its own.
- **Kish ESS of the end-of-flight sweep** (`summary/sweep-summary-<family>.json`, `ess_total`, before any hydro term):

| 00:19 option | free | Davey dynamics + radar | descent-climb | routes | status |
|---|---|---|---|---|---|
| 00:19 Held Out | 12,337,220 | 12,339,414 | 12,336,817 | 12,325,581 | estimable |
| 00:19 R600 BTO Only | 6,949,043 | 6,344,202 | 7,289,576 | 7,451,904 | estimable |
| 00:19 R600 BTO + Raw BFO | 234,529 | 224,950 | 341,483 | 272,778 | estimable |
| 00:19 Holland H1 | 50 | 34 | 125 | 46 | **not yet estimable - targeted sampler in progress** (ESS < 1,000 gate) |
| 00:19 Holland H2 | 67 | 64 | 106 | 73 | **not yet estimable - targeted sampler in progress** (ESS < 1,000 gate) |

- P(family) is held fixed at 0.6948 / 0.1527 / 0.1376 / 0.0149. The re-weighted families (Ẑ_00:19 per family and
  option) are shown beside the fixed values where a note uses them.
- `+alive` ln Ẑ is applied to `+unpowered` as a declared approximation.

## Gaps and their status
| id | gap | type | status |
|---|---|---|---|
| G1 | Holland H1 and H2 have ESS 34-125 per family | coverage | OPEN. Waiting for end of flight's targeted sampler. Labelled "not yet estimable" in every result. The windows cover their provisional ranges (impacts 00:19:46-01:10) |
| G2 | TL absolute level and slope (R1) | reach | OPEN. Hydro audit (architecture, 17:50 −0600) running. Every P_D and R_hyd is labelled "provisional on TL calibration" |
| G3 | ditching coupling (R2) and horizontal momentum (R3) | reach | DECLARED. ±10 dB on η. The total-KE vs vertical-KE pair brackets it |
| G4 | raw IMS data (D1) | data | Pete's decision. Request windows: H01W 00:25-02:20, H08S/H08N 00:45-02:50 UTC |
| G5 | below 13 Hz at H01W not measured | reach | DECLARED. The impact charts mark it |
| G6 | low-frequency branch at other impact positions | coverage | DECLARED. The receiver-depth cutoff is position-independent |

## Parameter bounds and sources
- Mass 175 t (scenario charts).
- Speeds and angles from EoF reference-289 / next-run impacts.
- η: F-35A (Brown 2026, 900 ± 200 MJ, 0.7 Pa at H11), ±10 dB for aircraft difference.
- SOFAR group speed 1.482 ± 0.006 km/s.
- Bearings: Kadri Table 1, Student-t sd 3.3 deg.
- IMS noise: Blackman 2004 App. B.
- Low-frequency noise: RHUM-RUM DPGs (RESIF YV), March 2013.
- τ prior: log-uniform 0.05-10 s (brief).

- Hydroacoustic Module
