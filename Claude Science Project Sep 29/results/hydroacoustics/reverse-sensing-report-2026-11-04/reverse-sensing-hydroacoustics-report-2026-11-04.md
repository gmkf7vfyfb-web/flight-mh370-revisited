# Reverse sensing of the 8 March 2014 hydroacoustic data: first run

Date: 4-5 Nov 2026. Status: exploratory, first full run. Independently reviewed (review /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/27f2e089-f5fb-4dd1-b963-8b0ef7af0f08/v59e60da6_reverse-sensing-report-review-2026-11-04.md, commit 3f1465a9); its corrections are applied in this version. Language: ASD-STE100 for work-specific text.
Condition: every result here is conditional on the Boeing alternate-configuration dive hypothesis and the impact window 00:19:38-00:29:44 UTC.

## 1. Result in brief

- No candidate reaches a network-global p of 0.05 or less after look-elsewhere. Every candidate is therefore **weak**. None is a **potential** detection under the rule we set before the run.
- The strongest multi-station item is a match of four stations near **29.5-30.5 S, impact 00:19:38-00:21:18**. It has network p 0.064 (127 of 2,000 slides; Monte Carlo ±0.011) in a sensitivity case that allows a fast rock leg near the receiver. It also needs the rock leg for two members and a 'large attenuation' Scott Reef path. Its Cape Leeuwin member (00:36:07.4) is at the pick bar for Royer 2016 event B (association 0.94, which is the ceiling of the association formula at zero offset). If that member is discounted, p is 0.65. The Diego Garcia South and Portland pair alone has global p of 0.92 or more and fits 40 of 110 arc points.
- The pre-registered network statistic gives its best value near **31.0-31.25 S, impact 00:28:18-00:28:38**, with p 0.080 (0.099 with the emergent-onset term). Under the project's 0.3 / 0.1 / 0.05 reporting tiers this is in the 0.05-0.1 tier. The smallest of all sensitivity p-values is 0.053 (rock-leg, best four, dive sub-range); with a Šidák correction for 2, 4 or 8 variants it becomes 0.12, 0.23 or 0.41.
- The most impact-like single item in the data held is the **Portland logger 3275 burst at 01:07:43**: classed impact-like, spectral weight 1.97. Its p is 0.046 for the best of six detectors, 0.091 across methods, and 0.19 station-global for the spectral search. No catalogued event explains it. Royer events A, B and 6 are ruled out on timing. The event 6 path is open on GEBCO; with the empirical speed range (1.467-1.507 km/s) event 6 arrives 27-84 s after the burst, and it would need 1.527 km/s, faster than any observed speed. The earlier associations (0.58 with Royer A, 0.75 with Royer 6) were reversed by a method choice made after the windows were open (own-pick speeds); this is stated as a post-hoc change. Where this burst predicts an arrival at Cape Leeuwin, the trace shows only weak transients (targeted p 0.98). We use no level model, so that quiet trace does not count against the burst.
- Single-station injections show that a broadband signal near 0 dB SNR is found at the two Kadri traces. No end-to-end network injection test has been run, so the network stage is not yet shown to recover a planted signal. The data held limit the result: about one third time coverage at the loggers, envelopes only at Cape Leeuwin and Diego Garcia South, and raw-logger station-level sensitivity worse than +12 dB.

## 2. What was done

