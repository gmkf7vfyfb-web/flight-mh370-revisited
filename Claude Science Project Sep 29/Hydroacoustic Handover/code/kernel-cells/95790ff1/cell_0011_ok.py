import json,base64,os
r=host.mcp("directory-386b459a-697f-4d1c-9f1e-712c3841fada","download_file_content",fileId="1xCqnNIVYuH1iF2OIFEnNgbtAMHbzekkU")
print(type(r), list(r.keys()) if isinstance(r,dict) else str(r)[:200])
os.makedirs("drive",exist_ok=True)
c=r.get("content") or r.get("data") or r.get("base64Content") if isinstance(r,dict) else None
if c is None and isinstance(r,dict):
    for k,v in r.items():
        if isinstance(v,str) and len(v)>1000: c=v
b=base64.b64decode(c); open("drive/blackman_receiver_observations.csv","wb").write(b); print(len(b))