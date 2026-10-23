out={}
for q in ["title contains 'ATSB'","title contains 'Search Areas'","title contains 'search area'","fullText contains 'Definition of Underwater Search Areas'","title contains 'AE-2014'","title contains 'Search and debris'","fullText contains 'IS06' or fullText contains 'I06AU'","fullText contains 'infrasound'"]:
    try:
        r=host.mcp(S,"search_files",query=q,excludeContentSnippets=True,pageSize=25)
        out[q]=[(f.get('title'),f.get('id'),f.get('fileSize')) for f in r.get('files',[])]
    except Exception as e: out[q]=str(e)[:200]
for k,v in out.items(): print(k, v,'\n')