print(t['total_messages'], t['truncated'], t['returned_range'], t['next_offset'])
msgs = t['messages']
print(msgs[0].keys())
out=[]
for m in msgs:
    role = m.get('role')
    c = m.get('content')
    if isinstance(c, list):
        txt = ' '.join(x.get('text','') for x in c if isinstance(x, dict) and x.get('type')=='text')
    else:
        txt = str(c)
    if txt.strip():
        out.append(f"### {role} [{m.get('created_at','')[:16]}]\n{txt}\n")
open('review_thread_text.md','w').write('\n'.join(out))
print(len(out), sum(len(o) for o in out))
