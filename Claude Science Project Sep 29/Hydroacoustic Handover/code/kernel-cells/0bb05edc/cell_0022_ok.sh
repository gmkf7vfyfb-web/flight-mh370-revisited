cd /Users/pete/Downloads/flight-mh370-revisited
git grep -n -E "G-W1|G4\b.*F-35|F-35.*G4\b" origin/claude-science-sep29 origin/hypothesis/hydroacoustics -- 'Claude Science Project Sep 29/' | sed 's|^origin/[a-z0-9/-]*:||' | sort -u | cut -c1-280
echo "=== bib row"; git show origin/claude-science-sep29:"Claude Science Project Sep 29/results/hydroacoustics-bibliography.csv" | sed -n '1p;11p'
echo "=== brief lines"; git show origin/claude-science-sep29:"Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md" | sed -n '282,286p;303,307p' | cut -c1-250
echo "=== lit review 58"; git show origin/claude-science-sep29:"Claude Science Project Sep 29/results/hydroacoustics-literature-review.md" | sed -n '58p' | cut -c1-400