#!/bin/sh
# Settling on end of flight's run C (on .../next-run-c/READY): core set and by-family (ruling 6) prep + settling passes.
# Render is done after reading end of flight's run C note (labels). 2 threads, outside the heavy lock (each step light; run C chain has priority).
set -eu
W=$(pwd); SM2="$W/wt-base/Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke"
ENG="$W/wt-rebase/Claude Science Project Sep 29/engine"; ROOT=/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run-c
EV=""; for i in $(seq 1 45); do EV=$(ls "$ROOT"/summary/family-evidence*.json 2>/dev/null | head -1 || true); [ -n "$EV" ] && break; sleep 60; done
EV_SRC="end of flight's run C family evidence"
if [ -z "$EV" ]; then   # end of flight's own tool, unmodified, over all four strata, with run C core P(family); superseded by end of flight's file
  PC=$(python3 -c "import json; P=json.load(open('/Users/pete/Downloads/mh370-exchange/core/next-run-c/report/early-families-mixture.json'))['P_family']; n={'free':'next-c-free','Davey dynamics + radar':'next-c-repro-radar','descent-climb':'next-c-descent-climb','routes':'next-c-routes'}; print(' '.join(f'{n[k]}={v}' for k,v in P.items()))")
  ( cd "$SM2" && python3 family_evidence.py "$ROOT" "$W/runc_family_evidence_settling.json" $PC ) > "$W/runc_family_evidence_settling.log" 2>&1 && EV="$W/runc_family_evidence_settling.json" && EV_SRC="computed by settling with end of flight's family_evidence.py (EoF tools $(cd "$SM2" && git log -1 --format=%h -- family_evidence.py)); end of flight's own file supersedes"
fi
if [ -z "$EV" ]; then EV="$W/runc_fixed_evidence.json"; python3 - "$EV" <<'PY'
import sys, json
# Run C family evidence not yet published: fixed weights = run C core P(family) (core/next-run-c/report/early-families-mixture.json).
src = "/Users/pete/Downloads/mh370-exchange/core/next-run-c/report/early-families-mixture.json"; P = json.load(open(src))["P_family"]
name = {"free": "next-c-free", "Davey dynamics + radar": "next-c-repro-radar", "descent-climb": "next-c-descent-climb", "routes": "next-c-routes"}
json.dump({"p_core": {name[k]: v for k, v in P.items()}, "mixtures": {}, "source": src,
           "note": "fixed weights only: run C family evidence absent at run time"}, open(sys.argv[1], "w"), indent=1)
PY
fi
echo "evidence: $EV ($EV_SRC)"; echo "$EV_SRC" > "$W/runc_evidence_source.txt"
SEEDS=$(ls -d "$ROOT"/*/seed-*/ | sed -e 's#/$##' -e 's#.*/seed-##' | sort -un | paste -sd, -); echo "seeds: $SEEDS"
export WF_SEEDS="$SEEDS" HOME="$W/scratch-home" CARGO_HOME=/Users/pete/.cargo CARGO_TARGET_DIR="$W/target-wt" PATH="/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH"
settle() { ( cd "$ENG" && RAYON_NUM_THREADS=2 SETTLING_THREADS=2 SETTLING_FIELD_IN="$W/field/$1_impacts.f64" SETTLING_FIELD_OUT="$W/field/$1_elements.f64" \
      cargo test --offline -j 2 --release -p mh370-hypotheses settling::tests::wreckage_field -- --ignored 2>&1 | grep "test result" ); }
python3 wf_standard.py prep "$SM2" "$ROOT" "$EV" nrc
for T in A B; do settle nrc$T; done
WF_FAMILY_MAP=ruling6 python3 wf_family.py prep "$SM2" "$ROOT" "$EV" nrcg
for j in 0 1 2; do settle nrcgF$j; done
echo RUNC_ALLROWS_DONE
# Second version (architecture ruling 20:35 -0600, G-H2): contact speed <= 1.25 VMO = 212 m/s, rest re-weighted; tags nrcS / nrcgS.
WF_SPEED_CAP_MPS=212 python3 wf_standard.py prep "$SM2" "$ROOT" "$EV" nrcS
for T in A B; do settle nrcS$T; done
WF_SPEED_CAP_MPS=212 WF_FAMILY_MAP=ruling6 python3 wf_family.py prep "$SM2" "$ROOT" "$EV" nrcgS
for j in 0 1 2; do settle nrcgSF$j; done
echo RUNC_SETTLING_DONE
