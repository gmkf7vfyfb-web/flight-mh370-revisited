import pandas as pd
hits=[]
for q in ['searched','posterior','pleiades','trajector','composer','seabed','sonar','source pdf','backtrack']:
    try:
        a=host.artifacts(search=q)
        for x in (a if isinstance(a,list) else a.get('artifacts',[])):
            hits.append((q, x.get('filename'), x.get('version_id'), str(x.get('created_at'))[:10]))
    except Exception as e: print(q,e)
H_=pd.DataFrame(hits,columns=['q','file','vid','date']).drop_duplicates('vid')
print(len(H_)); print(H_.sort_values('date',ascending=False).head(80).to_string())