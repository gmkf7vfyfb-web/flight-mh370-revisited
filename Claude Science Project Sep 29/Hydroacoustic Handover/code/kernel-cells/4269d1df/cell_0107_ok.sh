python3 - <<'EOF'
p='out/README.md'; s=open(p).read()
s=s.replace("With the time and position of an MH370 field from the bearing,\n   the field could not have been near Haixun on 4-5 Apr.","For a floating field released on the bearing at the branch times, the model gives a probability of at most 6e-4\n   that any of it was within 110 km of Haixun on 5 Apr.")
open(p,'w').write(s)
EOF
export HOME=$PWD/h XDG_CONFIG_HOME=$PWD/h/.config
D="repo/Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/drift"
mkdir -p "$D"; cp -r out/* "$D/"; rm -f "$D/rowcond.py"
cd repo; git add "Claude Science Project Sep 29/results/kadri-haixun-conditional-2026-10-18/drift"
git diff --cached --name-only | grep -E "\.bin$|fuel-tables.json|\.xlsm$" && echo BAD || echo audit-ok
git -c user.name="Claude Science" -c user.email="noreply@example.com" commit -q -m "Kadri-Haixun conditional, drift leg (Q7): row-level and point drift LLRs vs run J, forward/backward drift to 5 Apr, figures (INTERIM; dedicated L-point run queued)"
git pull -q --rebase && git push -q https://x-access-token:$GITHUB_TOKEN@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git HEAD:claude-science-sep29 2>&1 | grep -v "failed to store" ; git log --oneline -1