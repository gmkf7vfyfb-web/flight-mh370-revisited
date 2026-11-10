# Fresh-arrival marks: evidence basis and sensitivity (ocean drift, 10 Nov 2026)

Pete's question (10 Nov 2026): the Paindane fairing mark of 14 days ashore, and the 3-day and 10-day marks for the flaperon, have no stated reason. Test them against the delay distribution that is normally sampled.

## Summary (ASD-STE100)

- The marks are not in the headline result. The headline uses an exponential delay of mean 60 days between arrival and discovery for every find.
- The marks are comparison cases. I added them on 7 Nov 2026, after Pete asked about marine life on the finds. They are written to the rescored coefficients only.
- The sources give a qualitative reason for the flaperon and for the Mossel Bay cowling on 23 Dec 2015. They do not give a number of days.
- The Paindane reason is weak. It is one inference: the fairing was waterlogged.
- The numbers 3, 10 and 14 days are my choices for the classes "fresh" and "days to weeks". No source states them.
- The effect of the flaperon mark does not depend on 3 days or 10 days. The two values give nearly the same result.
- The marks move the drift latitude south and raise the tension p-value. The three marks together move the production-prior median from 30.1° S to 33.5–33.6° S and p from 0.11 to 0.41–0.46.
- No new drift run was needed. All cases are offline rescorings of the stored beachings.
- The run on deskstar was not touched.

## 1. What a mark is

- A mark F (days) says: the item was found soon after it came ashore.
- The model multiplies the probability of the arrival time by exp(−τ/F), where τ is the time ashore.
- The delay then has mean D·F/(D+F), with D = 60 days. F = 3, 10 and 14 days give 2.9, 8.6 and 11.4 days.
- The class total is unchanged. Only the find term changes.
- The marks were written as shadow finds in the module's coefficient file (`fresh_days` in the rescoring configuration). The headline never selects a shadow.

## 2. Evidence for each mark (from `debris-find-freshness.md`, 7 Nov 2026)

| Item | What the sources say | Class used | Number of days |
|---|---|---|---|
| Flaperon, Réunion, 29 Jul 2015 | A municipal beach-maintenance team carried it out of the surf. The press reports barnacles on it. | fresh (hours to a few days) | 3 and 10: my choice; no source gives a number |
| Mossel Bay cowling, 23 Dec 2015 | Photograph of 23 Dec 2015 (ATSB). The barnacles were dying and the item smelled. | fresh | 3 and 10: my choice |
| Paindane fairing, 27 Dec 2015 (official date) | The finder said that it was so waterlogged that it was heavy. The press gives 30 Dec 2015. ATSB found marine life on it. | days to weeks | 14: my choice; the evidence is one inference |
| Mpame fairing, 27 Jan 2017 | Seen floating on the Friday afternoon. On the sand next morning. | fresh | no mark was implemented |
| Other items | No direct evidence of time ashore. | unknown | none |

- Waterlogging shows that the part had not dried out ashore. It does not show how long the part was at sea. This is why I rate the Paindane evidence as weak.
- The flaperon evidence is qualitative. The sources do not say how often the beach is cleaned.

## 3. Method

- Coefficients: the rescored coefficients of 8–10 Nov 2026 (production run, wide run, higher-windage run). The shadow finds for the flaperon (3 d, 10 d), Mossel Bay (3 d, 10 d) and Paindane (14 d) were already in them.
- Each case swaps one original item for its shadow in the headline set of twelve items. The other items are unchanged. The identity weight of the shadow equals that of the original.
- Level marginalisation: seeds 1, 2 and 3 (49,152 draws per point). The headline case uses the same seeds, so the comparison is paired.
- Smoothing, bootstrap (400) and tension as for the headline (scripts `fresh_stage1_*.py`, `fresh_stage2_*.py`). The headline reproduces the 16-seed values (p 0.114, 0.330 and 0.569 against 0.109, 0.320 and 0.566).
- The three-day flaperon mark gives an exact zero likelihood in some ocean samples at the northern release points: 70 of 2,016 (GlobCurrent) and 42 of 2,016 (GLORYS12) point-and-sample entries. They count as zero. When all selected samples of a bootstrap replicate are zero, the smoother uses the lowest level seen divided by the number of samples. The ten-day case has no zero and gives the same result.

