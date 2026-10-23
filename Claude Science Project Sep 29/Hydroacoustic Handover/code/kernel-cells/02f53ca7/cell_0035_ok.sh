cd papers; python -c "
import pypdfium2 as p, re; d=p.PdfDocument('brown2026.pdf')
for i in range(len(d)):
    t=d[i].get_textpage().get_text_range()
    if re.search(r'(?i)F-35|F35|Misawa|JASDF', t):
        print('--- page', i+1)
        for l in t.split('\n'):
            if re.search(r'(?i)F-35|F35|Misawa|JASDF|Fig', l): print('   ', l.strip()[:200])
" | head -80