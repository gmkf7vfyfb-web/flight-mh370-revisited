import json
S="directory-386b459a-697f-4d1c-9f1e-712c3841fada"
qs=["title contains 'Kadri'","fullText contains 'AF447' and fullText contains 'hydroacoustic'","title contains 'AF447'","title contains 'San Juan'","title contains 'Vergoz'","title contains 'Nielsen'","fullText contains 'hydroacoustic'","title contains 'hydro'","title contains 'CTBTO'","title contains 'acoustic'","title contains 'Metz'","title contains 'published-figures'", "title contains '41598'","title contains 'Fig'" ]
res={}
for q in qs:
    try:
        r=host.mcp(S,"search_files",query=q,pageSize=50,excludeContentSnippets=True)
        res[q]=[(f.get('title'),f.get('id'),f.get('mimeType'),f.get('fileSize'),f.get('parentId')) for f in r.get('files',[])]
    except Exception as e:
        res[q]=str(e)[:300]
json.dump(res,open('handoff_drive.json','w'),indent=1)
for q,v in res.items():
    print("##",q, len(v) if isinstance(v,list) else v)
    if isinstance(v,list):
        for x in v[:25]: print("  ",x)