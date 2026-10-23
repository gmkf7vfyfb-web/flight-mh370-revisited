P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
TG=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables
mkdir -p /tmp/interim; cp $OUT/plan.csv /tmp/interim/; python - <<'EOF'
import pandas as pd
d=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid/ram_grid_rows.csv", on_bad_lines="skip")
d=d.drop_duplicates(["tag","fc_hz"]); d.to_csv("/tmp/interim/ram_grid_rows.csv", index=False)
d["off"]=d.tag.str.extract(r"S_([+-]\d+)-")[0].astype(float)
print(len(d), d.status.value_counts().to_dict()); print(d[d.off==0].groupby(d.tag.str.split("-").str[-1]).size().to_dict(), "offset0 rows (3 bands each)")
EOF
cd "$P" && PYTHONPATH=. python imos_ram_grid.py build /tmp/interim $TG /tmp/interim/tables 2>&1 | grep -v Warning | tail -30