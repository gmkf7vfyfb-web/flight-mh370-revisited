import base64, os
S="directory-386b459a-697f-4d1c-9f1e-712c3841fada"
r = host.mcp(S,"download_file_content",fileId='1XyxPBjlQ4vjVsd7Xl9W46I1xIdmQBvhJ')
b = r.get('content') if isinstance(r,dict) else None
open('src/ISASI2011_BEA.pdf','wb').write(base64.b64decode(b)); print(os.path.getsize('src/ISASI2011_BEA.pdf'))
for q in ["fullText contains 'underwater locator beacon' and fullText contains 'Yemenia'", "fullText contains 'Flight Data Recovery Working Group'", "fullText contains 'ULB' and fullText contains 'AF 447' and fullText contains 'battery'"]:
    rr = host.mcp(S,"search_files",query=q,pageSize=15,excludeContentSnippets=True)
    print('==',q); [print(' ',f['id'],f.get('fileSize'),f['title']) for f in rr.get('files',[])]