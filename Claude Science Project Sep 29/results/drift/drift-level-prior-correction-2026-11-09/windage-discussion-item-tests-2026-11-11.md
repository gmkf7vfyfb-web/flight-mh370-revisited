# Windage and delay: discussion, item-specific tests and delay calibration (11 Nov 2026)

## Summary (ASD-STE100)

- "Roy" is CSIRO's name for the engine cowling piece first seen at Mossel Bay on 23 Dec 2015. ATSB calls it Part No. 3.
- Nesterov (2018) gives windage as a function of the ratio of exposed to submerged area. His random model has a long upper tail. With my assumption on its draught factor, the median is 1.75 % and the 5–95 % range is 0.5–4.2 %.
- You are right about Paindane. The finder describes a waterlogged, heavy piece lying on the sand. This points to a recent beaching at the time of the find, not at the time of the report.
- The three early finds (Mossel Bay, Paindane, Vilanculos) carry almost all of the evidence for higher windage. Together at 3.0 % they give 4.8 of the 5.6 ln units of the class-wide gain.
- The two flap pieces (Mauritius, Pemba) prefer low windage. The exterior items do not share one windage level. A long right tail with most items near 1.2 % fits the data better than a shifted median.
- Mossel Bay alone, with a 50 % chance of the fast attitude for the whole drift, gains 1.7 ln units. Paindane and Mpame together gain 1.8 to 2.7. Neither explains the tension alone.
- The 8.6-day delay came from a 10-day "fresh" mark that I chose, combined with the 60-day delay. It is not a measured value.
- The delay data are too sparse to fix the mean. Two items were found within 2 days and two within about 3 weeks of arrival, out of twelve. The mean is 6 to 52 days, depending on how often a fresh arrival goes undocumented.
- The three widened log-normal targets (mean 1.2 %) were rescored. Their scoring was started, and the results were not read. See section 4.4.
- The class-wide two-component mixture scan was not started. See section 4.4.

## 1. What "Roy" is

- CSIRO Part I (Fig. 2.3.3 and sec. 2.3) uses "Roy" for the piece of engine cowling first seen at Mossel Bay, South Africa, on 23 Dec 2015. CSIRO built a replica of it.
- ATSB Update 2 calls the item Part No. 3: a segment of an engine cowling with a partial Rolls-Royce stencil.
- The project item identifier is `mossel-bay-engine-cowling-roy`. The replica is the same item in a drifter test, not a second object.
- CSIRO does not explain the name. The Rolls-Royce stencil is a likely origin. This is my inference, not a statement in the sources.
- The piece was seen on 23 Dec 2015 and found again on 21 to 22 Mar 2016 (Kruger). The model uses 23 Dec 2015. Nesterov (2018) discusses the item as the fourth object found, with arrival predicted for March to May 2016 and described as consistent with the discovery date.

## 2. Nesterov (2018): the area-ratio model

- Source: Nesterov, O. (2018), Ocean Science 14, 387–402, section 2.1.3 and 2.1.4.
- The object moves at (1 − α) times the water velocity plus α times the wind velocity. The leeway factor is α = √(ρa/ρw)·√k / (1 + √(ρa/ρw)·√k). Here k is the ratio of the area exposed to air to the area submerged, and the drag coefficients are taken as equal.
- Reference values: k = 1 (a thin plate floating flat) gives 3.33 %, close to the DGA flaperon value of 3.29 %. A 70 %-submerged cube gives 2.2 %. In my calculation k = 0.12, 0.34 and 0.75 give 1.2 %, 2.0 % and 2.9 %.
- Random model: the two parts of the object on each side of its principal axis have areas S1 and S2. Their logarithms are normal, with ln(S1/S2) distributed N(0, 1). A draught parameter γ in [0, 1] sets how deep the object floats (0: fully submerged; 1: centre of gravity at the surface). Then k = γ·S1 / (S2 + (1 − γ)·S1). Each particle keeps its value for the whole drift.
- The text I hold does not give the distribution of γ. I assumed uniform on [0, 1]. Figure 3 of the paper shows the result, and I could not read numbers from it.

