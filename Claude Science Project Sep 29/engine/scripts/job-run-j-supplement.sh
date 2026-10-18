set -u
# RUN-J NORTHERN SUPPLEMENT (core, 18 Oct 2026; Pete approved incl. the run, architecture.md 2026-10-18 00:41Z).
# Design: results/run-j-supplement/DESIGN.md. usage (job command): REV=<commit> [SEEDS="1001 ... 1016"] [CAP_H=9.3] sh job-run-j-supplement.sh
# Inputs in the job dir: ref-run-j-waypoints-seed1.sha256, ref-run-j-repro-radar-seed1.sha256 (run J seed-1 hashes).
# Order: wait for the drift arc-latitude chain to finish (ALL-DONE; it takes the heavy lock per leg, so the lock
# alone would pre-empt it) -> heavy lock -> build/tests at REV -> gates B/C + regress-seed1 -> FLAG-OFF run J repro
# seed 1 byte-identical -> FLAG-ON run J waypoints seed 1: every normal output byte-identical + a supplement drawn
# from run J's own population -> supplement seeds, one process each, until the wall cap.
. "$HOME/.cargo/env"
WORK=$PWD; T0=$(date +%s); tl() { echo "$(date -u +%FT%TZ) $*" >> $WORK/timeline.txt; }
J=/home/pete/.claude-science-scratch/.claude-science/jobs; J7=$J/7ba3b89b-e955-45a6-90d5-a28d3164673b; R0=$HOME/mh370
fail() { tl "NO-GO $2"; touch $WORK/NOGO $WORK/DONE; exit $1; }
SEEDS=${SEEDS:-"1001 1002 1003 1004 1005 1006 1007 1008 1009 1010 1011 1012 1013 1014 1015 1016"}; CAP_H=${CAP_H:-9.3}
# 1. the drift arc-latitude chain must be finished (do not pre-empt it)
n=0; while ! grep -q ALL-DONE $R0/drift/arclat/chain.log 2>/dev/null; do
  [ $n -eq 0 ] && tl "waiting for the drift arc-latitude chain (chain.log ALL-DONE)"; sleep 120; n=$((n+1)); [ $n -gt 900 ] && fail 7 "drift chain not done after 30 h"; done
tl "drift chain ALL-DONE"; T0=$(date +%s)   # the wall cap counts from here
# 2. heavy lock
exec 9>>$HOME/.mh370-heavy.lock; tl "waiting for heavy lock"; flock -w 36000 9 || fail 8 "heavy lock busy"; tl "heavy lock held"
AV=$(df -BG --output=avail $HOME | tail -1 | tr -dc 0-9); tl "disk free ${AV}G"; [ "$AV" -ge 20 ] || fail 6 "disk ${AV}G < 20G"
# 3. source at REV; build and unit tests
# A worktree of ~/mh370/repo at REV (the shared checkout is not moved); cargo target kept in ~/mh370/target-supp.
git -C $R0/repo fetch -q origin claude-science-sep29 && git -C $R0/repo worktree add -f --detach $WORK/wt $REV > /dev/null 2>&1 || fail 2 "worktree at $REV failed"
export CARGO_TARGET_DIR=$R0/target-supp
E="$WORK/wt/Claude Science Project Sep 29/engine"; tar xzf $J7/engine-data.tar.gz -C "$E" --exclude='data/._*'
mkdir -p "$E/data/external/fuel-model" && cp $J7/internal-v1.json "$E/data/external/fuel-model/"
cd "$E"; REV=$(git rev-parse --short HEAD); echo "$REV" > $WORK/REVISION; BIN=$R0/bin-$REV
if [ ! -x $BIN ]; then
  tl "build $REV"; cargo build --release -j 48 > $WORK/build.log 2>&1 || fail 3 "build failed"
  cargo test --release -j 48 -p mh370-flight -p mh370 2>&1 | grep -E "test result|FAILED|panicked" > $WORK/tests.txt || true
  if grep -q FAILED $WORK/tests.txt || ! grep -q "test result: ok" $WORK/tests.txt; then fail 3 "unit tests failed"; fi
  cp $CARGO_TARGET_DIR/release/mh370 $BIN
