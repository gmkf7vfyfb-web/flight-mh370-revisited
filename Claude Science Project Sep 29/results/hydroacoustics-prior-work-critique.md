# Hydroacoustics module: critical review of prior work on the MH370 case

Brief §10 item 2(b). The literature context and the keys used here are in `hydroacoustics-literature-review.md` and `hydroacoustics-bibliography.csv`.

**Provenance rules applied.**

- No `.md` file from the Kadri bundle (`Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/.../.sources/kadri-2024-hydroacoustics/`) was opened. Only its JSON configs and summaries were read.
- "DIGITISED" marks numbers read off published figures by the previous session (vector traces from Kadri 2024 Fig. 9 and S1 panels). They are never treated as measurements.
- "Own check" marks arithmetic I did on published numbers for this review.

**Assessment headings used for every item:**

- claim and evidence;
- trials factor;
- null model;
- pre-registration;
- bearing-error model;
- whether the stated significance survives;
- verdict, and what to reproduce.

---

## Summary table

| # | work | headline claim | survives? |
|---|---|---|---|
| 1 | Kadri 2024 + S1 | aircraft impacts are detectable at thousands of km; one MH370 candidate (00:54:30, 306.18°) | **No** for the candidate. Historical validation holds only for the F-35A. |
| 2 | Kadri 2025 poster | no plausible signal in the expected H01W/H08 window | Survives as a statement about his detector; uninformative as evidence until P_D is known |
| 3 | Kadri 2017, 2019 | single-station AGW ranging; E1 at 1,900 km; meteorite at 21:31 | **No**: field accuracy 2–6%; E1 range contradicts the two-station fix by about 3,000 km |
| 4 | Duncan & Dall'Osto 2023 | MH370 much less detectable than the F-35A; Curtin event likely seismic | Directionally sound; not transferable to the core-estimate geometry |
| 5 | Curtin CMST 2014-30 | HA01/RCS event at 5.9°S 77.2°E, incompatible with the arc | **Yes**, as "not a 7th-arc impact 00:19–00:51"; source unresolved |
| 6 | ATSB statements | acoustic analysis inconclusive / no useful new information | Yes (defers to CMST); the "likely geological" wording is not located |
| 7 | Royer 2016 (OHASISBIO) | no impact detected near the arc | Not assessable: report not obtained |
| 8 | Independent analysts (370location.org) | several arc-consistent candidates | **No**: no trials accounting; repeated retractions |
| 9 | Previous session (ISO Sept 28 worktree) | pre-registered IMOS search: 0 detections; tests of Kadri | Pre-registration sound; **detector failed every positive control**, so the non-detection carries almost no information |
| 10 | Withdrawn archive, two-station correlation | no significant H01W–H08S association | Yes (null result); illustrates null-model dependence |

---

## 1. Kadri (2024), *Sci. Rep.* 14:10102, and supplement S1

**Claim.**

- Ten historical crashes (2,211–4,695 km) and the ARA San Juan show that impacts produce distinct, detectable signals. Three signature types are proposed.
- If MH370 hit near the 7th arc, H01W should have recorded it.
- Of the transients in the window (Table 1), only one is a "major" candidate: 00:54:30 UTC, bearing 306.18°, which crosses the arc near 25.8°S.
- The probability of a chance signal is put below 3% (10-min window, 2° bearing) or below 12% (20 min, 5°).

**Evidence offered.** Spectrograms and filtered pressure traces in 10-minute panels, filtered with a 5 Hz high-pass and a 2–40 Hz band-pass. Detection is by windowed entropy above a fixed threshold, and bearing by cross-correlation lags across the triad, stated as ±0.4° at 99.5%. Raw data cannot be shared.

**Statistical assessment.**

- **The trials factor is inconsistent with the paper's own table.** The Methods compute chance with "four signals in 10 minutes". Table 1 lists **19 transients between 00:38:29 and 00:55:07 (16.6 min)**, with 18 of the 19 bearings between 234° and 343°, the sector facing the open ocean.
  - Own check: with four signals uniform over 360° and ±2°, the chance is 4.4%, not "less than 3%".
  - With the Table 1 rate inside the occupied sector it is about 51% at ±2°, and about 84% at the paper's alternative ±5°.
  - "Plausible direction" therefore does not discriminate between transients.
