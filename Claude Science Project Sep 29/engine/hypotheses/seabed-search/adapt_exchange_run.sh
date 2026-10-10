#!/bin/sh
# Turn one of end of flight's exchange STRATUM directories into a run directory this module's scripts
# can read, without copying 2.7 GB per seed.
#
#   sh hypotheses/seabed-search/adapt_exchange_run.sh <stratum-dir> <tag> [--skip-verify]
#
# The exchange layout is  <stratum>/seed-N/{impacts.npy, run.json, terminal.json, SHA256SUMS}
# with run.json PER SEED and no `bto-bfo` level. Every script here expects the run layout,
#   <run>/run.json  and  <run>/bto-bfo/seed-N/impacts.npy
# so this builds that shape out of symlinks plus one copied run.json. Nothing is duplicated and the
# exchange directory is never written to.
#
# SHA256SUMS is VERIFIED by default. The producer copies seed by seed, so a directory can be complete
# while the next one is still being written; a truncated impacts.npy would otherwise read as a short
# but valid array and give a quietly wrong answer. --skip-verify is for re-runs only.
#
# Note: core's (b) run has FOUR strata, combined by P(family) (free 0.69, Davey dynamics 0.15,
# descent-climb 0.14, routes 0.01). Adapt and run each separately; the mixed number is a weighted
# combination and inherits (b)'s non-convergence, so report per stratum as well as mixed.
set -eu
SRC="$1"; TAG="$2"; VERIFY="${3:-}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEST="$ROOT/runs/$TAG"
[ -d "$SRC" ] || { echo "no such stratum directory: $SRC" >&2; exit 2; }
mkdir -p "$DEST/bto-bfo"
n=0
for s in "$SRC"/seed-*/; do
  [ -f "$s/impacts.npy" ] || { echo "skipping $s: no impacts.npy (still being written?)" >&2; continue; }
  if [ "$VERIFY" != "--skip-verify" ] && [ -f "$s/SHA256SUMS" ]; then
    ( cd "$s" && shasum -a 256 -c SHA256SUMS >/dev/null ) \
      || { echo "CHECKSUM FAILED in $s - refusing to use it" >&2; exit 3; }
  fi
  name="$(basename "$s")"
  ln -sfn "$(cd "$s" && pwd)/impacts.npy" "$DEST/bto-bfo/$name-impacts.npy" 2>/dev/null || true
  mkdir -p "$DEST/bto-bfo/$name"
  ln -sfn "$(cd "$s" && pwd)/impacts.npy" "$DEST/bto-bfo/$name/impacts.npy"
  rm -f "$DEST/bto-bfo/$name-impacts.npy"
  [ -f "$DEST/run.json" ] || cp "$s/run.json" "$DEST/run.json"
  n=$((n+1))
done
[ "$n" -gt 0 ] || { echo "no usable seeds under $SRC" >&2; exit 4; }
echo "adapted $n seed(s) of $SRC -> $DEST (run.json from the first seed)"
