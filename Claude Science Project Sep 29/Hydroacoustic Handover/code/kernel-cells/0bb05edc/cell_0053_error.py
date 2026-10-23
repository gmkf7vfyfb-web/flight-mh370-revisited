
import json, re, unicodedata, collections, os
drive = json.load(open('handoff/drive_index.json'))
dpdf = [d for d in drive if d['mimeType']=='application/pdf']
print(len(drive), len(dpdf))
STOP=set("the of and in on for to a an with from by at as is are using use via their its into over under between during after before than that this these those new study analysis effect effects based model models method methods case data case".split())
def norm(s): 
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+',' ',s).strip()
def toks(s): return [w for w in norm(s).split() if w not in STOP and len(w)>2]
# artifact store PDFs (via repl later) -> read from local db file? use stored list from earlier query later
def doi_key(doi):
    d=doi.lower(); d=re.sub(r'^https?://(dx\.)?doi\.org/','',d); return re.sub(r'[^a-z0-9]+','',d)
local = [(os.path.basename(p), p) for p,_ in pdfs]
repo = json.load(open('handoff/repo_pdfs.json'))
def candidates_for(rec):
    sur = norm(rec['authors'].split(',')[0].split(';')[0]).split()
    sur = sur[0] if sur else ''
    tt = set(toks(rec['title']))
    hits=[]
    dk = doi_key(rec['doi']) if rec['doi'].startswith('10.') else None
    pools = [('drive', [(d['title'], d['id']) for d in dpdf]), ('local', local), ('repo', [(os.path.basename(x), x) for x in repo])]
    for pool, items in pools:
        for name, ref in items:
            n=norm(name); nk=re.sub(r'[^a-z0-9]+','',name.lower())
            score=0; why=[]
            if dk and dk in nk: score+=10; why.append('doi-in-name')
            nt=set(toks(name))
            ov=len(tt & nt)
            frac = ov/max(1,len(tt))
            if ov>=3 and frac>=0.5: score+=6; why.append(f'title {ov}/{len(tt)}')
            elif ov>=2 and frac>=0.6: score+=4; why.append(f'title {ov}/{len(tt)}')
            if sur and sur in n.split() and rec['year'] and rec['year'] in n: score+=4; why.append('surname+year')
            elif sur and len(sur)>3 and sur in n.split() and ov>=1: score+=3; why.append('surname+word')
            if score>=4: hits.append((score,pool,name[:90],ref,'; '.join(why)))
    hits.sort(key=lambda x:-x[0])
    return hits[:4]
cands=[{'key':r['key'],'authors':r['authors'],'year':r['year'],'title':r['title'],'doi':r['doi_or_url'],'oa':r['open_access'],'read':r['read_level'],'src':'hydro-bibliography'} for r in rows]
res={}
for rec in cands:
    res[rec['key']]=candidates_for(rec)
held=[k for k,v in res.items() if v]
print('with candidate matches:', len(held), 'of', len(cands))
for rec in cands:
    h=res[rec['key']]
    flagged = rec['oa'].lower().startswith(('closed','unknown','not public')) or re.search(r'metadata|abstract|snippet|secondary',rec['read'],re.I)
    if h and flagged:
        print(f"{rec['key']:20s} oa={rec['oa'][:12]:12s} read={rec['read'][:22]:22s} -> ", [(x[0],x[1],x[2][:55],x[4]) for x in h[:2]])
