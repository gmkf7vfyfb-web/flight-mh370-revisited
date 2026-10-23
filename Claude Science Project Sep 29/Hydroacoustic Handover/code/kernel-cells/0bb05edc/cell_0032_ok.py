
qs = ["title contains 'Kadri'", "title contains 'Rewinding'", "title contains 'Underwater_acoustic'", "title contains 'Underwater Acoustic'",
      "fullText contains 'Usama Kadri'", "fullText contains 'Kadri' and mimeType = 'application/pdf'",
      "fullText contains 'Journal of the Acoustical Society of America' and fullText contains 'Kadri'", "title contains 'San Juan'", "title contains 'acoustic-gravity'"]
seen={}
for q in qs:
    for page in (None,):
        try:
            r = host.mcp("google-drive", "search_files", query=q)
        except Exception as e:
            print(q,"ERR",str(e)[:200]); continue
        for f in r.get('files', []):
            seen[f['id']] = (f.get('title'), f.get('mimeType'), f.get('fileSize'), f.get('modifiedTime','')[:10], f.get('parentId'))
print(len(seen))
import re
for k,v in sorted(seen.items(), key=lambda kv: str(kv[1][0])):
    t=v[0] or ''
    if v[1]=='application/pdf' or re.search('kadri|underwater|rewind|san juan|acoustic',t,re.I):
        print(k, v)
