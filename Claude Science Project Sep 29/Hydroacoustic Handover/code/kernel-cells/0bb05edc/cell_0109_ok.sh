cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git"
P='Claude Science Project Sep 29'
git -c credential.helper= fetch -q "$URL" claude-science-sep29:refs/remotes/origin/claude-science-sep29 2>&1 | sed "s/${GITHUB_TOKEN}/***/g" | grep -v ignore || true
git sparse-checkout add "/$P/results/seabed-search-INDEX.md" "/$P/results/seabed-search-references.md" "/$P/results/settling-references.md" "/$P/results/kadri-haixun-conditional-2026-10-18/sources-sightings/sources-sightings-references.md" "/$P/ARCHITECTURE.md" "/$P/README.md" "/$P/coordination/*.md" "/$P/threads/master-prompts/*.md" "/$P/engine/AGENTS.md" 2>&1 | grep -v ignore || true
git checkout -q -B fix-sep29 origin/claude-science-sep29 2>&1 | grep -v ignore || true
git log -1 --format='%h %s' | cut -c1-80
echo "== my wording to normalise (working tree):"
grep -rn -i -E "no copy in (the )?(project )?store( yet)?|no copy in the project store" "$P" --include=*.md --include=*.csv --include=*.txt --include=*.py --include=*.json 2>/dev/null | grep -v "source-access-ledger" | sed "s|^$P/||" | cut -c1-250
echo "== settling 43/48 + sightings 13-14"
sed -n '43p;48p' "$P/results/settling-references.md" | cut -c1-900
sed -n '13,14p' "$P/results/kadri-haixun-conditional-2026-10-18/sources-sightings/sources-sightings-references.md" | cut -c1-600