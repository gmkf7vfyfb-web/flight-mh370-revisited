cd fix-metz/"Claude Science Project Sep 29"
for f in coordination/architecture.md coordination/HYDROACOUSTICS.md coordination/PAPER.md; do echo "=== $f ($(wc -l < $f) lines)"; tail -n 8 "$f" | cut -c1-230; done
echo; grep -n "RECOMMENDATION" coordination/PAPER.md | tail -3 | cut -c1-200