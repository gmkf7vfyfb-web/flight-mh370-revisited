cd /Users/pete/Downloads/flight-mh370-revisited
export GIT_CONFIG_GLOBAL=/dev/null
git fetch -q origin 2>&1 | grep -v "failed to store" | head -3
echo "branches:"; git for-each-ref --format='%(refname:short) %(objectname:short) %(committerdate:short)' refs/remotes/origin | head -20
PAT='closed[ -]access|closed-access|paywall|behind a paywall|not held|NOT HELD|unobtainable|not open access|open_access[^,]*closed|,closed,|licen[cs]e block|licen[cs]ing block|subscription|metadata only|abstract only|not obtained|no copy held|copy not held|not in the library|library copy from Pete|never commit|do not commit|not redistribut|redistribution'
for b in origin/claude-science-sep29 origin/hypothesis/hydroacoustics; do
  echo "=== $b : files under 'Claude Science Project Sep 29' with hits"
  git grep -c -i -E "$PAT" $b -- "Claude Science Project Sep 29" 2>/dev/null | sed "s|^$b:Claude Science Project Sep 29/||" | sort -t: -k2 -n -r | head -60
done