cd /Users/pete/Downloads/flight-mh370-revisited
F='Claude Science Project Sep 29/coordination/architecture.md'
git show origin/claude-science-sep29:"$F" > /tmp/arch.md
for L in 2191 2598 3014; do echo "=========== line $L"; awk -v l=$L 'NR>=l-12 && NR<=l+8' /tmp/arch.md | cut -c1-300; done
echo "=========== nearest dated headings before each"
for L in 2191 2598 3014; do awk -v l=$L 'NR<=l && /^#+ .*(2026|Oct|oct)/ {h=$0} END{print l": "h}' /tmp/arch.md | cut -c1-200; done