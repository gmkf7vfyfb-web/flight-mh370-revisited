cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pathlib
p=pathlib.Path('tl_grid_run_j.py'); s=p.read_text()
old="    offset lies outside the fitted span (extrapolated: 41.0 and 40.5 S only) are recorded in sources.csv.\"\"\""
new="    offset lies outside the fitted span are recorded in sources.csv (extrapolated at 41.0 and 40.5 S for every offset,\n    and for the western offsets at 40.0-39.0 S, where run J holds no impacts; fit rms there 0.01-0.09 deg).\"\"\""
assert old in s; p.write_text(s.replace(old,new))
p=pathlib.Path('tl_grid_evidence.py'); s=p.read_text()
old="noise_levels.json, and the two charts (PNG + PDF): tl_vs_latitude, detectable_fraction.\nUsage:"
new="noise_levels.json. The two charts (PNG + PDF: tl_vs_latitude, detectable_fraction) are drawn from these files by\ntl_grid_charts.py, not here.\nUsage:"
assert old in s; p.write_text(s.replace(old,new))
EOF
python -c "import ast; [ast.parse(open(f).read()) for f in ('tl_grid_run_j.py','tl_grid_evidence.py')]; print('ok')"