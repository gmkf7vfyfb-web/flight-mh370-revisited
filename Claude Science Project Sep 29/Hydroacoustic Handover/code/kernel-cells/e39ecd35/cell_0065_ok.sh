cd src && curl -sS -m 300 -L -o llnl_mh370_hydro.pdf -w "%{http_code} %{size_download}\n" "https://www.osti.gov/servlets/purl/1136454" && file llnl_mh370_hydro.pdf && python3 -c "
import pypdfium2 as p, re
d=p.PdfDocument('llnl_mh370_hydro.pdf')
t=[d[i].get_textpage().get_text_range() for i in range(len(d))]
open('llnl.txt','w').write('\n===PAGE===\n'.join(t))
print('pages',len(t))
for i,x in enumerate(t):
    for ln in x.split('\n'):
        if re.search(r'(energ|joule|kg of TNT|TNT|impact|source level|dB|kt\b|speed|velocit)', ln, re.I): print(i+1,'|',ln.strip()[:170])
" | head -60