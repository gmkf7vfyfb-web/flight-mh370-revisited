cd ./.tmp; curl -s -m 60 -L -o stone.pdf https://arxiv.org/pdf/1405.4720 -w "%{http_code}\n"; python3 - <<'EOF'
import pypdfium2 as p,re
d=p.PdfDocument('stone.pdf'); t=re.sub(r'\s+',' ',' '.join(d[i].get_textpage().get_text_range() for i in range(len(d))))
for kw in ['beacon','failed','found the wreck','discovered','probability of detect','0.9','one week','km of']:
    for m in list(re.finditer(kw,t))[:3]: print(f'[{kw}]',t[max(0,m.start()-200):m.end()+200])
EOF
python3 - <<'EOF'
import json,urllib.request,urllib.parse,time
for q in ['Observation of gravitational waves from a binary black hole merger Abbott 2016 Physical Review Letters','Surrogate time series Schreiber Schmitz Physica D 2000','PyCBC search for gravitational waves from compact binary coalescence Usman 2016']:
    u='https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':q,'rows':2,'select':'DOI,title,issued,container-title'})
    r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'bib-check'}),timeout=30))['message']['items']
    for i in r: print(i['DOI'],(i.get('title') or [''])[0][:90],(i.get('container-title') or [''])[0][:30],i['issued']['date-parts'][0][0])
    time.sleep(1.5)
EOF