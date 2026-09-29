# Published-route conditional comparison

```bash
python /jackbox/home/MH370/crates/reporting/scripts/proposed_route_report.py --audit /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/overnight-analysis/godfrey-trajectory-audit --positions /jackbox/home/MH370/.sources/godfrey-wspr-passive-radar/data/proposed-trajectory-2023.csv --paper /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/overnight-analysis/sources/godfrey-flight-path-analysis-2023.pdf --histories /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/turns16-mach8-altitude8-vertical-bfo-255000-seed-37091711/trajectory-examples.json --publication-traces /jackbox/home/MH370/.sources/kadri-2024-hydroacoustics/data/kadri-figure-extraction/figure9-vector-traces --output /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/proposed-route-comparison --inline-output /jackbox/home/MH370/mh370-proposed-route-comparison.html
```

Full source audit and limitations are in summary.json. This report does not fit a new trajectory or apply WSPR/acoustic evidence. The exact arguments are preserved below.

{
  "audit": "/jackbox/home/.iso/thread-storage/thr_rzreetwcyu/overnight-analysis/godfrey-trajectory-audit",
  "positions": "/jackbox/home/MH370/.sources/godfrey-wspr-passive-radar/data/proposed-trajectory-2023.csv",
  "paper": "/jackbox/home/.iso/thread-storage/thr_rzreetwcyu/overnight-analysis/sources/godfrey-flight-path-analysis-2023.pdf",
  "histories": "/jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/runs/turns16-mach8-altitude8-vertical-bfo-255000-seed-37091711/trajectory-examples.json",
  "publication_traces": "/jackbox/home/MH370/.sources/kadri-2024-hydroacoustics/data/kadri-figure-extraction/figure9-vector-traces",
  "output": "/jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis/proposed-route-comparison",
  "inline_output": "/jackbox/home/MH370/mh370-proposed-route-comparison.html"
}
