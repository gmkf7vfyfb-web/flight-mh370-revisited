python - <<'E'
import json
m=json.load(open('thread676.json'))
out=[]
for i,x in enumerate(m):
    c=x['content']
    if isinstance(c,list):
        t='\n'.join(b.get('text','') for b in c if isinstance(b,dict) and b.get('type')=='text')
    else: t=str(c)
    if not t.strip(): continue
    if x['role']=='user' and t.startswith('[System]') : t=t[:300]
    out.append(f"#### {i} {x['role']}\n{t}")
open('thread676.txt','w').write('\n\n'.join(out))
print(len(out))
E
wc -c thread676.txt; grep -n "#### .* user" thread676.txt | tail -40