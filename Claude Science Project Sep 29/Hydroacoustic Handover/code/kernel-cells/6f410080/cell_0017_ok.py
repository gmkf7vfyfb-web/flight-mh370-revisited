rr=host.mcp(S,"search_files",query="parentId = '1buQcueTInf336OgmSKsj1sPZ8yNnHYju'",excludeContentSnippets=True,pageSize=50)
for f in rr.get('files',[]): print(f.get('title'),f.get('id'),f.get('fileSize'),f.get('mimeType'))
for k,i in {'fluid':'1o0osNYLIIxnO-12EZMP3zY4N5PsLdhlG','sightings':'15XeBHoBA3C7LCQwwfTBH3KV1snUStecu'}.items():
    try:
        r=host.mcp(S,"read_file_content",fileId=i); open(f'handoff/{k}.txt','w').write(r.get('fileContent','')); print(k,len(r.get('fileContent','')))
    except Exception as e: print(k,e)