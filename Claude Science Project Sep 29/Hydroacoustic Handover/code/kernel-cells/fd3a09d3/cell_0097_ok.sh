OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid
for i in $(seq 1 19); do if [ -f $OUT/raw/ALLDONE ]; then break; fi; sleep 30; done
grep paths $OUT/raw/passC.log | tail -1; ls $OUT/raw | grep -c ALLDONE; date -u