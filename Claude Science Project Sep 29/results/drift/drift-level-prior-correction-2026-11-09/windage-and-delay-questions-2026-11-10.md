# Windage and delay: answers to eight questions (10 Nov 2026)

## Summary (ASD-STE100)

- I started no run. I did one short calculation on stored arrival tables (seconds) and one figure.
- A correction first. The two-attitude result in CSIRO Part I is for the fairing replica, not for the Mossel Bay cowling (Roy). It applies to the Paindane item and to Mpame (same part type).
- CSIRO reports no attitude test for Roy. It reports only an open-ocean trial of Roy, where Roy drifted slightly less than undrogued drifters.
- The flaperon extra leeway is shape-specific by CSIRO's own evidence. The fairing (concave down) did not show it in the same bay conditions.
- The centre of our exterior windage prior (1.2 %) comes from CSIRO. Its spread (0.3 %) and truncation (0.5–2 %) are my provisional choices. I found no source for them.
- The 60-day delay is not calibrated. A shorter delay helps, but it cannot explain the early finds: even with no delay the Mossel Bay probability rises only from 0.043 to 0.067 (production prior).
- The project has not used photographs for freeboard, orientation or growth zones. The literature has used them for the flaperon only.

## 1. Test the alternative attitude for the cowling?

- The sentence you quoted is about the fairing replica. Source: CSIRO Part I, section 2.3, printed pp. 6–7.
- CSIRO states that all three replicas (flaperon, Roy, fairing) have two stable orientations (p. 6). It reports a different drift rate for each orientation only for the fairing.
- Fairing, concave side up: it drifted away so fast that the team retrieved it. Concave side down: its drift could not be told from that of undrogued drifters.
- The test was in North West Bay: shallow, sheltered, gentle breeze, short waves. CSIRO never saw the wind pitch the fairing over, but thought it very likely (p. 7).
- In the open ocean (4 Oct 2016, about 20 kt, 48 h) Roy and the fairing moved 40 km while undrogued drifters moved 45 km. The attitude of each replica in that trial is not stated.
- Paindane (right No. 7 flap support fairing, Daghatane Beach) and Mpame are the same part type. The evidence for an attitude effect therefore supports Paindane better than Roy.

Technical note. Over about 650 days an item flips attitude many times. The effective windage is then (1 − x)·w_low + x·w_high, where x is the fraction of the time afloat in the fast attitude. A bimodal windage for each particle is justified only if one attitude lasts for months. CSIRO's own opinion (the wind pitches the concave-up fairing over) suggests that x is small in strong wind. The windage w_high was not measured. The data need an effective windage of about 2.5 % for Mossel Bay (early arrivals in the wide run have a mean of 2.6 %). If w_high were 3–4 % (my guess), x would have to be about 0.4–0.6 for months. That is a demanding hypothesis for Roy and a more plausible one for Paindane.

How to test it without a new run: reweight the stored particles with an item-specific windage prior. The rescorer now applies one set of weights to a whole class, so each find needs its own weights. That needs a small code change and about an hour of compute. I have not started it.

## 2. The extra leeway term of the flaperon

- CSIRO Part I assumed an extra 10 cm/s at zero wind that falls linearly to zero at 10 m/s. Part II used 13 field days and adopted a constant 10 cm/s, directed 10° to 20° left of the wind (Part II, section 3, printed p. 12).
- Our flaperon class uses 0.10 ± 0.03 m/s constant, with the angle uniform from −30° to 0° (rulings D-a and D-f). No other class has it.
- CSIRO attributes the extra term to the interaction of the raised tail with the waves (Part I, printed p. 7). That is specific to the shape.
- The fairing, concave side down, showed no extra drift in the same bay conditions where the flaperon did. No bay result is reported for Roy.
- Candidates for a flaperon-like term: flap sections and other control-surface pieces (Pemba outboard flap, Mauritius flap, wing trailing-edge panels). No measurement exists for them.
- Size. 10 cm/s equals about 1.4 % of a 7 m/s wind (my assumed typical wind). The inferred effective windage of 2.4–3.6 %, less the 1.2 % base, is 1.2–2.4 % or 8–17 cm/s at 7 m/s. That is the size of the measured flaperon extra term. The inference is therefore consistent with flaperon-like leeway on the exterior items. It is not proof, because an effective windage also absorbs other model error.
- To model it properly I need a new class with a constant-magnitude leeway and a new particle run. I have not started it.

