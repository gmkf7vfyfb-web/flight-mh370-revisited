set -u
# Core request 20 Phase 1 smoke (Pete GO 15 Oct 2026). One deskstar job under the deskstar heavy lock.
# See engine/config/sensitivity/request20-smoke/README.md. Seeds 1 and 2, repro-radar size, production 100k rows.
. "$HOME/.cargo/env"
WORK=$PWD; tl() { echo "$(date -u +%FT%TZ) $*" >> $WORK/timeline.txt; }
fin() { touch $WORK/DONE; tl "DONE ($1)"; exit $1; }
exec 9>>$HOME/.mh370-heavy.lock; tl "waiting for heavy lock"; flock -w 5400 9 || { tl "NO-GO heavy lock busy"; fin 8; }
tl "heavy lock held"
AV=$(df -BG --output=avail $HOME | tail -1 | tr -dc 0-9); tl "disk free ${AV}G"; [ "$AV" -ge 12 ] || { tl "NO-GO disk (need 12G)"; fin 6; }
J=/home/pete/.claude-science-scratch/.claude-science/jobs; J7=$J/7ba3b89b-e955-45a6-90d5-a28d3164673b; R0=$HOME/mh370
git -C $R0/repo fetch -q --depth 1 origin claude-science-sep29 && git -C $R0/repo reset -q --hard FETCH_HEAD || { tl "FETCH FAILED"; fin 2; }
E="$R0/repo/Claude Science Project Sep 29/engine"; tar xzf $J7/engine-data.tar.gz -C "$E" --exclude='data/._*'
mkdir -p "$E/data/external/fuel-model" && cp $J7/internal-v1.json "$E/data/external/fuel-model/"
cd "$E"; REV=$(git rev-parse --short HEAD); echo $REV > $WORK/REVISION; tl "build $REV"
cargo build --release -j 48 > $WORK/build.log 2>&1 || { tl "BUILD FAILED"; fin 3; }
cargo test --release -j 48 -p mh370-flight -p mh370 2>&1 | grep -E "test result|FAILED|panicked" > $WORK/tests.txt || true
if grep -q FAILED $WORK/tests.txt || ! grep -q "test result: ok" $WORK/tests.txt; then tl "UNIT TESTS FAILED"; fin 3; fi
BIN=$R0/bin-$REV; rm -f $BIN; cp target/release/mh370 $BIN; sha256sum $BIN > $WORK/BIN.sha256; tl "tests ok; binary $BIN"
( while [ ! -f $WORK/DONE ]; do echo "$(date -u +%FT%TZ) df $(df -h --output=avail $HOME | tail -1) mem $(( $(cat /sys/fs/cgroup/memory.current) / 1073741824 ))G" >> $WORK/monitor.txt; sleep 120; done ) &
S=config/sensitivity; X=$S/fuel-fixes; F=$S/early-families; Q=$S/request20-smoke; EF=hypotheses/end-of-flight; PY="python3 scripts/r20_smoke.py"
# ---- gates B and C against the 15 Oct references (the g_index key is off in both)
G=$WORK/gates; REF=$R0/gates-2026-10-15
RAYON_NUM_THREADS=6 $BIN config/davey2016.toml $S/handoff-smoke.toml config/smoke.toml $G/tb-B > $WORK/gate-B.log 2>&1
RAYON_NUM_THREADS=6 $BIN config/davey2016.toml $S/ladder/fuel.toml config/smoke.toml $G/tb-C > $WORK/gate-C.log 2>&1
python3 - $G $REF > $WORK/gates-vs-ref.txt <<'PY'
import sys, os, filecmp
G, R = sys.argv[1:3]; bad = 0
for g in ("tb-B", "tb-C"):
    n = 0
    for dp, dn, fn in os.walk(os.path.join(R, g)):
        for f in fn:
            if f.endswith((".json", ".log")): continue
            p = os.path.join(dp, f); q = os.path.join(G, g, os.path.relpath(p, os.path.join(R, g))); n += 1
            if not (os.path.exists(q) and filecmp.cmp(p, q, shallow=False)): bad += 1; print("DIFF", g, os.path.relpath(p, R))
    print("GATE", g, "files", n)
