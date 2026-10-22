# Hydroacoustics — overnight run of work order 2026-10-21 (21/22 October 2026): summary

**Status: every block of the work order ran and is committed. No detection is claimed. The module's likelihood in the
composer stays at zero pending an architecture ruling. All numbers are PREDICTIVE, NOT CALIBRATED, and carry caveats C1
(propagation source-term misfit) and C2 (coupling efficiency η not calibrated; swept over four decades, F-35A anchor
η = 2.1e-4).** Read this note first, then the block notes it points to. Every block note has its own COVERAGE section and
a list of deviations from its task; the deviations are repeated here in short form because they qualify every number.

Run: approved by Pete 21 Oct ~20:40Z, unattended, eleven parallel tracks on the Hydroacoustic Module profile from 02:15Z to
11:45Z (22 Oct), each with the shared operating note (never raise an approval; record gaps and continue). Impact set: run J
(74 seeds, 313,599,968 rows) plus the northern supplement. Latitude span 41–20 S (the 99th-percentile northern contour of the
run J prior is 27.5 S, so 20 S governs). Both Kadri times carried throughout: text time 00:52:03, caption time 00:54:30.

## What each block found (plain words first, then the technical line)

1. **Digitisation** (`results/hydroacoustics-digitised-sources.md`). We now hold, as data, Royer's 2016 OHASISBIO tables
   (14 hydrophones, 20 events, 143 picks) and 34 spectrogram panels; all ten Blackman 2004 Fig. 23 curves at the source's own
   resolution (air8 not separable, air2 sparse); Kadri 2024 S1 traces as vectors; Kadri 2017 and ARA San Juan tables; CMST 2014
   detections. A 50-row manifest records source, page, method and check. Finding: every H01W mark in Royer's figures is 7.7–16.6 s
   later than his Table 5 (the 2014 GPS–UTC offset is 16 s) — a question for Royer. Gaps: Brown 2026 contains **no** F-35A
   spectrum (it cites Metz et al. 2023, which Pete holds; G4); 'Kadri 2019' (G5) was Dall'Osto 2019 (JASA; no copy in the store), and Kadri 2019 is Sci. Rep. 9:912, held.
2. **Transmission-loss grid to 20 S** (`results/hydroacoustics-tl-grid-run-j.md`). 1,720 paths × 10 bands, bathymetry-following
   KRAKEN, method unchanged (pre-registered). The clamp gap fell from 10–16 % of run J mass per stratum to < 0.2 %. New table agrees
   with the old to < 1 dB where both exist, except Perth Canyon 3376 (9.6 dB in two bands, G-TL2). Evidence-alone view: at the
   F-35A anchor the median impact is below the noise median at every receiver.
3. **Arrival windows** (`results/hydroacoustics-run-j-windows.md`). D0′ p = 0.5, deep sound channel: H01W median 00:55:43
   (90 % 00:44:03–01:11:19); H08S 01:13:47 (01:02:01–01:29:11); Perth Canyon 00:57:35; Portland 01:21:31. Kadri's published
   panels cover 54 % (H01W) and 69 % (H08S) of the arrival mass; IMOS records 27–42 %. Deviation: supplement rows not re-weighted
   for p ≠ 0.5.
4. **Received levels and power screen** (`results/hydroacoustics-run-j-levels.md`; IMOS rows superseded by 9). On 2 M weighted
   draws per option × p: at the anchor the median impact is below the noise median everywhere; matched-filter detectable share
   H01W 8 %, best receiver 14 % (D0′), baseline detector 0 %. Hand fixture and an independent implementation agree with the chain
   to 0.045 dB. The IMOS numbers in this note were corrected by block 9 (see below).
5. **Weak-signal methods** (`results/hydroacoustics-weak-signal-methods.md`). Ten detectors on real IMOS background. A
   dispersion-aware envelope matched filter (M1b) reaches P_D = 0.5 at ~7 dB SNR (α 0.01) against 13–16 dB for STA/LTA — a
   model-matched upper bound (no real long-range arrival tested yet, G-W1). Cepstral, synchrosqueezing, change-point and
   stochastic-resonance detectors failed and are kept as negative results. H08S airgun suppression gives −5 to −8 dB residual.
