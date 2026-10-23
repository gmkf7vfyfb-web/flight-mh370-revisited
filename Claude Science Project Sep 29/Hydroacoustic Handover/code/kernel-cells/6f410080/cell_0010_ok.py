import requests
r=requests.get('http://web.archive.org/cdx/search/cdx',params={'url':'amsa.gov.au/media/*','from':'201403','to':'201405','output':'json','fl':'original,timestamp,statuscode','collapse':'urlkey','limit':2000},timeout=60)
print(r.status_code,len(r.text))
rows=r.json()[1:] if r.status_code==200 else []
print(len(rows))
for x in rows:
    if any(s in x[0].lower() for s in ['mh370','satellite','malaysia','search']): print(x)