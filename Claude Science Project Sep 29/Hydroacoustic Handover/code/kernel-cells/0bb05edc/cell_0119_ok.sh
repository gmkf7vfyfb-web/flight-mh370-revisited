cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git"
git -c credential.helper= fetch -q "$URL" '+refs/heads/claude-science-sep29:refs/remotes/origin/claude-science-sep29' '+refs/heads/hypothesis/hydroacoustics:refs/remotes/origin/hypothesis/hydroacoustics' 2>&1 | sed "s/${GITHUB_TOKEN}/***/g" | grep -v ignore || true
P='Claude Science Project Sep 29'; B=origin/claude-science-sep29
echo "head: $(git rev-parse --short $B)  hydro head: $(git rev-parse --short origin/hypothesis/hydroacoustics)"
echo "== files carrying the standing rule on sep29 head:"
git grep -l "STANDING RULE ON LABELS (Pete, 22 Oct 2026)" $B -- "$P" | sed "s|^$B:$P/||" | sort | tr '\n' ' ' ; echo
echo "count: $(git grep -l 'STANDING RULE ON LABELS (Pete, 22 Oct 2026)' $B -- "$P" | wc -l)"
echo; echo "== residual source-blocking words on sep29 head (excluding history/rule text, raw-data, superseded-file notes):"
git grep -n -i -E "closed[ -]access|paywall|unobtainable|\(closed\)|NOT held \(GAP\)|blocked, not untried|treat this as blocked|is closed and|not open access" $B -- "$P" | sed "s|^$B:$P/||" | grep -v -E "source-access-ledger|STANDING RULE|Pete's ruling on source access|Pete ruled|was wrong|wrongly|misattribution|mislabelled|CORRECTION|corrected|\"closed access|'closed access|never as|instead of|no longer|Never write|Both statements|label on Metz|mixed two papers|six \"Not held|not a reason to avoid|\"closed access\", \"paywalled\"|Also, \"Kadri" | cut -c1-200
echo; echo "== hydro branch engine/ residual:"
git grep -n -i -E "closed access|NOT held \(GAP\)|paywall|unobtainable" origin/hypothesis/hydroacoustics -- "$P/engine/hypotheses/hydroacoustics" | sed "s|^origin/hypothesis/hydroacoustics:$P/engine/hypotheses/hydroacoustics/||" | cut -c1-200 | head