cd papers; python -c "
import pypdfium2 as p, re; d=p.PdfDocument('brown2026.pdf')
t18=d[17].get_textpage().get_text_range(); i=t18.find('F-35'); print(t18[max(0,i-1500):i+2500]); print('=====')
for i in range(len(d)):
    t=d[i].get_textpage().get_text_range()
    for m in re.finditer(r'(Figure|Fig\.) ?([A-Z]?\.?\d+)[:.] ?([^\n]{0,160})', t):
        if m.start()<len(t) and t[max(0,m.start()-1)] in '\n ': print(i+1, m.group(0)[:200])
" | head -120