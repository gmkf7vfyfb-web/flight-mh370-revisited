r=host.mcp(S,"download_file_content",fileId='1DJG-kkcV5JiofBZQFA0YCVnajIrwcIWJ')
b=r.get('content') if isinstance(r,dict) else r
open('pod/icao_wp30.pdf','wb').write(base64.b64decode(b)); print(os.path.getsize('pod/icao_wp30.pdf'))