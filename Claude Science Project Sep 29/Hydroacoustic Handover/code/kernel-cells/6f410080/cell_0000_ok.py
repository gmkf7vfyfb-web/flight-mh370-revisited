S="directory-386b459a-697f-4d1c-9f1e-712c3841fada"
import json
out={}
for q in ["title contains 'Operational Search'","fullText contains 'Pleiades'","fullText contains 'satellite imagery' and fullText contains 'MH370'","title contains 'Safety Investigation'","fullText contains 'THEOS'","fullText contains 'Gaofen'","title contains 'Minchin'","title contains 'AMSA'"]:
    try:
        r=host.mcp(S,"search_files",query=q,excludeContentSnippets=True,pageSize=20)
        out[q]=[(f.get('title'),f.get('id'),f.get('fileSize'),f.get('mimeType')) for f in r.get('files',[])]
    except Exception as e:
        out[q]=str(e)
for k,v in out.items():
    print(k)
    for x in (v if isinstance(v,list) else [v]): print('   ',x)