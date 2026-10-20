# Davey et al. reference

- [Source paper: *Bayesian Methods in the Search for MH370*](davey-2016-bayesian-search-paper.pdf)
- [Complete local recreation package](../../../workspace/.sources/davey-2016-bayesian-search/README.md)
- [Citation ledger](../../../workspace/.sources/davey-2016-bayesian-search/citation-ledger.md)
- [Source ambiguities](../../../workspace/.sources/davey-2016-bayesian-search/data/source-ambiguities.md)

The bundled paper's SHA-256 is
`37554ca5f0c0ef14fddb825748d9f9dc9059a26563f783a3e4dfafcd0ced91b2`.
The source package preserves the independent paper-as-code reconstruction,
frozen inputs, digitized latitude marginal, outputs, and limitations.

Davey et al. is reference context, not a measurement imported into the current
posterior. The current broad runner implements its own explicit equations and
declared structural support. Where public inputs cannot recover proprietary
corrections or maneuver-history choices, the source package says so.

## Why no canonical comparison is shown

The previous `canonical-vs-davey-latitude` PDF/PNG/SVG compared Davey's
published latitude curve with an earlier canonical chain that assumed one turn
and then a frozen continuation. That comparison is historically informative
but is not a comparison with the corrected broad repeated-event model. It is
therefore excluded from this curated view and the current result manifest
rather than relabelled. The complete source-recreation package can retain it
only as explicitly historical output.

A future comparison must be regenerated directly from a provenance-valid broad
artifact, preserve evidence-family separation, and retain any failed numerical
support watermark. Until then, use the paper and source reconstruction as
methodological context only.
