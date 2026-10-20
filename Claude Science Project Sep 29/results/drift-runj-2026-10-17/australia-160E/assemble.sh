#!/bin/bash
# Reassemble split forcing files and verify every file against MANIFEST (sha256 size nparts relpath). Exit 3 on any mismatch.
set -u
MAN=$(readlink -f "$1"); [ -s "$MAN" ] || { echo "NO MANIFEST $1"; exit 4; }
cd "$HOME/.claude-science-scratch/ocean" || exit 4
nf=0
bad=0
while read -r h sz n rel; do
  if [ "$n" != "0" ]; then
    if [ ! -f "$rel" ] || [ "$(stat -c %s "$rel")" != "$sz" ]; then cat "$rel".part.* > "$rel.tmp" && mv "$rel.tmp" "$rel"; fi
  fi
  got=$(sha256sum "$rel" | cut -d' ' -f1)
  if [ "$got" != "$h" ]; then echo "BAD $rel"; bad=1; else [ "$n" != "0" ] && rm -f "$rel".part.*; fi
  nf=$((nf+1))
done < "$MAN"
[ $bad = 0 ] && [ $nf -gt 0 ] && echo "ALL VERIFIED $nf files" || { echo "VERIFY FAILED"; exit 3; }
