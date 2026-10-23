import re
hits=[]
off=1450
while off<1633:
    r = host.frames(frame_id="d74bf70e-a424-46a9-8149-902d027e782a", offset=off, max_results=60)
    for i,m in enumerate(r["messages"]):
        t=json.dumps(m)
        for mm in re.finditer(r"search_windows\.py[^\"]{0,600}", t):
            hits.append((off+i, mm.group(0)[:700]))
    off=r.get("next_offset") or 1633
    if not r.get("truncated"): break
for h in hits:
    if "--runs" in h[1] or "eof-module" in h[1]: print(h[0], h[1][:700]); print('==')