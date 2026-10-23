
import pypdfium2 as pdfium, re
d = pdfium.PdfDocument("src/davey.pdf")
dp = [d[i].get_textpage().get_text_range() for i in range(len(d))]
with open("src/davey.txt","w") as f:
    for i,t in enumerate(dp):
        f.write(f"\n\n===PDFPAGE {i+1}===\n\n"+t)
print("davey pdf pages", len(dp))
pat = re.compile(r"(fuel exhaust|end[- ]of[- ]flight|descent|glide|flaperon|NM of the|manoeuvre after)", re.I)
hits = [(i+1, len(pat.findall(t))) for i,t in enumerate(dp) if pat.search(t)]
print(hits)
