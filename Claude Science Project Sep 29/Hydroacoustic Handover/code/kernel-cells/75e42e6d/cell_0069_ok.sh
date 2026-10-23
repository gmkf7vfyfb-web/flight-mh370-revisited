python - <<'EOF'
import re
p='research-beacons-tpl-simulator-barnacles.md'; t=open(p).read()
m={'5b7f237d':'8069288e-3f0c-4a73-aa46-dbe092ed3ddb','77988670':'d3a5c183-9d7c-446f-befa-121af7d8ade4','4a3bf081':'54902127-5d6e-42e9-b165-5a8d85e7f4de'}
def rep(mo):
    path=mo.group(1)
    for k,v in m.items():
        if '/'+k in path: return '({{'+'!artifact:'+v+'}})'
    return mo.group(0)
t2=re.sub(r'\((/Users/pete/[^)]+artifacts/[^)]+)\)',rep,t)
open(p,'w').write(t2)
print(t2.count('!artifact:'), '/Users/pete' in t2)
EOF