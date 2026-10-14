#!/bin/bash
# Joined V2 production summary (after full/run_joined_v2.sh): per seed, the joined estimator (smoke/joined_v2.py) and the 22:41
# arm's onset-boundary / truncation / window statistics (smoke/pilot_oct13.py gate4 on the slim seed), then the 8-seed aggregate
# (smoke/joined_v2_summary.py). Light: about 2 min a seed at 4 threads; outside the heavy lock.
set -u
S=hypotheses/end-of-flight; PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python; SEEDS=${SEEDS:-"1 2 3 4 5 6 7 8"}
O=${EOF_OUT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i-joined-v2}; SD=/Users/pete/Downloads/mh370-exchange/core/run-i/next-i-waypoints/bto-bfo
R=$O/summary; mkdir -p $R
for k in $SEEDS; do
  H=$SD/seed-$k
  OMP_NUM_THREADS=4 PYTHONPATH=$S/smoke $PY $S/smoke/joined_v2.py $O/J2241 $O/J0011 $H/handoff-m2241/handoff.toml.gz $H/handoff-m0011/handoff.toml.gz $R/joined-s$k.json > $R/joined-s$k.txt 2>&1
  EOF_SEED=$k OMP_NUM_THREADS=4 PYTHONPATH=$S/smoke $PY $S/smoke/pilot_oct13.py gate4 $O/J2241 $R/gate4-s$k.json > /dev/null 2>&1
  echo "seed $k: $(grep -c '^D' $R/joined-s$k.txt) cells"
done
PYTHONPATH=$S/smoke $PY $S/smoke/joined_v2_summary.py $R $SEEDS
