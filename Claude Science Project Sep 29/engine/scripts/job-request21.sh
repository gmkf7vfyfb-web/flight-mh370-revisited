set -u
# Core request 21 (kappa_x): build from branch core-request21, unit tests, gates B/C against the
# 15 Oct references, regress-seed1, then a smoke (ff-internal chain, 2 seeds) off / on / shift.
. "$HOME/.cargo/env"
WORK=$PWD; tl() { echo "$(date -u +%FT%TZ) $*" >> $WORK/timeline.txt; }
exec 9>>$HOME/.mh370-heavy.lock; tl "waiting for heavy lock"; flock -w 14400 9 || { tl "NO-GO heavy lock busy"; touch DONE; exit 8; }
J=/home/pete/.claude-science-scratch/.claude-science/jobs; J7=$J/7ba3b89b-e955-45a6-90d5-a28d3164673b; R0=$HOME/mh370
git -C $R0/repo fetch -q --depth 1 origin core-request21 && git -C $R0/repo reset -q --hard FETCH_HEAD || { tl "FETCH FAILED"; touch DONE; exit 2; }
E="$R0/repo/Claude Science Project Sep 29/engine"; tar xzf $J7/engine-data.tar.gz -C "$E" --exclude='data/._*'
mkdir -p "$E/data/external/fuel-model" && cp $J7/internal-v1.json "$E/data/external/fuel-model/"
cd "$E"; REV=$(git rev-parse --short HEAD); echo $REV > $WORK/REVISION; tl "build $REV"
cargo build --release -j 48 > $WORK/build.log 2>&1 || { tl "BUILD FAILED"; touch $WORK/DONE; exit 3; }
cargo test --release -j 48 -p mh370-flight -p mh370 > $WORK/tests-full.txt 2>&1; grep -E "test result|FAILED|panicked|extrapolation_factor" $WORK/tests-full.txt > $WORK/tests.txt || true
if grep -q FAILED $WORK/tests.txt || ! grep -q "test result: ok" $WORK/tests.txt; then tl "UNIT TESTS FAILED"; touch $WORK/DONE; exit 3; fi
BIN=$R0/bin-$REV; rm -f $BIN; cp target/release/mh370 $BIN; sha256sum $BIN > $WORK/BIN.sha256; tl "tests ok; binary $BIN"
S=config/sensitivity; G=$WORK/gates; REF=$R0/gates-2026-10-15; mkdir -p $G
RAYON_NUM_THREADS=44 $BIN config/davey2016.toml $S/handoff-smoke.toml config/smoke.toml $G/tb-B > $G/tb-B.log 2>&1; tl "gate B exit $?"
RAYON_NUM_THREADS=44 $BIN config/davey2016.toml $S/ladder/fuel.toml config/smoke.toml $G/tb-C > $G/tb-C.log 2>&1; tl "gate C exit $?"
RAYON_NUM_THREADS=88 $BIN config/davey2016.toml $S/regress-seed1.toml $WORK/regress > $WORK/regress.log 2>&1; tl "regress-seed1 exit $?"
python3 - $G $REF $WORK/regress > $WORK/gates-report.txt 2>&1 <<'PY'
import sys, os, filecmp, json
G, REF, RG = sys.argv[1:4]
for gate in ("tb-B", "tb-C"):
    a, b = os.path.join(REF, gate), os.path.join(G, gate); n = 0; diff = []
    for dp, dn, fn in os.walk(a):
        for f in sorted(fn):
            if f.endswith(".json") or f.endswith(".log"): continue
            p = os.path.join(dp, f); rel = os.path.relpath(p, a); n += 1; q = os.path.join(b, rel)
            if not (os.path.exists(q) and filecmp.cmp(p, q, shallow=False)): diff.append(rel)
    print("GATE", gate, "files", n, "differ", len(diff), diff)
    for c in json.load(open(os.path.join(b, "summary.json"))).get("cases", []): print("LNZ", gate, c.get("case"), repr(c.get("log_evidence")))
for c in json.load(open(os.path.join(RG, "summary.json")))["cases"]: print("REGRESS_SEED1", c["case"], repr(c["log_evidence"]), "ref -97.51251428262529")
PY
tl "gates compared"
FF=$WORK/kx; mkdir -p $FF; F=$S/fuel-feasibility; X=$S/fuel-fixes
for v in off on shift; do
  RAYON_NUM_THREADS=88 $BIN config/davey2016-inmarsat.toml $F/ff-tables.toml $X/s2-temperature.toml $X/s3-internal.toml $X/s6-tanks.toml $X/inop-flow-fix.toml $F/ff-internal.toml $S/request21/kx-$v.toml $FF/kx-$v > $FF/kx-$v.log 2>&1; tl "kx-$v exit $?"
  python3 scripts/fuel_feasibility.py $FF/kx-$v > $WORK/kx-$v-feasibility.json 2> $WORK/kx-$v-feasibility.err; tl "kx-$v analysed exit $?"
  cp $FF/kx-$v/summary.json $WORK/summary-kx-$v.json
  rm -f $FF/kx-$v/bto-bfo/seed-*/routes.npy $FF/kx-$v/bto-bfo/seed-*/trace.npy
done
cat /sys/fs/cgroup/memory.events >> $WORK/timeline.txt || true
touch $WORK/DONE; tl DONE
