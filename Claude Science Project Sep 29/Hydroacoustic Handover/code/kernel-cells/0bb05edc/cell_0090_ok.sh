cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited.git"
git -c credential.helper= fetch -q "$URL" hypothesis/hydroacoustics:refs/remotes/origin/hypothesis/hydroacoustics 2>&1 | sed "s/${GITHUB_TOKEN}/***/g" | grep -v ignore || true
H=origin/hypothesis/hydroacoustics; P='Claude Science Project Sep 29'
git log -4 --format='%h %ad %an | %s' --date=format:%H:%M $H | cut -c1-150
echo "--- residual hits in engine/ of module branch (labels about sources):"
git grep -n -i -o -E ".{90}(closed access|closed\)|not held \(GAP\)|NOT held|is closed|paywall|unobtainable).{60}" $H -- "$P/engine/hypotheses/hydroacoustics" | sed "s|^$H:$P/engine/hypotheses/hydroacoustics/||" | grep -v -i "raw\|IMS data\|recordings are not held" | cut -c1-330