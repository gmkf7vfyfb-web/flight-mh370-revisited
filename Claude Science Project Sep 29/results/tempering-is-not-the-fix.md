# Tempering the mid-flight epochs: a negative result, and what it localises

`config/sensitivity/best-model-6temper.toml` — the fuel model with six tempered epochs instead of
three, eight replicates of 7,000,000 particles, 11.3 h equivalent. One variable changed from
`best-model`.

**It did exactly what it was designed to do to the per-epoch effective sample size, and almost
nothing to convergence.** That is the result.

## What it bought

| epoch | 3 tempered | 6 tempered | change |
|---|---|---|---|
| 20:41 | 2.50% | **25.86%** | **10.3×** |
| 21:41 | 7.63% | **45.12%** | **5.9×** |
| 22:41 | 5.54% | **38.13%** | **6.9×** |
| every other epoch | — | — | 1.00× |

The three targeted epochs lift by 6–10×. The correctness check is what happens to the others, and
it splits by position:

- **Epochs before the first newly tempered one are identical** — 18:25 13.30%, 18:28:05 67.52%,
  18:28:14 54.53%, 18:39 31.25%, 19:41 5.67% in both runs. They must be, since nothing upstream
  changed.
- **Epochs after it differ by at most 0.3%** — 23:15 58.17 → 58.13%, 00:11 11.62 → 11.65%,
  00:19:29 75.68 → 75.49%, 00:19:37 53.62 → 53.55%. Not identical, and they should not be:
  tempering resamples within each epoch it acts on, so the downstream population is a different
  draw from the same distribution. A 0.3% shift at an epoch running above 50% is resampling
  noise, not a disturbance.

Tempering sums its exponents to one, so the target and the evidence must be unchanged, and log
evidence moves from −104.734 to −104.748 — 0.014 nats, within replicate noise.

The bottleneck returns to **19:41 at 5.67%**, as predicted.

## What it did not buy

| | best-model (3 tempered) | 6 tempered | change |
|---|---|---|---|
| split-half, mean over 35 partitions | 0.8798 | **0.8869** | **+0.0071** |
| split-half range | [0.8260, 0.9368] | [0.8415, 0.9379] | — |
| floor at 8 replicates | 0.924 | 0.924 | **both fail** |
| replicate median span | 0.391° | **0.306°** | 22% tighter |
| median latitude at 00:19 | −37.583 | −37.586 | unmoved |
| overlap with Fig. 10.3 | 0.7825 | 0.7822 | unmoved |
| shoulder | 0.1047 | 0.1060 | unmoved |

A 6–10× improvement in three epochs' effective sample size bought **0.007 of split-half**. The
replicate median span tightening by 22% is the one real gain, and it says the replicates agree
better about *where the centre is* while still disagreeing about the distribution.

**This is the second independent confirmation.** Tempering 00:11 lifted that epoch 4.3× and
changed no convergence measure. Tempering 20:41, 21:41 and 22:41 lifted them 6–10× and changed
convergence by 0.007. Twice is a pattern, not an anomaly: **per-epoch effective sample size is not
what limits replicate agreement in this filter.** Any future proposal justified by "this epoch has
a low ESS" now has to answer this result first.

Runtime, and the derivation matters because the recorded number is not the comparable one. This
run was assembled from two launches: the first died at seed 2 when the app restarted, leaving seed
1 complete, and the resume covered **seeds 2–8**. So `run.json` and `model-comparison.csv` record
`runtime_h = 9.89`, which is the wall time of **seven** replicates, not eight. The like-for-like
figure is 9.89 / 7 × 8 = **11.3 h**, against `best-model`'s 6.88 h for eight — a ratio of
**1.64×**. Dividing the recorded 9.89 by 6.88 gives 1.44× and compares seven replicates with
eight.

The smoke calibration predicted 1.55×, so the scaling rule held to within 6%. An earlier figure of
1.94× quoted from the first two seeds was premature — those ran during start-up, and the settled
rate is 77–85 min per replicate.

## Where the disagreement actually lives

Decomposing the split-half discrepancy by latitude band — mean absolute difference in mass between
the two halves, over all 35 balanced partitions:

| band | 6 tempered | share | fuel-free tempered (converges) |
|---|---|---|---|
| −45 to −40 | 0.0008 | 0.4% | 0.0004 |
| −40 to −38.5 | 0.0695 | 30.8% | 0.0359 |
| **−38.5 to −37** | **0.1367** | **60.5%** | 0.0464 |
| −37 to −36.5 | 0.0078 | 3.5% | 0.0056 |
| −36.5 to −34.5 *(shoulder)* | 0.0085 | **3.8%** | 0.0016 |
| −34.5 to −32 | 0.0011 | 0.5% | 0.0004 |
| −32 to −25 | 0.0016 | 0.7% | 0.0007 |
| **total** | **0.2259** | | **0.0909** |

**91% of the replicate disagreement sits between −40 and −37 — the main peak. The shoulder carries
3.8%.** This overturns a belief carried in the project notes that the residual disagreement sits in
the northern tail; that was true of earlier narrow-Mach fuel runs and is not true here.

## The mechanism: mode-mixture instability

Posterior mode probability across the eight replicates:

| mode | weight | relative spread | particles | draws per million |
|---|---|---|---|---|
| true track | 0.581 | 33.2% | 1.4M | 706 |
| lateral navigation | 0.253 | **53.6%** | 1.4M | 684 |
| true heading | 0.105 | 40.0% | 1.4M | 927 |
| magnetic track | 0.049 | 30.5% | 1.4M | 583 |
| magnetic heading | 0.012 | 33.9% | 1.4M | 789 |

True track ranges 0.481–0.674 across replicates and lateral navigation 0.189–0.325. These two hold
**83% of the posterior mass** and are trading roughly twenty percentage points of it between
themselves from one replicate to the next. They have different geometries, so that trade moves the
peak between −38.5 and −37 — precisely the band carrying 60% of the disagreement.

The converging fuel-free run is tighter on exactly these: true track 21.3%, lateral navigation
36.2%, with 2.5M particles in each and 925 draws per million in true track against 706 here. In
absolute independent roots that is **about 2,310 against 990 — 2.3× fewer in the mode that sets
the peak.**

## What follows, and a correction

The equal 1,400,000-per-mode allocation was chosen deliberately, and its stated justification in
`best-model.toml` was that the earlier unequal split "starves exactly the part of the posterior
under examination" — meaning the magnetic modes and the shoulder. **The band decomposition says
that reasoning was wrong.** The shoulder carries 3.8% of the disagreement. What the equal split
actually did was take true track and lateral navigation from 2.5M down to 1.4M in order to give the
magnetic modes 1.4M each, starving the two modes that set the peak.

`config/sensitivity/6temper-realloc.toml` is the direct test: the same six-tempered fuel model with
the allocation that converges on the fuel-free problem — 1.0M/0.5M/2.5M/0.5M/2.5M, total held at 7M
so every comparison stays valid. One variable changed.

If that is right, convergence here was never a sampler-sophistication problem. It was a
stratification problem, and three sampler interventions were spent on the wrong thing.
