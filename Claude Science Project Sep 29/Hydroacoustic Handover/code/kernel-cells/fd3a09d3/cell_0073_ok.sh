OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid
for i in $(seq 1 19); do if [ -f $OUT/raw/passB/tl_grid.csv ]; then break; fi; sleep 30; done
grep paths $OUT/raw/passB.log | tail -1; ls $OUT/raw/passB 2>/dev/null; date -u