| Assumption | p05 | p25 | median | p75 | p95 | mean | frac_above_3pct |
|---|---|---|---|---|---|---|---|
| gamma uniform 0-1 | 0.48 | 1.12 | 1.75 | 2.57 | 4.20 | 1.97 | 0.17 |
| gamma = 1 (no draught factor) | 1.49 | 2.41 | 3.34 | 4.62 | 7.29 | 3.73 | 0.59 |

- Percentiles are in % of the 10 m wind speed. My simulation: 2 million draws. The last column is the fraction above 3 %.
- Use for us: the form is physical, the area ratio is log-normal, and the draught factor adds a long upper tail and a lower tail. Our 1.2 % centre corresponds to k of about 0.12. The Nesterov distribution has a higher centre and a wider spread than our production prior. It does not include a separate Stokes term. Its α is the total effective windage, as ours is (ruling D-b).

## 3. Paindane

- Your reading is better than mine. The reports say that Liam Lötter spotted a grey piece washed up on the sand while strolling on a beach near Xai-Xai. The piece was "so waterlogged" and heavy. A CNN report of 11 Mar 2016 quotes "quite light", most likely from the finder; I read that as the weight after drying (my inference).
- A composite piece that holds water and then becomes light has dried after it left the water. This favours a short time ashore before the find. The length of that time is still unknown. A hollow fairing can stay full of water for some days on a beach.
- The report date (March 2016, after about ten weeks at home) does not enter the model. The model uses the find date.
- Date: the finder, AP, NBC, CNN give 30 Dec 2015. ATSB and the Malaysian summary give 27 Dec 2015. The model uses 27 Dec. With 30 Dec the find-date probability changes from 0.070 to 0.073 (60 d delay, production prior) and from 0.099 to 0.107 (no delay).
- Literature: the IPRC ocean drift model (Hawaii, 14 Mar 2016) simulated the 30 Dec find and the Paluma sandbank piece. It reports that the three pieces (including the flaperon) drifted low in the water, consistent with 0.8 % windage in that model.
- I classify the Paindane time ashore as class B: about 2 to 21 days, weak to moderate evidence (table in section 5).

## 4. Updating the windage model: discussion

### 4.1 Summary (ASD-STE100)

- Your proposal is sound. Keep the 1.2 % centre for low-exposure items. Widen the distribution. Do not truncate it. Allow a right tail.
- Stokes drift is part of the effective windage. It is in the wind-factor distribution and in any additional term (ruling D-b).
- The data support a long right tail with heterogeneity between items. They do not support one common shifted median.
- A mean-1.2 % log-normal widened to sigma 0.7 gains about 2 ln units. The best cell of the grid gains about 6.1.

### 4.2 Structure I suggest

The total effective windage of an item is the sum of three parts:

1. A wave-driven floor of about 1.2 %. CSIRO found that the total leeway of undrogued drifters equals the wave-model Stokes drift. Our Stokes review (WAVERYS with ERA5) gave an along-wind Stokes fraction of 1.23 to 1.30 % with a standard deviation of 0.32 to 0.40 %. The floor is therefore a property of the sea state, not of the item. Its spread is model error.
2. A direct wind term from the exposed area. It is zero or positive and has a right-skewed distribution, for example log-normal in the area ratio (Nesterov). Attitude changes this term. A flat-floating item with a larger exposed area has a larger term.
3. A shape-specific extra leeway, a constant-magnitude vector at an angle to the wind, as CSIRO measured for the flaperon (10 ± 3 cm/s). It exists only for shapes that interact with waves in that way.

In the present model, parts 1 and 2 are one windage factor, and part 3 exists only for the flaperon. Your idea has two forms:

