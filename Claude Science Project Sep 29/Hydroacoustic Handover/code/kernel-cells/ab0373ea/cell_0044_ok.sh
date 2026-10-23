P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
cd "$P" && python - <<'EOF'
import pathlib
p=pathlib.Path("imos_ram_grid.py"); s=p.read_text()
s=s.replace('g = nd[lat_node]; return _interp_logf(g.index.values, g[col].reindex(bands).values, [r.fc_hz])[0]',
            'g = nd[lat_node]; return _interp_logf(np.array(bands), g[col].reindex(bands).values, [r.fc_hz])[0]')
s=s.replace('''    for (lg, lat, off), g in R.groupby(["logger", "lat", "offset_nm"]):
        g = g.set_index("fc_hz"); nodes[(lg, off)] = nodes.get((lg, off), {}); nodes[(lg, off)][lat] = g''',
'''    for (lg, lat, off), g in R.groupby(["logger", "lat", "offset_nm"]):
        if set(g.fc_hz.round(3)) != set(np.round(bands, 3)): continue   # a node counts only with every band done (partial nodes = not covered)
        g = g.set_index("fc_hz"); nodes[(lg, off)] = nodes.get((lg, off), {}); nodes[(lg, off)][lat] = g''')
s=s.replace("  (a) DELTA(lat, offset, f): linear in log f across the computed bands, clamped at the ends",
            "  (a) DELTA(lat, offset, f): a node is used only when every band is done (a partial node at the deadline is 'not covered');\n      linear in log f across the computed bands, clamped at the ends")
p.write_text(s)
EOF
python -m py_compile imos_ram_grid.py && PYTHONPATH=. python imos_ram_grid.py build /tmp/interim /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables /tmp/interim/tables 2>&1 | grep -v Warning | tail -30