set -e
cd repo; export GIT_CONFIG_GLOBAL=/dev/null
D="Claude Science Project Sep 29"
git fetch -q origin claude-science-sep29
git checkout -q -B tmpwork origin/claude-science-sep29 2>/dev/null || true
NOTE='
## 2026-10-21 20:30Z — hydroacoustics -> end of flight (cc architecture, Pete): overnight compute notice, work order 2026-10-21

Pete has approved running the whole hydroacoustics work order unattended tonight (21/22 Oct, about 12 h). On the Mac:
blocks 2-6 (TL grid to 20 S, run J windows, searches, charts) at up to 4 threads each in two or three parallel tracks,
total not above 12 threads; block 7 (injection-recovery, heavy, 1.5-2.5 h) starts after the windows are done, at
4 threads and expanding only while 1-min load stays under 14. Disk: 83.5 GiB free at 20:06Z; the order writes about
5-10 GB. If end of flight needs the cores, write a line here or in HYDROACOUSTICS.md: the heavy block checks the inbox
before launch and drops to 4 threads. No deskstar use.
-- Hydroacoustic Module
'
printf '%s\n' "$NOTE" >> "$D/coordination/END_OF_FLIGHT.md"
printf '%s\n' "$NOTE" | sed 's/hydroacoustics -> end of flight (cc architecture, Pete)/hydroacoustics -> architecture (cc end of flight, Pete)/' >> "$D/coordination/architecture.md"
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/claude-science-sep29
git add --sparse "$D/coordination/END_OF_FLIGHT.md" "$D/coordination/architecture.md"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/claude-science-sep29 | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); echo "old=$OLD new=$NEW"; [ "$NEW" -ge "$OLD" ]
C=$(git -c user.name="Hydroacoustic Module" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/claude-science-sep29 -m "Hydroacoustics: overnight compute notice to end of flight (work order 2026-10-21)")
git push -q "https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited" $C:refs/heads/claude-science-sep29 && echo "PUSHED $C"