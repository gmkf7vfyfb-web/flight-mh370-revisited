#!/bin/bash
# Usage: run_arclat.sh <config.toml> <label>. As aus160/run.sh, but waits for the heavy lock without a timeout and logs the binary hash.
set -u
CFG=$(readlink -f "$1"); LABEL="$2"
ENG="$HOME/mh370/drift/repo/Claude Science Project Sep 29/engine"
BIN=$(ls -t $HOME/mh370/drift/target/release/deps/mh370_hypotheses-* | grep -v '\.d$' | head -1)
LOG="$HOME/mh370/drift/runs/$LABEL.log"; mkdir -p "$HOME/mh370/drift/runs"
exec 9>>"$HOME/.mh370-heavy.lock"
flock 9
cp "$CFG" "$ENG/hypotheses/debris-drift/$(basename "$CFG")"
cd "$ENG/hypotheses"
( while sleep 30; do ps -o rss= -C $(basename "$BIN") 2>/dev/null | sort -n | tail -1; done ) > "$HOME/mh370/drift/runs/$LABEL.rss" 2>/dev/null &
MON=$!
echo "start $(date -u +%FT%TZ) bin=$BIN binsha=$(sha256sum "$BIN" | cut -c1-16) cfg=$(sha256sum "$CFG" | cut -c1-16)" > "$LOG"
env DRIFT_CONFIG="debris-drift/$(basename "$CFG")" RAYON_NUM_THREADS=88 "$BIN" pilot --ignored --nocapture >> "$LOG" 2>&1
RC=$?; kill $MON 2>/dev/null; echo "peak_rss_kb $(sort -n "$HOME/mh370/drift/runs/$LABEL.rss" | tail -1)" >> "$LOG"
echo "EXIT=$RC end $(date -u +%FT%TZ)" >> "$LOG"
