OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
grep -c "ok ram" $OUT/run.log; grep "ok ram\|failed" $OUT/run.log | tail -4; date; uptime
python - <<'EOF'
import pandas as pd
d=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid/ram_grid_rows.csv")
print(d.groupby("fc_hz").wall_s.describe()[["count","mean","max"]])
EOF