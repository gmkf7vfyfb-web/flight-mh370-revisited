python - <<'EOF'
import requests
for n in ['mh370-au1.jpg','mh370-au2.jpg','mh370-china.jpeg']:
    for host in ['www.ogleearth.com','ogleearth.com']:
        r=requests.get('http://web.archive.org/cdx/search/cdx',params={'url':f'{host}/{n}','output':'json','fl':'original,timestamp,statuscode','limit':5},timeout=60)
        rows=r.json()[1:] if r.text.strip() else []
        ok=[x for x in rows if x[2]=='200']
        if ok:
            o,ts,_=ok[0]; k=requests.get(f'http://web.archive.org/web/{ts}id_/{o}',timeout=90)
            open(f'contrail/{n}','wb').write(k.content); print(n,ts,k.status_code,len(k.content)); break
    else: print(n,'none')
EOF