- Form A (one wider factor): the distribution of the effective windage for each exterior item becomes log-normal or skewed, with a mean of 1.2 % and no truncation. Stokes drift and attitude are inside it. Cost: no new particle run (reweighting of the existing wide run).
- Form B (factor plus extra term): a narrow factor for the floor plus direct wind, and a flaperon-like extra term for flap and panel shapes. Stokes drift is in the factor. Cost: a new particle run.

My view: start with Form A as the paper's main treatment, with a hyperprior and item-level heterogeneity. Keep Form B for the sensitivity analysis and for the flap items. The reason is that the data cannot separate a wider factor from an extra term, because both change the speed of the item relative to the wind. The extra term changes the direction too, and that is the only way to tell them apart. Nearshore effects (tides, breaking waves, a coarse coast) change arrival, not open-ocean drift. They are better handled by the beaching kernel and a longer-range arrival term, not by windage.

### 4.3 What the stored results say (no new run)

Class-wide log-normal priors with sigma 0.25 to 0.7 and the log evidence (ln Z), from the earlier grid. The production-equivalent prior has ln Z = −182.91.

| Median (%) | sigma | Mean (%) | ln Z |
|---|---|---|---|
| 1.2 | 0.25 | 1.24 | −182.51 |
| 1.2 | 0.35 | 1.28 | −181.59 |
| 1.0 | 0.50 | 1.13 | −181.83 |
| 1.2 | 0.50 | 1.36 | −180.68 |
| 1.0 | 0.70 | 1.28 | −180.78 |
| 3.0 | 0.25 | 3.10 | −177.27 |
| 3.6 (higher-run particles) | 0.35 | 3.83 | −177.05 |
| 3.0 (higher-run particles) | 0.25 | 3.10 | −176.84 |

- A mean-1.2 % distribution widened to sigma 0.7 gains about 2.1 ln units against the production prior. The best cell (higher-run particles, median 3.0 %, sigma 0.25, ln Z = −176.84) gains 6.07.
- The truncation of the wide run is 0.3 to 5 % of wind speed. It is in the particles, not in the target. Values below 0.3 % exist in the production run only through the GlobCurrent offset.

### 4.4 Item-specific reweighting (done)

Method: each exterior item gets its own windage distribution. Each distribution is a log-normal target (sigma 0.35) of the reweighted wide run, or a mixture of the production-equivalent target and the 3.0 % target. The coefficients are linear in the particle weights, so a mixture of densities is the same mixture of coefficients. Validation: the class-wide cases reproduce the stored grid values with a maximum difference of 3.3e-6 in the log likelihood and the same ln Z to three decimals (−182.913 and −177.344). Four level-draw seeds (65,536 draws), 48 southern ocean samples, two ocean models at equal weight. Items not named keep the production-equivalent distribution.

Gain in ln Z of one item at its own median windage (all other items at 1.2 %):

| Exterior item (own median windage) | 1.5 % | 1.9 % | 2.4 % | 3.0 % |
|---|---|---|---|---|
| Mossel Bay | 1.03 | 1.52 | 1.94 | 2.28 |
| Paindane | 0.7 | 1.09 | 1.42 | 1.69 |
| Chidenguele | 0.45 | 0.71 | 0.91 | 1.04 |
| Vilanculos | 0.46 | 0.65 | 0.74 | 0.76 |
| Mpame | 0.34 | 0.47 | 0.53 | 0.53 |
| Nautilus Bay | 0.25 | 0.38 | 0.46 | 0.48 |
| Linga-Linga | 0.17 | 0.24 | 0.24 | 0.19 |
| Pemba | -0.09 | -0.21 | -0.43 | -0.73 |
| Mauritius | -0.29 | -0.55 | -0.87 | -1.22 |

Scenarios:

