#!/bin/bash
# Composer pass 2 (run I): 4 strata x 4 seed-quarters; NPROC single-threaded processes (12 under the heavy lock, or 2 outside it).
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for st in next-i-waypoints next-i-free next-i-descent-climb next-i-repro-radar; do
  for q in 1,3 2,4 5,7 6,8; do echo "$st $q"; done
done | xargs -P ${NPROC:-12} -L 1 sh -c 'python code/compose_quarter.py $0 $1 work/$0-q${1/,/-}.npz > work/log-$0-${1/,/-}.txt 2>&1'
