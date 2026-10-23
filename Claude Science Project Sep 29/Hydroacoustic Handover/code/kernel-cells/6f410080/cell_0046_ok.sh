python - <<'EOF'
import requests,re
r=requests.get('http://web.archive.org/cdx/search/cdx',params={'url':'amsa.gov.au/media/incidents/mh370/day3-2014-03-20/','matchType':'prefix','output':'json','fl':'original,timestamp,statuscode,mimetype,length','collapse':'urlkey','limit':500},timeout=60)
rows=r.json()[1:]
for x in rows: print(x)
EOF