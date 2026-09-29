# Pooled 00:11 area density

Provisional conditional PDF of airborne position.

Regenerate all figures and numerical artifacts, without sampling:

```bash
python /jackbox/home/MH370/crates/reporting/scripts/arc_density_report.py --runs /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/cruise-initial-prior-seed-37092211 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/cruise-initial-prior-seed-37092212 --output /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/cruise-initial-prior-comparison --baseline-runs 1
```

Requires NumPy and Matplotlib. Input identities, seeds, normalizers, source identity and comparisons are in summary.json. The 35,000 ft map label is a reference line, not a terminal altitude constraint. All initial candidates are counted, but resampled descendants are correlated. Independent nonoverlapping groups are reported separately.
