cd repo
R="Claude Science Project Sep 29/results/hydroacoustics-synthetic-composer-test.md"
sed -i '' 's|H08N and H08S are about 160 km|H08N and H08S are 218 km|' "$R"; grep -n "218 km" "$R"
git fetch -q origin; git diff --stat HEAD origin/claude-science-sep29 -- "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md"
git add "Claude Science Project Sep 29/results/hydroacoustics-synthetic-composer-test."*
git commit -q -m "results: hydroacoustics synthetic composer test - provisional, parametric 7th-arc PDF; only a cross-ocean H01+H08 pair moves the PDF materially"
for i in 1 2 3; do git pull -q --rebase origin claude-science-sep29 && git push -q origin HEAD:claude-science-sep29 && break; sleep 3; done
git log --oneline -1