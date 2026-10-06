# Compute plan: what the queue costs, and how to pay less for it

Every number here is measured on this machine (18 cores, 64 GB) or scaled from a measurement by a
stated rule. Nothing is a guess. Where a figure is inferred rather than timed, it says so.

## The cost model

Runtime is linear in particles × replicates, which is worth stating because it is what makes
smoke-scale calibration trustworthy: scaling the full-scale `best-model` run down to 1M × 2 seeds
predicts 884 s and the measured time was 760 s, 14% apart. So a 13-minute smoke run ranks a model
change reliably, and nothing needs a full run to be *ranked* — only to be *quoted*.

Full scale throughout means **7,000,000 particles × 8 replicates, one measurement case**.

| configuration | full-scale wall | how obtained |
|---|---|---|
| no fuel, 0 tempered epochs | ~0.35 h | inferred, c-series ratio |
| no fuel, 2 tempered | **0.45 h** | measured, `runs/tempered-1839-1941` |
| no fuel, 3 tempered | **0.62 h** | measured, `runs/tempered-three` |
| no fuel, 6 tempered | ~1.0 h | inferred, c-series ratio 2.92 |
| **fuel, 3 tempered** | **6.88 h** | measured, `runs/best-model` |
| **fuel, 6 tempered** | **11.3 h** | measured, `runs/best-model-6temper` |
| fuel, 6 tempered, wide Mach | **~9.7 h** | scaled, f6w/f3 = 1.41 |
| fuel, 7 tempered (+18:25) | ~11.9 h | inferred, +1 epoch at 139 s smoke |
| fuel, 6 tempered, 32 stages | ~18.3 h | inferred, stage arithmetic |

Two multipliers do the work:

- **Fuel costs 11.1×** (6.88 / 0.62 at matched tempering and particle total). This is the single
  dominant cost in the project and it is not the table lookups — it is the endurance proposal
  evaluating 16 Mach cells per manoeuvre draw plus the rejection of doomed trajectories.
- **Each tempered epoch costs ~18% of the untempered base** at 16 stages (three added epochs took
  f3 → f6, 760 s → 1178 s). Tempering is cheap. Fuel is not.

**The smoke rule has now been checked against a full run.** At smoke scale f6/f3 = 1.55, so the
six-epoch full-scale run was predicted at 1.55 × 6.88 = 10.7 h. It measured 11.3 h, a ratio of
1.64×. The rule under-predicted by 6%, in the same direction and of the same order as the 14% seen
on the particle-count scaling. Treat smoke-derived full-scale costs as a lower bound with roughly
10% headroom; they remain reliable for *ranking* changes, which is all they are used for.

A note on reading that 11.3 h out of the run record: `runs/best-model-6temper/run.json` and
`model-comparison.csv` both record `runtime_h = 9.89`, which is **seven** replicates. The run was
assembled from two launches after the first died at seed 2, and the resume covered seeds 2–8 while
seed 1 survived from the first attempt. The like-for-like eight-replicate figure is 9.89/7 × 8 =
11.3 h. Dividing the recorded 9.89 by `best-model`'s 6.88 gives 1.44× and compares seven replicates
with eight.

Smoke-gate costs at 1M × 2 seeds, one case: no fuel ~1–4 min, fuel + 3 tempered **12.7 min**,
fuel + 6 tempered **19.6 min**.

## (a) Temper 20:41, 21:41 and 22:41 — validated, do it first

Already tested at smoke scale (f3 against f6, identical in every other respect):

| epoch | 3 tempered | 6 tempered | change |
|---|---|---|---|
| 20:41 | 3.61% | **25.24%** | **7.0×** |
| 21:41 | 9.25% | **46.43%** | **5.0×** |
| 22:41 | 6.55% | **38.17%** | **5.8×** |
| everything earlier | — | — | identical to 2 d.p. |
| 00:11 | 11.38% | 12.70% | 1.12× |

Log evidence is unchanged within replicate noise (−104.263/−104.486 against −104.247/−104.544),
which is the check that matters: tempering sums its exponents to one, so it must not move the
evidence, and it does not.

The bottleneck returns to **19:41 at 5.59%**, which is already tempered at 16 stages. So this
intervention does what the diagnosis said it would and hands the problem back to where tempering
was first applied.

**Cost: ~10.7 h predicted.** **Caveat that must not be dropped:** per-epoch ESS is not replicate
agreement. This project has already been burned by that once — tempering 00:11 lifted its ESS 4.3×
and changed no convergence measure at all. So this is the right experiment, and it is not a promise
of a passing split-half.

