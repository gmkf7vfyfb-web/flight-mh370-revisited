cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
for f in imos_injection.py imos_injection_ext.py imos_detectors.py imos_noise.py h08s_shot_template.py h08s_pulse_energy.py exploratory/off_cadence.py kadri_fig9_noise.py; do echo "=================== $f ($(wc -l <$f) lines)"; python - "$f" <<'EOF'
import ast,sys
src=open(sys.argv[1]).read(); t=ast.parse(src)
d=ast.get_docstring(t) or ''
print(d[:1800])
print('--- defs:')
for n in t.body:
    if isinstance(n,(ast.FunctionDef,ast.ClassDef)):
        a=', '.join(x.arg for x in n.args.args) if isinstance(n,ast.FunctionDef) else ''
        print(f"  {n.name}({a})")
EOF
done