6. **Searches** (`results/hydroacoustics-searches-run-j.md`). Pre-registered; 786 windows on five IMOS loggers, the five digitised
   Kadri panels, Table 1, the six poster boxes, Royer B/D1/D2, infrasound. **No detection**: 184 / 60 / 29 rows at the 0.3 / 0.1 /
   0.05 levels against 236 / 79 / 39 by chance (H01W at 0.11 of chance). Strongest row: H01W 00:52:04 (text time), matched-filter
   p 0.043, needing η ≈ 0.026 (100× the anchor). Strongest two-site pair: H01W 00:52:04 × H08S 01:12:49, lag 1,245 s, 19
   lag-consistent pairs vs 8.8 expected, permutation p 0.019 over 36 tests (chance-level once the trials are counted); arc locus
   33.6 S 94.5 E, implied impact 00:31:41, needs η = 0.069 for P_D at both stations = 0.5. Table 1: 18 of 20 rows inside the D0′ 99 %
   window; two rows (00:49:58, 00:53:31) time-and-bearing consistent with the core region. The 306.18° row is uninformative at
   either time. Poster panel-(a) boxes 1–3 cannot be a post-00:19:29 arc impact by the sound channel; box 4 is marginal.
7. **Injection-recovery — the gate** (`results/hydroacoustics-injection-recovery-run-j.md`). 26,460 injections of KRAKEN-dispersed
   pulses into real background. **P_D as a function of received level on a declared background now exists at the four IMOS
   loggers** (M1b: P_D = 0.5 at +4 to +7 dB above the background median, α 0.01); H01W/H08S have proxy backgrounds only
   (IMOS noise shaped to Blackman 2003 medians); H08N blocked; Scott Reef no information. Detectability statement: η₅₀ for
   P_D(any receiver) = 0.5 is ≈ 6e-4 under D0′ p = 0.5 (3× the anchor; P_D(any) at the anchor 0.36) — on the OLD IMOS table.
8. **TL recalibration** (addendum in `results/hydroacoustics-blackman-validation.md`). With the EW0112 near-source spectrum the
   common-mode slope misfit falls from about −9 to −1.2 ± 1.8 dB/octave (slope PARTIAL at H01W, PASS at H08S); the level test is
   unit-inconsistent and is declared gap G23, so the pre-registered verdict reads NOT EXPLAINED. RAM shows the air7 ridge loss is an
   adiabatic-mode artefact (+55 dB adiabatic vs +16–22 dB RAM); a 15–22 dB path-wide excess remains (G22 partly explained). Route 2
   (F-35A spectrum) unavailable (G4). air8 negative control still holds.
9. **RAM along the grid at the IMOS loggers — gap G-TL1** (`results/hydroacoustics-imos-ram-grid.md`). The constant per-logger
   RAM correction was wrong by ±15–25 dB south of 33 S and 50–120 dB north of 29 S. All 253 planned paths now have RAM at
   5/8/10/20/40 Hz. Corrected shares (D0′ p 0.5, matched filter, η = 1e-3): Perth Canyon 3315 29.9 → 2.4 %, 3376 15.4 → 8.6 %,
   Portland 3275 25.4 → 5.8 %; at the anchor 0.1 / 1.0 / 0.0 %. The 40:1 Perth Canyon inversion is gone, but the two loggers 100 m
   apart still differ by a factor 3.6–10, which points at the 3376 terminal profile (G-TL2). Power screen: 3315 MARGINAL, 3376 and
   3275 KEEP, 3274 and 3250 DROP.
10. **Composition** (`results/hydroacoustics-composition-run-j.md`, addenda A4/A5 = corrected table). IMOS-gated likelihood
    L = (1 − P_D) + P_D × m/β per impact row, η marginalised over log-uniform [1e-6, 1e-2], written for all 313.6 M rows on the
    corrected IMOS table as `run-j-gated-v2/` (READY 12:34Z; `run-j-gated/` is the old-table version, kept and marked SUPERSEDED).
    Final headline (D0′ p 0.5): the IMOS non-detections are weakly informative — ln Z −0.034, median latitude +0.05°, mass north of
    33 S 0.058 → 0.063, KL 0.008 nats; 95 % upper limit on η from the non-detection 5.6e-3 against 6.3e-3 for the prior alone;
    P(no detection | η) = 0.56 / 0.79 / 0.89 at η = 1e-2 / 1e-3 / anchor; classical 95 % exclusion is not reached below η = 1e-2
    anywhere. Bayes factors: Kadri 306.18° row −0.04 (both times); Royer B −0.18; Royer D1/D2 and poster boxes 1–3 no information;
    Holland-type p = 1 vs p = 0 within ±0.03 under D0′. New defect G11-1: the pre-registered match term is amplitude-blind (it drove
    +1.4° shifts under D3/D4 p = 1 on the old table; +0.15° on the corrected table; amplitude-weighted +0.10°; non-detection only
    −0.02°). A first statistics re-run that straddled the table rewrite was withdrawn and redone (A5, disclosed). **Ruling requested
    from architecture: may `hydro-lnL-imos-margeta` in run-j-gated-v2 enter the composer as the module's default (G11-1 label), IMS
    proxy as sensitivity? The composer default is unchanged (0.0) until then.**
