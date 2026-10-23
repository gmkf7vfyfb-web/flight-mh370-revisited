
import json,re
hits=[]
for off in range(1700,2144,100):
    r=host.frames(frame_id="d74bf70e", offset=off, max_results=100)
    for i,m in enumerate(r['messages']):
        s=json.dumps(m)
        if 'scenario_markers' in s and ('json.dump' in s):
            hits.append((off+i,len(s)))
            open(f'audit/lineage/msg_{off+i}.json','w').write(s)
print(hits)
