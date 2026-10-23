python - <<'EOF'
import pandas as pd
TG="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables"; OUT="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid"
c=pd.read_csv(f"{TG}/imos_tl_ram_coverage.csv",dtype={"logger":str}); r=c[c.run]
print("planned",len(r)); print(r.groupby("offset_nm").coverage.value_counts().unstack(fill_value=0))
print("complete total",(r.coverage=="complete").sum(), "partial",(r.coverage=="partial bands").sum(), "not reached",r.coverage.str.startswith("not reached").sum())
rows=pd.read_csv(f"{OUT}/ram_grid_rows.csv"); print("rows",len(rows),"cpu-h",round(rows.wall_s.sum()/3600,1)); 
d=pd.read_csv(f"{TG}/imos_ram_minus_kraken_arc.csv"); print("delta rows",len(d)); print("drop-in rows", len(pd.read_csv(f"{TG}/imos_tl_ram_arc.csv")))
print(r[r.coverage=="complete"].groupby(["offset_nm","logger"]).size().unstack())
EOF