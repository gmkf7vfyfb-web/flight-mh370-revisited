S="directory-386b459a-697f-4d1c-9f1e-712c3841fada"
import json
for q in ["fullText contains 'Safety Investigation Report' and fullText contains '9M-MRO'",
          "title contains 'MH370'", "title contains 'SIR'", "fullText contains 'Emergency Locator Transmitter'",
          "fullText contains 'towed pinger locator'", "fullText contains 'barnacle'", "title contains 'Definition of Underwater'"]:
    try:
        r = host.mcp(S,"search_files",query=q,pageSize=30,excludeContentSnippets=True)
        print("==",q)
        for f in r.get('files',[]): print(' ',f['id'],f.get('fileSize'),f['title'])
    except Exception as e: print(q,e)