cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
cat results-data/airgun_sites_confirm/README.txt; echo; cat results-data/airgun_sites_confirm/verdict.json; echo
head -3 results-data/airgun_sites_confirm/airsites_tl.csv; grep -c . results-data/airgun_sites_confirm/airsites_tl.csv
python -c "
import pandas as pd; t=pd.read_csv('results-data/airgun_sites_confirm/airsites_tl.csv'); print(t.columns.tolist()); print(t.groupby(['site','station']).size() if 'site' in t else t.head())
print(t[(t.get('site','')=='air7')].to_string() if 'site' in t else '')
"
cat results-data/airgun_sites_confirm/fig23_CL_air7_bands_DIGITISED.csv; cat results-data/airgun_sites_confirm/fig23_CL_air9_bands_DIGITISED.csv
find . -name "airgun_lines_ew0112.csv" | head; cat $(find . -name "airgun_lines_ew0112.csv" | head -1) 2>/dev/null
echo "=== audit paths.py"; python - <<'EOF'
import ast
p="../../../../../repo/Claude Science Project Sep 29/results/hydroacoustics-audit/scripts/paths.py"
m=ast.parse(open(p).read()); print((ast.get_docstring(m) or '')[:1500])
for n in m.body:
    if isinstance(n,ast.FunctionDef): print(n.name, [a.arg for a in n.args.args], (ast.get_docstring(n) or '')[:200].replace('\n',' '))
EOF
date -u