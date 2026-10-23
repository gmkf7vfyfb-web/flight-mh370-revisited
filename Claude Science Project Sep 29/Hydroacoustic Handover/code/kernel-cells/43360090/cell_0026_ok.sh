cd ./.tmp; python3 - <<'EOF'
import json,urllib.request,urllib.parse,time
exec(open('xref.py').read().split('out={}')[0])  # loads qs
out=json.load(open('xref.json'))
extra={'oliveira2016':'Oliveira Kadri 2016 Acoustic-gravity waves from the 2004 Indian Ocean earthquake and tsunami Journal of Geophysical Research Oceans',
'koper2001':'Koper Wallace Taylor Hartse Forensic seismology and the sinking of the Kursk Eos 2001'}
qs.update(extra)
todo=[k for k,v in out.items() if isinstance(v,str)]+list(extra)
for k in todo:
    u='https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':qs[k],'rows':2,'select':'DOI,title,author,issued,container-title'})
    for attempt in range(4):
        try:
            req=urllib.request.Request(u,headers={'User-Agent':'python-urllib bibliography check'})
            r=json.load(urllib.request.urlopen(req,timeout=30))['message']['items']
            out[k]=[{'doi':i.get('DOI'),'title':(i.get('title') or [''])[0][:110],'year':(i.get('issued',{}).get('date-parts') or [[None]])[0][0],'venue':(i.get('container-title') or [''])[0][:50],'a1':((i.get('author') or [{}])[0].get('family'))} for i in r]; break
        except Exception as e:
            out[k]=str(e); time.sleep(3+3*attempt)
    time.sleep(1.2)
json.dump(out,open('xref.json','w'),indent=1)
for k in todo:
    v=out[k]
    if isinstance(v,str): print(k,'ERR',v); continue
    for i in v[:2]: print(f"{k:14s} {i['doi']:38s} {i['year']} {i['a1']} | {i['title'][:85]} | {i['venue'][:30]}")
EOF