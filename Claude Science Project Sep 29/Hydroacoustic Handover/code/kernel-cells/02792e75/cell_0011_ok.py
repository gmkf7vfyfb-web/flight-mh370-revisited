import base64, os
os.makedirs("src",exist_ok=True)
ids={"atsb2017_operational_search.pdf":"1zwSCCwXcsryJdi4kHb4WE13_9-WIb4J4",
"atsb2014_search_areas_30jul2015.pdf":"1lDHdjQhdoyiqRIck6Gkmdyur7g1ua_Lw",
"amsa_reports_search.pdf":"1w6c_lgv8IKH5YXEDoETST5v2uoW9H8oD",
"icao_ai6_wp30.pdf":"1DJG-kkcV5JiofBZQFA0YCVnajIrwcIWJ",
"ulich2018_north25S.pdf":"1yRDZNpqGJonOWS4ZFBwcB1jbmKzw-Sai",
"mot2015_factual_information.pdf":"1P77F067zbrYdekEctQBzv9mGeFURUfG5",
"sir2018.pdf":"1eXn_nXdxnIL2xDNEJIMJaQRmLc02iId5",
"possible_debris_aerial_march2014.pdf":"1k1spe4FTmfO7bJfbY5we03Wl9pJeWlQn"}
for fn,i in ids.items():
    try:
        r=host.mcp(S,"download_file_content",fileId=i)
        b=None
        if isinstance(r,dict):
            for k in ("content","base64Content","data","blob"):
                if k in r: b=r[k];break
            if b is None: print(fn,"keys",list(r.keys())[:10]); continue
        else: b=r
        open("src/"+fn,"wb").write(base64.b64decode(b)); print(fn,os.path.getsize("src/"+fn))
    except Exception as e: print(fn,"ERR",str(e)[:200])