## 4. Results (drift alone, two ocean models at equal weight)

Production windage prior, normal 1.2 % ± 0.3 %, truncated 0.5–2 %:

| Time-ashore case | Median (° S) | North of 33° S (%) | Tension p (5–95 % bootstrap) | ln Z against headline |
|---|---|---|---|---|
| 60-day delay for every find (headline) | 30.1 | 73 | 0.114 (0.10–0.13) | +0.00 |
| Flaperon fresh mark 3 days | 31.9 | 59 | 0.212 (0.16–0.31) | +0.15 |
| Flaperon fresh mark 10 days | 31.8 | 61 | 0.200 (0.15–0.27) | +0.21 |
| Mossel Bay fresh mark 3 days | 30.9 | 67 | 0.159 (0.12–0.23) | +0.78 |
| Mossel Bay fresh mark 10 days | 31.0 | 66 | 0.159 (0.12–0.23) | +0.65 |
| Paindane fresh mark 14 days | 30.8 | 68 | 0.144 (0.11–0.21) | +0.53 |
| Marks 3 / 3 / 14 days (flaperon, Mossel Bay, Paindane) | 33.6 | 44 | 0.410 (0.28–0.61) | +1.48 |
| Marks 10 / 10 / 14 days (flaperon, Mossel Bay, Paindane) | 33.5 | 46 | 0.460 (0.28–0.63) | +1.37 |

Wide windage prior, log-normal median 1.2 %, σ(log) 0.5, truncated 0.3–5 %:

| Time-ashore case | Median (° S) | North of 33° S (%) | Tension p (5–95 % bootstrap) | ln Z against headline |
|---|---|---|---|---|
| 60-day delay for every find (headline) | 33.3 | 48 | 0.330 (0.25–0.42) | +0.00 |
| Flaperon fresh mark 3 days | 34.0 | 39 | 0.505 (0.36–0.68) | +0.33 |
| Flaperon fresh mark 10 days | 34.0 | 37 | 0.490 (0.37–0.62) | +0.39 |
| Mossel Bay fresh mark 3 days | 33.7 | 43 | 0.416 (0.28–0.60) | +0.70 |
| Mossel Bay fresh mark 10 days | 33.9 | 40 | 0.456 (0.32–0.60) | +0.63 |
| Paindane fresh mark 14 days | 33.6 | 44 | 0.378 (0.26–0.55) | +0.46 |
| Marks 3 / 3 / 14 days (flaperon, Mossel Bay, Paindane) | 34.6 | 29 | 0.611 (0.43–0.77) | +1.48 |
| Marks 10 / 10 / 14 days (flaperon, Mossel Bay, Paindane) | 34.8 | 26 | 0.621 (0.51–0.71) | +1.50 |

Higher windage prior, log-normal median 2.4 %, σ(log) 0.35, truncated 0.8–6 %:

| Time-ashore case | Median (° S) | North of 33° S (%) | Tension p (5–95 % bootstrap) | ln Z against headline |
|---|---|---|---|---|
| 60-day delay for every find (headline) | 34.6 | 30 | 0.569 (0.50–0.65) | +0.00 |
| Flaperon fresh mark 3 days | 34.9 | 27 | 0.647 (0.55–0.83) | +0.27 |
| Flaperon fresh mark 10 days | 35.0 | 25 | 0.661 (0.57–0.76) | +0.35 |
| Mossel Bay fresh mark 3 days | 34.9 | 26 | 0.639 (0.52–0.76) | +0.70 |
| Mossel Bay fresh mark 10 days | 34.9 | 25 | 0.624 (0.54–0.72) | +0.58 |
| Paindane fresh mark 14 days | 34.9 | 25 | 0.595 (0.52–0.67) | +0.30 |
| Marks 3 / 3 / 14 days (flaperon, Mossel Bay, Paindane) | 35.4 | 20 | 0.762 (0.58–1.00) | +1.32 |
| Marks 10 / 10 / 14 days (flaperon, Mossel Bay, Paindane) | 35.5 | 17 | 0.670 (0.58–0.78) | +1.25 |

