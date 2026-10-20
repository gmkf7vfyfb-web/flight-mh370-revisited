set -u
SM=$1; EN=$2; cd "$EN"
S=config/sensitivity; F=$S/early-families; X=$S/fuel-fixes
COMMON="config/davey2016-inmarsat.toml $S/no-exhaustion-prior.toml $X/s1-factor.toml $X/s2-temperature.toml $X/s3-internal.toml $X/s4-ceiling.toml $X/s5-hard-reject.toml $X/s6-tanks.toml $S/reference-snapshots.toml $F/radar-full.toml"
CX="$X/s7-single-engine.toml $X/s8-hold-taper.toml $X/inop-flow-fix.toml"
for fx in ANOKO XE15 XE30 XW15; do
  t0=$(date +%s)
  RAYON_NUM_THREADS=2 OMP_NUM_THREADS=2 $SM/mh370-core-local $COMMON $CX $F/waypoints.toml $SM/cfg/a-$fx.toml $SM/runs/a-$fx > $SM/runs/a-$fx.log 2>&1
  echo "$(date -u +%FT%TZ) a-$fx exit $? $(( $(date +%s)-t0 ))s" >> $SM/runs/smoke.log
done
