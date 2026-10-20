# Sensitivity of the posterior to the BTO and BFO error model

The base filter takes its measurement standard deviations per epoch from
`data/satcom-observations.csv`: BTO 29 µs at seven epochs, 43 µs at two, 63 µs
at one, and BFO 7 Hz at all eleven epochs that carry a BFO. The 7 Hz figure is
Davey's own a priori value (Assumption 2, p. 60); the per-epoch BTO figures
follow Davey's scheme of assigning σ by message type rather than a single
constant.

Davey's Assumption 2 explicitly names BTO variance inflation as a modelling
choice that was made and not tested, and Figures 5.2 and 5.3 record the R-channel
delay `T_channel` as non-stationary — a residual mean of 10 µs and drift over
several days. So the error model is a declared assumption with a declared
weakness, and it had never been varied in this engine. Three variants were run.

## The 7 Hz figure is already an inflation, by the book's own account

This turned out to matter more than expected, so it is worth stating before the
results. The BTO values are empirical and stated as such (p. 27): "For the R1200
messages, the empirically derived standard deviation of the measurement noise
wBTO_k is 29µs, and for R600 messages, 62 µs. For anomalous R1200 messages a
standard deviation of 43µs was used." The three classes in the observations file
are exactly these.

The BFO figure is different. Table 5.1 (p. 31) gives the measured statistics from
the 20 flights of 9M-MRO before the accident flight:

| sample | mean error (Hz) | sd (Hz) | mean, outliers excl. | sd, outliers excl. |
|---|---|---|---|---|
| including tarmac | 0.2246 | 4.9592 | 0.2745 | **4.0192** |
| in-flight only | 0.1079 | 5.4840 | 0.1755 | **4.3177** |

The book then states the choice in the next sentence: "to be conservative and
allow for potential variation in the δf_bias value on the accident flight, our
model assumes a noise standard deviation of 7 Hz."

So 7 Hz is not a measurement. It is the 4.32 Hz in-flight figure inflated by a
factor of 1.62 to cover uncertainty in the BFO bias. The `bfo-4hz` run is
therefore not an arbitrary tightening — it is the book's own empirical value,
run without the inflation.

That framing raises a question about the inflation itself. The engine, following
the book, already treats the BFO bias as an unknown constant per trajectory with
a 25 Hz prior standard deviation and marginalises it in closed form through the
Rao-Blackwellised step (p. 30). Bias uncertainty is thus accounted for twice:
once properly, in the marginalisation, and again in the σ inflation. Whether
that double-count is material is exactly what `bfo-4hz` measures, and the answer
below is that it is.

Two things the book's own analysis says that qualify this. The histogram of
3,392 in-flight BFO errors (Fig. 5.5) "shows some non-Gaussian features and the
tails of the distribution for negative errors are somewhat heavier than those for
positive errors" — so a Gaussian at the empirical sd understates the tails, which
is part of what the inflation buys. And the 4.32 Hz figure excludes outliers and
excludes climbing and descending data points, so it is the sd of level cruise
with outliers removed, not of the whole record.

## Runs

| run | change from base | replicates |
|---|---|---|
| `davey2016` | none (BTO 29/43/63 µs, BFO 7 Hz) | 8 |
| `bfo-4hz` | BFO σ 7 → 4 Hz at all eleven epochs | 4 |
| `bto-2x` | every BTO σ doubled (29/43/63 → 58/86/126 µs) | 4 |
| `bto-29us` | every BTO σ collapsed to the single R1200 value, 29 µs | 4 |

Only the observations file changes; the dynamics, priors, particle allocation
and seeds are identical. All three variants passed the convergence gate.

## Results

| run | median °S | 95% interval | mode °S | P(shoulder) | overlap w/ Davey Fig 10.3 | split-half | median spread across replicates |
|---|---|---|---|---|---|---|---|
| `bto-29us` | −38.066 | −39.592 … −35.903 | −38.100 | 0.0363 | 0.728 | 0.907 | 0.204° |
| base | −38.160 | −39.533 … −35.880 | −38.350 | **0.0368** | 0.717 | 0.934 | 0.312° |
| `bto-2x` | −37.766 | −39.402 … −35.286 | −37.600 | **0.0640** | **0.776** | 0.941 | 0.049° |
| `bfo-4hz` | −37.488 | −38.904 … −34.476 | −37.450 | **0.1182** | **0.742** | 0.936 | 0.142° |

Two findings, in order of importance.

**The channel-type refinement of the BTO σ is immaterial.** Collapsing all three
classes to the single a priori R1200 value moves the shoulder from 0.0368 to
0.0363 and the median by 0.09°, both inside the replicate spread. The per-epoch
table and a single a priori σ are interchangeable at this resolution — so the
answer to whether per-epoch σ is *necessary* is no, not for the posterior, only
for fidelity to how the book states the model.

**The overall scale of the measurement σ is not immaterial.** Doubling BTO
raises the shoulder 1.7× and tightening BFO from 7 to 4 Hz raises it 3.2×. Both
move the posterior north, and — the part that matters — **both improve agreement
with Davey's published latitude PDF.** `bto-2x` gives the closest agreement any
run has produced, 0.776 against the base 0.717, while also being the most stable
run in the set: its replicate medians span 0.049°, a sixth of the base spread.

The shoulder mass is therefore not a fixed property of this dataset. It moves by
a factor of three under a change to one declared σ, with convergence *improving*
rather than degrading.

## Mechanism

