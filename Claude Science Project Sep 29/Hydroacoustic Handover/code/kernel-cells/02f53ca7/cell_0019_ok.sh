cd hydro; git ls-tree -r --name-only origin/hypothesis/hydroacoustics | grep -i "airgun_lines\|blackman_source_classes\|blackman_receiver" ; cd ..
grep -rn "air7\|air8" "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/blackman/"*.csv 2>/dev/null | head -20
ls "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/blackman/"
grep -n "air7\|air8\|air9" "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/airgun_sites_confirm.py" | head -20
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python - <<'EOF'
import ast
m=ast.parse(open('ram_tl_check.py').read()); print((ast.get_docstring(m) or '')[:2500])
for n in m.body:
    if isinstance(n,ast.FunctionDef): print(n.name, [a.arg for a in n.args.args])
EOF
cat ../results-data/ram_check/convergence.json | head -40