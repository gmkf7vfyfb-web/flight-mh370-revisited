import json, os
S="directory-386b459a-697f-4d1c-9f1e-712c3841fada"
os.makedirs("handoff",exist_ok=True)
out={}
for k,fid in [("atsb2017","1zwSCCwXcsryJdi4kHb4WE13_9-WIb4J4"),("atsb2014jun","1lDHdjQhdoyiqRIck6Gkmdyur7g1ua_Lw")]:
    try:
        r=host.mcp(S,"read_file_content",fileId=fid)
        out[k]=r.get("fileContent","") if isinstance(r,dict) else str(r)
    except Exception as e:
        out[k]="ERR "+repr(e)[:300]
    print(k,len(out[k]))
json.dump(out,open("handoff/atsb_texts.json","w"))