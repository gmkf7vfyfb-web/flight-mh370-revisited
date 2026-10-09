# Two-epoch windage calibration: set-up, injection-recovery, and the real result (PROVISIONAL)

2026-10-09, Pléiades module. Sequence steps 1, 2 and 4 of the 9 Oct entry. Code: `export.rs` (tracks,
through `mh370-ocean`), `prepare/twoepoch.py` (enumeration, information gain, Bayes factor),
`prepare/injection.py`, `prepare/d5_real.py`, tests `prepare/test_twoepoch.py`. Numbers:
`d5-real-arms.csv`, `d5-real-windage-posteriors.csv`, `d5-injection-summary.csv`,
`d5-floor-scan-summary.csv`. Figure: `d5-two-epoch.png`.

## Answer

**The COSMO-SkyMed to Pléiades pair carries no usable windage information, and injection-recovery
shows that this is a property of the data, not of the method.** Under the reference spread, three
contacts that truly drifted with a known windage give 0.003-0.008 bits. The calibration needs a
transport spread of about 6 km or less per component **and** a confident prior that contacts have
counterparts before it recovers anything. The pass time adds a second, smaller loss on top.

## Model (declared)

- θ = (windage c, `cosmo-pass`, ±25 min offset, K). c uniform 0-5 % on 21 nodes. Pass dawn/dusk 0.5/0.5.
  K log-uniform 30-1000 m²/s (the shared provisional prior), one K per realisation shared by all pairs.
- Deterministic tracks from `mh370-ocean`: GLORYS12 surface current + c·ERA5 10 m wind. Stokes is
  absorbed in c, so no WAVERYS term. Leeway angle 0.
- Analytic Gaussian spread per component: 2KΔt + Ornstein-Uhlenbeck model error (σ_e 0.05 m/s,
  T_e 2 d) + COSMO position sd 1 km + target sd 0.5 km. Model error is independent between pairs
  (reference) or fully shared (sensitivity).
- **Matching enumerated, never sampled.** Every partial injective assignment of contacts to targets:
  229 (F1-F3 × 6 clusters), 1,045 (F1-F4 × 6), 1,753 (× 12), 18,001 (F1-F4 × 12 objects). All checked
  against Σ_k C(m,k)·n!/(n−k)!.
- Assignment prior: each contact has a counterpart with probability π_m (reference 0.5), with the
  target chosen in proportion to its prior weight (rating weight ρ, cluster-weight form).
- Matched pair likelihood ratio p(y|x,θ)·A_scene, against the target being background uniform over its
  500 km² scene (GA: "each scene is approximately 25 km x 20 km"). The empty assignment contributes 1
  for every θ.

## Step 2: injection-recovery, with the pass time marginalised

Simulation-based calibration: c drawn from its prior, K from its prior, k = 1, 2 or 3 of F1-F3 truly
drifted, and the six real rating-5 clusters left in the scene as distractors. 200 replicates per cell.
Each replicate was analysed twice, with the pass time marginalised and with it known.

| | coverage 68 % | coverage 90 % | information gain (bits) | P(true pass) |
|---|---|---|---|---|
| independent error, pass known | 0.67-0.76 | 0.90-0.93 | 0.003-0.008 | 1 (given) |
| independent error, marginalised | 0.66-0.74 | 0.91-0.93 | 0.003-0.005 | 0.50-0.51 |
| shared error, pass known | 0.65-0.72 | 0.85-0.93 | 0.003-0.008 | 1 (given) |
| shared error, marginalised | 0.65-0.71 | 0.86-0.92 | 0.003-0.004 | 0.50-0.51 |

- **The machinery is calibrated:** coverage is at nominal within Monte Carlo error.
- **At the reference spread nothing is recovered,** even with three true counterparts. The posterior
  stays at the prior, and P(any match) falls to 0.12-0.16 against a prior of 0.875. A true match sits
  about one spread (≈ 10 km) from its predicted position, and that is no more likely than a background
  object within the 500 km² scene.

