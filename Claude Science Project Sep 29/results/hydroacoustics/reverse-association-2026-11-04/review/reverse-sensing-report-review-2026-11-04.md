# Independent review of the reverse-sensing hydroacoustics report (first run, 4-5 Nov 2026)

Reviewer role: adversarial check of the headline claims against the committed tables and code. Statistical signal detection and underwater acoustics.
Report under review: `reverse-sensing-hydroacoustics-report-2026-11-04.md` (artifact e3838a04, version ecb0f0b7). Main source: `reverse-association-run-report-2026-11-04.md` (version 2246484e, the later of the two versions) and the tables that the task names.
Method: I recomputed only the values needed to test each claim. I did not run the pipeline again. The script `review_checks.py` and its output `review_checks_output.txt` are in this folder.
Condition: every result is conditional on the Boeing alternate-dive hypothesis and the impact window 00:19:38-00:29:44 UTC.

## 0. Limits of this review

1. **Blocked step.** The platform safety check blocked one read of the hydro data database. I did not read it another way. Instead, I took station positions from the arrival-window grid. I inverted the per-cell geodesic distances, with a residual of about 3 m RMS.
2. **No time-slide code.** The back-projection, time-slide and check cells ran in the session kernel only. The scripts are not in the repo (blocked step 4 of the report). So I could not inspect how the time-slide null treats co-located loggers, the wrap at record edges, or the 30 s minimum shift. Section 2 below uses the report text and the committed tables only.
3. **Coarse grid.** My intersection checks use the 1° × 25 NM grid of the window table (110 points). The run used 0.25° × 10 NM × 10 s. Band edges therefore differ by up to one coarse step.
4. **Provisional values.** The "independent shifts" values (section 2) and the Royer event B arrival at Diego Garcia South (section 7) are estimates from the grid and the empirical speed range. They are provisional.

## 1. Summary of verdicts

| # | Claim (short) | Verdict |
|---|---|---|
| 1 | Numbers in sections 1-3 match the sources | Holds, with 7 small corrections (section 1 table) |
| 2 | The time-slide null is valid, and look-elsewhere is inside the maximum | Holds with caveat. It is valid under the null hypothesis for space × impact time. It is conservative for short timelines. It does NOT cover the choice of statistic, geometry, window or method. Two post-hoc deviations from the specification are not stated in the headline report. |
| 3 | Every candidate is "weak" | Holds (none at p ≤ 0.05). But a single label hides Pete's 13 Oct tiers (screen 0.3, mark 0.1, report 0.05). Rank 2 stays in the 0.1 band in every sensitivity. Rank 1 does not. Some single-station p values are quoted too low. |
| 4 | Portland 3275 01:07:43: Royer A, B and 6 are ruled out; open path; predicted Cape Leeuwin windows | Holds with caveat. The ±6.8 s is too narrow, but the conclusion survives a much wider speed range. The reversal of two earlier associations (0.58 and 0.75) comes from a post-hoc method choice and must be stated. "No catalogued event" is weak evidence because the catalogue holds almost no ice events. |
| 5 | Rank 1 is driven by the Royer B member | Holds. It also depends on two path assumptions (rock leg for two members; a "large attenuation" Scott Reef path). The pair Diego Garcia South + Portland alone has global p ≥ 0.92. |
| 6 | Royer event B is about 494 km off the arc | Holds: 492.5 km from the arc line, about 400 km outside the ±50 NM band |
| 7 | Over- or under-confidence | 0.94 is the ceiling of the association calculation, not a near miss. "The method itself works" is untested end to end. The classifier has no ice class. The Kadri local p floor is a resolution limit, not a tail probability. |

## 2. Claim-by-claim

### Claim 1. Numbers in sections 1-3 against the sources

