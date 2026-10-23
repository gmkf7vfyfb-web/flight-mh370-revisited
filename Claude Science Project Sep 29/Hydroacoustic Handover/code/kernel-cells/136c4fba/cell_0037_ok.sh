cd repo && export XDG_CONFIG_HOME=/tmp/xdg
git push -q origin hypothesis/hydroacoustics 2>&1 | tail -3; echo "pushed: $(git rev-parse --short origin/hypothesis/hydroacoustics 2>/dev/null || git rev-parse --short HEAD)"
cd "Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
KD="../../../../Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data"
time python3 prepare/kadri_northern_conditional.py "$KD" results-data/kadri_northern 2>&1 | tail -40