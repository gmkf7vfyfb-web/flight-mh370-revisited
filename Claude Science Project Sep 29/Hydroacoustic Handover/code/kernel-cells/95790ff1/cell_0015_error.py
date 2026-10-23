import pypdfium2 as pdfium, os, PIL
pdfp="repo/ISO Sept 28 Status/inputs/papers/hydroacoustics/ucrl-tr-207323.pdf"
doc=pdfium.PdfDocument(pdfp)
os.makedirs("pages",exist_ok=True)
for pn in range(1,35):
    img=doc[pn-1].render(scale=300/72).to_pil()
    img.save(f"pages/p{pn:02d}.png")
print(pdfium.V_PYPDFIUM2, pdfium.V_PDFIUM, PIL.__version__, img.size)
for pn in (25,26):
    im=PIL.Image.open(f"pages/p{pn:02d}.png"); print(pn, im.size)