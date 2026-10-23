# Whale calls in the 8 March 2014 data: methods, validation and results

Track: hydroacoustics back to basics, whale calls (23 Oct 2026). Status: EXPLORATORY. No detection claim about MH370 is made here.
The purpose is to find whale calls so that they can be removed from (or kept apart from) the list of potential impact signals.

## Deviations and limits (read first)

1. **Royer 2016 panels: no call-level catalogue.** The template detectors gave the same score distribution on real and null
   templates on the digitised panels (99th-percentile real minus null between -1.8 and +1.5 dB for 19 of the 20 family x panel-type cells with detections; the one exception, +3.8 dB for the Omura's template on the coarse Fig. 2 panels, is not a plausible species at Cape Leeuwin; `validation_royer_kernels_real_vs_null_p99.csv`).
   The digitised grids (jet colour inversion clipped at 70-100 dB, about 1 Hz native resolution, JPX compression) do not resolve single calls
   for automatic detection. What was done instead: (a) whole-panel chorus test (26 Hz line) on all 34 panels; (b) a spectral test at each candidate
   time (17-28 Hz tonal excess against out-of-band excess) with a random-time base rate; (c) for OHASISBIO stations, the **published** SEANOE
   Z-call detections (made by Leroy et al. on the raw data) replace our own detection.
2. **Kadri Fig. 9 traces: frequency-blind.** Only duration and repetition can be tested. Species cannot be assigned. H08S is dominated by the
   9.98 s airgun train, so whale periodicities cannot be separated there. H08S candidates are "not assessable".
3. **Fin whale 20 Hz pulses** were searched (energy detector + inter-pulse-interval regularity) but almost none were found (18 short regular trains
   in 4,572 records, none on 8 March at Portland; interpretation open). No fin catalogue is reported; this agrees with the published seasonality
   (fin whales at Cape Leeuwin from April, Perth Canyon May-October; Aulich et al. 2019).
4. **No detectors** were built for humpback, southern right, sei, Bryde's, Antarctic minke (bio-duck, > 50 Hz, winter) or pygmy blue D-calls
   (short downsweeps). These are out of season or outside the 5-45 Hz candidate bands; two unexplained Portland candidates with
   biological-like character are listed as "unidentified".
5. **Manual validation** is a visual check of random spectrogram crops at modest display resolution (`validation_manual_review.csv`, 6 crops per
   class, 15 classes); precision values are approximate.
6. **Site caps.** After manual review, call types that were not confirmed at a site are capped at "low" (listed in `build_catalogue.py`, CAPS):
   Omura's whale outside Scott Reef, pygmy blue at Scott Reef, Antarctic blue Z-call at all IMOS sites, and the 'Chagos' and Madagascan types everywhere.
7. **Clock.** IMOS UTC uses the module's convention A (true = logger - e(t)), verified by the module clock test (dA = -0.24 s on the Curtin
   01:33:44 control). Royer figure times may carry an unexplained +13.1 +/- 3.4 s offset against Royer Table 5 (potential-signals v3 README);
   whale-call extents (10-40 s) are longer than this, but coincidence calls within 15 s of a call edge depend on it.
8. **Records excluded:** 5 of 4,572 IMOS records (defective, very low level; `run_summary.json`). The 'S' (signal-window) records were
   **included**: the purpose of this track is to classify what is in them.

## Data used (all found locally or online; no stand-ins)

| Input | Where | Check |
|---|---|---|
| IMOS raw records 8 Mar 2014, loggers 3315, 3376 (Perth Canyon), 3250 (Scott Reef), 3274, 3275 (Portland) | `~/Downloads/mh370-inputs/hydroacoustics/imos/{MH370,Portland_MH370}` | 540 records, as in module `data/imos/recordings.csv` |
| IMOS 14-day backgrounds 1-15 Mar 2014 (3250, 3274, 3376; 8 Mar excluded) | `.../imos/background/<logger>/<yyyymmdd>/` | 4,032 records (96/day x 14 days x 3) |
| Calibration (gain files, sensitivities, clock entries) | `.../MetaData*.txt`, `.../*alibration/` | module chain (`imos_noise.py`) |
| Royer 2016 report spectrogram grids | `digitise_royer_2016.py` re-run on the report PDF (artifact) | 34 panels |
| Kadri 2024 Fig. 9 vector traces and Table 1 | repo `Archive ISO Pre Sept 28/.../kadri-figure-extraction/figure9-vector-traces/`, `kadri-table1-transients.csv` | 5 panels, 19 transients |
| Royer Table 5 arrivals | repo `digitised/royer-2016/royer_arrivals.csv` | 143 picks |
| Module ranked singles (22 Oct) | repo `ranked_candidates/ranked_singles.csv` | 184 rows |
| Potential signals v3 (current product) | `~/Downloads/mh370-exchange/hydroacoustics/potential-signals-2026-10-23-v3/` tables 1-2 | 121 sets (260 members), 73 singles |
| Blackman 2003 noise (H01W, H08S, H08N) | repo `blackman_noise/blackman_noise_summary.json` | third-octave medians |
| SEANOE 46124 and 51007 | downloaded (see DOWNLOADS.md) | 8 Mar 2014 covered |

