qs=["fullText contains 'revisiting MH370'","title contains 'Underwater acoustic'","title contains '60529'","fullText contains 'San Juan' and fullText contains 'hydroacoustic'","title contains 'Dall'","title contains 'Duncan'","title contains 'Heaney'","fullText contains 'Air France' and fullText contains 'hydrophone'","parentId = '1GuJIfdQQhEmN_iWX5aioWEfNWAs3xiTM'","parentId = '1YGIlIxKOHXoqGkFuq-CyS2zK6bu3dPVK'"]
res2={}
for q in qs:
    try:
        r=host.mcp(S,"search_files",query=q,pageSize=40,excludeContentSnippets=True)
        res2[q]=[(f.get('title'),f.get('id'),f.get('mimeType'),f.get('fileSize')) for f in r.get('files',[])]
    except Exception as e:
        res2[q]=str(e)[:200]
json.dump(res2,open('handoff_drive2.json','w'),indent=1)
for q,v in res2.items():
    print("##",q, len(v) if isinstance(v,list) else v)
    if isinstance(v,list):
        for x in v[:14]: print("  ",x[0][:90],x[1],x[3])