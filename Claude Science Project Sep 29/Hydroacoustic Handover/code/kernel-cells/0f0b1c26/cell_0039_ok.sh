cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-digitisation/sources/; python - <<'EOF'
import pypdfium2 as pdfium, re
for f in ['nielsen2020.pdf','vergoz2021.pdf']:
    pdf=pdfium.PdfDocument(f); txt=[]
    for i in range(len(pdf)): txt.append(pdf[i].get_textpage().get_text_range())
    t="\n".join(f"=====P{i+1}\n"+x for i,x in enumerate(txt))
    open('/tmp/'+f+'.txt','w').write(t)
    print('##',f,len(pdf))
    for m in re.finditer(r'(?i)[^\n]{0,160}(TNT|kg|lb|yield|source level|dB re|depth charge|grenade|SL\b|Pa\b|amplitude|signal-to-noise|SNR)[^\n]{0,160}',t):
        print('  ',m.group(0)[:330].replace('\n',' '))
EOF