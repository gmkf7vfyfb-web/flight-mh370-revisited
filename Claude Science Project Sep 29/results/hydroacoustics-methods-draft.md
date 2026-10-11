# Hydroacoustics module: methods (draft for the paper) - PROVISIONAL-OVERNIGHT

**Status:** working draft, written 10 Oct 2026 (~04:00–05:00 UTC) under the overnight plan
(`coordination/OVERNIGHT-2026-10-10.md`). It describes methods only. **No result in it is final.** Every
number is copied from a committed results note, which is named beside it.
**Labels:** prior impacts are either the *stand-in* (run `no-exhaustion-prior`, `b3dd44b`, track
295.66° ± 1.0°, `config/sensitivity/no-exhaustion-prior.toml`) or *reference-289* (`runs/snap289-m0011`,
track 289.7° ± 1.0°, `davey2016.toml` + `sensitivity/no-exhaustion-prior.toml` +
`sensitivity/reference-snapshots.toml`, rev `55c4536-dirty`). Both carry **uncorrected fuel** and a
**provisional sampler**. Platform: macOS arm64 workstation.
**Citations:** keys are those in `hydroacoustics-references.md` / `.bib`. Square brackets mark a key.

## 1. Role in the estimator

The module maps each impact draw from end of flight (time, position, speed, flight-path angle, mass,
kinetic energy) to predicted pressure arrivals at every relevant receiver. It does this along two
**separate** branches:
1. The deep sound channel (SOFAR), carrying acoustic energy at 1–100 Hz.
2. Acoustic-gravity waves (AGW), carrying compressible-ocean modes below the first cut-off.

Each branch returns a detection probability P_D before any likelihood is formed. A likelihood is admitted
only where (a) P_D at the receiver exceeds the gate and (b) the receiver's data are held. **Until both
hold, the module returns 0.0 in predictive mode** (ARCHITECTURE.md, stage 4). This is the module's
current status (§9).

## 2. Data

1. **IMS stations H01W (Cape Leeuwin), H08S and H08N (Diego Garcia), and H11N/H11S (Wake).** We use
   positions and instrument responses only [FDSN-IM]. Waveforms are not held: the public FDSN service
   returns no data for 2014.
2. **IMOS passive-acoustic loggers** [IMOS-ANMN-PA]. These are 3315 and 3376 (Perth Canyon), 3274 and
   3275 (Portland) and 3250 (Scott Reef), recorded at 6 kHz with a 34 % duty cycle and an 8 Hz analogue
   high-pass. We use raw recordings for 8 Mar 2014, plus a 14-day background (1,344 files each) at 3376,
   3274 and 3250.
3. **Published H01W and H08S traces** [Kadri2024]. These are the Figure 9 vector traces, digitised from
   the PDF (median vertex spacing 0.049 s), and Table 1's 19 H01W transients with bearings. The traces were
   high-passed at 5 Hz and band-passed at 2–40 Hz by the author (p. 11), so they carry no AGW content.
4. **Calibration and control shots** [Blackman2004UCRL; Blackman2004JASA], used for transmission-loss
   validation (air9 at H01W and H08S; air8 as a blockage control).
5. **Positive controls** from [CMST2014] (pp. 6 and 15) and [CMST2014ScottReef].
6. **The F-35A JASDF 79-8705 loss** on 9 Apr 2019, used as the calibrating impact:
   - working source point 40.64°N 142.96°E, at 10:26:32 UTC [Metz2023, p. 1348];
   - about 19 t, near-vertical entry [JASDF2019a; JASDF2019b];
   - energy 900 ± 200 MJ and 0.7 Pa peak at H11 [Brown2026, p. 17].
   The coordinates given in Kadri's Supplementary S1 are not used (ledger entry [KadriS1-F35]).
7. **Environment:** bathymetry from [GEBCO2026]; temperature and salinity from [WOA23] (March), converted
   to sound speed with TEOS-10 [TEOS10; McDougallBarker2011]; geodesics by [Karney2013] and [Vincenty1975].

