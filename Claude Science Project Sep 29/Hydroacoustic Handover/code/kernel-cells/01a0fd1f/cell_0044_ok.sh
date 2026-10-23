cd rr; python -c "
import pypdfium2 as p
d=p.PdfDocument('ucrl.pdf'); print(len(d))
for i in [0,1,2,3]:
    d[i].render(scale=1.4).to_pil().save(f'ucrl_p{i+1}.png')
"; which tesseract || echo no-tess