## Detectors (code: `code/whale_detectors.py`, reusable on any dB spectrogram)

Spectrogram: 250 Hz data, Hann 1024 (4.1 s), 0.5 s step, 0.244 Hz bins, 5-120 Hz, calibrated to dB re 1 uPa^2/Hz. Noise normalisation
by the per-frequency 25th percentile of the record; linear smoothing over 2.5 s; **flank contrast** = mean level within +/-0.35 Hz minus the
lower of the two flank rings (0.9-1.6 Hz above and below). Flank contrast removes broadband energy (impacts, airguns, ships' bursts) so a
broadband transient does not score as a tonal call. A broadband index (85-120 Hz) rejects detections that sit on broadband events (> 9 dB).

Kernel (template) detectors: mean flank contrast along a piecewise-linear contour (fundamental and harmonics), maximised over a grid of
frequencies/durations that spans the published variability, with every part of a multi-part call required to be present (weakest
component >= 1.5 dB). Templates (frequencies for March 2014):

| Family | Contour | Source |
|---|---|---|
| PB_SEIO_II pygmy blue (Australian song) unit II | upsweep from 19.5-21.5 Hz by +2 to +3.5 Hz over 18-28 s; harmonics 1 and 3 | Gavrilov 2011; Jolliffe 2019 |
| PB_SEIO_III unit III | flat 17.25-19.75 Hz, 22 s; harmonics 1-3 | Jolliffe 2019 |
| PB_SEIO_I unit I | 18 s tone at 18.5-20 Hz, then +1 to +1.75 Hz step for 19 s; harmonics 1-2 | Jolliffe 2019 |
| ABW_Z Antarctic blue Z-call | 8 s at 25.75-26.45 Hz, 1.5 s downsweep, 8 s at 18.5-19 Hz | Leroy 2016; SEANOE 51007 (26.02-26.09 Hz on 8 Mar 2014) |
| OMURA_TONE Omura's whale (Australian song) tonal end | 3.3 s at 24.75-25.5 Hz, then 4.9 s at 19.8 Hz | Leroy 2021 Fig. 6d |
| CHAGOS 'Chagos' song unit 1-2 | 29.5-31 Hz down-tone, then 23 Hz tone | Leroy 2021 (+1 Hz for 2014 vs 2017) |
| PB_SWIO_U1 Madagascan unit 1 | 33.5-34.3 Hz, 12 s | SEANOE 51007 (33.9 Hz in March 2014) |

Pulse detectors (0.512 s windows): fin whale 20 Hz pulses (15-30 Hz vs 35-45 Hz, 0.4-2.5 s, regular trains with IPI 7-26 s), fin upper
component (92-100 Hz), Omura's noisy pulsed units (20-45 Hz vs 50-60 Hz, 2.5-9 s).

Song structure: pygmy blue unit order and spacing (II->III 38-62 s, I->II 38-60 s) and inter-song intervals (P3 165-210 s, P2 80-100 s, P1 43-52 s);
Omura's noisy pulsed unit within 12 s before the tonal end; Z-call repeats 40-80 s.

## False-alarm estimate and confidence

**Target-decoy.** Every record is also scanned with null templates: time-reversed contours for swept calls and contours shifted in frequency
(+8 to +13 Hz, or -5.5 Hz) for flat tones. For each family and site, q(s) = monotone minimum of N_null(>= s)/N_real(>= s) over all 4,567
records (event day + backgrounds); `fa_per_h` = N_null(>= s) / recorded hours (Perth Canyon 131.4 h, Portland 134.9 h, Scott Reef 123.2 h).
The nulls also catch real calls of other types (for example pygmy blue song under a reversed template), so q is conservative where whales are many.

**Confidence.** high = q <= 0.05 and song structure; medium = q <= 0.05, or q <= 0.2 with structure; low = q <= 0.5 (limit of detectability; kept
on purpose). Cross-family overlaps (>= 40 % of the shorter call) keep only the stronger family. A record with >= 2 high-confidence calls of one
species sets lower confidence ('off-context') on weaker calls of other species in that record.

**Injection-recovery** (synthetic calls added to 450 Portland background records, threshold = Portland null 99.9th percentile score):
50 % detection at in-band SNR (signal power / noise power in 1 Hz) of 2.2 dB for pygmy blue unit II (0.018 false alarms per hour),
6.5 dB for the Antarctic blue Z-call (0.050 per hour), 8.5 dB for the Omura's tonal end (0.112 per hour) (`validation_injection_*.csv`).

**Manual review** (`validation_manual_review.csv`): pygmy blue unit II at Perth Canyon judged true in 5/6 high, 3/6 medium, 2/6 low; Portland 6/6,
5/6, 2/6; Omura's tonal end at Scott Reef 6/6, 6/6, 4/6. 'Chagos' (0/6), Z-call at Scott Reef (0/6) and Portland (0/6), pygmy blue unit I at Scott
Reef (0/5) and Omura's at Perth Canyon and Portland (0/5 each) were not confirmed: those types are capped at low.

## Results

**IMOS 8 March 2014 (`whale_call_catalogue_imos_8mar2014.csv`, 2,728 unit detections, 1,125 high/medium):**
- Perth Canyon 3315 and 3376: south-east Indian Ocean pygmy blue whale song all day (3315: 233 high + 120 medium; 3376: 262 high + 123 medium
  unit detections); full P3 phrases (units I, II, III, about 190 s cycle).
- Scott Reef 3250: Omura's whale song (Australian song type, Leroy et al. 2021 recorded it at this site in March 2013), many overlapping singers
  (high: 49 tonal ends + 160 noisy pulsed units; medium: 133 + 45).
- Portland 3274 and 3275: no high/medium calls on 8 March (pygmy blue unit II occurs on other days: 13 high + 26 medium in the 14-day background).
- Antarctic blue whale Z-calls are not resolved as single calls at any IMOS site; the chorus is present (26 Hz line).
- Backgrounds (`whale_call_catalogue_imos_backgrounds.csv.gz`, 29,060 rows): same picture on every day (Perth pygmy blue, Scott Reef Omura's).

**OHASISBIO stations (published SEANOE detections):** Antarctic blue Z-calls on 8 March 2014 at MAD 91, NCRO 43, SSEIR 82, SWAMS 57, WKER 414;
in 00:00-02:00 UTC: 6, 1, 3, 1, 54. Week 10 also had the Australian pygmy blue type (SSEIR, SWAMS), the Madagascan pygmy blue type (SSEIR, NCRO,
WKER, SWAMS) and the fin whale 96 Hz pulse (WKER).

**Royer panels, 26 Hz lines (`royer_26hz_lines.csv`, Fig. 3b):** all 34 digitised panels (7 stations) have a median-spectrum peak between
25.74 and 26.86 Hz (median 26.11 Hz), 1.1-5.8 dB above 22.5-24.3 / 28-30 Hz. The published unit-A frequency for 8 March is 26.02-26.09 Hz, and the
strongest line is at WKER (5.8 dB), the station with by far the most Z-calls that day (414). The 26 Hz lines are the Antarctic blue whale chorus.
(The H01W-2 peaks sit 0.4-0.7 Hz higher than the OHASISBIO peaks; a frequency-axis calibration offset in the digitised H01W panels is possible.)

**Blackman 2003 17-27 Hz excess (Fig. 3a):** against a log-linear fit through the bands outside 14-28 Hz, H01W (May-June 2003) has +5.5, +7.6
and +5.3 dB in the 16, 20 and 25 Hz third-octaves and |residual| <= 0.8 dB elsewhere; H08S +1.1, +2.0, +1.0 dB; H08N none. A band-limited excess
in exactly the baleen-whale band (Antarctic blue units A/B and downsweep 18-28 Hz, fin 15-30 Hz, pygmy blue 17-25 Hz), in the season with most
Antarctic blue chorus at Cape Leeuwin (Feb-Oct, Gavrilov et al. 2012) and with fin whales arriving from April (Aulich et al. 2019), is the
signature of whale chorus. It should therefore not be carried into the 8 March 2014 noise model as ambient noise: the March 2014 H01W-2 spectrum
(Royer) does not have it (previous noise track: agreement within about 1 dB except this peak).

**Kadri traces (`kadri_trace_periodicity.csv`, `kadri_trace_envelope_events.csv`):** H01W panels a-c have few envelope events above 3 dB (7 in
30 min) and no autocorrelation peak at the pygmy blue (P1/P2/P3) or Z-call intervals (all <= 0.10). Panel a has a 10 s periodicity (0.29),
like the H08S airgun train (0.73-0.85 at 10 s). The one long event (00:51:58-00:52:06, 8 s) is broadband on Royer H01W-2 (17-28 Hz +4.7 dB,
outside +4.3 dB), so not a whale call. What cannot be concluded: species, and whether any low-level whale song lies under the trace noise.

**Candidate cross-check (`candidate_crosscheck.csv`, Fig. 2):**

| List | explained | possibly | coincides (Z-call overlap) | not explained | not assessable |
|---|---|---|---|---|---|
| Kadri 2024 Table 1 (H01W, 19) | 0 | 0 | 0 | 19 (10 no clear excess, 9 broadband on Royer H01W-2) | 0 |
| Royer Table 5 arrivals (143) | 0 | 0 | 1 (event 16, SSEIR 02:08:46, 23.7 s after a published Z-call) | 133 | 9 |
| Module ranked singles (184) | 16 (15 Scott Reef, Omura's song; 1 Perth Canyon 3376 00:38:03, pygmy blue unit II) | 29 (28 Scott Reef) | 0 | 92 | 47 (H08S) |
| Potential signals v3 table 1 (260 members) | 0 | 0 | 0 | 145 | 115 (H08S) |
| Potential signals v3 table 2 (73) | 1 (S068, 3376 00:38:03) | 0 | 0 | 37 | 35 (H08S) |

- In the current products (v3), only **S068 (Perth Canyon 3376, 00:38:03, 20-40 Hz)** is explained by a whale call (pygmy blue unit II,
  00:37:40-00:38:08, high confidence). The 31 Perth Canyon 3315 members (00:45:44, 00:49:48) sit in records with pygmy blue song but the
  call does not account for the candidate energy (manual review).
- The top single-site candidate **S001 (Portland 3275, 01:20:34-35)** is not one of the catalogued whale calls, but it is a **tonal** signal
  (steady 26.9 Hz for about 12 s plus 38.6 Hz), biological-like and not an impulsive broadband pulse (Fig. 1e). This character argues against
  an impact origin and should be considered by the ranking.
- Portland 3275 01:07:46 is a short broadband multi-pulse transient (not whale). Portland 3275 01:36:47 is diffuse 35-70 Hz energy of unidentified type.
- At Cape Leeuwin, none of the 19 Kadri Table 1 transients and none of the H01W members of the v3 tables shows a whale-band tonal excess on
  Royer H01W-2 (random-time base rate of that class 0.2 %).
- The Royer arrivals at OHASISBIO stations are not explained by Z-calls (1 overlap in 86, consistent with chance: about 3 % per pick at SSEIR).
  Royer icequake A at WKER (00:42:04.65) falls between the published Z-calls at 00:40:42.8 and 00:42:59.0.

## Files

See README.md for the file list. Code: `code/imos_io.py` (I/O, calibration, clock), `code/whale_detectors.py` (detector feature set),
`code/make_event_spectrograms.py`, `code/process_imos.py` (one pass per record, sharded), `code/build_catalogue.py` (q-values, confidence,
catalogue), `code/crosscheck.py` (candidate cross-check).

## Re-use on the deskstar spectrogram cubes

`whale_detectors.run_templates(L, f, t, bank, null=...)` takes any dB spectrogram [f, t] with uniform axes. For cubes with other resolution set
`contrast_kw` (e.g. half_bw about 1.5 bins, flank rings about 3-6 bins) and keep the null run for the target-decoy q-values; `pulse_events` and
`regular_train` take a short-window spectrogram. `process_imos.template_rows` shows the per-record call pattern.
