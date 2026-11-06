# Independent review of the combined-detector run on 8 March 2014 (pre-registration item C)

Date: 6 November 2026. Inputs reviewed: combined-detector-2014-results.zip (code, outputs, pre-registration v1.0) and combined-detector-2014-results.md.
Method: reading of all code in the package, recomputation of every reported number from the CSV and NPY outputs, and one read-only check of the raw cache (background file time ranges). No reruns were made, because sigdet.py and ns/paths_lib are not in the package. The package was not modified.

## Verdict

The detection result stands. The network statistic, time-shift null, global p and BH are coded correctly; the observed and null statistics use the same code path; every reported number was reproduced from the package files (global p 0.93 primary, 0.67 wide; smallest BH q 0.98 and 1.00; 6/19 and 17/19 Kadri fits; coverage 0.45/0.48; all SNR50 and null-rate tables). No issue found is anti-conservative enough to hide or create a detection. The sensitivity statements need revision: injections whiten with the clean noise record (optimistic, mainly for the impact-lag correlation that sets the best SNR50 values); co-located loggers count as separate stations and share a shift, so the Perth Canyon 1 + 2 network row does not apply and site-based two-IMOS coverage is 0.40/0.43, not 0.45/0.48; summary item 7 reads as an exclusion. Four pre-registered items changed without declaration (time-slide design, Kadri null, 3 and 5 Nov seeds, 3315 cross-check). In the seeded test, the co-located partner of an IMOS seed should also be excluded.

Severity scale: would-change-conclusion / minor / cosmetic. No finding is rated would-change-conclusion.

## Findings

| # | Item | Status | Severity |
|---|---|---|---|
| 1. | Network statistic, Fisher combination, k>=2 rule, time-shift null, global p (network14.py, run14.py) | PASS | none |
| 1a. | Co-located loggers count as separate stations and share one time shift | ISSUE | minor |
| 1b. | Seeded test keeps the co-located partner of an IMOS seed | ISSUE | minor |
| 1c. | Cyclic wrap length for IMOS is not a multiple of 900 s | ISSUE | minor |
| 1d. | Benjamini-Hochberg | PASS | cosmetic |
| 2. | Recomputation of report numbers from the CSVs | PASS | none |
| 2a. | Coverage by independent sites | ISSUE | minor |
| 3a. | Injection whitening uses the clean host record (oracle noise reference) | ISSUE | minor |
| 3b. | Same records for calibration and injection background (in-sample) | ISSUE | minor |
| 3c. | SNR scaling and injection window | PASS | none |
| 3d. | 'EQ real' control construction | ISSUE | cosmetic |
| 3e. | Network-pair sensitivity | ISSUE | minor |
| 4. | imos_calib.py TailMap and window-max calibration | PASS | minor |
| 5a. | Summary item 7 reads as an exclusion | ISSUE | minor |
| 5b. | Cape Leeuwin envelope 'only 00:47:04 stands out (p 0.0056)' | ISSUE | minor |
| 5c. | Smaller wording mismatches | ISSUE | cosmetic |
| 6a. | Time-slide design differs from pre-registration B6 and is not declared | ISSUE | minor |
| 6b. | Kadri envelope null differs from B2 and is not declared | ISSUE | minor |
| 6c. | Promised seeds missing | ISSUE | minor |
| 6d. | 3315 site-partner cross-check not done | ISSUE | minor |
| 6e. | Whitener exclusion width | ISSUE | cosmetic |
| 6f. | Declared omissions | PASS | none |


### 1. Network statistic, Fisher combination, k>=2 rule, time-shift null, global p (network14.py, run14.py)

Status: PASS. Severity: none.

Per-station window p uses the same WindowCal map in the observed and the shifted evaluations. evaluate(None) and evaluate(shifts) run the same code path (cyclic wrap with shift 0 returns the original times). Fisher combination is chi2.sf(-2 sum ln p, 2k) over stations with data and an open path. g2 = max over hypotheses with k>=2. Global p = (count(null >= obs)+1)/(N+1). IMOS shifts are 900 s x {2..8} x {+1,-1}; Kadri shifts are uniform 300 s to L-300 s, cyclic. Global p recomputed from the .npy files: 0.9291 (primary), 0.6723 (wide); 95th percentiles 3.393 and 3.079. All match global_results.csv and the report.

