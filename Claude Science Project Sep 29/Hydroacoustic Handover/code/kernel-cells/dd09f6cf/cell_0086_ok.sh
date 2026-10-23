export HOME=$PWD/home XDG_CONFIG_HOME=$PWD/home/.config; cd repo
git pull --rebase -q origin claude-science-sep29 2>&1 | tail -2; git log --oneline -3
P='Claude Science Project Sep 29'; wc -l "$P/coordination/SEARCHED_AREAS.md"; tail -40 "$P/coordination/SEARCHED_AREAS.md" | cut -c1-400
git ls-tree --name-only HEAD -- "$P/results/kadri-haixun-conditional-2026-10-18/"