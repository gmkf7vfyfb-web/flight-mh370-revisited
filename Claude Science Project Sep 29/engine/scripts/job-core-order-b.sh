set -u
# Core order 2026-10-15b, steps 1 and 3, one deskstar job held under the deskstar heavy lock
# (flock on $HOME/.mh370-heavy.lock; deskstar has flock, not lockf). Usage (job command):
#   sh job-core-order-b.sh
# Step 1: gate B and gate C references from an unmodified HEAD build (RAYON_NUM_THREADS=6, the
#   gate convention), a repeat of both at 44 threads (thread-count byte identity), and the
#   regress-seed1 ln Z (davey2016 + regress-seed1, 1 seed x 7M).
# Step 3: fuel feasibility, variants ff-tables and ff-internal (4 seeds x 1.75M), then
#   scripts/fuel_feasibility.py over both and over run I's repro stratum (J/6a2ec01f).
. "$HOME/.cargo/env"
WORK=$PWD; tl() { echo "$(date -u +%FT%TZ) $*" >> $WORK/timeline.txt; }
exec 9>>$HOME/.mh370-heavy.lock
tl "waiting for heavy lock"; flock -w 5400 9 || { tl "NO-GO heavy lock busy 90 min"; touch $WORK/DONE; exit 8; }
tl "heavy lock held"
J=/home/pete/.claude-science-scratch/.claude-science/jobs
J7=$J/7ba3b89b-e955-45a6-90d5-a28d3164673b
R0=$HOME/mh370
git -C $R0/repo fetch -q --depth 1 origin claude-science-sep29 && git -C $R0/repo reset -q --hard FETCH_HEAD || { tl "FETCH FAILED"; touch $WORK/DONE; exit 2; }
E="$R0/repo/Claude Science Project Sep 29/engine"
tar xzf $J7/engine-data.tar.gz -C "$E" --exclude='data/._*'
mkdir -p "$E/data/external/fuel-model" && cp $J7/internal-v1.json "$E/data/external/fuel-model/"
cd "$E"; REV=$(git rev-parse --short HEAD); echo $REV > $WORK/REVISION
echo "crates last changed at $(git log -1 --format=%h -- crates Cargo.toml Cargo.lock 2>/dev/null)" >> $WORK/REVISION
tl "build $REV"
cargo build --release -j 48 > $WORK/build.log 2>&1 || { tl "BUILD FAILED"; touch $WORK/DONE; exit 3; }
cargo test --release -j 48 -p mh370-flight -p mh370 2>&1 | grep -E "test result|FAILED|panicked" > $WORK/tests.txt || true
if grep -q FAILED $WORK/tests.txt || ! grep -q "test result: ok" $WORK/tests.txt; then tl "UNIT TESTS FAILED"; touch $WORK/DONE; exit 3; fi
BIN=$R0/bin-$REV; rm -f $BIN; cp target/release/mh370 $BIN; sha256sum $BIN > $WORK/BIN.sha256; tl "tests ok; binary $BIN"
( while [ ! -f $WORK/DONE ]; do echo "$(date -u +%FT%TZ) df $(df -h --output=avail $HOME | tail -1) mem $(( $(cat /sys/fs/cgroup/memory.current) / 1073741824 ))G" >> $WORK/monitor.txt; sleep 300; done ) &
S=config/sensitivity; G=$WORK/gates; mkdir -p $G
# ---- step 1: gates
for T in 6 44; do
  RAYON_NUM_THREADS=$T $BIN config/davey2016.toml $S/handoff-smoke.toml config/smoke.toml $G/t$T/tb-B > $G/tb-B-t$T.log 2>&1; tl "gate B t$T exit $?"
  RAYON_NUM_THREADS=$T $BIN config/davey2016.toml $S/ladder/fuel.toml config/smoke.toml $G/t$T/tb-C > $G/tb-C-t$T.log 2>&1; tl "gate C t$T exit $?"
