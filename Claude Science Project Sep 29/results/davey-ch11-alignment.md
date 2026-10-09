# Davey et al. (2016) chapter 11 against this project's drift and searched-areas methods

Architecture session, 8 October 2026. Source: Davey, Gordon, Holland, Rutten and Williams, *Bayesian
Methods in the Search for MH370*, ch. 11 "Ongoing Refinement", printed pp. 101–109 (page numbers from
the running headers; CC BY-NC 4.0; PDF in the artifact store as `10.1007_978-981-10-0379-0_11.pdf`).

**Purpose.** For each module, state where this project follows Davey, where it departs, and for each
departure either the argument that defends it or the decision to adopt Davey's approach instead.

**Correction to the project's own record.** Davey did not merely propose a drift update; §11.2
performed one, for a single object — the Réunion flaperon. This project extends it to many objects.
For searched areas, §11.1 gives the mathematics and does not apply it.

---

## 1. Ocean drift

### What Davey did

- **Update form (eq. 11.4, p. 103).** Re-weight each particle by the likelihood that debris released
  there arrives at the find location: `p(x | Z, y) ∝ Σ_p w_p p(y | x_p) δ(x − x_p)`.
- **Transition density, empirically (§11.2.3, pp. 106–107).** From undrogued Global Drifter Program
  trajectories over 30 years in February–April, augmented by "joining" trajectories that passed close
  together — four segments chained, each join creating about 30 new trajectories.
- **Likelihood as a density ratio (eq. 11.9, p. 106).** Kernel density of drifters that reached a small
  region around Réunion in 508 ± 30 days, divided by the kernel density of all drifter positions in
  February–April, each with ε = 10⁻⁴ added, using a fixed 1° kernel.
- **A Poisson debris-field model (eqs. 11.5–11.6, pp. 103–104)** for "one item found at `y` and none
  elsewhere", with expected item count λ and identification probability `P_I`. **Not run**, because λ
  and `P_I` "cannot be adequately specified" (p. 104). The absence of other debris was treated
  qualitatively.
- **Result (p. 109):** the posterior is "shifted very slightly to the North, but the effect is
  negligible".

### Where we are aligned

| | Davey | this project |
|---|---|---|
| Update form | per-particle re-weighting by `p(y | x)` | likelihood on the shared impact samples (contract rules 1 and 3) |
| Debris as an observation | yes, one item | yes, many |
| Undrogued drifters as the right analogue | yes, and drifters not matched to the flaperon acknowledged | undrogued replay validates object response; windage marginalised |
| Thinning and timing | proposed as refinements (p. 104) | recovery layer models arrival, discovery delay and retention; settling supplies the float partition |

The core of the method is the same. The differences are in how `p(y | x)` is obtained and how many
observations enter.

### Where we depart, and why the departure is defensible

**D1. Forward simulation through the 2014–16 ocean, not climatological drifter statistics.** Davey's
transition density pools thirty years of February–April drifters and chains segments from different
years. That assumes the ocean is stationary across years and Markov at the joins, and it mixes
object responses — every drifter, not the flaperon. Controlled forward releases through the actual
2014–16 reanalysis fields give `p(y | x)` for the year that happened, for a declared object response.
**Cost of our choice:** dependence on reanalysis skill, which is why ocean products are declared
alternatives and drifter replay is a validation test.

**D2. No sampling-density denominator, so no ε.** Davey's denominator in eq. 11.9 corrects for drifters
not being deployed uniformly. It is a necessary correction for found data, but it is the source of the
instability the authors note themselves: "large values can occur in areas of limited sample support due
to noise" (pp. 108–109), which ε then suppresses by pulling the ratio towards one where data are thin.
With controlled releases the release density is known by construction — one ensemble per source cell —
so there is no denominator to estimate and no regulariser. This is a strict improvement and it is
consistent with contract rule 4 (no floors).

**D3. Resolution.** Davey's kernel has a 1° standard deviation, about 60 NM, against a posterior
whose 95% width was about 4.5° (digitised from their Fig. 10.3). This project's reference posterior has
a 50% width of 0.85° (51 NM) and a 90% width of 2.85°.

