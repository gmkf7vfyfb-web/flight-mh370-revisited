import base64, os, hashlib
os.makedirs('src',exist_ok=True)
def dl(fid, name):
    r=host.mcp(S,"download_file_content",fileId=fid)
    if isinstance(r,dict):
        b=r.get('content') or r.get('base64Content') or r.get('data')
        if b is None:
            return ('keys',list(r.keys())[:10])
    else:
        b=r
    data=base64.b64decode(b)
    open('src/'+name,'wb').write(data)
    return (name,len(data),hashlib.sha256(data).hexdigest()[:16], data[:5])
for fid,name in [('1ZxR_3Y6Ryn-OXyRJ0tjOPSjassZn8ioW','kadri2024_drive.pdf')]:
    try: print(dl(fid,name))
    except Exception as e: print('ERR',str(e)[:400])