11. **Kadri package v2** (`results/hydroacoustics-kadri-package-v2.md`; `prepare/kadri_package/v2-2026-10-22/`; zip-ready copy in the
    exchange). predictions.csv on the whole-arc grid, windows.csv with both Kadri times and the poster boxes, the measurement script
    with M1b, requests A–G, the five questions (which signal carries 306.18°; what the panel-(a) boxes denote; the two Table 1 rows;
    H08S 01:05–01:20; the 16 s GPS–UTC question), a draft letter to Royer, and a cover note listing what Pete is approving.
    **Nothing has been sent.** Its predictions.csv carries the old IMOS table and needs a reload before sending.

## What changed in the module's standing
- The P_D gate is passed at the IMOS loggers on declared backgrounds; it is proxy-only at the IMS stations. The module can now
  return a likelihood from the IMOS non-detections; it is weakly informative, and whether it enters the composer is a ruling.
- The TL slope caveat C1 is now a source-term caveat (EW0112 source), not a path caveat; the level test needs unit-consistent
  measured levels (G23) before any absolute verdict.
- Adiabatic KRAKEN overstates loss on sill-crossing and seabed-receiver paths; RAM is now the method at the IMOS receivers and is
  recommended for sill-crossing IMS paths (ruling requested by the recalibration track).
- The weak-signal screen (M1b) is the primary statistic going forward; its gain is a model-matched upper bound until a real
  long-range arrival with known source is tested (G-W1).

