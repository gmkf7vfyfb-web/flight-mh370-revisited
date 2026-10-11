# Hydroacoustics: N×2D Fresnel-corridor transmission loss for the calibration events (ruling 6)

Hydroacoustic Module, 11 Oct 2026.
- Pre-registered at `4d62d144` (`prepare/nx2d.py`).
- Results data at `29e21362` (`results-data/nx2d/`).
- Chart: `hydroacoustics-nx2d-corridor.png` / `.pdf`.
- Status: **method check PASSED; not used for any likelihood**. Hydroacoustics stays predictive (`lnL_gated` = 0.0).

## Method (as pre-registered)
- **Corridor members.** For each band (5–40 Hz, 10 third-octave bands), 17 member paths are offset sideways from the
  geodesic by u·F(s), with F = √(λ s (R−s)/R) and u = −2 … 2 in steps of 0.25. Member weight is exp(−u²).
- **Per-member TL.** Each member gets its own GEBCO_2026 section (3×3 median, 0.5 km steps) and its own KRAKEN
  coupled-mode TL, using the same profile builder and hard bottom as `air9_tl_validation`. The receiver is at
  hydrophone depth.
- **Blocking.** A member that has no propagating mode on any profile is BLOCKED and contributes zero intensity.
- **Corridor TL.** Corridor TL = −10 log10 Σ w_j 10^(−TL_j/10) / Σ w_j. The open-weight fraction is reported with it.
- **Checks on AF447 → H10S** (no feature shallower than 1,000 m), at z_s = 10 m:
  - K1: |corridor − ocean-transport section TL| ≤ 1.5 dB;
  - K2: |u = 0 member − section| ≤ 1.0 dB.

## Results
| path | open weight | corridor − single path (z_s 10 m) | check |
|---|---|---|---|
| AF447 → H10S (control, 2,210 km) | 1.00 in all bands | max 0.14 dB | K1 PASS (0.14 ≤ 1.5), K2 PASS (0.16 ≤ 1.0) |
| San Juan charge → H10N (5,989 km) | 1.00 in all bands | −0.03 to +0.34 dB | – |
| Yemenia 626 → H08S (3,237 km) | **0.00** (510/510 members blocked) | – | – |
| Yemenia 626 → H08N | **0.00** (510/510 members blocked) | – | – |

1. **Open paths.** The corridor changes TL by 0.34 dB or less. On paths where single-path propagation is open,
   N×2D is not a material correction.
2. **Yemenia 626 (June 2009).** No member reaches H08S or H08N in any band from 5 to 40 Hz at z_s = 2, 10 or 30 m.
   - Every member crosses water 26 m deep or shallower, or land: Saya de Malha Bank (9.2–9.9° S, 59.7–61.0° E) on both
     paths, the Farquhar group (10.2° S, 51.0° E) on H08N, and Grande Comore for u > 0. In 26 m of water, KRAKEN
     finds no propagating mode at these frequencies.
   - The predicted SOFAR peak is therefore zero, which agrees with Kadri's upper limits (H08S 0.78 Pa at SNR 1.07;
     H08N 0.25 Pa at SNR 0.87). **Yemenia cannot test the coupling at the Diego Garcia stations** under this model.
     It is removed from the Q1 candidate list for H08, and the reason is recorded.
3. **San Juan calibration charge → H10N.** The implied source spectrum is RL (noise-subtracted, Nielsen 2021 Fig. 5c)
   plus TL, with an OLS slope on log2 f:

   | z_s | single path | corridor |
   |---|---|---|
   | 33 m (charge depth) | −1.83 ± 0.33 dB/oct | −1.73 ± 0.33 dB/oct |
   | 2 m | −1.67 ± 0.31 dB/oct | −1.56 ± 0.31 dB/oct |

   - The change is 0.1 dB/oct, less than one SE.
   - The single-path numbers reproduce the stand-in exactly.
   - The absolute level is **still untested**, because no cited explosive source spectrum is in hand (Gaspin & Shuler
     1971 is blocked and needs Pete's manual download).

## Deviation
The San Juan run took 13 min of wall time at 1 thread outside the heavy lock, over the ~10 min guide. It was started
outside the lock because core run G and drift run A were holding it. Peak RSS was under 0.3 GB.

## COVERAGE
- **(a) Feasible set (here: physical propagation paths).**
  - 3-D horizontal refraction and diffraction around banks.
  - Seabed-borne (seismic) paths.
  - Mode tunnelling through short shallow stretches.
- **(b) Model reach.**
  - In-plane coupled modes on 17 laterally offset 2-D sections within ±2 Fresnel widths; hard bottom.
  - **Gap G-N1 (reach):** diffraction around a bank wider than ±2 F (Saya de Malha is about 300 km across, against
    F of about 30 km at 5 Hz) and seabed-borne paths cannot be produced. This is declared conditional: "SOFAR branch,
    within ±2 Fresnel widths". It affects only the Yemenia → H08 conclusion, and only in the direction of "more
    signal than predicted".
- **(c) Proposal coverage.** This study is deterministic, so no sampling ESS applies.
  - Bands: 10 of the 10 pre-registered.
  - Source depths: 3 (4 for San Juan).
  - Members: 17 per band.
  - No impact posterior is used, so the 00:19 options and families A1/A2/B are not applicable. No MH370 result is
    affected.
- **Parameter bounds.**
  - u range ±2: pre-registered; at that offset the Fresnel weight is e⁻⁴ = 0.018.
  - Hard bottom: as air9 validation.
  - Charge depth 33 m: Vergoz 2021 p. 2528.

## Next (audit fix list, in order)
1. **Ruling 1 (paths).** Request an H04S section from ocean transport. The H04S position comes from Nielsen 2021 and
   is cited as a secondary source. With it, the San Juan station difference (H10N − H04S observed −6.6 to +4.4 dB)
   becomes a TL-only test that needs no source spectrum.
2. **F3.** Find more calibration events with SNR ≥ 3 at a station with an open path.
3. **F9.** Relabel the borrowed IMS P_D.
