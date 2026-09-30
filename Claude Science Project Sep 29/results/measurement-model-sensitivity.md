# Sensitivity of the posterior to the BTO and BFO error model

The base filter takes its measurement standard deviations per epoch from
`data/satcom-observations.csv`: BTO 29 µs at seven epochs, 43 µs at two, 63 µs
at one, and BFO 7 Hz at all eleven epochs that carry a BFO. The 7 Hz figure is
Davey's own a priori value (Assumption 2, p. 73); the per-epoch BTO figures
follow Davey's scheme of assigning σ by message type rather than a single
constant.

Davey's Assumption 2 explicitly names BTO variance inflation as a modelling
choice that was made and not tested, and Figures 5.2 and 5.3 record the R-channel
delay `T_channel` as non-stationary — a residual mean of 10 µs and drift over
several days. So the error model is a declared assumption with a declared
weakness, and it had never been varied in this engine. Three variants were run.

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
2. **4 Hz assumes no transient bias.** It is the scatter measured from the data
   on the assumption that the BFO bias is constant over the flight. The engine
   marginalises a constant BFO bias, so that assumption is partly built in — but
   any drift in the bias would appear as scatter, and attributing all of it to
   measurement noise then makes the 4 Hz figure too tight. The run should be read
   as the lower end of a plausible range, not as a better-calibrated value.
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

So the per-epoch table is a channel-type table, which is what Davey specifies —
62 µs for R600 against 29 µs for R1200, with the log-on acknowledges treated as a
separate class because their BTOs are known to be anomalous. The only fidelity
gap is 63 against the book's 62 µs, already recorded in the parameter table.
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
