
import pypdfium2 as pdfium, urllib.request, os
pdf = pdfium.PdfDocument("src/holland_arxiv_v3.pdf")
pages = [pdf[i].get_textpage().get_text_range() for i in range(len(pdf))]
open("src/holland.txt","w").write("\n\n===PAGE %d===\n\n".join([""]+pages))
# rewrite with markers
with open("src/holland.txt","w") as f:
    for i,t in enumerate(pages):
        f.write(f"\n\n===PAGE {i+1}===\n\n"+t)
print("holland pages", len(pages))

for url in ["https://link.springer.com/content/pdf/10.1007/978-981-10-0379-0.pdf",
            "https://library.oapen.org/bitstream/handle/20.500.12657/27976/1002023.pdf"]:
    try:
        with urllib.request.urlopen(url, timeout=120) as r:
            b = r.read()
        open("src/davey.pdf","wb").write(b); print("OK", url, len(b)); break
    except Exception as e:
        print("FAIL", url, type(e).__name__, str(e)[:150])
