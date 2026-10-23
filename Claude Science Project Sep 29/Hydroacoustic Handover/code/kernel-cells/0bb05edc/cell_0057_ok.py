
hits = json.load(open('handoff/drive_fulltext_hits.json'))
allrec = {r['key']:r for r in flag_rows}
for e in extra: allrec[e['key']]=dict(e, open_access='', read_level='')
# Drive PDFs that cite a DOI are often big review PDFs/reference lists; report by hit-type
doi_hits = {k:[h for h in v if len(h)>4 and h[4]=='doi'] for k,v in hits.items()}
n=0
for k,v in doi_hits.items():
    if v:
        n+=1
        print(f"{k:22s}", [(h[0][:60],h[2]) for h in v[:3]])
print(n,'sources with a DOI full-text hit')
print('title-only hit sources:')
for k,v in hits.items():
    t=[h for h in v if len(h)>4 and h[4]=='title']
    if t and not doi_hits[k]: print(f"{k:22s}", [(h[0][:60],h[2]) for h in t[:2]])