## 3. How well informed are the windage distributions?

| Parameter | Value in the module | Source | Strength |
|---|---|---|---|
| Exterior centre | 1.2 % | CSIRO Part I, section 2.4 (undrogued drifters, BRAN2015 and wave model); Part III, printed p. 6. Our own drifter fits: 1.36 % (GLORYS12 with ERA5), 0.75 % (GlobCurrent) | Moderate for low-exposure items. Not measured for panels |
| Exterior spread and shape | normal, σ 0.3 %, truncated 0.5–2 % | My provisional choice. The configuration comment says "PROVISIONAL priors" | None |
| Interior class | log-normal, median 2.5 %, σ(log) 0.35, truncated 1–5 % | Provisional. Between CSIRO's 3 % class and the 0–5 % literature range | Weak |
| Flaperon | 1.2 % plus 10 ± 3 cm/s, angle −30° to 0° | CSIRO Part II (genuine flaperon) | Good for one item |
| Wide and higher priors | log-normal, medians 1.2 % and 2.4 % | My scenarios | Scenarios only |

- Literature. CSIRO Part III uses 0 %, 1.2 % and 3 %. CSIRO Part I quotes earlier studies at 0–5 %. Jansen et al. (2016) use 0–2.5 % in steps of 0.5 % and weight the members by the data (as our hierarchical inference does). Nesterov (2018) gives a physical model: the leeway factor follows from the ratio of exposed to submerged area, with a log-normal area ratio (σ of the log ratio = 1) and a draught factor. DGA's flaperon model gives 2.8–3.3 %.
- CSIRO's own later view (Griffin, 10 Aug 2018 web post "MH370 - drift analysis", one scanned page, file "V IMPORTANT GRIFFIN CSIRO AUG 2018.pdf" in the dissertation folder, read this turn): the African items are described as low-windage debris. The post lists, among its limitations, that drifters are not fit for modelling items at the surface (Stokes drift, wave forcing and wind forcing all differ) and that better Stokes-drift models and better treatment of an item's response to waves may change the picture. This supports a wider windage prior as a stated uncertainty. It gives no new windage value.
- The CSIRO replica trial supports "close to drifters" in strong wind (15–25 kt). It has no barnacles, damage or waterlogging, and the weak-wind behaviour of Roy and the fairing was not tested in the open ocean.
- The central value is defensible only as a drifter-equivalent for low-exposure items. The 0.5–2 % truncation is not defensible as a bound, because the data prefer 2.4–3.6 %.
- Flat-plate physics (3.3 %, equal exposed and submerged area) did not match CSIRO's flaperon measurements. Treat any area-ratio prior with care.
- Better options: (1) a physical prior on the area ratio per item (Nesterov form) with a hyperprior; (2) item-specific attitude mixtures; (3) a flotation test with the actual dimensions, as CSIRO did for the flaperon; (4) the hierarchical inference already done.

## 4. Mossel Bay, Paindane and Vilanculos

What the model uses:

| Item | Date used | Place used | Window | Delay | Detection level |
|---|---|---|---|---|---|
| Mossel Bay cowling | 23 Dec 2015 (day 655) | 22.150° E, 34.094° S | 1 day | exponential, mean 60 d | 0.5 (provisional) |
| Paindane fairing | 27 Dec 2015 (day 659) | 35.500° E, 24.078° S | 1 day | same | 0.5 |
| Vilanculos panel | 28 Feb 2016 (day 722); official 27 Feb is a shadow find | 35.519° E, 22.089° S | 1 day | same | 0.5 |

