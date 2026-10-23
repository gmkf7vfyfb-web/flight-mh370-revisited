cd /Users/pete/Downloads/flight-mh370-revisited
B=origin/claude-science-sep29
PAT='closed[ -]access|closed-access|paywall|behind a paywall|not held|NOT HELD|unobtainable|not open access|licen[cs]e block|licen[cs]ing block|subscription|metadata only|abstract only|not obtained|no copy held|copy not held|not in the library|library copy from Pete|not redistribut|no redistribution|cannot be redistributed|allowlist'
git grep -n -i -E "$PAT" $B -- "Claude Science Project Sep 29" ':!*architecture.md' ':!*hydroacoustics-bibliography.csv' ':!*.py' ':!*.rs' 2>/dev/null | sed "s|^$B:Claude Science Project Sep 29/||" | cut -c1-330 > /tmp/hits_sep29.txt
wc -l /tmp/hits_sep29.txt
sed -n '1,70p' /tmp/hits_sep29.txt