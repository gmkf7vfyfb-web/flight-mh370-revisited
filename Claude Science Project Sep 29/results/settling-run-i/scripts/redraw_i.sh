#!/bin/sh
# Redraw waypoints (title overrun; histograms re-made by a 1-thread re-prep under a scratch tag) and free (row spacing) after run_i.sh ends.
WK=/Users/pete/Downloads/mh370-settling-work; cd $WK; X=/Users/pete/Downloads/mh370-exchange/settling/run-i
E=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i; C=/Users/pete/Downloads/mh370-exchange/core/run-i
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 MPLCONFIGDIR=$WK/mpl HOME=$WK/home
while [ ! -e $X/READY ]; do sleep 60; done; echo "redraw start $(date -u +%T)"
EOFC=$(cat eof-smoke-commit.txt)
python3 wf_runi.py prep "$E/next-i-waypoints" "$C/next-i-waypoints" ri_wpre > log_redraw_wpre.txt 2>&1 || { echo "re-prep FAILED"; exit 1; }
for f in field/ri_wpre_H_*.npy; do mv $f $(echo $f | sed 's/ri_wpre/ri_waypoints/'); done; rm -f field/ri_wpre_*
for pair in "next-i-waypoints ri_waypoints run-i-waypoints" "next-i-free ri_free run-i-free"; do
  set -- $pair
  for ext in impacts.f64 elements.f64 draws.npz info.json source.npy; do ln -sf $X/$1/$2_$ext field/$2_$ext; done
  for w in core cause family; do python3 wf_runi.py render $2 $3 9330d4c $EOFC $w > log_redraw_$2_$w.txt 2>&1 || echo "render $2 $w FAILED"
    for e in png pdf json; do cp settling-seabed-wreckage-$3-$w.$e $X/$1/; done; done
  ( cd $X/$1 && shasum -a 256 $(ls | grep -v '^SHA256SUMS$\|^READY$') > SHA256SUMS && date -u +%Y-%m-%dT%H:%MZ > READY )
  for ext in impacts.f64 elements.f64 draws.npz info.json source.npy; do rm -f field/$2_$ext; done
  echo "redrawn $1 $(date -u +%T)"
done
echo "redraw done $(date -u +%T)"
