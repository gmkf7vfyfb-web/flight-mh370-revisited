#!/bin/bash
# Usage: run.sh <config.toml> <label>. Runs the debris-drift transport (pilot test entry) under the deskstar heavy lock.
set -u
CFG=$(readlink -f "$1"); LABEL="$2"
ENG="$HOME/mh370/drift/repo/Claude Science Project Sep 29/engine"
BIN=$(ls -t $HOME/mh370/drift/target/release/deps/mh370_hypotheses-* | grep -v '\.d$' | head -1)
LOG="$HOME/mh370/drift/runs/$LABEL.log"; mkdir -p "$HOME/mh370/drift/runs"
cp "$CFG" "$ENG/hypotheses/debris-drift/$(basename "$CFG")"
exec 9>>"$HOME/.mh370-heavy.lock"
flock -w 5400 9 || { echo "NO-GO lock timeout" > "$LOG"; exit 8; }
cd "$ENG/hypotheses"
TIMER=""; [ -x /usr/bin/time ] && TIMER="/usr/bin/time -v"
( while sleep 30; do ps -o rss= -C $(basename "$BIN") 2>/dev/null | sort -n | tail -1; done ) > "$HOME/mh370/drift/runs/$LABEL.rss" 2>/dev/null &
MON=$!
echo "start $(date -u +%FT%TZ) bin=$BIN cfg=$(sha256sum "$CFG" | cut -c1-16)" > "$LOG"
$TIMER env DRIFT_CONFIG="debris-drift/$(basename "$CFG")" RAYON_NUM_THREADS=88 "$BIN" pilot --ignored --nocapture >> "$LOG" 2>&1
RC=$?; kill $MON 2>/dev/null; echo "peak_rss_kb $(sort -n "$HOME/mh370/drift/runs/$LABEL.rss" | tail -1)" >> "$LOG"
echo "EXIT=$RC end $(date -u +%FT%TZ)" >> "$LOG"
grep -h -E 'oom_kill' /sys/fs/cgroup/memory.events >> "$LOG" 2>/dev/null
