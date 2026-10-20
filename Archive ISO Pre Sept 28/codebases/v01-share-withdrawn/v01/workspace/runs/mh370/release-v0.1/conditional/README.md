# Optional spatial sensitivities

These branches apply one declared source surface to the primary impact family. They never
update the central posterior, and alternative Pléiades transport surfaces are never pooled
or multiplied. The equal-family surface is an uncalibrated display sensitivity.

## Pléiades resolution audit

The checked-in 5×512 ensemble appeared sharply localized, but a frozen-binary ladder at
2,000, 8,000, and 30,000 draws per seed showed that this was particle collapse rather than
a resolved conditional PDF.

| Surface | Conditional ESS at 150,000 | Centroid shift from baseline | Change from 40,000 | Native-cell TV from 40,000 |
|---|---:|---:|---:|---:|
| BRAN2016 | 5.63 | 58.27 NM | 3.19 NM | 0.365 |
| OSCAR v2 Final | 9.14 | 55.00 NM | 0.76 NM | 0.0046 |
| GLORYS12 + WAVERYS | 6.13 | 42.38 NM | 1.37 NM | 0.0023 |
| Equal-family sensitivity | 5.63 | 58.27 NM | 3.19 NM | 0.365 |

At the largest rung, 99.9203% of baseline mass is inside native support and the likelihood
floor receives negligible conditional mass, so neither boundary loss nor flooring explains
the collapse. Every Pléiades ESS remains below 10, and one impact particle can carry 22–36%
of conditional mass. Consequently, all Pléiades contours, centroids, and areas are
**numerically unresolved and display only**. They must not rank or allocate search effort in
this release. The large pilot ensembles were not promoted.

Machine results and full provenance are in
[pleiades-resolution-audit.json](pleiades-resolution-audit.json); all ladder rows and robust
spatial diagnostics are in [pleiades-resolution-audit.csv](pleiades-resolution-audit.csv).
The canonical RNZAF context plot prints the equal-family ESS directly on panel C and labels
the conditional contour unresolved.

The separately labelled CMEMS ocean-drift branch does not have this numerical problem
(conditional ESS 924.62 from the 5×512 release ensemble), but its source family remains
`diagnostic_only`, `admitted=false` and cannot update the central estimator.

## Reproduction

The executable is frozen at SHA-256
`de28b0adc6de796026e6075da614b5e11c78459d4beafbca42f6e30b10758b4b`.
Generate each temporary ladder suite from the repository root with:

```text
python3 crates/runner/scripts/impact_release_suite.py --matrix configs/mh370-impact-release-families.json --runner target/release/mh370 --output <temporary-directory>/mh370-impact-primary-pilot-<draws>x5 --draw-count <draws> --jobs 5
```

Use `<draws>` equal to `2000`, `8000`, or `30000`. Copy each corresponding checked-in
Pléiades conditional TOML to `/tmp`, change only the parent-suite prefix and relative input
prefix, then run:

```text
nice -n 15 target/release/mh370 apply-conditional-surface --config <temporary-directory>/mh370-pleiades-resolution-<draws>-<surface>.toml --output <temporary-directory>/mh370-pleiades-resolution-pilot/n<draws>/<surface>
```

Exact suite and parent handoff hashes are pinned in the JSON audit.
