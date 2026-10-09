# The detectable target for the seabed search

Searched-areas module, 9 October 2026. Deliverable 2 of `threads/master-prompts/searched-areas.md` §3
and §7, written before any code is changed, as the brief requires.

**What this file fixes.** Three things the brief names as the module's hardest modelling problem:
what a detection *is*, what the minimum detectable piece is for each sensor, and how a wreckage field
that lies partly inside a swath is scored. It also states, precisely, what `q_k` and `ρ` mean once the
target is a field rather than a point, because the two are only separable if the target definition is
fixed first.

---

## 1. The target is a field, not an object

A Boeing 777 that strikes water at speed does not come to rest as one object. What the sonar could
have seen is a set of pieces

```
W = { (x_i, L_i, h_i) : i = 1 … N }
```

with seabed positions `x_i`, characteristic plan lengths `L_i` and heights above the seabed `h_i`,
produced by the settling module for a given impact sample, together with whatever scour, impact
depressions or linear disturbance the field created. `W` is a draw, not a summary: settling emits
samples precisely so that this module can integrate over them (ARCHITECTURE decision 2, option 3).

For scale, the module header inherited from the M3 migration quotes the ATSB: "aircraft debris fields
typically cover areas larger than 200 m by 200 m" (ATSB 2017, p. 96). *Status: inherited, not
re-verified — see §8.*

## 2. What a detection is

Three candidate definitions, and the one adopted.

| level | event | why not / why |
|---|---|---|
| L1 piece | a single piece returns a contact that an analyst classifies as man-made | too strong on its own: it makes a large field almost certainly detected, because independent per-piece classification drives `Π_i (1 − q)` to zero for `N` in the hundreds |
| L2 cluster | several pieces within one resolution neighbourhood form a recognisable signature | this is what the operational record actually did — contacts were listed, clustered, revisited and dismissed |
| L3 field | the field's spatial pattern, density anomaly or scour is recognised | real, but not separable from L2 in any data this project can obtain |

**Adopted: a two-part event.** Campaign `k` detects the wreck when

1. **at least one piece is imaged in the detectable class** — it falls inside valid data for `k` and is
   large enough, against that sensor at that range and on that terrain, to produce a classifiable
   return; and
2. **the imaged material is recognised** as man-made and pursued — the campaign's quality-assurance
   chain, including revisiting contacts assessed as potential debris.

Part 1 is where piece size, sensor resolution and swath geometry enter. Part 2 is a **campaign-level,
not a piece-level**, event: the same analysts, the same classification rules, the same seabed texture
and the same QA process act on every contact in a campaign. Treating recognition as independent per
piece is not defensible and would make the likelihood collapse to a hard exclusion wherever coverage
exists. This is the single most consequential choice in the module and it is made here deliberately.

## 3. The likelihood that follows

For campaign `k` and a settled field `W`:

```
M_k(W)  =  1 − c_k(W) · g_k(W) · q_k                    (non-detection by campaign k)

g_k(W)  =  1 − Π_i [ 1 − a_k(L_i, h_i, x_i) ]           (some piece is in the detectable class)

P(no detection | W)  =  ρ  +  (1 − ρ) · Π_k M_k(W)
```

with

- **`c_k(W)` — covered fraction.** The fraction of the ground occupied by the field on which campaign
  `k` recorded valid data, read by bilinear interpolation from the 0.01° coverage raster at the
  field's centroid. Off every raster, `c_k = 0` and `ln L = 0` exactly: not searched is no
  information (binding ruling).
- **`a_k(·)` — size response.** The probability that piece `i` is in the detectable class for sensor
  `k`. Defined in §4. Smooth, with no floor, as contract rule 4 requires.
- **`g_k(W)` — in-class probability for the field.** Saturates at 1 as soon as one piece is
  comfortably above threshold. This is where the target model lives, and §6 shows it is close to 1 for
  any field settling is likely to produce.
- **`q_k` — recognition probability, conditional on the target being in the detectable class.** The
  ATSB's per-region data-quality ratings measure exactly this and nothing else. **If a later change
  lets `q_k` absorb terrain masking or burial, ρ double-counts and the change must be refused.**
- **`ρ` — field-level undetectability.** The probability that the field could not have been found by
  any of these campaigns wherever it lay: buried, hidden by terrain at the whole-field scale, or
  imaged and dismissed as geology. It is the shared part of the misses. Reference case 0.05, reported
  with the sweep 0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5.

**Reduction.** Put `N = 1`, `a = 1` (so `g = 1`), one cumulative campaign, `ρ = 0`:
`P(no detection) = 1 − c·q = 1 − P_D(x)`, which is Davey eq. (11.1) exactly. The reduction test of
the architecture entry of 8 October tests this expression and nothing else.

## 4. The minimum detectable piece, per sensor

A side-scan or synthetic-aperture image detects a proud object by two cues: the **highlight**, the
direct return from the object, and the **shadow** it casts down-range, which is usually the stronger
cue on a flat abyssal plain. Both must span enough resolution cells to be classifiable rather than
merely present.

