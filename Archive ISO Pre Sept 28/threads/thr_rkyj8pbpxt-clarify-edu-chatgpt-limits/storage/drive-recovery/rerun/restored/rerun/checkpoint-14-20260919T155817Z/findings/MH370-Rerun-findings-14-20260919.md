# MH370 Rerun checkpoint 14 findings

Created: 2026-09-19T15:58:17Z

## Outcome

The source boundary introduced at checkpoint 13 is no longer merely an uncompiled design. It compiles with the project's exact Rust version, its relevant unit and contract tests pass, and the retained-parent transition-pool path runs through the physical aircraft estimator.

Two runner compile defects were found and repaired only in an isolated candidate:

1. diagnostics accessed `initial.flight` even though the typed wrapper is `initial.state.flight`;
2. the retained-parent closure's result needed an explicit `Result<SampledFlight, SmcError>` annotation.

These were compile integration defects, not changes to the probability law.

## Verification

- exact compiler: `rustc 1.98.0 (88d9e12ae 2026-08-18)`;
- release runner built successfully;
- 87 `mh370-end-of-flight` tests passed;
- 63 `mh370-estimator` tests passed;
- 74 `mh370-particle-filter` tests passed;
- 7 bridge-boundary Python contract tests passed;
- no active MH370 sampler process or live lease was present before the independent runs;
- hydroacoustic code and evidence were not invoked.

`cargo fmt --check` remains red because the recovered baseline contains broad pre-existing formatting drift across several crates. The candidate was not mass-formatted, because doing so would obscure the two-line semantic integration repair. The full workspace test command also still depends on a missing `inputs/controls/forward-model-golden.json` fixture; this checkpoint therefore reports focused relevant tests, not a full clean workspace suite.

## Physical K=1 identity control

Both runs used seed `37091713`, four threads, 20 roots per each of five modes (100 roots total), the exact same observation and environment inputs, and no trajectory-example output.

The baseline and retained-parent configuration with `K=1` agreed on:

- `filter-checkpoints.json` — byte-identical;
- `initial-allocation.json` — byte-identical;
- `observation-blocks.json` — byte-identical;
- `posterior.csv` — byte-identical;
- `sequential-filter-config.json` — byte-identical;
- log evidence — exactly `-90.65806819602719` in both;
- posterior SHA-256 — exactly `23cb6dfc63f06f22473078f6ff0e35b77bdc199ebf8c359843b4304f45eee210` in both.

`particles.json` differed only in `elapsed_seconds`. Provenance and resolved configuration differed because one run truthfully declares the `K=1` retained-parent proposal. This is the intended result: the new sampler path is scientifically inert at `K=1`.

## Physical K=4 engineering control

The same bounded seed/configuration was rerun with four candidates per retained parent at the 18:39/19:41 observation block.

- parents entering the pool: 100;
- generated candidates: 400;
- positive candidates: 400;
- distinct positive candidate roots: 41;
- candidate ESS: `3.5743479915629397`;
- candidate-root ESS: `3.3664117923976282`;
- maximum candidate weight: `0.5212716308841339`;
- maximum candidate-root weight: `0.5328299841664093`;
- candidate log-evidence increment: `-19.23673757667722`;
- realized log-evidence increment: `-19.23673757667722`;
- output-resampling log correction: `0.0`.

All five initial-mode strata generated 80/80 positive candidates. Their output stratum masses matched candidate posterior masses to floating-point precision, so the pool preserved the intended stratum mixture at this boundary.

After the complete run, the 100-row posterior had row ESS `4.90972361119828`, root ESS `2.0374476645082069`, and maximum root weight `0.5516489977494877`. The comparable `K=1` control had row ESS `4.10459081313186`, root ESS `1.5591758069571178`, and maximum root weight `0.7853935553721276`.

This directional improvement is encouraging but not inferential evidence. It comes from one small seed and four times as many block proposals. The `K=4` and `K=1` log evidences (`-89.42827` and `-90.65807`) cannot be interpreted as a Bayes factor or estimator preference from this experiment.

## Implication for the 96–98% ancestry question

This control supports the proposal-coverage component of the existing diagnosis. At the critical observation block, the prior predictive transition produces broad physical support—400/400 candidates were positive—but the likelihood/proposal-weight distribution is extremely concentrated (candidate ESS only 3.57). That is not the signature of a hard dynamical impossibility eliminating nearly everything. It is the signature of a narrow high-weight region being poorly covered by ordinary forward proposals. Subsequent resampling can then turn that weight concentration into genealogical dominance.

The control does not show that the early path is unconstrained. The observations are genuinely selective, and the final interpretation remains a three-part mechanism: real information, insufficient proposal overlap, then resampling amplification.

## Boundary/bridge status

The exact bridge-boundary source from checkpoint 13 is unchanged (SHA-256 `dc7712c0c6ef0918a5be8056a21cdab7f40eb81bb0c5be4ae570eb390724bd78`). It retains:

- endpoint prior/proposal mixture correction;
- path prior/proposal correction;
- fuel and exhaustion-time prior/proposal corrections;
- the fuel/time Jacobian;
- explicit observation-factor ownership;
- fail-closed duplicate observation handling;
- fail-closed exclusion of 00:19 from proposals when 00:19 is to be scored later.

The present physical run exercises the retained-parent proposal pool, not yet the backward fuel-exhaustion bridge itself. The next adoption gate is multi-seed, matched-budget validation followed by integration of that exact boundary into aircraft propagation.

## Claims explicitly not made

- no calibrated posterior location probability;
- no solved crash location;
- no claim that `K=4` is converged or unbiased from this one run;
- no use of a uniformly selected endpoint as an observed location;
- no double conditioning on SATCOM or fuel evidence;
- no hydroacoustic inference.
