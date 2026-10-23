cd "repo/Claude Science Project Sep 29/results"; cat >> hydroacoustics-blackman-validation.md <<'EOF'

## Addendum, 22 October 2026: transmission-loss recalibration (work order 2026-10-21 block 9; Refresh v2 §9 a, b, d) — PREDICTIVE, NOT CALIBRATED

Pre-registration `e949144` (`prepare/tl_recal_block9.py`, module branch), committed before any number below was computed;
amendment 1 (band counts, no rule changed) and amendment 2 (exploratory +30/+40/+50 km offsets) are recorded in the same
file. Criteria: the audit's level, slope and shape grades (`hydroacoustics-audit/criteria.md`, `940f1a3`). Every number
carries **C1** (propagation slope misfit, +10.4 / +7.4 dB per octave uncorrected at H01W / H08S) and **C2** (coupling
efficiency η not calibrated). Overnight unattended run; the model's parameters come from EW0112, OFR 95-228 and geometry,
none from Fig. 23. **Disclosure:** the author had seen the earlier post hoc result (`air9_ew0112` amendment 1), so route 1
is a confirmatory re-scoring of a pre-specified model on the training case, not a blind test and not an independent
confirmation (the independent-site test `airgun_sites_confirm` was NOT TESTABLE).

### (a) Route 1 — air9 source spectrum from the EW0112 near-source calibrated recordings

Forward model: received level = S0 + AF − TL, with S0 the far-field monopole source spectrum built from the EW0112 Fig. 2
Ball hydrophone spectrum (DIGITISED, two shots, scaled to 1 m by 25.75 m, near-field reference factor removed for the
OFR 95-228 20-gun layout, V^(1/3) weights, Ball 30 m ahead and 15 m deep), AF the horizontal array factor toward each
station, and TL the module's KRAKEN chain recomputed on the shared GEBCO_2026/WOA23 sections (pipeline check against the
audit's M1 model TL: 0.0 dB in every band). Measured received level = SL_B − TL_obs(Fig. 23, DIGITISED), SL_B = 235 dB
(230–240 as the range). Bands: Fig. 23 span ∩ Fig. 2 readable (40 Hz excluded): H01W 12.5–63 Hz (7 bands), H08S 6.3–63 Hz
(10 bands); 7 shared bands.

![](hydroacoustics-air9-ew0112-predicted-vs-measured.png)

| station, nominal (z_s 10 m) | n | LEVEL (SL_B 235; 230 / 240) | SLOPE (dB/oct) | SHAPE (dB) |
|---|---|---|---|---|
| H01W | 7 | −11.5 FAIL (−16.5 / −6.5, FAIL at all three) | **−2.3 ± 1.7 PARTIAL** | 3.1 PARTIAL |
| H08S | 10 | −15.9 FAIL (−20.9 / −10.9, FAIL at all three) | **+0.5 ± 1.3 PASS** | 3.9 PARTIAL |
| grid (45 geometries) | | | slope PARTIAL-or-better at both: **0.78** (z_s 9 m 0.93, 10 m 0.80, 12 m 0.60; fails only for a deep Ball, z_h 20–30 m) | shape not FAIL anywhere |

With the common mode removed (the path-only view, 7 shared bands): r̃ slope ∓1.1 ± 0.2 dB/oct per station (PASS),
level ±1.9 dB (PASS), shape 0.3 dB (PASS); the station difference itself has slope 2.2 ± 0.3 dB/oct (PARTIAL under C2)
and median 3.7 dB (PARTIAL). The common mode c_b after the EW0112 source: slope **−1.2 ± 1.8 dB/oct (PASS)**, shape
3.2 dB (PARTIAL); before it (flat source, same bands, same sign) the common slope was about −9 dB/oct.

![](hydroacoustics-air9-ew0112-residual-vs-frequency.png)

