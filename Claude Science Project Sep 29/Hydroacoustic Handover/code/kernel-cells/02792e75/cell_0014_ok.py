import pypdfium2 as pdfium, re, os, json
os.chdir(os.path.expanduser(os.getcwd()))
texts={}
for fn in sorted(os.listdir("src")):
    if fn.endswith(".pdf") and os.path.getsize("src/"+fn)>10000:
        try:
            pdf=pdfium.PdfDocument("src/"+fn); texts[fn]=[pdf[i].get_textpage().get_text_range() for i in range(len(pdf))]
        except Exception as e: print(fn,e)
texts["atsb2017_text.txt"]=[open("src/atsb2017_text.txt").read()]
pat=re.compile(r"Haixun|white object|90 km|Echo|Tireless|37\.5",re.I)
hits=[]
for fn,pages in texts.items():
    for i,p in enumerate(pages):
        for m in pat.finditer(p):
            hits.append((fn,i+1,m.group(0)))
from collections import Counter
print({fn:len(p) for fn,p in texts.items()})
print(Counter((h[0],h[2].lower()) for h in hits))