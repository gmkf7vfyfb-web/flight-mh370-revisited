import json
def user_texts(fid):
    rows = host.query(f"SELECT idx, msg_json FROM frame_messages WHERE frame_id='{fid}' ORDER BY idx")['rows']
    out=[]
    for idx, mj in rows:
        try: m=json.loads(mj)
        except: continue
        if m.get('role')!='user': continue
        c=m.get('content')
        if isinstance(c,list):
            txt=' '.join(b.get('text','') for b in c if isinstance(b,dict) and b.get('type')=='text')
        else: txt=str(c)
        txt=txt.strip()
        if not txt or txt.startswith('[System]') and len(txt)<300: continue
        if 'tool_result' in mj[:200] and not txt: continue
        out.append((idx, txt))
    return out
lines=[]
for fid,name in [('d74bf70e-a424-46a9-8149-902d027e782a','old module thread'),('676a6e64-2eac-490f-b67d-6c3f5c82f047','module thread 21-22 Oct'),('a35831fe-107a-4961-bc9f-e6fd6d255601','critical review'),('0bb05edc-67da-48f0-9322-bf94577b110d','locate PDF')]:
    u=user_texts(fid)
    lines.append(f"\n######## {name} {fid} n={len(u)}")
    for idx,t in u:
        # strip memory recall / skill discovery blocks
        for marker in ['[Memory] <memory_recall','[System] <skill_discovery']:
            pass
        lines.append(f"\n--[{idx}] {t[:3000]}")
open('pete_msgs.txt','w').write('\n'.join(lines))
print([ (l[:80]) for l in lines if l.startswith('\n########')])