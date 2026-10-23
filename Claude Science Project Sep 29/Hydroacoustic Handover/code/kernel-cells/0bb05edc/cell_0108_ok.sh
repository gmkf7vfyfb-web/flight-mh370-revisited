find /Users/pete/Downloads -maxdepth 4 \( -iname "*operational*search*" -o -iname "*ae-2014-054*" -o -iname "*ae2014054*" -o -iname "atsb2017*" \) 2>/dev/null | head; echo ---
cd fix-metz && export GIT_CONFIG_GLOBAL=/dev/null; P='Claude Science Project Sep 29'; B=origin/claude-science-sep29
git show $B:"$P/results/seabed-search-INDEX.md" | sed -n '44,49p' | cut -c1-400
echo ---; git show $B:"$P/results/seabed-search-references.md" | sed -n '116,130p' | cut -c1-400