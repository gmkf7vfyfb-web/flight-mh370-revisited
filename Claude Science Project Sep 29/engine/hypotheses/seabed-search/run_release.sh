#!/bin/sh
# Searched areas: the whole chain for one end-of-flight release, in one command.
#
#   sh hypotheses/seabed-search/run_release.sh <exchange release dir> <tag> "<labels>" [settling samples dir]
#
# e.g.  sh hypotheses/seabed-search/run_release.sh \
#           /Users/pete/Downloads/mh370-exchange/end-of-flight/run-c c "core (c) ..." \
#           /Users/pete/Downloads/mh370-exchange/settling/run-c-core-set
#
# Steps, in order:
#   1. adapt each <stratum>/seed-N directory into the run layout, verifying SHA256SUMS;
#   2. the five ruled core 00:19 options per stratum and as a P(family) mixture, plain and +alive;
#   3. the field-coverage check per option against settling's samples, if a directory is given.
#
# STRATUM WEIGHTS are read from the release's own info file when it has one, and otherwise must be
# passed as WEIGHTS="0.69,0.15,0.14,0.01" in the stratum order printed by step 1. They are never
# hardcoded here: core's P(family) changes between runs and a stale weight is a silent error.
set -eu
SRC="$1"; TAG="$2"; LABELS="${3:-}"; FIELD="${4:-}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export RAYON_NUM_THREADS="${RAYON_NUM_THREADS:-4}"
OUT="../results/seabed-search-$TAG"; mkdir -p "$OUT"

echo "== 1. adapt the strata =="
STRATA=""
for d in "$SRC"/*/; do
  name="$(basename "$d")"; [ -d "$d" ] || continue
  case "$name" in *seed-*) continue;; esac
  sh hypotheses/seabed-search/adapt_exchange_run.sh "$d" "$TAG-$name" || continue
  STRATA="$STRATA $TAG-$name"
done
set -- $STRATA
[ "$#" -gt 0 ] || { echo "no strata adapted under $SRC" >&2; exit 2; }
echo "strata in order:$STRATA"

if [ -z "${WEIGHTS:-}" ]; then
  echo "WEIGHTS not set. Pass core's P(family) in the order above, e.g." >&2
  echo "  WEIGHTS=0.69,0.15,0.14,0.01 sh $0 ..." >&2
  exit 3
fi

echo "== 2. the five core options, per stratum and mixed =="
SPEC=""; i=1
for s in $STRATA; do
  w=$(printf '%s' "$WEIGHTS" | cut -d, -f$i)
  SPEC="${SPEC:+$SPEC,}runs/$s:$w"; i=$((i+1))
  python hypotheses/seabed-search/impact_map_options.py "runs/$s" "$OUT/impact-map-$s" \
    --arcs runs/fixture-8/run.json --constraints alive --labels "$LABELS" > "$OUT/$s.log" 2>&1
  echo "  $s done"
done
python hypotheses/seabed-search/impact_map_options.py "$SPEC" "$OUT/impact-map-$TAG-mixture" \
  --arcs runs/fixture-8/run.json --constraints alive --labels "$LABELS" | tee "$OUT/mixture.log"

if [ -n "$FIELD" ] && [ -d "$FIELD" ]; then
  echo "== 3. field coverage per option =="
  mkdir -p "$OUT/field-coverage"
  q=0
  while [ "$q" -le 4 ]; do
    set_name=$(ls "$FIELD" | sed -n 's/\(.*\)A_impacts\.f64/\1A/p' | head -1)
    [ "$q" -eq 0 ] || set_name=$(printf '%s' "$set_name" | sed 's/A$/B/')
    step=5; [ "$q" -eq 0 ] || step=1
    python hypotheses/seabed-search/field_coverage_check.py --dir "$FIELD" --set "$set_name" \
      --option "$q" --mixture fixed --step "$step" > "$OUT/field-coverage/opt$q.json" \
      2> "$OUT/field-coverage/opt$q.err" && echo "  option $q done" || echo "  option $q FAILED (see .err)"
    q=$((q+1))
  done
else
  echo "== 3. field coverage SKIPPED: no settling samples directory given ==" | tee "$OUT/field-coverage.skipped"
fi
printf '%s\n' "$LABELS" > "$OUT/LABELS.txt"
echo "wrote $OUT"
