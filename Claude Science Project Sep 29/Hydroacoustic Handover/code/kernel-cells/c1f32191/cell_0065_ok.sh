cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j"
O=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated; S=$O.staging
cat $O/READY; head -4 $O/README.txt | cut -c1-200
mv $O $S && rm -f $S/READY
cat > /tmp/topup.sh <<'EOF'
#!/bin/bash
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j"
S=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging
SEEDS="run-j-waypoints:21 run-j-waypoints:22 run-j-waypoints:23 run-j-waypoints:24 run-j-free:2 run-j-free:3 run-j-free:10 run-j-free:11 run-j-free:12 run-j-free:13 run-j-free:14 run-j-free:15 run-j-free:16 run-j-free:17"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 B11_TOPUP=1
n=0
for sk in $SEEDS; do
  s=${sk%%:*}; k=${sk##*:}
  while [ $(jobs -r | wc -l) -ge 4 ]; do sleep 5; done
  free=$(df -k /System/Volumes/Data | tail -1 | awk '{print $4}')
  if [ $free -lt 22020096 ]; then echo "SKIP $s $k free_kb=$free" >> $S/topup.log; continue; fi
  echo "launch $s $k free_kb=$free $(date -u +%H:%M:%S)" >> $S/topup.log
  python worker.py $s $k $S > $S/_w_topup_${s}_$k.log 2>&1 &
done
wait; echo "topup done $(date -u +%H:%M:%S)" >> $S/topup.log
EOF
chmod +x /tmp/topup.sh; nohup /tmp/topup.sh > /dev/null 2>&1 &
sleep 5; cat $S/topup.log