- Probability that the model find date is no later than observed (ramp detection, production and wide priors): Mossel Bay 0.020 and 0.040; Paindane 0.028 and 0.054; Vilanculos 0.092 and 0.137.
- Paindane: Liam Lötter found it near Xai-Xai. The official date is 27 Dec 2015. He and AP give 30 Dec. He said it was "so waterlogged … quite heavy". The family kept it for about ten weeks and reported it in March 2016. The model uses the first find date, not the date of recovery by the authorities. Jansen et al. do the same.
- Vilanculos: Gibson found it after a 20-minute search on an offshore sandbank. I found no time-ashore information. Pattiaratchi notes that abrasion on a sandbank removes fouling. A biologist quoted by Wise says "no fouling" means days to weeks in the water. That is weak, and ATSB found marine life on it.
- Hypotheses from the available information:
  1. High effective windage for the exterior class (tested; large effect).
  2. Attitude dependence of the fairing (CSIRO; fits Paindane).
  3. Flaperon-like extra leeway (flap and panel shapes).
  4. Short time ashore (fresh marks; modest effect, shown in section 6).
  5. Nearshore transport that the model lacks: 1/12° ocean grid, no tides, no wave-driven onshore transport, and a 50 km beaching kernel.
  6. A source further north on the arc (this is what the tension tests).
  7. Seasonal detection: Paindane was found in the Christmas holidays. An item that arrived earlier may have waited for visitors. This lengthens the delay and makes the early arrival harder to explain.
- Other literature with item information: Jansen et al. (2016) use December 2015 for the fairing and 27 February for the panel. CSIRO Part I (section 3.1) says only that the December finds are qualitatively consistent. Trinanes et al. (2016) put the Mozambique finds at 21 to 23 months. ATSB Update 1 says visible marine ecology was present on both parts. I found no published identification of that marine ecology in the files I hold, and I have not searched the 2018 final report beyond appendices 2.6A and 2.6B (flaperon barnacles).
- If you mean a specific statement about the time between beaching and recovery, tell me which source. I could not find one for either item beyond the above.

## 5. Photographs: freeboard, waterline, orientation, growth zones

- Used in the literature for the flaperon: Poupin (12 Aug 2015, Appendix 2.6A) read the barnacle positions as showing that it floated with its flat side up and the domed side submerged, and the size as 15–16 months of growth. DGA buoyancy tests gave the equilibrium waterline in both attitudes (Pengam 2016, shown in CSIRO Part I, Fig. 2.3.2). De Deckker (2017) read a temperature history from the barnacle shells.
- CSIRO built the Roy and fairing replicas with "realistic" waterlines (Part I, printed p. 4). The method is not stated.
- In this project: photographs serve as date evidence only (the 23 Dec 2015 Mossel Bay photograph). There is no freeboard, orientation or growth-zone analysis.
- What photographs can give: the attitude during growth (Lepas settle just below the waterline), the freeboard (the upper limit of the fouling or a waterline stain), and the time afloat (barnacle size). They cannot give the windage directly. An area ratio converts freeboard to windage: exposed-to-submerged area ratios of 0.12, 0.34 and 0.75 correspond to about 1.2 %, 2 % and 3 % (Nesterov form, my calculation). The flat-plate result of 3.3 % was not borne out by CSIRO's field data, so the conversion needs a flotation test.
- Limits: abrasion and sand cover, rotation after beaching, perspective, and unknown scale.
- What exists: ATSB Update 2, Fig. 3 (Mossel Bay, 23 Dec 2015); ATSB Update 1 figures; Gibson's and others' photographs; a commentator's note of a "very visible waterline" on the Pemba flap. The pieces are held by ATSB and the Malaysian team and could be measured and flotation-tested.
- My reading of the Mossel Bay photograph (one photograph, no measurement): the stencil face lies upward. Its centre is mostly free of barnacles and partly covered by sand. A ring of barnacles runs along the edge. This is compatible with a thin curved piece that floated low and nearly flat, with the waterline near the rim, and with the stencil face exposed to the air. It is not conclusive, because surf may have turned the piece over. If it is right, the exposed area was comparable to the submerged area and the windage would be high. This is a hypothesis to test, not a result.

## 6. The delay between arrival and discovery

