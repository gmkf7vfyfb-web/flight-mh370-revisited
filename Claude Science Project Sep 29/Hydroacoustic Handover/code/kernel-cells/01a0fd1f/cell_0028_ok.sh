cd rr/drive; python - <<'EOF'
import re
L=open('atsb_search_areas.txt').read().split('\n')
def page(i):
    for j in range(i,-1,-1):
        m=re.match(r'=== PAGE (\d+) ===',L[j])
        if m: return m.group(1)
for n in [228,248,256,315,1282,1286,1337]: print(n,page(n-1),L[n-1][:100])
print('\n'.join(L[225:262]))
EOF