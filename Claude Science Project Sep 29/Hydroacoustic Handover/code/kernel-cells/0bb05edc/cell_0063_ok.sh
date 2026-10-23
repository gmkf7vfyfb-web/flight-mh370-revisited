cd /Users/pete/Downloads/flight-mh370-revisited
B=origin/claude-science-sep29; P='Claude Science Project Sep 29'
git show $B:"$P/results/settling-references.md" | sed -n '40,52p' | cut -c1-900
echo ======; git show $B:"$P/results/settling-references.md" | grep -n -i -E "chu2006|dnv|anderson2018|museum.wa|knkt|dki574|calhoun|mearns|andersen" | cut -c1-420