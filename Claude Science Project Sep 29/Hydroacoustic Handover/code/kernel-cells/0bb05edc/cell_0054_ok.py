
bib = list(csv.DictReader(io.StringIO(show(f'{P}/results/hydroacoustics-bibliography.csv').replace('\r',''))))
cands=[{'key':r['key'],'authors':r['authors'],'year':r['year'],'title':r['title'],'doi':r['doi_or_url'],'oa':r['open_access'],'read':r['read_level'],'src':'hydro-bibliography'} for r in bib]
res={rec['key']:candidates_for(rec) for rec in cands}
print('with candidate matches:', sum(1 for v in res.values() if v), 'of', len(cands))
for rec in cands:
    h=res[rec['key']]
    flagged = rec['oa'].lower().startswith(('closed','unknown','not public')) or re.search(r'metadata|abstract|snippet|secondary',rec['read'],re.I)
    if h and flagged:
        print(f"{rec['key']:20s} oa={rec['oa'][:10]:10s} read={rec['read'][:18]:18s} -> ", [(x[0],x[1],x[2][:60],x[4]) for x in h[:2]])
