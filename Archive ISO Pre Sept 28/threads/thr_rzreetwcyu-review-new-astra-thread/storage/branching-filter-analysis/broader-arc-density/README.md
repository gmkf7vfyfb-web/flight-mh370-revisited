# Pooled 00:11 area density

Provisional conditional PDF of airborne position.

Regenerate all figures and numerical artifacts, without sampling:

```bash
python /jackbox/home/MH370/crates/reporting/scripts/arc_density_report.py --runs /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/turns16-mach8-altitude8-vertical-bfo-seed-37091631 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/turns16-mach8-altitude8-vertical-bfo-seed-37091640 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/turns16-mach8-altitude8-vertical-bfo-255000-seed-37091711 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/turns16-mach8-altitude8-vertical-bfo-255000-seed-37091712 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/turns16-mach8-altitude8-vertical-bfo-170000-seed-37091713 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/turns16-mach8-altitude8-vertical-bfo-170000-seed-37091714 --output /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/broader-arc-density --baseline-runs 4
```

Requires NumPy and Matplotlib. Input identities, seeds, normalizers, source identity and comparisons are in summary.json. The 35,000 ft map label is a reference line, not a terminal altitude constraint. All initial candidates are counted, but resampled descendants are correlated. Independent nonoverlapping groups are reported separately.
