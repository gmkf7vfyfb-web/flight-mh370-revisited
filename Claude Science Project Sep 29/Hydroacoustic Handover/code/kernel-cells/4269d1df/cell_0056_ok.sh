export HOME=$PWD/h XDG_CONFIG_HOME=$PWD/h/.config
mkdir -p scorer; cd repo; P="Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke"
for f in option_table_0019.py displacement_hist.py compact_impacts.py compact-columns.json; do git show "origin/eof:$P/$f" > ../scorer/$f; done
git show "origin/eof:Claude Science Project Sep 29/engine/data/satcom-observations.csv" > ../scorer/satcom-observations.csv 2>/dev/null || git show "origin/claude-science-sep29:Claude Science Project Sep 29/engine/data/satcom-observations.csv" > ../scorer/satcom-observations.csv
git log -1 --format=%h origin/eof; cd ../scorer; wc -l *; grep -n "^def \|^import\|^from\|SATCOM_CSV\|^LAT\|T0" option_table_0019.py | head -40; grep -n "^def \|T0\|import" compact_impacts.py displacement_hist.py | head -30