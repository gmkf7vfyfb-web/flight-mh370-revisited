# Combined weak-signal detector on the 8 March 2014 data: results, version 2

Date: 6 November 2026.
Pre-registration: `combined-detector-2014-prereg.md` v1.0, committed (a1c449fd) before any scoring.
This version replaces version 1. It includes:
- the fixes from the independent review (`review-combined-detector-2014.md`);
- the earthquake-cleaned noise calibration that Pete asked for on 6 Nov;
- results at several false-alarm levels;
- a ranked list of weak candidates;
- multi-site views of the top Cape Leeuwin (CL) and Diego Garcia South (DGS) candidates.

## 1. Summary

1. **Where the full detector could be used.** It ran at the five IMOS loggers. At Cape Leeuwin and Diego Garcia South we hold no 8 March 2014 waveform, only the digitised Kadri (2024) Figure 9 envelopes. There the detector reduces to band energy and persistence. Spectral shape, the templates and the impact-pattern correlation cannot be used. This is the largest single limit on this work. The raw H01W and H08S waveforms for 8 March 2014 (CTBTO) would remove it.
2. **Network result.** No impact time and place reaches even the 50 % global false-alarm level. With the earthquake-cleaned calibration (the final version), the best network evidence is 1.76 against levels of 2.50 (50 %), 3.04 (20 %) and 3.57 (5 %). The global chance is 0.88; it is 0.59 with the wide sound-speed range.
   - Every sensitivity run gives 0.88–0.97: pre-registered calibration 0.93; Portland 2 on Portland 1 noise 0.95; Perth Canyon 2 on Perth Canyon 1 noise 0.97; empirical tail floor 0.94; earthquake looks also removed on 8 March 0.88.
3. **Weak candidates exist and are listed (section 4).** The strongest network hypotheses are glide or ditching impacts near 00:53–00:55 at 20–25° S, 100–150 NM east of the arc. Two sites carry them:
   - Scott Reef, p 0.05–0.06, on a path with large attenuation only;
   - Perth Canyon 2, p 0.03–0.04, the logger calibrated on only 75 records.

   Their global chance is 0.59–0.91. That is the level expected from noise alone. They are recorded as weak candidates, not as detections.
4. **Seeds.** 65 seeds were tested: 19 Kadri, 12 screening picks, 31 strongest looks and 3 earlier network cells. No seed is confirmed at the other stations. The smallest seeded p is 0.073 (Kadri 00:42:02), and the smallest Benjamini–Hochberg q is 0.98. Kadri 00:54:30 gives p 0.53.
5. **Kadri fit.** 17 of 19 Kadri transients fit a glide or ditching on the arc; 6 of 19 fit a steep dive. Under the glide window, 00:54:30 implies impact 00:31–00:40 at 26° S.
6. **Sensitivity at one logger, known arrival time.** For 50 % detection the logger needs:
   - at 5 % false alarms per look: about −8 to +1 dB (8–40 Hz SNR);
   - at 20 % per look: about −17 to −4 dB.
7. **Sensitivity of the network.** Two independent IMOS sites need about 2.4–8.6 dB each at the global 5 % level, −0.1 to 5.4 dB at 20 % and −3.3 to +3.1 dB at 50 %. One more covering station that carries only noise adds 1.2–4.3 dB. Only 40 % (dive) to 43 % (glide) of hypotheses reach two IMOS sites that were recording.
8. **What can be concluded.** This search excludes nothing. It gives a stated sensitivity for the hypotheses that two sites covered. Converting that into "an MH370 impact would or would not have been heard" needs the received-level model (source level, transmission loss, noise level). That step is not done.

## 2. Corrections since version 1

