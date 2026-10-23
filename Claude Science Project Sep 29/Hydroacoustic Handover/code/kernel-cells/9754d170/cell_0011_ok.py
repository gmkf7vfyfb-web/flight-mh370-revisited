
import pypdfium2 as pdfium, os
os.makedirs('audit/pages',exist_ok=True)
pdf=pdfium.PdfDocument("audit/hb/ISO Sept 28 Status/inputs/papers/hydroacoustics/ucrl-tr-207323.pdf")
for p in [9,10,23]:
    img=pdf[p-1].render(scale=2.5).to_pil()
    img.save(f'audit/pages/p{p}.png'); print(p,img.size)
