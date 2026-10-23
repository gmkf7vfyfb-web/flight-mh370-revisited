python - <<'EOF'
import requests,time
for n in ['mh370_3.jpg','area1_A1.jpg','area2_A1.jpg','area3_A1.jpg','area4_A1.jpg','mh370_1.jpg','mh370_2.jpg']:
    u=f'www.gistda.or.th/gistda_n/newsphotos/20140327-mh370/ori/{n}'
    r=requests.get('http://web.archive.org/cdx/search/cdx',params={'url':u,'output':'json','fl':'original,timestamp,statuscode,length','limit':5},timeout=60)
    rows=[x for x in (r.json()[1:] if r.text.strip() else []) if x[2]=='200']
    if not rows: print(n,'none'); continue
    o,ts,_,_=rows[0]
    for a in range(3):
        k=requests.get(f'http://web.archive.org/web/{ts}id_/{o}',timeout=120)
        if k.status_code==200: break
        time.sleep(5)
    open(f'gistda/{n}','wb').write(k.content); print(n,ts,k.status_code,len(k.content))
EOF