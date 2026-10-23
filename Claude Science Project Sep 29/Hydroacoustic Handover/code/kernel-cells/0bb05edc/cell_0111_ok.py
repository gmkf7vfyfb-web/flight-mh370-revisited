
import os, re, collections
ROOT=os.path.abspath('fix-metz'); P=os.path.join(ROOT,'Claude Science Project Sep 29')
APPROVED="not retrieved — ask Pete"
reps=[
 (r"there is no copy of the paper or of LaCasce \(2008\) in the project store yet, so this is a library request for Pete", "the paper and LaCasce (2008) are "+APPROVED+" (library request)"),
 (r"\*\*No copy in the project store yet\.\*\*", "**Not retrieved — ask Pete.**"),
 (r"\*\*No copy in the project store yet\*\*", "**Not retrieved — ask Pete**"),
 (r"\*\*Abstract only in the project store\*\*", "**Abstract only; the full paper is not retrieved — ask Pete**"),
 (r"no copy in the project store yet", APPROVED),
 (r"no copy in the project store", APPROVED),
 (r"no copy in the store yet", APPROVED),
 (r"no copy in the store", APPROVED),
 (r"no copy in store", APPROVED),
 (r"NO COPY IN STORE", APPROVED),
 (r"No copy of the\nthree is in the project store;", "The\nthree are "+APPROVED+";"),
]
targets=[]
for dp,dn,fn in os.walk(P):
    for f in fn:
        if f.endswith(('.md','.csv','.txt','.py','.json')):
            targets.append(os.path.join(dp,f))
changed=collections.Counter(); ctx=collections.Counter()
for p in targets:
    try: t=open(p,encoding='utf-8',newline='').read()
    except Exception: continue
    o=t
    for pat,rep in reps:
        t=re.sub(pat,rep,t)
    if t!=o:
        for m in re.finditer(re.escape(APPROVED), t):
            ctx[(t[max(0,m.start()-28):m.start()].replace('\n',' '), t[m.end():m.end()+26].replace('\n',' '))]+=1
        open(p,'w',encoding='utf-8',newline='').write(t); changed[os.path.relpath(p,P)]=len(re.findall(re.escape(APPROVED),t))
print(len(changed),'files changed'); 
for k,v in changed.most_common(30): print(' ',v,k)
print(len(ctx),'distinct contexts')
for (a,b),n in list(ctx.items())[:60]: print(f'..{a}[{APPROVED}]{b}..')
