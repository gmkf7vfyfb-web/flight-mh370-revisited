cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; ls exploratory; grep -l "farfield_array_factor\|posthoc_hflat" -r . ../../../../../ 2>/dev/null | head
grep -rl "farfield_array_factor" "../../../../../../repo/Claude Science Project Sep 29/results/hydroacoustics-audit/scripts" 2>/dev/null
echo "=== kraken_tl API"; python - <<'EOF'
import ast
m=ast.parse(open('kraken_tl.py').read()); print((ast.get_docstring(m) or '')[:1500])
for n in m.body:
    if isinstance(n,ast.FunctionDef): print(n.name, [a.arg for a in n.args.args], (ast.get_docstring(n) or '')[:400].replace('\n',' '))
m=ast.parse(open('air9_tl_validation.py').read())
for n in m.body:
    if isinstance(n,ast.FunctionDef): print('A9V', n.name, [a.arg for a in n.args.args], (ast.get_docstring(n) or '')[:300].replace('\n',' '))
m=ast.parse(open('shared_paths.py').read()); print((ast.get_docstring(m) or '')[:1200])
for n in m.body:
    if isinstance(n,ast.FunctionDef): print('SP', n.name, [a.arg for a in n.args.args])
EOF