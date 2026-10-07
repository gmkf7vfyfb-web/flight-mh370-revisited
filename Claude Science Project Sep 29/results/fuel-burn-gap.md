# The fuel burn gap: root cause, fix, and what it invalidates

Supersedes the earlier version of this note, which named a cause it had not confirmed. The
cause is now identified exactly, reproduced in isolation, fixed, and re-validated against
Boeing's own figures.

## 1. What the defect was

`FuelTables::fuel_flow_kg_h` interpolates fuel flow between the two tabulated speed schedules
that bracket the particle's Mach, fitting `a·M² + b/M²` through the pair. Two of the five
schedules — CI = 52 and LRC — are Ulich's reconstruction of the same cruise regime, and between
FL270 and FL430 their tabulated Mach numbers agree to **four decimal places** at some gross
weights without being bitwise equal. The code removed duplicate points with
`dedup_by(|a, b| a.0 == b.0)`, exact float equality, so it caught the pairs that happened to
round to the same bits and left the rest as two distinct points a few times 10⁻⁵ apart.

The fit through such a pair has determinant `m0²/m1² − m1²/m0²` of order 10⁻⁴. The tabulated
flows at the two points differ only by table rounding — about 1.5 kg/h — and that difference is
then divided by the determinant and extrapolated. At FL270 and M0.82, over 0.4 t of gross
weight:

| gross weight | top-pair Mach gap | flow returned | true cruise flow |
|---|---|---|---|
| 208.50 t | 0.000080 | 5,619 kg/h | ~6,200 |
| 208.60 t | 0.000080 | 4,171 kg/h | ~6,200 |
| 208.65 t | 0.000049 | 2,100 kg/h | ~6,200 |
| **208.70 t** | 0.000019 | **no flow at all** | ~6,200 |
| 208.75 t | 0.000012 | **30,195 kg/h** | ~6,200 |
| 208.80 t | 0.000042 | 13,830 kg/h | ~6,200 |

So the visible symptom — a step that burnt nothing — was the sign change in the middle of a
numerical catastrophe, not the whole defect. Either side of it the model priced the same cruise
condition anywhere from a third to five times the correct flow.

**Why it concentrated instead of averaging out.** When the lookup returned nothing,
`burn_fuel` returned without burning, so `fuel_kg` did not change, so `weight_t` did not
change. If altitude and Mach held, the next step failed identically: the pocket is an
**absorbing state**. A path that entered it flew free for the rest of the leg. The particle
filter then did exactly what it is built to do — the endurance requirement rewards paths that
still have fuel, so those paths were resampled into many copies. The sampler found a numerical
singularity in the model and exploited it.

That is the signature in the posterior: the fraction of the leg spent not burning was
**bimodal**, not uniform. Exactly 61.6 % of mass had none of it; 24.8 % spent 40–100 % of the
leg in the pocket.

**Why it hid for so long.** Three reasons, all worth remembering:

1. The time was accumulated into `fuel_below_tables_s`, pooled with the FL060 clamp. The two
   have **opposite** effects on burn — the clamp burns at a higher flow than cruise, the pocket
   burns nothing — so pooling them made a fuel-conserving defect look like an altitude
   diagnostic.
2. The code comment on the branch asserted it meant "outside the weight grid entirely, which
   the prior cannot reach". That was **wrong**, and because it sounded impossible nobody read
   the counter.
3. It needs FL270–FL430 *and* a specific gross weight *and* a Mach above the top schedule.
   The failing region is 0.05–0.44 % of the (weight × Mach) domain at a given level. A static
   sweep of the reachable domain on a 2 t weight grid steps straight over it — mine did, twice,
   which is why I could not find it by reading the code.

## 2. How it was found

Reasoning about the code had failed, so I instrumented it. Splitting the counter into
`fuel_no_flow_s` and recording a cause code took one rebuild and a two-minute 280 k-particle
run, and settled it immediately: `fuel_below_tables_s` was **exactly zero** — the FL060 clamp
never fires, confirming the altitude evidence — and 20.6 % of mass carried no-flow time with
all three arguments finite and in range. Recording the arguments of the first failing step then
gave FL270–300, 183–209 t, M0.735–0.840: ordinary cruise. Replaying those in a faithful Python
port reproduced the failure on the first try.

The lesson is cheap to state: when static reasoning about a defect fails twice, stop reasoning
and make the program say what it did.

## 3. The fix

In `points_at`, schedules whose tabulated Mach agrees to within `MACH_MERGE_TOL = 5e-3` are
merged into one point, averaging both coordinates. Two nominally different schedules whose
tabulated Mach is indistinguishable **are** one point, and two points at the same Mach with
different flows is contradictory data that must be resolved before any fit, not after. The
tolerance sits two orders of magnitude above the tables' own Mach rounding and two orders below
the narrowest genuine schedule separation (0.0053 Mach, CI 52 to LRC at FL270), so it separates
the schedules that differ and joins the ones that do not.

Two guards back it up: a near-singular determinant or a non-positive fitted flow now falls back
to the nearest tabulated flow and sets `Coverage::fit_fallback`, and the Mach bracket search
defaults to the lowest pair rather than propagating `None`, so a NaN Mach cannot buy a free
step either. **A step that cannot be priced must never be a step that is free.**

Three regression tests enforce it: no cell in the reachable domain FL060–430 × 174–218 t ×
M0.41–0.90 may return no flow or a runaway flow; the FL270 weight window must price within
1 % across 1 t; and no two points at one (level, weight) may remain inside the merge tolerance.
`cargo test --release` is 56 tests, up from 53.

