python - <<'EOF'
import requests
for path in ['www.amsa.gov.au/file/2681/download','www.amsa.gov.au/file/2682/download','www.amsa.gov.au/file/2850/download','amsa.gov.au/media/incidents/mh370/day3-2014-03-20/image1-thumb.jpg','amsa.gov.au/media/incidents/mh370/day3-2014-03-20/image2-thumb.jpg','amsa.gov.au/media/incidents/mh370/day3-2014-03-20/*']:
    r=requests.get('http://web.archive.org/cdx/search/cdx',params={'url':path,'output':'json','fl':'original,timestamp,statuscode,mimetype,length','limit':40},timeout=60)
    rows=r.json()[1:] if r.text.strip() else []
    print(path,len(rows)); 
    for x in rows[:40]: print('  ',x)
EOF