set -u
# RUN J (core), one stratum per job, pinned to git tag run-j. Definition: config/sensitivity/run-j/README.md.
# usage (job command): STRATUM=<smoke|sampler|free|dc|repro|companions> [PREV=<job id to wait for>] sh job-run-j.sh
# Pete pre-approved run J (16 Oct 2026 ~02:15Z) once the final smoke passes.
. "$HOME/.cargo/env"
WORK=$PWD; tl() { echo "$(date -u +%FT%TZ) $*" >> $WORK/timeline.txt; }
J=/home/pete/.claude-science-scratch/.claude-science/jobs; J7=$J/7ba3b89b-e955-45a6-90d5-a28d3164673b; R0=$HOME/mh370
fail() { tl "NO-GO $2"; touch $WORK/NOGO $WORK/DONE; exit $1; }
# 1. wait for the previous stratum job (any outcome), so strata run in a fixed order
if [ -n "${PREV:-}" ]; then
  tl "waiting for previous job $PREV"; n=0
  while [ ! -e $J/$PREV/DONE ]; do sleep 60; n=$((n+1)); [ $n -gt 1800 ] && fail 7 "previous job $PREV not DONE after 30 h"; done
  tl "previous job DONE ($( [ -e $J/$PREV/OK ] && echo OK || echo 'not OK' ))"
fi
# 2. disk: wait until there is room for this stratum before compaction (GiB)
case $STRATUM in sampler) NEED=74;; free) NEED=38;; dc) NEED=20;; repro) NEED=16;; companions) NEED=10;; smoke) NEED=12;; *) fail 2 "unknown stratum $STRATUM";; esac
n=0; while :; do AV=$(df -BG --output=avail $HOME | tail -1 | tr -dc 0-9); [ "$AV" -ge $NEED ] && break
  [ $n -eq 0 ] && tl "disk free ${AV}G < ${NEED}G: waiting for the Mac copy of earlier strata"; sleep 300; n=$((n+1)); [ $n -gt 144 ] && fail 6 "disk ${AV}G < ${NEED}G after 12 h"; done
tl "disk free ${AV}G (need ${NEED}G)"
# 3. heavy lock
exec 9>>$HOME/.mh370-heavy.lock; tl "waiting for heavy lock"; flock -w 36000 9 || fail 8 "heavy lock busy"; tl "heavy lock held"
# 4. source pinned to tag run-j; build and unit tests once per revision
git -C $R0/repo fetch -q --depth 1 origin +refs/tags/run-j:refs/tags/run-j && git -C $R0/repo reset -q --hard run-j || fail 2 "fetch of tag run-j failed"
E="$R0/repo/Claude Science Project Sep 29/engine"; tar xzf $J7/engine-data.tar.gz -C "$E" --exclude='data/._*'
mkdir -p "$E/data/external/fuel-model" && cp $J7/internal-v1.json "$E/data/external/fuel-model/"
cd "$E"; REV=$(git rev-parse --short HEAD); echo "$REV (tag run-j)" > $WORK/REVISION; BIN=$R0/bin-$REV
if [ ! -x $BIN ]; then
  tl "build $REV"; cargo build --release -j 48 > $WORK/build.log 2>&1 || fail 3 "build failed"
  cargo test --release -j 48 -p mh370-flight -p mh370 2>&1 | grep -E "test result|FAILED|panicked" > $WORK/tests.txt || true
  if grep -q FAILED $WORK/tests.txt || ! grep -q "test result: ok" $WORK/tests.txt; then fail 3 "unit tests failed"; fi
  cp target/release/mh370 $BIN
