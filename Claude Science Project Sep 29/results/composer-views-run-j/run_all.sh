#!/bin/bash
# Composer views run J: every seed of the four production strata and the both-burst supplementary set, 4 processes.
W=/Users/pete/Downloads/mh370-exchange/composer/run-j-views/work/v6; mkdir -p $W
X=/Users/pete/Downloads/mh370-exchange/end-of-flight
jobs=()
for st in run-j-waypoints run-j-free run-j-repro-radar run-j-descent-climb; do
  for d in $X/run-j/$st/seed-*/; do k=$(basename $d); k=${k#seed-}; jobs+=("prod $st $k"); done
done
for d in $X/run-j-both-burst/run-j-waypoints/seed-*/; do k=$(basename $d); k=${k#seed-}; jobs+=("both run-j-waypoints $k"); done
printf '%s\n' "${jobs[@]}" | while read s st k; do f=$W/${s}_${st}_${k}.npz; [ -s $f ] || echo "$s $st $k"; done | \
  xargs -P 5 -L 1 bash -c 'OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python reduce_seed_views.py $0 $1 $2 '$W'/$0_$1_$2.npz.tmp.npz && mv '$W'/$0_$1_$2.npz.tmp.npz '$W'/$0_$1_$2.npz' 2>&1
echo ALLDONE
