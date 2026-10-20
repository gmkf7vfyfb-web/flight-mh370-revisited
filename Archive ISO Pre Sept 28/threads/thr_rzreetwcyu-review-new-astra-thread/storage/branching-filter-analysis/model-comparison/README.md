# Cruise-model comparisons

```bash
python /jackbox/home/MH370/crates/reporting/scripts/flight_sensitivity_report.py --status /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/relaxation-status.json --baseline /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/recovered-history-seed-37091631 /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/recovered-history-seed-37091640 --output /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/model-comparison --inline-output /jackbox/home/MH370/mh370-model-comparison.html
```

Equal-effort SMC measures are pooled within a model using their estimated normalizers. Different priors are never combined. The matched baseline consists of two selected original runs, not the full million ensemble.
