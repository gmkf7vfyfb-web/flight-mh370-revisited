cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; python -c "
import ast;print(ast.get_docstring(ast.parse(open('prepare/fetch_imos_background.py').read())))"; python -c "
import json;m=json.load(open('data/imos_background/MANIFEST.json'));print(list(m.keys()) if isinstance(m,dict) else type(m)); print(json.dumps(m,indent=0)[:2500])"