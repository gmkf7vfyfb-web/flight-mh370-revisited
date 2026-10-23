r=host.mcp(S,"download_file_content",fileId='1b01voYe_hxetXTV-wEBGtbDCVfiD1DNd')
b=r.get('content') if isinstance(r,dict) else r
open('pod/griffin2018.pdf','wb').write(base64.b64decode(b)); print(os.path.getsize('pod/griffin2018.pdf'))