| Scenario | Gain in ln Z | Drift alone: median (° S) | North of 33° S (%) | Tension p (5–95 %) | With core: median / mean (° S) | With core: north of 33° S (%) |
|---|---|---|---|---|---|---|
| All nine exterior items at 3.0 % | 5.57 | 35.1 | 22.4 | 0.70 (0.60–0.79) | 36.2 / 36.14 | 2.3 |
| All nine at 2.4 % | 5.24 | 34.6 | 30.4 | 0.66 (0.53–0.76) | 36.1 / 36.01 | 3.5 |
| Mossel Bay, Paindane, Vilanculos at 3.0 % | 4.84 | 34.5 | 31.9 | 0.67 (0.50–0.94) | 36.1 / 35.93 | 3.8 |
| Mossel Bay, Paindane, Vilanculos at 2.4 % | 4.24 | 34.0 | 39.7 | 0.55 (0.38–0.82) | 36.0 / 35.81 | 5.3 |
| Those three and Mpame at 3.0 % | 5.24 | 34.5 | 30.4 | 0.59 (0.47–0.73) | 36.0 / 35.90 | 3.6 |
| Mossel Bay, Paindane, Mpame: 50 % chance of 3.0 % each | 3.32 | 33.9 | 40.5 | 0.46 (0.33–0.56) | 35.9 / 35.66 | 5.6 |
| Paindane and Mpame at 3.0 % | 2.68 | 32.2 | 57.3 | 0.20 (0.13–0.29) | 35.7 / 35.28 | 10.2 |
| Paindane and Mpame: 50 % chance of 3.0 % each | 1.81 | 31.8 | 60.8 | 0.17 (0.12–0.23) | 35.7 / 35.18 | 11.8 |
| Mossel Bay alone at 3.0 % | 2.28 | 32.1 | 58.4 | 0.19 (0.15–0.27) | 35.8 / 35.35 | 11.2 |
| Mossel Bay alone at 2.4 % | 1.94 | 31.7 | 61.7 | 0.16 (0.13–0.22) | 35.7 / 35.19 | 12.8 |
| Mossel Bay alone: 50 % chance of 3.0 % | 1.69 | 32.1 | 58.5 | 0.19 (0.15–0.28) | 35.8 / 35.30 | 11.5 |
| Paindane alone at 3.0 % | 1.69 | 31.6 | 62.0 | 0.15 (0.12–0.21) | 35.7 / 35.16 | 12.2 |
| Paindane alone: 50 % chance of 3.0 % | 1.19 | 31.5 | 63.7 | 0.15 (0.12–0.20) | 35.7 / 35.08 | 13.4 |
| All nine at 3.0 % except the three early finds | 0.15 | 32.7 | 53.9 | 0.22 (0.17–0.32) | 35.8 / 35.35 | 10.0 |
| Production-equivalent (all at 1.2 %) | 0.0 | 30.3 | 76.3 | 0.10 (0.08–0.10) | 35.4 / 34.36 | 23.5 |

- The production-equivalent case (wide-run particles reweighted to the production prior) gives a drift-alone median of 30.3° S and p = 0.095. The headline production run gives 30.1° S and p = 0.114. The difference comes from the 48-sample ocean ensemble of the wide run.
- The three early finds give 87 % of the class-wide gain (4.84 of 5.57). Without them the other six items gain 0.15 in total. Chidenguele (+1.04), Mpame (+0.53), Nautilus Bay (+0.48) and Linga-Linga (+0.19) gain a little. Mauritius (−1.22) and Pemba (−0.73) lose. The three early finds alone gain +2.28 (Mossel Bay), +1.69 (Paindane) and +0.76 (Vilanculos).
- Mossel Bay alone: a 50 % chance of the fast attitude for the whole drift gives +1.69 (a fast median of 3.0 %) and p = 0.19. The tension stays at about the production value. Mossel Bay alone cannot remove the tension.
- Paindane and Mpame together at 3.0 % give +2.68 and p = 0.20.
- Mossel Bay, Paindane and Mpame, each with a 50 % chance of 3.0 %, give +3.32 and p = 0.46. This is the largest gain among the attitude-only hypotheses that I tested. It rests on the CSIRO fairing result for Paindane and Mpame. For the cowling the attitude evidence is weaker: CSIRO reports two stable orientations for the replica and no measured difference in drift.
- The gains are not strictly additive, because the detection level is shared between items. The sum of the single-item gains at 3.0 % is 5.02, against 5.57 for all items together.
- Not run: the three widened log-normal targets with mean 1.2 % (sigma 0.85, 1.0, 1.2; medians 0.84, 0.73, 0.58 %). The reweighting and rescoring of the wide run on the deskstar finished without failure (73 s; the job log gives an effective sample size of 2,108 of 6,250 particles for the widest target). The Mac scoring of the three targets was started. I could not read its results, because the check on the log was not run. These results are not reported here.
- Not run: the class-wide two-component mixture (fraction pi at 3.0 % or 2.4 %, rest at 1.2 %, for all nine exterior items). The scan of ten scenarios was not started, because the launch was not run.

