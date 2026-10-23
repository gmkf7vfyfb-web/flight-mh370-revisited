cd rr/drive; python - <<'EOF'
import re
L=open('sir.txt',encoding='utf-8',errors='ignore').read().split('\n')
def page(i):
    for j in range(i,-1,-1):
        m=re.match(r'--- page (\d+) ---',L[j])
        if m: return m.group(1)
for a,b in [(2355,2385),(3035,3075),(14820,14845)]:
    print('#### PDF page',page(a)); print('\n'.join(x for x in L[a:b] if x.strip()))
hits=[i for i,x in enumerate(L) if re.search(r'military radar|Military radar|primary radar|Primary radar|18:22|1822',x)]
print([ (i,page(i)) for i in hits][:60])
EOF