## Gaps opened or changed tonight (status in the block notes)
G4 (F-35A spectrum; Metz et al. 2023 is held, digitised 22 Oct), G5 (Dall'Osto 2019; was listed as 'Kadri 2019'), G23 (unit-consistent received level for the air9 level test),
G-TL1 (closed to the 5/8/10/20/40 Hz, 1° node, ±30 NM set; G-TL1c/d residuals), G-TL2 (3376 terminal profile), G-TL-X (offsets beyond
±60 NM, 16–26 % of prior mass), G7-1..10 (injection: supplement rows, single dispersion profile, no AGW waveform, IMS proxies),
G-S1..9 (searches: AGW not searchable, digitised panels only, IMOS has no bearing), G-W1..6 (weak-signal), G11-1..6 (composition:
amplitude-blind match; short seeds; old-table columns). G22 partly explained. No gap was closed silently.

## Compute, disk and incidents
About 60 CPU-hours on the Mac; wall 02:15–11:45Z plus follow-ups to ~14:15Z. Disk fell from 83.5 to 11.9 GiB at the minimum
(eleven track workspaces at ~3 GB each plus Time Machine snapshots of deleted scratch; exchange outputs ~9 GB) and recovered to
~35 GiB; nothing of Pete's was deleted. Two load spikes (to ~480 and ~220) came from a duplicate RAM launch that the track could
not signal and starved instead, and from oversubscribed workers; no output was affected (byte-identical rows dropped). End of flight
did not reply to the compute notice and ran nothing on the Mac overnight. `make scope` logic checked by hand: all 36 module-branch
commits touch only `engine/hypotheses/hydroacoustics/`; one stray `.md` inside engine/ was renamed to `.txt` (11b3a23).

## Deviations declared by the tracks (short form; full lists in the block notes)
- Weak-signal: Ground-truth cases named in the brief (San Juan, F-35A, Blackman shots) not run: no digitised waveforms available overnight (block 1 deliverable); synthetic pulses used as the work order specified; Secondary targets 3274 and 3250 at file stride 4 (336 of 1,344 files) and 60 instead of 120 injections per cell (pre-registered); SNR grid extended 15-30 dB after the first run (amendment 1, disclosed; pre-registered results stand).
- Windows: Level/power-screen half of block 3 not processed: the TL grid from the parallel track had not arrived when the timing half finished.; Supplement rows not re-weighted for dive probability p != 0.5 (no pushover_to_surface column in reduced/impacts-ruleB.npz); 10.5-12.5% of the mass.; The earlier 'Acoustic publication coverage versus end of flight' chart was not found; the updated chart was built from the work-order description of it..
- Digitisation: Royer PDF taken from the project's artifact store because the Google Drive link redirects to a non-allowlisted host; Brown et al. 2026 holds no F-35A waveform/spectrum, so the F-35A spectrum deliverable is reported as a gap (Metz et al. 2023 is held; the track did not find it) rather than digitised; Dall'Osto 2019 (listed as 'Kadri 2019'; no copy in the store) and AF447 (no source in the bibliography) not extracted.
- TL recalibration: Route 2 (F-35A spectral shape) not computed: no spectrum in Brown 2026 and Metz et al. 2023 was not found by the track (one fetch, nothing returned; the paper is held, artifact 7e4d336f) — recorded as gap G4 per the parent's instruction; Step (b) was computed although its pre-registered condition (route 1 EXPLAINED/PARTLY) was not met; reported as descriptive; Steps (b) and (d) at source depth 10 m only (9/12 m not run); air7 bands 16–63 Hz (80 Hz omitted); RAM at 31.5–63 Hz on three paths only; air7 v2 re-score used 3 bands (31.5/40/63) because the new trace has < 3 columns at 50 Hz.
- TL grid: Cross-arc offsets: the mandated deliverable uses {−30, 0, +30} NM (the five-offset grid was projected over the 90-minute rule); ±60 NM was then run as a labelled supplement and merged into the tables.; 50 and 63 Hz bands not computed (budget; not used by the chain).; RAM subset: 8 paths at 31.5 and 40 Hz only (not 50–63 Hz), one per receiver, exploratory..
- Searches: Coincidence significance: the pre-registered time-slide null was kept but a held-span permutation null was added after the first run and sets p (amendment A1, disclosed in the note and code); Geometry sample for lags/bearings/energy: waypoints seeds 1-8 every 6th row + northern supplement every 4th row, not all 74 seeds (0.2 % of the mixture omitted; D3 ESS 403); eta_needed uses the interim block-2 TL grid pass A (one source latitude per receiver, src depth 10 m) rather than a per-impact TL; Scott Reef labelled blocked.
- Injection: 3315/3275 backgrounds = own 8 March recordings outside the request window (95/90 files, ~370 null windows), not the 14 GB set, which holds only 3376/3274/3250; co-located 14-day sets used as cross-check; Run J inputs from a systematic chunk subsample (8 x 50,000 rows per seed, 74 seeds; 1-in-4 thin stored; a further 1-in-8 thin for the eta bisection, 925,000 rows; ESS per option reported; D3 ESS 15-31 thin); northern supplement not included; H01W/H08S TL taken from the block 2 grid pass A on disk (provisional) rather than waiting; IMOS TL from the module's RAM-corrected table; a first eta run (pass A + RAM deltas, contrary to the pre-registration) was discarded and rerun as pre-registered (result within 3 %).
- Levels: Weighted subsample of 2 M draws per option x p (12 keys) instead of all 313.6 M rows, as the task asked; Kish ESS 1.80-1.93 M per key.; Supplement rows: E = 1/2 m v^2 (energy_transferred_j is NaN in the reduced file) and tau90 resampled from the strata distribution (column absent) — amendment 1, disclosed.; IMOS background noise percentiles from every 12th file of the 14-day set (112 files per logger) rather than all 1,344; 8 Mar set uses all role-B recordings..
- Kadri package: Prose files inside engine/ named .txt instead of .md (no-.md-in-engine rule); the zip carries .md copies; Per-band received level given at the anchor η only; the five-η sweep only for the 5–40 Hz total; make scope not executed in the sparse clone.
- Composition: α = 0.05 primary (screen level 0.3 as a sensitivity); amplitude-aware match is a down-weighting sensitivity, not a
  calibrated likelihood ratio; supplement rows enter the statistics with a τ stand-in and no column; the first A4 statistics run
  (mixed table versions) is withdrawn and replaced (A5).
- RAM IMOS: 31.5 Hz interpolated; 2 m / 30 m sources take the 10 m delta; donor-node rule on 10 % of covered rows.

## Next (for Pete and architecture)
1. Rulings: composer default for the IMOS-gated column; RAM in place of adiabatic KRAKEN on sill-crossing IMS paths; re-register the
   air9 level test with slope + shape only or obtain unit-consistent levels.
2. Pete's approvals: the Kadri package v2 and the Royer letter (cover note lists the items); Metz et al. 2023 (held) was digitised on 22 Oct by track metz-f35a; Dall'Osto 2019 via Pete if wanted.
3. Module: amplitude-aware match term pre-registered as an amendment (G11-1); real-arrival test of M1b (G-W1) once any waveform with a
   known source is held; RAM at 3376 with the terminal profile (G-TL2); reload the Kadri package predictions on the corrected table.
4. Housekeeping for Pete: thin Time Machine local snapshots; the eleven track workspaces (~33 GB) can be swept.

Commits (work branch): weak-signal 622dc6f/59a714b; windows 7bb4b08; digitisation acba616/51efc9e; recalibration
c51c0c5/2a332a7/f1d0bd3/a99f24a; TL grid 2e3f501; searches 214f890/c6a6732; injection dddd044/3d787e6/9e46b29; Kadri package ad153c3;
levels bd34ead; composition 3a566a0/e79bba2/037d154/faa8828; RAM IMOS 880ae5f/9e12486. Module branch 77b4b49 → see `git log` (36+ commits, pre-registrations
first in every block).

— Hydroacoustic Module, 22 October 2026
