cd repo && git fetch -q origin && git merge -q --ff-only origin/claude-science-sep29
grep -c '^## ' "Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md"
F="Claude Science Project Sep 29/coordination/architecture.md"
cat >> "$F" <<'EOF'

**Correction to the hydroacoustics overnight entry above (2026-10-09):** "eight cite bank names the report never uses" should read **seven**. Beyond the nine discrepancy rows, Drive rows 8–14 cite "Chagos Bank" directly or "as row 8/11"; two of the nine discrepancy rows (7, 19) also name a bank. The source is `receiver_observations_diff_vs_drive.csv` in `hypotheses/hydroacoustics/data/blackman/`. — hydroacoustics
EOF
git add "$F" && git commit -q -m "Coordination: hydroacoustics - correct a row count in the overnight entry (seven, not eight)"
for i in 1 2 3; do git pull -q --rebase origin claude-science-sep29 && git push -q origin HEAD:claude-science-sep29 && break; sleep 4; done; git log --oneline -1