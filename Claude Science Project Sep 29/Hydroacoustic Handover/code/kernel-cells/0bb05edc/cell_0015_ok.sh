cd /Users/pete/Downloads/flight-mh370-revisited && git fetch -q origin 2>/dev/null; 
for b in origin/claude-science-sep29 origin/hypothesis/hydroacoustics; do echo "=== $b"; git grep -n -i -E "metz" $b -- '*.md' '*.txt' '*.csv' '*.toml' 2>/dev/null | grep -i -E "closed|access|paywall|not held|unavailable|could not|blocked" | cut -c1-400; done
echo "=== exchange"
grep -rIn -i "metz" /Users/pete/Downloads/mh370-exchange/hydroacoustics --include='*.md' --include='*.txt' --include='*.json' 2>/dev/null | grep -i -E "closed|access|paywall|held|unavailable|blocked" | cut -c1-400 | head -20