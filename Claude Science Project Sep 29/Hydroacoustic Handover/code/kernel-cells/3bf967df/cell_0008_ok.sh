cd repo; export HOME=$PWD/../h XDG_CONFIG_HOME=$PWD/../h/.config
git sparse-checkout set --no-cone "ISO Sept 28 Status/inputs/papers/hydroacoustics/" "Claude Science Project Sep 29/results/evidence-sweep-2026-10-17/" "Claude Science Project Sep 29/results/hydroacoustics-kadri-table1-test.md" "Claude Science Project Sep 29/engine/data/satellite-ephemeris-inmarsat.csv" "Claude Science Project Sep 29/engine/data/satcom-observations.csv" 2>&1|tail -1
git ls-remote --heads origin | awk '{print $2}'
P="ISO Sept 28 Status/inputs/papers/hydroacoustics"
wc -c "$P"/*.txt
grep -n -iE '306|bearing|00:5[0-9]|0?0:3[4-9]|intersect|25\.[0-9]+ ?°? ?S|26\.[0-9]|preferred|most likely' "$P/kadri2024.txt" | head -60