**The floor** (`d5-floor-scan-summary.csv`): K and σ_e fixed and known, k = 3, both passes, 30
replicates per cell.

| sd per component | π_m 0.5, known / marginalised | π_m 0.9, known / marginalised | P(true pass), π_m 0.9 |
|---|---|---|---|
| 3.4 km (K 30, no model error) | 0.14 / 0.06 bits | 1.74 / 1.33 bits | 0.80 |
| 5.9 km (K 100, no model error) | 0.03 / 0.01 | 0.61 / 0.37 | 0.62 |
| 9.2-9.3 km | 0.008 / 0.005 | 0.23 / 0.15 | 0.55 |
| 18-20 km (K 1000) | 0.001 / 0.001 | 0.05 / 0.04 | 0.51 |

- Recovery appears only when the spread is about 6 km or less **and** π_m is 0.9. At 3.4 km with
  π_m 0.9 the posterior-mean error is 0.26 % (known pass) and 0.37 % (marginalised), against 1.2 % for
  the prior alone.
- **The pass time costs a quarter to two fifths of the information where there is any**: 1.74 → 1.33
  bits at 3.4 km, 0.61 → 0.37 at 5.9 km. The data identify the true pass only weakly (P = 0.80 at best,
  0.5 at the reference spread). So the acquisition time does limit the calibration, but second to the
  transport spread, not first.

## The real result (`d5-real-arms.csv`)

| arm | information gain (bits) | ln BF (free vs c fixed at 2.5 %) | P(dawn) | P(any match), posterior / prior |
|---|---|---|---|---|
| **reference** (F1-F3, rating-5 clusters, independent, σ_e 0.05, π_m 0.5) | 0.006 | −0.008 | 0.50 | 0.11 / 0.875 |
| F1-F4 | 0.006 | −0.008 | 0.50 | 0.11 / 0.94 |
| cluster-weight count | 0.012 | −0.021 | 0.50 | 0.17 / 0.875 |
| shared model error | 0.006 | −0.007 | 0.50 | 0.11 / 0.875 |
| σ_e 0.10 | 0.002 | −0.013 | 0.50 | 0.10 / 0.875 |
| π_m 0.9 | 0.142 | −0.047 | 0.50 | 0.55 / 0.999 |
| ratings 4+5, ρ4 0.25 / 0.5 / 1 | 0.003 | −0.012 to −0.013 | 0.50 | 0.09 / 0.875 |
| rating-5 objects (F1-F3: 1,753 assignments; F1-F4: 18,001) | 0.012 | −0.021 | 0.50 | 0.17 / 0.875 (F1-F3), 0.94 (F1-F4) |

1. **Information gain is at most 0.14 bits** in every arm, inside what the injection floor shows
   the geometry can give. **The Bayes factor is unity to within 5 %.** That is the negative result
   stated as a number.
2. **F4 changes nothing.** Every windage puts it 60-115 km from every target, so it is never matched.
   It agrees with the brief's "poor transport fit", now measured, and it is why both
   `cosmo-contact-set` arms agree.
3. **The data discriminate nothing between the pass times**: P(dawn) = 0.497-0.503 in every arm.
4. Under π_m 0.9 the leading match is F1 → PHR_4 objects 2-6 at about 3 % windage on the dawn pass,
   with posterior 0.16. It is not evidence for H; it is the one place a contact track passes within
   about 4 km of a cluster.
5. **The windage calibration therefore offers drift nothing.** That goes to drift as a result (no
   calibrated windage from this pair at the reference spread), not as a missing deliverable.

## Limits

- One ocean-model option. K's prior is provisional; σ_e and T_e are declared, not measured (brief §13).
- No footprint term. A contact predicted to land inside a scene and not seen there is not penalised,
  because footprints are not assembled and COSMO's are missing. That would sharpen the windage only if
  footprints existed.
- Leeway angle is fixed at 0. Contact and target position errors are declared.
- Injected arrivals are not conditioned on landing inside a footprint.
