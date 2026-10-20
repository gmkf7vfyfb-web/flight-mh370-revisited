set -u
# Core request 20 smoke, follow-up diagnostic: parent- or descent-limited? Re-runs pass0 (uniform 100k m0011 rows,
# deterministic, so identical to the smoke's) and its end-of-flight scoring for seeds 1-2, then r20_smoke.py split.
. "$HOME/.cargo/env"
WORK=$PWD; tl() { echo "$(date -u +%FT%TZ) $*" >> $WORK/timeline.txt; }
fin() { touch $WORK/DONE; tl "DONE ($1)"; exit $1; }
exec 9>>$HOME/.mh370-heavy.lock; tl "waiting for heavy lock"; flock -w 5400 9 || { tl "NO-GO heavy lock busy"; fin 8; }
J=/home/pete/.claude-science-scratch/.claude-science/jobs; J7=$J/7ba3b89b-e955-45a6-90d5-a28d3164673b; R0=$HOME/mh370
git -C $R0/repo fetch -q --depth 1 origin claude-science-sep29 && git -C $R0/repo reset -q --hard FETCH_HEAD || { tl "FETCH FAILED"; fin 2; }
E="$R0/repo/Claude Science Project Sep 29/engine"; tar xzf $J7/engine-data.tar.gz -C "$E" --exclude='data/._*'
mkdir -p "$E/data/external/fuel-model" && cp $J7/internal-v1.json "$E/data/external/fuel-model/"
cd "$E"; REV=$(git rev-parse --short HEAD); echo $REV > $WORK/REVISION
# The engine source must equal the smoke's (e069ff8): rebuild only if the binary for this revision is absent.
BIN=$R0/bin-$REV; [ -x $BIN ] || { cargo build --release -j 48 > $WORK/build.log 2>&1 && cp target/release/mh370 $BIN || { tl "BUILD FAILED"; fin 3; }; }
sha256sum $BIN > $WORK/BIN.sha256; tl "binary $BIN"
S=config/sensitivity; X=$S/fuel-fixes; F=$S/early-families; Q=$S/request20-smoke; EF=hypotheses/end-of-flight; PY="python3 scripts/r20_smoke.py"
CHAIN="config/davey2016-inmarsat.toml $S/no-exhaustion-prior.toml $X/s1-factor.toml $X/s2-temperature.toml $X/s3-internal.toml $X/s4-ceiling.toml $X/s5-hard-reject.toml $X/s6-tanks.toml $S/reference-snapshots.toml $F/radar-full.toml $X/s7-single-engine.toml $X/s8-hold-taper.toml $X/inop-flow-fix.toml $Q/smoke-base.toml"
EOFC="$EF/smoke/snapshot-m0011.toml $EF/smoke/terminal.toml $EF/full/reference-289.toml $EF/full/descent-idle-floor.toml"
EXTRA="$EF/smoke/v2-broad.toml $EF/full/family-b-ditching.toml $EF/full/residual-bank-boeing.toml $EF/smoke/trim-at-loss.toml $EF/full/pushover.toml $EF/full/boeing-sequence.toml $EF/full/b-late-onset-proposal.toml $EF/full/holland-estimable.toml $EF/full/a1-aimed-pitchdown.toml $EF/full/piloted-turns.toml $EF/full/run-i.toml $EF/smoke/within-parent-unnormalised.toml"
for k in 1 2; do
  printf 'seeds = [%d]\n' $k > $WORK/seed-$k.toml
  RAYON_NUM_THREADS=88 $BIN $CHAIN $Q/pass0.toml $WORK/seed-$k.toml $WORK/p0-$k > $WORK/p0-$k.log 2>&1; tl "seed $k pass0 exit $?"
  sha256sum $WORK/p0-$k/bto-bfo/seed-$k/final.npy > $WORK/final-sha-$k.txt
  RT=$WORK/sin0-$k/bto-bfo/seed-$k; mkdir -p $RT; H=$WORK/p0-$k/bto-bfo/seed-$k/handoff-m0011; ln -sf $H/handoff.toml $RT/handoff.toml; ln -sf $H/handoff.npy $RT/handoff.npy
  RAYON_NUM_THREADS=88 $BIN terminal $WORK/sin0-$k $CHAIN $EOFC $EXTRA $WORK/seed-$k.toml $WORK/s0-$k > $WORK/s0-$k.log 2>&1; tl "seed $k score exit $?"
  $PY score $WORK/s0-$k $k $H pass0 > $WORK/score-pass0-$k.json 2>&1
  $PY split $WORK/s0-$k $k > $WORK/split-$k.json 2> $WORK/split-$k.err; tl "seed $k split exit $?"
  rm -rf $WORK/p0-$k/bto-bfo/seed-$k/final.npy $WORK/p0-$k/bto-bfo/seed-$k/routes.npy $WORK/s0-$k/bto-bfo/seed-$k/impacts.npy
done
fin 0
