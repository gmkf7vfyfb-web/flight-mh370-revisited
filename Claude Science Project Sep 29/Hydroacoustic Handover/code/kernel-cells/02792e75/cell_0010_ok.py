import json
S="directory-386b459a-697f-4d1c-9f1e-712c3841fada"
out={}
for q in ["title contains 'Operational'","title contains 'Underwater Search'","title contains 'Definition'","title contains 'Factual'","title contains 'Safety Investigation'","title contains 'JACC'","title contains 'AE-2014-054'","fullText contains 'Haixun'"]:
    try:
        r=host.mcp(S,"search_files",query=q,excludeContentSnippets=True,pageSize=20)
        out[q]=[(f.get('title'),f.get('id'),f.get('mimeType'),f.get('fileSize')) for f in r.get('files',[])]
    except Exception as e: out[q]=str(e)
for k,v in out.items():
    print(k); [print("  ",x) for x in v] if isinstance(v,list) else print("  ",v)