done
python3 - $G > $WORK/gates-report.txt 2>&1 <<'PY'
import sys, os, hashlib, filecmp, json
G = sys.argv[1]
for gate in ("tb-B", "tb-C"):
    a, b = os.path.join(G, "t6", gate), os.path.join(G, "t44", gate); files = []; diff = []
    for dp, dn, fn in os.walk(a):
        dn.sort()
        for f in sorted(fn):
            if f.endswith(".json") or f.endswith(".log"): continue
            p = os.path.join(dp, f); rel = os.path.relpath(p, a); files.append(rel)
            q = os.path.join(b, rel)
            if not (os.path.exists(q) and filecmp.cmp(p, q, shallow=False)): diff.append(rel)
            print("SHA256", gate, hashlib.sha256(open(p, "rb").read()).hexdigest(), os.path.getsize(p), rel)
    print("FILES", gate, len(files), "DIFF_t6_vs_t44", len(diff), diff)
    for t in ("t6", "t44"):
        s = json.load(open(os.path.join(G, t, gate, "summary.json")))
        for c in s.get("cases", []):
            print("LNZ", gate, t, c.get("case"), repr(c.get("log_evidence")), [(r.get("seed"), repr(r.get("log_evidence"))) for r in c.get("replicates", [])])
PY
tl "gates compared"
(cd $G/t6 && tar czf $WORK/gates-bc-refs.tar.gz tb-B tb-C) ; mkdir -p $R0/gates-2026-10-15 && cp -r $G/t6/tb-B $G/t6/tb-C $R0/gates-2026-10-15/ && cp $BIN $R0/gates-2026-10-15/; tl "refs packed and kept in $R0/gates-2026-10-15"
RAYON_NUM_THREADS=88 $BIN config/davey2016.toml $S/regress-seed1.toml $WORK/regress > $WORK/regress.log 2>&1; tl "regress-seed1 exit $?"
python3 -c "import json,glob;s=json.load(open(glob.glob('$WORK/regress/summary.json')[0]));[print('REGRESS_SEED1',c['case'],repr(c['log_evidence'])) for c in s['cases']]" >> $WORK/gates-report.txt 2>&1
# ---- step 3: fuel feasibility
F=$S/fuel-feasibility; X=$S/fuel-fixes; FF=$WORK/ff; mkdir -p $FF
AV=$(df -BG --output=avail $HOME | tail -1 | tr -dc 0-9); tl "disk free ${AV}G"; [ "$AV" -ge 8 ] || { tl "NO-GO disk (need 8G)"; touch $WORK/DONE; exit 6; }
RAYON_NUM_THREADS=88 $BIN config/davey2016-inmarsat.toml $F/ff-tables.toml $FF/ff-tables > $FF/ff-tables.log 2>&1; tl "ff-tables exit $?"
RAYON_NUM_THREADS=88 $BIN config/davey2016-inmarsat.toml $F/ff-tables.toml $X/s2-temperature.toml $X/s3-internal.toml $X/s6-tanks.toml $X/inop-flow-fix.toml $F/ff-internal.toml $FF/ff-internal > $FF/ff-internal.log 2>&1; tl "ff-internal exit $?"
for N in ff-tables ff-internal; do python3 scripts/fuel_feasibility.py $FF/$N > $WORK/$N-feasibility.json 2> $WORK/$N-feasibility.err; tl "$N analysed exit $?"; done
python3 scripts/fuel_feasibility.py $J/6a2ec01f-3a06-4810-92bb-b3d4efca768f/runs-i/next-i-repro-radar > $WORK/run-i-repro-feasibility.json 2> $WORK/run-i-repro-feasibility.err; tl "run-i repro analysed exit $?"
cd $FF && tar czf $WORK/ff-small.tar.gz */run.json */summary.json */bto-bfo/seed-*/diagnostics.json *.log; tl "packed small files"
cat /sys/fs/cgroup/memory.events >> $WORK/timeline.txt || true
touch $WORK/DONE; tl "DONE"
