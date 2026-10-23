cd /tmp
PAT='closed[ -]access|closed-access|paywall|behind a paywall|not held|NOT HELD|unobtainable|not open access|metadata only|abstract only|not obtained|\(closed\)|closed and|, closed|is closed|closed\)'
grep -n -i -E "$PAT" arch.md | cut -c1-420