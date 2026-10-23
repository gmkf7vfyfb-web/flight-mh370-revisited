OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
for i in $(seq 1 38); do if grep -q '"n_jobs": 112' $OUT/wall.json 2>/dev/null; then break; fi; sleep 15; done
cat $OUT/wall.json | tr '\n' ' '; echo; grep -c "ok ram" $OUT/run4_offsets.log; date; uptime