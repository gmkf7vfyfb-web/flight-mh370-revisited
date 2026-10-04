# What Davey et al. (2016) actually specifies, and where this engine departs from it

The book was absent from the working tree for most of this project's life — `paper.pdf` is
gitignored and was never fetched — so a number of things had been inferred from secondary
sources and from the previous ChatGPT-era threads. It has now been obtained from the publisher
(see `.sources/davey-2016/README.md`). This note records what the original says, and audits the
engine against it. Page numbers are PDF pages of the 124-page Springer file.

## The convergence criterion: Davey published none that is quantitative

This was an open question in `results/split-half-threshold.md`, which could only observe that
the project's 0.90 split-half floor was asserted rather than derived and that "what Davey used
is not established". It is now established, and the answer is that he used nothing of the kind.

The phrase "effective sample size" does not occur in the book. Neither does "converged".
"Degeneracy" occurs once, in the generic description of particle filters (p. 30). There is no
split-half statistic, no ESS threshold, and no numerical convergence test anywhere in the text.

What the book does say is procedural (p. 70): rather than running a pre-specified number of
particles, they chose "to adaptively increase the number of particles used until it was possible
to identify an adequate number of likely paths". That is the criterion — a qualitative judgement
about the number of surviving high-weight trajectories, made by the analyst, not a statistic
with a threshold.

**Consequence for the paper.** The 0.90 floor cannot be attributed to Davey and should not be.
The honest statement is that the published work reports no quantitative convergence diagnostic,
that this project introduces one, and that the floor is calibrated against a converged reference
rather than inherited. The calibration in `split-half-threshold.md` stands on its own and is now
the only justification the number has — which is a stronger position than citing a precedent
that turns out not to exist.

## Table 8.2, and the engine audit

Table 8.2 (p. 73) is the authoritative parameter summary. Every row, against the engine's
`Parameters::default()` and `config/davey2016.toml`:

| Table 8.2 | published | engine | |
|---|---|---|---|
| Initial latitude s.d. | 0.4 arcmin | 0.5 NM | **differs**, 25 % wider |
| Initial longitude s.d. | 0.4 arcmin | 0.5 NM | **differs**, 25 % wider |
| Initial control Mach s.d. | Gaussian 0.03 | uniform 0.73–0.84 | **differs**, structurally |
| Initial control angle s.d. | 1° | 1.0° | matches |
| Initial BFO bias s.d. | 25 Hz | 25 Hz | matches |
| Initial Mach deviation s.d. | 0.00311 | 0.003113 (derived) | matches |
| Initial angle deviation s.d. | 0.0826° | 0.0826° (derived) | matches |
| Initial wind deviation s.d. | 5.68 kn | 5.684 kn (derived) | matches |
| Mach reversion β | 1.06 × 10⁻² | 1.058 × 10⁻² | matches |
| Mach noise q | 2.05 × 10⁻⁷ s⁻¹ | 2.05 × 10⁻⁷ | matches |
| Angle reversion β | 9.8 × 10⁻³ | 9.792 × 10⁻³ | matches |
| Angle noise q | 4.07 × 10⁻⁸ rad² s⁻¹ | 4.074 × 10⁻⁸ | matches |
| Wind reversion β | 1.09 × 10⁻³ | 1.087 × 10⁻³ | matches |
| Wind noise q | 7.02 × 10⁻² kn² s⁻¹ | 7.021 × 10⁻² | matches |
| Mean manoeuvre time τ | Jeffreys(0.1, 10) h | Jeffreys(0.1, 10) h | matches |
| New Mach | uniform 0.73–0.84 | uniform 0.73–0.84 | matches |
| Turn angle | uniform ±180° | uniform ±180° | matches |
| New altitude | uniform 25,000–43,000 ft | uniform 25,000–43,000 ft | matches |
| Branching rate n̄ | 3–10 | n/a | **structural**, see below |
| Likelihood threshold η | e⁻²⁵ or e⁻³⁰ | n/a | **structural**, see below |

