# Antenna gain blocked-prediction results

## Primary blocked prediction

The primary analysis used a Gaussian channel-random/continuous-time OU model,
held out each complete time event, and purged observations within 30 minutes.
It retained 16 paired held-out events. Positive
log-density differences favor no gain precompensation.

- Mean event log-density difference per point:
  +0.1161.
- Paired bootstrap 95% interval:
  [-0.1936,
  +0.4616].
- Enumerated two-sided paired-event sign-flip p:
  0.5364.
- Point RMSE: no precompensation
  1.717 dB; full precompensation
  1.875 dB.
- Point MAE: no precompensation
  1.276 dB; full precompensation
  1.517 dB.

## Temporal-boundary and forward diagnostics

The fitted OU timescale reached its 0.05-hour lower bound in most folds. In
the corresponding independent-event limit, the mean log-density difference
was +0.0116, with bootstrap
interval [-0.2576,
+0.2695] and paired sign-flip
p=0.9308. Its point RMSE was
1.732 dB under no gain precompensation and
1.833 dB under full gain precompensation.

Forward-only prediction reversed direction: the mean log-density difference
was -0.4651, with bootstrap
interval [-1.1268,
+0.0652]. These model-dependent sign
changes do not support a stable preference between the endpoint hypotheses.

The bootstrap and sign-flip values are dependence-sensitive diagnostics:
leave-event-out training sets overlap, and event exchangeability cannot be
verified from sixteen events.

## Continuous beta

The full-sample hierarchical estimate was beta =
1.118, with conditional standard error
0.296 and an event-t
approximation [0.488,
1.749]. Beta=0 denotes full gain
precompensation and beta=1 denotes no gain precompensation.
Only 2 of 16 events contain more than 0.05 dB of within-event modeled gain
variation, so this interval is driven mainly by between-event comparisons. It
is conditional on the random-effects independence assumption and is not a
blocked or causal interval.

## Interpretation boundary

These are model-conditional predictions. The channel and temporal random
effects represent, but do not identify, propagation, receiver, satellite, HPA
or other persistent physical effects. Failure to distinguish the endpoints is
not proof that their mechanisms are equivalent.

The gain observable therefore remains excluded from unconditional core use
under the tested physical model and available control sample.

## Conditional MH371 medium-BFO control

The canonical runner evaluates both endpoint conditions separately with
12,000 particles and deterministic seeds 37102001 and 37102002. The gain
surface is oriented with the particle's airframe true heading (magnetic heading
plus IGRF-14 declination), not ground track.

The full-precompensation endpoint is posterior-identical to the medium-BFO
baseline, as required: its event likelihood is constant across particles.
Under the no-precompensation endpoint:

- average terminal mean error changes from 26.36 to 20.13 NM;
- average terminal mass within 100 NM changes from 0.6041 to 0.6208;
- worst-seed terminal mass within 100 NM changes from 0.5724 to 0.5990;
- mean position error improves on four of six reported arcs;
- worst-seed terminal truth HPD mass changes from 0.7822 to 0.7898;
- minimum pairwise overlap changes from 0.6933 to 0.6963;
- maximum pairwise Jensen-Shannon divergence changes from 0.07825 to 0.08356 nats.

The no-precompensation log evidence is about 2.45 units higher than the
full-precompensation endpoint for each seed within this conditional model.

Because terminal HPD calibration is slightly worse and the active-envelope
surface lacks verified antenna handoff behaviour, this is promising
conditional evidence rather than a core-admission result.

The post-score truth geometry audit in `mh371_surface_truth_audit.csv` finds a
1.740 dB grid-versus-workbook departure mismatch at the first arc; the maximum
absolute mismatch across the other five arcs is 0.335 dB. Held-back truth was
used only for this audit after inference and scoring.