### 4.5 Reading

- The preference for high windage is item-specific. It appears for the early finds and reverses for the later flap pieces. A hierarchical model with item-level heterogeneity is the correct frame. The earlier class-level result (median 2.4 to 3.6 %) mixes two groups.
- This weakens the argument for one shifted class-wide distribution. It supports a skewed distribution with a long right tail, or a two-component mixture, with most items near the drifter-equivalent 1.2 %.
- A caution: with nine items and flexible item-level windage, the data can be fitted by many hypotheses. Each early item has a gain of 1 to 2.3 ln units, which is moderate evidence. A tension p of 0.46 to 0.70 in the scenarios that free the early items does not independently confirm windage. It shows that windage can absorb the early arrivals.
- Alternatives that the same data cannot reject: shorter delay (small effect), nearshore transport, a source farther north on the arc, a different date for Mossel Bay.

## 5. Delay: origin of 8.6 days, data and calibration

### 5.1 Where 8.6 days came from

- A fresh-arrival mark F multiplies the arrival-to-find probability by exp(−τ/F). With the 60-day delay D, the combined delay is exponential with mean D·F/(D + F).
- F = 10 days gives 8.57 days. F = 14 days gives 11.4 days. F = 3 days gives 2.86 days.
- F = 3, 10 and 14 days are my choices. The sources give a qualitative reason only. 8.6 days is therefore not a measured value and not a fit. I used it to show a short-delay case in the figure.

### 5.2 Data for time ashore before the find (the twelve items)

| item | class | time_ashore_range_used | evidence |
|---|---|---|---|
| Réunion flaperon (29 Jul 2015) | A | at most 2 d | Carried out of the surf by a municipal beach-maintenance team. |
| Mpame fairing (27 Jan 2017) | A | at most 2 d | Seen floating on the Friday afternoon; on the sand the next morning. |
| Mossel Bay cowling (23 Dec 2015) | B | 2 to 21 d | Photograph of 23 Dec 2015: barnacles dying, item smelled, only object on empty sand. |
| Paindane fairing (27 Dec 2015) | B | 2 to 21 d (weak) | Spotted washed up on the sand while strolling; heavy and waterlogged when found; described as light later (CNN, 11 Mar 2016). |
| Vilanculos panel (Feb 2016) | C | none | Sandbank accumulation site; marine growth present; no time-ashore information. |
| Mauritius flap (May 2016) | C | none | About 14 d between find and report: storage time, not time ashore before the find. |
| Rodrigues door panel (30 Mar 2016) | C | none | Found by tourists; no information. |
| Chidenguele cowling (24 Apr 2016) | C | none | Corrosion shows long exposure, not time ashore. |
| Antsiraka cabin panel (12 Jun 2016) | C | none | Item-specific information not found. |
| Pemba flap (Jun 2016) | C | none | Weak indication that it was taken from the water. |
| Linga-Linga stabilizer | C | none | No information used. |
| Nautilus Bay aileron (22 Dec 2016) | C | none | Found during a cricket game on the beach; no freshness evidence. |

- Class A: at most 2 days. Class B: 2 to 21 days. Class C: unknown. The class limits are my choices.
- I removed one entry from the earlier list. The 14 days of the Mauritius flap are storage after the find, not time ashore before it. Paindane's ten weeks at home are also after the find.
- All documented cases are documented because someone could see the item was fresh. This selects short times.

