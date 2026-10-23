set -e
cd repo; export GIT_CONFIG_GLOBAL=/dev/null
D="Claude Science Project Sep 29"; B=claude-science-sep29; URL="https://x-access-token:${GITHUB_TOKEN}@github.com/gmkf7vfyfb-web/flight-mh370-revisited"
git fetch -q origin $B
git sparse-checkout reapply 2>/dev/null || true
# bring coordination files to the remote head before appending
git show origin/$B:"$D/coordination/architecture.md" > "$D/coordination/architecture.md"
git show origin/$B:"$D/coordination/HYDROACOUSTICS.md" > "$D/coordination/HYDROACOUSTICS.md"
cp ../hydroacoustics-overnight-2026-10-22-summary.md "$D/results/hydroacoustics-overnight-2026-10-22-summary.md"
ENTRY='
## 2026-10-22 ~14:00Z — Hydroacoustic Module -> architecture, composer, end of flight, Pete: OVERNIGHT RUN OF WORK ORDER 2026-10-21 COMPLETE

Every block ran and is committed; summary first: `results/hydroacoustics-overnight-2026-10-22-summary.md` (points to the ten block
notes). No detection claimed. Gate: P_D(received level) on declared backgrounds at the four IMOS loggers; proxy-only at H01W/H08S.
IMOS-gated likelihood written as `mh370-exchange/hydroacoustics/run-j-gated-v2/` (READY; weakly informative: ln Z -0.034,
median latitude +0.05 deg under D0 p 0.5); composer default stays 0.0. RULINGS REQUESTED: (1) composer default for
hydro-lnL-imos-margeta with the G11-1 label, IMS proxy as sensitivity; (2) RAM in place of adiabatic KRAKEN on sill-crossing IMS
paths; (3) re-register the air9 level test with slope + shape only, or obtain unit-consistent levels (G23). APPROVALS FOR PETE:
Kadri package v2 and the Royer letter (prepare/kadri_package/v2-2026-10-22/, cover note); Metz et al. 2023 and Kadri 2019 (closed
access). Disk: 83.5 -> 11.9 (min) -> ~28 GiB; nothing of Pete'"'"'s deleted; the eleven track workspaces (~33 GB) and run-j-gated
(6.5 GB, superseded) can be swept, and Time Machine local snapshots thinned.
-- Hydroacoustic Module
'
printf '%s\n' "$ENTRY" >> "$D/coordination/architecture.md"
printf '%s\n' "$ENTRY" | sed 's/-> architecture, composer, end of flight, Pete/-> HYDROACOUSTICS (own inbox, for the next session)/' >> "$D/coordination/HYDROACOUSTICS.md"
export GIT_INDEX_FILE=.git/index-commit; rm -f $GIT_INDEX_FILE
git read-tree origin/$B
git add --sparse "$D/results/hydroacoustics-overnight-2026-10-22-summary.md" "$D/coordination/architecture.md" "$D/coordination/HYDROACOUSTICS.md"
TREE=$(git write-tree); OLD=$(git ls-tree -r origin/$B | wc -l); NEW=$(git ls-tree -r $TREE | wc -l); echo "old=$OLD new=$NEW"; [ "$NEW" -ge "$OLD" ]
C=$(git -c user.name="Hydroacoustic Module" -c user.email="noreply@users.noreply.github.com" commit-tree $TREE -p origin/$B -m "Hydroacoustics: overnight run of work order 2026-10-21 complete - summary note, rulings requested, approvals for Pete")
git push -q "$URL" $C:refs/heads/$B && echo "PUSHED $C"