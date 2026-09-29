# Exact trajectory examples

Reproduce with:

```bash
python /jackbox/home/MH370/crates/reporting/scripts/trajectory_examples_report.py --histories /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/recovered-history-seed-37091631 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/recovered-history-seed-37091640 --pooled-summary /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/pooled-arc-density/summary.json --output /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/trajectory-gallery --inline-output /jackbox/home/MH370/mh370-route-examples.html
```

Dependencies match the canonical arc-density report (NumPy and Matplotlib). All routes come from saved exact deterministic replays. No trajectory is inferred by joining contact positions. Latitude-bin probabilities use the stated pooled ensemble; examples use two constituent runs. Histories are illustrative positive-weight draws, not a hard observation-fit feasibility boundary.
