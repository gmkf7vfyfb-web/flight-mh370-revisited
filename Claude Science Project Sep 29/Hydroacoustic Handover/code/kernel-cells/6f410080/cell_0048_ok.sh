python - <<'EOF'
import requests
for n in ['DIGO_00718_01_14.jpg','DIGO_00718_02_14.jpg']:
    r=requests.get('http://web.archive.org/cdx/search/cdx',params={'url':f'amsa.gov.au/media/incidents/images/{n}','output':'json','fl':'original,timestamp,statuscode,length','limit':10},timeout=60)
    rows=[x for x in r.json()[1:] if x[2]=='200']; print(n,rows[:3])
    if rows:
        o,ts,_,_=rows[0]; k=requests.get(f'http://web.archive.org/web/{ts}id_/{o}',timeout=120)
        open(f'contrail/{n}','wb').write(k.content); print(k.status_code,len(k.content))
EOF