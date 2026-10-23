r=host.artifacts(content_type="application/pdf", limit=200, project_id="all")
print(r['count'], r.get('truncated'))
import re
for a in r['artifacts']:
    fn=a['filename']
    if re.search(r'(?i)kadri|af447|san.?juan|vergoz|nielsen|hydro|acoust|ctbto|sofar|bea|dall|duncan|metz|f-?35|heaney|tolstoy|cmst|royer|blackman|jasa|seism', fn):
        print(fn, a['latest_version_id'], a['size_bytes'], a['project_id'])