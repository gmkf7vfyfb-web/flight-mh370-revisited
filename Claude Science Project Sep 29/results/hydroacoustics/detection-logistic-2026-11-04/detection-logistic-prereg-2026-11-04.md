# Pre-registration: heard / not-heard logistic regression for hydroacoustic detection

Run folder: `results/hydroacoustics/detection-logistic-2026-11-04/`. Written 4 Nov 2026 BEFORE any model in this run was fitted.
Author: Hydroacoustic Module session 9891b08e (independent check of the step 2 separation gate; it does not edit the files of the overnight session).
Status of this run: EXPLORATORY, UNCHECKED until an independent verifier passes.

## 1. Purpose

1. Test, by an independent method, criterion C of the step 2 gate (heard / not-heard separation), with cross-validation and intervals.
2. Fit an empirical detection curve that does not use the transmission-loss model (Pete has low confidence in it).
3. Find whether the frozen chain adds skill over that curve.
4. Give a predictive band for the probability that an MH370 impact was heard at Cape Leeuwin (H01W) and Diego Garcia South (H08S), along the 7th arc.
This is a calibration / measurement product. It does not change the composer, likelihood code or any ruled value.

## 2. Labelled data (rules fixed now)

One row per source-station outcome. Outcome 1 = arrival reported or detected; 0 = looked for and not found. Rows with no assessment (data truncated, not reported, station not named) are not used.

| Set | Source | Use |
|---|---|---|
| S1 Blackman 2003 Appendix B (LLNL) and SIO text/figures: SUS 1.8 lb, glass spheres (single, 5-cluster), at H01W, H08S, H08N | data store table `dg_data_blackman_blackman_receiver_observations` (hydro_data.sqlite e0442ace...) | primary |
| S2 Blackman 2001 SIO: airgun sites air1-9, spheres sph1-7, imploding cylinders imp2-7 | same table | primary (cylinders: the report states that no imploder shot was detected in IMS data; coded 0 at H01W, H08S, H08N) |
| S3 Royer 2016 located events at OHASISBIO and H01W | data store `royer_event_labelled` | primary for range / path / station effects, through a likelihood conditional on the number of stations that heard each event (source energy is unknown and event selection depends on that count) |
| S4 Earthquakes 6-10 Mar 2014, IDC T-phase associated at H01W / H08S | data store `known_event` | SENSITIVITY only: the label is "associated in the IDC bulletin", not "looked for and not found" |
| S5 Aircraft: F-35A at H11N / H11S (heard; Pacific); Sriwijaya 182 and Lion Air 610 at H08S (project search, no significant detection) | data store `impact_case` | check rows and sensitivity; Kadri claimed detections are a comparison set and are not labels |

Coding rules: (a) "detected" by any Blackman analysis = 1; (b) "not_detected_with_tentative_pick" = 0 in the primary, 1 in a sensitivity; (c) "detected_questionable_pick" = 1 in the primary, 0 in a sensitivity; (d) where LLNL and SIO disagree, rule (a) applies; (e) H01W1-3 count as one station, SWAMS1-3 as one site (SWAMS2) for Royer; (f) SUS partial fires (A9suspuf, A10suspuf) have no printed position: they are not used.

Covariates: range (great-circle, km); path class from the frozen-chain path builder (`path-sections-index.csv`, `path-classes-royer-dense.csv`; rule: blocked / ridge above the channel axis / ridge near the channel axis / clear deep path; "not classified" where no section exists); station; source family; log10 source energy proxy (SUS 3.4e6 J chemical; sphere and cylinder p V at the firing depth, 5-cluster 5 p V; earthquake log10 E = 1.5 M + 4.8); site (source position) for grouping.

## 3. Models

All models are Bayesian logistic regressions (logit link), fitted by NUTS (numpyro), 4 chains. Continuous inputs are centred and scaled to sd 0.5 (Gelman 2008). Priors: coefficients Student-t(3, 0, 2.5); intercept Student-t(3, 0, 5); group sd half-normal(1). Firth-penalised maximum likelihood is a check for every fixed-effect model.

