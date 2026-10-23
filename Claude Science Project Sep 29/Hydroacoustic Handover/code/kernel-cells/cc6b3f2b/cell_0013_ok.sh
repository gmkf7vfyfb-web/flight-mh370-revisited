cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n 1,400p kraken_tl.py | grep -v "^\s*$" | sed -n 25,200p
echo ==== shared_paths; python -c "
import ast;t=ast.parse(open('shared_paths.py').read());print((ast.get_docstring(t) or '')[:2500]);print([n.name for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))])"
ls ../data/ocean_paths | head; 