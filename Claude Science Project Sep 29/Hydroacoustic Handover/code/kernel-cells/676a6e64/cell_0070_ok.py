def tail2(fid, n=6):
    t = host.frames(frame_id=fid, max_results=1); tot = t['total_messages']
    t = host.frames(frame_id=fid, max_results=n, offset=max(0, tot-n))
    out=[]
    for m in t['messages']:
        c = m.get('content')
        if isinstance(c, list):
            parts=[]
            for x in c:
                if not isinstance(x, dict): continue
                ty = x.get('type')
                if ty=='text': parts.append(x['text'][:400])
                elif ty=='tool_use': parts.append('TOOL_USE '+x.get('name','')+' '+str(x.get('input',{}))[:500])
                elif ty=='tool_result':
                    cc = x.get('content'); s = cc if isinstance(cc,str) else ' '.join(y.get('text','') for y in cc if isinstance(y,dict))
                    parts.append('RESULT '+s[:500])
            out.append(f"[{m.get('role')}] " + ' | '.join(parts))
        else: out.append(f"[{m.get('role')}] {str(c)[:400]}")
    return tot, out
for name, fid in [('Composition','c1f32191-7101-489b-8677-1367fdb83543'), ('RAM IMOS','ab0373ea-3460-46fd-87d0-112603723552')]:
    tot, out = tail2(fid)
    print(f"===== {name} total={tot}")
    for o in out: print(o[:900]); print('--')