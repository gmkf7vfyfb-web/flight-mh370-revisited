# MH370 Engineering Contract

This repository has one product: a fast, reproducible Bayesian estimator for
the final flight of MH370, with publication-quality reports. Keep it small
enough that an engineer can understand the complete inference path.

## Canonical code only

- There is one current implementation. Improve it in place; do not create
  sequentially numbered copies, derivation folders, or parallel "final"
  versions.
- Names describe scientific or software purpose. Do not use identifiers such
  as `D-####`, `C-####`, gates, stages, or scorecard terminology.
- Code belongs in the product only when it is used by the central runner or is
  a focused control needed to trust that runner.
- Develop uncertain alternatives on a branch or in a temporary worktree. If an
  alternative is accepted, integrate it cleanly and remove the superseded
  implementation. If it is rejected, remove its code and record a short
  `Not integrated:` explanation in the relevant source README or the root
  README. Do not preserve a dead implementation merely as history; Git is the
  history.

## Hub-and-spoke architecture

The command-line runner is the hub. It owns configuration, deterministic run
setup, module selection, inference orchestration, and output generation. It
must remain lean and must not contain scientific equations that belong to a
module.

Scientific capabilities are spokes with narrow interfaces. Expected spokes
include flight dynamics, SATCOM observations, end-of-flight behaviour, ocean
drift, hydroacoustics, antenna gain, and reporting.

- A spoke owns its equations, parameters, input validation, and focused tests.
- A spoke accepts typed inputs and returns likelihoods, state transitions, or
  report data. It does not reach into another spoke's files or global state.
- Spokes may depend on shared units, coordinates, time, particle, and
  uncertainty types. They do not depend on one another. The runner composes
  them.
- Optional evidence is selected explicitly in run configuration. A result must
  state which spokes were enabled; absence of a spoke must not silently imply a
  neutral scientific conclusion.
- Each spoke must be runnable against a small fixture or benchmark without
  running the complete estimator.

The intended dependency direction is:

```text
runner -> particle filter + selected scientific spokes -> shared domain types
runner -> reporting
scientific spokes -X-> other scientific spokes
product crates -X-> .sources/
```

## Published work and `.sources/`

Published papers are inputs to investigation, not automatically correct
implementations. Keep paper recreation outside the product workspace at:

```text
.sources/<descriptive-paper-name>/
  README.md       # citation, claim recreated, commands, result, and limitations
  paper.pdf       # the exact paper version, when redistribution is permitted
  code/           # independent paper-as-code recreation
  data/           # the exact relevant datasets or retrieval instructions
  outputs/        # recreated figures and numeric comparisons
```

- Use descriptive directory names, never sequential identifiers.
- Record the paper and dataset versions or hashes and all required units,
  coordinate frames, time standards, and assumptions in the local README.
- Recreate the result independently where possible. State plainly when it
  agrees, disagrees, or cannot be recreated and why.
- `.sources/` is not a Cargo workspace member, runtime dependency, or part of
  the central test suite. Its code nevertheless follows the same standards for
  determinism, numerical correctness, readable implementation, and
  reproducible commands as product code.
- Never import paper recreation code into the runner. If a method proves useful,
  implement the smallest justified form as a canonical spoke and validate it
  there. Keep the source recreation only as supporting material.
- Large or restricted datasets may live in external storage, but the README
  must provide an exact retrieval method and integrity hash.

## Confidence without bloat

Testing exists to catch scientifically or operationally meaningful failures,
not to maximize test count.

- Prefer a small set of strong checks: dimensional and coordinate invariants,
  independently calculated fixtures, limiting cases, known-flight or synthetic
  recovery, and one end-to-end deterministic run.
- Every stochastic run records its seed, configuration, input identities, code
  revision, runtime, and convergence information.
- New scientific code includes a rough independent calculation or reference
  fixture so that a shared implementation error cannot validate itself.
- Measure wall-clock and memory use. A module that makes normal iteration slow
  must be profiled and simplified before integration.
- Keep normal module checks quick. Put expensive sensitivity sweeps and large
  production runs behind explicit commands, never the default test command.
- Delete generated runs, caches, copied environments, and obsolete outputs from
  the repository. They must be reproducible from code, inputs, and configuration.

## Scientific and reporting standard

- Separate measured inputs, model choices, and calculated outputs in code and
  prose. Do not present a paper's conclusion as a measurement.
- Carry units, reference frames, sign conventions, time basis, uncertainty, and
  correlations explicitly wherever they can affect the estimate.
- Do not combine incompatible model families as though their spread were random
  sampling error. Run and report them as explicit alternatives.
- Failed independent recreation is useful evidence. It cannot become a runner
  assumption unless the uncertainty is explicitly modelled and the user can
  enable it conditionally.
- Reports and plots are generated from run artifacts, never hand-edited. PDFs
  must be publication quality: legible at print size, consistent typography,
  labelled units, explained uncertainty, vector graphics where practical, and
  captions that state configuration and evidence conditions.
- A report must make the estimate reproducible from one documented command.

## Change rule

Before adding a directory, dependency, abstraction, or test, ask whether it
makes the central estimate more correct, faster to iterate, easier to inspect,
or clearer to reproduce. If it does none of those things, do not add it.
