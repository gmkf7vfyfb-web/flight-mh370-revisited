for n,i in {'atsb_search_areas.pdf':'1lDHdjQhdoyiqRIck6Gkmdyur7g1ua_Lw','bharat_rakshak.pdf':'1xq5fWd3mslUMGyZF0lAgUoW0xnNTztAh','iannello_safety_report.pdf':'16JydYyyM32GrWI9jdwa7Aek1tDXpAnCF'}.items():
    try:
        r=host.mcp(S,"download_file_content",fileId=i)
        c=r.get('content') or r.get('base64Content') or r.get('data')
        open('rr/drive/'+n,'wb').write(base64.b64decode(c)); print(n, os.path.getsize('rr/drive/'+n))
    except Exception as e: print(n,'ERR',str(e)[:300])