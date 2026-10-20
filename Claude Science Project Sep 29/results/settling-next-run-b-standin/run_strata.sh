#!/bin/sh
# Stand-in driver: settling's unchanged wreckage_field_rerun.sh, once per stratum, then the +alive map (no new draws).
set -eu
ROOT=$(pwd)
export HOME=$ROOT/scratch-home CARGO_HOME=/Users/pete/.cargo RUSTUP_HOME=/Users/pete/.rustup CARGO_TARGET_DIR=$ROOT/target-9823b4e PATH=/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH
export RAYON_NUM_THREADS=2
R="$ROOT/repo/Claude Science Project Sep 29/results/settling-wreckage-field-289-priorities"
SM="$ROOT/eof-3c6319f/Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke"; RUNS=/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run
ARCS="/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/386151e9-859f-412a-8d9d-b8da48899575/repo/Claude Science Project Sep 29/engine/runs/reference-289/run.json"
ENG="$ROOT/eng-9823b4e/Claude Science Project Sep 29/engine"
LBL="core (b) split-half NOT converged; two-tank bookkeeping only; PROVISIONAL-OVERNIGHT; EoF sweep run by a stand-in; settling run by an architecture stand-in, module to review; internal-v1 fuel, one-engine flow 2x source tables (core 06:10)"
for ST in free repro-radar descent-climb routes; do
  mkdir -p "$ROOT/work/$ST"; cd "$ROOT/work/$ST"
  echo "== $ST start $(date -u +%H:%M:%S)"
  WF_RUN_PATTERN="next-$ST/seed-{s}" WF_SEED_PATTERN="." WF_LABEL="next-run-b, $ST stratum" WF_OUTSTEM="settling-wreckage-field-next-run-b-$ST" WF_RUN_LABELS="$LBL" \
    sh "$R/wreckage_field_rerun.sh" "$SM" "$RUNS" "$ARCS" "$ENG" > plain.log 2>&1 || { tail -20 plain.log; echo "FAILED $ST plain"; exit 1; }; tail -6 plain.log
  echo "== $ST plain done $(date -u +%H:%M:%S)"
  WF_RUN_PATTERN="next-$ST/seed-{s}" WF_SEED_PATTERN="." WF_LABEL="next-run-b, $ST stratum" WF_OUTSTEM="settling-wreckage-field-next-run-b-$ST-alive" WF_RUN_LABELS="$LBL" WF_CONSTRAINT=alive \
    python3 "$R/wreckage_map_priorities_run.py" "$SM" "$RUNS" "$ARCS" > alive.log 2>&1 || { tail -20 alive.log; echo "FAILED $ST alive"; exit 1; }; tail -3 alive.log
  echo "== $ST alive done $(date -u +%H:%M:%S)"
done
