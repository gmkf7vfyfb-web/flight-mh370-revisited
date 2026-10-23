import zipfile, io
z=zipfile.ZipFile(host.artifact_path('81044812-7f45-482b-b0c1-98dfae20fee6'))
names=z.namelist(); print(len(names), names[:5])
for n in names:
    if not n.lower().endswith('.pdf'): continue
    try:
        dd=pymupdf.open(stream=z.read(n),filetype='pdf'); t=' '.join(p.get_text() for p in dd)
    except Exception as e: continue
    t=re.sub(r'\s+',' ',t)
    for m in re.finditer(r'[^.]*(weather|sea state|visibility|suspend|fog|cloud|swell|wind)[^.]*\.',t,re.I):
        print(n.split('/')[-1][:45],'||',m.group(0).strip()[:230])