fi
sha256sum $BIN > $WORK/BIN.sha256; tl "binary $BIN"
S=config/sensitivity; X=$S/fuel-fixes; F=$S/early-families; RJ=$S/run-j
# 5. gates: byte-identical to the 15 Oct references, and regress-seed1 equal (every job checks its own binary)
G=$WORK/gates; REF=$R0/gates-2026-10-15; mkdir -p $G
RAYON_NUM_THREADS=44 $BIN config/davey2016.toml $S/handoff-smoke.toml config/smoke.toml $G/tb-B > $G/tb-B.log 2>&1
RAYON_NUM_THREADS=44 $BIN config/davey2016.toml $S/ladder/fuel.toml config/smoke.toml $G/tb-C > $G/tb-C.log 2>&1
RAYON_NUM_THREADS=88 $BIN config/davey2016.toml $S/regress-seed1.toml $G/regress > $G/regress.log 2>&1
python3 - $G $REF > $WORK/gates-report.txt 2>&1 <<'PY'
import sys, os, filecmp, json
G, REF = sys.argv[1:3]; bad = 0
for gate in ("tb-B", "tb-C"):
    a, b = os.path.join(REF, gate), os.path.join(G, gate); n = 0; diff = []
    for dp, dn, fn in os.walk(a):
        for f in sorted(fn):
            if f.endswith(".json") or f.endswith(".log"): continue
            p = os.path.join(dp, f); rel = os.path.relpath(p, a); n += 1; q = os.path.join(b, rel)
            if not (os.path.exists(q) and filecmp.cmp(p, q, shallow=False)): diff.append(rel)
    print("GATE", gate, "files", n, "differ", len(diff), diff); bad += len(diff) + (n == 0)
r = [c["log_evidence"] for c in json.load(open(os.path.join(G, "regress", "summary.json")))["cases"]]
print("REGRESS_SEED1", repr(r[0]), "ref -97.51251428262529"); bad += (repr(r[0]) != "-97.51251428262529")
print("GATES_OK" if bad == 0 else "GATES_FAILED")
PY
grep -q GATES_OK $WORK/gates-report.txt || fail 4 "gates differ from the 15 Oct references"
tl "gates OK"; rm -rf $G
# 6. chains
COMMON="config/davey2016-inmarsat.toml $S/no-exhaustion-prior.toml $X/s1-factor.toml $X/s2-temperature.toml $X/s3-internal.toml $X/s4-ceiling.toml $X/s5-hard-reject.toml $X/s6-tanks.toml $S/reference-snapshots.toml $F/radar-full.toml"
CX="$X/s7-single-engine.toml $X/s8-hold-taper.toml $X/inop-flow-fix.toml"
SPEED=$F/speed-envelope-throughout.toml; LA=$S/handoff-lookahead-d.toml; JX="$RJ/obs-bfo432.toml $RJ/kx.toml"
chain() {  # chain <stratum key> -> config list without output dir; repro stays exactly Davey speeds (no envelope)
  case $1 in
    sampler) echo "$COMMON $CX $SPEED $LA $JX $F/route-sampler.toml $RJ/size-sampler.toml";;
    free) echo "$COMMON $CX $SPEED $LA $JX $F/free.toml $RJ/size-free.toml";;
    dc) echo "$COMMON $CX $SPEED $LA $JX $F/descent-climb.toml $RJ/size-dc.toml";;
    repro) echo "$COMMON $CX $LA $JX $RJ/size-repro.toml";;
    repro-r600) echo "$COMMON $CX $LA $JX $RJ/size-repro-r600.toml $RJ/companion-r600.toml";;
    repro-r600bfo) echo "$COMMON $CX $LA $JX $RJ/size-repro-r600bfo.toml $RJ/companion-r600bfo.toml";;
  esac; }
