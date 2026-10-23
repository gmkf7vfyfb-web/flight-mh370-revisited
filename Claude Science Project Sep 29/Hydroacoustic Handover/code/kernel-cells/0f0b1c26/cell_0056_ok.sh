mkdir -p k17; python - <<'EOF'
import pypdfium2 as pdfium, re
f='articles/10.1038_s41598-017-14177-3.pdf'
pdf=pdfium.PdfDocument(f); print(len(pdf))
t="\n".join(f"=====P{i+1}\n"+pdf[i].get_textpage().get_text_range() for i in range(len(pdf)))
open('k17/kadri2017.txt','w').write(t)
for m in re.finditer(r'(?i)[^\n]{0,200}(filter|band|Hz|window|sampl|spectrogram|detect|threshold)[^\n]{0,200}',t):
    s=m.group(0).replace('\r','')
    if len(s)>40: print('-',s[:380])
EOF