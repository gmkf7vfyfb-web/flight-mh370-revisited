# usage: bash truth_eof.sh CASE THREADS -> cases/case-CASE/truth-eof/ (EoF production recipe, children 256 on the truth parent's seed)
set -u; . $HOME/mh370/e2e/env.sh; CASE=$1; TH=${2:-16}; D=$E2E/cases/case-$CASE; cd "$ENG"
SDIR=$($PY -c "import json;print(json.load(open('$D/truth-core.json'))['chosen']['seed_dir'])"); SN=$(basename $SDIR); K=${SN#seed-}
case "$SDIR" in /*) ;; *) SDIR=$E2E/$SDIR;; esac
RT=$D/truth-eof-rt; rm -rf $RT; mkdir -p $RT/prior/$SN; ln -s $SDIR/handoff-m0011/handoff.toml $RT/prior/$SN/handoff.toml; ln -s $SDIR/handoff-m0011/handoff.npy $RT/prior/$SN/handoff.npy
printf 'seeds = [%s]\n' $K > $D/seed-truth.toml
printf '[terminal]\nchildren = 256\n' > $D/children-256.toml
rm -rf $D/truth-eof; t0=$(date +%s)
RAYON_NUM_THREADS=$TH $BIN terminal $RT $CHAIN_WP $D/truthgen.toml $EOF_A $D/seed-truth.toml $EOF_EXTRA $EOF_RJ $D/children-256.toml $D/truth-eof > $D/truth-eof.log 2>&1; rc=$?
echo "truth-eof case $CASE rc $rc wall $(( $(date +%s)-t0 )) s"; tail -3 $D/truth-eof.log; ls $D/truth-eof $D/truth-eof/prior/$SN 2>/dev/null | head
