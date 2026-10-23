OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
echo "work dirs: $(ls $OUT/work 2>/dev/null | wc -l)"; ls $OUT/work 2>/dev/null | head
echo "pids on rows file: $(lsof -t $OUT/ram_grid_rows.csv 2>/dev/null | sort -u | tr '\n' ' ')"
echo "python pids on this run dir: $(lsof -c python 2>/dev/null | grep -c 'run-j-imos-ram-grid')"; lsof -c python 2>/dev/null | grep 'run-j-imos-ram-grid' | awk '{print $2}' | sort | uniq -c | head -20
for p in $(lsof -c python 2>/dev/null | grep 'run4_offsets.log' | awk '{print $2}' | sort -u); do echo "pid $p threads: $(lsof -p $p 2>/dev/null | head -1 >/dev/null; echo n/a)"; done
grep -c "ok ram" $OUT/run4_offsets.log; tail -c 300 $OUT/run4_offsets.log | grep -o '\[[0-9]*/112\][^$]*' | tail -1; date; uptime
# per-process CPU via top (one sample)
top -l 1 -stats pid,cpu,th,command 2>/dev/null | grep -i python | head -12