set -e
U=https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git
rm -rf main hyd
git clone -q --depth 1 --single-branch -b claude-science-sep29 --filter=blob:none --sparse $U main 2>&1 | grep -v config/git || true
cd main
git sparse-checkout set --no-cone '/Claude Science Project Sep 29/results/hydroacoustics-*.md' '/Claude Science Project Sep 29/results/source-access-ledger-2026-10-22.*' '/Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md' '/Claude Science Project Sep 29/coordination/architecture.md' '/Claude Science Project Sep 29/ARCHITECTURE.md' '/Claude Science Project Sep 29/threads/work-orders/hydroacoustics-*' '/Claude Science Project Sep 29/results/evidence-sweep-2026-10-17/*' '/Claude Science Project Sep 29/threads/master-prompts/hydroacoustics.md' 2>&1 | grep -v config/git || true
git log -1 --format='%h %ci %s'
cd ..
git clone -q --depth 1 --single-branch -b hypothesis/hydroacoustics --filter=blob:none --sparse $U hyd 2>&1 | grep -v config/git || true
cd hyd; git log -1 --format='%h %ci %s'
git ls-tree -r --name-only HEAD | grep -i hydroacoustics/ | sed 's|Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/||' | awk -F/ '{print $1"/"$2}' | sort | uniq -c | sort -rn | head -40