# 7. manifest
{ echo "run J manifest, job $(basename $WORK), stratum $STRATUM, $(date -u +%FT%TZ)"; echo "revision $REV (tag run-j)"; cat $WORK/BIN.sha256
  for k in sampler free dc repro repro-r600 repro-r600bfo; do echo "chain $k: $(chain $k)"; done
  sha256sum $(chain sampler) $(chain free | awk '{print $(NF-1)}') $F/descent-climb.toml $RJ/* config/davey2016.toml
  sha256sum data/*.csv data/*.json data/variants/satcom-observations-bfo432*.csv data/variants/satellite-ephemeris-inmarsat-r600-1825.csv data/external/fuel-model/*.json $J7/engine-data.tar.gz 2>/dev/null
} > $WORK/MANIFEST.txt
# 8. tiny preflight of the exact chains this job runs
case $STRATUM in smoke) KEYS="sampler free dc repro repro-r600 repro-r600bfo";; companions) KEYS="repro-r600 repro-r600bfo";; *) KEYS=$STRATUM;; esac
PF=$WORK/preflight; mkdir -p $PF
for k in $KEYS; do
  C=$(chain $k); SZ=$(echo $C | awk '{for(i=1;i<=NF;i++) if ($i ~ /size-/) print $i}')
  sed -e 's/^particles_per_mode.*/particles_per_mode = [4000, 2000, 10000, 2000, 10000]/' -e 's/^seeds.*/seeds = [1]/' -e 's/handoff_rows = 100000/handoff_rows = 1000/' $SZ > $RJ/tiny.toml
  C2=$(echo $C | sed "s#$SZ#$SZ $RJ/tiny.toml#"); RAYON_NUM_THREADS=40 $BIN $C2 $PF/$k > $PF/$k.log 2>&1
  [ -f $PF/$k/run.json ] && [ -f $PF/$k/bto-bfo/seed-1/trace.npy ] || { rm -f $RJ/tiny.toml; fail 5 "preflight $k (run.json or trace.npy missing)"; }
  tl "preflight $k GO"
done; rm -f $RJ/tiny.toml; rm -rf $PF/*/
# 9. production
case $STRATUM in smoke) KEYS=sampler;; esac
RUNS=$WORK/runs-j; mkdir -p $RUNS; touch $WORK/STARTED
( while [ ! -f $WORK/DONE ]; do echo "$(date -u +%FT%TZ) df $(df -h --output=avail $HOME | tail -1) mem $(( $(cat /sys/fs/cgroup/memory.current) / 1073741824 ))G" >> $WORK/monitor.txt; sleep 300; done ) &
rcall=0
for k in $KEYS; do
  C=$(chain $k)
  if [ $STRATUM = smoke ]; then sed -e 's/^seeds.*/seeds = [1]/' -e 's/^name.*/name = "run-j-smoke-waypoints"/' $RJ/size-sampler.toml > $RJ/smoke.toml; C=$(echo $C | sed "s#$RJ/size-sampler.toml#$RJ/size-sampler.toml $RJ/smoke.toml#"); fi
  NM=$(for f in $C; do grep -h '^name' $f 2>/dev/null; done | tail -1 | cut -d'"' -f2)
  tl "RUN J $k START $NM (88 threads)"
  RAYON_NUM_THREADS=88 $BIN $C $RUNS/$NM > $RUNS/$NM.log 2>&1; rc=$?
  [ -f $RUNS/$NM/run.json ] || rc="$rc (no run.json)"; tl "RUN J $k END $NM exit $rc"; [ "$rc" = 0 ] || rcall=1
  rm -f $RJ/smoke.toml
  python3 scripts/compact_c.py $RUNS/$NM > $WORK/compact-$NM.log 2>&1; tl "compacted $NM exit $?"
  cp $RUNS/$NM/summary.json $WORK/summary-$NM.json 2>/dev/null; cp $RUNS/$NM.log $WORK/ 2>/dev/null
  (cd $RUNS && find $NM -type f | sort | xargs -d '\n' sha256sum > $WORK/SHA256SUMS-$NM && cp $WORK/SHA256SUMS-$NM $NM/SHA256SUMS); tl "hashed $NM ($(wc -l < $WORK/SHA256SUMS-$NM) files, $(du -sh $RUNS/$NM | cut -f1))"
  ls $RUNS/$NM > /dev/null
done
cat /sys/fs/cgroup/memory.events >> $WORK/timeline.txt || true
[ $rcall = 0 ] && touch $WORK/OK; touch $WORK/DONE; tl "DONE (rc $rcall)"
