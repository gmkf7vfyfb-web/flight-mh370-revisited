cd rr; pip -q install pypdfium2 2>&1|tail -1; python -c "
import pypdfium2 as p
d=p.PdfDocument('ctbto.pdf')
for i in [2,3,4]:
    d[i].render(scale=2).to_pil().save(f'ctbto_p{i+1}.png')
print('ok')"