| Item | Version 1 | Version 2 | Effect on global chance |
|---|---|---|---|
| Network rule | at least two loggers (co-located pair counted twice) | at least two independent sites | none (0.93) |
| Seeded test | seed logger excluded | whole site of the seed excluded | none |
| Time-shift wrap | broke the 15-min recording phase | whole 15-min cycles | none |
| Injection whitening | from the clean noise record (optimistic) | from the signal-plus-noise record, as on real data | single-logger SNR50 up to 0.5 dB; network up to about 0.6 dB |
| Perth Canyon 2 null | own-day records only | also Perth Canyon 1 noise as a sensitivity | 0.97 |
| Tail sensitivity (pre-registration A6) | not run | empirical floor 1/(n+1) | 0.94 |
| Earlier network cells as seeds (B7) | missing | 3 Nov graded best (39.5° S, 00:44:30), 3 Nov hourly best (38° S, 00:33:30), 4 Nov dive best (30° S, 00:19:38–00:21:18) | seeded p 0.25, 0.84, 0.70 |
| Known earthquakes | not removed from the noise; candidates not labelled | removed from the calibration; event-day looks labelled; removal sensitivity | 0.88 |
| False-alarm levels | 5 % only in the sensitivity chart | 5 % and 20 % per look; 5 %, 20 % and 50 % global | — |

Declared departures from the pre-registration that are kept:
- **Time-shift design (B6).** Shifts are per site, not per station. IMOS shifts are 30–120 min in whole records; Kadri traces are shifted cyclically by at least 5 min, because the traces are only 29.5 and 19.4 min long.
- **Kadri null (B2).** It uses the within-trace rank null, not the 4 Nov block bootstrap.
- **Whitener exclusion.** It is ±30 s, not ±15 s.
- **Recorded-quake control.** It uses IMS waveforms with IMOS gain applied and no path filter, so it is a waveform-shape control only.

## 3. Earthquakes and the noise distribution

- **Catalogue and rule.** USGS M ≥ 3.5 within 70° of each site, 27 Feb–16 Mar 2014 (332–381 events per site). A record is flagged when its 307 s overlaps origin + distance/1.52 km/s − 30 s to origin + distance/1.45 km/s + 180 s. This is the same rule as the 6 Nov IMS test.
- **Records removed:** 14–19 % at each logger. Five records with instrument faults (non-finite or impossible band energy above 100 dB) were removed as well.
- **Effect on the tail: small at IMOS.** The band-energy 99 % level changes by 0.0–0.7 dB, for example Perth Canyon 1 from 15.4 to 15.2 dB. The IMS stations behaved differently: −2.5 dB on 6 Nov. The likely reason is that each IMOS score is referenced to the median of its own 307 s record, so an earthquake filling the record does not stand out.
- **Event day.** No CL or DGS candidate in section 5 lies inside a USGS M ≥ 3.5 arrival window. The 4 Nov screening labels came from the wider pre-registered catalogue (ISC) at association probability below 0.95. They are kept as labels and nothing was removed.

## 4. Ranked weak network candidates (final calibration, independent sites ≥ 2)

Primary sound speed 1.465–1.520 km/s with 2 % detour. Distinct candidates are at least 2° or 3 min apart. File: `network_candidates_ranked_eqclean.csv`.

| Rank | Impact (UTC) | Arc, offset | Sites | Evidence | Global chance | Station p |
|---|---|---|---|---|---|---|
| 1 | 00:54:38 | 23° S, +125 NM | 2 | 1.76 | 0.88 | Scott Reef 0.063; Perth Canyon 2 0.040 |
| 2 | 00:54:53 | 20° S, +25 NM | 2 | 1.66 | 0.91 | Scott Reef 0.12; Perth Canyon 2 0.026 |
| 3 | 00:54:23 | 34° S, +150 NM | 3 | 1.47 | 0.96 | Scott Reef 0.0018; Portland 1 0.79; Perth Canyon 2 0.79 |
| 4 | 00:39:08 | 41° S, −150 NM | 2 | 1.30 | 0.99 | Portland 0.17/0.41; Perth Canyon 2 0.026 |
| 5 | 00:28:08 | 23° S, −50 NM | 2 | 1.26 | 0.99 | CL 0.065; DGS 0.15 |

With the wide sound speed, the best is 00:53:53 at 25° S, +100 NM: evidence 1.98, global chance 0.59, Scott Reef 0.052, Perth Canyon 2 0.026.

Notes on these candidates:
- The top three sit at the end of the glide window, and the Scott Reef path to them has large attenuation only.
- The Scott Reef record at about 01:00–01:05 contains a train of repeated broadband pulses (see the multi-site views).

## 5. Top 10 Cape Leeuwin and Diego Garcia South candidates, viewed at every other site

File: `candidate_views_cl_dg.pdf` (47 pages: one summary page, then one page per candidate and site, each with spectrogram, band energy, impact-pattern correlation and combined p). Per-site numbers: `candidate_views_sites.csv`.

