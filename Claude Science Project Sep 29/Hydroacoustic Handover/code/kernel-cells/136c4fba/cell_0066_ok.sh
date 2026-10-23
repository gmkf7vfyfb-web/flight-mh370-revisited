cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics" && export XDG_CONFIG_HOME=/tmp/xdg
KD="../../../../Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data"
python3 prepare/kadri_h01w_time_discriminant.py "$KD" results-data/kadri_northern 2>&1 | grep -c verdict
ls -la results-data/kadri_northern/