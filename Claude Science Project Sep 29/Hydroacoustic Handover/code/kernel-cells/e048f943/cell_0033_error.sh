OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels
for i in $(seq 1 30); do n=$(ls $OUT/draws/*/seed-*.npz 2>/dev/null | wc -l); echo "$(date +%T) $n"; [ $n -ge 74 ] && break; sleep 20; done
grep -c "rows" $OUT/logs/draw-*.log; grep -il "error\|Traceback" $OUT/logs/draw-*.log