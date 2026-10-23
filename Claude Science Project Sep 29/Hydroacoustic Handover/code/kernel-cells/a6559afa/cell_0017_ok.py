def human(m):
    if m['role']!='user': return None
    c=m['content']
    texts=[b.get('text','') for b in c if isinstance(b,dict) and b.get('type')=='text'] if isinstance(c,list) else [str(c)]
    keep=[]
    for t in texts:
        s=t.strip()
        if s.startswith('[System]') or s.startswith('[Memory]') or s.startswith('[Auditor]') or s.startswith('(recalled') or s.startswith('<') : continue
        if s.startswith('[From ') : continue
        keep.append(s)
    return '\n'.join(keep) if keep else None
out=[]
cnt={}
for fid,ms in store.items():
    n=0
    out.append(f"\n######## {fid}")
    for i,m in enumerate(ms):
        h=human(m)
        if h and len(h)>2:
            n+=1; out.append(f"\n--[{i}] {h[:2500]}")
    cnt[fid[:8]]=n
open('pete_full.txt','w').write('\n'.join(out))
print(cnt, sum(len(x) for x in out))