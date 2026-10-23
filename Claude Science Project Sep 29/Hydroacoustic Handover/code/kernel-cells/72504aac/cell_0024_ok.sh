X=/Users/pete/Downloads/mh370-exchange; R="repo/Claude Science Project Sep 29/results"
grep -n -i -E "core|\| *D *\||DS|product|D0|treatment|drift" $X/composer/run-j-views-v3.2/README.md | head -40
echo ===; ls "$R/composer-views-run-j/"; grep -n -E "def |NX|NY|^[A-Z_]+ *=" "$R/composer-views-run-j/views_common.py" | head -40
echo ===; python -c "
import pandas as pd
t=pd.read_csv('$X/hydroacoustics/run-j-tl-grid/tables/tl_grid.csv.gz',nrows=3); print(list(t.columns)); print(t.head(3).T)
p=pd.read_csv('$X/hydroacoustics/run-j-searches/coincidence/pairs.csv'); print(p.shape, list(p.columns)); print(p.head(3).T)
"
cat "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/composition_run_j/v2/coincidence_locus.csv"
ls -la $X/hydroacoustics/graphics-2026-10-22/ranked/ 2>&1 | head