**Outcome (run, 11.3 h):** the caveat was the operative sentence. Full scale reproduced the smoke
ESS gains almost exactly — 20:41 2.50% → 25.86%, 21:41 7.63% → 45.12%, 22:41 5.54% → 38.13% — with
log evidence unmoved at −104.748, epochs before 20:41 identical and epochs after differing by
≤0.3%. Split-half agreement went 0.8798 → **0.8869** against a 0.924 floor: a gain of 0.0071 for
1.64× the compute. The replicate median span did tighten, 0.391° → 0.306°. This is the second
independent demonstration that per-epoch ESS is not what limits replicate agreement. Written up in
`results/tempering-is-not-the-fix.md`.

## (b) Fuel with the wider Mach range — we have effectively done it, and it is worse

Two things to separate. **Fuel with a wide Mach prior has already been run**: the `stage2-fuel`
family uses `mach_range = [0.41, 0.86]` and is the worst-converging family in the project, split
half 0.743–0.755 against 0.829 for the book's range, with 69% of posterior weight on paths whose
tanks ran dry before 00:11. What is genuinely new is wide Mach *with the tempered sampler*, and
up to 0.87 (the 777-200ER M_MO) rather than 0.86.

Measured at smoke scale, f6w (Mach 0.41–0.87, altitude floor lowered to 2,000 ft) against f6:

| quantity | book Mach | wide Mach |
|---|---|---|
| 18:25 ESS | 17.17% | **2.35%** |
| 19:41 ESS | 5.59% | 4.27% |
| log evidence | −104.396 | −106.858 |
| median latitude | −37.657 | −38.041 |
| overlap with Fig. 10.3 | 0.6430 | 0.5235 |

It costs 2.46 nats, moves the median *away* from Davey's −37.532, drops the overlap by a fifth,
and makes **18:25 — the first arc, untempered — the new bottleneck at 2.35%**. Runtime is
unaffected: 1072 s against 1178 s, slightly *cheaper*, because the fuel model dooms more
trajectories early.

These are two-seed smoke runs, so the split-half figures from them are single partitions on two
replicates and are indicative only — smoke runs are never evidence. But the direction is
consistent with the earlier full-scale wide-Mach family, so the recommendation is: **do not spend
~10 h on wide Mach as it stands.** If the wide prior is wanted for its own sake — and there is a
real argument that a fuel model should be allowed to decide the speed rather than inheriting
Davey's floor — then temper 18:25 as well (7 epochs, ~11.9 h) and expect to defend a worse
agreement with Fig. 10.3 as the honest consequence of a less informative prior.

## (c) The waypoint hypothesis — not built

`hypotheses/` contains `_template`, `altitude-prior`, `antenna-gain`, `arc-kernel` and
`initial-mach`. There is no waypoint module. This is development work, not a compute item.

The specification is complete and unusually detailed (`results/waypoint-stratum-spec.md`): three
phases with their own candidate sets, the phase-3 polygon, the rule that transition out of
waypoint navigation is sampled north of the polygon's southern boundary with every trajectory
transitioned by the time it crosses, and a destination catalogue for the post-transition
lateral-navigation flavour. One geometry item is still open: the phase-3 ring must close up the
92°E meridian, and the literal walk in the spec self-intersects.

Compute, once built: the "without" arm **is** run (a), so only one extra run is needed, at (a)'s
cost — **+11.3 h** — plus the smoke gate.

## (d) Controlled descent before fuel exhaustion — not built, and the design is not on record

What is on record is the requirement, in `results/core-model-stages.md`: the descent hypothesis
"cannot be tested by adding the term alone: it needs a model in which a descent is *sustained* — a
declared descent-onset latent with its own particle budget". The specification for that latent was
never written. `bfo_vertical_rate` is already implemented and is already **on** in `best-model`,
and is inert in cruise because only ~0.7% of flight time sits in a level change.

**The machinery to avoid generating descending trajectories throughout the flight already
exists**, which is the design recollection worth acting on. The filter has a configurable **stop
epoch**, `[terminal]` carries `handoff`/`handoff_floor`/`children`/`arc`/`target`, the config
takes "observation IDs of bursts after the stop, e.g. `m0019a.bto`", and `mh370 terminal <run-dir>
<config> <out>` re-runs the end-of-flight stage alone from the stored hand-off. So:

> Run the filter **once** to 22:41 with fuel and tempering, then branch every descent family off
> the stored hand-off, scoring 00:11, 00:19:29 and 00:19:37 in the terminal stage.

