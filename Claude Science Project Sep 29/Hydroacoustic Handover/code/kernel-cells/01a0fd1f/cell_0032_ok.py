fid='1oNz_mS9YlpcV7ONudQNp_HwsUBvhNLmc'
try:
    m=host.mcp(S,"get_file_metadata",fileId=fid,excludeContentSnippets=True)
    print({k:m.get(k) for k in ['title','fileSize','mimeType','owner','createdTime','modifiedTime']})
    r=host.mcp(S,"download_file_content",fileId=fid)
    c=r.get('content') or r.get('base64Content') or r.get('data')
    open('rr/royer2016.pdf','wb').write(base64.b64decode(c)); print(os.path.getsize('rr/royer2016.pdf'))
except Exception as e: print('ERR',str(e)[:400])