### 1a. Co-located loggers count as separate stations and share one time shift

Status: ISSUE. Severity: minor.

GROUP puts 3315+3376 (Perth Canyon) and 3274+3275 (Portland) on one shift. This keeps their joint noise in the null, which is correct. But k>=2 can then be met by one site only: 951 hypotheses (2.8 % of those with k>=2) have no second site (their largest evidence is 0.75, so this run is not affected). A signal seen only by the two loggers of one site keeps its coincidence in every shifted series. Some shifted series then contain it at another impact time, so such a signal can never pass the global test. The report's network-sensitivity row 'Perth Canyon 1 + Perth Canyon 2' (2.7-3.9 dB) therefore does not apply. Also, the loggers record in complementary slots of each 15 min (3315 at about 0-307 s, 3376 at about 303-610 s; 3274 at about 0-307 s, 3275 at about 285-592 s). Both loggers record the same short arrival only near the slot boundary.

Suggested fix: Define network evidence as at least two independent sites. Remove the Perth Canyon 1 + Perth Canyon 2 row from the network-sensitivity table (or mark it as not a network detection). Report coverage by sites as well.

### 1b. Seeded test keeps the co-located partner of an IMOS seed

Status: ISSUE. Severity: minor.

The seed station is correctly removed from both the observed and the null statistic (lpo = tot - LP[seed station], same masks). But for a seed at 3274/3275/3315/3376, the co-located partner stays in. In the null the partner shifts by at least 30 min against the fixed seed time, so the null breaks a local seed-partner coincidence that the observed data keep. This is anti-conservative for IMOS seeds. It contradicts pre-registration B7 ('independent data'). No seed came close (smallest q 0.98), so the conclusion does not change.

Suggested fix: Exclude the whole site group of the seed station (GROUP[seed station]) in both the observed and the null seed statistic.

### 1c. Cyclic wrap length for IMOS is not a multiple of 900 s

Status: ISSUE. Severity: minor.

cyc = (t_min, t_max+450) with look times t0+15..t0+290. The wrap length is then about 900(N-1)+725 s, so wrapped records land about 175 s off the logger's own 15-min recording phase. 3376 and 3275 start at 00:05 UTC on 8 March. For positive shifts, the 00:20-01:40 arrival span therefore reads wrapped end-of-day records at a changed duty-cycle phase relative to the other loggers. This changes the coverage pattern in part of the null. The direction of the effect is not known. It is probably small.

Suggested fix: Wrap over a length that is an integer number of 900 s cycles (e.g. L = 900*ceil((t_max - t_min + 1)/900)), or shift only within the contiguous data without wrap.

### 1d. Benjamini-Hochberg

Status: PASS. Severity: cosmetic.

The BH step-up is correct (recomputed q matches bh_q exactly in both files). It is applied over the seeds with a finite statistic: 58 (primary) and 59 (wide), not 62. Four seeds (primary) and three (wide) have no consistent hypothesis with other-station data: Kadri 00:47:04, Kadri 00:49:41, IMOS3250 01:49:14.9 and (primary only) IMOS3274 01:00:44.5. Smallest q: 0.977 and 0.997.

Suggested fix: State 'BH over 58 (primary) and 59 (wide) seeds that could be tested'; change '124 seed tests' to 117.

### 2. Recomputation of report numbers from the CSVs

Status: PASS. Severity: none.

