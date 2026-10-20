# Design: a hydroacoustic test of the Pléiades conditional hypothesis

Pléiades module, 10 Oct 2026. Pete approved this design and asked Modular Architecture to coordinate it.

## Question

H is the hypothesis that the objects imaged by Pléiades on 23 March 2014, and the four COSMO-SkyMed radar contacts
of 20/21 March, are debris from 9M-MRO. If H is true, the impact must lie in a smaller region. That region implies its
own predicted hydroacoustic arrivals: times, ranges and bearings at H01W, H08S, H08N and the other stations. The test asks:

  **Are the hydroacoustic observations (detections or non-detections) more probable under the impact distribution
  implied by H than under the flight posterior alone?**

The statistic is the ratio of predictive probabilities

  R_hyd = p(hydroacoustic data | flight data, H) / p(hydroacoustic data | flight data)
        = Σ_i w_i L_P,i L_hyd,i / Σ_i w_i L_P,i   ÷   Σ_i w_i L_hyd,i / Σ_i w_i,

where:
- i runs over end of flight's impact samples;
- w_i is end of flight's weight for the chosen 00:19 option;
- L_P,i is the Pléiades likelihood of impact i under H;
- L_hyd,i is the hydroacoustic module's likelihood of its own data for impact i.

R_hyd is interpretable as it stands, and it is one factor in the Bayes factor for H. The Pléiades factor itself stays
uninterpretable (no scene-footprint or background term), so R_hyd is reported alone, never as P(H | data).

## What is passed, and why

**Not a subset of impacts inside the 50/90/99 % regions, and not those regions' boundaries sent back to end of flight.**
1. A highest-density region is a summary for display. Cutting impacts at it discards the tail mass and flattens the
   weighting inside the region.
2. The hydroacoustic prediction depends on each impact's time, descent state and energy. In end of flight's samples
   these are correlated with impact location. A geographic boundary loses that correlation.
3. Both are selection on the outcome, which composition rule 2 rules out.
4. New sampling is unnecessary. For the first pass, 00:19 R600 BTO Only, end of flight's existing impacts keep an
   effective sample size under H of about 90,000-145,000 rows (10,000-16,000 parents) per seed in every stratum of
   core (b), against 1.5-1.9 million rows without H (seed 1 of each stratum).

**Instead:**
1. **Per-impact Pléiades log-likelihood columns, from the Pléiades module.** These are keyed to end of flight's own
   rows (stratum, seed, row index, parent). Contents:
   - ln L for Pléiades only, for all four COSMO-SkyMed contacts only, and for both together ("one debris field", the
     two likelihoods multiplied), each per ocean model and averaged over the two models;
   - a flag where the value is not computed (outside 85-103 E, 43-25 S).
   Hydroacoustics already reads end of flight's `impacts.npy`, which carries each impact's time, position, velocity
   vector and flame-out state, so it joins the columns and nothing is copied or cut. Weight without H: w_i. Weight
   under H: w_i × L_P,i, using the "one debris field" column.
2. **A resampled source package for expensive acoustic propagation runs, from the Pléiades module.** About 5,000 rows,
   drawn half from the flight posterior and half from the posterior under H (a defensive mixture), so that one set of
   simulations serves both. Each row carries end of flight's key and full state vector, and both importance weights.
   Hydroacoustics reports the effective sample size for each weight.
3. **What hydroacoustics returns:**
   - R_hyd per 00:19 option, with its Monte Carlo error (split-half over seeds);
   - predicted arrival windows at each station under H and without H, compared on the same chart.

## First pass

- 00:19 option: **00:19 R600 BTO Only.** The R600 BTO (18,400 µs) is scored with no BFO, the log-on cause is not fuel
  exhaustion, and the aircraft is required to be transmitting at 00:19:37.
- Impacts: core (b) via end of flight's next-run, strata mixed by core's P(family), held fixed.
- Pléiades: rating-5 objects in 6 clusters, equal weights; all four COSMO-SkyMed contacts. Ocean models GLORYS12 + ERA5
  and GlobCurrent daily + ERA5 at equal weight, with the measured transport error.
- Then the other core options in the ruled order: 00:19 Held Out, then 00:19 R600 BTO + Raw BFO.

## Caveats carried with the result

1. The Pléiades likelihood releases debris at a fixed 00:20 UTC, not at each impact's own time. This is small against a
   transport error of about 100 km per component.
2. Pléiades and COSMO-SkyMed transport errors are treated as independent. A correlation of 0.5-0.8 widened the 90 %
   region by 28-38 % on reference-289. The pair correlation is requested from ocean transport.
3. GlobCurrent windage is not yet product-relative (debris-drift audit F1). The same issue applies to this module; its
   sensitivity is being run now.
4. Core (b) is not converged (split-half), and its fuel model is uncorrected.

— Pléiades
