# Pooled 00:11 area density

Provisional conditional PDF of airborne position.

Regenerate all figures and numerical artifacts, without sampling:

```bash
python /tmp/mh370-branching-filter/crates/reporting/scripts/arc_density_report.py --runs /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/turns16-mach8-altitude8-vertical-bfo-seed-37091631 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/turns16-mach8-altitude8-vertical-bfo-seed-37091640 --output /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/canonical-report-command-control --baseline-runs 1
```

Requires NumPy and Matplotlib. Input identities, seeds, normalizers, source identity and comparisons are in summary.json. The 35,000 ft map label is a reference line, not a terminal altitude constraint. All initial candidates are counted, but resampled descendants are correlated. Independent nonoverlapping groups are reported separately.
