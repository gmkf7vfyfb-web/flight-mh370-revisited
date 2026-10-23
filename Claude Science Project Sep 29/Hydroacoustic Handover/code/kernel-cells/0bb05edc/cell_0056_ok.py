
import json, re
d = json.load(open('handoff/flag_rows.json'))
items = d['flag_rows'] + [dict(e, open_access='', read_level='') for e in d['extra']]
out = {}
for it in items:
    doi = it['doi_or_url'] if it['doi_or_url'].startswith('10.') else None
    hits=[]
    qs=[]
    if doi: qs.append(f"fullText contains '{doi}' and mimeType = 'application/pdf'")
    # distinctive title phrase (first 7 words, strip punctuation)
    tw = re.sub(r"[^A-Za-z0-9 ]"," ", it['title']).split()
    if len(tw)>=4: qs.append("fullText contains '" + ' '.join(tw[:6]) + "' and mimeType = 'application/pdf'")
    for q in qs:
        try:
            r = host.mcp("google-drive","search_files", query=q, pageSize=8, excludeContentSnippets=True)
        except Exception as e:
            hits.append(('ERR', str(e)[:80])); continue
        for f in r.get('files',[]):
            hits.append((f['title'][:100], f['id'], f.get('fileSize'), f.get('modifiedTime','')[:10], 'doi' if q.startswith("fullText contains '10.") else 'title'))
    out[it['key']] = hits
json.dump(out, open('handoff/drive_fulltext_hits.json','w'))
print('done', len(out), sum(1 for v in out.values() if v))
