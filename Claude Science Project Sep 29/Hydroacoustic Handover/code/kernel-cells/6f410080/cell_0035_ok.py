import base64
r=host.mcp(S,"download_file_content",fileId='17J6pJ38bw0y6SleSEuBv3XtepbKMr0RA')
keys=list(r.keys()) if isinstance(r,dict) else type(r)
print(keys)
b=r.get('content') or r.get('base64Content') or r.get('data')
open('handoff/ckpt18.zip','wb').write(base64.b64decode(b)); print('ok')