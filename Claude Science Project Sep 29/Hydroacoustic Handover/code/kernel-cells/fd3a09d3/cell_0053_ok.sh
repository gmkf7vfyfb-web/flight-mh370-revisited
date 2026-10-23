OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid
for i in $(seq 1 40); do if [ -f $OUT/raw/passA/tl_grid.csv ]; then break; fi; sleep 30; done
grep paths $OUT/raw/passA.log | tail -1; ls $OUT/raw/passA; date -u