EXD=/Users/pete/Downloads/mh370-exchange/hydroacoustics/kadri-package-v2
rm -rf $EXD/__pycache__ "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22/__pycache__"
cd $EXD/.. && rm -f kadri-package-v2/*.zip && zip -qr kadri-package-v2/kadri-package-v2-2026-10-22.zip kadri-package-v2 -x 'kadri-package-v2/*.zip' 'kadri-package-v2/COVER_NOTE_FOR_PETE.md' 'kadri-package-v2/SHA256SUMS' && cd kadri-package-v2 && shasum -a 256 *.csv *.md *.txt *.json *.npz *.py *.zip synthetic_triad/*.npz > SHA256SUMS && ls -la *.zip && unzip -l *.zip | tail -1
cat >> "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/kadri_package/README.txt" <<'EOF'
- 22 Oct 2026 (work order 2026-10-21 block 12): v2-2026-10-22/ is the CURRENT package (run J, whole-arc grid 41-20 S x
  -60..+60 NM x 8 receivers, D0'/D2/D3/D4 weights, both branches, M1b optional detector with templates, run J pulse model
  for the synthetic triad set, REQUESTS.md incl. the Royer draft, CALIBRATION_STATUS.txt rewritten, COVER_NOTE_FOR_PETE.md).
  Zip-ready copy: /Users/pete/Downloads/mh370-exchange/hydroacoustics/kadri-package-v2/ (synthetic waveforms only there).
  Everything above this line is superseded and kept for the record. NOTHING IS SENT before Pete approves.
EOF
# inbox re-read before commit
cd repo && GIT_CONFIG_GLOBAL=/dev/null git fetch -q origin claude-science-sep29 && GIT_CONFIG_GLOBAL=/dev/null git show origin/claude-science-sep29:"Claude Science Project Sep 29/coordination/HYDROACOUSTICS.md" | grep -n "^## " | tail -3