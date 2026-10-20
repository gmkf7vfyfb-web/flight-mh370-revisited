# A2 shared truth pool: NREP single-particle fuel-only prior replicates in chunks, compacted per chunk. Resumable (a chunk with its npz is skipped).
# usage: bash build_pool.sh POOL_DIR NREP CHUNK THREADS     seeds POOLBASE+1 .. POOLBASE+NREP (POOLBASE 5_000_000; case seeds are CASE*10000+i, CASE < 500)
set -u; . $HOME/mh370/e2e/env.sh; POOL=$1; NREP=$2; CH=$3; TH=$4; BASE=${POOLBASE:-5000000}
mkdir -p $POOL/handoff $POOL/work; cd "$ENG"
[ -f $POOL/obs-dummy.csv ] || $PY $E2E/py/make_dummy.py data/variants/satcom-observations-bfo432.csv data/satellite-ephemeris-inmarsat.csv $POOL/obs-dummy.csv $POOL/eph-dummy.csv > /dev/null
for c0 in $(seq 0 $CH $((NREP-1))); do
  n=$(printf %05d $((c0/CH))); OUT=$POOL/chunk-$n.npz; [ -f $OUT ] && continue
  hi=$(( c0+CH<NREP ? c0+CH : NREP )); SEEDS=$(seq -s, $((BASE+c0+1)) $((BASE+hi))); t0=$(date +%s)
  cat > $POOL/work/truthgen-$n.toml <<T
name = "e2e-pool-$n"
particles_per_mode = [1, 1, 1, 1, 1]
seeds = [$SEEDS]
[[cases]]
id = "prior"
use_bfo = false
use_bto = false
[inputs]
observations = "$POOL/obs-dummy.csv"
ephemeris = "$POOL/eph-dummy.csv"
[sampler]
temper_epochs = []
[output]
residual_samples = 1
handoff_rows = 5
handoff_floor = 1
route_samples = 1
T
  rm -rf $POOL/work/chunk-$n
  RAYON_NUM_THREADS=$TH $BIN $CHAIN_WP $POOL/work/truthgen-$n.toml $POOL/work/chunk-$n > $POOL/work/chunk-$n.log 2>&1; rc=$?
  [ $rc = 0 ] || { tl "pool chunk $n engine rc $rc"; tail -3 $POOL/work/chunk-$n.log; exit 5; }
  (cd $E2E && $PY py/compact_chunk.py $POOL/work/chunk-$n $OUT.tmp.npz $POOL/obs-dummy.csv $POOL/eph-dummy.csv $POOL) >> $POOL/work/chunk-$n.log 2>&1 || { tl "pool chunk $n compact failed"; tail -3 $POOL/work/chunk-$n.log; exit 5; }
  mv $OUT.tmp.npz $OUT; rm -rf $POOL/work/chunk-$n
  tl "pool chunk $n done ($hi/$NREP) $(( $(date +%s)-t0 )) s; $(tail -1 $POOL/work/chunk-$n.log | cut -c1-120); pool $(du -sh $POOL | cut -f1); disk free $(df -h --output=avail $HOME | tail -1)"
done
cp $POOL/work/truthgen-00000.toml $POOL/truthgen-template.toml
echo "NREP=$NREP CHUNK=$CH BASE=$BASE chunks=$(ls $POOL/chunk-*.npz | wc -l) handoff_seeds=$(ls $POOL/handoff | wc -l) $(date -u +%FT%TZ)" > $POOL/COMPLETE; tl "pool complete: $(cat $POOL/COMPLETE)"
