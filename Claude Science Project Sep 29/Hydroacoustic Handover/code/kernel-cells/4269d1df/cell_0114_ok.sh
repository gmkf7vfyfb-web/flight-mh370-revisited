export HOME=$PWD/h XDG_CONFIG_HOME=$PWD/h/.config
sed -i '' -e 's/898b1595-edf7-4c12-aade-e3ef87a5f9af/1ba7eef8-5626-4d99-bb70-3ae767d7e2ab/' -e 's/42afca60-1149-424c-8b09-f2d823e74c7e/7097742d-38bd-4fc9-88c8-377f02181e8e/' out/README.md
grep -c "1ba7eef8\|7097742d" out/README.md
D="repo/Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/drift"; cp out/README.md out/figs.py out/fig-forward-drift-5apr.* out/fig-backward-origin-ring.* "$D/"
cd repo; git add "Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/drift"
git diff --cached --name-only | grep -E "\.bin$|fuel-tables.json|\.xlsm$" && echo BAD || echo audit-ok
git -c user.name="Claude Science" -c user.email="noreply@example.com" commit -q -m "Kadri-Haixun drift leg: figure captions state sighting date (5 Apr 03:05-03:25 UTC) and source dates"
git stash -q 2>/dev/null; git pull -q --rebase; git push -q https://x-access-token:$GITHUB_TOKEN@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git HEAD:claude-science-sep29 2>&1 | grep -v "failed to store"; git rev-parse --short HEAD; git ls-remote https://x-access-token:$GITHUB_TOKEN@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git refs/heads/claude-science-sep29 | cut -c1-7