Most numbers match exactly. I checked: 0.080, 0.65/0.44 (0.6474/0.4396), 0.138, 0.155 (0.1548), 0.21-0.99 (0.2139-0.992), 13.8°, 343°, 964/913/51, airgun shot-population minimum 0.17, S10 local p 0.0043, impulsiveness local p 8e-4 (8.1e-4), W1 1.97, Royer 6 prediction 01:09:03.5 ± 6.8 s (offset −80.4 s), Royer A/B offsets 175/315 s, targeted p 0.98 (0.9785) and 0.87 (0.8676), the window times 00:35:21-01:06:50 (00:35:20.6-01:06:49.7) and 00:57:36-01:18:24, 110 arc points, 67 located known events, dive margins 20 s and 7 min 26 s, Kadri groups 18 and 36, Cape Leeuwin station-level p 0.011/0.045/0.388, classifier 87 %/57 %.

| Where | Report says | Source says | Suggested wording |
|---|---|---|---|
| §1, §3 rank 1 | network p 0.063 | 0.0635 (127 of 2,000 slides). The association report table says 0.064. Monte Carlo 95 % interval ±0.011 | "0.064 (127 of 2,000 slides; 95 % interval 0.053-0.074)" |
| §1 | the rank-1 value is the sensitivity case | The smallest sensitivity value is 0.053 (rock leg, best four, dive sub-range). The association report summary item 3 says the best is 0.063, which is wrong. Its limit 8 says 0.053. | Quote 0.053 as the smallest uncorrected sensitivity value |
| §2 dive row | "Only run 3 fits well (misfit 4.0 ... 5.9)" | 4.0 and 5.9 are without the delay prior ("acceptable"). With the delay prior, χ² is 23.9 and 25.7 ("marginal"), and run 4 with the Holland bias (22.3) is as good | "Run 3 fits best without the delay prior (misfit 4.0 / 5.9); with the delay prior all alternate runs are marginal or poor (χ² ≥ 22.3)" |
| §2 dive row | "Alternate dives that fit ... reach the sea 00:19:58-00:22:18" | That range covers ALL alternate runs, including poor fits (run 6, χ² 94-120). The acceptable and marginal runs alone give 00:19:58-00:22:17 | "All alternate runs (any fit quality) reach the sea at 00:19:58-00:22:18" |
| §2 dive row | normal runs without the 00:19 data, 00:28:00-00:43:07 | Not in the dive-fit table (its normal runs use the 00:19 data and reach the sea at 00:29:12-00:29:15) | Cite the outer-bound table that holds this range. Not checked here. |
| §2, §5 coverage | "30-42 %" (§2) and "28-42 %" (§5) | Grid per-cell coverage 18-45 %, station medians 33-39 %. The association report says 34 %. | Use one statement: "medians 33-39 % (18-45 % by arc cell)" |
| §3 rank 1 | "Inside the dive-fit range" | The band 00:19:38-00:21:18 starts 20 s before the dive-fit range | "Overlaps the dive-fit range" |
| §3 ranks 5-11 | 27-31 S | 27.25-31.25 S | "27-31.25 S" |
| Association §4.3(d) | energy 7.3-7.5 % | 5.6-7.5 % at 80 s blocks (S1: 0.056, 0.058, 0.075, 0.073) | "energy 5.6-7.5 %" |
| §1 Portland | "station-level p 0.046" | That is the best single detector (impulsiveness). The same row gives across-method p 0.091 and BH q 1.0. S10 gives station-global 0.19 and method-global 0.65. | See claim 3 |

I did not check (no source in the named tables): 31 bearing-only observations, 110 airgun shots, 220/210/217/158 back-projected transients, 124 classified transients.

### Claim 2. Is the cross-station time-slide null valid?

**What holds.**
- Look-elsewhere over arc cells and impact times is inside the maximum. Each slide takes the maximum over the whole dense grid. The run densified the whole span (decision 4), so no cell was selected first.
- **Fixing Cape Leeuwin does not bias p in either direction under the null hypothesis.** The test asks whether the other stations line up with the real Cape Leeuwin transients more often than chance. Cape Leeuwin's real transients, including the three capped onsets (Royer A, B and 5), are present in the observed data and in every slide. The test therefore has no bias. One consequence: the test detects ANY cross-station coherence. A real non-impact event that the catalogue does not remove also gives a small p. Section 7 shows that the catalogue cannot remove events matched by Royer figure marks.
- Circular shifts on the recorded timeline keep the duty cycle. A transient can only move to a time that was recorded.

