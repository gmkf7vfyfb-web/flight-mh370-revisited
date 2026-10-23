python - <<'EOF'
import requests,re
r=requests.get('http://web.archive.org/cdx/search/cdx',params={'url':'amsa.gov.au/media/incidents/mh370-search.asp','output':'json','fl':'original,timestamp,statuscode','limit':30,'from':'20140321','to':'20140330'},timeout=60)
rows=[x for x in r.json()[1:] if x[2]=='200']; print(rows[:5])
o,ts,_=rows[0]
p=requests.get(f'http://web.archive.org/web/{ts}id_/{o}',timeout=90).text
for m in re.finditer(r'(?:href|src)="([^"]+)"',p):
    u=m.group(1)
    if re.search(r'day3|image|satell|digital|defence',u,re.I): print(u)
i=p.lower().find('satellite'); 
import html
c=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',p)))
for m in re.finditer('atellite',c): print('..',c[max(0,m.start()-300):m.start()+400])
EOF