That converts (d) from N full runs into one filter run plus N cheap stage-2 runs. Estimated filter
run to 22:41: **~8.5 h** (the four dropped epochs are mostly cheap, but 00:11 is tempered).
Terminal variants: a small fraction of that each, since they start from a resampled hand-off
rather than 7M particles.

Two things this must respect. The existing end-of-flight design pairs top of descent with
flame-out — an unpiloted model — so a controlled descent before exhaustion is a **new terminal
family**, not a parameter of the old one; and `decisions/eof-no-unpiloted-assumption.md` requires
piloted and unpiloted cases to be covered without preference and reported per assumption. Also
worth noting for the paper: at 17.50 Hz per 1,000 ft/min, the 00:19 pair's 184 Hz step in 8 s is
~10,500 ft/min, about nine times the largest bias excursion in the book's own Fig. 5.4 — so that
pair can discriminate a steep descent, whereas the single 00:11 value cannot be separated from a
±20 Hz bias excursion.

The aside about earlier measurements is worth a separate test: 18:25 and the 18:39 call. 18:25 ESS
already falls from 17.17% to 13.30% when fuel is added, and it collapses to 2.35% under a wide
Mach prior, so any descent latent placed there needs its own tempering before it means anything.

## Optimisation: where the savings actually are

1. **The smoke gate, every time.** 13–20 minutes ranks a change that would cost 10 h to run.
   It is what established (a) and ruled out (b) today. Nothing new goes to full scale unranked.
2. **One filter run, many terminal variants** (the stop-epoch split above). This is the single
   biggest structural saving in the queue and it applies to every impact-level module later —
   settling, hydroacoustics and searched areas all consume the same hand-off.
3. **Particle allocation is free.** `best-model` gave every mode 20% of the particles while the
   posterior weights are true track 59.2%, lateral navigation 24.6%, true heading 10.2%, magnetic
   track 4.8%, magnetic heading 1.2%. The fuel-free tempered runs used an unequal split. Allocate
   deliberately: by posterior mass, or toward whichever modes are ESS-limited. **This is now the
   leading candidate for the convergence failure, not a housekeeping note.** Across the eight
   six-epoch replicates, true track and lateral navigation hold 83% of the mass and swing 33% and
   54% of their own value between replicates; the converging fuel-free run gave each of them 2.5M
   particles against `best-model`'s 1.4M, so true track had ~2,310 independent draws there against
   ~990 here.
4. **One measurement case, not two.** `config/davey2016.toml` also runs a `bto-only` case at two
   seeds. Every sensitivity config already overrides to the single `bto-bfo` case; keep doing it.
5. **Temper only where it pays, and check it paid.** 00:11 tempering bought nothing fuel-free but
   does help with fuel (4.60% → 11.62%). 22:41's benefit is concentrated in true track. These are
   per-configuration facts, not general ones.
6. **Don't stack (a) and (b).** Changing the sampler and the prior in one run leaves nothing
   attributable. (a) against `best-model` is one variable.
7. **Watch the manoeuvre-step fidelity fix.** Going from 5 s to the book's 1 s is a 5× increase in
   manoeuvre integration work and could be the most expensive single item in the queue. Measure it
   at smoke scale before committing.

## Recommended order

| # | item | cost | gate | status |
|---|---|---|---|---|
| 1 | (a) fuel + 6 tempered epochs, book Mach | 11.3 h measured | smoke-validated | **done — split-half 0.8869, still fails 0.924** |
| 1b | reallocate particles by posterior mass at 6 tempered epochs | ~11 h | follows from the band decomposition | **running** |
| 2 | if 19:41 still binds: 32 stages | 18.3 h | smoke first | deferred — tempering twice shown not to be the lever |
| 3 | BFO 4 Hz shoulder re-test, 4 seeds × 3.5M | ~3 h | — | queued |
| 4 | (d) build the descent family; one filter run to 22:41 | 8.5 h + variants | design review first | not built |
| 5 | (c) build the waypoint module; one extra run | 11.3 h | close the polygon ring first | not built |
| 6 | (b) wide Mach, only with 18:25 tempered | 11.9 h | expect worse agreement | deferred |

Item 1b is new and it is the item the six-epoch run earned. The disagreement between replicates is
60.5% in the −38.5..−37 band and only 3.8% in the shoulder, and it is carried by the true-track and
lateral-navigation modes trading ~20 points of probability mass between replicates. `best-model`
gave those two modes 1.4M particles each where the converging fuel-free run gave them 2.5M. Equal
allocation was the wrong call: it starved the modes that set the peak in order to protect a band
carrying 3.8% of the disagreement.

Items 1 and 3 are pure compute on existing code. Items 4 and 5 are development first, and item 4
needs a written specification before it needs cores.
