cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import pathlib
p=pathlib.Path('tl_grid_table.py'); s=p.read_text()
old='''    try:
        arc.to_parquet(out / "tl_grid.parquet", index=False)
    except Exception as e:  # pyarrow absent
        print("parquet not written:", e)
    arc.to_csv(out / "tl_grid.csv.gz", index=False)'''
new='''    np.savez_compressed(out / "tl_grid.npz", **{c: arc[c].to_numpy() for c in arc.columns})   # column arrays; csv index beside
    arc.to_csv(out / "tl_grid.csv.gz", index=False)'''
assert old in s; s=s.replace(old,new)
s=s.replace("  tl_grid.parquet / tl_grid.csv.gz   every (source, receiver, band, source depth) row of the grid, with",
            "  tl_grid.npz / tl_grid.csv.gz       every (source, receiver, band, source depth) row of the grid (npz = one array per column), with")
p.write_text(s)
EOF
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid
python tl_grid_table.py /tmp/tlg_tables_A $OUT/raw/passA > /dev/null && ls /tmp/tlg_tables_A
time python tl_grid_evidence.py /tmp/tlg_tables_A /tmp/tlg_ev_A 2>&1 | tail -40
python -c "import json; d=json.load(open('/tmp/tlg_ev_A/noise_levels.json')); print({k:(round(v['median'],1),round(v['lo'],1),round(v['hi'],1)) for k,v in d['noise'].items()}); print(d['E_q05_q50_q95_j'], d['tau_median_s'])"