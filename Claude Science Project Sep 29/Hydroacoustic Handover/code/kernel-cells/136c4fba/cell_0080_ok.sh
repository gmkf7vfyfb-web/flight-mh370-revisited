cd repo && export XDG_CONFIG_HOME=/tmp/xdg
P="Claude Science Project Sep 29"
git add "$P/engine/hypotheses/hydroacoustics" "$P/results/hydroacoustics-kadri-northern-run-j.md" "$P/threads/run-state" "$P/coordination/HYDROACOUSTICS.md" "$P/coordination/architecture.md"
git -c user.name="hydroacoustics" -c user.email="hydroacoustics@local" commit -q -m "Hydroacoustics run J Task 1: Kadri northern conditional on held data - no detection at any pre-registered level; amendment A1 resolves Kadri's two times from his own figure 9 panel c (00:52:03); work-order correction on where the digitised H08S record ends; RUN-STATE written" 
git log --oneline -4
echo "--- files ---"; git show --stat --oneline HEAD | tail -14
git push -q origin hypothesis/hydroacoustics && echo "pushed $(git rev-parse --short HEAD)"