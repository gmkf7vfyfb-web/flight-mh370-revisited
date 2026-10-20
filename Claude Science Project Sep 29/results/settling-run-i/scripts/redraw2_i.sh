#!/bin/sh
# Redraw all run I figures (wording: "Holland transient bias added" in short names; stamps say row ESS; wrap by panel width). 1 thread.
WK=/Users/pete/Downloads/mh370-settling-work; cd $WK; X=/Users/pete/Downloads/mh370-exchange/settling/run-i
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 MPLCONFIGDIR=$WK/mpl HOME=$WK/home
EOFC=$(cat eof-smoke-commit.txt); echo "redraw2 start $(date -u +%T)"
for pair in "next-i-waypoints ri_waypoints run-i-waypoints" "next-i-free ri_free run-i-free" "next-i-descent-climb ri_descentclimb run-i-descent-climb" "next-i-repro-radar ri_reproradar run-i-repro-radar"; do
  set -- $pair
  for ext in impacts.f64 elements.f64 draws.npz info.json source.npy; do ln -sf $X/$1/$2_$ext field/$2_$ext; done
  for w in core cause family; do python3 wf_runi.py render $2 $3 9330d4c $EOFC $w > log_redraw2_$2_$w.txt 2>&1 || echo "render $2 $w FAILED"
    for e in png pdf json; do cp settling-seabed-wreckage-$3-$w.$e $X/$1/; done; done
  ( cd $X/$1 && shasum -a 256 $(ls | grep -v '^SHA256SUMS$\|^READY$') > SHA256SUMS && date -u +%Y-%m-%dT%H:%MZ > READY )
  for ext in impacts.f64 elements.f64 draws.npz info.json source.npy; do rm -f field/$2_$ext; done
  echo "redrawn $1 $(date -u +%T)"
done; echo "redraw2 done $(date -u +%T)"