**Caveats.**
1. **Short timelines give little decorrelation, so p is conservative for a real signal.** A slide breaks a coincidence only if it moves a transient by more than its impact-time interval. Median interval widths on open paths (`review_interval_widths.csv`): Portland 484 s (rock leg 640 s), Diego Garcia South 414 s (569 s), Scott Reef 256 s (412 s), Perth Canyon 198 s (353 s), Cape Leeuwin 205 s. The impact window is 606 s, so a Portland interval covers 80 % to all of it. From the timeline lengths (Diego Garcia South 1,200 s; loggers about 630-750 s from coverage × window), the number of independent shifts is about: Portland 1.1-1.5, Diego Garcia South 2.1-2.9, Scott Reef 1.5-2.4, Perth Canyon 2.1-3.8 (`review_independent_shifts_estimate.csv`, provisional). A member at Portland or Diego Garcia South thus adds almost no timing evidence. Its slid copy usually still fits. The effect makes p too HIGH for a true coincidence, not too low. The specification (§ "Report two values", item 6) asks for the **minimum achievable p** per record. The run does not report it.
2. **Two deviations from the pre-registered null are made after the windows were opened.** (a) IMOS: the specification takes the slid station's triggers from a background day at the same clock time. The run uses circular shifts on the event-day timeline instead (decision 2). (b) The specification sets a minimum offset of the largest lag spread + 60 s. The run uses 30 s (decision 3). Both changes make the null weaker, not more permissive. Both must be listed in the headline report's methods row.
3. **Look-elsewhere is NOT inside the maximum for the choice of statistic.** That choice covers k = 2, 3, 4 or all; base or rock-leg geometry; full or dive sub-range; five methods; and two association discounts. That is 16 time-slide variants alone. Rank 1 is the minimum over variants (it is a sensitivity, not the pre-registered statistic). Corrections for illustration only (Šidák): 0.0635 becomes 0.12 / 0.23 / 0.41 for 2 / 4 / 8 effective independent looks. The smallest value (0.053) becomes 0.10 / 0.20 / 0.35. The only confirmatory value is the pre-registered 0.080.
4. **Monte Carlo error.** 0.0635 ± 0.011 and 0.080 ± 0.012 (95 %, 2,000 slides). The stacking value 0.138 ± 0.030 (500 slides). The drop-one table uses about 400 slides; the report does not say so.

Verdict: **holds with caveat**. Suggested wording: "Network p values come from circular time slides on each station's recorded timeline, with Cape Leeuwin fixed. They include look-elsewhere over the arc cells and impact times, but not over the 16 statistic, geometry and window variants. Short records at Portland and Diego Garcia South decorrelate poorly, so the test is conservative there. These two choices replace the pre-registered background-day null and minimum offset."

### Claim 3. Is "weak" right for every candidate? Is any p too high or too low?

- **The label itself holds.** No value reaches 0.05, even before trial correction. The specification defines only a "detection claim" (exclusion p ≤ 0.01, two or more stations, after the known-event screen). The "potential" rule (inclusive p ≤ 0.05) is decision 7 of this run, so "the rule we set before the run" is not accurate. The pre-registered detection rule depends on the exclusion p, and this run showed that p is uninformative: 9 of 20 noise realisations (45 %, 95 % interval 23-68 %) gave ≤ 0.01. The pre-registered rule would therefore false-alarm about half the time. That is a real finding and belongs in the headline report as a deviation.
- **One label hides useful order.** Pete's 13 Oct 2026 ruling is "screen at 0.3, mark at 0.1, report at 0.05", with rank, p, SNR and likelihood ratio for every candidate rather than a tier verdict. Under that ruling:
  - Rank 2 (pre-registered, 0.080) is **marked**. It stays at or below 0.1 with the emergent-onset term (0.0989) and with the figure-mark discount (0.0989).
  - Rank 1 (0.0635) is marked only in its own sensitivity. It falls to 0.65 with the Royer B discount, so it is not robust.
  - Ranks 3-5 (0.138, 0.155, 0.214) are in the screen band. Ranks 6-11 are above 0.3.
  - The ranked table does not give SNR or likelihood ratio.