Figure (same folder): `delay-distribution-working.png` (with source note) and `delay-distribution-jon.png` (Journal of Navigation form: greyscale, no title or note on the image, 127 mm wide). Caption for the JON version: (a) Exponential delay between arrival and discovery, mean 60 days, with 5,000 sampled delays (histogram) and the same distribution for a mean of 8.6 days (dashed). (b) Probability that the predicted find date is no later than the observed date, against the mean delay, for three early finds. (c) Mossel Bay cowling: arrival at the coast (grey), predicted discovery date for a mean delay of 60 days (black) and 8.6 days (dashed), and the observed find date.

- Form: exponential with mean 60 days. Median 42 d, 90th percentile 138 d, 95th percentile 180 d. 13.5 % of the mass lies beyond 120 d. There is no upper truncation. The find window is 1 day. An arrival counts only if the particle stays on the coast until the find.
- Origin: a design choice of the extended-window run. It lies between the literature (Durgadoo et al. allow 30 d and test 10 and 50 d) and the months that the Madagascar hand-ins imply. It is not calibrated.
- Direction. You are right: a longer assumed delay forces the arrival to be earlier, so it makes an early find more anomalous. The size is limited. The model arrives late: only 6.6 % (production prior) or 13 % (wide prior) of the Mossel Bay arrivals occur before 23 Dec 2015. The median predicted find date is 18 Oct 2016 (production prior) and 11 Sep 2016 (wide prior).

Probability that the predicted find date is no later than observed (constant detection, core-weighted, two ocean models):

| Item and prior | Mean 60 d | 30 d | 11.4 d | 8.6 d | 2.9 d | No delay |
|---|---|---|---|---|---|---|
| Mossel Bay, production | 0.043 | 0.050 | 0.059 | 0.061 | 0.065 | 0.067 |
| Mossel Bay, wide | 0.090 | 0.102 | 0.118 | 0.122 | 0.130 | 0.134 |
| Paindane, production | 0.070 | 0.080 | 0.090 | 0.092 | 0.097 | 0.099 |
| Paindane, wide | 0.140 | 0.153 | 0.166 | 0.168 | 0.174 | 0.177 |
| Vilanculos, production | 0.190 | 0.220 | 0.247 | 0.251 | 0.260 | 0.263 |
| Vilanculos, wide | 0.276 | 0.310 | 0.338 | 0.342 | 0.350 | 0.353 |

- The best case (no delay at all) raises the probability by a factor of about 1.5. The change from the production to the wide windage prior raises it by about 2.
- Calibration evidence on the time ashore: flaperon (carried out of the surf, hours), Mossel Bay on 23 Dec 2015 (dying barnacles, days), Mpame (seen floating the day before, under a day), Mauritius flap (about 14 days of storage before the report), Paindane (weak), Madagascar hand-ins (months). The rest is unknown. The documented cases are biased towards short times, because someone had to see the arrival.
- CSIRO treats non-reporting explicitly (Griffin, 10 Aug 2018): for crash sites north of 33° S, arrivals before December 2015 would have to remain undiscovered, and the post says the required non-reporting interval is longest (more than a year) for sites between 23° S and 21° S. For sites south of 24° S, it reports that the 10th percentile of the modelled beaching date is no more than 6 months before the earliest find. The post also states that the dates of first arrival on African shores are uncertain and that it is unclear whether items came ashore unnoticed in 2015. This agrees with our delay model in principle (a delay between arrival and discovery exists and is unknown). It gives no calibrated delay distribution.
- Recommendation: replace the global 60-day delay by an evidence class for each item: fresh (3–10 d) for the flaperon, Mossel Bay and Mpame; unknown (60 d, or a 30 d and 90 d mixture) for the rest; months for items held by finders. This needs offline rescoring only, no new run.

## 7. CSIRO windage classes and citations

CSIRO does not define formal classes. It uses these values:

