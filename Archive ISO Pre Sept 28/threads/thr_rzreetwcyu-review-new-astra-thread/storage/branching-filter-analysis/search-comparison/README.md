# Search context and conditional probability capture

```bash
python /jackbox/home/MH370/crates/reporting/scripts/posterior_search_context.py --conditioned /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/terminal-conditioned-seed-37091811 --spatial-state /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/spatial-comparison-status.json --numerical-comparison /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/terminal-guided-conditioned --search-atlas /jackbox/home/MH370/.sources/mh370-seabed-search-coverage/data/map/search-evidence-atlas.geojson --output /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/search-comparison --inline-output /jackbox/home/MH370/mh370-search-comparison.html --budget-km2 7500.0
```

Cell ranking uses the canonical WGS84 equal-area projection and no smoothing. Every physical model and evidence condition is separate. Context footprints never change weights. Independent numerical-run capture is reported where available. Complete ranks, tile identities and input hashes are retained in summary.json; PDF/SVG figures show R600-first cases.
