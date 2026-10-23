cd "repo/Claude Science Project Sep 29/coordination"
wc -l architecture.md
grep -n '^## ' architecture.md
echo ====
grep -n -i -E 'hydro|acoustic|seafloor.depth|bathymetr|tau|zero until|selectable' architecture.md | cut -c1-220 | head -40
echo ====
ls ../results/ 2>/dev/null | head -50
cd ../../ && git log --oneline -12 -- "Claude Science Project Sep 29/coordination/architecture.md" "Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md"