OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection
ps aux | grep -c "[i]nputs.py"; tail -c 1500 $OUT/inputs/inputs.log; ls $OUT/inputs