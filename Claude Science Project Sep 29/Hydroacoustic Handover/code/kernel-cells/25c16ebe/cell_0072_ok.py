C.to_csv("eof-dynamics-options-costing.csv", index=False)
note = r"""# End-of-flight dynamics: 6-DOF against extending the point mass — costing and recommendation

All compute figures are scaled from **measured** cost on run-i-dive: 1,179 µs of CPU per descent,
549 integration steps at a 2 s step, 2.15 µs of CPU per step, and a full sweep of 128.0 M descents at
**41.9 CPU-hours = 3.5 wall-hours** on 12 threads. Scaling is (2.00 / step_s) × a per-step work
multiplier, bounded low and high. Development figures are working sessions, not hours.

## 1. Compute, per full sweep

| in-sweep model | step | cost factor | CPU-hours | wall-hours at 12 threads |
|---|---|---|---|---|
| current 3-DOF point mass | 2.00 s | 1 | 41.9 | **3.5** |
| + asymmetric thrust (trim drag, yaw rate) | 2.00 s | 1.2–1.5 | 50–63 | **4.2–5.2** |
| + bank dynamics and spiral mode | 0.50 s | 6.4–8.8 | 268–369 | **22–31** |
| + pitch (short-period) dynamics | 0.10 s | 44–70 | 1,845–2,935 | **154–245** |
| full 6-DOF rigid body | 0.05 s | 320–1,000 | 13,416–41,925 | **1,118–3,494** (47–146 days) |
| full 6-DOF with control loop | 0.02 s | 1,000–3,000 | 41,925–125,775 | **3,494–10,481** (146–437 days) |

**This settles the standing question about running the 6-DOF directly in the sweep: no, by two orders
of magnitude.** Even the lean bound is 47 days of wall time per sweep on this machine, against 3.5
hours now, and the project runs several variant sweeps per week. The architecture's existing choice —
a fast in-sweep model fitted to a 6-DOF ensemble — is not a convenience, it is the only arrangement
that runs.

## 2. Compute, for the 6-DOF used only as a reference

Trivial. This is the part people assume is expensive and is not.

| use | lean | full |
|---|---|---|
| 100,000 reference descents | 0.9 wall-h | 2.7 wall-h |
| 1,000,000 reference descents | 8.7 wall-h | 27.3 wall-h |
| one likelihood evaluation over all ten Boeing traces | 1.7 CPU-s | 5.4 CPU-s |
| a 10,000-evaluation fit | 4.8 CPU-h | 14.9 CPU-h |
| the same with leave-one-out on all ten cases | 53 CPU-h | 164 CPU-h |

So the entire 6-DOF fitting programme is **4 to 14 wall-hours** of compute. The cost of the 6-DOF is
not compute. It is development sessions and the risk of a fit that cannot converge.

## 3. Development effort

| work | sessions | risk |
|---|---|---|
| asymmetric thrust in the point mass | 1–2 | low — three parameters, all with closed-form checks |
| bank dynamics and an explicit spiral eigenvalue | 1–2 | low, but changes the step and so every sweep's cost |
| calibrating the existing phenomenological parameters against the Boeing traces | 2–3 | **medium, and this is the high-value item** |
| 6-DOF phase 0, data and sources | 1 | low |
| 6-DOF phase 1, simulator, control laws, mode verification | 3–5 | medium |
| 6-DOF phase 2, fit and leave-one-out | 3–6 | **high — has already failed once** |
| 6-DOF phase 3, fast model fitted to the ensemble, integration | 3–4 | medium |

Full 6-DOF programme: **11–16 sessions**, with the risk concentrated in phase 2, plus the
identifiability and parameter-budget work that is not yet in the plan at all.

## 4. The argument that decides it

**The 6-DOF's compute is cheap and its information is not.** The fit data is 1 Hz position and
altitude for ten cases — no attitude, no rates, bank only as implied by turn rate. A 6-DOF carries
of order 25–35 aerodynamic derivatives plus mass properties; the traces can constrain perhaps five
to eight effective combinations of them, and the rest are identified only by the prior. The 4 per
cent misfit reduction already observed is what an under-determined fit looks like, not a tuning
problem. Adding optimiser effort will not change it.

**Meanwhile the current model already contains the reduced-order forms a 6-DOF would derive.** The
descending spiral comes out of the same equations as the phugoid under residual bank, and its growth
is set by `spiral_doubling_s`, sampled over 60–120 s. The published 747 figures that the 6-DOF base
would be rescaled from give doubling times of 296 s at Mach 0.70 and 89 s at Mach 0.90 — so the
existing band already brackets the high-Mach case the Boeing dives sit in. **Fitting that one
parameter to the Boeing bank-growth traces is better identified than deriving it from derivatives the
traces cannot constrain**, and it uses exactly the same data.

**And the 6-DOF's main claimed advantage cannot be validated here.** Its value over a phenomenological
model is extrapolation to configurations the traces do not cover. But all ten Boeing cases are
uncontrolled, while the piloted and deliberate families carry 32 and 52 per cent of posterior weight
and have **no trace data of any kind**. A 6-DOF fitted only to uncontrolled dives extrapolates to the
controlled families on the strength of its derivatives — which are the part the data never
constrained. The extrapolation is not more trustworthy for being physically parameterised; it is
only harder to see.

## 5. Recommendation

**Do the cheap extension now; gate the 6-DOF behind an identifiability result.**

1. **Asymmetric thrust in the point mass — do this first.** It closes a measured gap: 36.9 per cent
   of posterior weight has exactly one engine thrusting at descent onset, 22.5 per cent of the
   fuel-exhaustion families fly a single-engine phase of several minutes, and all of it is currently
   flown as a symmetric point mass. Three parameters — engine moment arm from published geometry,
   a trim-drag increment as a function of thrust asymmetry, and a corrected-or-uncorrected yaw
   state — each with a closed-form equilibrium test. Compute cost: 3.5 → 4.2–5.2 wall-hours per
   sweep. One to two sessions.
2. **Calibrate the existing phenomenological parameters against the ten Boeing traces** —
   `spiral_doubling_s`, the residual-bank band, the trim offset at loss of control, the windmilling
   and ram-air-turbine increments. This is plan phase 2 applied directly to the fast model, skipping
   phases 0 and 1. It closes the §8 calibration gate on the uncontrolled arm, which is what currently
   blocks quoting any impact energy or attitude as physics. Two to three sessions, a few CPU-hours.
3. **Add bank dynamics and an explicit spiral mode only if step 2 cannot reproduce bank growth.**
   It costs 22–31 wall-hours per sweep, which is affordable for headline runs and not for routine
   variant sweeps, so it should be earned by a demonstrated failure rather than adopted up front.
4. **Before any further 6-DOF fitting, produce the identifiability analysis the plan lacks**: which
   derivative combinations are observable from 1 Hz position and altitude, which are not, a fixed
   parameter budget against the effective (not nominal) observation count given the traces'
   autocorrelation, and a discrepancy-aware noise model. If that analysis says fewer than about ten
   combinations are identifiable, the 6-DOF's role is permanently that of a *structure check* on the
   fast model — run once, compared once, not fitted — and the programme shrinks from 11–16 sessions
   to about 5.
5. **Write down what validates the controlled families.** Nothing currently does, and nothing
   available can. That belongs in the methods as a declared limitation rather than being left to
   emerge from the absence of a calibration figure.

**What the 6-DOF would still buy, if it is built:** attitude at impact for the controlled families —
currently a placeholder covering 52 per cent of weight — and a demonstration that the fast model's
functional form is adequate rather than merely fitted. Both are real. Neither is urgent against the
onset-truncation and sampling-collapse items, and neither is blocked by doing steps 1 to 3 first.
"""
open("eof-dynamics-options-costing.md","w").write(note)
print(len(note))
