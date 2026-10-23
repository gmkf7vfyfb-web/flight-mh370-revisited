r=host.mcp(S,"read_file_content",fileId='1iwxd8kz_bvpHvXU4QYhRaF23zaG1ARiD')
open('handoff/csiro3.txt','w').write(r.get('fileContent',''))
print(len(r.get('fileContent','')))
for q in ["fullText contains 'WorldView'","fullText contains 'Gaofen'","fullText contains 'GISTDA'","fullText contains 'Tomnod'","title contains 'satellite imagery'","fullText contains '122 objects'","fullText contains 'Remote Sensing Agency'"]:
    try:
        rr=host.mcp(S,"search_files",query=q,excludeContentSnippets=True,pageSize=15)
        print(q,[(f.get('title'),f.get('id'),f.get('fileSize')) for f in rr.get('files',[])])
    except Exception as e: print(q,e)