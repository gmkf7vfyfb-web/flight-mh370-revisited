cd ./.tmp/repo
head -n 6 .git/info/sparse-checkout > /tmp/sp; mv /tmp/sp .git/info/sparse-checkout
K="/Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics"
cat >> .git/info/sparse-checkout <<EOF
/Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md
/Claude Science Project Sep 29/coordination/architecture.md
/ISO Sept 28 Status/threads/hydroacoustics-open-questions.md
$K/data/two-station-correlation-config.json
$K/outputs/two-station-*
$K/outputs/correlation-driving-windows.csv
$K/outputs/reference-source-correlations.csv
$K/outputs/two-station-candidate-context.pdf
$K/code/two_station_correlation_scan.py
EOF
git checkout -q claude-science-sep29 2>&1 | tail -2; git read-tree -mu HEAD 2>&1|tail -2
ls -la "${K#/}/outputs" "${K#/}/data" 2>&1 | head -30
git ls-tree -r --name-only HEAD | grep "kadri-2024-hydroacoustics" | grep -v "\.md$" | sed 's|.*kadri-2024-hydroacoustics/||' | awk -F/ '{print $1}' | sort | uniq -c
wc -c "Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md" "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" "Claude Science Project Sep 29/ARCHITECTURE.md" "ISO Sept 28 Status/threads/master-prompts/common.txt"