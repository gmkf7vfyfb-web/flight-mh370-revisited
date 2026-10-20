# usage: bash truth_eof_pool.sh CASE THREADS [CHILDREN]  -> cases/case-CASE/truth-eof/ : the end-of-flight production recipe flown for EVERY accepted candidate (S2)
# Candidate hand-offs are extracted from the pool's per-chunk tars into cases/case-CASE/truth-handoff/seed-N/handoff-m0011/ (kept: make_synth and pick_flight read them).
# The working copy of each header drops the per-replicate evidence lines so that one terminal run accepts all seeds (the stage uses only stop.unix_s; main.rs compares whole headers).
set -u; . $HOME/mh370/e2e/env.sh; CASE=$1; TH=${2:-40}; CHN=${3:-64}; D=$E2E/cases/case-$CASE; cd "$ENG"
RT=$D/truth-eof-rt; rm -rf $RT $D/truth-handoff; mkdir -p $RT/prior $D/truth-handoff
$PY - <<PY
import json, tarfile, os, gzip
C = json.load(open("$D/truth-candidates.json")); by = {}
for c in C["candidates"]: by.setdefault(c["chunk_tar"], []).append(c["seed"])
for t, seeds in by.items():
    with tarfile.open(f"$POOL/{t}") as tf:
        for k in seeds:
            for nm in ("handoff.npy", "handoff.toml.gz"):
                m = tf.getmember(f"./seed-{k}/{nm}"); m.name = nm; tf.extract(m, f"$D/truth-handoff/seed-{k}/handoff-m0011")
            g = f"$D/truth-handoff/seed-{k}/handoff-m0011/handoff.toml"
            txt = gzip.open(g + ".gz", "rt").read(); os.remove(g + ".gz"); open(g, "w").write(txt)
            os.makedirs(f"$RT/prior/seed-{k}", exist_ok=True)
            open(f"$RT/prior/seed-{k}/handoff.toml", "w").write("\n".join(l for l in txt.split("\n") if not l.startswith(("log_evidence", "mode_probability"))))
            os.symlink(f"$D/truth-handoff/seed-{k}/handoff-m0011/handoff.npy", f"$RT/prior/seed-{k}/handoff.npy")
print("extracted", sum(len(v) for v in by.values()), "candidate hand-offs from", len(by), "chunk tars")
PY
SEEDS=$($PY -c "import json;print(','.join(str(c['seed']) for c in json.load(open('$D/truth-candidates.json'))['candidates']))")
printf 'seeds = [%s]\n' $SEEDS > $D/seed-truth.toml
printf '[terminal]\nchildren = %s\n' $CHN > $D/children-truth.toml
rm -rf $D/truth-eof; t0=$(date +%s)
RAYON_NUM_THREADS=$TH $BIN terminal $RT $CHAIN_WP $D/truthgen.toml $EOF_A $D/seed-truth.toml $EOF_EXTRA $EOF_RJ $D/children-truth.toml $D/truth-eof > $D/truth-eof.log 2>&1; rc=$?
echo "truth-eof case $CASE candidates $(echo $SEEDS | tr , '\n' | wc -l) children $CHN rc $rc wall $(( $(date +%s)-t0 )) s"; tail -2 $D/truth-eof.log; exit $rc