**Verdict under the pre-registered rule: NOT EXPLAINED.** The slope and shape conditions are met at both stations and
on 78% of the geometry grid, but the LEVEL condition fails for every SL_B in 230–240 dB, and the rule requires it.
What the level failure means, stated post hoc and labelled as such: the measured side is a *peak* level (Blackman's
230–240 dB re 1 µPa at 1 m) and the predicted side is a *spectrum* level (Pa²/Hz over an unstated analysis window), so
the −11 to −16 dB offset is a units mismatch of unknown size, not a measured error of the model; the pre-registration
should have declared the level test uninterpretable rather than binding. That is recorded as a lesson, not used to
re-grade. Sensitivities (not graded): each Fig. 2 shot alone moves the slope by ≤ 0.2 dB/oct and the level by ±3 dB;
equal gun weights ≤ 0.1 dB/oct; across-track sign ≤ 0.05 dB/oct.

**Consequence (as pre-registered for NOT EXPLAINED):** caveat **C1 is unchanged** and air9 absolute TL stays NOT
CALIBRATED in slope for any likelihood. What the module may say descriptively: the EW0112 source spectrum removes most of
the common-mode tilt (from about 9 to 1.2 ± 1.8 dB/oct), which supports the attribution of the tilt to the airgun source
spectrum rather than to the path, but this is fit-consistency on the training case and awaits an independent site or the
F-35A route. A proposal for the architect, not applied here: a re-registration of route 1 with a unit-consistent level
test (received level in matched units from Blackman's processing or from Kadri's archive) and the slope/shape rule alone
as the C1 criterion.

### Route 2 — F-35A spectral shape (Brown et al. 2026)

