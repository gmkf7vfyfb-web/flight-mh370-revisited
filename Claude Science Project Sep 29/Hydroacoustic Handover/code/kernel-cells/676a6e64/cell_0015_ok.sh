cd repo
P="Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
echo "=== fig9 triggers"; git show "FETCH_HEAD:$P/results-data/kadri2a/kadri_fig9_triggers.csv" | head -30
echo; echo "=== table1 transients"; git show "FETCH_HEAD:ISO Sept 28 Status/inputs/recovered-v01/.sources/kadri-2024-hydroacoustics/data/kadri-table1-transients.csv" | head -25
echo; echo "=== table1 summary json"; git show "FETCH_HEAD:$P/results-data/kadri2a/kadri_table1_summary.json" | head -40
echo; echo "=== which fig9 panels digitised"; git ls-tree -r FETCH_HEAD --name-only | grep -i -E 'fig9|fig-9|figure9' | grep -v -E '\.(png|pdf)$' | head -20