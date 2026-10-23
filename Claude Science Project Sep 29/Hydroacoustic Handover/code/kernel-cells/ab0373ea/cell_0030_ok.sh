OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
echo "log:"; lsof -t $OUT/run.log 2>/dev/null | sort -u | tr '\n' ' '; echo
echo "rows:"; lsof -t $OUT/ram_grid_rows.csv 2>/dev/null | sort -u | tr '\n' ' '; echo
echo "work:"; lsof -t +D $OUT/work 2>/dev/null | sort -u | tr '\n' ' '; echo
echo "python cmds:"; lsof -c python 2>/dev/null | grep -i "imos_ram\|run-j-imos" | awk '{print $2}' | sort -u | tr '\n' ' '; echo
ls $OUT/work