The shift is a reweighting of the autopilot mode mixture, not a change within
modes. Measured mode posteriors:

| run | TH | MH | TT | MT | LNAV |
|---|---|---|---|---|---|
| base | 0.0593 | 0.0032 | 0.5427 | 0.0146 | 0.3802 |
| `bfo-4hz` | 0.0609 | **0.0157** | 0.5536 | **0.0542** | 0.3156 |
| `bto-2x` | 0.0750 | 0.0069 | 0.6043 | 0.0200 | 0.2938 |

The two magnetic modes carry the shoulder — P(shoulder | mode) is 0.522 for MH
and 0.547 for MT, against 0.010 and 0.016 for TT and LNAV. Under `bfo-4hz` the
MH weight rises 4.9× and MT 3.7×, and that alone accounts for the shoulder
increase.

The direction is initially counter-intuitive: *tightening* the BFO σ admits more
of the magnetic-mode paths. The explanation is that BFO is the measurement that
discriminates between modes at all — BTO constrains range from the satellite and
is nearly mode-blind. At 7 Hz the BFO likelihood is flat enough across candidate
tracks that the mode mixture is decided mostly by BTO fit, which favours the
great-circle-like TT and LNAV paths. At 4 Hz the BFO starts to discriminate, and
it does not prefer them as strongly as the 7 Hz model implied. A conservative
error bar is not a neutral choice: it transfers the mode decision to the other
measurement.

`bto-2x` works the other way — loosening BTO removes the penalty that was
selecting against paths which do not intersect the arcs cleanly, which are
disproportionately the curving magnetic-mode paths.

## Caveats

1. **Log evidence is not comparable across these runs.** Changing σ changes the
   likelihood's normalising constant, so the reported values (−96.26 base,
   −95.45 `bfo-4hz`, −99.38 `bto-2x`) cannot be read as model comparison. They
   are only comparable within a fixed observation model — which is how the
   declination and weather sensitivities used them.
2. **4 Hz is the book's level-cruise, outliers-excluded figure.** Table 5.1's
   4.3177 Hz excludes climbing and descending points and excludes outliers, and
   Fig. 5.5 records heavier negative tails than a Gaussian. So 4 Hz is defensible
   as the noise of level cruise and *not* defensible as the noise of the whole
   record, including the descent that may have been in progress at 00:11 and
   00:19. Read `bfo-4hz` as the un-inflated end of a range whose other end is the
   book's 7 Hz, with the true figure epoch-dependent in a way neither run
   captures. This is one more reason to get vertical rate into the BFO model: the
   inflation is partly standing in for a state variable that is missing.
3. **`bto-2x` is a bracket, not a calibration.** Doubling every σ is a way of
   asking how much of the result rests on BTO confidence. It is not a claim that
   the true σ is twice the nominal. A *drifting* BTO offset — the thing Figures
   5.2/5.3 actually record — is a different model again, and remains untested; a
   constant offset was already eliminated by the ephemeris test.
4. Only the 00:11 and 00:19 epochs are near the end of flight, and the tightest
   ESS in every run is at m1941, so none of this is driven by the terminal
   epochs.

## Is per-epoch σ necessary?

It is Davey's own scheme, not a departure from it. The observations file carries
the channel type for every epoch, and the three σ values map onto three message
classes exactly as the book assigns them:

| σ | epochs | channel class (from `note`) |
|---|---|---|
| 29 µs | m1828a, m1828b, m1941, m2041, m2141, m2241, m0011 | R1200 |
| 43 µs | m1825, m0019b | anomalous R1200 log-on acknowledge |
| 63 µs | m0019a | R600 log-on request |
| — | m1839, m2315 | C-channel, BTO not used (means of 51 and 29) |

So the per-epoch table is a channel-type table, matching the book's p. 27
sentence class for class: 29 µs for R1200, 62 µs for R600, 43 µs for anomalous
R1200. The only fidelity gap is 63 against the book's 62 µs, already recorded in
the parameter table.
What this engine does differently is read the value from the observations file
instead of hardcoding the channel table, which is why the parameter table shows
these rows as derived `from_observations` rather than as declared constants —
presentational, not substantive.

`bto-29us` collapses all three classes to the single R1200 value and brackets
`bto-2x` from the opposite side. It changes nothing measurable: shoulder 0.0363
against 0.0368, median −38.066 against −38.160, overlap 0.728 against 0.717. So
the per-epoch table can be reported as a fidelity choice rather than defended as
a modelling requirement, and a reader who prefers Davey's stated single a priori
value gets the same answer.

Two qualifications. `bto-29us` *tightens* the two epochs the data flags as
anomalous, which is the one thing the channel notes advise against — it is a
bracket, not a candidate model. And its split-half overlap is 0.907, the lowest
of the set and only just above the 0.90 floor, consistent with a tighter
likelihood concentrating weight on fewer prior draws.

## Implication for the shoulder

Three candidate causes of the shoulder shortfall have now been tested. The
declination generation was eliminated — IGRF-11, the grid NOAA actually served
in 2014, gives a shoulder of 0.0369 against 0.0368. Weather source moves it
trivially (0.0360 under FNL). The measurement error model moves it by a factor
of three.

That reorders the list. The BTO/BFO error model is now the largest identified
lever on the shoulder outside the sampler itself, and unlike the sampler it is a
declared assumption of the published method rather than a reimplementation
difference. The remaining untested candidates — the branching resampler, and the
particle allocation that starves MH and MT — both act on the same mode mixture
this sensitivity has just shown to be the operative quantity.
