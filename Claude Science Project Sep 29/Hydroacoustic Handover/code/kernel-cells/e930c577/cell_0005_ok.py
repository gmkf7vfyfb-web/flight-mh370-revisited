import json
q="SELECT id, body FROM memories WHERE id IN (%s)"%",".join("?"*len(ids))
r=host.query(q,params=ids)
import os; os.makedirs('handoff',exist_ok=True)
with open('handoff/mem.txt','w') as f:
    for i,b in r['rows']: f.write(f"## {i}\n{b}\n\n")
print(r['row_count'], sum(len(b) for _,b in r['rows']))
