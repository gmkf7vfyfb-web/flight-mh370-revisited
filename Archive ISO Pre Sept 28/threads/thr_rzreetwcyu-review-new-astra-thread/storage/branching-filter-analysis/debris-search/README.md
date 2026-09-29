# Debris and unsuccessful-search conditional comparison

Completed:54saved input populations×6search conditions=324results. No new
flight or ocean samples.30new matched debris compositions and search updates
took27.32seconds; the search spoke itself took7.59seconds.48six-panel figures
rendered in145.51seconds with peakRSSabout1.35GiB.

Run the saved numerical composition through the canonical hub:

```bash
target/iteration/mh370 apply-searched-area-evidence --config /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/debris-search/search-configuration.json --output /tmp/mh370-search-reproduction
```

The output must be a fresh directory. The configuration pins all parent inputs
and the GeoJSON bySHA256. It explicitly selects effective detection, footprint
assumptions and inter-campaign dependence. The spoke returns P(no detection|x)
and normalized updated weights without a likelihood floor or resampling. The
same impact weight maps back to its actual00:11parent for report summaries.
The54populations retain separate evidence subsets, polars, terminal runs and
cowling seeds; they are never pooled as independent evidence.

`prepare_debris_search.py` in the parent artifact directory reproduces the
subset preparation and complete composition from the retained, hash-checked
source terms. `verify_debris_search.py` checks selected-term sums, independent
MatplotlibvsRust polygon geometry and all324updates. Maximum weight difference
is1.23e-15. Parser round-trip variation is bounded to2binaryULPs and measured
as1.43e-14degrees/0.24microseconds; no trajectory identity changes.

Render with `target/iteration/mh370 report-flight-drift --evidence-only
--analysis <owner-analysis> --output <report-output> --inline-output <HTML>`
and `MH370_REPORT_PYTHON=/tmp/mh370-acoustic-venv/bin/python`. The48maps retain
50/90/99% contours, a25km display kernel on a5km equal-area grid, both footprint
outlines and the FL400seventh-arc reference. This reference does not constrain
particle altitude. All figures and144SVG/PDF/PNG assets were served byte-for-
byte overHTTP; all36browser parameter combinations passed JS/DOM-stub checks.
No full browser engine or authenticated remote-device test was available.

ATSB(2017),Figure73,printedp96/PDFp105, gives the assessed coverage fractions
underlying the94%area-average reference. Uniformly applying it to the separate
detailedL0data footprint is a conditional approximation.50/80% are stress
settings. The optional2018outline60%case is an explicit area/quality assumption,
not measured detection. Shared and independent campaign misses are separate
alternatives. Known holes are retained. Planned boxes, AIS and unlocalized
recent campaign totals are not treated as coverage. Existing archive metadata
still marks the footprint ineligible for a calibrated negative likelihood.

The stable calibrated estimator and original paper goal remain unfinished.
Cruise fuel-conditioned recovery, rare-object drift response, residual terminal
sampling variation and pointwise sonar quality remain material limitations.
The next fixed two-seed fourfold terminal comparison is recorded separately in
`../mixed-terminal-sampling/progress.json`; its status must be checked for liveness.
