set -e
cd repo
export GIT_CONFIG_GLOBAL=/dev/null
D="Claude Science Project Sep 29"
cat >> "$D/coordination/HYDROACOUSTICS.md" <<'EOF'

## 2026-10-21 ~18:30Z — review session (Pete) -> HYDROACOUSTICS: brief Refresh v2 and a new work order

Pete reviewed the brief, materials and prior work on 21 Oct. `threads/master-prompts/hydroacoustics.md` now carries
"Refresh v2" (governs where it differs) with in-place fixes (run J; four decades; IMOS five loggers; 13 Oct
thresholds; both Kadri times labelled text/caption; lock retired; latitude span to 20 S or the 99th-percentile
contour). The work order is `threads/work-orders/hydroacoustics-order-2026-10-21.md` (12 blocks, dependencies,
costs). Key rulings: no raw data expected from Kadri or Royer, so extract every digitised source; generate weak
candidates at the screen level with labels, never gate them conservatively; explore weak-signal methods; the six
poster boxes, Table 1, Royer B/D1/D2 and infrasound are named test sets; TL recalibration plan a–e. Start at block 0.
-- Review session for hydroacoustics (default profile), 21 Oct 2026
EOF
cat >> "$D/coordination/architecture.md" <<'EOF'

## 2026-10-21 ~18:30Z — hydroacoustics review session -> architecture (cc end of flight, composer, Pete): brief Refresh v2 + work order committed
`threads/master-prompts/hydroacoustics.md` Refresh v2 and `threads/work-orders/hydroacoustics-order-2026-10-21.md`.
Rulings by Pete (21 Oct): latitude span to 20 S or the 99th-percentile contour for every module output; both Kadri
times carried (text 00:52:03 / caption 00:54:30); screen-level candidate generation with labels; digitisation of all
published sources as a deliverable; TL recalibration plan. For end of flight: hydroacoustics will request a compute
slot before injection-recovery (block 7); blocks 2–6 run at 4 threads. For the composer: the evidence-alone view will
come from a whole-arc prediction grid (block 2), not from run J rows. Gap register unchanged (G16 declared-conditional,
G17–G19 open, G21–G22 declared).
-- Review session for hydroacoustics, 21 Oct 2026
EOF
git fetch -q origin claude-science-sep29
OLD=$(git ls-tree -r origin/claude-science-sep29 | wc -l)
export GIT_INDEX_FILE=.git/index-commit
rm -f $GIT_INDEX_FILE
git read-tree origin/claude-science-sep29
git add --sparse "$D/threads/master-prompts/hydroacoustics.md" "$D/threads/work-orders/hydroacoustics-order-2026-10-21.md" "$D/coordination/HYDROACOUSTICS.md" "$D/coordination/architecture.md"
TREE=$(git write-tree)
NEW=$(git ls-tree -r $TREE | wc -l)
echo "entries old=$OLD new=$NEW"
[ "$NEW" -ge "$OLD" ]
git diff --stat origin/claude-science-sep29 $TREE | tail -6
C=$(git -c user.name="Claude Science (hydroacoustics review)" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/claude-science-sep29 -m "Hydroacoustics: brief Refresh v2 (Pete's rulings 21 Oct 2026) + work order 2026-10-21; inbox and architecture entries")
echo "commit $C"
git push -q "https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited" $C:refs/heads/claude-science-sep29 && echo PUSHED
git ls-remote origin refs/heads/claude-science-sep29