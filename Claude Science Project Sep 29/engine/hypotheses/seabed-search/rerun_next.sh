#!/bin/sh
# Searched areas: everything this module re-runs when end of flight writes
# /Users/pete/Downloads/mh370-exchange/end-of-flight/next-run/READY (overnight plan, 10 Oct 2026).
#
#   sh hypotheses/seabed-search/rerun_next.sh <run-dir> <out-tag> ["extra labels"]
#
# <run-dir> is a run directory carrying impacts.npy per seed and a run.json with impact_columns.
# Three products, in the order they are useful:
#   1. the four-panel 00:19 comparison, plain and +alive, with ESS on every panel;
#   2. the rho sweep, variant table and Davey eq. 11.2 planning curve;
#   3. the field-coverage check, if settling has posted wreckage samples for that run.
#
# LABELS. Architecture's 05:45 UTC entry requires every result built on core's (b) run to carry
# `core (b): split-half NOT converged` and `two-tank bookkeeping only`, plus deskstar, track 289.7,
# Inmarsat ephemeris, internal-v1 fuel and PROVISIONAL-OVERNIGHT. Pass them as the third argument;
# they are printed beneath every chart and copied into each note.
# VERIFIED end to end 10 Oct 2026 06:55 UTC against runs/eof-289-full (tag DRIVER-DRYRUN, output
# discarded): all three stages ran, the four-panel and sweep numbers reproduced those already
# published (none__other+alive Z 0.7206, run.toml row 0.7206, field coverage point 0.7337 /
# mean 0.7340 / any 0.7106), and the labels string was confirmed present in the chart PDF text.
set -eu
RUN="$1"; TAG="$2"; LABELS="${3:-}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/../results/seabed-search-$TAG"
mkdir -p "$OUT"
cd "$ROOT"
export RAYON_NUM_THREADS="${RAYON_NUM_THREADS:-4}"

echo "== 1. four-panel 00:19 comparison, plain and +alive =="
python hypotheses/seabed-search/impact_map_options.py "$RUN" "$OUT/impact-map-0019-$TAG" \
  --arcs runs/fixture-8/run.json --constraints alive --labels "$LABELS" | tee "$OUT/options.log"

echo "== 2. rho sweep, variants and Davey eq. 11.2 =="
for C in "" alive; do
  python hypotheses/seabed-search/report.py "$RUN" --option none ${C:+--constraint "$C"} \
    | tee "$OUT/sweep${C:+-$C}.log"
  cp runs/seabed-search-analysis/search-evidence.pdf "$OUT/search-evidence${C:+-$C}.pdf"
done

echo "== 3. field coverage over settling's wreckage samples, if posted =="
D=/Users/pete/Downloads/mh370-exchange/settling
NEW="$(ls -dt "$D"/*wreckage-field* 2>/dev/null | head -1 || true)"
if [ -n "$NEW" ]; then
  python hypotheses/seabed-search/field_coverage_check.py --dir "$NEW" --step 5 | tee "$OUT/field-coverage.json"
else
  echo "no settling wreckage samples found under $D: skipped, and the note must say so" \
    | tee "$OUT/field-coverage.skipped"
fi

printf '%s\n' "$LABELS" > "$OUT/LABELS.txt"
echo "wrote $OUT"