The three initial *deviation* rows are not configured values in the engine; they are drawn from
the stationary distribution of the corresponding OU process, `sqrt(q / 2β)`. That they land on
Davey's tabulated figures to three significant figures is a real check on the OU constants, and
`crates/flight/src/lib.rs` already carries a test asserting it.

### The three genuine departures

**Initial position spread.** Ours is 0.5 NM against a tabulated 0.4 arcmin, i.e. 0.4 NM. Note
the book is internally inconsistent here: the validation chapter (p. 77) states the same prior
as "0.4° in latitude and longitude", which is 60 times wider and cannot be reconciled with
Table 8.2. Either is negligible against a 29 µs BTO σ of about 2.3 NM, but the table is the
specification and the engine should use it.

**Initial Mach.** Table 8.2 initialises Mach as Gaussian with s.d. 0.03 about the radar-derived
value; the engine draws it uniformly across the full 0.73–0.84 band. This is not a rounding
difference — it is a materially wider prior at 18:01:49, and it is a plausible contributor to
the spread the filter then has to resolve. The plumbing already exists: `Prior::mach_gaussian`
is implemented and simply unset in `config/davey2016.toml`.

**Resampling.** This is the large one. The engine uses systematic resampling of a fixed
population when ESS falls below half. Davey does not resample in that sense at all. Sect. 8
describes a *branching* scheme over independently propagated trajectories: each particle is
treated separately, and at each step a particle with weight `w ≥ η` is duplicated into n̄
branches each carrying weight `w/n̄`, while a particle below the threshold survives with
probability `w` at weight 1 and is otherwise pruned. The weights are left unnormalised until the
very end. The population size is therefore not fixed — it grows and is pruned adaptively, which
is exactly what makes "increase particles until enough likely paths appear" implementable.

They are explicit that this was chosen for exploration rather than efficiency: the scheme "is not
necessarily computationally efficient, but in this particular application it was more important
to broadly explore the enormous state space". Table 8.2 pins the constants we would need, n̄ in
3–10 and η at e⁻²⁵ or e⁻³⁰.

## Davey states this project's 19:41 problem, in advance

The passage at p. 69 is worth quoting against the three failed interventions:

> A problem with sampling from the dynamics is that this can be a very diffuse distribution. In
> the MH370 case, the model allows for turns and speed and altitude changes, and potentially
> several of each can be sampled between measurements. The proportion of particles that sample a
> trajectory close to the measurements will be small and a very large number of samples will be
> required to capture the high probability regions.

"Potentially several of each can be sampled between measurements" is quantifiable from Table
8.2's own τ prior. Over the 4,267 s leg into 19:41, with three manoeuvre clocks each of mean τ
and τ ~ Jeffreys(0.1, 10) h, the expected number of manoeuvres is **7.6** and the probability of
at least one is **83 %**. (An earlier version of `m1941-geometry-and-lookahead.md` quoted 56 %,
computed against a τ range of 1–20 h that is neither Davey's nor the engine's; the engine has
always used 0.1–10 h and the corrected figure is 83 %.)

That is the common cause of the look-ahead, bridge and rejuvenation failures, and the book
anticipates it. It also says what they did about it — branch wide and prune — which is neither
of the two families this project has tried.

## What this changes

1. The 0.90 split-half floor is ours, not Davey's, and the paper must say so.
2. Two prior settings should be corrected to the table: initial position s.d. to 0.4 arcmin, and
   initial Mach to Gaussian s.d. 0.03.
3. Davey's filter assumes **infinite fuel** (assumption 4, p. 74) and applies fuel constraints
   afterwards as a censor. This project's in-filter fuel model is an extension beyond the
   published method, not a reproduction of it, and should be presented that way.
4. The branching resampler moves from "an idea on the list" to "the published method we are not
   yet reproducing", with its constants known. It is the one remedy for the 19:41 bottleneck that
   has the original authors' endorsement.