## 3. Propagation

1. **Paths.** Every source-receiver geodesic is cut into a range-dependent section, sampled every 25 km
   along a ±2 km swath. The ocean-transport module's `ocean_paths` exporter produces these sections. Since
   the corrected build, its output has been identical on all 44 paths to the module's earlier segmented
   workaround, which is now retired.
2. **Transmission loss (TL)** comes from adiabatic normal modes, KRAKEN [Porter1992], with incoherent mode
   addition, in third-octave bands from 5 to 40 Hz. Volume attenuation follows [FrancoisGarrison1982a;
   FrancoisGarrison1982b], with spherical correction. The bottom is a fluid half-space, "hard": cp
   1,650 m/s, ρ 1.9 g/cm³, 0.5 dB/λ. The "soft" alternative (1,560 m/s, 1.5 g/cm³, 1.0 dB/λ) was rejected
   (§3.3).
3. **Validation against measured TL** [Blackman2004UCRL, Fig. 23], with verdict rules fixed in advance
   (`hydroacoustics-blackman-validation.md`):
   - air9: by the pre-registered rule (median and RMS over 13–40 Hz), **partly validated** at both stations.
     Median residual −0.15 dB at H01W and +3.17 dB at H08S; RMS 7.93 and 7.91 dB.
   - **That rule cannot see a slope, and the slope is wrong** (correction of 10 Oct, raised by Pete).
     Measured − predicted TL tilts by +12.7 dB per octave (H01W) and +7.4 dB per octave (H08S): about −10 dB
     at 5–20 Hz, rising to +14/+15 dB at 63 Hz. **Absolute level and frequency slope are therefore NOT
     validated.** The tilt is shared by both stations, which points to the assumed airgun source spectrum or
     to near-source coupling rather than to the path. An independent audit (architecture,
     `results/hydroacoustics-audit/`) tests this with independent source spectra.
   - The station-to-station difference, which cancels the source term, fits to −1.5 dB median and 3.4 dB RMS.
     This is the only part that is validated.
   - A slope criterion is added for future validation (not retroactive).
   - The soft bottom misfits by +28 to +36 dB and is rejected.
   - air8: the negative control follows (+38.1 dB blockage to H01W). The positive control is consistent
     (+0.1 dB at H08S).
4. **Cross-check by parabolic equation.** RAM [Collins1993], via [pyram] (split-step Padé, 8 terms), is
   run in the same environment (`hydroacoustics-ram-tl-check.md`, prereg `6b747a1`):
   - On the air9 → H01W path (station difference validated; absolute slope not), the two models agree to a median |Δ| of 1.78 dB.
   - To the seabed IMOS loggers, KRAKEN is pessimistic by 13–47 dB at Perth Canyon and 23–132 dB at
     Portland. This is the shelf and slope coupling that the adiabatic approximation loses.
   - Detection probabilities at the IMOS loggers therefore use RAM-corrected TL.
   - air8's ridge blockage weakens from 39.1 dB under KRAKEN to 18.3 dB under RAM.
   - On the F-35A → H11 path, KRAKEN is about 3.5 dB optimistic.

## 4. Source term and coupling calibration

1. **Model.** The source energy flux density at 1 m is E_s = η · E · ρc / 2π. Here E is the impact kinetic
   energy (vertical KE as a sensitivity case) and η the acoustic coupling efficiency. E_s is distributed
   over a spectrum S_b(τ), which is flat to the corner frequency 1/τ and rolls off as f⁻² (f⁻⁴ as a
   sensitivity case). It is radiated by a near-surface dipole at source depth z_s.
