# Copyright, licences, and redistribution boundaries

This capsule combines original estimator code and documentation, generated
run artifacts, published reference material, official public data, community
context layers, and files retained only by hash or retrieval instruction. No
single licence applies to the whole capsule. Inclusion for scientific
reproducibility does not erase upstream copyright or grant rights beyond the
terms attached to each component.

This document records the local rights evidence used for packaging; it is not
legal advice and does not replace an upstream licence or notice.

## Repository-produced code

The Rust workspace manifest at `workspace/Cargo.toml` declares SPDX licence
`MIT`, and the Rust crates inherit that workspace value. Copyright remains with
the respective contributors; this capsule does not invent a different owner or
transfer copyright.

The workspace also contains Python reporting and provenance tools,
documentation, generated figures, and normalized data. Where a file is not
covered by package metadata and carries no separate licence notice, do not
infer a new permission merely because it is present in the capsule. Preserve
file-level notices, source history, and attribution. This document does not
relicense third-party material under MIT.

The packaged executable is a compiled derivative of the Rust workspace and
its pinned dependencies. `workspace/Cargo.lock` identifies dependency
versions. Each third-party dependency remains under its own upstream terms;
preserve any licence and notice files shipped with a vendored dependency tree.
This document is not a substitute for a complete third-party-notices review
before redistribution in another product.

## Generated diagnostics and capsule documentation

The MH371 and MH370 diagnostic PDF, PNG, and JSON files are generated works
whose scientific provenance is recorded by their report audits. Their presence
does not grant permission to remove the failed-support watermark, detach them
from the configuration and report JSON, or represent them as endorsed location
products. Retain attribution to the project and the complete provenance chain
when sharing them.

No warranty is made as to scientific correctness, fitness for navigation,
search planning, safety, or any other operational purpose. Both reports fail
numerical support and are diagnostic only. They contain no releaseable MH370
coordinate, impact posterior, or search box.

## Davey et al. paper

The bundled book *Bayesian Methods in the Search for MH370* is
© Commonwealth of Australia 2016. Its copyright page states that the open
access book is distributed under the
[Creative Commons Attribution-NonCommercial 4.0 International licence](https://creativecommons.org/licenses/by-nc/4.0/).
Noncommercial reuse must credit the authors and source, link the licence, and
identify changes. Material credited separately may require permission from its
own rights holder.

The capsule carries the unchanged paper at
`views/reference/davey/davey-2016-bayesian-search-paper.pdf`. The local
paper-as-code recreation is a separate project artifact and does not alter the
book's licence. Davey material is methodological context; it is not imported as
a prior, likelihood, truth value, or current broad-model comparison.

## Search-evidence atlas and source data

The authoritative item-by-item rights record is
`workspace/.sources/mh370-seabed-search-coverage/provenance/sources.lock.json`.
Consult it before extracting or redistributing a layer.

Bundled Geoscience Australia/AusSeabed records are identified there as
© Commonwealth of Australia and licensed under
[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
where the individual record says so. Preserve the recorded publisher,
attribution, source URL, transformation note, and licence.

Approximate Ocean Infinity outlines and community AIS reconstructions are
source-graded contextual layers with attribution retained. Their source-lock
entries do not assert a general permissive licence, and this capsule grants no
broader rights. They must not be relabelled as official AUV swaths, valid-data
masks, or calibrated negative evidence.

Several ATSB, Malaysian government, Ocean Infinity, and other references are
intentionally link-and-hash only because their redistribution status, embedded
third-party material, or size did not justify bundling. Do not add those bytes
to a redistributed capsule without reviewing the recorded decision and current
upstream terms.

The atlas PDF, PNG, and SVG are contextual derivatives. Sharing a rendered
atlas does not convert any underlying layer to a new licence or make the atlas
an operational search plan.

## Scientific inputs and source packages

`workspace/inputs/` contains the normalized bytes consumed by the runner.
`workspace/.sources/` records upstream identities, transformations, licences,
citations, restrictions, and retrieval instructions. These directories contain
materials with different rights; neither is covered by a blanket capsule
licence.

In particular, some upstream MH371 workbooks are restricted and are not
redistributed. Their absence is intentional; the capsule preserves the exact
normalized runtime inputs and audit trail needed for this calculation. ERA5,
IGRF, SATCOM, fuel/performance, and other source materials remain subject to
the terms and attribution recorded in their respective source README and
manifest files.

When a source package says `not bundled`, provides only a hash/link, or records
an unresolved licence, do not acquire and republish the material on the
assumption that research use is equivalent to redistribution permission.

## Withdrawn historical package

The earlier one-turn package labelled v0.1 has been withdrawn scientifically.
That withdrawal does not change ownership or licensing of its contents, but it
does prohibit treating its narrow location, impact, Davey-comparison, or search
planning products as current project results. Historical source outputs may be
retained for audit only with clear superseded labels.

## Trademarks and names

Airline, aircraft, satellite, government, publisher, and organization names
are used descriptively. Their inclusion does not imply sponsorship,
endorsement, or waiver of trademark or other rights.

