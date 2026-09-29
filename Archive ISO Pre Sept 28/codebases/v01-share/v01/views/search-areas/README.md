# Seabed-search evidence context

This directory contains a posterior-independent atlas of reported and mapped
search evidence. It is context for interpreting candidate geography, not an
input to the v0.1 broad-flight filter.

- [Evidence atlas PDF](evidence-atlas.pdf)
- [PNG](evidence-atlas.png)
- [SVG](evidence-atlas.svg)
- [Combined map geometry](search-evidence-atlas.geojson)
- [Official-source FL400 seventh arc](seventh-arc-fl400.geojson)
- [Area inventory](area-inventory.json)
- [Evidence register](evidence-register.json)
- [Readiness record](readiness.json)
- [Located-passage citation ledger](citations.json)
- [Source lock](sources.lock.json)
- [Complete source package and build instructions](../../workspace/.sources/mh370-seabed-search-coverage/README.md)

## Interpretation

The package distinguishes official data footprints, reported aggregate areas,
display polygons, and approximate contextual outlines. These layers are not
interchangeable. No available polygon is treated as a calibrated
searched/not-searched mask, and the broad posterior is not multiplied by a
negative-search likelihood.

Detailed sonar quality, holidays, navigation overlap, target state, and a
calibrated probability-of-detection model remain unavailable. Exact Ocean
Infinity AUV swaths were not obtained; approximate outlines and surface-vessel
tracks are visibly contextual. Consult `evidence-register.json` and
`readiness.json` before using any geometry.

The `seventh-arc-fl400.geojson` is an official-source contextual geometry used
by the atlas. It was not calculated by the broad run and is not a most-likely
flight track or impact curve.

## Why planning tiles are absent

The earlier baseline planning PDF, PNG, SVG, and selected-tile GeoJSON were
computed from an impact population downstream of the superseded narrow
one-turn/frozen-continuation analysis. Publishing those tiles beside the broad
diagnostic would imply unsupported continuity between the two models.

They are intentionally excluded from this curated view and the current result
manifest; a complete source-recreation directory may retain them only as
historical output. No replacement search ranking is released because the
corrected broad population has not been propagated through a provenance-valid
terminal/impact model, and because numerical support and search-detection
calibration must be assessed separately.

## Rebuilding the atlas

From `v01/workspace`, after creating the documented Python environment:

```bash
.venv/bin/python -B \
  .sources/mh370-seabed-search-coverage/code/build.py build
.venv/bin/python -B \
  .sources/mh370-seabed-search-coverage/code/build.py check
```

The source package records retrieval identities, licences, geometries, stable
output hashes, and explicit unavailable-data fields. Rebuilding the atlas does
not alter either flight's posterior.