- **Ranking.** Envelope evidence at the station: band energy and persistence on the digitised Kadri trace, smallest p within ±15 s.
- **Window at each other site.** It runs from the earliest arrival at 1.56 km/s to the latest at 1.40 km/s with 5 % detour, over every impact point and time consistent with the candidate (bearing within 3°; impact 00:19:38–00:55:00), widened by 20 % of its length at each end. The shaded band shows the primary speeds.
- **Result.** No other-site window reaches p < 0.1. The smallest are:
  - Portland 2, p 0.17. This is the same look (01:07:53, inside the known Portland 2 burst) for several candidates, on a logger whose calibration is optimistic.
  - Portland 1, p 0.25.
- **Left out.** Two strong Kadri transients have bearings that miss the arc within 150 NM: 00:47:04 (343.2°) and 00:49:41 (234.7°).

## 6. Is the time-shift null too strict?

At loose levels the real data give fewer passes than chance: 3 seeds at p < 0.2 against about 12 expected.

- **Not a coverage artefact.** The real and shifted alignments cover the same share of hypotheses with two or more sites: 0.764 and 0.763.
- **The real data are quieter.** The real alignment's average network evidence is 0.185, against 0.279 ± 0.057 for 60 shifts; 97 % of shifts are higher.

So the 8 March 00:20–01:40 records score lower on this detector than nearby periods. Seeds also overlap, so they are not independent. The high global chance reflects quiet data, not a biased null. A null drawn from the same hours on other days would test this further.

## 7. Detection sensitivity (injection version 2)

SNR (dB, 8–40 Hz) for 50 % detection at one logger with a known arrival time. Each cell gives the value at 5 % / 20 % false alarms per look.

| Logger | Steep dive | Shallow entry | Ditching-like | + break-up | Recorded quake |
|---|---|---|---|---|---|
| Perth Canyon 1 | −7.8 / −12.8 | −7.7 / −13.2 | −7.4 / −12.9 | −8.4 / −14.3 | −6.2 / −10.7 |
| Perth Canyon 2 | −1.0 / −15.2 | −1.0 / −14.4 | −1.2 / −16.7 | −3.6 / −16.1 | −2.0 / −13.5 |
| Portland 1 | −0.4 / −5.0 | 0.4 / −4.8 | 0.2 / −4.8 | −0.7 / −6.2 | 0.9 / −4.1 |
| Portland 2 | −4.6 / −12.7 | −4.8 / −13.5 | −4.5 / −11.8 | −4.7 / −14.3 | −1.7 / −8.8 |
| Scott Reef | 0.5 / −6.9 | −0.5 / −5.4 | −0.5 / −3.8 | −3.6 / −7.2 | 0.9 / −6.3 |

Caveats on this table:
- Perth Canyon 2 and Portland 2 are calibrated in-sample on 89–92 of their own records, so their values are optimistic.
- The no-signal check gives 0.040–0.055 at 5 %, except Perth Canyon 2 at 0.085.
- 58–63 % of synthetic impact energy is below 8 Hz, so the 8–40 Hz SNR understates the total signal.

Network sensitivity is in `network_detection_snr_v2_g05/g20/g50.csv` and is drawn in the sensitivity figure.

## 8. Files

All files are in `results/hydroacoustics/combined-detector-2014/`:
- Final run: `run14v3_eqclean/` (calibration `imos_calib_eqclean.pkl`, built by `eq_clean.py`) and `run14v3_eqclean_remove/`.
- Runs after the review fixes: `run14v2/`, `run14v2_null3275/`, `run14v2_null3315/`, `run14v2_a6floor/`.
- Version 1 as first run: `run14/`, `run14_null3275/`.
- Injections: `imos_injections_physics_v2.csv`, `imos_injections_purenull_v2.csv`, and the version 1 (oracle-whitened) files.
- Candidates: `candidate_views_cl_dg.pdf`, `candidate_views_sites.csv`, `cand_all.csv`, `network_candidates_ranked_eqclean.csv`, `kadri_seeded_windows_both_families.csv`, `kadri_times_cape_leeuwin_envelope_p.csv`.
- Earthquake calibration effect: `eqclean_calibration_effect.csv`.
- Review: `review-combined-detector-2014.md`.
