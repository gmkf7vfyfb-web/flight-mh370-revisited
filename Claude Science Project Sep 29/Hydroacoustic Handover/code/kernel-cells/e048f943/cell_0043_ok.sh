OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels
for i in $(seq 1 40); do if grep -q "DROP\|KEEP\|MARGINAL" $OUT/logs/levels.log 2>/dev/null || grep -q Traceback $OUT/logs/levels.log; then break; fi; sleep 20; done
tail -n 14 $OUT/logs/levels.log; ls $OUT/tables/