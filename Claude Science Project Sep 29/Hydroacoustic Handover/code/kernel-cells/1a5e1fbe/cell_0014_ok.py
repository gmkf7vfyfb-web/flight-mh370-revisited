S="directory-386b459a-697f-4d1c-9f1e-712c3841fada"
import json
out={}
for q in ["title contains 'CSIRO'","fullText contains 'AF447' and fullText contains 'Metron'","title contains 'first-principles' or title contains 'First Principles'","fullText contains 'operational search for MH370'"]:
    try:
        r=host.mcp(S,"search_files",query=q,excludeContentSnippets=True,pageSize=20)
        out[q]=[(f.get('title'),f.get('id'),f.get('fileSize')) for f in r.get('files',[])]
    except Exception as e: out[q]=str(e)
for k,v in out.items(): print(k); [print('  ',x) for x in (v if isinstance(v,list) else [v])]