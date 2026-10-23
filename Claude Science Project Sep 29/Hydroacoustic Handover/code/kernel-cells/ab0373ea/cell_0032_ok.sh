for p in 80982 81230 81269 81505 87011; do kill -0 $p; echo "$p rc=$?"; done 2>&1
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
lsof -t $OUT/ram_grid_rows.csv 2>/dev/null | sort -u | tr '\n' ' '; echo
id; 