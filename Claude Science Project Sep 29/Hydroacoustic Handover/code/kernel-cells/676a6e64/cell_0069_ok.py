def tail(fid, n=4):
    t = host.frames(frame_id=fid, max_results=1)
    tot = t['total_messages']
    t = host.frames(frame_id=fid, max_results=n, offset=max(0, tot-n))
    out=[]
    for m in t['messages']:
        c = m.get('content'); 
        txt = ' '.join(x.get('text','') for x in c if isinstance(x, dict) and x.get('type')=='text') if isinstance(c, list) else str(c)
        out.append(f"[{m.get('role')}] {txt[:700]}")
    return tot, out
for name, fid in [('Composition','c1f32191-7101-489b-8677-1367fdb83543'), ('RAM IMOS','ab0373ea-3460-46fd-87d0-112603723552')]:
    tot, out = tail(fid)
    print(f"===== {name} total_messages={tot}")
    for o in out: print(o); print('--')