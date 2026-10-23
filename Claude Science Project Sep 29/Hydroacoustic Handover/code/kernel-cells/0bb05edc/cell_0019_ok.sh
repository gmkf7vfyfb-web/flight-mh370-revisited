cd /Users/pete/Downloads/flight-mh370-revisited
for b in origin/claude-science-sep29 origin/hypothesis/hydroacoustics origin/main; do echo "=== $b"; git grep -n -i -E "metz|s00024-022-03117" $b 2>/dev/null | grep -v -i "le bras\|lebras\|hunga" | sed "s|^$b:||" | cut -c1-230; done > /tmp/metz_all.txt
wc -l /tmp/metz_all.txt; cut -d: -f1 /tmp/metz_all.txt | sort | uniq -c | sort -rn | head -40
echo "=== exchange + inputs + review"
grep -rIl -i -E "metz" /Users/pete/Downloads/mh370-exchange /Users/pete/Downloads/mh370-inputs /Users/pete/Downloads/review 2>/dev/null | head -20