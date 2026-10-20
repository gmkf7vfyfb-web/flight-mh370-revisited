#!/bin/bash
# Run J joined V2 summary (after full/run_j_joined_v2.sh): per seed the joined estimator (smoke/joined_v2.py), the 22:41 arm's
# gate-4 statistics, the 8-seed aggregate (smoke/joined_v2_summary.py), and the onset-prior sensitivity U1 per seed
# (smoke/onset_uniform_reweight.py; Pete's item 4 ruling 16 Oct 02:08Z). Light; run from engine/ after run-j-joined-v2 is complete.
set -u
S=hypotheses/end-of-flight; PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python; SEEDS=${SEEDS:-"1 2 3 4 5 6 7 8"}
O=${EOF_OUT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-joined-v2}; SD=/Users/pete/Downloads/mh370-exchange/core/run-j/run-j-waypoints/bto-bfo
R=$O/summary; mkdir -p $R/onset-uniform
for k in $SEEDS; do
  H=$SD/seed-$k
  OMP_NUM_THREADS=4 PYTHONPATH=$S/smoke $PY $S/smoke/joined_v2.py $O/J2241 $O/J0011 $H/handoff-m2241/handoff.toml.gz $H/handoff-m0011/handoff.toml.gz $R/joined-s$k.json --seed $k > $R/joined-s$k.txt 2>&1
  EOF_SEED=$k OMP_NUM_THREADS=4 PYTHONPATH=$S/smoke $PY $S/smoke/pilot_oct13.py gate4 $O/J2241 $R/gate4-s$k.json > /dev/null 2>&1
  OMP_NUM_THREADS=4 PYTHONPATH=$S/smoke $PY $S/smoke/onset_uniform_reweight.py $O/J2241 $O/J0011 $H/handoff-m2241/handoff.toml.gz $H/handoff-m0011/handoff.toml.gz $R/onset-uniform/seed-$k.json $k > $R/onset-uniform/seed-$k.log 2>&1
  echo "seed $k: $(grep -c '^D' $R/joined-s$k.txt) cells; U1 $([ -s $R/onset-uniform/seed-$k.json ] && echo ok || echo FAILED)"
done
PYTHONPATH=$S/smoke $PY $S/smoke/joined_v2_summary.py $R $SEEDS
