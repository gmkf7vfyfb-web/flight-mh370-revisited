cd repo && export XDG_CONFIG_HOME=/tmp/xdg
git sparse-checkout add "Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data" 2>&1|tail -2
D="Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data/kadri-figure-extraction"
ls -la "$D/figure9-vector-traces/"
echo "=== metadata ==="; cat "$D/metadata.json"
echo "=== head panel d ==="; head -4 "$D/figure9-vector-traces/kadri-2024-figure9-panel-d-H08S.csv"; wc -l "$D/figure9-vector-traces/"*.csv
echo "=== head panel e ==="; head -4 "$D/figure9-vector-traces/kadri-2024-figure9-panel-e-H08S.csv"