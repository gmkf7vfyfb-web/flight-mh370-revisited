cd ./.tmp/repo; K="Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics"
for f in data/aligned-detection-config.json outputs/aligned-detection-analysis-summary.json outputs/event-pair-analysis-summary.json data/event-pair-analysis-config.json outputs/summary.json outputs/conditional-geometry-summary.json outputs/oscar-boundary-audit-summary.json outputs/impact-simulation-summary.json; do echo "/$K/$f" >> .git/info/sparse-checkout; done
git read-tree -mu HEAD 2>&1 | tail -1
cd "$K"; wc -c outputs/aligned-detection-analysis-summary.json outputs/event-pair-analysis-summary.json outputs/summary.json outputs/conditional-geometry-summary.json outputs/oscar-boundary-audit-summary.json outputs/impact-simulation-summary.json
grep -o '"[a-z_]*p[a-z_]*": *0\.00[0-9]*' outputs/*.json | head -30
grep -l "0.0025\|0\.002[0-9]" outputs/*.json