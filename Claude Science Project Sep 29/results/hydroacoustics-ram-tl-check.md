# Hydroacoustics: RAM parabolic-equation cross-check of the KRAKEN transmission loss - PROVISIONAL

**Pre-registration:** `prepare/ram_tl_check.py`, committed `6b747a1` before any matched comparison was
computed.

**Implementation fixes** (`de73e15`, `0a48073`, `f7461b1`). None changes the design:
- read KRAKEN's field at the receiver range;
- handle the disclosed stage B `no_modes` case;
- hold the sound speed below 7,000 m across the Japan Trench, exactly as KRAKEN's profile builder does.

**Outputs:** `engine/hypotheses/hydroacoustics/results-data/ram_check/`.

**Runtime:** 1 h 45 min single-threaded, outside the lock (ruling H7). The convergence step took a
further 43 min.

**Run provenance** (from `results/no-exhaustion-prior-run.json`): impact positions are the module stand-in drawn from run `no-exhaustion-prior` (`b3dd44b`; `results/no-exhaustion-prior-summary.json`, sha256 `394029b4…cb9c`), prior track **295.66° ± 1.0°**, base config `config/sensitivity/no-exhaustion-prior.toml`. Not yet reference-289.

## Set-up

- **Common environment:** RAM (pyram 1.3.0, split-step Padé with 8 terms) and KRAKEN (adiabatic,
  incoherent modes) see the same environment:
  - 5 km bathymetry profiles;
  - shared sound-speed nodes;
  - a fluid half-space bottom (1,650 m/s, density 1.9, 0.5 dB/λ);
  - no water absorption in either model;
  - the same spherical correction and the same receiver depths.
- **Band values:** RAM is averaged in intensity over 9 frequencies across each third octave and over the
  last 500 m of range.
- **Grid:** dr = 2λ, dz = λ/20. Halving both moves no band value by more than 0.83 dB, so the
  pre-registered criterion of 1 dB passes.

## Results: Δ = TL_KRAKEN − TL_RAM (dB), 10 m source

| path | 5 Hz | 10 Hz | 20 Hz | 40 Hz | reading |
|---|---|---|---|---|---|
| air9 → H01W (validated deep path) | −2.0 | +1.5 | +1.3 | +5.3 | **sanity check passes**: median \|Δ\| 1.78 dB against ≤ 3 dB |
| impact (50 % latitude) → 3376 Perth Canyon, 407 m | +2.6 | +12.9 | +28.5 | +47.2 | adiabatic is pessimistic |
| impact (50 % latitude) → 3274 Portland shelf, 149 m | (no KRAKEN mode) | +22.8 | +57.7 | +132.2 | adiabatic is grossly pessimistic |
| air8 → H01W (ridge) | +2.4 | +0.6 | +10.0 | +34.7 | see the air8 section |
| F-35A → H11S | −0.8 | −3.5 | −3.1 | −3.8 | adiabatic is about 3.5 dB optimistic |

The 30 m source gives the same Δ to within 1 dB. RAM's own TL to the seabed loggers is 123–151 dB, which
is comparable to deep-water SOFAR paths.

**Why the adiabatic model fails here.** It removes each mode's energy at its up-slope cutoff. A coupled
solution hands that energy to the lower modes, which still reach the canyon floor and the shelf. This
also explains the Curtin event being recorded at the RCS canyon floor.

## Verdicts (rules fixed before running)

1. **The IMOS conclusion is ROBUST TO THE TL MODEL, but narrowly.**
   - **Corrections applied:**
     - stage B TL corrected by Δ (Perth Canyon Δ for 3315/3376, Portland Δ for 3274/3275);
     - H11 TL corrected by the F-35A Δ, which raises η_cal from a median of 1.3×10⁻³ to 2.7×10⁻³;
     - stage C rerun with the same draws.
   - **Result:** P_D(any open logger) = **7.6 %** at false alarm 0.005 (f⁻²; 7.6 % with f⁻⁴), below the
     0.1 threshold.
   - **At false alarm 0.05 it is 32 %.** The median best-logger SNR is now **+9.8 dB** (95th percentile
     +33 dB), against −13.8 dB before.
   - **"Effectively blind" was wrong.** The previous notes said the IMOS recorders were effectively blind
     to the impact; that was an artefact of adiabatic TL. They are marginal.
   - **The non-detection still carries little position information.** The 2b bound is about 5×10⁻⁵ bit at
     P_D 0.1 and about 6×10⁻⁴ bit at 0.3. Still negligible.
2. **The air8 blockage is WEAKENED.**
   - RAM puts air8 → H01W 18.3 dB above air9 → H01W (band mean): 7.6, 19.8, 22.4 and 23.3 dB at 5, 10, 20
     and 40 Hz.
   - KRAKEN's Δ_H01 was +39.1 dB; the pre-registered threshold is 20 dB.
   - **The ridge still costs about 20 dB at 10 Hz and above,** so the air8 non-observation at H01 remains
     consistent with blockage whenever air9's H01 SNR was below about 20 dB. Blackman does not print it,
     so the explanation is weakened, not refuted.

## Consequences

- **The item 3 and F-35A notes are corrected** by addenda pointing here.
- **Stage B and C P_D are no longer reported as lower bounds** for the RAM-corrected loggers. They now
  carry RAM's own uncertainty: one path per site, interpolated in log f, with a fluid half-space bottom.
- **The likelihood stays 0.0.** For IMOS the non-detection is worth well under 10⁻³ bit, so the gate
  question is moot in practice. For H01W/H08S the raw data needed to measure P_D are not held (§9).

*Hydroacoustics module, 2026-10-09.*
