# Rerun checkpoint 3 — physical bottleneck exporter prepared, validation environment lost

19 September 2026. This is a candidate implementation checkpoint, not a new
MH370 posterior.

## Outcome

The isolated runner now has an opt-in diagnostic designed to answer the next
specific question: within the archived block that carries the 18:39:55 BFO-only
contact and the 19:41:02 BTO/BFO contact, how much realized weight concentration
appears at each chronological proposal and measurement update, and how much
initial-state diversity remains?

The exporter is deliberately replay-only. When requested, it retains the exact
block snapshots, reconstructs every child with the production bootstrap RNG
identity, and refuses output unless both the reconstructed state and normalized
child weight agree with the retained run. It records child, parent and root IDs;
stratum; input and child weights; proposal `log(p/q)`; total contact likelihood;
separate BTO, BFO and remaining factors; support; residuals; pre/post BFO-bias
state; and actual initial, parent and post-contact flight states. The associated
analyzer computes chronological row ESS, root ESS, maximum row/root mass,
positive root count, factor-only stress diagnostics and weighted initial-state
CDF shifts.

This resolves an instrumentation gap. It does **not** yet resolve the scientific
cause of the 96–98% synthetic ancestry concentration: no physical factor rows
were produced in this work unit.

## Validation completed

Ten independent Python tests pass:

- five boundary-transport tests, including the radar/18:28 fuel change of
  variables and broad endpoint proposal correction;
- exact enumeration of a two-contact, four-row, three-root factor bank;
- explicit rejection/support handling with negative-infinity weights;
- three packaged-source contracts pinning opt-in/backward-compatible behavior,
  the production RNG domain, the weight identity and a single CSV formatter.

The analyzer verifies both the finite-weight pattern and normalized log weights,
with a `3e-12` tolerance. The runner itself requires, per child,

`input log weight + block likelihood + proposal log(p/q) - block evidence increment = child log weight`

within `2e-12`, plus byte-equivalent serialized reconstructed state. This is a
strong proposed replay gate, but only compilation and a physical run can execute
it.

## Validation not completed

The shared prior workspace was pruned during this work unit. That removed its
authenticated Rust toolchain, exact environment files and heartbeat/lease
records. Neither `cargo` nor `rustc` is available in the current runtime. The
new runner integration therefore remains **uncompiled candidate source**.
Earlier checkpoint-2 Rust tests passed before this integration and cannot be
used as proof that it compiles.

The candidate verification helper now reports this distinction mechanically:
the Python/source checks pass, while the overall receipt remains false and exits
2 because both locked Rust commands are blocked. No sampler lane was acquired,
no sampler was launched, and no missing heartbeat was interpreted as permission
to reuse another thread's lane.

## Input recovery progress

The exact ERA5 object's Drive multipart folder and manifest were located. The
manifest identifies `mh370-era5-grid.bin` as 337,328,648 bytes with SHA256
`73a14bf7e931da9f4f3f034b77ac24b9514fdef727b82eb9e30c67df938489f4`.
Eleven part IDs are recorded in
`candidate-20260919T0334/environment-recovery-status.json`. The bytes have not
been locally reassembled or hash-verified because this runtime exposed no
verified connector-to-local multipart transfer path.

The exact 5,564,268-byte broad IGRF grid has not been located. A similarly named
WSPR-era magnetic grid is not a substitute. The Rust toolchain was also not
found in the saved artifacts. These are concrete physical-replay blockers, not
evidence that the estimator has failed.

## Scientific interpretation and next gate

Once compiled and run, the chronological table can distinguish several cases:

- a sharp loss of root ESS before the block means proposal/support coverage was
  already poor;
- loss at 18:39 BFO with broad row support implicates the conditional BFO/bias
  update rather than a BTO arc;
- loss mainly in proposal `p/q` exposes realized guided-proposal mismatch;
- diverse rows but one root after 19:41 demonstrates genealogical loss even if
  row ESS later recovers;
- many rejected rows or absent regions means reweighting cannot diagnose paths
  that were never proposed.

These are diagnostic patterns, not calibrated causal percentages. BTO, BFO and
proposal terms are correlated through the trajectory and shared bias state, so
factor-only removal is order-sensitive. The primary valid comparison remains
multiple fixed seeds and matched budgets, reporting actual initial-state
diversity, row/root ESS, support, evidence, marginal CDF differences and
synthetic coverage.

The immediate next steps are:

1. restore a compatible Rust toolchain and authenticate/reassemble ERA5 and the
   exact broad IGRF input;
2. compile the candidate and run the locked Rust suites;
3. prove tracing-disabled versus tracing-enabled scientific replay equality;
4. export the 18:39/19:41 factor rows for at least two archived seeds, analyze
   them, then design a support-preserving bridge based on the observed failure;
5. only after exact/synthetic recovery, compare the explicit 00:15–00:17
   exhaustion hypothesis with 00:15–00:19 using a correctly weighted terminal
   proposal and path-dependent fuel map.

No full-aircraft bridge has been run by Rerun, no replacement estimator is
validated, and hydroacoustic evidence remains excluded.
