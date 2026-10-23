cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pathlib
p=pathlib.Path('tl_grid_run_j.py'); s=p.read_text()
old="    offset lies outside the fitted span are recorded in sources.csv (extrapolated at 41.0 and 40.5 S for every offset,\n    and for the western offsets at 40.0-39.0 S, where run J holds no impacts; fit rms there 0.01-0.09 deg).\"\"\""
new="    offset lies outside the fitted span (arc_fit_extrapolated) are recorded per source point in sources.csv; the\n    results note reports which rows are extrapolated (the southern rows, where run J holds few impacts) and their rms.\"\"\""
assert old in s; p.write_text(s.replace(old,new)); print('ok')
EOF
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid; grep paths $OUT/raw/passA.log | tail -1; ls $OUT/raw/passA | head; date -u