**Corrected 9 October by measurement — the original argument here was wrong.** This note first argued
that Davey's negligible shift was "in part a consequence of the kernel". The drift module tested that
directly (`results/davey-ch11-reproduction.md`, `8b844e3`). Davey's settings on our reference posterior
reproduce their result — median −37.227° → −37.182°, **+2.75 NM north**, ESS fraction 0.988, across four
seeds +0.07 to +5.81 NM, bootstrap +3.0 ± 1.8 NM. **Narrowing the kernel to 0.25° does not enlarge the
shift** (+1.16 NM), and at 0.25° the seed-to-seed variation (TV 0.119) exceeds the update itself (0.095).
So **Davey's negligible result comes mainly from how little the thirty-year drifter record says about a
single find**, which is the reason they give, and not from kernel width. The update acts on the tails —
mass north of 31.5°S rises from 0.025 to 0.036, stably across seeds — a shoulder, not a mode shift.

What survives of D3: a finer source grid is still needed when **many** finds are combined, because their
joint likelihood can have structure that no single find has. That is an argument about D4, not about
Davey's one-item result, and the paper must not imply their kernel caused their answer.

**D4. Many objects, with a shared ocean.** Davey's one item avoids the question of how several items
combine. With many, contract rule 8 applies: the ocean is marginalised once, outside the product over
objects, so that each object cannot select whichever ocean model happens to fit it best.

**D5. The obstacle Davey stopped at can be removed exactly.** Their Poisson model needs λ (the expected
number of items) and `P_I` (identification probability), which they judged unknowable. Write the
thinned intensity of found items from source `x` as `λ q(y | x)`, with `q(y | x) = P_I(y) p(y | x)` and
`Q(x) = ∫ q(y | x) dy`. For `N` found items at `y_1 … y_N` the Poisson likelihood factorises into

```
Poisson(N ; λ Q(x))  ×  Π_j  q(y_j | x) / Q(x)
```

With the scale-invariant prior `p(λ) ∝ 1/λ`, the count term integrates to `Γ(N)/N!`, **independent of
`Q(x)`** — verified numerically for N = 1, 9, 41 and Q from 10⁻⁴ to 5. So:

1. **λ drops out exactly.** The marginal likelihood equals the likelihood conditional on the number of
   finds.
2. **A single global constant in `P_I` cancels** between numerator and `Q(x)`. *Corrected 9 October,
   from the drift review:* that is all that cancels. The **relative levels between coast-and-time
   blocks are unknown and do not cancel**; they must be latent parameters marginalised as part of η,
   not declared values. Absence of finds is only informative where identification was possible — the
   drift module's test confirms a source sending half its items to a searched coast with nothing found
   loses exactly 2³ over three finds, and loses nothing when that coast's `P_I` is 0.
3. **The absence of finds elsewhere enters automatically, through `Q(x)`.** A source that would have
   sent most items to a coast with high identification probability — Western Australia is the case
   Pete has queued — is penalised when nothing was found there. That is Davey's qualitative argument
   made quantitative, and it addresses the queued Western Australia reminder.

This is the drift brief's "conditioning denominator" (§4), now with its justification. **The price** is
the information carried by the count itself, which is given up under the vague prior on λ. That is the
honest trade, and it should be stated.

**What it still requires:** a model of the relative identification probability by coast segment and
**by time**. Search effort on the coasts rose sharply after the flaperon was found in July 2015, so
`P_I(y, t)` is not stationary. That is a modelling task, not a parameter to fit.

### Where Davey is better, or has something we lack — adopt

**A1. A drifter-empirical arm.** Davey's method is model-free and observation-based. Keep it — not as
the estimator but as a declared alternative under `ocean-model`, named `gdp-empirical`, and as the
**reproduction target**: rerun Davey's single-flaperon update with their method on our reference
posterior and reproduce the negligible shift before presenting anything new. A result that differs
from theirs must be traceable to D1–D5, one at a time.

