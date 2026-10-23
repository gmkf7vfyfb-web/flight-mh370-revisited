rows = host.query("SELECT idx, msg_json FROM frame_messages WHERE frame_id='a35831fe-107a-4961-bc9f-e6fd6d255601' ORDER BY idx")['rows']
from collections import Counter
c=Counter()
for idx,mj in rows:
    m=json.loads(mj); c[(m.get('role'), m.get('type'), tuple(sorted(m.keys()))[:6])]+=1
for k,v in c.most_common(12): print(v,k)
print(rows[2][1][:600])