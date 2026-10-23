f=[x for x in docs if 'Maps' in x][0]
rd=pypdf.PdfReader(f); print(len(rd.pages))
for i,p in enumerate(rd.pages): print(i, re.sub(r'\s+',' ',p.extract_text()))
import shutil; shutil.copy(f,'mrsa_map_26mar2014.pdf')
try:
    import fitz
    d=fitz.open(f)
    for i,pg in enumerate(d): pg.get_pixmap(dpi=110).save(f'mrsa_p{i}.png')
    print('fitz ok')
except ImportError: print('no fitz')