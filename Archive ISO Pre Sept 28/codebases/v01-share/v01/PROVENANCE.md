# Provenance and frozen artifact identities

This document records the final pre-packaging audit of the corrected v0.1
broad-flight artifacts. SHA-256 values are hashes of exact file bytes. Sizes,
PDF page counts, and PNG dimensions were independently recomputed on
2026-09-06 UTC from the native repository artifacts before copying them into
the capsule views.

The final capsule-wide `SHA256SUMS` ledger is the authority for packaged path
membership. The table below records the important scientific and contextual
identities so a reader can check the chain without mistaking a filename for
provenance.

## Provenance chain

```text
runner TOML + exact producer binary + frozen scientific inputs
        |
        v
run-manifest.json -> all family/seed summaries and snapshot CSV hashes
        |
        v
report spec + reporter source + optional MH371 held-back truth
        |
        v
broad_snapshot_diagnostic.json -> PDF and PNG byte hashes
        |
        v
release-validation.json -> capsule-wide SHA256SUMS
```

Truth is optional only at the reporting edge. MH371 truth is absent from the
runner and hash-bound when opened by the reporter. MH370 is reported with no
truth file.

## Final audited identities

| Artifact | Capsule path | Bytes | Extent | SHA-256 |
| --- | --- | ---: | --- | --- |
| MH371 diagnostic PDF | `views/mh371/broad_snapshot_diagnostic.pdf` | 2,656,860 | 9 pages | `67d988de7a869344ba9f94ee07d933c9fbfecb29aa6c57f76dc4d3297b2c28c9` |
| MH371 all-epoch PNG | `views/mh371/broad_snapshot_diagnostic.png` | 1,966,018 | 1936 × 4752 px | `27a88d15e0b1349e14ab99d32279049d75f920299c939bc531876a6d43313bdc` |
| MH371 report audit | `workspace/runs/mh371/broad-flight-truth-control/diagnostic-report/broad_snapshot_diagnostic.json` | 2,240,786 | n/a | `ac40e904cefea023a10b562c7abe0d376e0c77d408f5f400eebd319cf71abbde` |
| MH371 release validation | `workspace/runs/mh371/broad-flight-truth-control/diagnostic-report/release-validation.json` | 11,870 | n/a | `56b36812aa6866d1633f76d46710ce0cd6d7f814ca0d0ea87e79d048984eda38` |
| MH370 diagnostic PDF | `views/mh370/broad_snapshot_diagnostic.pdf` | 4,225,120 | 14 pages | `c567a329bd1a988645982facd2921d086c9006630779b8aa8292bba7143f321e` |
| MH370 all-epoch PNG | `views/mh370/broad_snapshot_diagnostic.png` | 3,550,449 | 1936 × 8712 px | `8d78a06570689b9f66e4938ea331896afb0792a95ed540b1da6f3fc268f4e170` |
| MH370 report audit | `workspace/runs/mh370/broad-flight-uncertainty-diagnostic/diagnostic-report/broad_snapshot_diagnostic.json` | 3,818,887 | n/a | `fa7c3f27fb2ed46c60263677652f8e49ce428f44741d4582041cd77034441769` |
| MH370 release validation | `workspace/runs/mh370/broad-flight-uncertainty-diagnostic/diagnostic-report/release-validation.json` | 11,774 | n/a | `a800f3aa7a3b9ebf8a96050e744fb2519b71b38b3265f301e37cc70e022e4a90` |
| MH371 runner configuration | `workspace/configs/mh371-broad-powered-flight-control.toml` | 8,576 | n/a | `9b8bd2d0d61890eb50abfc2a5ebd5688f831fae39e56bc4fd31892823a4df06f` |
| MH371 report specification | `workspace/configs/mh371-broad-snapshot-report.json` | 5,446 | n/a | `5e92ad87bca44d203e8e31eda72d7b45af663d288ec3a45c49817b6a896cbb9c` |
| MH370 runner configuration | `workspace/configs/mh370-broad-powered-flight-diagnostic.toml` | 8,572 | n/a | `1d404bceb70d70825a770e3c80aa3638a4bd103e287b0898022ce2cfd4766a2e` |
| MH370 report specification | `workspace/configs/mh370-broad-snapshot-report.json` | 5,543 | n/a | `920fd37b57a545a0cd795eaadbbf533806bcf793d3a55a86cde7cb85d6cb00ea` |
| Broad snapshot reporter | `workspace/crates/reporting/scripts/broad_snapshot_report.py` | 70,532 | n/a | `166b7570b86b49f083c02bfa1326063bc30125fa85898e47a009f563b2d7eca2` |
| Broad release validator | `workspace/crates/reporting/scripts/validate_broad_release.py` | 69,954 | n/a | `dacab35d0715d0f3e62bdba6bf06c411120fd1853454674b2842ecf7cfe4d215` |
| Exact Linux x86-64 producer | `bin/linux-x86_64/mh370-v0.1` | 9,986,256 | n/a | `d20eb4bf68133592b9324e7f056962e198623eec309fc054fbd1c6172d6a7e7c` |
| Davey et al. paper | `views/reference/davey/davey-2016-bayesian-search-paper.pdf` | 6,898,866 | 124 pages | `37554ca5f0c0ef14fddb825748d9f9dc9059a26563f783a3e4dfafcd0ced91b2` |
| Search-evidence atlas PDF | `views/search-areas/evidence-atlas.pdf` | 69,936 | 1 page | `b8a24eae8f067936c25ee88706fdeeae5ae1811f968adc63aa73094d9e4ac9ec` |
| Search-evidence atlas PNG | `views/search-areas/evidence-atlas.png` | 606,394 | 3408 × 2064 px | `934af32f370e036add2378807ad0d82bb38cfa3719d99fb7944cf5c1986c3b3a` |
| Search-evidence atlas SVG | `views/search-areas/evidence-atlas.svg` | 257,372 | vector | `15e50db1054484cb05d01fad4f168d17d68f1134385e82a5e148b48e463682ba` |

