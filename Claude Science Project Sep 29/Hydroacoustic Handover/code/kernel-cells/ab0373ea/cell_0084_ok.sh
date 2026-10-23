OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
for i in $(seq 1 36); do kill -0 23504 2>/dev/null || break; if grep -q '"n_jobs": 112' $OUT/wall.json 2>/dev/null; then break; fi; sleep 15; done
sleep 5; echo "parent alive: $(kill -0 23504 2>/dev/null && echo yes || echo no)"; cat $OUT/wall.json | tr '\n' ' '; echo; grep -c "ok ram" $OUT/run4_offsets.log; grep -i "deadline\|failed" $OUT/run4_offsets.log | head -2; date