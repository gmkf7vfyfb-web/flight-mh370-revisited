cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; ls; python - <<'EOF'
import ast,glob
for f in ['kraken_tl.py']+sorted(glob.glob('*ram*.py'))+sorted(glob.glob('*level*.py'))+sorted(glob.glob('*air9*.py'))+sorted(glob.glob('*source*.py')):
    try:
        d=ast.get_docstring(ast.parse(open(f).read()))
        print('=====',f); print((d or '')[:1500])
    except Exception as e: print(f,e)
EOF