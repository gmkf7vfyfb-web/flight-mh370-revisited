import os, time
os.makedirs('amsa',exist_ok=True)
sel=[x for x in rows if ('/media/documents/' in x[0] and ('MH370' in x[0] or 'Update' in x[0])) or 'day3-2014-03-20' in x[0] and x[0].endswith('.pdf') or 'day4' in x[0] or ('mh370' in x[0].lower() and x[0].endswith('.pdf'))]
res={}
for orig,ts,sc in sel:
    fn='amsa/'+orig.split('/')[-1]
    if os.path.exists(fn): continue
    u=f'http://web.archive.org/web/{ts}id_/{orig}'
    try:
        rr=requests.get(u,timeout=60)
        open(fn,'wb').write(rr.content); res[fn]=(rr.status_code,len(rr.content))
    except Exception as e: res[fn]=str(e)[:80]
for k,v in res.items(): print(k,v)
try:
    import pypdf; print('pypdf',pypdf.__version__)
except Exception as e: print(e)