All reproduced exactly: global p 0.93/0.67/0.94 and k>=1 0.93/0.72/0.95; largest evidence 1.57/1.77; thresholds 3.39/3.08; hypothesis counts 43,318 = 2,706 + 40,612; Kadri fits 6/19 dive and 17/19 glide (primary); 00:54:30 window 00:32:38-00:40:08, 25-26 S, -150 to +150 NM; seeded p (0.078, 0.25, 0.69, 0.78, 0.18, 0.031, 0.42, 0.50, 0.86, 0.82); coverage 1.00/1.00/0.45 (dive) and 0.97/0.77/0.48 (glide), after 00:40 0.43-0.55; known-time SNR50 at 5 % and 1 % (all 25 cells each); pure-null pass rates 0.040-0.055, 3315 0.085, all 0.056 and 0.204; network pair SNR50 table; Cape Leeuwin envelope 4.8 % of points with p <= 0.05; SNR-reference offsets 0.23-0.42 dB, Scott Reef 2.08 dB. One gap: at 3315 the 1 % SNR50 for 'EQ real' is not reached by +30 dB (NaN); the report does not say this.

### 2a. Coverage by independent sites

Status: ISSUE. Severity: minor.

'Two or more IMOS loggers' (0.45 dive, 0.48 glide) counts co-located pairs. Counted by independent IMOS sites (Perth Canyon, Portland, Scott Reef), the shares are 0.40 (dive) and 0.43 (glide). Two or more sites of any kind: 1.00 (dive) and 0.75 (glide).

Suggested fix: Report site-based coverage beside logger-based coverage in section 3.6 and summary item 7.

### 3a. Injection whitening uses the clean host record (oracle noise reference)

Status: ISSUE. Severity: minor.

imos_inject.case calls record_stats(y, ..., xref=x). The AR(60) whiteners and the lag bank for the impact-lag correlation (cimp) therefore come from the noise-only record. On the real data (xref=None) they come from the record itself outside +/-30 s, and that part contains any signal tail longer than 30 s (R3 with sub-events lasts 15-60 s; the earthquake control is 150 s long). The other components (band energy, templates, shape, persistence) use y and are realistic. cimp carries the best sensitivities: single-component SNR50 for cimp is -7.6 dB (3376), -7.8 dB (3275) and -11.4 dB (3315), against -7.5, -4.5 and -1.9 dB combined. The Perth Canyon 1 figure (-7.9 dB) and three of the four network pairs depend on it. The bias is optimistic. Its size is not known.

Suggested fix: Re-run the injections with xref=None (whitener from the signal-plus-noise record, as on the real data). Until then, label the SNR50 values in summary items 5-7 and sections 3.5 as provisional upper bounds on sensitivity.

### 3b. Same records for calibration and injection background (in-sample)

Status: ISSUE. Severity: minor.

Host records come from null_records(lg), the same records that built the point maps and window-max tables. For 3250/3274/3376 (1,344 records) the effect is negligible. For 3315 (92) and 3275 (89) the host is about 1 % of the calibration set. More important: the split-half check shows 3275 is optimistic out of sample (0.082 at 5 %, 0.037 at 1 %). The in-sample injection hides this, so P_D for 3275 at a true 5 % false-alarm rate is lower than reported. The pure-null binomial statement ('2.3 sd') also treats 200 cases as independent, but they reuse 92 records.

Suggested fix: Use leave-one-record-out (or split-half) calibration for injections at 3315 and 3275, or state P_D at the split-half-corrected levels.

### 3c. SNR scaling and injection window

Status: PASS. Severity: none.

SNR = peak 30 s 8-40 Hz signal energy over the median 30 s noise energy of the host record. This is as declared in departure 1. p_combined is the window-max p over looks centred in [t0-10, t0+60] s (70 s, about 14-15 looks), calibrated for that look count. This is as declared in departure 5.

### 3d. 'EQ real' control construction

Status: ISSUE. Severity: cosmetic.

170 distinct earthquake T-phases from H01W/H08S (band SNR > 30 dB) are tapered, placed with the peak about 40 s after t0, and multiplied by the IMOS gain shape. The IMS instrument response is not removed and no path filter to the IMOS range is applied (dist_km is stored but not used). It is therefore a waveform-shape control, not a path-matched one. The helper inject.real_signal is not in the package.

Suggested fix: State this in the figure footnote and the methods.

### 3e. Network-pair sensitivity

Status: ISSUE. Severity: minor.