print("GATES_DIFF", bad)
PY
grep -q "GATES_DIFF 0" $WORK/gates-vs-ref.txt || { tl "NO-GO gates B/C differ from references"; fin 4; }
tl "gates B and C byte-identical to the 15 Oct references"; rm -rf $G
CHAIN="config/davey2016-inmarsat.toml $S/no-exhaustion-prior.toml $X/s1-factor.toml $X/s2-temperature.toml $X/s3-internal.toml $X/s4-ceiling.toml $X/s5-hard-reject.toml $X/s6-tanks.toml $S/reference-snapshots.toml $F/radar-full.toml $X/s7-single-engine.toml $X/s8-hold-taper.toml $X/inop-flow-fix.toml $Q/smoke-base.toml"
EOFC="$EF/smoke/snapshot-m0011.toml $EF/smoke/terminal.toml $EF/full/reference-289.toml $EF/full/descent-idle-floor.toml"
EXTRA="$EF/smoke/v2-broad.toml $EF/full/family-b-ditching.toml $EF/full/residual-bank-boeing.toml $EF/smoke/trim-at-loss.toml $EF/full/pushover.toml $EF/full/boeing-sequence.toml $EF/full/b-late-onset-proposal.toml $EF/full/holland-estimable.toml $EF/full/a1-aimed-pitchdown.toml $EF/full/piloted-turns.toml $EF/full/run-i.toml $EF/smoke/within-parent-unnormalised.toml"
echo "CHAIN $CHAIN" > $WORK/chains.txt; echo "EOF $EOFC $EXTRA" >> $WORK/chains.txt
GD=$WORK/g; mkdir -p $GD; sed "s|G_DIR|$GD|" $Q/pass2-template.toml > $WORK/pass2.toml
NPM=500000,250000,1250000,250000,1250000; T=88
for k in 1 2; do
  printf 'seeds = [%d]\n' $k > $WORK/seed-$k.toml; ps=$((1000+k)); printf 'seeds = [%d]\n' $ps > $WORK/pseed-$k.toml
  RAYON_NUM_THREADS=$T $BIN $CHAIN $Q/pass1.toml $WORK/seed-$k.toml $WORK/p1-$k > $WORK/p1-$k.log 2>&1; tl "seed $k pass1 exit $?"
  # Pilots in chunks of 100,000 distinct parents (one pilot run of 500k x 32 descents would exceed the 36 GiB cap).
  $PY dedupe_chunks $WORK/p1-$k/bto-bfo/seed-$k/handoff-m0011 $WORK/pin-$k seed-$ps 100000 > $WORK/dedupe-$k.json 2>&1; tl "seed $k dedupe exit $? $(tail -1 $WORK/dedupe-$k.json)"
  PARTS=""
  for CD in $(ls -d $WORK/pin-$k/c* | sort -V); do c=$(basename $CD)
    RAYON_NUM_THREADS=$T $BIN terminal $CD $CHAIN $EOFC $EXTRA $WORK/pseed-$k.toml $WORK/pilot-$k-$c > $WORK/pilot-$k-$c.log 2>&1; rc=$?
    $PY graw $WORK/pilot-$k-$c $ps $CD/bto-bfo/seed-$ps/map.json $WORK/graw-$k-$c.json > $WORK/graw-$k-$c.err 2>&1; tl "seed $k pilots $c exit $rc, graw exit $? ($(tail -1 $WORK/pilot-$k-$c.log)); peak $(( $(cat /sys/fs/cgroup/memory.peak 2>/dev/null || echo 0) / 1073741824 ))G"
    cp $WORK/pilot-$k-$c/bto-bfo/seed-$ps/terminal.json $WORK/pilot-terminal-$k-$c.json 2>/dev/null; rm -f $WORK/pilot-$k-$c/bto-bfo/seed-$ps/impacts.npy
    PARTS="$PARTS${PARTS:+,}$WORK/graw-$k-$c.json"
  done
  $PY gmerge $PARTS $NPM $GD $k > $WORK/g-$k.log 2>&1; tl "seed $k g merged exit $?"; rm -rf $WORK/pin-$k; gzip -f $WORK/graw-$k-*.json
  RAYON_NUM_THREADS=$T $BIN $CHAIN $Q/pass0.toml $WORK/seed-$k.toml $WORK/p0-$k > $WORK/p0-$k.log 2>&1; tl "seed $k pass0 exit $?"
  RAYON_NUM_THREADS=$T $BIN $CHAIN $WORK/pass2.toml $WORK/seed-$k.toml $WORK/p2-$k > $WORK/p2-$k.log 2>&1; tl "seed $k pass2 exit $?"
  for p in 0 1 2; do echo "pass$p $(sha256sum $WORK/p$p-$k/bto-bfo/seed-$k/final.npy | cut -c1-64)" >> $WORK/filter-identity-$k.txt; done
  python3 -c "import json;d=json.load(open('$WORK/p2-$k/bto-bfo/seed-$k/diagnostics.json'));print(json.dumps([m.get('handoff_lookahead') for m in d['modes']]))" > $WORK/la-diag-$k.json 2>&1
  for p in 0 2; do
    RT=$WORK/sin$p-$k/bto-bfo/seed-$k; mkdir -p $RT; H=$WORK/p$p-$k/bto-bfo/seed-$k/handoff-m0011; ln -sf $H/handoff.toml $RT/handoff.toml; ln -sf $H/handoff.npy $RT/handoff.npy
    RAYON_NUM_THREADS=$T $BIN terminal $WORK/sin$p-$k $CHAIN $EOFC $EXTRA $WORK/seed-$k.toml $WORK/s$p-$k > $WORK/s$p-$k.log 2>&1; tl "seed $k score pass$p exit $?"
    $PY score $WORK/s$p-$k $k $H pass$p > $WORK/score-pass$p-$k.json 2> $WORK/score-pass$p-$k.err; tl "seed $k scored pass$p exit $?"
    cp $WORK/s$p-$k/bto-bfo/seed-$k/terminal.json $WORK/terminal-pass$p-$k.json 2>/dev/null; rm -f $WORK/s$p-$k/bto-bfo/seed-$k/impacts.npy
  done
  $PY prior $WORK/p0-$k/bto-bfo/seed-$k/handoff-m0011 $WORK/p2-$k/bto-bfo/seed-$k/handoff-m0011 > $WORK/prior-$k.json 2>&1; tl "seed $k prior exit $?"
  rm -rf $WORK/p1-$k/bto-bfo/seed-$k/handoff-m0011; for p in 0 1 2; do rm -f $WORK/p$p-$k/bto-bfo/seed-$k/final.npy $WORK/p$p-$k/bto-bfo/seed-$k/routes.npy; done
  tl "seed $k done; disk $(df -h --output=avail $HOME | tail -1)"
done
cd $WORK && tar czf r20-small.tar.gz *.json *.txt *.log g/g-summary-*.json 2>/dev/null; tl "packed"
cat /sys/fs/cgroup/memory.events >> $WORK/timeline.txt; fin 0
