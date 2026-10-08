# Pléiades and COSMO-SkyMed — mission and master prompt

**Status.** Aligned 8 October 2026 by the architecture session, from Pete's context of the same
date, the nine slides of prior work he supplied, the September ISO brief
(`ISO Sept 28 Status/threads/master-prompts/pleiades.txt`) and the archived object table.

**Authority.** This file supersedes `pleiades.txt` wherever they differ, and they differ
substantially: the ISO brief does not mention COSMO-SkyMed, SAR, object matching, or the tension
measurement, and one of its sentences about what the module returns is wrong (§2 below). Read
`ISO Sept 28 Status/threads/master-prompts/common.txt` for the shared contract and the eight
composition rules — those are not restated here and they bind you. Read
`Claude Science Project Sep 29/ARCHITECTURE.md` for how this module sits in the estimator.

**Module location.** `hypotheses/pleiades/`, created with `make new-hypothesis H=pleiades`.

---

## 1. Mission

A conditional hypothesis, and it is labelled as one on every figure, in every table and in every
sentence of the paper.

**H: at least one of the objects imaged by Pléiades on 23 March 2014 (Geoscience Australia Record
2017/13) or detected by COSMO-SkyMed on 21 March 2014 came from 9M-MRO.**

"At least one" is the hypothesis, and it ranges over one object through all of them. The module
does not decide which objects, and it cannot: there is no identity evidence (§3). What it can do
is ask which impact locations are *compatible* with ocean transport to the observed positions on
the observed dates, and return that compatibility as a log-likelihood on the shared impact
samples. The prior π on H is swept, never fixed, and the composer reports p(x | D, H), P(H | D)
and the mixture.

Everything this module knows comes from **where the objects were seen and when**. Nothing comes
from what they look like.

### The expertise this module is expected to bring

Everything asked of the ocean drift module — world-class knowledge of the ocean-transport
literature, prior drift-based search cases and especially those with ground truth, thorough
Bayesian competence, and the willingness to review a method critically rather than reproduce it.
Add to that: optical and SAR remote sensing, the detection and false-alarm behaviour of each
sensor, and the geospatial practice used by Geoscience Australia in its own analysis of these
scenes, including the PCA mask work. You are expected to know why a 24 m × 24 m Pléiades image
field with a 5 m rule constrains what can be said about a 40 m² object, and to say so.

---

## 2. The contract — stable; changes need architecture review

**What the module returns.** A log-likelihood on the shared impact samples, computed from the
positional compatibility of the imaged objects with transport from each candidate impact
location, mixed over the prior π on H.

The ISO brief says the module returns "the log-likelihood ratio of the object data under H versus
not-H". **That sentence is wrong and is withdrawn.** It implies the imagery discriminates H from
not-H, and it does not: the morphology screen produced no identity likelihood and is not going to
(§3). The ISO brief's own design formula is correct and stands:

```
log L(s) = ln[ (1 - pi) + pi * SUM_c w_c * p(y_c | s) / q_c ]
```

summed over object clusters `c`, where `s` is the impact location, `p(y_c | s)` is the normalised
transport density of a release at `s` arriving at cluster position `y_c` on the observation date,
`q_c` is a documented background density over the imaged footprint, and `w_c` is the cluster
weight. Note what each part does: π carries the hypothesis, and the data enter only through a
ratio of position densities. That is an honest account of the available information.

**Both outputs, always paired.** Reweighting the impact samples by `log L` gives the conditional
PDF. Summing gives the evidence, and the evidence against the unconditional case gives the
tension. These are two readings of one computation, not alternatives, and reporting either alone
is a defect.

**Why the pairing is mandatory and not a matter of taste.** A conditional PDF can be narrow
*because* the hypothesis is in tension. If the likelihood is near zero across the unconditional
posterior's bulk, the conditional concentrates in whatever far-tail region survives: it acquires
a small 90% HDR and reads as a sharpened answer, when the estimate has in fact been relocated
into a region the flight evidence disfavours. **A narrow conditional is not evidence of
precision.** Three tension quantities therefore travel with the PDF everywhere it appears:

1. the evidence ratio, P(D | H) against the unconditional case;
2. the two-way overlap of the 90% HDRs — the unconditional mass inside the conditional's HDR, and
   the converse, reported as two numbers because they are not equal;
3. the mode displacement in nautical miles.