- **The target was not pre-specified.** 306° was selected as the strongest transient after inspection, and the chance calculation then conditions on its bearing. No time or bearing window was registered beforehand.
- **No null model and no false-alarm rate.** The detector threshold is not related to a false-alarm rate on background data. No other nights, off-bearing windows or time slides are used.
- **Bearing error.** The claimed ±0.4° contrasts with the paper's own M2.7 Sinabang check at H08S on the same night, which was off by 3.4° (about 140 km). Curtin's ±0.75° and TGS bias of 0.6° [CMST2014] apply to cleaner arrivals.
- **The candidate fails the timing of the hypothesis it is meant to support.** Δt = +17.1 min after the arc crossing (Table 1; reproduced by the previous session as +17.2 min). By Kadri's own Eq. (4), that requires at least 10 minutes of further flight after 00:19:29. That contradicts the fuel-exhaustion descent he adopts, and it puts the impact far outside the core estimate (median −37.225°; 50% interval [−37.85, −37.00]).
- **Signal strength (DIGITISED).** On the digitised Fig. 9c trace the previous session's band-energy detector gives the candidate an SNR of about 2.1 dB, ranked 3rd of 43 peaks in the panel. Most Table 1 transients sit at about 0.5 dB or below, and several have no detector peak within 5 s. This is a single plotted, already filtered channel, so it is a weak check, but it does not support "major".
- **Internal inconsistencies.**
  - The main text dates the 306° signal at 00:52; Table 1 has 00:54:30.
  - 00:52:36 appears twice with different bearings.
  - The previous session found a sign error in Δt at 00:42:02.
  - Reference 3 cites Kadri (2019) as article 919; the published number is 912.
  - S1 reference 5, for Transair 810, is an unrelated NTSB report on a different accident.