- **Values quoted too low (over-confident).**
  - The rank-1 0.063 is a selected sensitivity without trial correction (claim 2).
  - Portland 3275 "station-level p 0.046" is the best of six detectors. The across-method value at that station is 0.091. S10 gives station-global 0.19 and method-global 0.65. Over the seven stations with data, 0.046 becomes about 0.28, and 0.091 becomes about 0.49 (Šidák).
  - Cape Leeuwin local p 4e-6 is the floor of a block bootstrap built from only 440 s of off-window trace. It means "larger than anything that 440 s can make". It is not a tail probability. The 8 March trace itself holds three such onsets in 31.5 min, all at Royer events, so strong arrivals are common at Cape Leeuwin.
- **Values that may be too high (conservative).**
  - The time-slide p for coincidences that involve Portland or Diego Garcia South (claim 2, caveat 1).
  - The Diego Garcia South form-matched null, which is drawn from the record itself (the report says so).
  - The Cape Leeuwin station-level values at the floor (0.011), which are upper bounds.

Suggested wording: "No candidate reaches network p 0.05 (pre-registered statistic 0.080; smallest uncorrected sensitivity 0.053). Under the 0.3/0.1/0.05 tiers, the pre-registered candidate near 31 S is marked (p ≤ 0.10 in every sensitivity). The rock-leg four-station match is marked only before the Royer B discount (0.064, then 0.65)."

### Claim 4. Portland 3275 burst at 01:07:43

