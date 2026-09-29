import sys, pypdf
r = pypdf.PdfReader(sys.argv[1])
out = []
for i, p in enumerate(r.pages):
    try:
        t = p.extract_text() or ''
    except Exception as e:
        t = f'[extract error {e}]'
    out.append(f'--- page {i+1} ---\n{t}')
open(sys.argv[2], 'w').write('\n'.join(out))
print(len(r.pages), 'pages')
