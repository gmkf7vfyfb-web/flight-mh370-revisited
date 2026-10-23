def ptxt(f):
    try: return '\n'.join((p.extract_text() or '') for p in pypdf.PdfReader(f).pages)
    except Exception as e: return 'ERR '+str(e)
import html as H
def htxt(f):
    t=open(f,errors='ignore').read()
    t=re.sub(r'<(script|style).*?</\1>','',t,flags=re.S|re.I)
    return re.sub(r'\s+',' ',H.unescape(re.sub(r'<[^>]+>',' ',t)))
docs={}
for f in sorted(glob.glob('mot/*'))+sorted(glob.glob('jacc/*'))+sorted(glob.glob('gistda/*')):
    if os.path.getsize(f)==0: continue
    docs[f]=ptxt(f) if f.endswith('.pdf') else htxt(f)
pat=re.compile(r'satellite imag|imagery|satellite.{0,40}(object|debris|image)|Thai|Japan|French|Airbus|MRSA|Remote Sensing|Gaofen|122|THEOS|Thaichote',re.I)
with open('handoff/mot_jacc_snips.txt','w') as out:
    for f,t in docs.items():
        hits=[m.start() for m in pat.finditer(t)]
        if not hits: continue
        out.write(f'\n######## {f}\n')
        last=-1
        for h in hits:
            if h<last: continue
            out.write('... '+t[max(0,h-400):h+600].replace('\n',' ')+'\n'); last=h+600
print(len(docs), os.path.getsize('handoff/mot_jacc_snips.txt'))
print([f for f in docs if pat.search(docs[f])])