There are no separate native files literally named `all-arcs`. For each
flight, `broad_snapshot_diagnostic.png` is the all-epoch visual overview and
`broad_snapshot_diagnostic.json` is the complete machine-readable all-epoch
audit. The PDF contains the corresponding per-epoch arc/support panels.

## Final status closure

| Flight | Validation schema | Validation status | Release eligible | Failed validator checks | Report schema | Numerical support | Publication eligible | Required watermark |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| MH371 | `mh370-broad-release-validation:1` | `passed` | `true` | 0 | `mh370-broad-snapshot-diagnostic:1` | `failed` | `false` | `FAILED NUMERICAL SUPPORT — DIAGNOSTIC ONLY` |
| MH370 | `mh370-broad-release-validation:1` | `passed` | `true` | 0 | `mh370-broad-snapshot-diagnostic:1` | `failed` | `false` | `FAILED NUMERICAL SUPPORT — DIAGNOSTIC ONLY` |

For both flights, the final audit confirmed all of the following against the
current bytes:

- the validation's report-audit hash matches the native report JSON;
- its configuration and executable hashes match the runner TOML and producer;
- its run-manifest and suite-summary hashes match the retained run;
- the report's generator and specification hashes match the reporter and spec;
- the report's PDF and PNG hashes match the rendered files; and
- every validator check passed.

This establishes provenance and model closure. It does not cure the report's
failed particle/root ESS, genealogy, map-capture, material-stratum, or
between-seed support criteria. No coordinate, impact distribution, or search
box follows from a closed failed diagnostic.

## MH371 truth provenance and caveat

The MH371 runner has no truth argument and does not read
`workspace/inputs/controls/mh371-truth.csv`. The reporter opens and hashes that
file only after loading the finalized snapshot artifacts, then computes the
per-epoch truth diagnostics recorded in its JSON.

The experimental selection was not fully prospective. A pilot inspection
moved the last selected window from 06:59 to 06:48 to avoid the known descent
turn. The inference bytes remain truth-separated, but the window choice is
partly truth-informed. Any use of MH371 accuracy or coverage must state both
facts and must not generalize one flight into calibrated MH370 coverage.

## Contextual-source provenance

The Davey PDF is the unchanged 2016 open-access book and is context, not an
input to the broad posterior. Its complete local recreation, citation ledger,
and limitations are under
`workspace/.sources/davey-2016-bayesian-search/`. The obsolete
canonical-versus-Davey plot is not a corrected release result because its
canonical curve came from the withdrawn one-turn chain.

The search atlas is independently generated from the ledgers under
`workspace/.sources/mh370-seabed-search-coverage/`. Its source lock records
exact URLs, byte hashes, licences, attribution, transformations, and explicit
non-bundling decisions. The atlas does not consume either broad posterior and
does not represent a calibrated detection model or search recommendation.

See [COPYRIGHT_AND_LICENSE.md](COPYRIGHT_AND_LICENSE.md) for rights boundaries
and [REPRODUCE.md](REPRODUCE.md) for exact verification and regeneration
commands.

