import base64, os
os.makedirs('rr/drive',exist_ok=True)
ids={'sir.txt':'1ZnLkEA271aezeLAjS-4IDLJ5jVRdaP9X','royer.txt':'1O4ldxVDSORNwJh0IWJG6ahpYOENX0ysy','hydroacoustics.txt':'1xJ7VOGotXup9YnWlamOMnu9ShKEkW1_a','assembled-hydroacoustics.txt':'1ZIT6FNLl1zzZ0aTdb88FFCtpR3MxXpRR','ig_malacca.pdf':'1v0OfkaVAC8lmXo0oJOxUz4WthzYxGcAz'}
for n,i in ids.items():
    try:
        r=host.mcp(S,"download_file_content",fileId=i)
        c=r.get('content') or r.get('base64Content') or r.get('data')
        if c is None: print(n, list(r.keys())); continue
        open('rr/drive/'+n,'wb').write(base64.b64decode(c)); print(n, os.path.getsize('rr/drive/'+n))
    except Exception as e: print(n,'ERR',str(e)[:300])