**Resolution cells.**

- Along-track, real-aperture side-scan: `Δy = R · θ`, proportional to range `R` and to the horizontal
  beamwidth `θ`. Resolution degrades linearly across the swath.
- Along-track, synthetic aperture: `Δy ≈ D/2`, half the physical aperture, **independent of range**.
  This is the operational difference between the deep-tow side-scan and the SAS systems and it is why
  the SAS layers are not simply more of the same coverage.
- Across-track: `Δx = c/(2B)` for a chirp of bandwidth `B`, projected onto the seabed as
  `Δx / cos(γ)` with `γ` the grazing angle, so range resolution degrades towards nadir, not away
  from it.

**Shadow length.** For a towfish or AUV at altitude `H` above the seabed, an object of height `h` at
ground range `R` casts a shadow of length

```
S  =  h · R / (H − h)
```

so the same object is far more visible at the outer swath than near nadir, and lowering the vehicle
shortens every shadow. Detection against a flat seabed is therefore driven by `h`, not only by plan
size `L`.

**The size response.** Rather than a hard threshold — which contract rule 4 forbids — the module uses
a log-normal response in the ratio of the shadow (or highlight) extent to the resolution cell:

```
a_k(L, h, x)  =  Φ(  ln( S(h, R, H) / (m · Δ_k(R)) )  /  s_k  )
```

where `Δ_k(R)` is the coarser of the two resolution cells at that range, `m` is the number of cells a
feature must span to be classifiable (literature practice is roughly 2 for detection and 3–5 for
recognition; the module uses `m = 3` and sweeps it), and `s_k` is the spread that carries sensor and
terrain variability. `Φ` is the standard normal CDF, so `a_k` is smooth and strictly between 0 and 1.

**Terrain.** Three distinct effects, kept apart:

1. **No data** — slopes facing away, terrain-avoidance altitude excursions, nadir gaps. These are
   already holes in the delivered mosaics, so they enter as `c_k = 0` and must not also be charged to
   `q_k` or ρ.
2. **Data of reduced usefulness** — layover on slopes facing the sensor, high rugosity raising the
   false-alarm rate so that a real contact is dismissed. This is `q_k`.
3. **Whole-field obscuration or burial** — the field lies in a crevasse, or in sediment. This is ρ,
   and it is the reason ρ is a field-level quantity.

**Campaign sensor classes.** Four, from the Geoscience Australia Phase 2 release, whose layer names
carry the sensor type: deep-tow side-scan (`Inverse Deep Tow (SSS)`), towed synthetic aperture
(`Wide GoPhoenix (SAS)`, `Wide DHJ (SAS)`), and AUV side-scan (`Inverse Autonomous Underwater Vehicle
(SSS)`). All four are delivered as 5 m backscatter mosaics — the grid spacing in the layer descriptors
is 5.56 × 10⁻⁵° in longitude, about 5 m. **The 5 m product grid is the resolution of the delivered
coverage product, not of the sonar**; coverage is measured from the mosaic, detection is modelled at
the sensor's own resolution. Conflating the two was a defect in the archived v01 work and is not
repeated.

## 5. A field partly inside a swath

This is the question the coverage raster cannot answer on its own: `c_k` is a covered fraction over a
0.01° cell, about 1.1 km, while a debris field is a few hundred metres across. Two treatments bound
the answer.

- **(a) Fine-grained.** Each piece is independently inside valid data with probability `c_k`:
  `M_k = Π_i [1 − c_k · a_k(i) · q_k]`. Appropriate when the field is large compared with the scale of
  the coverage gaps.
- **(b) Coarse-grained.** The field is inside or outside as a whole, with probability `c_k`:
  `M_k = 1 − c_k · g_k(W) · q_k`. Appropriate when the field is small compared with the gap and swath
  structure.

**Adopted: (b), with (a) as a labelled sensitivity.** The gaps in the Phase 2 mosaics are swath-edge
and terrain-avoidance features at scales of hundreds of metres to kilometres — comparable to or larger
than the field — so coverage over a field is strongly spatially correlated, not a set of independent
per-piece coin flips. (a) would understate the chance that the whole field fell in a gap.

Two consequences worth stating because they constrain what the module can claim:

1. **The reduction test cannot distinguish (a) from (b).** For a single piece they are identical.
   The choice only acts once settling supplies multi-piece fields.
2. **Nothing in the coverage data resolves it.** The honest treatment is the sensitivity, and the
   decision rule is contract rule 7: settle by evidence if any arrives, otherwise report as a labelled
   alternative.

## 6. What the target model is actually worth

Under §3, `g_k(W) = 1 − Π_i [1 − a_k(L_i, h_i, x_i)]` saturates quickly. A field of even a few dozen
pieces, of which a handful are metres across and a metre or more proud of a flat abyssal seabed, gives
`g_k` indistinguishable from 1 against any of these sensors. The likelihood then reduces to

