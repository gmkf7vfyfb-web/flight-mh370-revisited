#!/bin/bash
# Recompute only the arc-uniform products of every per-seed file in work/v4 into work/v5 (other arrays copied), 4 processes.
W=/Users/pete/Downloads/mh370-exchange/composer/run-j-views/work; mkdir -p $W/v5
ls $W/v4/*.npz | grep -v tmp | while read f; do b=$(basename $f .npz); [ -s $W/v5/$b.npz ] || echo "${b%%_*} $(echo $b | cut -d_ -f2) $(echo $b | cut -d_ -f3)"; done | \
  xargs -P 4 -L 1 bash -c 'OMP_NUM_THREADS=1 python reduce_seed_views.py $0 $1 $2 '$W'/v5/$0_$1_$2.tmp.npz '$W'/v4/$0_$1_$2.npz && mv '$W'/v5/$0_$1_$2.tmp.npz '$W'/v5/$0_$1_$2.npz' 2>&1
echo ALLDONE
