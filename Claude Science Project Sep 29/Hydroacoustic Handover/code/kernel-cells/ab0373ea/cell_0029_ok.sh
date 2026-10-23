OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
head -1 $OUT/ram_grid_rows.csv; awk -F, '{print NF}' $OUT/ram_grid_rows.csv | sort | uniq -c
python - <<'EOF'
import pandas as pd
d=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid/ram_grid_rows.csv")
print(len(d), d.duplicated(["tag","fc_hz"]).sum()); print(d[d.duplicated(["tag","fc_hz"],keep=False)].sort_values(["tag","fc_hz"])[["tag","fc_hz","tl_ram_db","finished_at"]].head(12))
print(d.status.value_counts(dropna=False))
EOF