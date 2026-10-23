OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
kill -0 80915 2>&1 && echo "80915 alive" || echo "80915 gone"
ls $OUT; ls $OUT/work 2>/dev/null | head; tail -2 $OUT/run.log
# find python pids via /proc-less approach: lsof on the log
lsof -t $OUT/run.log 2>/dev/null | sort -u | tr '\n' ' '; echo
lsof -t $OUT/ram_grid_rows.csv 2>/dev/null | sort -u | tr '\n' ' '; echo