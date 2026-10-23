cd hydro; export GIT_CONFIG_GLOBAL=/dev/null
KD="Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data"
git ls-tree -r --name-only origin/hypothesis/hydroacoustics "$KD" | sed "s|$KD/||"
mkdir -p ../kadri_data/kadri-figure-extraction/figure9-vector-traces
for p in a-H01W b-H01W c-H01W d-H08S e-H08S; do git show "origin/hypothesis/hydroacoustics:$KD/kadri-figure-extraction/figure9-vector-traces/kadri-2024-figure9-panel-$p.csv" > ../kadri_data/kadri-figure-extraction/figure9-vector-traces/kadri-2024-figure9-panel-$p.csv; done
git show "origin/hypothesis/hydroacoustics:$KD/kadri-table1-transients.csv" > ../kadri_data/kadri-table1-transients.csv 2>/dev/null
for f in ../kadri_data/kadri-figure-extraction/figure9-vector-traces/*.csv; do echo "$f $(wc -l < $f)"; head -3 "$f"; done
head -5 ../kadri_data/kadri-table1-transients.csv