Table `fresh-arrival-marks-sensitivity.csv` has the same values with the unrounded ln Z, ln S and the bootstrap intervals of the median.

## 5. Reading

- Paindane alone (14 days): the median moves 0.7° south (production prior), p from 0.114 to 0.144. The effect is small.
- Flaperon alone: the median moves 1.7–1.8° south (production prior) and p from 0.114 to 0.20–0.21. The effect is larger than for Paindane. It does not depend on 3 or 10 days.
- Mossel Bay alone: 0.8–0.9° south, p 0.159.
- The effects add up approximately. The three marks together give 33.5–33.6° S and p 0.41–0.46 (production prior), 34.6–34.8° S and p 0.61–0.62 (wide prior), 35.4–35.5° S and p 0.67–0.76 (higher prior).
- The size of the effect depends on the windage prior. It is largest for the production prior, which has the least windage freedom.
- The ln Z differences (+0.15 to +1.5) are not evidence for the marks. A mark adds an observation (found fresh), so the data differ between cases. Only the shifts of the latitude and of the p-value are meaningful.
- The earlier README sensitivity (section 4, "Fresh-arrival marks 10/10/14 d; 3/3/14 d") tested the three marks only together, with the core and with the production prior. This note separates them and adds the wide and higher priors.

## 6. Limits

- Three seeds, and the 32 ocean samples at the southern release points. Seed noise of p is about 0.01 at the production prior.
- Only 14 days was available for Paindane. Other values (3, 7, 30 days) need a new rescoring on deskstar. I will do this after the run ends, so that the run is not disturbed.
- The Mpame arrival is documented but has no mark. A shadow needs a rescoring of the wide legs after the run ends.
- The marks are applied one item at a time, with the date of each item as in the headline. The Mossel Bay date is not yet ruled by Pete (23 Dec 2015 against 21–22 Mar 2016). The Mossel Bay mark applies to the 23 Dec 2015 date only.

## 7. Recommendation (technical judgement; the headline composition is Pete's decision)

- Keep the 60-day delay for every find in the headline until Pete decides. It ignores the documented evidence, so it is conservative.
- Do not use the Paindane mark in any headline. Show it as a sensitivity. Its evidence is weak and its effect is small.
- Report the flaperon and Mossel Bay marks (3–10 days) as a documented, evidence-informed variant. The result does not depend on the value within 3–10 days.
- Decide the marks together with the Mossel Bay date, because the two choices interact.

## Key assumptions and modelling choices

| Item | Value | Status |
|---|---|---|
| Delay between arrival and discovery | exponential, mean 60 days | provisional (headline; from the extended-window run) |
| Flaperon mark | 3 d and 10 d | my choice (class "fresh"; no numeric source) |
| Mossel Bay mark | 3 d and 10 d, 23 Dec 2015 date | my choice; the date is not ruled by Pete |
| Paindane mark | 14 d | my choice (class "days to weeks"; weak evidence) |
| Mark form | P(fresh given time ashore) = exp(−τ/F), class total unchanged | my choice (module design of 7 Nov 2026) |
| Identity weight of a shadow | same as the original item | my choice |
| Detection prior | ramp, period medians 0.1 / 0.5 / 1 / 1, σ = 1 | provisional |
| Windage priors | production, wide, higher | provisional (Pete's decision pending) |
| Seeds | 1, 2, 3 (49,152 draws) | my choice (smoke-test depth) |
| Zero-likelihood samples | counted as zero; floor in the bootstrap if all are zero | my choice |
| Core | final 7 Nov end-of-flight model, D0 | Pete's ruling |

## Files

- `fresh-arrival-marks-sensitivity.csv`
- scripts `fresh_stage1_prod.py`, `fresh_stage1_wide.py`, `fresh_stage1_high.py`, `fresh_stage2_prod.py`, `fresh_stage2_wide.py`, `fresh_stage2_high.py`, `fresh_runner.py`
- source note: `debris-find-freshness.md` (artifact version 24628161-30e4-4b2d-af12-4f4be7204987)