The code that produced network_detection_snr.csv is not in the package. As described, it Fisher-combines two known-time logger p values and compares the result with 3.39. It ignores the extra noise terms from other stations that cover the same hypothesis; these add degrees of freedom and raise the required SNR. Scott Reef has no clear paths (all 'large attenuation' or blocked), but the injection draws Scott Reef ranges from non-blocked points without extra attenuation. Received-SNR statements are still valid, but the report's 'two loggers with clear paths' is wrong for the two Scott Reef pairs.

Suggested fix: Add the generator script. Either run an end-to-end injection through network_scores, or state the dilution caveat. Change 'clear paths' to 'open paths'.

### 4. imos_calib.py TailMap and window-max calibration

Status: PASS. Severity: minor.

TailMap: empirical (n-rank+1)/(n+1) below the 90th percentile; 0.1 x GPD sf above it (exceedance share is m/n = 0.1). There is no discontinuity at u. The Fisher F is re-calibrated on background, so no chi-square assumption is made at station level. Window max: one random window per record for each length 1-56, empirical p with floor 1/(n+1). Beyond the sample maximum it uses min(empirical, n_looks x point-tail p), which is a Bonferroni bound and conservative given the GPD. Points to note: (i) for 3315 (floor 1/93 = 0.0108) and 3275 (1/90 = 0.0111) the 1 % level cannot be reached empirically and needs the Bonferroni-on-GPD bound. This, not a 'heavy noise tail', explains the 29 dB value at 3315. (ii) If a GPD fit has shape < 0, values beyond its endpoint get p = 1e-15. This did not happen on 8 March (smallest point p in the series is 6.4e-8, 3315 persistence). (iii) The split-half check tests point-level p_F only, not the window-max p that the network uses, and its output is not saved. (iv) The background files for 3250/3274/3376 contain no record in 8 March 00:15-02:00 (checked in the cache).

Suggested fix: Correct the 29 dB explanation. Save the split-half table. Add a split-half check of the window-max p. Run the declared A6 empirical-floor sensitivity.

### 5a. Summary item 7 reads as an exclusion

Status: ISSUE. Severity: minor.

'The null result therefore excludes, at about 50 % detection probability, only impacts that gave SNR of roughly 2-6 dB...' A 50 % detection probability does not exclude anything: half of such impacts would be missed. The sentence also conflicts with item 8 ('not evidence against impact').

Suggested fix: Write: 'The run had about 50 % probability to detect an impact that gave 2-6 dB (8-40 Hz) at two IMOS sites with open paths, for the 40-43 % of hypotheses that two IMOS sites covered. It excludes nothing.'

### 5b. Cape Leeuwin envelope 'only 00:47:04 stands out (p 0.0056)'

Status: ISSUE. Severity: minor.

The reported values are the minimum point p within +/-15 s (7 looks) of each Kadri time; p at the nearest look is 0.014 (00:47:04), 0.10 (00:54:30), 0.19 (00:39:53), 0.17 (00:51:50). There is no correction for 19 transients x 7 correlated looks, and the rank-p floor is 1/355. 'Stands out' overstates one look-up among about 19 x 7.

Suggested fix: State that it is the minimum of 7 looks, give the nearest-look value, and say it is not significant after allowing for 19 transients.

### 5c. Smaller wording mismatches

Status: ISSUE. Severity: cosmetic.

(i) '5 per station (31)': four stations gave 4 seeds. (ii) 'BH over 62 seeds' and '124 seed tests': 58/59 and 117 (see 1d). (iii) Best hypotheses 'at 23-34 S, +100 to +150 NM': the top 20 span 20-34 S and -50 to +150 NM. (iv) 'Per 5 s look over a 2 min window': imosdet uses 30 s analysis windows on a 5 s grid; the 2 min element is not visible in the package (sigdet not included). (v) Screening seeds contain near-duplicates (00:36:07.4/00:36:07.5; 00:51:50, 00:51:58, 00:52:03). These inflate the BH count slightly (conservative).

Suggested fix: Correct the wording; mark duplicate seeds.

### 6a. Time-slide design differs from pre-registration B6 and is not declared

Status: ISSUE. Severity: minor.

