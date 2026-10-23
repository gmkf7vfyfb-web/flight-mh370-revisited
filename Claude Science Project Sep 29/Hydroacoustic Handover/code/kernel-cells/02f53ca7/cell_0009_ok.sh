cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
for f in air9_ew0112.py air9_tl_validation.py nx2d.py f35a_eta_calibration.py air8_negative_control.py airgun_sites_confirm.py; do echo "=================== $f ($(wc -l < $f) lines)"; python - "$f" <<'EOF'
import ast,sys
src=open(sys.argv[1]).read(); m=ast.parse(src); d=ast.get_docstring(m) or ''
print(d[:3500])
print("FUNCS:", [n.name for n in m.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))])
EOF
done
ls ../results-data/digitised 2>/dev/null || echo "no results-data/digitised yet"
echo "=== INBOX tail"; cd "../../../../coordination"; grep -n "^## \|^### " HYDROACOUSTICS.md | tail -8