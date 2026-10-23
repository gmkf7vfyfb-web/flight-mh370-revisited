cd /Users/pete/Downloads
echo "=== Downloads/ (kadri in name, any depth)"; find . \( -iname "*kadri*" \) -not -path "*/node_modules/*" 2>/dev/null | grep -i -E "\.(pdf|txt|docx|md)$" | head -40
echo "=== PDFs whose first-page text mentions Kadri / known Kadri titles"
python3 - <<'EOF'
import subprocess, glob, os, re
cands=[]
for root in ['/Users/pete/Downloads/mh370-exchange/hydroacoustics','/Users/pete/Downloads/mh370-inputs/hydroacoustics','/Users/pete/Downloads/review']:
    for dp,dn,fn in os.walk(root):
        for f in fn:
            if f.lower().endswith('.pdf'): cands.append(os.path.join(dp,f))
print(len(cands),"PDFs scanned")
try:
    import pypdf
except ImportError:
    pypdf=None
for p in sorted(cands):
    try:
        r=pypdf.PdfReader(p); t=(r.pages[0].extract_text() or '')[:600].replace('\n',' ')
    except Exception as e:
        t='ERR '+str(e)[:40]
    if re.search(r'kadri|underwater acoustic analysis|aircraft crash|airplane crash|abstract',t,re.I) and re.search(r'kadri|acoustic|crash',t,re.I):
        print(os.path.relpath(p,'/Users/pete/Downloads'),'|',len(r.pages),'pp |',t[:170])
EOF