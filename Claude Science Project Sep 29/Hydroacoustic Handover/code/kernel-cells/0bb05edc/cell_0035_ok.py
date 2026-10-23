
import json,re
fid='d74bf70e'
pat=r"Metz"
off=0; hits=[]; calls=0
while True:
    r = host.frames(frame_id=fid, pattern=pat, include_tool_results=True, max_results=500, offset=off)
    calls+=1
    for i,m in enumerate(r['messages']):
        c=m.get('content'); txt = c if isinstance(c,str) else json.dumps(c)
        if 'without matches skipped' in txt and len(txt)<200: continue
        hits.append((r.get('returned_range'), m['role'], txt))
    if not r.get('truncated') or calls>40: break
    off = r.get('next_offset', off+500)
print(calls, len(hits))
key = re.compile(r"(unobtainable|closed (and|access)|not held|in hand|buying|purchas|bought|paywall)", re.I)
n=0
for rr, role, txt in hits:
    for mm in re.finditer(r"Metz", txt):
        seg = txt[max(0,mm.start()-120): mm.end()+240]
        if key.search(seg):
            print(rr, role, '|', seg.replace('\\n',' ')[:360]); n+=1; break
    if n>=14: break
