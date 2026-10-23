
import pypdfium2 as pdfium, re, os
def extract(p, out):
    d = pdfium.PdfDocument(p)
    t=[d[i].get_textpage().get_text_range() for i in range(len(d))]
    with open(out,"w") as f:
        for i,x in enumerate(t): f.write(f"\n\n===PAGE {i+1}===\n\n"+x)
    return t
bl = extract("src/blelly_marchand_analysis.pdf","src/blelly.txt")
sl = extract("src/mot_sir_slides.pdf","src/mot_slides.txt")
print("blelly pages",len(bl),"slides",len(sl))
pat=re.compile(r"(ditch|glide|L/D|lift-to-drag|touchdown|vertical speed|fpm|flare|impact|drift ?down|45 ?Nm|arc 7)",re.I)
print([i+1 for i,t in enumerate(bl) if pat.search(t)])
print([i+1 for i,t in enumerate(sl) if pat.search(t)])