### 5.3 Calibration of a single exponential delay

Model: each item has time ashore T ~ exponential with mean D. An item is documented as class A or B with probability qA or qB, if its time falls in that class. Counts: A = 2, B = 2, C (undocumented) = 8. The likelihood for undocumented items is 1 − qA·P(A) − qB·P(B). Two priors on D. The table gives the posterior of D and the predictive delay (a mixture of exponentials over the posterior).

| case | prior | D_median | D_05 | D_95 | pred_mean | pred_median | pred_p90 | pred_p95 |
|---|---|---|---|---|---|---|---|---|
| documentation certain (q 1 / 1) | log-uniform prior | 52.1 | 24.6 | 139.1 | 63.2 | 36.2 | 148.5 | 212.0 |
| documentation certain (q 1 / 1) | prior centred on 60 d | 53.0 | 26.5 | 122.4 | 61.0 | 36.8 | 143.5 | 200.5 |
| q 0.9 / 0.5 | log-uniform prior | 18.0 | 5.1 | 59.5 | 23.5 | 11.8 | 56.5 | 84.2 |
| q 0.9 / 0.5 | prior centred on 60 d | 27.2 | 10.4 | 72.3 | 32.5 | 18.2 | 77.5 | 111.2 |
| q 0.7 / 0.3 | log-uniform prior | 8.5 | 2.9 | 31.8 | 11.9 | 6.0 | 28.5 | 43.2 |
| q 0.7 / 0.3 | prior centred on 60 d | 18.0 | 6.4 | 52.2 | 22.2 | 12.0 | 53.2 | 77.5 |
| q 0.5 / 0.25 | log-uniform prior | 6.0 | 2.4 | 23.0 | 8.6 | 4.2 | 20.2 | 30.8 |
| q 0.5 / 0.25 | prior centred on 60 d | 14.8 | 5.0 | 45.1 | 18.7 | 10.0 | 45.0 | 65.8 |

(Columns: q = documentation probabilities for A and B; D = mean delay of the exponential; "pred" = predictive delay for a new item; days.)

- If every fresh arrival were documented, the data would favour a mean near 52 days, and 60 days would be acceptable. This case is not realistic.
- If half or more of the fresh arrivals are documented, the mean falls to 6 to 27 days. Your estimate of 10 to 20 days lies inside the range for documentation probabilities of 0.5 to 0.9.
- The data alone cannot fix the mean. The unknown documentation probability controls the result.
- With a single exponential the data stay in tension: 2 of 12 items within 2 days is 17 %, against 3.3 % at 60 days and 12.5 % at 15 days. The data suggest a mixture: a fast component (frequented beaches) and a slow one (remote beaches).

Exponential delays for comparison (days):

| mean | median | p90 | p95 | P(<=2 d) | P(<=21 d) | P(>60 d) | P(>120 d) |
|---|---|---|---|---|---|---|---|
| 10.0 | 6.9 | 23.0 | 30.0 | 0.181 | 0.878 | 0.002 | 0.000 |
| 15.0 | 10.4 | 34.5 | 44.9 | 0.125 | 0.753 | 0.018 | 0.000 |
| 20.0 | 13.9 | 46.1 | 59.9 | 0.095 | 0.650 | 0.050 | 0.002 |
| 30.0 | 20.8 | 69.1 | 89.9 | 0.064 | 0.503 | 0.135 | 0.018 |
| 60.0 | 41.6 | 138.2 | 179.7 | 0.033 | 0.295 | 0.368 | 0.135 |

### 5.4 Effect on the early finds (probability that the predicted find date is no later than the observed date)

