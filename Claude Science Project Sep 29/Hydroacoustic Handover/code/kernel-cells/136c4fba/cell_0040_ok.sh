cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics" && export XDG_CONFIG_HOME=/tmp/xdg
KD="../../../../Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data"
time python3 prepare/kadri_northern_conditional.py "$KD" results-data/kadri_northern 2>&1 | grep -v "UserWarning\|_set_context\|RuntimeWarning\|return (x -" | tail -45