python - <<'EOF'
import requests,re,html
for u in ['https://ogleearth.com/2014/03/flight-mh370-search-data-in-google-earth/']:
    try:
        r=requests.get(u,timeout=40); print(r.status_code,len(r.text)); t=r.text
    except Exception as e:
        print('ERR',str(e)[:100]); 
        r=requests.get('http://web.archive.org/web/2014id_/'+u,timeout=60); print('wb',r.status_code,len(r.text)); t=r.text
    open('contrail/ogle.html','w').write(t)
    print(re.findall(r'href="([^"]+\.km[lz][^"]*)"',t))
    c=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',re.sub(r'<(script|style).*?</\1>','',t,flags=re.S))))
    i=c.find('UPDATE March 20'); print(c[i-600:i+1500])
EOF