- **Energy argument.** Equating 4 GJ of kinetic energy with an M3.2 earthquake treats all kinetic energy as radiated wave energy. It also compares a surface impact with an in-crust source whose T-phase conversion is efficient. The coupling factor, which is the largest uncertainty [Brown2026], is absent.
- **Historical "detections" checked against ground truth** (literature review §1.3; own check of S1 panels plus the previous session's DIGITISED reconstruction):
  - Six of eight assessed non-F-35 station-detections are 4–12 minutes off the water-path arrival time.
  - Two S1 panels (Yemenia H08N, Sriwijaya H08S) do not even contain the predicted water-path arrival.
  - The two timing-consistent cases (Lion Air 904) have an implausible amplitude, and Kadri himself doubts them.
  - Several sources lie in shallow shelf seas.
  - The ARA San Juan arrival at H03S via a land path is not reported in the CTBTO or Vergoz analyses.

**Verdict.**

- The MH370 candidate **does not survive**. Its significance is not established once the paper's own transient rate is used, the selection was post hoc, it is single-station with no H08S confirmation, and its timing contradicts the scenario it supports.
- The historical set **validates long-range detectability only for the F-35A**, which is independently confirmed [Metz2023 via Brown2026]. The other nine cases are unverified claims and in most checked cases timing-inconsistent.
- The paper's lasting contributions are the controlled-explosion proposal and the observation that H08S is airgun-dominated that night.

**Reproduce.**

1. The Table 1 Δt values (done by the previous session: median residual +0.12 min, 16 of 18 rows within 0.5 min).
2. The chance probability with the Table 1 rate and the bearing distribution actually observed (own check above). Then a proper look-elsewhere computation on raw H01W background, if Kadri provides it.
3. Historical predicted-arrival residuals from raw data (Kadri package request, brief §9).
4. The candidate is carried as the conditional hypothesis of §8 with an explicit prior, never folded into the base estimate.

---

## 2. Kadri (2025) poster P1.4-254

**Claim.**

- Ten incidents show basin-scale detectability, including land-coupled paths.
- For MH370, "within the narrow time-bearing window, no candidate signal appears at H01W (nor H08)".
- The lack of H08S confirmation is put down to noise and bathymetric loss, and labelled as an insight, not definitive.
- Bearing is again stated as ±0.4° at 99.5%.

**Statistical assessment.** A non-detection with no stated window, threshold, P_D or background characterisation. It implicitly re-classifies the 2024 candidate as outside the "narrow" window, which is consistent with item 1's timing objection, but the window itself is not defined.

**Verdict.** A legitimate statement about his own detector. As evidence about impact location it is **uninformative until P_D is known** (brief §2 rule 2).

**Reproduce (brief §8).**

1. Obtain his window definition.
2. Rerun his detector unchanged on injected signals in the H01W background (package request).
3. State the received level at which his "no candidate" would have become a candidate.

---

## 3. Kadri et al. (2017), *Sci. Rep.* 7:13949, and Kadri (2019), *Sci. Rep.* 9:912

**Claim.**

- Acoustic-gravity-wave modal dispersion at a single station yields source range.
- Numerical accuracy is better than 0.02% beyond 1,000 km.
- For 8 March 2014: E1 at 01:34:40, 301.4 ± 0.4°, 1,900 ± 200 km from HA01, source time 01:11–01:16. E2 at 00:50:00, 234.6 ± 0.4°, 1,940 km, source time 00:25–00:31, about 43.5°S 94.5°E.
- A 21:31:24 event is attributed to a possible meteorite.
- In 2019, water/seabed transmission routes allow E1 to lie anywhere from 1,900 to 4,294 km.

**Statistical assessment.**

- **Field validation.** Against two catalogued M5.1 earthquakes the range errors were +140 km (+5.9%) and −100 km (−1.8%). That is the realistic accuracy. The 0.02% figure is only the algorithm's self-consistency.
- **Contradiction with the independent two-station fix.** E1 is the same event as Curtin's: same time, and bearing 301.4° against 301.6°. Curtin's HA01–RCS arrival-time difference places it at 4,962 km [CMST2014]. E1's 1,900 ± 200 km is about 3,060 km (≈15 of the stated σ) away. None of the 2019 alternative routes (largest 4,294 km) reaches 4,962 km.
- **Post-hoc flexibility.** Adding transmission routes after the fact turns a range estimate into a menu with no penalty for added freedom, so it cannot be falsified by range.
- **Wrong band for AGW.** The analyses high-pass at 5 Hz. The AGW cut-off at abyssal depth is about 0.1 Hz, and gravity is negligible at 2–40 Hz, where tens to hundreds of modes propagate (own arithmetic). The isovelocity, constant-depth model behind the inversion does not describe range-dependent deep-channel propagation over 2,000–5,000 km.
- **Meteorite claim.** Brown2026 note that no bolide data were presented and treat the association as unproven.
- E2 is the same transient as Kadri 2024's Table 1 entry at 00:49:41, 234.67°. Kadri rejects it because it would need 3,300 km/h. It is also the second-ranked driver of the withdrawn two-station correlation (item 10).

**Verdict.** Single-station AGW ranging is **not validated for this use**. Its range estimates for 8 March 2014 should not enter the module. The physics belongs on the SOFAR branch (brief §2 rule 3).

**Reproduce.** None is needed for the likelihood. Keep E1/E2 as named transients in the background catalogue and as controls.

---

## 4. Duncan & Dall'Osto (2023), ASA 185th meeting (JASA abstract 10.1121/10.0022761; lay-language paper; figures 3 and 5 on the branch)

**Claim.**

- Long-range detection of MH370 is much less likely than that of the F-35A.
- The F-35A site offered both routes into the deep channel: a downslope seabed and a channel axis near the surface.
- Along the bearing of the signal of interest from HA01, the second route is ruled out and the first rarely applies.
- The Curtin signal is more likely low-level seismic activity, which produces arrivals at HA01 from similar directions about once per day.

**Evidence.**

- Fig. 3: modelled relative signal strength against range for the F-35A path and for "MH370". The MH370 bathymetry matches CMST2014's 301.6° transect: Naturaliste Plateau, then Batavia Seamount at about 1,700 km.
- Fig. 5: sound-speed section along that bearing to 8,500 km. The channel axis descends from about 1,000 m toward about 1,800 m, and ridges rise above it.

**Statistical assessment.**

- Deterministic model with no uncertainty bands. The lay version does not give source depth, frequency or seabed parameters, and it has not been peer reviewed.
- My visual read of Fig. 3 (not digitised) puts the MH370 curve 20–30 dB below the F-35A curve at their respective source ranges, consistent with brief §3.
- But **the "MH370 path" is the 301.6° bearing of the Curtin event**, which crosses the 7th arc at roughly 24–26°S, not the core-estimate geometry near −37° (H01W bearing about 255–265°). **The 20–30 dB is therefore a statement about the north-west bearing.** It cannot be used as a prior for the core region without recomputation.
- The "about once per day" background comes from five years of HA01 data. CMST2014 notes these events were heavily clustered in time, so a Poisson rate is not appropriate.

**Verdict.** Physically sound and consistent with CMST2014 and with the controlled-source evidence on site coupling (literature review §1.1). **Qualitatively robust, quantitatively non-transferable.**

**Reproduce.**

1. Digitise Fig. 3, labelled as digitised with the method recorded (brief §2 rule 10).
2. Run range-dependent PE along 301.6° with stated parameters to see whether the 20–30 dB difference is reproduced.
3. Repeat along the core-estimate paths to H01W, H08S and H11. That is the number the module actually needs.

---

## 5. Curtin CMST Report 2014-30 (Duncan, Gavrilov & McCauley, June 2014)

**Claim.**

- An event at RCS (Perth Canyon, 450 m) at 01:33:44 ± 4 s and at HA01 at 01:34:50 ± 3 s, bearing 301.6 ± 0.75°.
- The 66 s arrival-time difference with a modelled group velocity of 1,486 m/s gives 5.93°S 77.22°E (4,962 km), emitted about 00:39:11.
- Placing the source on the arc would need the time difference to be 17 s smaller.
- Most likely explanation: the same natural event at both sites, unrelated to MH370.
- An automated scan of eight hours at HA01 found this the only arrival from a northerly direction.
- HA08S showed nothing consistent. The TGS survey was detected with a 0.6° bearing bias; the Woodside survey was not.
- A Bayesian estimate gives P(same source | timing) > 0.5 if the prior exceeds 0.03.

**Statistical assessment.**

- **Pre-registration.** Not applicable (operational work in 2014). However, the event emerged from an automatic scan with fixed acceptance criteria: residual ≤ 10 ms, apparent speed 1.42–1.55 km/s, a neighbour within ±0.5°. "Only northerly arrival" is a post-hoc category, but over a fixed eight-hour scan.
- **Timing robustness.**
  - The 17 s shift needed is more than 4σ of the stated ±4 s.
  - The clock correction (25.8 s, from a 31.76 s drift over the deployment assumed linear) was checked by two independent events: predicted minus actual 3.2 ± 6 s and 0 ± 7 s.
  - HA01 timing was confirmed by the CTBTO.
  - A linear-drift assumption and the canyon site of RCS are residual risks, but neither plausibly produces 17 s.
- **Bayes calculation.** Correct in form, but fragile:
  - λ comes from two events in five hours. Own check: the Poisson 95% interval for two counts gives P(B | not same) of about 0.004–0.10, against the stated 0.030.
  - The five-year "once per day" rate gives about 0.003, but the events are clustered.
  - P(B | same) = 1 ignores pick error.
  - The calculation addresses "same source", not "MH370". The authors flag all of this themselves.
- **Bearing model.** ±0.75° treated as a hard bound. Heavier tails would elongate the box but would not reconcile the timing.

**Verdict.** **Sound and appropriately hedged; survives.** On the timing alone the event is not a 7th-arc surface impact between 00:19 and 00:51. A sinking-debris implosion near the arc much later is not excluded by the HA01 bearing alone, but it is excluded by the two-station range if both arrivals are the same event. The "arc is wrong" alternative is outside this module's scope.

**Reproduce.**

1. From the held IMOS 3315 record: the 01:33:44 pick and the 25.8 s drift correction.
2. The two-station fix with our celerity model and the demonstrated bearing tails.
3. Keep the event as a positive control (it already is one in the previous session's pre-registration).
4. Obtain and review Curtin's second report (September 2014, Scott Reef; ATSB *Operational Search* Appendix I), which was not read here.

---

## 6. ATSB statements on the ~01:34 UTC HA01 event

**Found.**

- The June 2014 *Definition of Underwater Search Areas* lists hydrophone acoustic detections among the information considered [ATSB2014DUSA].
- The 2016 First Principles review states that hydroacoustic analysis contributed no useful new information to the search [ATSB2016FP; search snippet only].
- The 2017 *Operational Search* reproduces the Curtin reports as appendices [ATSB2017OS; not read].

**Not found.** I could not locate ATSB wording that calls the event "likely geological". That characterisation is Curtin's (natural seismic origin most likely) and Duncan & Dall'Osto's (low-level seismic activity). Brief §6(e) should attribute it accordingly until the ATSB source is found.

**Assessment.** The ATSB did no independent acoustic analysis that I found. Its position rests on CMST2014.

**Verdict.** Consistent with item 5.

---

## 7. Royer (2016), OHASISBIO report (released July 2026 via journalism)

**What is known (secondary sources only).**

- Eight autonomous hydrophones at six southern Indian Ocean sites in 2014, recovered January–February 2015.
- An 18-page report dated 22 December 2016 identifies five events around the time of the disappearance, two of them also seen in CTBTO data, including an Antarctic ice event.
- **No impact was detected near the 7th arc.**
- One secondary account indicates that the instrument closest to the presumed crash area did not deliver usable data.
- The report was submitted to the French and Australian investigations but is not in the ATSB final report.

**Assessment.** These are moored deep-channel hydrophones closer to the arc than HA01, on independent clocks, so potentially the most valuable regional non-detection data. Without the report, the data, the windows and P_D, nothing can be scored.

**Verdict.** Not assessable.

**Reproduce.** Brief §9 already requests Royer's 2014 data. Add the report itself and the station list, so that coverage and the closest-instrument loss can be checked.

---

## 8. Independent analyses (370location.org and others)

**Claim.** Over 2015–2019, several arc-consistent candidates:

- 00:39:18 at 271.73° from H01 (32.97°S 95.40°E);
- a 03:30 H01 / 05:20 H08 cross-bearing on the arc at 39.7°S;
- a "Java anomaly" at 01:15:48;
- a 4.65°N 66.62°E relocation of the Curtin event;

together with several published retractions.

**Assessment.**

- Wave-speed restrictions were relaxed until candidates appeared.
- Windows extended to hours after impact, with implosion hypotheses added afterwards.
- There is no trials accounting and no null. This is the textbook look-elsewhere pattern.

**Verdict.** Not evidence.

**Use.** Add every published candidate time and bearing to the background catalogue and to the list of controls, so our own searches are seen not to rediscover them by construction.

---

## 9. Previous session: `ISO Sept 28 Status/results/worktree-hydroacoustics/`

Read: `kadri-package/preregistration.toml`, `imos/search.json`, `imos/detection-probability.json`, `imos/earthquake-controls.json`, `widened-windows.json`, `kadri-tests/kadri-tests.json`, `kadri-tests.png`, `report-page-1.png`, `eta.txt`, and `threads/hydroacoustics-open-questions.md`. `report.pdf` pages 2–6 and `detection-control.json` were not read in full.

**Claims.**

- A pre-registered search of the IMOS loggers (3315, 3376, 3250, 3274, 3275):
  - windows built by a rule from a stand-in impact set (Davey 2016 base-run positions ±250 km, impact time uniform 00:19:37–00:55);
  - detector D1: band energy ratio in four bands;
  - thresholds set at 0.25 false alarms per hour per band on background;
  - quarantine of in-window data until the envelope was committed;
  - amendments dated and justified.
- Result: 0 detections at 3315, 3376, 3274 and 3275; one at Scott Reef, whose paths are all blocked (p = 0.51).
- P(any IMOS logger detects) = 0.24 at the F-35A-anchored η of 8.7×10⁻³, 0.095 at η/10, and 0.005 at η/1000.
- Tests of Kadri: timing residuals; digitised Fig. 9 measurements; loudness and timing of historical cases.

**Statistical assessment.**

- **Pre-registration: good practice.** It was dated, git-recorded and rule-based, with backgrounds from real data, other nights, earthquake controls and injection-recovery specified. The amendment that excluded dropout records was made before in-window data were opened, and the text says so. This is the protocol of brief §6 implemented.
- **The positive controls failed.**
  - The two Curtin clock cross-check events at RCS reached at most S = 10–17 dB. The background rate at or above those levels is 0.67–2.1 per hour per band, against the registered 0.25 per hour. Neither control would be detected at threshold. The pre-registration amendment records that both were missed before it, and the post-amendment numbers in `search.json` still fall below threshold.
  - The 01:33:44 Curtin event itself reaches S = 14.5 dB at a background of 1.2 per hour: also below threshold.
  - Earthquake controls: 0 of 6 above threshold.
  - Together with the roughly 28–36% duty-cycle coverage, this means **the IMOS non-detection carries very little information**. That is consistent with the small P_D values, but it is a statement about the detector (4 s energy window on a single hydrophone), not only about η.
- **η anchor.** The previous session's "F-35 anchor" η₀ = 8.66×10⁻³ is about two orders of magnitude above Brown2026's ~10⁻⁴. It is defined relative to the session's own propagation chain (the `kadri-tests.png` axis is "chain relative to the F-35 anchor"), not as acoustic energy over kinetic energy. **The two numbers must not be compared or mixed.** η needs one documented definition.
- **The F-35 peak used differs by source.** The session read 1.1 Pa (H11N) and 1.0 Pa (H11S) from Kadri's filtered S1 panels (DIGITISED); Brown2026, citing Metz2023, gives 0.7 Pa. The ratio of about 1.6 (4 dB) propagates directly into η.
- **Window choice.** The registered H01W bearing window (242.6–298.1°) excludes both Kadri's 306.18° and Curtin's 301.6°. That is correct under the stand-in prior. The widened windows (to 300.5°) for late or powered endings are labelled as sensitivity, and they are not fully blind for IMOS, as the session's own note says.
- **Kadri tests.** The Δt reproduction is solid (median +0.12 min). The digitised Fig. 9 measurement and the historical loudness and timing table are labelled as published, processed traces, not raw and not blind, which is correct. The historical timing result underpins item 1.

**Verdict.**

- The **method and discipline survive**, and should be kept.
- The **IMOS null result is correct but nearly uninformative**, because the detector demonstrably misses known events of the relevant kind.
- The η scale must be re-anchored.

**Reproduce or repair.**

1. Replace D1 with a matched or band-limited correlation detector whose false-alarm curve is measured on IMOS background. Require it to recover the Curtin and earthquake controls before any search is re-run (brief §11 null test).
2. Re-derive η against one definition (literature review, implication 2).
3. Rerun injection-recovery across η, as the 2026-10-08 ruling requires.

---

## 10. Withdrawn archive: two-station correlation and associated audits (JSON/CSV only)

Files read: `two-station-correlation-config.json`, `two-station-correlation-summary.json`, `oscar-boundary-audit-summary.json`, `aligned-detection-analysis-summary.json`, `event-pair-analysis-summary.json`, `summary.json`, `conditional-geometry-summary.json`, `impact-simulation-summary.json`. No `.md` and no PDF was opened.

**Claim.**

- An energy correlation of the digitised H01W panels (b, c) against the H08S panels (d, e) over a source grid on the 7th arc (±100 NM; 17,753 unique lag hypotheses × 41 fine offsets).
- Significance from the maximum over the complete search under IAAFT surrogates, plus a pulse-conditioned test with mark permutation and H01W time slides.

**Results.**

| test | statistic | p |
|---|---|---|
| unfiltered energy correlation | max r = 0.120 | 1.0 (IAAFT, scan maximum) |
| airgun-filtered, rank 8 | max r = 0.109 | 0.964 |
| pulse-conditioned Fisher | — | 0.948 (mark permutation); 1.0 (time slide) |

- The leading driver window is Kadri's 306.18° transient; the second is the 234.67° transient (E2).
- The "OSCAR" boundary audit found an H01W feature at 00:52:04 with **panel-maximum IAAFT p ≈ 0.001**, but that interval was **chosen after visual inspection**. Its H08S counterpart lies 0.5 s inside a panel edge and within the periodic airgun mask, and burst-preserving controls give **p = 0.63** (matched cycle windows) and **p = 0.91** (periodic-phase null).
- The aligned-detection test gives p = 0.035 for a fixed window chosen after inspection, against **p = 0.115** for the full-panel maximum.

**Statistical assessment.**

- The complete-search maximum used as the test statistic is correct look-elsewhere practice.
- The primary null (IAAFT) destroys burstiness. Where burst-preserving alternatives were run they raised p from about 0.001 to about 0.6–0.9: the null model decided significance, exactly as brief §5 records.
- Inputs are already-filtered publication vectors, not raw triads, so pressure phase is lost and only energy is correlated.
- The source grid was a Pléiades transport-family density. That couples this module's search to another module's evidence, which conflicts with brief §2 rule 6 (score the shared impact samples) and risks the double counting rule 5 forbids.
- **The brief's specific "p = 0.0025" was not found** in any JSON read. The pattern it describes is present with the values above.

**Verdict.** A **null result that survives**. It is also the clearest in-project demonstration that significance claims are null-dependent, and that post-hoc windows inflate significance by about an order of magnitude.

**Reproduce.** Keep it as a negative result behind a config flag (agent rules). Rerun only on raw triads, with time slides and stationary-bootstrap nulls, on the shared impact samples.

---

## Cross-cutting discrepancies to resolve (for the architecture session and Pete)

1. **Duncan & Dall'Osto path (brief §3).** The 20–30 dB comparison is along the Curtin 301.6° bearing, not along the core-estimate path. Brief §3's sentence should say so.
2. **Two η scales.** The previous session's anchor (8.66×10⁻³, chain-relative) and Brown2026's ~10⁻⁴ (Arons SOFAR-equivalent yield over kinetic energy) differ by about 87 times. One definition must be fixed in the impact-source interface.
3. **F-35 received peak.** 0.7 Pa [Brown2026/Metz2023] against 1.1 Pa (DIGITISED from Kadri's filtered panels).
4. **"p = 0.0025".** Not located. The values found are 0.001 (IAAFT) against 0.63 and 0.91 (burst- and phase-preserving), and 0.035 against 0.115 (fixed against full-panel window).
5. **"Likely geological" attributed to the ATSB (brief §6(e)).** Wording not found in ATSB sources searched. The attributable sources are CMST2014 and DuncanDallOsto2023.
6. **Kadri internal inconsistencies:** candidate at 00:52 or 00:54:30; duplicate 00:52:36 rows; the Δt sign at 00:42:02; the Sriwijaya range (S1 gives 4,694 km, the previous session used 3,828 km); the Kadri 2019 article number (912, not 919).
7. **HA08 data gap.** Kadri2019 reports 25 minutes of missing data on all three HA08S hydrophones from 03:07 UTC on 8 March. That is outside the registered H08S windows (to 02:31), but relevant to any late-impact or implosion window.

## What to reproduce first (ordered by information per effort)

1. Curtin RCS/HA01 timing and fix from the held IMOS record (item 5). It is both a positive control and an engine timing test.
2. A detector that recovers the Curtin and earthquake controls on IMOS background, before any re-search (item 9).
3. Duncan's 301.6° comparison by PE, then the core-estimate paths (item 4), feeding the detectability statement (§10 item 6).
4. Requests to Kadri: predicted-arrival residuals and raw triads for the historical crashes, and his window definition (items 1, 2).
5. Royer's report and data (item 7).