I also tried a second guard that widened a narrow pair before extrapolating from it. It is
**not** in the fix: it made two of Boeing's extrapolated points worse and, in its first form,
could oscillate between two narrow pairs forever. The test suite hung rather than failed, which
is how I found it. A guard that can loop is worse than the hole it plugs.

## 4. Boeing validation

`.sources/fuel-performance/validate.py` against Appendix 1.6E of the Malaysian safety report
(the appendix text survives in the frozen Sep 28 snapshot), before and after:

| | inside the schedules | above M0.84 | below the holding schedule |
|---|---|---|---|
| before | **1.0085 ± 0.0178** (11 items) | −8.1 % to +0.9 % (4 items) | −8.5 % to +3.7 % (8 items) |
| after | **1.0086 ± 0.0178** (11 items) | −8.7 % to +0.9 % (5 items) | −11.5 % to +3.7 % (8 items) |

The calibration the whole fuel model rests on is unchanged to four decimal places, and the
tolerance test still passes with nothing beyond 3 s.d. The largest change to any single
in-range item is 0.05 %.

Two honest costs. The merge moves the anchor point of the far extrapolations, so the worst
extrapolated item degrades from −8.5 % to −11.5 % (FL400 at M0.727, below the lowest schedule
there); the module documentation now states "up to about 12 %" rather than 8 %. Against that,
the fix prices one row of Boeing's own Table 4 — FL400 at M0.861 — that the unmerged code
could not price at all, so the "above M0.84" group gains its fifth item.

One model-validity limit is now documented rather than silent: below about M0.41 the `b/M²`
term runs away, reaching 66,112 kg/h at FL375 and M0.20. That is the fit extrapolated far
outside its validity, not a flight condition, and unlike the no-flow pocket it is
self-limiting — such a path goes dry within minutes instead of flying for free. No configured
run reaches it; the widest Mach prior floors at 0.41.

## 5. What this invalidates

Every absolute fuel quantity from every run that used the defective binary. Specifically:
mean fuel remaining (6,462 kg), fraction dry by 00:19:37 (36.8 %), the implied burn rate
(4,788 kg/h whole posterior, 4,190 kg/h never-dry), the exhaustion-time histogram, and the
conditioned-on-exhaustion posteriors.

The 4,190 kg/h figure was the tell and I read it too charitably at the time: it sits below the
entire FL350/192 t tabulated cruise band of 5,395–6,241 kg/h, at a lighter weight than this
flight began. 5,950 × 0.805 = 4,790 kg/h reproduces the measured whole-posterior rate to three
figures, i.e. the posterior was burning correct cruise flow for 80.5 % of the leg and nothing
for the rest.

**Partly** invalidated: the arithmetic on the exhaustion term. The *conclusion* that it is
nearly inert survives, and is the reason the term is being dropped, but both the number and
the mechanism have moved. On the defective binary the term was worth 0.09 nats because almost
nothing ran dry, so a never-dry path was scored once at the last step, 127 s from the target
against σ = 300 s — a flat −0.0896 nats that could not distinguish 100 kg remaining from 10 t.
Re-measured on the fixed binary, where about half the posterior does reach exhaustion, the
term is worth **0.168 nats**: the dry paths land a mean 197 s from 00:17:30, which is 0.66 σ.
So it is still flat, for the opposite reason. The full re-measurement, including why the
6.79-nat log-evidence gap is 6.62 nats of Gaussian density normalisation rather than misfit,
is in `exhaustion-prior-is-nearly-inert.md`.

**Not** invalidated: everything else that does not depend on an absolute fuel state. All
fuel-free runs are untouched, as is the convergence ledger's fuel-free half.

## 6. The clean subset, and why it is a preview and not a result

Selecting the 61.0 % of posterior mass with no no-flow step (replicate-mean pooling; the
replicate spread is wide, 55.0–74.8 %, which is itself a symptom):

| | all paths | clean subset |
|---|---|---|
| mass | 100 % | 61.0 % |
| distinct 18:01 roots | 40,427 | 32,411 (80 %) |
| median latitude at 00:19:37 | −37.636° | **−37.290°** |
| 50 % interval width | 1.10° | **0.80°** |
| 90 % interval width | 3.70° | 2.80° |
| shoulder mass (−36.5 to −34.5) | 0.107 | **0.165** |
| dry by 00:19:37 | 36.2 % | **57.2 %** |
| split-half overlap | 0.9109 | 0.9232 |

It is a **biased** subsample, not a corrected posterior. The removed paths are measurably
slower — final Mach median M0.791 against M0.818 — because the pocket needs a Mach above the
top schedule at FL270–300, and the slow southern paths were the ones that found it and then
survived on free fuel. So the clean subset over-represents fast, direct, northern trajectories
and its 0.35° northward shift is an upper bound on the fix's effect, not an estimate of it.

The same selection on the single surviving BFO 4 Hz replicate is recorded for direction only:
one replicate admits no convergence diagnostic at all.

## 7. Corrections to the record

- The previous version of this note said the failing branch "returns without burning". The
  direction was right but the branch was wrong: it named the `None` arising from the weight
  grid, which never fires. The actual return is the non-positive-flow guard at the end of the
  fit.
- "Every trajectory burns no fuel for about 20 % of the time" was wrong. The distribution is
  bimodal: 61.6 % of mass clean, 24.8 % spending 40–100 % of the leg in the pocket. The 19.55 %
  figure was a mass-weighted mean across both modes.
- The Python port that found "no `None` anywhere" was not faithful: it iterated LRC's 35-level
  flight-level grid in the step-down loop where the Rust iterates holding's 10 levels, and it
  swept gross weight on a 2 t grid that steps over a pocket 0.05 t wide. Both are fixed in the
  port used in section 2.