**NOT AVAILABLE from the paper.** The arXiv text of Brown et al. (2026; arXiv:2604.12723, 60 pp., retrieved 22 Oct
02:30 UTC; the module branch has no papers folder, so this is a declared substitution) contains no F-35A waveform or
spectrum figure: the F-35A appears only in the text (p. 17–18: 0.7 Pa peak at H11, 3,300 km, 900 ± 200 MJ; "one order of
magnitude in pressure amplitude above the local background", citing Metz et al.), and its figures are the bolide cases
(Figs. 5–8, C.9–C.16). The Digitisation track's folder (`results-data/digitised/brown2026/`) was polled every 30 min;
status at the final poll is recorded at the end of this addendum. Route 2 therefore cannot confirm or lift C1; the
remaining sources for an F-35A spectrum are Metz, Obana & Fukao (2023; closed access, waveform request pending) and the
Kadri (2024) S1 traces.

### (b) air8 negative control under the same source model — DESCRIPTIVE (outside the pre-registered condition)

The pre-registration ran step (b) only on an EXPLAINED or PARTLY EXPLAINED route 1; the computation had already run in
the same command, so it is reported, labelled descriptive. The source spectrum S0 cancels within a station; only the array
factor changes (air8 heading 106.9°, air9 111.2°), by ≤ 0.65 dB at H01W and ≤ 3.5 dB at H08S (50 Hz). Received-level
difference air8 − air9, 16–50 Hz, audit-builder sections for both sites, z_s 10 m: **H01W median −39.0 dB (FOLLOWS, ≤ −10)**,
**H08S median −1.2 dB (CONSISTENT, |·| ≤ 5)** → the control **still holds**; TL-only medians −38.8 / +0.5 dB, as before.

### (d) air7 → H01W, the ridge path (gap G22)

Source = shot-weighted mean of the two air7 segments (22.913°S 87.018°E), range 2,946 km, geodesic crest 1,199 m at
28.94°S 98.34°E; z_s 10 m; audit-builder sections; air9 → H01W on the same builder as the reference. Observed (Fig. 23 CL
panel, DIGITISED): TL(air7) − TL(air9) = −0.2 to −0.7 dB at 31.5–63 Hz.

![](hydroacoustics-air7-corridor-sensitivity.png)

| model, excess over the observed air7 − air9 difference, median 31.5–63 Hz | dB |
|---|---|
| single section on the geodesic | **+56.8** (43.6, 53.0, 60.5, 74.5 by band) |
| N×2D Fresnel corridor (nx2d.py, 17 members, all open, weights exp(−u²)) | **+55.3** |
| least-loss single path within ±20 km (3-D proxy; least loss at +20 km in every band, crest 1,420 m) | **+36.5** |
| exploratory extension (amendment 2): +30 / +40 / +50 km (crest 1,37x / 1,572 / 1,779 m) | +32.0 / +26.6 / +25.1 |
| coupled-mode (RAM) check on the geodesic and the +20 km path, 31.5 and 40 Hz | see the RAM line below |

**Verdict under the pre-registered rule: NOT REPRODUCED.** Neither the corridor nor any path within ±20 km comes within
10 dB; clearing the ridge altogether (+40 to +50 km, about seven Fresnel half-widths off the geodesic, which would need
horizontal refraction, not diffraction) still leaves about 25 dB. Where the remaining loss sits (TL against range on the
+50 km path): about 10 dB more than air9 inside the first 200 km from the source (the air7 site lies on the Ninetyeast
Ridge flank), about 15 dB across the 1,780–1,950 m sills at 1,300–1,700 km, and the receiver-end slope. Two readings are
open: (i) the adiabatic model overstates mode stripping at sills (RAM gave 18 dB where KRAKEN gave 39 dB on air8), so a
coupled or 3-D model is the next test; (ii) the observation may be a noise-selected ceiling — Fig. 23 plots the median
only over shots with signal more than 3 dB above noise, and Blackman call air7 at Cape Leeuwin weak in a noisier period,
so the plotted air7 TL is bounded above by SL − (noise + 3 dB) and "air7 ≈ air9" may partly reflect that bound.

**Proposed G22 status line (for the architect; ARCHITECTURE.md not edited here):** "G22 still open: air7 → H01W
single-section, N×2D corridor and ±20 km 3-D-proxy TL exceed the observed air7 ≈ air9 level by 57 / 55 / 37 dB (median
31.5–63 Hz); clearing the ridge (+40–50 km) still leaves ~25 dB; the observation may be a noise-selected ceiling.
Next: coupled-mode/3-D model, and Kadri's archive for the 2001 shots."

### COVERAGE
- **Feasible set** (what the calibration events can test): absolute received level, slope and shape of a near-surface
  source over deep SOFAR paths at 6.3–63 Hz (air9); within-station differences at 16–50 Hz (air8); ridge-crossing paths
  at 31.5–63 Hz (air7). The MH370 bands below 6.3 Hz and the AGW branch are outside every span (G2, G5 unchanged).
- **Model's reach:** KRAKEN adiabatic incoherent modes, flat hard half-space, no roughness, no mode coupling, no
  horizontal refraction beyond the Fresnel corridor; z_s 9–12 m; the EW0112 source for an airgun array only (an aircraft
  impact source is C2's domain).
- **Proposal's coverage:** 45 source–Ball geometries × 3 SL_B × 2 shots × 2 weightings × 2 signs for route 1 (all
  reported); 7 + 3 lateral offsets and one Fresnel corridor for air7; z_s 10 m only for (b) and (d) (declared).
- **Gaps and status:** G22 still open (above). Level test of route 1 uninterpretable (units) — new gap **G23**, declared:
  "absolute level of the EW0112 route needs a unit-consistent measured level". Route 2 not available (no F-35A spectrum
  in Brown 2026). C1 unchanged; C2 unchanged. No ESS applies (no sampled posterior enters this note).
- **Parameter bounds and sources:** Ball geometry EW0112 p. 5/7; layout OFR 95-228 Fig. 4; SL_B 230–240 Blackman p. 7;
  offsets ±20 km pre-registered, +30–50 km exploratory.

*Hydroacoustic Module (TL recalibration track), 2026-10-22.*
EOF
echo appended; wc -l hydroacoustics-blackman-validation.md