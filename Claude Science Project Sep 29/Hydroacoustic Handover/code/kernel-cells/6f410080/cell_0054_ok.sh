python - <<'EOF'
import requests,time
r=requests.get('http://web.archive.org/cdx/search/cdx',params={'url':'gistda.or.th/gistda_n/newsphotos/20140327-mh370/','matchType':'prefix','output':'json','fl':'original,timestamp,statuscode,mimetype,length','limit':200},timeout=60)
rows=r.json()[1:]
for x in rows:
    if x[3].startswith('image'): print(x)
got=set()
for o,ts,sc,mt,ln in rows:
    if sc=='200' and mt.startswith('image') and o.split('/')[-1]+o.split('/')[-2] not in got:
        k=requests.get(f'http://web.archive.org/web/{ts}id_/{o}',timeout=120)
        n=o.split('/')[-2]+'_'+o.split('/')[-1]
        open(f'gistda/{n}','wb').write(k.content); got.add(o.split('/')[-1]+o.split('/')[-2]); print('saved',n,k.status_code,len(k.content),k.content[:4]); time.sleep(1)
EOF