fi
sha256sum $BIN > $WORK/BIN.sha256; tl "binary $BIN"
S=config/sensitivity; X=$S/fuel-fixes; F=$S/early-families; RJ=$S/run-j; SU=$S/run-j-supplement
# 4. gates (as job-run-j.sh)
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
COMMON="config/davey2016-inmarsat.toml $S/no-exhaustion-prior.toml $X/s1-factor.toml $X/s2-temperature.toml $X/s3-internal.toml $X/s4-ceiling.toml $X/s5-hard-reject.toml $X/s6-tanks.toml $S/reference-snapshots.toml $F/radar-full.toml"
CX="$X/s7-single-engine.toml $X/s8-hold-taper.toml $X/inop-flow-fix.toml"
SPEED=$F/speed-envelope-throughout.toml; LA=$S/handoff-lookahead-d.toml; JX="$RJ/obs-bfo432.toml $RJ/kx.toml"
SAMPLER="$COMMON $CX $SPEED $LA $JX $F/route-sampler.toml $RJ/size-sampler.toml"
REPRO="$COMMON $CX $LA $JX $RJ/size-repro.toml"
{ echo "run-J supplement manifest, job $(basename $WORK), $(date -u +%FT%TZ)"; echo "revision $REV"; cat $WORK/BIN.sha256
  echo "chain sampler: $SAMPLER"; echo "chain repro: $REPRO"; echo "supplement: $SU/size-north.toml $SU/supplement.toml (seeds $SEEDS)"
  sha256sum $SAMPLER $F/descent-climb.toml $RJ/* $SU/* config/davey2016.toml
  sha256sum data/*.csv data/*.json data/variants/satcom-observations-bfo432*.csv data/external/fuel-model/*.json $J7/engine-data.tar.gz 2>/dev/null
} > $WORK/MANIFEST.txt
RUNS=$WORK/runs; mkdir -p $RUNS; touch $WORK/STARTED
( while [ ! -f $WORK/DONE ]; do echo "$(date -u +%FT%TZ) df $(df -h --output=avail $HOME | tail -1) mem $(( $(cat /sys/fs/cgroup/memory.current) / 1073741824 ))G" >> $WORK/monitor.txt; sleep 300; done ) &
# compare a compacted seed dir with run J seed-1 reference hashes (handoff.toml compared uncompressed)
cmpref() {  # cmpref <seed dir> <ref file> <label>
  python3 - "$1" "$2" <<'PY' > $WORK/identity-$3.txt 2>&1
import sys, os, gzip, hashlib
d, ref = sys.argv[1:3]; bad = 0; n = 0
for line in open(ref):
    h, rel = line.split(); p = os.path.join(d, rel); n += 1
    if rel.endswith("handoff.toml"): got = hashlib.sha256(gzip.open(p + ".gz").read()).hexdigest() if os.path.exists(p + ".gz") else "missing"
    else: got = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "missing"
    ok = got == h; bad += not ok; print("SAME" if ok else "DIFFERS", rel)
print(f"IDENTITY files {n} differ {bad}"); print("IDENTICAL" if bad == 0 and n > 0 else "NOT_IDENTICAL")
PY
  grep -q "^IDENTICAL" $WORK/identity-$3.txt; }
one() {  # one <label> <chain> -> runs $RUNS/<label>, compacts, hashes
  tl "RUN $1 START"; RAYON_NUM_THREADS=88 $BIN $2 $RUNS/$1 > $RUNS/$1.log 2>&1; rc=$?
  [ -f $RUNS/$1/run.json ] || rc="$rc (no run.json)"; tl "RUN $1 END exit $rc"
  python3 scripts/compact_c.py $RUNS/$1 > $WORK/compact-$1.log 2>&1; tl "compacted $1 exit $?"
  (cd $RUNS && find $1 -type f | sort | xargs -d '\n' sha256sum > $1/SHA256SUMS); [ "$rc" = 0 ]; }
# 5. FLAG OFF: run J repro seed 1 at this revision must reproduce run J bit-exactly
printf 'name = "flagoff-repro-seed1"\nseeds = [1]\n' > $SU/tmp-flagoff.toml
one flagoff-repro-seed1 "$REPRO $SU/tmp-flagoff.toml" || fail 5 "flag-off repro seed 1 failed"
cmpref $RUNS/flagoff-repro-seed1/bto-bfo/seed-1 $WORK/ref-run-j-repro-radar-seed1.sha256 flagoff-repro || fail 5 "FLAG OFF: repro seed 1 is NOT byte-identical to run J"
[ -d $RUNS/flagoff-repro-seed1/bto-bfo/seed-1/handoff-m0011-supplement ] && fail 5 "FLAG OFF wrote a supplement"
tl "flag-off repro seed 1 IDENTICAL to run J"; rm -f $SU/tmp-flagoff.toml
# 6. FLAG ON on run J waypoints seed 1: every normal output identical; the supplement comes from run J's own population
one run-j-supplement-validate "$SAMPLER $SU/supplement.toml $SU/validate-seed1.toml" || fail 5 "flag-on waypoints seed 1 failed"
cmpref $RUNS/run-j-supplement-validate/bto-bfo/seed-1 $WORK/ref-run-j-waypoints-seed1.sha256 flagon-waypoints || fail 5 "FLAG ON: normal outputs of waypoints seed 1 are NOT byte-identical to run J"
[ -f $RUNS/run-j-supplement-validate/bto-bfo/seed-1/handoff-m0011-supplement/supplement.json ] || fail 5 "FLAG ON wrote no supplement"
tl "flag-on waypoints seed 1: normal outputs IDENTICAL to run J; supplement written"; touch $WORK/VALIDATED
# 7. supplement seeds, one process each, until the wall cap (a seed is started only if it should end inside the cap)
last=0
for s in $SEEDS; do
  el=$(( $(date +%s) - T0 )); est=${last:-0}; [ $est -eq 0 ] && est=1500
  if [ $(( el + est )) -gt $(python3 -c "print(int($CAP_H*3600))") ]; then tl "wall cap: not starting seed $s (elapsed ${el}s, last seed ${est}s)"; break; fi
  AV=$(df -BG --output=avail $HOME | tail -1 | tr -dc 0-9); [ "$AV" -ge 12 ] || { tl "disk ${AV}G < 12G: stopping before seed $s"; break; }
  printf 'seeds = [%s]\n' $s > $SU/tmp-seed.toml
  t1=$(date +%s); one north-$s "$SAMPLER $SU/size-north.toml $SU/supplement.toml $SU/tmp-seed.toml" || tl "seed $s FAILED"
  last=$(( $(date +%s) - t1 )); echo $s >> $WORK/SEEDS_DONE; rm -f $SU/tmp-seed.toml
done
cat /sys/fs/cgroup/memory.events >> $WORK/timeline.txt || true
rm -f $SU/tmp-*.toml; cd $WORK; git -C $R0/repo worktree remove --force $WORK/wt 2>/dev/null; git -C $R0/repo worktree prune
touch $WORK/OK $WORK/DONE; tl "DONE"
