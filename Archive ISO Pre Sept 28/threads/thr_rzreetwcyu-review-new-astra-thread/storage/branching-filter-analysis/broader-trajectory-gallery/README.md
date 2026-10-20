# Exact trajectory examples

Reproduce with:

```bash
python /jackbox/home/MH370/crates/reporting/scripts/trajectory_examples_report.py --histories /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/turns16-mach8-altitude8-vertical-bfo-170000-seed-37091713 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/turns16-mach8-altitude8-vertical-bfo-170000-seed-37091714 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/turns16-mach8-altitude8-vertical-bfo-seed-37091640 --pooled-summary /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/broader-arc-density/summary.json --output /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/broader-trajectory-gallery --inline-output /jackbox/home/MH370/mh370-broader-route-examples.html
```

Dependencies match the canonical arc-density report (NumPy and Matplotlib). All routes come from saved exact deterministic replays. No trajectory is inferred by joining contact positions. Latitude-bin probabilities use the stated pooled ensemble; example source runs are listed above. Histories are illustrative positive-weight draws, not a hard observation-fit feasibility boundary.
