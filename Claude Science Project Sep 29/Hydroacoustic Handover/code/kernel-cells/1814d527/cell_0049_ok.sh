cd "$OLDPWD" 2>/dev/null; cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/1814d527-d9b6-410a-a48a-1b497eabc73d || exit 1
cat >> "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/README.txt" <<'EOF'
- 22 Oct 2026 (work order 2026-10-21 block 12): v2-2026-10-22/ is the CURRENT package (run J, whole-arc grid 41-20 S x
  -60..+60 NM x 8 receivers, D0'/D2/D3/D4 weights, both branches, M1b optional detector with templates, run J pulse model
  for the synthetic triad set, REQUESTS.md incl. the Royer draft, CALIBRATION_STATUS.txt rewritten, COVER_NOTE_FOR_PETE.md).
  Zip-ready copy: /Users/pete/Downloads/mh370-exchange/hydroacoustics/kadri-package-v2/ (synthetic waveforms only there).
  Everything above this line is superseded and kept for the record. NOTHING IS SENT before Pete approves.
EOF
tail -3 "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/README.txt"
cd repo && export GIT_CONFIG_GLOBAL=/dev/null && git fetch -q origin claude-science-sep29 && git show origin/claude-science-sep29:"Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | grep -n "^## " | tail -3
git show origin/claude-science-sep29:"Claude Science Project Sep 29/coordination/architecture.md" | grep -n "^## " | tail -6