- **Open path: holds.** The check table gives the path open: shallowest 438 m outside the 50 km end zones, and 63 km shallower than 1,000 m outside the end zones. That agrees with "the first 113 km cross the shelf at 438-874 m", because 113 km minus the 50 km end zone is 63 km.
- **Royer 6 ruled out on timing: holds, but the ±6.8 s is too narrow.** The 6.8 s comes from the spread of the event's own picks. These come from two effective sites (Cape Leeuwin and the SWAMS triad), so the spread does not represent speed differences between directions. A wider test: across the Royer A, B and 6 picks the empirical speed is 1.467-1.507 km/s. With that whole range, Royer 6 reaches Portland 3275 at **01:08:10.5-01:09:07.6**. The burst is still 27-84 s early. To arrive at 01:07:43.1, the path must average **1.5265 km/s**, which is faster than every empirical speed in the table. A source-side rock leg cannot help, because it is common to all receivers and goes into Royer's origin time. Royer's formal errors (origin ±0.33 s; ±0.018°/±0.041°) are small.
- **Royer A and B: hold.** With the same speed range, A arrives at 01:03:54-01:05:11 and B at 01:02:06-01:03:12. The burst is 152-229 s and 271-337 s later.
- **Not stated: the reversal.** The screening run associated the burst with Royer A (0.58). The spectral run associated it with Royer 6 (0.75, ±44 s, with the 113 km catalogue rock leg). The association run reverses both. The cause is decision 8 (empirical speed from the event's own picks), made after the burst had been flagged. The physics favours the new result, but the headline must state the reversal and its cause.
- **"No catalogued event explains it": true, but weak evidence.** The known-event list holds 20 Royer events (6 icequakes) and 47 earthquakes from ISC, USGS, EMSC and GEOFON. It holds no ice catalogue for the Antarctic margin south of Australia, which Portland faces. The classifier also has no ice class. An unlisted ice event is therefore a live alternative that the data held cannot test.
- **Predicted Cape Leeuwin windows: hold** (00:37:29.5-00:44:27.9, best z 2.15, p 0.9785; independent speeds 00:35:34.8-00:48:23.7, p 0.8676). The report correctly does not count the quiet trace against the burst.

Suggested wording: "Royer events A, B and 6 do not explain the burst on timing. Even with the full range of empirical speeds (1.467-1.507 km/s), Royer 6 arrives 27-84 s later than the burst. The earlier associations (0.58 with A, 0.75 with 6) used catalogue windows and the 113 km rock leg; GEBCO shows that leg is water. The catalogue holds no ice events for the Antarctic margin south of Australia, and the classifier has no ice class. Thus an unlisted ice event remains possible."

### Claim 5. Is rank 1 driven by the Royer B member?

- **Holds.** The discount of the Cape Leeuwin 00:36:07.4 onset alone moves p from 0.0635 to 0.6474 (0.4396 in the dive sub-range).
- **Pair alone (Diego Garcia South 01:04:30 + Portland 01:07:43).** The pair weight is z 2.79 + 3.76 = 6.56. That is below the observed best-pair maximum (8.026), whose global p is 0.92 (base) and 0.941 (rock leg). So the pair's global p is **at least 0.92**. On the grid, the pair fits **40 of 110 points (30-38 S, all offsets, impact 00:19:38-00:25:07)** in the base geometry and 49 of 110 (30-39 S) with the rock leg. The Diego Garcia South member has station-level p 0.94. The pair therefore carries almost no location, time or detection information. This confirms the report's statement.
- **Missing dependencies.** At 30 S, +25 to +50 NM, the Cape Leeuwin member and the Scott Reef member both need the rock-leg branch. Their base impact-time upper bounds are 00:18:40 and 00:18:10, both before 00:19:38. Every Scott Reef path to the arc is "blocked" (59) or "large attenuation" (51). The four-site match exists only on large-attenuation Scott Reef paths. If those are skipped, the match goes away (`review_rank1_member_intersections.csv`). On the coarse grid, the four-site match fits only 2 of 110 points (30 S, +25 and +50 NM). In the base geometry, the triple Cape Leeuwin + Diego Garcia South + Portland fits only at 30-31 S, −50 NM, impact 00:19:38-00:20:07 (this is rank 3).

Suggested wording: "Rank 1 depends on three things: the Cape Leeuwin onset that Royer event B explains (without it p 0.65), the rock-leg branch for two of its four members, and a Scott Reef path classed 'large attenuation'. Without Cape Leeuwin, the Diego Garcia South + Portland pair fits 40 of 110 arc points, and its network p is at least 0.92."

### Claim 6. Royer event B is about 494 km off the arc

**Holds.** The distance from 35.224 S 99.922 E to the arc line is **492.5 km** (nearest at 32.3 S), and about 400 km outside the ±50 NM band. Royer's formal error (±0.076°/±0.022°) is under 10 km. Note: B's origin time (00:21:30.6) is inside the impact window, so its location is the only thing that separates it from an impact hypothesis. The report should say so. Suggested: "about 490 km from the arc line (400 km outside the ±50 NM band)".

### Claim 7. Over- and under-confidence elsewhere

1. **"Just below the 0.95 removal level" is wrong in kind (over-confident).** The figure-mark values fit P = L/(L + c), with L = exp(−dt²/(2·2²)) and c = 0.0638. This reproduces 0.94, 0.922, 0.801 and 0.074 at offsets of 0.0, 1.5, 3.3 and 6.5 s, and 0.938 at −0.5 s. At zero offset P = 0.94, which is the **largest value the calculation can give** at sd 2 s. The 0.95 removal level cannot be reached, so a figure mark can never remove a candidate, whatever the match. Pete's decision 1 should be framed this way: "an exact match gives 0.94, the ceiling".
2. **The two association sensitivities give identical results** (emergent-onset term and figure-mark discount: 0.0989, 0.3566, 0.5015, 0.1818). This is plausible: after either discount (z × 0.275 = 1.17 or z × 0.06 = 0.26), neighbouring weak Cape Leeuwin transients (z 1.8-2.15) fill the Cape Leeuwin slot. But it looks like a copy error, and the table should say why.
3. **Diego Garcia South members.** The rank-1 member (01:04:30.0) and the rank-2 member (01:08:29.7) are both classed "airgun shot" (envelope-only classifier, 57 % correct). Their station-level p values are 0.94 and 0.997. The headline report does not say this. Per the 23 Oct rule they stay in, but they must be labelled in §3. Provisional: the rank-2 member at 01:08:29.7 is inside the arrival range for Royer event B at Diego Garcia South (01:07:21-01:08:35 at 1.467-1.507 km/s; catalogue window 01:05:41-01:15:25, "ridge (partial)" path). The run did not test this. The rank-2 Portland member (01:20:31, z 3.6) is a call-like tone. Its Cape Leeuwin member has a bearing north of the arc span. Rank 2 is marked on p, but each strong member has a non-impact reading.
4. **"The method itself works" (over-confident).** The injections tested the single-station detectors. No report shows an end-to-end injection through back-projection, time slides and the network statistic. Suggested: "The single-station detectors find a broadband signal near 0 dB SNR on the two Kadri traces (energy test). The network stage has not yet been injection-tested."
5. **Classifier.** The 87 % (leave-one-group-out) is on full spectra. The whale, ship and airgun scores are optimistic, about half the earthquake labels may be chance matches, and there is no ice class. The class rules were defined after the windows were opened (specification D15). "Impact-like 0.68-0.94" mixes the version-2 score (0.68) with the window scores (0.85-0.94). Suggested: "broadband and impulsive (impact-like 0.68 by the version-2 rules; 0.85-0.94 by window). The classifier has no ice class, so an ice event would also score impact-like."
6. **Kadri form-matched null.** The false-alarm check runs on the same 440 s trace that feeds the bootstrap, so it is a self-consistency check, not an independent validation. The 95 % intervals are wide: 2.0-17.6 % at 55 looks and 4.2-7.3 % at 878 looks. Windows overlap, so the effective number of looks is smaller. With 20 s blocks, up to 11 %. Suggested: "5-8 % at 80 s blocks (95 % intervals up to 18 %); up to 11 % at 20 s blocks; checked on the same trace."
7. **Under-confident.** The report is too modest about one real finding: the pre-registered detection rule (exclusion p) false-alarms in about 45 % of noise realisations. That is a methods result worth stating in the paper.

## 3. Changes requested before the report goes to the paper

1. Replace "just below 0.95" with the ceiling statement (claim 7.1).
2. Put the pre-registered 0.080 first as the confirmatory value. Show rank 1 as a sensitivity, with its three dependencies.
3. State the two null deviations (background-day null and minimum offset) and the post-hoc "potential" rule. Report the minimum achievable p per record, as the specification requires.
4. Quote the Portland burst with across-method p 0.091 and S10 station-global 0.19 beside 0.046. State the reversal of the earlier associations and the absence of an ice catalogue and ice class.
5. Label the Diego Garcia South members as airgun-class, with their station-level p. Test rank 2's Diego Garcia South member against Royer B.
6. Apply the small number corrections in the claim 1 table.
7. Export the time-slide code to the repo (blocked step 4). Without it the network p values cannot be audited.

## 4. Files in this folder

- `reverse-sensing-report-review-2026-11-04.md`: this review
- `review_checks.py` and `review_checks_output.txt`: recomputation script and its output (inputs: arrival-window grid v6bfb80b1, known events v54883e6a, Kadri null calibration v09a5a788)
- `review_rank1_member_intersections.csv`: arc points that fit the rank-1 members, by geometry and path rule
- `review_interval_widths.csv`: median impact-time interval width per station
- `review_independent_shifts_estimate.csv`: estimated number of independent time-slide shifts (provisional)
