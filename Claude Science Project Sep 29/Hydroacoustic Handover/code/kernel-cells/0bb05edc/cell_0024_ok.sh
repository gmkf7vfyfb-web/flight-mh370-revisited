set -e
export GIT_CONFIG_GLOBAL=/dev/null
rm -rf fix-metz
git clone -q --filter=blob:none --no-checkout https://github.com/gmkf7vfyfb-web/flight-mh370-revisited.git fix-metz 2>&1 | grep -v "failed to store" || true
cd fix-metz
git config user.name "Claude Science session" ; git config user.email "claude-science@users.noreply.github.com"
git sparse-checkout init --no-cone
P='Claude Science Project Sep 29'
git sparse-checkout set "/$P/coordination/architecture.md" "/$P/coordination/HYDROACOUSTICS.md" "/$P/results/hydroacoustics-bibliography.csv" "/$P/results/hydroacoustics-digitised-sources.md" "/$P/results/hydroacoustics-blackman-validation.md" "/$P/results/hydroacoustics-kadri-package-v2.md" "/$P/results/hydroacoustics-overnight-2026-10-22-summary.md" "/$P/results/hydroacoustics-weak-signal-methods.md" "/$P/results/hydroacoustics-literature-review.md" "/$P/threads/master-prompts/hydroacoustics.md" "/$P/paper/CITATIONS-LEDGER.md" "/$P/engine/hypotheses/hydroacoustics/prepare/digitise_brown_2026.py" "/$P/engine/hypotheses/hydroacoustics/prepare/tl_recal_block9.py" "/$P/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22/REQUESTS.txt" "/$P/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22/COVER_NOTE_FOR_PETE.txt"
git checkout -q -b fix-sep29 origin/claude-science-sep29
find . -type f -not -path './.git/*' | sort
echo "--- on hydro branch:"; git ls-tree -r --name-only origin/hypothesis/hydroacoustics -- "$P/engine/hypotheses/hydroacoustics/prepare/kadri_package/v2-2026-10-22/" "$P/engine/hypotheses/hydroacoustics/prepare/digitise_brown_2026.py" "$P/engine/hypotheses/hydroacoustics/prepare/tl_recal_block9.py" | head
echo "--- same files on sep29?"; git ls-tree -r --name-only origin/claude-science-sep29 -- "$P/engine/hypotheses/hydroacoustics/prepare/kadri_package/" "$P/engine/hypotheses/hydroacoustics/prepare/digitise_brown_2026.py" "$P/engine/hypotheses/hydroacoustics/prepare/tl_recal_block9.py" | head
sed -n '371,373p' "$P/results/hydroacoustics-weak-signal-methods.md" | cut -c1-300
sed -n '271p' "$P/paper/CITATIONS-LEDGER.md" | cut -c1-400; grep -n "^| Key\|^| key" "$P/paper/CITATIONS-LEDGER.md" | head -3 | cut -c1-300