2. **Calibration of η on the F-35A** (`hydroacoustics-f35a-eta-calibration.md`, prereg `3ca9564`):
   - The relation η_cal = (0.7²/R) / [E ρc/2π · Σ_b S_b(τ) 10^(−TL_b/10)] is inverted along the
     Metz-consistent path to H11.
   - Under KRAKEN, η_cal runs from 2×10⁻² at z_s = 2 m to 1×10⁻⁴ at 30 m (f⁻²).
   - With the RAM correction for that path, the median rises from 1.3×10⁻³ to 2.7×10⁻³.
   - η is then drawn per MH370 sample *paired* with the same τ and z_s. The dipole factor and most of the
     spectral dependence therefore cancel between calibration and prediction.
3. **Is the F-35A the most efficient coupler?** We do not assume so. It is a single near-vertical,
   high-speed (≥ 305 m/s) entry. Glide or ditch entries (flight-path angles 1.4–4°) may couple differently,
   and that uncertainty is carried through the paired (τ, z_s, η) draw rather than resolved.

## 5. Detection, null distributions and injection-recovery

1. **Detectors on IMOS raw data** (`hydroacoustics-imos-detectors.md`, prereg `02bb8d0`):
   - D1 is an STA/LTA energy ratio, 5–40 Hz (STA 2 s, LTA 30 s).
   - D2 is band-power exceedance over the background median.
   - D3 is two-site coincidence.
   - p-values come from each logger's empirical window-maximum null over the 14-day background, leaving
     out the tested recording.
   - D1 recovers all four published positive controls, at SNR 7.9–19.2 dB.
2. **Injection-recovery** (`hydroacoustics-item3-injection-recovery.md`): real transients are injected
   into real noise to give P_D(SNR). At false alarm 0.005, SNR₅₀ is 28.8 dB (3376), 18.6 dB (3274) and
   38.5 dB (3250). Stage B maps SNR to coupling η; stage C maps it to the impact prior.
3. **Detectability.** With RAM-corrected TL, P_D at any open IMOS logger is 7.6 % at false alarm 0.005
   and 32 % at 0.05 (stand-in prior). The windows recorded on 8 Mar 2014 show no detection. Because P_D is
   low, the information from this non-detection is below 10⁻³ bit.
4. **Coverage.** The duty cycle alone caps P_D. The 5 min alternating slots mean a given arrival is
   recorded with probability about 0.34 per logger (`hydroacoustics-imos-noise.md`, §3).

## 6. Coincidence and pair tests on the published traces

1. **Purpose.** These tests ask whether pairs of transients at two sites are more consistent with a
   common impact source than with chance. The rate of chance pairs is measured, never assumed.
2. **Pair statistic.**
   - For an H01W trigger and an H08S candidate, the Bayes factor BF compares a common source against
     independent arrivals.
   - Under the common-source hypothesis, the implied source lies on the impact prior, the impact time is
     00:19:37 + 300 ± 180 s, and the group speed is c = 1.482 ± 0.006 km/s.
   - Picks carry 10 s error. Table 1 bearings use a Student-t with sd 3.3°.
   - **The per-pair threshold, BF ≥ 10, is the conventional "strong" boundary of [Jeffreys1961].** The
     alternative scale of [KassRaftery1995] was considered. We report a sweep over thresholds (0 to 2 in
     log₁₀ BF) rather than relying on one.
3. **Null distribution.** The null is a time slide: one site's picks are shifted against the other's over
   non-physical lags, and the best-pair BF is recomputed each time. p is the fraction of slides at least as
   extreme as the observed value.
4. **H08S impulse train.**
   - Kadri's H08S panels are dominated by an impulse train with a 9.98 s period. We attribute it to
     seismic airgun surveys, as CMST documented for that period [CMST2014, pp. 20–23].
   - The train is treated as a structured background, not as signal.
   - We test it three ways, each pre-registered, with injection-recovery for each:
     1. cycle-outlier tests, on timing (prereg `ddaa848`, amended `4b0ee7e`);
     2. an energy-only test (prereg `8ff37fb`), using per-pulse peak, pre-peak and post-peak energy so as
        to be independent of a cadence that varies with vessel range;
     3. a template-shape test on the 0.25 s log-envelope, testing shape, shoulder and tail (prereg
        `360bf14`). Phase cannot be recovered from digitised polylines, so the test does not use it.
   - Excess energy (constructive interference or an added source) is the primary statistic, and a deficit
     is secondary, because unrelated sources add energy on average.
