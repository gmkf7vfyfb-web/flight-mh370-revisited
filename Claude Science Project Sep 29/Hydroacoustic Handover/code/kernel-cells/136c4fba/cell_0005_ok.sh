cd repo && export XDG_CONFIG_HOME=/tmp/xdg
git fetch origin hypothesis/hydroacoustics:hypothesis/hydroacoustics 2>&1 | tail -2
git checkout hypothesis/hydroacoustics 2>&1 | tail -3
echo "=== HEAD ==="; git log --oneline -3
P="Claude Science Project Sep 29"
echo "=== threads ==="; ls "$P/threads" "$P/threads/master-prompts" "$P/threads/run-state" 2>&1
echo "=== inbox ==="; ls "$P/coordination/inbox" 2>&1
echo "=== hypotheses ==="; ls "$P/engine/hypotheses" 2>&1
echo "=== results hydro ==="; ls "$P/results" | grep -i hydro