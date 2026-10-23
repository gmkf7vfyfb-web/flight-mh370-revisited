cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import ast
for f in ["per_impact_lnl.py","kraken_tl.py","search_windows.py","synthetic_composer_test.py"]:
    t=ast.parse(open(f).read()); d=ast.get_docstring(t) or ''
    print("=====",f); print(d[:2500]); print('--- defs:', [n.name for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))])
EOF
grep -n "spread\|sigma_t\|dispers\|1.482\|0.006\|S_b\|tau" per_impact_lnl.py | head -40