5. **Look-elsewhere.** Searches not fixed in advance are labelled exploratory. Their p-values are corrected
   for the number of variants tried.

## 7. AGW regime

For each impact draw, the local water depth H gives the AGW cut-off period T_c ≈ 4H/c. Each draw is
classed by the ratio of its source duration τ to T_c as impulsive, transitional or quasi-static
(`agw_regime.py`, prereg `393843f`). On the stand-in prior, H runs from 3,292 to 4,355 m, so T_c is
8.8–11.6 s. 87 % of draws are impulsive and 13 % transitional.

AGW arrivals at H01W and H08S would lie below the 5 Hz high-pass applied to the published traces. They can
only be tested on raw IMS data, which are not held. The IMOS loggers' 8 Hz analogue high-pass likewise
excludes them.

**Amplitude estimate (exploratory, prereg `55ebdcc`; `hydroacoustics-agw-scenarios.md`).**
- **Model:** a vertical surface-force impulse J = m v_z on an isovelocity, rigid-bottom waveguide, adiabatic
  normal modes [Jensen2011]. Noise from measured sea-floor pressure: RHUM-RUM DPGs [RHUMRUM_YV], March 2013.
- **Results:**
  - No full-water-depth mode below 0.24 Hz (H01W) or 0.27 Hz (H08S) reaches the hydrophones, whose local
    water depth is about 1.5 km.
  - From 0.25 to 2 Hz the median noise is 12–110 dB above the upper end of the steep-entry signal range.
  - Ditching is 40–110 dB below.
- **So the AGW branch carries P_D ≈ 0 for every scenario and adds no likelihood term.** Kadri's 2–40 Hz
  "AGW" signals [Kadri2024] are the acoustic arrival of §3. Tunnelling past shallow barriers
  [KadriAbdolaliKirby2025] is not modelled.

## 8. Discipline

1. **Pre-registration.** Every test's hypotheses, statistic, threshold and verdict rules are committed
   before it is run.
2. **Defects are disclosed, and the defective run is kept.** For example, the template test's first run
   had a residual that was zero by construction at the peak. It is kept as `v1_defective`, and the
   corrected run excludes the peak window.
3. **Negative results are kept** behind configuration flags.
4. **Provenance.** Results record their provenance from the producing run's `run.json`.
5. **Smoke runs are never quoted** as evidence.
6. **Every figure carries a footnote** giving run, prior track, base config, key parameters and
   assumptions.

## 9. What stands, what is open

- **The module returns 0.0 to the composer** under both priors. The non-detection at IMOS carries less
  than 10⁻³ bit, and the IMS data that could carry more are not held.
- **Value of raw IMS data (exploratory planning only, not a result).** A weak H01W + H08S pair could add
  about 1–2.7 bits, depending on pick error (`hydroacoustics-near-limits-planning.md`).
- **Window for a raw-data request.** Windows come from end of flight's option × cause posteriors, with impacts
  before 00:19:37.443 excluded (`+alive`) and `+silent` beside them (`prepare/search_windows.py`, prereg `55eb191`;
  `hydroacoustics-search-windows-ref289.md`). On reference-289 they are H01W 00:25–02:20 and H08S/H08N 00:45–02:50
  UTC, with unconverged end edges. They will be re-derived from the large-run impacts.
- **Proxy noise to replace.** The IMS noise is currently proxied from the Perth Canyon logger. It is to be
  replaced by noise traced from [Blackman2004UCRL] Appendix B.
- **Request for raw data:** Pete's decision.
