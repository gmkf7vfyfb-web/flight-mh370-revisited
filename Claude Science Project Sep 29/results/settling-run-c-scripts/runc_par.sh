#!/bin/sh
# Run C settling, one of two parallel tracks (core set | by family). Prep is single-threaded; settling passes at 1 thread here, so the two
# tracks together stay within 2 threads outside the heavy lock. Usage: sh runc_par.sh standard|family
set -eu
W=$(pwd); SM2="$W/wt-base/Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke"
ENG="$W/wt-rebase/Claude Science Project Sep 29/engine"; ROOT=/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run-c
EV="$ROOT/summary/family-evidence-run-c.json"; test -e "$EV"
export WF_SEEDS=1,2,3,4,5,6,7,8 HOME="$W/scratch-home" CARGO_HOME=/Users/pete/.cargo CARGO_TARGET_DIR="$W/target-wt" PATH="/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH"
settle() { ( cd "$ENG" && RAYON_NUM_THREADS=1 SETTLING_THREADS=1 SETTLING_FIELD_IN="$W/field/$1_impacts.f64" SETTLING_FIELD_OUT="$W/field/$1_elements.f64" \
      lockf "$W/.settle-build.lock" cargo test --offline -j 1 --release -p mh370-hypotheses settling::tests::wreckage_field -- --ignored 2>&1 | grep "test result" ); echo "settled $1 $(date -u +%H:%M)"; }
if [ "$1" = standard ]; then
  python3 wf_standard.py prep "$SM2" "$ROOT" "$EV" nrc; for T in A B; do settle nrc$T; done; echo ALLROWS_DONE $(date -u +%H:%M)
  WF_SPEED_CAP_MPS=212 python3 wf_standard.py prep "$SM2" "$ROOT" "$EV" nrcS; for T in A B; do settle nrcS$T; done
else
  WF_FAMILY_MAP=ruling6 python3 wf_family.py prep "$SM2" "$ROOT" "$EV" nrcg; for j in 0 1 2; do settle nrcgF$j; done; echo ALLROWS_DONE $(date -u +%H:%M)
  WF_SPEED_CAP_MPS=212 WF_FAMILY_MAP=ruling6 python3 wf_family.py prep "$SM2" "$ROOT" "$EV" nrcgS; for j in 0 1 2; do settle nrcgSF$j; done
fi
echo "$1 TRACK_DONE $(date -u +%H:%M)"