| Step | Result | Repo commit | Main artifact |
|---|---|---|---|
| Dive window | Alternate dives that fit both 00:19 BFO treatments reach the sea 00:19:58-00:22:18. The ruled window holds all of them (20 s early margin, 7 min 26 s late margin). Only run 3 fits well without the log-on delay prior (misfit 4.0 with Holland transient bias added, 5.9 as observed); with the prior it is marginal (23.9 / 25.7). Without the 00:19 data, normal runs reach the sea 00:28:00-00:43:07. | 15549f19 | {{artifact:522e7a21-1f1b-4cab-a410-f0256ca847b7}} |
| Arrival windows and data | 110 arc points (20-41 S, 0/±25/±50 NM), speeds 1.40-1.56 km/s, 0-5 % detour, rock-leg branch. Cape Leeuwin window 00:35:21-01:06:50; Diego Garcia South 00:57:36-01:18:24; IMOS loggers 30-42 % covered. 67 located known events, 31 bearing-only observations, 110 airgun shots. | 264a9a4 | {{artifact:ee87a04e-e02a-4812-b632-92ad36bb91a7}} |
| Methods (fixed before any window was opened) | Eight screening detectors (S1-S8), cross-station time slides (B1), stacking (C1), unique-transient search (C2), analogue shape (C3), change points (C4). Amendment 1: spectral-shape weight (rank only). Amendment 2: spectral-template search S10 and source classifier (added after screening began; parameters fixed before running). Amendment 3: primary-secondary pair test. | ddc20bd, 709b2da1, d748fff | {{artifact:bb5c3068-491c-4347-9dba-68b07017bd9e}} |
| Screening | 964 weak candidates; 913 kept; 51 removed (Royer located events, one whale call). Airgun shot-population test: no unusual shot (lowest global p 0.17). | 3c3ff40d | {{artifact:ae4c6ebc-1dc2-49c1-ba19-9a9484a6027e}} |
| Spectral search and classifier | S10: 7 weak single-station candidates, none at station-global p 0.05. Classifier 87 % correct on raw data (57 % envelope only). | b11c0ecd, a7d4b12a | {{artifact:f8a6ba0c-3782-4060-96af-ece8f941e51d}} |
| Association | 220 transients back-projected; 210 map to the arc. Best network p 0.064 (sensitivity) and 0.080 (pre-registered). | 6bd9cac7 | {{artifact:2246484e-03a5-4b01-aedc-543837f326c9}} |

## 3. Ranked candidates (all weak)

| Rank | Method | Stations | Arc band | Impact time | Network p | Notes |
|---|---|---|---|---|---|---|
| 1 | Time-slide coincidence, rock-leg case | Cape Leeuwin 00:36:07, Diego Garcia South 01:04:30, Portland 01:07:43, Scott Reef 00:48:48 | 29.5-30.5 S, +20 to +50 NM | 00:19:38-00:21:18 | 0.064 | Inside the dive-fit range. Cape Leeuwin member = Royer event B pick bar (0.94); with that discount p 0.65 (0.44 in the dive sub-range). Diego Garcia South member is airgun-class (station p 0.94). |
| 2 | Time-slide coincidence, pre-registered | 8 sites, led by Cape Leeuwin 00:46:57 | 31.0-31.25 S, +40 to +50 NM | 00:28:18-00:28:38 | 0.080 | Outside the dive-fit range, inside the ruled window. Published Cape Leeuwin bearing (343°) points north of the arc span; it needs an array bias of 13.8° or more (known bias +8 to +13°). Diego Garcia South member (01:08:29.7, station p 0.997, airgun-class) may be Royer event B (predicted 01:07:21-01:08:35; provisional). |
| 3 | Stacking | Cape Leeuwin, Diego Garcia South, Portland | 29.5-31.0 S, -50 to -10 NM | 00:19:38-00:20:28 | 0.138 | Same three transients as rank 1. |
| 4 | Unique-transient search | Cape Leeuwin, Perth Canyon, Portland | 37.75-39.25 S | 00:19:38-00:22:28 | 0.155 | |
| 5-11 | Other methods and cells | | 27-31 S | | 0.21-0.99 | See the ranked table. |

Single-station item of note: Portland 3275 at 01:07:43 (impulsiveness local p 8.4e-5; best-of-six station p 0.046; across-method p 0.091; S10 local p 0.0043, station-global 0.19; impact-like 0.68-0.94). Charts: {{artifact:1fa76cd4-c10e-4d8d-9fa1-63ddd44960a4}}, {{artifact:b401876f-d8d3-47eb-b54e-74a71b0ab2ee}}, {{artifact:2e975fbb-3c59-4f58-a7a7-a46fd92b4c3d}}. Full ranked table: {{artifact:64d0e2db-e4af-4809-9bdf-7c450c0137c0}}.

