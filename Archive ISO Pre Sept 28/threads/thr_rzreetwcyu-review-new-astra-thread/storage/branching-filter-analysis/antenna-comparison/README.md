# Conditional antenna comparisons

```bash
python /jackbox/home/MH370/crates/reporting/scripts/antenna_sensitivity_report.py --statuses /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/antenna-baseline-status.json /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/antenna-relaxation-status.json /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/antenna-enlarged-status.json /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/antenna-broader-million-status.json --output /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/antenna-comparison --inline-output /jackbox/home/MH370/mh370-antenna-comparison.html
```

All inputs are saved runner outputs. Each named NPZ contains unsmoothed 5 km cell probabilities for one flight/antenna model. The equal-area projection is defined in arc_density_report.py.
