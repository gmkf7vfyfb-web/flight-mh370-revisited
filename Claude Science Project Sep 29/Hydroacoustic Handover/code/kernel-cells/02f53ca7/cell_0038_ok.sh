cd papers; python -c "
import pypdfium2 as p, re; d=p.PdfDocument('brown2026.pdf')
for i in range(len(d)):
    t=d[i].get_textpage().get_text_range()
    n=len(re.findall(r'H11|Wake', t))
    caps=[m.group(0)[:150].replace('\r\n',' ') for m in re.finditer(r'Figure [A-Z]?\.?\d+: [^\r\n]{0,140}', t)]
    if n or caps: print(i+1, 'H11/Wake hits', n, caps)
"