**Scale.** `absolute_scale` is true. The likelihood is normalised in position and seed-free, so
its scale is meaningful and must not be max-normalised. The ISO work's likelihood-handoff builder
destroyed exactly this and is discarded (§8).

**Alternatives are declared by name and shared.** Three matter:

- `ocean-model` — the transport product. **The same name as every other module that depends on the
  ocean**, so the composer marginalises it jointly. The trap: if this module runs on BRAN and the
  drift module runs on GLORYS and the composer multiplies their likelihoods, nothing is formally
  double-counted but the ocean uncertainty is silently treated as resolved. Same name, joint
  marginalisation, or the two are not combinable.
- `cosmo-contact-set` — values `all-four` and `F1-F3`. Both arms are run; see §6.
- `object-rating` — whether rating-4 objects are carried, and at what weight.

**What this module must never do.** It must never be used to pre-select impact samples, filter
the core posterior, or restrict a grid before any other module sees it. It enters as a likelihood
on samples every other module also scored, and that is the whole of its entry. Composition rule 2
exists for this case.

---

## 3. There is no identity likelihood, and this is the most important finding in the prior work

The morphology screen compared the five shortlisted rating-5 objects against 26,976 masks in eight
families — 777 parts, random geometries, and ocean-debris classes — and the result is negative in
three separate ways:

- **777 shapes remain admissible but so does everything else.** Wings, other 777 parts and
  fuselage sections pass the two-sided size gate; so do two random geometries, an ocean control, a
  wing and a fuselage section among the per-object minima. The controls matched at least as well.
- **The flooding model is not favoured.** Mean minima: flooding wing 0.3286, random-pose wing
  0.3232, random geometry 0.3267. And in the later, better-informed simulation, **none of the 168
  simulated flooding states matched the PCA masks.**
- **The loss measure is not a probability.** PCA loss is one minus a reflected mask IoU after a
  size gate. It measures mask overlap. It is not a class probability and not a Bayes factor, and
  converting it into one would be fabrication.

Margins across the screen were 0.0002 to 0.009. Pete's own conclusion from it stands: the objects
cannot be identified, and a source near 35°S is admissible **only** as a conditional hypothesis.

**Do not redo this screen** unless you have a genuinely new approach, and if you think you do,
raise it before spending compute. What you may not do is present shape evidence as support for H.

---

## 4. The tension is in the observations, not in the drift model

Measured against the reference posterior `no-exhaustion-prior` (median −37.225°, 90% interval
[−38.35°, −35.50°]), every transport-inferred source mode in the prior work lies **north of the
90% bound**: BRAN2016 +5 NM, GLORYS12+WAVERYS +7 NM, the equal-prior three-family mixture +17 NM,
OSCAR v2 +35 NM. Only Griffin and Oke's 35.6°S sits inside, by 6 NM. Conditioning on the seabed
searches moves the residual mean from 35.13°S to 34.93°S — from 22 NM outside to 34 NM outside.

And the raw observed positions are further north still: the six clusters sit **121 to 166 NM north
of the reference median**. So the tension does not arise from a choice of ocean product, a windage
assumption or a diffusion parameter. It is present in the coordinates.

This bounds what the module can conclude before it starts, and you should state the bound rather
than discover it late: **this is a conditional that relocates the impact estimate, not one that
sharpens it.** The 90% HDR of the three-family mixture is 28,768 km², which is not obviously
narrower than the unconditional posterior either.

The comparison above is one-dimensional — reference latitudes are along-arc impact latitudes,
the Pléiades figures are source latitudes not constrained to the arc. It fixes the sign and the
rough size, not the number. **Your first deliverable replaces it with the proper two-dimensional
overlap** (§10).

---

## 5. The object table, the clusters, and why the linkage threshold is a parameter

**Twelve rating-5 objects**, from GA Record 2017/13 Tables 1–4, archived at
`.archive/.sources/pleiades-bran2016-forward-inversion/data/pleiades-rating5-objects.csv` and
spot-checked. Reported areas run 23 to 70 m², median 40, 514 m² in total. Five were in the
morphology shortlist: PHR_4 objects 6, 18, 19, 26 and 27.

At a 3 km single-linkage threshold they form **six clusters**, not the four the ISO brief assumed:

| scene | objects | n | mean lat | mean lon | area m² |
|---|---|---|---|---|---|
| PHR_1 | 1 | 1 | −35.2053 | 90.4580 | 39 |
| PHR_3 | 10 | 1 | −34.5938 | 90.4934 | 28 |
| PHR_3 | 7 | 1 | −34.5571 | 90.4563 | 60 |
| PHR_4 | 26, 27 | 2 | −34.5467 | 91.2982 | 88 |
| PHR_4 | 18, 19 | 2 | −34.5014 | 91.3061 | 110 |
| PHR_4 | 2, 3, 4, 5, 6 | 5 | −34.4539 | 91.3568 | 189 |

The cluster count sets both the matching space and the weights `w_c`, so **the linkage threshold
is a declared configuration parameter, reported with the result, and the sensitivity of the
answer to it is reported too.** It is not a choice buried in code. The ISO brief's four-location
reading is a legitimate alternative threshold, not a correction to the six above.

**COSMO-SkyMed: four possible radar contacts**, F1 to F4, 21 March 2014 — two days before the
Pléiades acquisition.

**Rating-4 objects.** The archived table holds rating-5 only, so the rating-4 count is **not
known to this project** and must be read from GA Record 2017/13 Tables 1–4. Do not guess it.

GA's table has latitude and longitude transposed for PHR_2 object 12. **That is a typo. Correct
it, record the correction in the data manifest, and move on.** It has no bearing on whether
rating-4 objects are in scope.

The rating-4 scope question is separate and is ruled as follows. A GA rating of 4 rather than 5 is
a statement about classification confidence, so the principled treatment is **inclusion at a lower
weight, not a binary include-or-exclude**. Carry rating-4 under the `object-rating` alternative
with a declared weight, and report both arms. Discarding them throws away the rating as
information and invites exactly the selection effect that excluding F4 would.

---

## 6. The two-epoch opportunity, and how to settle it honestly

Pléiades and COSMO-SkyMed imaged two days apart. Under H, that is two snapshots of the same
drifting field, and it is **the only place in this project where a drift parameter could be
calibrated against observation rather than assumed.** That makes it valuable well beyond this
module: the drift module's own sensitivity shows object response dominates everything else —
scaling Stokes by 0.5, 1 and 1.5 moved the drift mode to 11.9, 18.0 and 34.9°S, against 1.2° for
changing the current product. **A calibrated windage is therefore worth more to drift than to
Pléiades, and it is exposed as a drift input whatever happens to the conditional.**

**The prior attempt was nearly inert, and its own caption says why.** Uniform 0–5% windage gave a
90% area of 44,417 km² and a mode at 35.24°S; a common calibrated windage gave 44,503 km² and
35.18°S; separate windages gave 42,359 km² and 35.24°S. A 5% change in area and 0.06° in mode.
The caption reads "distinct Pléiades counterparts assumed" — so the calibration was
information-limited by the **matching**, not by the method.

### Enumerate the matching. Do not sample it.

With four COSMO contacts and six clusters, allowing each contact to have no counterpart, there are
**1,045 possible assignments**. Over all twelve objects individually there are **18,001**. Both are
trivial to enumerate exhaustively. So marginalise over every assignment with a declared prior:
no seed dependence, no selection effect, and the marginal answers directly whether the pair carries
any windage information at all.

This replaces the proximity-matching and random-sampling approaches that were proposed when
comprehensive matching looked out of reach. It is not out of reach.

### If the answer is "no information", prove it rather than assert it

A negative result here is acceptable and publishable, but only if it is demonstrated. A frequentist
p-value is the wrong instrument: the matching is a nuisance we marginalise over, so there is no
clean null sampling distribution without also fixing the thing we do not know. Report three
quantities instead:

1. **Information gain in bits** — the Kullback–Leibler divergence from the windage prior to the
   windage posterior, marginalised over all assignments. Zero bits means the pair taught us
   nothing, and it needs no significance threshold to be interpretable.
2. **A Bayes factor** between a free-windage model and one with windage fixed at its prior mean.
   A factor near unity is the negative result stated as a number.
3. **Injection and recovery, which establishes the floor.** Simulate the two epochs from a known
   windage, run the identical enumeration, and ask whether the known value is recovered. If this
   geometry and this many objects cannot recover a value that is there by construction, the
   negative result is a property of the data's information content, established rather than
   claimed. This is the same discipline required of hydroacoustics before it may return a
   likelihood, and for the same reason.

### COSMO contact F4

