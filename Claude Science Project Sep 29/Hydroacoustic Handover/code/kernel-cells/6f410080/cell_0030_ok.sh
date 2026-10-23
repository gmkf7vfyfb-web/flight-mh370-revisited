mkdir -p contrail && python - <<'EOF'
import requests,re,json
urls={'metabunk':'https://www.metabunk.org/threads/claim-mh370-contrails-have-been-identified.6068/',
'370loc':'https://370location.org/2016/11/mh370-plume-candidate-on-satellite-thermal-images/',
'aviationist':'https://theaviationist.com/2014/03/24/meteosat-mh370-contrails/',
'arxiv':'https://arxiv.org/abs/1811.09315'}
for k,u in urls.items():
    try:
        r=requests.get(u,timeout=40); print(k,r.status_code,len(r.text)); open(f'contrail/{k}.html','w').write(r.text)
    except Exception as e: print(k,'ERR',str(e)[:100])
r=requests.get('http://web.archive.org/cdx/search/cdx',params={'url':'weathergraphics.com/*','from':'201403','to':'201412','output':'json','fl':'original,timestamp,statuscode,mimetype','collapse':'urlkey','limit':5000},timeout=90)
rows=r.json()[1:] if r.text.strip() else []
print('wg',len(rows))
for x in rows:
    if re.search(r'mh370|malaysia|370|meteosat|contrail|tim/',x[0],re.I): print(x)
json.dump(rows,open('contrail/wg_cdx.json','w'))
EOF