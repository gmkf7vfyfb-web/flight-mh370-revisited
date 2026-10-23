OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
mv $OUT/paths $OUT/paths_hold; sleep 240
grep -i "deadline reached\|Error" $OUT/run.log | tail -3
lsof -t $OUT/ram_grid_rows.csv 2>/dev/null | sort -u | tr '\n' ' '; echo
lsof -c python 2>/dev/null | grep -i "run-j-imos" | awk '{print $2}' | sort -u | tr '\n' ' '; echo