| prior | item | find_day | 60 d | 30 d | 20 d | 15 d | 10 d | 5 d | no delay |
|---|---|---|---|---|---|---|---|---|---|
| production prior | Mossel Bay | 655.5 | 0.043 | 0.05 | 0.054 | 0.057 | 0.06 | 0.064 | 0.067 |
| production prior | Paindane | 659.5 | 0.07 | 0.08 | 0.085 | 0.088 | 0.091 | 0.095 | 0.099 |
| production prior | Paindane, 30 Dec | 662.5 | 0.073 | 0.083 | 0.088 | 0.091 | 0.095 | 0.1 | 0.107 |
| production prior | Vilanculos | 722.5 | 0.19 | 0.22 | 0.234 | 0.242 | 0.249 | 0.257 | 0.263 |
| wide prior | Mossel Bay | 655.5 | 0.09 | 0.102 | 0.109 | 0.114 | 0.12 | 0.127 | 0.134 |
| wide prior | Paindane | 659.5 | 0.14 | 0.153 | 0.159 | 0.163 | 0.167 | 0.172 | 0.177 |
| wide prior | Paindane, 30 Dec | 662.5 | 0.142 | 0.156 | 0.163 | 0.167 | 0.171 | 0.177 | 0.185 |
| wide prior | Vilanculos | 722.5 | 0.276 | 0.31 | 0.325 | 0.333 | 0.34 | 0.347 | 0.353 |

- Production and wide windage prior, constant detection, two ocean models, core-weighted. The gain from 60 days to a 15-day mean is a factor of 1.3 for Mossel Bay and 1.3 for Paindane.

### 5.5 Recommendation

- Item-level evidence classes: A (mean 1 day) for the flaperon and Mpame; B (mean 7 days) for Mossel Bay and Paindane. These replace the mean of 60 days.
- General case (class C): an exponential with a mean of 20 days, with a log-uniform hyperprior of 8 to 60 days for sensitivity. This is within your range of 10 to 20 days and inside the calibration table. It is a judgement. It is not a fit.
- Report the delay result as a sensitivity band. A single value is not defensible with these data.

## Key assumptions and modelling choices

| Item | Value | Status |
|---|---|---|
| Item-specific windage targets | log-normal, sigma 0.35, medians 1.5, 1.9, 2.4, 3.0 %; mixtures with the production-equivalent target | my choice |
| Fast attitude median | 3.0 % | my choice; not measured |
| Attitude hypotheses | a mixture: 50 % chance that the item is in the fast attitude for the whole drift | my choice; a time average over the drift would shift the median instead (panel a) |
| Draught-factor distribution (Nesterov) | uniform on [0, 1] | my assumption; not in the text I read |
| Delay classes | A at most 2 d; B 2 to 21 d; C unknown | my choice |
| Documentation probabilities | qA, qB: 1/1, 0.9/0.5, 0.7/0.3, 0.5/0.25 | my assumption; not measured |
| Prior on mean delay | log-uniform 2 to 400 d, or centred on 60 d | my choice |
| Recommended delay | A 1 d, B 7 d, C 20 d | my judgement; not ruled |
| Windage convention | effective windage includes Stokes drift | Pete's ruling D-b, restated 11 Nov |
| Ocean ensemble | 48 southern samples, two models, equal weight | provisional |
| Detection prior | ramp 0.1, 0.5, 1, 1 | provisional |
| Core | final 7 Nov end-of-flight model, D0 | Pete's ruling |

## Decisions for you

1. Paindane class. Shall I classify Paindane as class B (2 to 21 days) in the delay model? My recommendation is yes. The finder's account supports it, and the effect on the result is small.
2. Delay model. Shall the headline use item-level evidence classes with a 20-day general mean, with 10 to 40 days as the sensitivity? My recommendation is yes. It matches the data better than 60 days and keeps the choice visible.
3. Windage treatment. Shall the main treatment be a skewed, untruncated distribution with item-level heterogeneity (Form A), with the extra-leeway form (Form B) as a sensitivity run on a new particle run? My recommendation is yes. A new particle run is a later decision for you.
4. Approval to read the results of the widened-target scoring and to run the class-wide mixture scan (about 20 minutes on the Mac, 8 GB per process). Both were not run in this turn, because the safety check on the commands did not run.
