fid=t['frame_id']
allm = list(msgs)
off = t['next_offset']
while off is not None:
    tt = host.frames(frame_id=fid, offset=off)
    allm += tt['messages']
    off = tt.get('next_offset') if tt.get('truncated') else None
print(len(allm))
out=[]
for m in allm:
    role = m.get('role'); c = m.get('content')
    if isinstance(c, list):
        txt = ' '.join(x.get('text','') for x in c if isinstance(x, dict) and x.get('type')=='text')
    else: txt = str(c)
    if txt.strip(): out.append(f"### {role}\n{txt}\n")
open('review_thread_text.md','w').write('\n'.join(out))
print(len(out), sum(len(o) for o in out))
