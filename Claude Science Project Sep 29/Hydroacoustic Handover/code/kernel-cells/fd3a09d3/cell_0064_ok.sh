cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pathlib
p=pathlib.Path('tl_grid_table.py'); s=p.read_text()
old='''    g["ramcorr_extrapolated"] = (g.status == "ok") & (np.abs(g.tl_db.values - ref_i) > 10.0)'''
new='''    g["ramcorr_extrapolated"] = (g.status == "ok") & (np.abs(g.tl_db.values - ref_i) > 10.0) & (g.fc_hz.values >= ref.dropna().index.min())'''
assert old in s; p.write_text(s.replace(old,new))
EOF
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
python tl_grid_table.py /tmp/tlg_tables_A /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw/passA > /dev/null
python tl_grid_evidence.py /tmp/tlg_tables_A /tmp/tlg_ev_A 2>&1 | tail -34
python tl_grid_charts.py /tmp/tlg_tables_A /tmp/tlg_ev_A /tmp/tlg_charts_A --stamp "pass A only (offset 0), draft" && ls /tmp/tlg_charts_A