python - <<'EOF'
import requests,zipfile,io,re,json
r=requests.get('http://web.archive.org/cdx/search/cdx',params={'url':'ogleearth.com/mh370-imagery.kmz','output':'json','fl':'original,timestamp,statuscode'},timeout=60)
rows=r.json()[1:] if r.text.strip() else []; print(rows[:10])
for orig,ts,sc in rows:
    if sc!='200': continue
    k=requests.get(f'http://web.archive.org/web/{ts}id_/{orig}',timeout=90)
    print(ts,k.status_code,len(k.content))
    try:
        z=zipfile.ZipFile(io.BytesIO(k.content))
        for n in z.namelist():
            if n.endswith('.kml'):
                s=z.read(n).decode('utf8','ignore'); open(f'contrail/ogle_{ts}.kml','w').write(s)
                for pm in re.findall(r'<Placemark>.*?</Placemark>',s,re.S):
                    nm=re.findall(r'<name>(.*?)</name>',pm,re.S); co=re.findall(r'<coordinates>(.*?)</coordinates>',pm,re.S); ds=re.findall(r'<description>(.*?)</description>',pm,re.S)
                    print(' PM',nm[:1],[c.strip()[:120] for c in co][:2],[re.sub(r'\s+',' ',d)[:300] for d in ds][:1])
                for go in re.findall(r'<GroundOverlay>.*?</GroundOverlay>',s,re.S):
                    print(' GO',re.findall(r'<name>(.*?)</name>',go)[:1],re.findall(r'<(north|south|east|west)>(.*?)</\1>',go))
            else: print('  file',n)
    except Exception as e: print('zip err',e)
EOF