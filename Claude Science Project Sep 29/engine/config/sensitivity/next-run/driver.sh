#!/bin/bash
# The next large core run (Pete's pre-approval, 10 Oct 2026): four strata, seeds 1-4, every fix in.
# usage: driver.sh <binary> <size: local|server> <runs dir> [strata...]   (run from engine/)
# Each stratum is its own invocation; a finished stratum (run.json present) is skipped.
BIN=$1; SIZE=$2; RUNS=$3; shift 3
STRATA=${*:-"repro free routes dc"}
S=config/sensitivity; F=$S/early-families; X=$S/fuel-fixes; R=$S/next-run
L=$RUNS/next-run-driver.log
mkdir -p $RUNS
COMMON="config/davey2016-inmarsat.toml $S/no-exhaustion-prior.toml $X/s1-factor.toml $X/s2-temperature.toml $X/s3-internal.toml $X/s4-ceiling.toml $X/s5-hard-reject.toml $X/s6-tanks.toml $S/reference-snapshots.toml $F/radar-full.toml"
for s in $STRATA; do
  case $s in
    repro) fam="" ;;
    free) fam=$F/free.toml ;;
    routes) fam=$F/waypoints.toml ;;
    dc) fam=$F/descent-climb.toml ;;
    *) echo "unknown stratum $s"; exit 2 ;;
  esac
  name=$(grep '^name' $R/$SIZE-$s.toml | cut -d'"' -f2)
  if [ -f $RUNS/$name/run.json ]; then echo "$(date -u +%FT%TZ) skip $name (done)" >> $L; continue; fi
  rm -rf $RUNS/$name
  echo "$(date -u +%FT%TZ) start $name ($SIZE) threads=${RAYON_NUM_THREADS:-all}" >> $L
  $BIN $COMMON $fam $R/$SIZE-$s.toml $RUNS/$name > $RUNS/$name.log 2>&1
  echo "$(date -u +%FT%TZ) end $name exit $?" >> $L
done
echo "$(date -u +%FT%TZ) DONE $STRATA" >> $L