B6: 'each station shifted by an independent random offset of 20-120 min, wrapped within its own data'. Implemented: shifts per site group (co-located loggers together); IMOS 30-120 min in 15 min steps (14 values per group); Kadri uniform 5 min to (trace length - 5 min) on 29.5 min (Cape Leeuwin) and 19.4 min (Diego Garcia South) traces. Section 2 describes the method but section 5 does not list it as a departure. The changes are reasonable (Kadri traces are shorter than 20 min shifts allow) but must be declared.

Suggested fix: Add to section 5 with reasons.

### 6b. Kadri envelope null differs from B2 and is not declared

Status: ISSUE. Severity: minor.

B2 promised a 'form-matched block bootstrap of the off-window trace (as validated 4 Nov)'. kadrienv uses point ranks within the whole trace and random windows within the trace (in-sample, including the Kadri transients). This is probably conservative, but it is a different method.

Suggested fix: Declare it as a departure, or run the pre-registered bootstrap as a sensitivity.

### 6c. Promised seeds missing

Status: ISSUE. Severity: minor.

B7 lists 'the best network cells of 3 Nov and 5 Nov' as seeds. seeds.csv has none. The Portland 3275 burst is present (screening IMOS3275 01:07:43.1). The omission is not declared.

Suggested fix: Add the 3 Nov and 5 Nov best cells as seeds, or declare the omission.

### 6d. 3315 site-partner cross-check not done

Status: ISSUE. Severity: minor.

B4: 3315 and 3275 are 'cross-checked with the site partner'. Only 3275 was re-run on Portland 1 noise (global p 0.94). 3315 was not re-run on 3376 noise, although its pure-null rate (0.085 at 5 %) and -20 dB rate (0.107) are high. Not declared.

Suggested fix: Run the 3315-on-3376-noise sensitivity, or declare it.

### 6e. Whitener exclusion width

Status: ISSUE. Severity: cosmetic.

A4 says 'window +/-15 s excluded' for the whitener; imosdet excludes +/-30 s. Not declared. The effect is negligible.

Suggested fix: Declare.

### 6f. Declared omissions

Status: PASS. Severity: none.

A6 (Pareto versus empirical-floor sensitivity) and B8 (known-event labelling) are declared as not done in section 5.4. The -20 dB null-check problem and the added pure-null check are declared (5.2).

## Recomputed values (from the package files)

| Quantity | Report | Recomputed |
|---|---|---|
| Global p, k>=2 (primary / wide / 3275 on 3274 noise) | 0.93 / 0.67 / 0.94 | 0.9291 / 0.6723 / 0.9421 |
| Global p, k>=1 | 0.93 / 0.72 / 0.95 | 0.9311 / 0.7163 / 0.9491 |
| 5 % global threshold (primary / wide) | 3.39 / 3.08 | 3.393 / 3.079 |
| Smallest BH q (primary / wide) | 0.98 / 1.00 | 0.977 (58 seeds) / 0.997 (59 seeds) |
| Kadri fits, primary (dive / glide) | 6 / 17 of 19 | 6 / 17 of 19 |
| Two or more IMOS loggers (dive / glide) | 0.45 / 0.48 | 0.454 / 0.481 |
| Two or more IMOS sites (dive / glide) | not reported | 0.396 / 0.425 |
| Two or more sites, any kind (dive / glide) | not reported | 1.000 / 0.748 |
| Pure-null pass at 5 %, all loggers | 0.056 | 0.056 |
| Cape Leeuwin points with p <= 0.05 | 4.8 % | 4.79 % |
| Single-component SNR50, cimp (3376 / 3275 / 3315) | not reported | -7.6 / -7.8 / -11.4 dB |
| Combined SNR50 over all families (3376 / 3275 / 3315) | not reported | -7.5 / -4.5 / -1.9 dB |

The known-time SNR50 tables (5 % and 1 %) and the network-pair table match the CSV files cell by cell.

## Scope notes

- No rerun was possible (sigdet.py, ns/paths_lib, inject.py, kadri_table1.csv, grid_ext_paths.csv and imos_calib.pkl are not in the package). The split-half table (report 3.1) and the generator of network_detection_snr.csv could therefore not be checked.
- The direction of the oracle-whitener bias (finding 3a) is certain from the code; its size is not measured.