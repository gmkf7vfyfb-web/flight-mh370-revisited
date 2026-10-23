cd rr/drive; python - <<'EOF'
import re
L=open('sir.txt',encoding='utf-8',errors='ignore').read().split('\n')
def page(i):
    for j in range(i,-1,-1):
        m=re.match(r'--- page (\d+) ---',L[j])
        if m: return m.group(1)
for a,b in [(15610,15632),(14100,14116)]:
    print('#### PDF page',page(a)); print('\n'.join(x for x in L[a:b] if x.strip()))
EOF
head -30 ig_malacca.txt; sed -n 2480,2500p ig_malacca.txt; sed -n 2596,2610p ig_malacca.txt; grep -n -E "^(@|Richard|Posted|[A-Z][a-z]+ [0-9]+, 20[0-9]{2})" ig_malacca.txt | sed -n 1,5p; grep -n -B2 "38 NM behind" ig_malacca.txt | head; grep -n -E "201[0-9] at" ig_malacca.txt | sed -n '1,3p;' 