Model A (forward-chain test). Data: the held-out calibration table used by step 2 (artifact 960bbcc0, `indian-ocean-calibration-opportunities.csv`), rows at H01W / H08S / H08N with a frozen-chain margin m = predicted minus noise (dB) and a binary outcome.
- A1: logit P = a + b m.
- A2: A1 + station intercepts (partial pooling) + source-family intercepts (partial pooling; they absorb the different level conventions of the families).
- Derived: 50 % margin m50 = -a/b (dB); logistic scale s = 1/b (dB); equivalent probit sd sigma = s pi / sqrt(3).
- Calibrated chain (pre-stated test): the 95 % interval of m50 contains 0 dB, and the 95 % interval of sigma overlaps the stated spread (12.58 dB used by step 2 for the frozen chain; about 20 dB v2 inflated at 25 Hz; about 10 dB proposed step 2 amendment).

Model B (model-free). Data: S1 + S2 (+ S3 through the conditional likelihood). logit P = alpha + family effect + beta_E x log10 energy proxy + beta_R x log10(range / 2000 km) + path-class effect + station effect (partial pooling) + site effect (partial pooling; S1/S2 only).
- B-S4 sensitivity: add S4 earthquakes as a family, with the IDC label caveat; S4 path classes from the `known_event` geometric screen (open -> clear deep path; ridge/plateau -> ridge above the axis; shelf < 200 m or land -> blocked; long seismic leg -> its own class).
- B-air sensitivity: add the F-35A rows (aircraft family, Pacific).

Link sensitivity: A1, A2 and B refitted with the probit link.

## 4. Held-out scheme and scores

Leave-one-SITE-out cross-validation (sister shots at one site never inform each other): one fold per source site (Blackman site A1-A11, air1-9, 2001 sphere/cylinder site, Royer event). For each held-out row: posterior predictive P. Scores: mean log score, Brier score, AUC; 95 % intervals by bootstrap over sites (2,000 resamples). Base rate: intercept-only model under the same folds. Calibration plot: held-out P in bins against the observed fraction.

Skill of the chain: on the rows that have a chain margin, held-out log score of A1 (and A2) minus that of B fitted on the same rows; paired bootstrap over sites.

## 5. Pass criteria (separation gate, independent check)

PASS if all hold, for the primary data of Model A and for Model B:
1. held-out AUC >= 0.70 and its 95 % lower bound > 0.50;
2. held-out Brier < held-out base-rate Brier;
3. held-out log score > held-out base-rate log score.
"Chain adds skill" if the held-out log-score difference A minus B is > 0 and its 95 % interval excludes 0. Otherwise: "not shown".

## 6. MH370 prediction (stated now)

- Model A: frozen-chain margin for an impact with F-35A-like coupling, kinetic energy E log-uniform on 1e7-1e10 J, source depth 10 m, 43 arc points 41-20 S. Cape Leeuwin margin from the step 1 table (`cape-leeuwin-10GJ-prediction-real-ocean-by-arc-point.csv`, column snr_frozen_10m, 30 s window) plus 10 log10(E / 1e10). Diego Garcia South by the same formula with the dense-grid band gain ratio and noise 100.4 dB (status file) in place of 103.68 dB. The calibration margins are band exposure against one second of noise, so the primary adds 10 log10(30) = 14.8 dB to the 30 s margin; the 30 s convention is a sensitivity. P(heard) = posterior predictive of A1 and A2 (new site; station effect where fitted).
- Model B: P(heard) for a source of a NEW family (family effect drawn from the fitted between-family spread), energy proxy E, at the arc path class and range of each station. Sensitivity with the F-35A rows.
- Reported as a predictive band (5-95 %) over the posterior, the energy range and the arc, not a point.

## 7. Known limits stated before fitting

- No aircraft impact in the Indian Ocean is in the labelled set. The MH370 numbers are extrapolations.
- In Model A, SUS rows exist only where Blackman reported a detection (the chain was not run for the SUS non-detections). This biases the SUS part of A toward "heard".
- The energy proxy is not acoustic energy; family effects absorb the coupling differences.
Anything chosen after the first fit is reported as POST HOC.
