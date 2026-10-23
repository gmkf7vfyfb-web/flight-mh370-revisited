set -e
export GIT_CONFIG_GLOBAL=/dev/null
cd repo && git sparse-checkout set --skip-checks "Claude Science Project Sep 29/coordination" "Claude Science Project Sep 29/results" "Claude Science Project Sep 29/threads" "Claude Science Project Sep 29/ARCHITECTURE.md" 2>/dev/null; cd ..
P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
ls "$P" | head -30
echo ---
find "$P" -maxdepth 3 -iname '*kadri*' | head -40
echo ---
ls "repo/Claude Science Project Sep 29/results/" | grep -i hydro
echo ---
ls "repo/Claude Science Project Sep 29/threads/work-orders/" "repo/Claude Science Project Sep 29/threads/master-prompts/" | grep -i hydro
ls "repo/Claude Science Project Sep 29/coordination/" | head