**Reading of the pattern.** Three of the top four items use the same arc segment near 30 S and an early impact time. That segment and time fall inside the dive fits (run 3 reaches the sea at 00:20:04-00:20:05). But the match rests on one Cape Leeuwin transient that Royer's pick for event B also explains. Royer located event B at 35.22 S 99.92 E, origin 00:21:30.6, which is 492.5 km from the arc line and about 400 km outside the ±50 NM band. Without that member, the Diego Garcia South and Portland pair alone carries little location information. The honest status is "weak, depends on one disputed member".

## 4. Steps blocked and decisions for Pete

Blocked by the unavailable platform safety check. We did not retry them another way. Each needs Pete's approval to re-run:
1. Amendment 3 primary-secondary pair test on the top candidates.
2. Build of the full single-station back-projection table.
3. Re-render of the screening timeline-chart footnotes.
4. Export of the screening and association analysis cells to the repo as scripts.

Decisions for Pete:
1. **Royer figure pick bars.** They match Cape Leeuwin 00:36:07.4 (event B, 0.94) and 00:51:58.3 (event A, 0.92). Should these figure marks join the pre-registered catalogue? If yes, candidate 1 falls to p 0.65.
2. **The 0.95 removal level cannot be reached by timing alone.** With a 2 s timing sd and the background-rate term, the association formula has a ceiling of 0.94 at zero offset. A timing-only match is therefore never removed. Options: keep it (most data kept), or change the formula so that an exact match with a located event can reach 0.95.
3. **Emergent-onset association term** (lag 0-30 s after a pick). As a sensitivity it gives association 0.725 and moves the primary p from 0.080 to 0.099. Adopt it or not.

## 5. Limits

- Conditional on the dive hypothesis window. With the 00:19 data held out, the normal-configuration impacts (00:28-00:43) need a later window.
- Data held: IMOS loggers record 307 s in every 15 min (28-42 % of each window); Cape Leeuwin and Diego Garcia South are digitised envelopes only (Kadri 2024 Fig. 9); OHASISBIO sites are picks and spectrogram colours only.
- Sensitivity: about 0 dB SNR50 at the Kadri traces (energy test); worse than +12 dB at every raw logger at station level.
- The Kadri-trace persistence and combined tests needed a form-matched null (block bootstrap, 80 s; 5-8 % false alarms per look). The screening values under the older null were anti-conservative and are replaced.
- Classifier: ice class untrained; earthquake labels provisional (about half may be chance matches). Natural long-range arrivals also score impact-like, so catalogue timing must separate them.
- Sensitivity p-values (best-k, rock-leg, dive sub-range) are not corrected for the number of sensitivities.
- Propagation is used for travel time only. No amplitude or level model is used anywhere.
- The pre-registered detection rule (excluded-background p of 0.01 or less) is not usable: it gives 0.01 or less in 9 of 20 noise realisations. The 'potential' rule used here (inclusive network p of 0.05 or less) is post hoc and needs Pete's ruling as an amendment.
- Two changes to the pre-registered null were made after the windows were open: circular slides on each station's recorded event-day timeline, and a 30 s minimum shift. Portland and Diego Garcia South give only about 1-3 independent shifts (provisional), so the test is conservative there.
- Look-elsewhere covers all cells and impact times, but not the 16 statistic, geometry and window variants.
- The time-slide and back-projection code is in the session record only, not yet in the repo, so the reviewer could not audit the null code directly. There is no ice catalogue, and the classifier has no ice class.

## 6. Proposed next steps

1. **Approve the four blocked steps.** The pair test is the most informative: it uses a lag that does not depend on propagation.
2. **Add an end-to-end network injection test**, so the network stage is shown to recover a planted signal before any result is used.
3. **Rule on the three decisions** in section 4, and on the 'potential' rule.
4. **Run the same pipeline on the held-out window** (00:28-00:43, normal-configuration impacts), with no code change.
5. **Package the pipeline for raw IMS data** (Kadri / CTBTO), because the envelopes limit both sensitivity and the waveform methods.
