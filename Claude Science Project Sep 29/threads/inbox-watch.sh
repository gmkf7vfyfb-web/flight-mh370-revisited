#!/bin/sh
# Inbox watcher for module sessions (Modular Architecture, 10 Oct 2026).
#
# Run it as a BACKGROUND cell, then end your turn. The cell finishes, and so wakes your session, when:
#   - your inbox file changes on branch claude-science-sep29 (exit 0; prints the new section headers),
#   - the optional trigger path appears on local disk (exit 0), or
#   - MAX_HOURS pass (exit 3; restart the watcher).
#
# Usage (give the trigger as an ABSOLUTE path):
#   sh "Claude Science Project Sep 29/threads/inbox-watch.sh" <inbox-path-in-repo> [trigger-path] [max-hours]
# Example:
#   sh "Claude Science Project Sep 29/threads/inbox-watch.sh" \
#      "Claude Science Project Sep 29/coordination/END_OF_FLIGHT.md" \
#      /Users/pete/Downloads/mh370-exchange/core/next-run/READY 8
#
# It polls the public raw file every 5 min (no credentials, no clone). It writes only under $TMPDIR.
# Raw GitHub can lag a push by up to about 5 min.
set -u
INBOX="$1"; TRIGGER="${2:-}"; MAXH="${3:-8}"; EVERY=300
RAW="https://raw.githubusercontent.com/gmkf7vfyfb-web/flight-mh370-revisited/claude-science-sep29/$(printf '%s' "$INBOX" | sed 's/ /%20/g')"
W=$(mktemp -d "${TMPDIR:-/tmp}/inbox-watch-XXXXXX") || exit 2
get() { curl -fsSL -m 60 -H 'Cache-Control: no-cache' "$RAW?t=$(date +%s)" -o "$1"; }
get "$W/old.md" || { echo "cannot read $RAW"; exit 2; }
start=$(date +%s)
echo "watching $INBOX ($(wc -l < "$W/old.md") lines) trigger=${TRIGGER:-none} max=${MAXH}h from $(date -u +%H:%M:%SZ)"
while :; do
  if [ -n "$TRIGGER" ] && [ -e "$TRIGGER" ]; then echo "TRIGGER PRESENT: $TRIGGER $(date -u +%H:%M:%SZ)"; exit 0; fi
  if get "$W/new.md" && ! cmp -s "$W/old.md" "$W/new.md"; then
    echo "INBOX CHANGED $(date -u +%H:%M:%SZ). New section headers:"
    diff "$W/old.md" "$W/new.md" | grep '^> ## ' | sed 's/^> //'
    exit 0
  fi
  [ $(( $(date +%s) - start )) -ge $(( MAXH * 3600 )) ] && { echo "TIMEOUT after ${MAXH}h: restart the watcher"; exit 3; }
  sleep $EVERY
done
