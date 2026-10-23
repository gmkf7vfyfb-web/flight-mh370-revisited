for k,i in {'ulich':'10B8hIcV09s_6u2XfDVeuDyeR1Lto1z7X','sattools':'15qfNKk3pEt9KeVT4aGFCG733A5MIJoxJ'}.items():
    r=host.mcp(S,"read_file_content",fileId=i); t=r.get('fileContent',''); open(f'handoff/{k}.txt','w').write(t); print(k,len(t))
for q in ["fullText contains 'contrail' and fullText contains 'Meteosat'","title contains 'contrail'","fullText contains '370location' and fullText contains 'plume'","fullText contains 'Vasquez'"]:
    rr=host.mcp(S,"search_files",query=q,excludeContentSnippets=True,pageSize=20)
    print(q,[(f.get('title'),f.get('id'),f.get('fileSize')) for f in rr.get('files',[])])