# Pooled 00:11 area density

Provisional conditional PDF of airborne position.

Regenerate all figures and numerical artifacts, without sampling:

```bash
python /jackbox/home/MH370/crates/reporting/scripts/arc_density_report.py --runs /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/fuel-initial-proposal-85000-seed-37091631 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/fuel-initial-proposal-85000-seed-37091632 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/fuel-initial-proposal-85000-seed-37091633 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/fuel-initial-proposal-85000-seed-37091634 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/fuel-initial-proposal-85000-seed-37091635 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/fuel-initial-proposal-85000-seed-37091636 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/fuel-initial-proposal-85000-seed-37091637 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/fuel-initial-proposal-85000-seed-37091638 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/fuel-initial-proposal-85000-seed-37091639 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/fuel-initial-proposal-85000-seed-37091640 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/fuel-initial-proposal-85000-seed-37091641 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/fuel-initial-proposal-85000-seed-37091642 --output /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/pooled-arc-density --baseline-runs 3
```

Requires NumPy and Matplotlib. Input identities, seeds, normalizers, source identity and comparisons are in summary.json. The 35,000 ft map label is a reference line, not a terminal altitude constraint. All initial candidates are counted, but resampled descendants are correlated. Independent nonoverlapping groups are reported separately.
