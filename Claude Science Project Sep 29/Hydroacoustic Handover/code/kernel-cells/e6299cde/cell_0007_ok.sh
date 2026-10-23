cd "repo/Claude Science Project Sep 29"
grep -n "^## \|^### \|^\*\*" results/hydroacoustics-weak-signal-methods.md | head -50
echo ====; sed -n 1,40p results/hydroacoustics-weak-signal-methods.md
cd "../../hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
echo "==== weak_signal dir"; ls weak_signal; ls kadri_package
for f in imos_detectors.py imos_preregistration.py kadri_table1_test.py imos_coincidence.py imos_noise.py kadri_fig9_noise.py; do echo "==== $f"; python - "$f" <<'EOF'
import ast,sys
src=open(sys.argv[1]).read(); d=ast.get_docstring(ast.parse(src)) or ''
print(d[:1800]); print('... [funcs]', [n.name for n in ast.parse(src).body if isinstance(n,ast.FunctionDef)][:30])
EOF
done