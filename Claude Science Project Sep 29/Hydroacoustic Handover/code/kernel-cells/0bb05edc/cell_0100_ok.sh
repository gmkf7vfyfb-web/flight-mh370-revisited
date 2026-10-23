cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git"
git -c credential.helper= fetch -q "$URL" claude-science-sep29:refs/remotes/origin/claude-science-sep29 hypothesis/hydroacoustics:refs/remotes/origin/hypothesis/hydroacoustics 2>&1 | sed "s/${GITHUB_TOKEN}/***/g" | grep -v ignore || true
P='Claude Science Project Sep 29'
for b in origin/claude-science-sep29 origin/hypothesis/hydroacoustics; do echo "== $b head $(git rev-parse --short $b)"; git log -1 --format='%s' $b | cut -c1-90; done
echo "ledger on head: $(git ls-tree --name-only origin/claude-science-sep29 "$P/results/" | grep -c source-access-ledger) files; ruling entry present: $(git show origin/claude-science-sep29:"$P/coordination/architecture.md" | grep -c "Pete's ruling on source access")"
echo "--- remaining source-blocking phrases on sep29 (Sep 29 folder, excluding data-not-held lines):"
git grep -n -i -E "closed access|closed-access|behind a paywall|is paywalled|unobtainable|\(closed\)|not held \(GAP\)|NOT held" origin/claude-science-sep29 -- "$P" | sed "s|^origin/claude-science-sep29:$P/||" | grep -v -i "raw\|ledger\|ruling\|Pete ruled\|was wrong\|wrongly\|misattribution\|source-access\|mislabelled\|IMS" | cut -c1-210 | head -25