```
P(no detection | W)  ≈  ρ + (1 − ρ) · Π_k [1 − c_k q_k]
```

which is the M3 expression with a point target. **So the detectable-target model earns its place in
two regimes only:** a field that is small, low-relief or buried — where `g_k` falls below 1 — and a
field whose extent rivals the coverage-gap scale, where §5 bites. Everywhere else the result is set by
coverage and ρ.

That is a finding, not a reason to skip the model: it says the module's uncertainty budget belongs to
ρ and to the coverage rasters, and that effort spent refining the piece-size distribution will not
move the posterior. It also says the point-target placeholder of brief §3 is not a crude stand-in —
it is the saturated limit of the full model, and runs made with it are valid wherever `g ≈ 1`.

**The placeholder, specified.** Until settling delivers fields: `N = 1`, `a = 1`, `g = 1`, field
centroid at the impact position. Labelled "point target, provisional" in every figure. The first
parametric field, when it is needed, is an isotropic Gaussian scatter of characteristic radius 150 m
about the settled centroid with a log-normal piece-size distribution; its parameters are not yet
evidence-backed and it is not used for any reported number until they are.

## 7. A correction to carry into step 4

The brief states that the marginal likelihood depends only on the mean of ρ, so a broad prior on ρ
gives the same answer as a point mass at its mean. **That is exactly true for the expression in §3,
which is linear in ρ** — and it is the reason ρ is swept rather than given a distribution.

It stops being true under a *dependent* repeat-search model built from a continuous shared
detectability. If campaign misses are correlated through a latent variable `v` with `E[v] = 1 − ρ`,
then `E[Π_k (1 − c_k q_k v)]` involves the higher moments of `v` wherever two or more campaigns
overlap. The two-state model of §3 — undetectable with probability ρ, otherwise independent across
campaigns — is itself a dependent model, and the one for which the mean-only property holds. Step 4
must therefore report which dependent construction it uses, and must not carry the mean-only claim
across to a construction where it fails.

## 8. Provenance and status of every quantity

| quantity | value / form | status |
|---|---|---|
| coverage `c_k` | 0.01° raster, bilinear, from the GA 5 m Phase 2 mosaics | **measured**, approved under composition rule 3 |
| Phase 2 areas | deep-tow 103,921.5 km², GO Phoenix 14,627.3, DHJ 3,164.3, AUV 16,164.1, union 120,486.5 km² | **measured** from the mosaics |
| `q` Phase 2 | 0.940–0.945, from ATSB per-region detection ratings conditional on data present | **inherited** from the M3 header (ATSB 2017, Fig. 73, p. 96); not re-verified |
| `q` Bluefin-21 | 0.9, not rated by ATSB | **assumed**, and the campaign removes no mass on the fixture |
| swath width about the arc | 25 NM either side, widened to 36 NM north-west and 41 NM south-east | **inherited** (ATSB 2017, pp. 76, 95); not re-verified |
| debris-field extent | "larger than 200 m by 200 m" | **inherited** (ATSB 2017, p. 96); not re-verified |
| ρ | 0.05 reference, swept 0 → 0.5 | **ruled** (Pete, 8 October) |
| `m`, cells to classify | 3, swept | **assumed** from survey practice |
| `s_k`, size-response spread | per sensor class, to be set when `g < 1` matters | **not yet set**; irrelevant while `g ≈ 1` |
| field model | point target now; Gaussian scatter, log-normal sizes later | **placeholder**, labelled in every figure |

**The ATSB report could not be fetched this session.** `www.atsb.gov.au` was allowlisted on request but
did not respond — two attempts, 120 s and 300 s, both timed out at the read, with no HTTP status. The
four rows marked *inherited* therefore stand on the M3 module header, which cites them by page. They
are flagged here rather than silently adopted, and verifying them against the report is an open item;
none of them is load-bearing for the port or the reduction test, and `q` enters the result only
through its product with `c`.

## 9. Tests this definition commits the module to

1. **Reduction to Davey eq. (11.1)**: `ρ = 0`, `N = 1`, `a = 1`, one cumulative campaign ⇒
   `1 − P_D(x)` to numerical precision.
2. **Averaging**: two identical settling draws give the same likelihood as one. Alternative draws are
   alternative outcomes; their non-detection probabilities are averaged, never multiplied.
3. **Off searched ground**: `ln L = 0` exactly, never NaN.
4. **ρ-mean**: a broad ρ distribution and a point mass at its mean give the same marginal, for the §3
   expression — and §7 says where that test may not be extended.
5. **Saturation**: `g_k → 1` monotonically in the number of in-class pieces, and the likelihood of a
   many-piece field matches the point-target likelihood to within the tolerance claimed in §6.
6. **Coverage-grain sensitivity**: (a) and (b) of §5 agree exactly for `N = 1` and are reported as a
   labelled pair for multi-piece fields.

---

*Searched areas, 9 October 2026. Written before the port, as brief §7 item 2 requires.*
