cd papers; python -c "
import pypdfium2 as p, re; d=p.PdfDocument('brown2026.pdf')
for i in (18,25,45):
    t=d[i].get_textpage().get_text_range()
    for m in re.finditer(r'H11|Wake|Metz', t):
        print(i+1, repr(t[max(0,m.start()-200):m.start()+200].replace('\r\n',' ')))
        print()
" | head -60