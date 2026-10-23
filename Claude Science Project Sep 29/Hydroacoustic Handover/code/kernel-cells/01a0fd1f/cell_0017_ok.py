S="directory-386b459a-697f-4d1c-9f1e-712c3841fada"
import json
out={}
for q in ["title contains 'Safety Investigation'","title contains 'SIR'","title contains 'Underwater Search'","title contains 'Definition'","title contains 'OHASISBIO'","title contains 'Royer'","fullText contains 'Lhokseumawe'","fullText contains 'OHASISBIO'","title contains 'Blackman'","fullText contains 'EK343'"]:
    try:
        r=host.mcp(S,"search_files",query=q,excludeContentSnippets=True,pageSize=20)
        out[q]=[(f.get('title'),f.get('id'),f.get('fileSize'),f.get('mimeType')) for f in r.get('files',[])]
    except Exception as e: out[q]=str(e)[:200]
for k,v in out.items(): print(k, v)