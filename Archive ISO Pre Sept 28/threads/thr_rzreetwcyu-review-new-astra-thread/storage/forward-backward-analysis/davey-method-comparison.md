# Davey method comparison

Checked 8 September 2026, 18:20 UTC, in response to Pete's question about why
the published method succeeded while this project has not delivered a stable
estimate. No simulation was launched and the closed compute ledger is unchanged.

## Located source evidence

Sources below are the published 2016 Springer chapters by Samuel Davey, Neil
Gordon, Ian Holland, Mark Rutten and Jason Williams in *Bayesian Methods in the
Search for MH370*. Full publisher HTML was retrieved and read. The separately
retrieved ATSB December 2015 draft is not used for these locators.

| Claim | Source and locator | Short located passage | Status |
| --- | --- | --- | --- |
| Conventional filtering struggled; adaptive particle counts and weighted depth-first branching were adopted. | [Particle Filter Implementation](https://link.springer.com/chapter/10.1007/978-981-10-0379-0_8), opening discussion, equations 8.4–8.6 | “adaptively increase the number of particles” | FOUND |
| Repeated manoeuvres are allowed; navigation-mode switching remains restricted. | Same chapter, section 8.2 and section 8.3 assumption 3 | “one of five prescribed modes” | FOUND |
| The principal filter assumes cruise Mach 0.73–0.84 and does not propagate a fuel limit. | Same chapter, section 8.3 assumptions 4 and 7 | “Infinite fuel”; “Mach 0.73–0.84” | FOUND |
| Validation uses six known flights and ten message subsets per flight. | [Validation Experiments](https://link.springer.com/chapter/10.1007/978-981-10-0379-0_9), introduction | “six validation flights”; “a total of sixty validation measurement sets” | FOUND |
| Validation checks uncertainty coverage; the subsets share information and are not sixty independent flights. | Same chapter, introduction and sections 9.7.2–9.7.3 | “the results within a single flight are quite correlated” | FOUND |

## Local implementation evidence

- `.sources/davey-2016-bayesian-search/code/run_filter.py:410` explicitly states:
  `fixed-N bootstrap SMC replaces Davey depth-first branching implementation`.
  The execution loop initializes a fixed population, advances all particles
  between observations, and resamples that population when its weight-based
  effective sample fraction is low. This is a valid class of particle filter,
  but is not an implementation of Davey's branching procedure.
- The source reconstruction also substitutes zero nominal wind and magnetic
  declination and does not reproduce all calibration inputs. Its own
  `data/source-ambiguities.md` rejects an exact-reproduction label. These limits
  concern that source reconstruction, not the later runner's ERA5/IGRF inputs.
- The latest temporary experiment uses tempered SMC over complete ordered
  control histories, with forward/reverse blocks and corrected proposals. It
  replays whole flights and is neither Davey's algorithm nor classical
  forward-filter/backward-state simulation. See the archived experimental
  source and `/tmp/mh370-command-sampler/README.md`.
- `conclusion.json` records the failed independent accurate one-turn comparison:
  maximum coordinate-CDF difference 0.1875, with no stable family demonstrated.
  Numerical integration checks passed after a correction; those checks do not
  establish sampling convergence or independent aircraft-model calibration.

## Assessment

The project has not demonstrated a faithful, validated reproduction of the
published estimator. Algorithm substitution followed by extensions before that
baseline was established is an implementation-strategy failure. This evidence
does not identify branching as a guaranteed cure: there has been no controlled
comparison holding dynamics, observations, inputs and compute budget fixed.

The justified next benchmark is the published algorithm and declared model,
with every unavailable input explicit, first against independently checkable
synthetic cases and then against retrievable known-flight data. Matching a
published accident-flight curve alone is not validation. Real-flight calibration
cannot be claimed from synthetic tests. Extension of the prior and fuel model
requires separate checks after the benchmark works. Runtime must be measured;
the published success does not establish a cheap runtime for our broader model.