F4 is flagged in the prior work as a poor transport fit and it does not match across the two days
in the way the others might. **Run with it and without it**, as the `cosmo-contact-set`
alternative, because it is still a data point in the imagery and dropping an inconvenient one is a
selection effect. Both arms come from the same enumeration, so the cost is negligible.

---

## 7. Forward, not reverse — and the prior work already turned this corner

The method is **forward transport from candidate impact locations**, consistent with the rest of
the estimator: release at `s`, advect to the observation date, evaluate the density at the observed
cluster positions. Bayes happens in the composer. The project does not use reverse drift as an
estimator; see §4 of the ocean-drift brief for the full argument, which applies here unchanged.

Pete's instinct that the earlier work should be re-done forward is right in principle and already
satisfied in fact: the reverse-drift three-model source estimate is the older approach, and the
forward-transport compatibility panels are the newer one. Treat the forward work as the baseline to
reproduce and improve, and the reverse work as reference only.

The forward prior work, for calibration of your own results — four alternatives over 5,289 release
cells (32–39°S, ±100 NM, 5 NM spacing), 8 to 23 March:

| alternative | mode | 90% HDR km² | mass within ±30 NM | east ǀ west |
|---|---|---|---|---|
| BRAN2016, 2.5 m layer | 35.418°S 92.886°E | 24,309 | 68.3% | 47.2 ǀ 46.2 |
| OSCAR v2 Final, upper 30 m | 34.917°S 92.047°E | 18,393 | 46.4% | 4.8 ǀ 90.9 |
| GLORYS12 0.494 m + WAVERYS Stokes | 35.391°S 92.163°E | 22,123 | 63.5% | 12.0 ǀ 80.6 |
| equal-prior three-family mixture | 35.218°S 92.247°E | 28,768 | 59.4% | 21.3 ǀ 72.6 |

Pairwise total variation between families 0.484 to 0.570; mode separation 53.8 to 94.4 km. **The
families are alternatives, never independent evidence, and their spread is not sampling error.**
BRAN's mode is 21.7 km from Griffin and Oke's 35.6°S 92.8°E.

**Do not count Stokes drift twice.** Griffin and Oke's 1.2% windage is itself a Stokes proxy, so
adding WAVERYS Stokes on top of it double-counts. If you use their windage, do not add Stokes; if
you add Stokes, do not use their windage as a windage.

---

## 8. Evidence, data, licence and provenance

All under `Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/pleiades-bran2016-forward-inversion/` (corrected 8 October; the ISO path `.archive/.sources/...` does not exist on this branch), with URLs and hashes in the
manifests, regenerable with `code/fetch_data.mjs`:

- `data/pleiades-rating5-objects.csv` — the object table, from GA Record 2017/13 Tables 1–4.
- BRAN2016 at 0.1°, via NCI OPeNDAP, anonymous.
- OSCAR v2 at 0.25°, via Earthdata — Pete's login works.
- GLORYS12 at 1/12° and WAVERYS, via Copernicus. Raw CMEMS NetCDFs for March to July 2014 are
  cached at `/jackbox/home/.cache/mh370-cmems-{glorys12,waverys}`.
- The CSIRO Part III PDF, the method reference, is in `paper/`.

**Licence, and it is not negotiable.** The GA report is CC BY 4.0 **except** the images marked
© CNES, which covers every object crop. **Never commit the crops.** Read them by path. The same
rule the searched-areas module follows for the traced Ocean Infinity outline applies here: an
unauthorised or unlicensed copy is never cited and never committed.

**Port** `transport_core.mjs`'s two independent tests — constant-current analytic displacement,
and random-walk RMS — if the shared ocean transport lacks them. They are good tests.

**Discard** the likelihood-handoff builder, whose max-normalisation destroyed the likelihood scale;
the 216 scenario directories; and the renderers.

---

## 9. What the prior work measured, and where it went wrong

**The integration collapsed.** Effective sample size was 5.6 to 9.1 out of 150,000, with a single
particle holding 22 to 36% of the mass. The cause is diagnosed and the diagnosis is the important
part: the likelihood was an **unnormalised 10 km kernel with no model-error term**, so the tails
were set by whichever of 576 particles happened to land nearest. That is not a sampling problem to
be fixed with more particles; it is a likelihood that cannot be integrated.