- Drifter-like items: effective windage 1.2 % (the total leeway of undrogued drifters equals the wave-model Stokes drift). Part I, sections 2.3 and 2.4; Part II, section 2.3; Part III, printed p. 6 ("subject to Stokes Drift but not direct wind forcing").
- Windage factors of 0 %, 1.2 % and 3 %: deep-drafted items, items floating flat at the surface, items with substantial wind exposure. Part III, section 3.1, printed p. 8. Part IV uses 1.2 % and 3 % ("low" and "high").
- Flaperon: 1.2 % plus an extra 10 cm/s, 10–20° left of the wind. Part II, sections 2.3 and 3.
- Earlier studies: 0–5 %. Part I, printed p. 2.

- Later CSIRO statement (Griffin, D., 10 August 2018, "MH370 - drift analysis", web post; the cached copy is a single scanned page): the debris on African shores is called low-windage debris; the flaperon is the item for which drift tests exist. I found no new windage class in it.

Citations:
- Griffin, D.A., Oke, P.R. and Jones, E.M. (2016). The search for MH370 and ocean surface drift. CSIRO Oceans and Atmosphere, report EP167888, 8 Dec 2016, doi 10.4225/08/5892224dec08c (Part I).
- Griffin, D.A., Oke, P.R. and Jones, E.M. (2017). The search for MH370 and ocean surface drift – Part II. CSIRO, report EP172633, 13 Apr 2017, doi 10.4225/08/58fba83e73f2b.
- Griffin, D.A. and Oke, P.R. (2017). The search for MH370 and ocean surface drift – Part III. CSIRO, report EP174155, 26 Jun 2017.
- Griffin, D.A. and Oke, P.R. (2017). The search for MH370 and ocean surface drift – Part IV. CSIRO, report EP177204, 3 Oct 2017 (the title page gives 3 Oct; the citation line gives August 2017).
- Also cited above: Jansen, Coppini and Pinardi (2016), Nat. Hazards Earth Syst. Sci. 16, 1623–1628; Nesterov (2018), Ocean Sci. 14, 387–402; Pengam (2016), DGA, as quoted by CSIRO; Allen and Plourde (1999), as quoted by Jansen et al.

## 8. What I did not do, and what I propose

- I did not start a run, an estimate or a rescoring. The arrival-table calculation (seconds) and the figure are the only new computations.
- Proposed order, nothing started:
  1. Photo and geometry review of the early and anomalous items (Roy, Paindane, Vilanculos, Mauritius flap, Pemba flap).
  2. Item-specific windage priors by reweighting (about an hour): attitude mixture for the fairing items (Paindane, Mpame), then Roy.
  3. Evidence-class delay model (offline rescoring).
  4. A flaperon-like class for flap-type items (needs a new particle run; plan it with the other methodology questions).

## Key assumptions and modelling choices

| Item | Value | Status |
|---|---|---|
| Delay | exponential, mean 60 d | provisional (not calibrated) |
| Exterior windage | normal 1.2 % ± 0.3 %, truncated 0.5–2 % | provisional; centre from CSIRO, spread and truncation mine |
| Fresh marks | 3, 8.6, 11.4 d (60 d combined with 3, 10, 14 d marks) | my choice |
| Figure, section 6 | production prior, constant detection, kernel 50 km, two ocean models at equal weight | my choice |
| Typical wind for the leeway comparison | 7 m/s | my assumption |
| w_high of the fairing and 0.4–0.6 time fraction | guess | my assumption, not measured |
| Reading of the Mossel Bay photograph | low, nearly flat float | my visual reading; unverified |
| Core | final 7 Nov end-of-flight model, D0 | Pete's ruling |

## Decisions for you

1. Which item-specific hypotheses to test first. My recommendation: the fairing attitude mixture (Paindane, Mpame), then the same for Roy as a declared hypothesis, then a flaperon-like class for flap-type items. Reason: CSIRO's measurement supports the fairing case, and each test is cheap by reweighting except the flaperon-like class.
2. Whether I may use the original photographs (ATSB or Malaysian team) for a freeboard and orientation review. Reason: freeboard decides whether 1.2 % or 3 % is physical, and the project holds only the published images.
3. Whether to replace the global 60-day delay by the evidence-class model. Reason: it changes the early-find probabilities by up to a factor of 1.5 and is the only part of the arrival-to-find chain that has documented evidence.