**A2. The temperature-history constraint from biofouling.** Davey marks drifter segments colder than
18 °C, the threshold above which barnacle settlement and growth accelerate, because the flaperon showed
accelerated growth (p. 104, Fig. 11.1). That is an observation about the object's thermal history,
independent of where it beached. **The drift brief does not use it.** Add it as a deferred observation
channel: the reanalysis supplies sea-surface temperature along each simulated path, so the constraint
is cheap once transport exists. Cite the biological literature, not Davey, for the threshold itself.

---

## 2. Searched areas

### What Davey set out

- **Update (eq. 11.1, p. 101):** `p(x_final | S, Z_K) ∝ [1 − P_D(x_final)] p(x_final | Z_K)`, with
  `P_D(x)` "the probability that the cumulative search effort would have detected the aircraft" at `x`.
  The aircraft is stationary, so the prediction stage is degenerate.
- **Planning quantity (eq. 11.2, p. 101):** for an area `A` searched with constant `P_D`,
  `P(find) = P_D ∫_A p(x | Z) dx`.
- **AF447 precedent (p. 102):** side-scan `P_D` modelled as 0.9 — their ref. [40], which Stone et al.
  2014 states as a deliberate cap. Confirm [40] against the reference list.
- **Assumption (p. 102):** given quality assurance, "highly unlikely that the search would fail to
  detect the aircraft if the correct location is searched".
- **Not applied.**

### Where we are aligned

Eq. 11.1 is our update in its simplest case. Set ρ = 0, take a point target at the impact location, and
collapse the campaigns into one cumulative coverage, and ours reduces to theirs exactly:
`P(no detection) = 1 − c(x) q(x) = 1 − P_D(x)`. **The reduction is a required test** — the module with
those three settings must reproduce eq. 11.1 to numerical precision.

### Where we depart, and why

**S1. The wreck rests somewhere else.** Davey evaluates `P_D` at `x_final`, the impact point. The
wreckage settles at a displaced location, as a field. Searched ground is scored where the wreck lies,
which is why settling exists. A defensible departure with no counter-argument: the search swept the
seabed, not the sea surface.

**S2. Campaigns are explicit, with their dependence.** Davey's `P_D(x)` is cumulative and leaves the
combination of efforts unspecified. Ours writes `Π_k [1 − c_k q_k]` per campaign, with dependent misses
as the default — terrain that hid the wreck from one pass hides it from the next.

**S3. ρ ≈ 0 is replaced by ρ = 0.05.** Davey's p. 102 sentence is the assumption ρ ≈ 0. The defence of
the departure is AF447 itself: confident detection estimates had already failed once, which is why
Stone caps them at 0.9. The paper reports the full ρ sweep and states that the marginal depends only
on the mean of ρ.

**S4. Field average, not point evaluation.** Alternative settling draws are averaged. Davey's form has
one point and does not reach this question.

### Adopt

**A3. Eq. 11.2 as a reported output.** Probability of success per candidate area is the quantity a
search planner actually uses, and it falls out of the residual posterior at no cost. Report it for the
residual PDF under each source posterior. It turns "a residual PDF" into "where to look next, and with
what chance", which is Davey's own stated purpose for §11.1.

---

## 3. Summary

| | aligned | departs, defended | adopt from Davey |
|---|---|---|---|
| Drift | update form; debris as observation; undrogued analogue; thinning and timing | D1 2014–16 forward transport; D2 no density denominator or ε; D3 resolution (corrected 9 Oct: not the cause of Davey's small shift); D4 many objects with shared ocean; D5 λ removed exactly by conditioning | A1 `gdp-empirical` arm and reproduction of their result; A2 biofouling temperature constraint |
| Searched areas | eq. 11.1 is the reducible special case | S1 settled field; S2 explicit campaigns and dependence; S3 ρ = 0.05; S4 field average | A3 probability of success per area |

The required tests that make the alignment checkable rather than asserted: **drift must reproduce
Davey's single-flaperon shift with their method** (A1); **searched areas must reduce to eq. 11.1**
under ρ = 0, point target, one cumulative campaign.
