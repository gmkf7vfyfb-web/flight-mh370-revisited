
import os, re, collections, json
ROOT=os.path.abspath('fix-metz'); P=os.path.join(ROOT,'Claude Science Project Sep 29')
GEN_SKIP=('results/hydroacoustics-graphics-2026-10-22/',)   # generated products documented against their CSV/chart outputs
def files(ext):
    for dp,dn,fn in os.walk(P):
        for f in fn:
            if f.endswith(ext): yield os.path.join(dp,f)
rel=lambda p: os.path.relpath(p,P)
# 1. DO NOT USE fig10-3 bullets
pat1=re.compile(r"^- DO NOT USE: `fig10-3-bfo-latitude-pdf\.csv`.*\n",re.M)
d1={}
for p in files('.md'):
    t=open(p,encoding='utf-8',newline='').read()
    n=len(pat1.findall(t))
    if n: d1[rel(p)]=n
print('1. fig10-3 DO NOT USE bullets:', sum(d1.values()), 'in', len(d1),'files:', sorted(d1))
# 2. map captions
pat2=re.compile(r"\s*Do not use (these maps for a search|them as a result|these maps for a search)\.?")
d2={}
for p in files('.py'):
    t=open(p,encoding='utf-8',newline='').read()
    n=len(pat2.findall(t))
    if n: d2[rel(p)]=n
print('2. map-caption sentences in figure scripts:', sum(d2.values()), d2)
# 3. 'not held' in md prose (dry run, with exclusions)
pat3=re.compile(r"\b(not held|NOT held|Not held)\b(?! out| behind| at a band| fixed| constant| back)")
ctxs=collections.Counter(); per=collections.Counter(); skipped=[]
for p in files('.md'):
    r=rel(p)
    if r.startswith(GEN_SKIP): skipped.append(r); continue
    t=open(p,encoding='utf-8',newline='').read()
    for i,line in enumerate(t.split('\n')):
        if '"not held"' in line or '“not held”' in line or 'closed access' in line or 'STANDING RULE' in line: continue
        for m in pat3.finditer(line):
            per[r]+=1; ctxs[(line[max(0,m.start()-45):m.start()].strip(), line[m.end():m.end()+30])]+=1
print('3. not held in md prose:', sum(per.values()),'in',len(per),'files; skipped generated dirs:', sorted(set(skipped)))
for (a,b),n in list(ctxs.items())[:70]: print(f'   ..{a} [not held]{b}')
