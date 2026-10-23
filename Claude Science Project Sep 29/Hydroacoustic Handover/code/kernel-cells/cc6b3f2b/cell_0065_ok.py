
T = json.load(open("handoff/note_tables.json"))
S = T["S"]; ks = T["ks"]; TB = T["TB"]
note = f"""# Hydroacoustics — weak-signal method trials (work order 2026-10-21, block 8; brief Refresh v2 §7)

**Status: DONE as a method trial; PREDICTIVE, NOT CALIBRATED. No detection is claimed.** Every number below carries
caveat C1 (propagation slope misfit, +10.4/+7.4 dB per octave at H01W/H08S) and C2 (coupling efficiency not
calibrated; η swept over four decades, F-35A upper anchor). The Kadri Fig. 9 traces are DIGITISED plots (PDF vector
polylines, ~14.5 vertices/s, envelope resolution), not recordings. Both Kadri times are carried everywhere: text time
00:52:03 and caption time 00:54:30.

Pre-registration: module branch commit `78c7e88` (`prepare/weak_signal/preregistration.py`), committed before any
statistic on data. Amendment 1 (SNR grid 15–30 dB, `run_injection_ext.py`) is disclosed below. Code:
`engine/hypotheses/hydroacoustics/prepare/weak_signal/` (module branch). Data products:
`/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-weak-signal/` (17 MB, SHA256SUMS). Thread budget 3 processes;
total compute about 12 minutes (templates 33 s, null + injections {S['seconds']['total']} s, extension {T['E_seconds']} s, panels {ks['seconds']} s).

## 1. Summary

1. On real IMOS background (Perth Canyon 3376, 14 days, 5,376 null windows of 60 s), **the two dispersion-aware
   matched filters reach P_D = 0.5 at SNR ≈ 7 dB** (α = 0.01 per 60 s window), against 13–16 dB for the STA/LTA
   baseline and 27–28 dB for the band-energy baseline: a 6–9 dB gain over STA/LTA, about 20 dB over band energy. At
   α = 0.001 only the matched filters reach P_D = 0.5 at all (envelope 16–19 dB, waveform 24–25 dB; STA/LTA P_D ≤ 0.24
   at 30 dB). **This is the model-matched best case**: the injected pulses were made with the same KRAKEN propagation
   model as the templates (declared in the pre-registration). The gain is the shape test: a 50 s dispersed arrival does
   not look like the loud local transients (ships, fish, whales) that fill the null's upper tail.
2. Spectral kurtosis is equivalent to STA/LTA (SNR_50 13–15 dB at α = 0.01). Cepstral fingerprint, time-domain
   kurtosis, synchrosqueezed concentration, Bayesian change-point and stochastic resonance **failed** as implemented
   (P_D ≤ 0.17 at 30 dB): negative results, kept in the code behind the method table (not deleted).
3. Two-station envelope stacking at a known lag (idealised, same SNR at both loggers) reaches only P_D = 0.27 at
   +10 dB (α = 0.01): stacking band-level z-scores from two heavy-tailed backgrounds does not beat one shape test.
4. On the digitised H01W panels, **only the envelope matched filter reaches p = 0.05 inside an author's box**: at the
   text time 00:52:03 (panel c, p = 0.052, label *mark*). The caption time 00:54:30 gives p = 0.16 (screen). The four
   poster panel-(a) boxes stay at p ≥ 0.08 for every method (best: Bayesian change-point in box 1, p = 0.080, *mark*).
   The cepstral statistic marks three unlabelled times in panel b (Kadri's "no signal" panel) at p = 0.002–0.021; with
   nine methods on 50 minutes of trace, chance gives about two such values, and this method had no power in test (a).
   On H08S (panels d, e) the kurtosis statistics fire on the airgun shots throughout (46 *report* rows): the IMOS
   emulated null does not represent a shot-dominated record, so those rows are **null-mismatch artefacts**, listed but
   not candidates.
5. H08S airgun suppression on the digitised panels: shot-template subtraction lowers the residual energy by 5.8 dB (d)
   and 4.7 dB (e); with cadence gating (30 % of time removed) 7.6 and 5.3 dB. It cuts the chance rate of a z ≥ 3 peak
   within ±2 s of a random time from 0.40–0.62 to 0.00–0.20, while an injected deep-channel arrival 4 dB below the median
   shot peak is still found in 0.88 (d) / 0.50 (e) of trials (0 dB: 0.98 / 0.92). Below −8 dB it is not recovered.
   36 residual peaks survive at z ≥ 3; 9 of them fall in the lag windows of the two Kadri H01W times (table below), all
   carried as screen-level rows with labels, none as a claim.
6. Recommendation for the main pipeline (§7): add the dispersion-aware **envelope** matched filter as the primary
   screen statistic beside STA/LTA (it is the only method that keeps power at α = 0.001 and it is robust to phase),
   with the waveform matched filter as a secondary at α = 0.01; calibrate its threshold on the real background of each
   receiver as here; and test it on a non-model-matched ground-truth case before any MH370 statistic (gap G-W1).

## 2. Test set (a): synthetic impact pulses in real IMOS background

**Design (as pre-registered).** Background: IMOS public-bucket days 1–7 and 9–15 March 2014 (8 March excluded; it holds
the MH370 windows). Primary target 3376 (Perth Canyon): all 1,344 files (0 unreadable). Secondary 3274 (Portland) and
3250 (Scott Reef): every 4th file (336 each). Series: module `imos_noise.read_volts/decimate` (500 Hz), 5–40 Hz
4th-order Butterworth zero-phase, decimated to 100 Hz. Null: statistic maxima over non-overlapping 60 s windows from
32 s; thresholds = null (1 − α) quantiles, α ∈ {{0.01, 0.001}} per window ({S['n_null_windows']['3376']} windows at 3376, so the 0.001
quantile rests on the top ~5 values; {S['n_null_windows']['3274']} at each secondary target, where 0.001 is at the resolution floor).
Pulse: one-pole source (ESD flat to 1/τ, f⁻² above; the module's `band_fraction` model), τ ∈ {{0.1, 1, 10}} s, convolved
with a KRAKEN coherent broadband channel (2–48 Hz, step 1/64 Hz, {TB['n_freq']} frequencies, {TB['n_modes_min']}–{TB['n_modes_max']} modes; WOA23 March profile at the
path midpoint 36.6°S 102.2°E of the run J seed-1 weighted-median impact (37.07°S 89.85°E) → H01W, extended below
4,800 m holding SA and CT; flat bottom at the path's median GEBCO 2026 depth 4,610 m; module 'hard' half-space;
Francois–Garrison; source 10 m, receiver at the channel axis 1,200 m). Of the two time conventions the one whose energy
builds to an abrupt end (the deep-sound-channel crescendo) was taken as physical; 50 s templates with the peak at 35 s.
Injection ranges on a 25 km grid over 1,800–3,000 km; template bank at 1,800, 2,200, 2,600, 3,000 km × 3 τ (12
templates), so a range mismatch of up to 200 km exists. SNR = peak 1 s 5–40 Hz level of the pulse minus the target's
background median 1 s level (3376: {S['bg_median_level_db']['3376']:.1f} dB re V²). N_INJ = 120 per (SNR, τ) cell at 3376, 60 at the secondary
targets; seed {S['seed']}. Stochastic-resonance constants set on the first 20 background files (k = {S['sr']['k']}, σ = {S['sr']['sigma']}; background
switch rate {S['sr']['rate']:.2f} per s — the pre-registered target of 1 per s was not reached on the grid, disclosed). Cepstral band Q =
{S['q_band'][0]:.2f}–{S['q_band'][1]:.2f} s.

**Amendment 1 (disclosed, not pre-registered).** The pre-registered SNR grid (−15 to +10 dB) ended before the baselines
and most trial methods reached P_D = 0.5, so their SNR_50 was unidentified. The same design was re-run at 15, 20, 25,
30 dB (seed 20261023), thresholds unchanged; fits below use the union grid. The pre-registered P_D values stand.

**Null thresholds at 3376** (statistic units; per 60 s window):

| method | α = 0.01 | α = 0.001 |
|---|---|---|
{T['thrtab']}

**SNR_50 (dB) at 3376** from a logistic fit on the union grid; "not reached" = P_D never crossed 0.5 by 30 dB:

| method | α 0.01, τ 0.1 s | α 0.01, τ 1 s | α 0.01, τ 10 s | α 0.001, τ 0.1 s | α 0.001, τ 1 s | α 0.001, τ 10 s |
|---|---|---|---|---|---|---|
{T['tab1']}

**P_D at 3376, τ = 1 s, α = 0.01** (120 trials per cell; −15…+10 dB pre-registered, 15–30 dB amendment 1):

{T['pd_3376_01']}

**P_D at 3376, τ = 1 s, α = 0.001:**

{T['pd_3376_001']}

**Secondary targets, τ = 1 s (SNR_50, dB):**

| logger | method | α = 0.01 | α = 0.001 |
|---|---|---|---|
{T['sec']}

Scott Reef 3250 has the heaviest null tail (its STA/LTA 0.01 threshold is 206 in stage A); only the matched filters
reach P_D = 0.5 there, at 24–26 dB. Portland 3274 is the quietest: envelope matched filter SNR_50 = 2.3 dB (α 0.01).

**Two-station envelope stacking (M2), 3376 + 3274 at the same SNR, known lag, ±30 s search, 60 trials per cell:**

{T['m2tab']}

**Verdicts (pre-registered rule: better = SNR_50 at α 0.01 at least 2 dB below the better baseline with
non-overlapping Wilson intervals at the baseline's SNR_50):**

| method | principle | free parameters (fixed in prereg) | FAR control | verdict at 3376 |
|---|---|---|---|---|
| M0a STA/LTA | energy ratio, 2 s / 30 s | STA, LTA | null quantile | baseline (SNR_50 13–16 dB) |
| M0b band energy | 1 s band level over preceding-60 s median, 3 s mean | bands, memory | null quantile | baseline (28 dB); worst |
| M1a matched filter, waveform | normalised cross-correlation with 12 KRAKEN dispersed templates | bank ranges, τ, template length | null quantile | **better** (−7 to −9 dB vs STA/LTA; α 0.001 reached) |
| M1b matched filter, envelope | as M1a on the 0.5 s squared envelope at 10 Hz | as M1a | null quantile | **better** (−6 to −8 dB; best at α 0.001) |
| M2 two-station stacking | z(band level) summed at predicted lag | lag search ±30 s | pair null | worse than M1 (P_D 0.27 at +10 dB) |
| M3 cepstral fingerprint | cepstral energy fraction in Q, z vs preceding 60 s | segment 8 s, Q | null quantile | **failed** (P_D ≤ 0.17 at 30 dB) |
| M4a spectral kurtosis | Antoni SK, 1 s STFT, 8 s blocks, 5–40 Hz mean | block, hop | null quantile | equivalent to STA/LTA (13–15 dB) |
| M4b time kurtosis | excess kurtosis, 2 s frames | frame | null quantile | failed (≤ 0.12) |
| M5 synchrosqueezed concentration | top-5 % energy fraction of SST, z vs preceding 60 s | block, top fraction | null quantile | failed (≤ 0.12); ssqueezepy 0.6.6 |
| M6 Bayesian change-point | Adams–MacKay on 1 s band level, hazard 1/120 | prior, hazard | null quantile | failed (≤ 0.04) |
| M7 stochastic resonance | bistable well switching rate | k, σ | null quantile | failed (≤ 0.01); exploratory |

Why the failures: M3, M5 and M6 are z-scored against the preceding 60 s and the null's upper tail (loud local
transients) already saturates them; M6's change probability is near 1 at every transient; M7's switching rate is
set by the normalised series and is insensitive to a slow 50 s energy ramp. They are kept in `methods.py` as
negative results.

## 3. Test set (b): the digitised Kadri Fig. 9 traces

**These traces are decimated plots** (panels a, b, c: 8,706 / 8,722 / 8,716 vertices over 600 s; d, e: 8,936 / 8,974),
resampled to 20 Hz and band-passed 1–9 Hz; the matched filter uses the template envelope only (2,200 km for H01W,
3,704 km for H08S). Null: IMOS 3376 background passed through a plot-decimation emulator (per 69 ms bin the min and
max as vertices, 20 Hz), {ks['n_null_files']} files × 4 windows of 60 s. p = fraction of null window maxima ≥ the statistic.
Labels: report p < 0.05, mark p < 0.1, screen p < 0.3 (ruling 13 Oct). Chance alone gives about one p < 0.05 value per
20 minutes of trace per method, so with nine methods on 50 minutes a handful of *report* rows is the expectation.

**Counts of candidate rows (local maxima with p < 0.3) by method and station:**

{T['cnt_lines']}

The H08S counts for spectral and time kurtosis (46 *report* rows) are the airgun shots: the emulated IMOS null has no
10 s shot train, so the null is mismatched for H08S and these rows are not candidates. Full list:
`run-j-weak-signal/kadri/candidates.csv` ({T['n_cands']} rows, {T['n_h08_cands']} of them H08S).

**H01W candidate rows ranked by p (top 25 of the screen-level list):**

{T['h01tab']}

**Author's boxes: the smallest p inside each box, per method** (the test the work order asked for):

{T['bxtab']}

Reading: at the text time 00:52:03 the envelope matched filter gives p = 0.05 (mark) and STA/LTA p = 0.44; at the
caption time 00:54:30 the best is the Bayesian change-point at p = 0.11 and the matched filter at p = 0.16 (screen);
the four panel (a) boxes reach p = 0.08 at best (change-point, box 1) and are otherwise screen-level or below. The
21 Oct review diagnostic (fixed STA/LTA ratio 4.69 at 00:52:03, 2.38 at 00:54:28, panel (a) maxima 1.7–2.7) is
consistent with these p-values on the same traces. A fixed single-station threshold would remove every box; under the
screen-level stance they are all carried as rows with their labels.

**Two-station stacking across the panels (H08S − H01W lag 855.93–1346.50 s, 1 s steps):**

{T['m2tab_k']}

Every top pair lands on the same H08S second, 01:09:00 (540 s into panel d), which lies 0.9 s from the shot grid
(cadence 9.95 s, phase 1.83 s): a loud on-cadence airgun shot, not an independent second-station event. The pairs are
therefore driven by one H08S feature and carry no coincidence information; they are listed for completeness only.

## 4. Test set (c): H08S airgun suppression

Panels d, e at 40 Hz (as `h08s_shot_outliers.load`); envelope p² smoothed 0.25 s; shots by the `h08s_pulse_energy`
rule ({int(T['suptab'].split('|')[9]) if False else '64 and 52'} shots). (c1) Local median template of up to 12 neighbouring shots over [−3, +6] s, scaled to the
shot's peak, subtracted. (c2) Cadence = median 9–11 s interval, phase = circular median; ±1.5 s gated (30 % of time).
(c3) Off-cadence flag = phase distance > 2 s.

{T['suptab']}

**Candidate energy surviving (z ≥ 3 against the median/MAD of the raw envelope in shot-free gaps):**

{T['survtab']}

**Survivors after (c1)+(c2)** (lag-consistent = inside [t₁ + 855.93, t₁ + 1346.50] s for a Kadri H01W time t₁):

{T['s12tab']}

The surviving rows are what a shot-suppressed H08S scan would hand to the coincidence test. Nine lie in the lag
windows of the Kadri times (01:07:03–01:09:57 for the text time, 01:08:54–01:16:41 for the caption time); 5 of those 9
are off-cadence. None is a claim: on a decimated plot the residual misfit of the template itself produces peaks, and the
null for this residual is unknown (gap G-W3). With raw H08S triad data the same procedure applies to full waveforms
and three elements, and the residual null can be measured on adjacent survey hours.

**Recovery of the module's H08S-range template envelope injected into the panels (40 onsets per level):**

{T['iptab']}

"Chance" is the same rule at the same time with nothing injected. Suppression lowers the chance rate by 3–5× and keeps
recovery at ≥ −4 dB relative to the median shot peak; at −8 dB recovery is marginal (0.40 vs 0.10 chance at d) and
below that absent. About a quarter of injected peaks fall inside the gate and are lost by construction.

## 5. COVERAGE

- **Feasible set.** Impact source: the module's source model (one-pole ESD, τ 0.05–10 s; brief §"impact source
  interface"), coupling η over four decades (C2). Propagation: deep-sound-channel arrivals over 1,500–3,700 km with
  modal dispersion of 20–40 s; AGW branch (not touched here). Receivers: IMOS 3315/3376/3250/3274/3275 (single
  hydrophones, 307 s records every 15 min), IMS H01W/H08S/H08N triads (raw data not held).
- **Model's reach.** Templates: one range-independent KRAKEN profile (WOA23 March midpoint, flat 4,610 m), receiver at
  the channel axis (1,200 m) while the IMOS loggers sit at 400–500 m; τ ∈ {{0.1, 1, 10}}; ranges 1,800–3,000 km. Not
  reached: bathymetry-following paths, the H08S path's 3,704 km other than as one envelope, receiver depth of the
  loggers, AGW arrivals, bearing (single hydrophones). The injected pulses share the template model (model-matched).
- **Proposal's coverage.** Null: 3376 full (5,376 windows), 3274 and 3250 at stride 4 (1,344 each); SNR −15…+30 dB in
  5 dB steps; 120/60 trials per cell (Wilson intervals ±0.09 at P_D 0.5, n = 120). Panels: five digitised panels only.
- **Gaps.** G-W1 (open): no non-model-matched ground-truth test — the brief's San Juan / F-35A / Blackman shots need
  digitised waveforms (block 1) or raw records; until then the matched-filter gain is an upper bound. G-W2 (open):
  the panel null is an emulation from one IMOS site; it is mismatched for the shot-dominated H08S panels. G-W3 (open):
  no null for the H08S suppression residual. G-W4 (declared): secondary-target nulls at stride 4 put α = 0.001 at the
  resolution floor. G-W5 (declared): stochastic-resonance background rate 0.92 per s, not the 1 per s target. G-W6
  (declared): the two-station test is idealised (equal SNR, known lag). ESS is not applicable (no weighted samples).
- **Parameter bounds with sources.** τ from the module's `TAU_GRID` 0.05–10 s (brief); ranges from the run J median
  impact to H01W (2,198 km) ± the bank span; band 5–40 Hz (Kadri's chain, Refresh §5); SNR grid chosen to bracket the
  stage A result (SNR_50 12.6 dB at α 0.05 for D1 at 3376).

## 6. Deviations from the work order

- The ground-truth cases named in the brief (San Juan, F-35A, Blackman shots) were not run: their digitised waveforms
  are block 1's deliverable, which was not available to this track overnight. Test set (a) used synthetic pulses as the
  work order specified; the real-transient templates T_C1/T_C2 of stage A were not added (they are Perth-Canyon
  recordings of unknown source and would not carry a known dispersion).
- Secondary targets at file stride 4 (declared in the pre-registration), N_INJ 60 rather than 120.
- The pre-registered stochastic-resonance target rate was not reached on the fixed grid (0.92 per s).
- The SNR grid was extended after the first run (amendment 1).
- All methods run at 100 Hz (STA/LTA is therefore a 100 Hz variant of the module's D1), declared in the pre-registration.

## 7. Recommendations for the main search pipeline

1. Add the dispersion-aware envelope matched filter (M1b) as the primary screen statistic, STA/LTA beside it; set the
   thresholds per receiver on its own real background exactly as here (null of 60 s window maxima).
2. Build the template bank per receiver from the module's bathymetry-following KRAKEN paths (not the flat profile used
   here), at the receiver's depth, over the run J range span, τ from the `tau90` sidecar; keep a 200 km range step.
3. Before any MH370 statistic, close G-W1: run M1a/M1b on a real long-range arrival with a known source (block 1
   digitisations, or the stage A Curtin events once their sources are identified) and report the loss of gain against the
   model-matched case.
4. For H08S, apply (c1)+(c2) before the screen and report the residual null from adjacent survey hours; carry the
   off-cadence flag with every H08S row.
5. Drop M3, M5, M6, M7 from the pipeline; keep them in the code as negative results behind the method table.

## 8. Charts

- `hydroacoustics-weak-signal-pd-vs-snr.png/.pdf` — P_D against SNR per method, 3376, two false-alarm rates, three τ.
- `hydroacoustics-weak-signal-kadri-panels.png/.pdf` — panels (c) and (a) with every method's p-value trace and the boxes.
- `hydroacoustics-weak-signal-h08s-suppression.png/.pdf` — H08S envelopes before/after suppression, detail, recovery.

Signed: Hydroacoustic Module (weak-signal track, unattended), 22 Oct 2026.
"""
open("hydroacoustics-weak-signal-methods.md","w").write(note); print(len(note))
