# Ocean-drift family surface

Paper: Ulich et al. (2023), bundled at `paper/paper.pdf`.
The PDF SHA-256 is
`f17ffcf4a5ee27e645720abb2b4835113cd7c99986490df0487357b2578030c1`.

The bundle preserves the compact 25 by 9 cross-arc source grid and separate
HYCOM- and GDP-conditional likelihood surfaces. `code/geodesy.py` and
`code/surface_core.py` contain the independent geodesy and surface arithmetic.
The canonical product loader is `crates/ocean-drift`; it never averages model
families silently and never extrapolates beyond calculated support.

## Current status

Not integrated as a likelihood. The ordinary production surface exists, but
the historical rare-event replacement and isotope refinement did not finish.
The audit therefore records
`diagnostic_only_not_admitted_as_likelihood`; the product has no switch that
can admit this unfinished surface as a posterior likelihood.

The surface is retained because it is useful conditional context and because
future work can complete or replace it without modifying the flight engine.
It is not a crash posterior: combining it requires an independently justified
flight prior, current-family prior, common cell measure, and completed
Monte-Carlo uncertainty assessment.

The unfinished legacy rare-event cycle was stopped on 2026-08-25 after 18 of
42 replacement cells completed. Its raw partial results and logs remain in the
external archive as diagnostic evidence. No runtime code, incomplete isotope
surface, admission machinery, or sequential analysis naming was migrated into
the canonical product.

The large raw HYCOM, GDP, weather, coast, and isotope collections are not kept
in the lean repository. Their original workspace is preserved in the external
legacy archive recorded by the repository README.
