import glob, pypdf
txt={}
for f in sorted(glob.glob('amsa/*.pdf')):
    if os.path.getsize(f)==0 or 'Akademik' in f or 'Antartica' in f or '406' in f: continue
    try:
        txt[f]='\n'.join((p.extract_text() or '') for p in pypdf.PdfReader(f).pages)
    except Exception as e: txt[f]='ERR '+str(e)
out=[]
for f,t in txt.items():
    if re.search(r'satellite|imagery|°|deg|south|latitude',t,re.I):
        out.append(f'##### {f}\n{t}')
open('handoff/amsa_releases.txt','w').write('\n'.join(out))
for f,t in txt.items(): print(f,len(t), bool(re.search('satellite',t,re.I)))