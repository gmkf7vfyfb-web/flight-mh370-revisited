cd /Users/pete/Downloads/flight-mh370-revisited
B=origin/claude-science-sep29; P='Claude Science Project Sep 29'
ctx(){ f="$1"; shift; git show $B:"$P/$f" > /tmp/_f.txt; for n in "$@"; do echo "--- $f:$n"; awk -v l=$n 'NR>=l-2 && NR<=l+1' /tmp/_f.txt | cut -c1-320; done; }
ctx results/hydroacoustics-references.md 16 44 73 98 118 237 243
ctx results/hydroacoustics-prior-work-critique.md 33
ctx results/debris-drift-find-episodes.md 40
ctx results/hydroacoustics-literature-review.md 7