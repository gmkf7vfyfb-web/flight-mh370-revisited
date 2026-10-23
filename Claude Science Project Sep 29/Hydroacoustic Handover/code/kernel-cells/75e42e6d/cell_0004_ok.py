import base64, os
os.makedirs('src', exist_ok=True)
def dl(fid, name):
    try:
        r = host.mcp(S,"download_file_content",fileId=fid)
        b = r.get('content') or r.get('base64Content') or r.get('data') if isinstance(r,dict) else None
        if b is None: print(name, 'keys', list(r.keys()) if isinstance(r,dict) else type(r)); return
        open('src/'+name,'wb').write(base64.b64decode(b)); print(name, os.path.getsize('src/'+name))
    except Exception as e: print(name, 'ERR', str(e)[:300])
dl('1ZnLkEA271aezeLAjS-4IDLJ5jVRdaP9X','sir.txt')
dl('18nqWqo4W9ePq1dNOz9IS_akZ1JN7xtT7','App1.6D_ELT.pdf')
dl('1zFXrlDlFF230oZIYDcOV_hXS-8tFzuAQ','ATSB_ELT_AR-2012-128.pdf')
dl('18qGq9srq4OBNB-bnHHT-wa3mWWt_78M9','App2.6A_MarineBio1.pdf')
dl('1GsCmFa5Af6X9idD9WurJ4pQM-uWnQ298','App2.6B_MarineBio2.pdf')
dl('1TZAYXauEHlX1T2Uiyh6pmO-DGfox48Hw','FrenchJudiciary_article.pdf')
dl('1lDHdjQhdoyiqRIck6Gkmdyur7g1ua_Lw','ATSB_search_areas_30jul2015.pdf')
dl('1dYcGutFhcjvclPyJdP9p3nQQhdfEW4cV','GafferTape_OceanShield.html')