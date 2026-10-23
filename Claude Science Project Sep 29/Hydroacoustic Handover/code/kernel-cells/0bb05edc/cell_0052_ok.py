
import json, os, time
os.makedirs('handoff', exist_ok=True)
SERVER = "google-drive"
allf = {}
def sweep(query, tag):
    tok=None; pages=0
    while True:
        kw = dict(query=query, pageSize=100, excludeContentSnippets=True)
        if tok: kw['pageToken']=tok
        try:
            r = host.mcp(SERVER, "search_files", **kw)
        except Exception as e:
            print(tag, 'ERR', str(e)[:200]); break
        for f in r.get('files', []):
            allf[f['id']] = {k: f.get(k) for k in ('id','title','mimeType','fileSize','parentId','modifiedTime')}
        pages+=1
        tok = r.get('nextPageToken')
        if not tok or pages>60: break
    print(tag, 'pages', pages, 'total', len(allf))
sweep("mimeType = 'application/pdf'", 'pdf')
sweep("mimeType = 'application/vnd.google-apps.document'", 'gdoc')
sweep("mimeType = 'text/plain' or mimeType = 'text/markdown'", 'txt')
json.dump(list(allf.values()), open('handoff/drive_index.json','w'))
print('saved', len(allf))
