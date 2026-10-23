r=host.mcp(S,"download_file_content",fileId='1iwxd8kz_bvpHvXU4QYhRaF23zaG1ARiD')
b=r.get('content') if isinstance(r,dict) else r
open('pod/csiro3.pdf','wb').write(base64.b64decode(b)); print(os.path.getsize('pod/csiro3.pdf'))