**The fix, which is a requirement and not a suggestion.** Use an **analytic spread** — random walk
plus transport-model error calibrated against drifters — so that `p(y | s)` is normalised,
seed-free, and has support everywhere the physics allows. Report ESS per factor. An ESS that is a
few tens out of a hundred thousand is labelled "not resolved" and not plotted.

This is the same failure mode the drift module is warned about, from the same cause. If you find
yourself tuning a kernel width to make a result look reasonable, stop and raise it.

---

## 10. Deliverables, in order

1. **The two-dimensional tension measurement** against the reference posterior, replacing the
   one-dimensional comparison in §4: evidence ratio, two-way 90% HDR overlap, mode displacement.
   This comes first because it bounds the value of everything after it, and it can be computed
   from the existing forward-transport grids before any new transport runs.
2. **The object model**: clusters at a declared linkage threshold with a reported sensitivity, the
   background density `q_c` over the imaged footprints, and the cluster weights.
3. **The likelihood**, with the analytic normalised spread of §9, and its tests.
4. **The conditional PDF and its tension quantities, paired**, over the `ocean-model`,
   `cosmo-contact-set` and `object-rating` alternatives.
5. **The matching enumeration and the two-epoch calibration result**, with information gain in
   bits, the Bayes factor, and the injection-recovery floor — whichever way it comes out.
6. **The western-residual feasibility test** (§11).
7. **The residual search PDF under H**, once settling is available: what is left after the seabed
   searches found nothing, under the conditional. The prior work puts 42.2% of mass outside past
   search envelopes before search conditioning and 85.8 to 88.2% after, so this is where H and the
   searched-areas module interact most strongly.

---

## 11. The test nobody has run, and it may be decisive

The prior work's own note, on the slide reporting the search-conditioned residual: the surviving
mass moves west to about 91.0°E, and **"those western locations have NOT been checked against
flight or fuel feasibility."**

This project can check it, and that is the main thing this architecture adds over the earlier
effort. 91°E at 35°S lies well inside the seventh arc, north-west of it. Ask directly whether any
impact sample in the core posterior reaches there at all, and with what weight. If the western lobe
is largely unreachable under the BTO, BFO and fuel evidence, most of the residual mass under H
disappears — and that is a result, not a disappointment.

Run this early. It is cheap, it uses the posterior you already have, and it changes how much effort
the rest of the module deserves.

---

## 12. Tests

- `make scope H=pleiades` must pass. **Note core request 11**: the target currently diffs against
  `main`, which is behind the working branch, so on a module branch it reports architecture-owned
  documentation as out of scope. Until that is fixed, check your file list by hand against your own
  module directory.
- The two ported transport tests of §8.
- A normalisation test on `p(y | s)`: it integrates to one over the plane, to tolerance, for a
  representative `s`.
- A seed-independence test: two seeds give the same likelihood column to tolerance. If they do not,
  the spread is not analytic.
- An enumeration test: the 1,045 cluster assignments and the 18,001 object assignments are both
  generated, counted and checked against the closed-form count.
- The injection-recovery test of §6, which doubles as the calibration test.

---

## 13. Deferred, and to be raised again with Pete

- A **correlated multi-object likelihood**. The current form treats clusters as independent given
  `s`, which they are not — they drifted through the same ocean.
- A **Poisson term for debris that should have been seen and was not**, over the imaged footprints.
  This is the symmetrical counterpart of the searched-areas non-detection logic and it is currently
  missing on this side.
- **Scene footprints**, which the Poisson term needs and which are not yet assembled.
- The **size of the 15-day transport error**, which is currently assumed rather than measured.
- Whether the seabed imagery over this area can be obtained and searched, which Pete raised as
  "maybe try searching the bed imagery".

---

## 14. Open, needing the architecture session

- The **rating-4 count and table**, which must come from GA Record 2017/13 and is not in this
  project's data.
- The **transport-product allocation** between this module and the longer ocean drift: different
  products were used for the local 15-day problem and the 16-month problem, and whether that is
  defensible is a model-selection question for the shared ocean-transport owner. Raise it in
  `coordination/OCEAN_TRANSPORT.md`. The binding constraint is already known: whatever is chosen,
  the alternative is declared under the **same name** across modules and marginalised jointly.
- Whether the **windage calibration**, if it carries information, is published as a Pléiades result
  or as a drift input, or both. Architecture's current view is both, with the drift use being the
  more valuable.
