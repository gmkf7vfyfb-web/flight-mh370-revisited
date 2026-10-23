cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git"
git -c credential.helper= fetch -q "$URL" '+refs/heads/*:refs/remotes/origin/*' 2>&1 | sed "s/${GITHUB_TOKEN}/***/g" | grep -v ignore || true
P='Claude Science Project Sep 29'
PAT='closed[ -]access|closed-access|paywall|unobtainable|\(closed\)|not held \(GAP\)|NOT held|is closed and|[Bb]locked,? not untried|treat this as blocked|not open access|restricted source|licen[cs]e block|cannot be used|may not be used|do not use'
for b in claude-science-sep29 hypothesis/hydroacoustics hypothesis/end-of-flight hypothesis/pleiades hypothesis/settling hypothesis/debris-drift hypothesis/seabed-search architecture/module-briefs-oct06; do
  n=$(git grep -c -i -E "$PAT" origin/$b -- "$P" ':!*/ISO*' 2>/dev/null | wc -l); echo "$b: $n files with hits (head $(git rev-parse --short origin/$b))"
done
echo; echo "== sep29, files + lines (excluding my own ruling text and arrival-window csv):"
git grep -n -i -E "$PAT" origin/claude-science-sep29 -- "$P" | sed "s|^origin/claude-science-sep29:$P/||" | grep -v -E "arrival_window_matrix|source-access-ledger|Pete's ruling on source access|Pete ruled|was wrong|wrongly|misattribution" | cut -c1-230