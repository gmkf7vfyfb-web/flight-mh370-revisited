# usage: bash truth_core.sh CASE NREP THREADS  -> $E2E/cases/case-CASE/truth-core/
set -u; . $HOME/mh370/e2e/env.sh; CASE=$1; NREP=$2; TH=${3:-8}; VAL=${4:-false}; OUTN=${5:-truth-core}
D=$E2E/cases/case-$CASE; mkdir -p $D; cd "$ENG"
$PY $E2E/py/make_dummy.py data/variants/satcom-observations-bfo432.csv data/satellite-ephemeris-inmarsat.csv $D/obs-dummy.csv $D/eph-dummy.csv > /dev/null
CH=${CHUNK:-500}; rm -rf $D/$OUTN; mkdir -p $D/$OUTN/prior; t0=$(date +%s)
for c0 in $(seq 0 $CH $((NREP-1))); do
SEEDS=$(seq -s, $((CASE*10000+c0+1)) $((CASE*10000+(c0+CH<NREP ? c0+CH : NREP))))
cat > $D/truthgen.toml <<T
name = "e2e-truth-$CASE"
particles_per_mode = [1, 1, 1, 1, 1]
seeds = [$SEEDS]
[[cases]]
id = "prior"
use_bfo = $VAL
use_bto = $VAL
[inputs]
observations = "$D/obs-dummy.csv"
ephemeris = "$D/eph-dummy.csv"
[sampler]
temper_epochs = []
[output]
residual_samples = 1
handoff_rows = 5
handoff_floor = 1
route_samples = 1
T
RAYON_NUM_THREADS=$TH $BIN $CHAIN_WP $D/truthgen.toml $D/chunk > $D/$OUTN.log 2>&1; rc=$?
for sd in $D/chunk/prior/seed-*; do mkdir -p $D/$OUTN/prior/$(basename $sd); mv $sd/handoff-m0011 $sd/residuals $D/$OUTN/prior/$(basename $sd)/; done
rm -rf $D/chunk
done
echo "truth-core case $CASE rc $rc wall $(( $(date +%s)-t0 )) s"; tail -1 $D/$OUTN.log
