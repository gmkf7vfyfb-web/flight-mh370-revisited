python - <<'EOF'
import requests,re,html
def clean(t):
    t=re.sub(r'<(script|style).*?</\1>','',t,flags=re.S|re.I)
    t=html.unescape(re.sub(r'<[^>]+>',' ',t)); return re.sub(r'\s+',' ',t)
r=requests.get('https://www.metabunk.org/threads/claim-mh370-contrails-have-been-identified.6068/',timeout=60)
print('metabunk',r.status_code,len(r.text)); open('contrail/metabunk.html','w').write(r.text)
t=clean(r.text)
i=t.find('MH370 contrails have been identified and measured')
print(t[i:i+9000])
EOF