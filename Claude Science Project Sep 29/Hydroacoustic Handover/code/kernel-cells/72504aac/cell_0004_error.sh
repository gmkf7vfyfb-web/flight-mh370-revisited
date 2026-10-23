R="repo/Claude Science Project Sep 29"
tail -c 4000 "$R/coordination/HYDROACOUSTICS.md"; echo ======
grep -n -i -E "00:52:04|01:12:49|33\.6|1,245|0\.019|330|strongest" "$R/results/hydroacoustics-searches-run-j.md" | head -30; echo =====
grep -n -i -E "00:52:04|01:12:49|33\.6|0\.069|330|strongest|η = 0" "$R/results/hydroacoustics-composition-run-j.md" | head -30
ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/ ; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/graphics-2026-10-22 2>/dev/null