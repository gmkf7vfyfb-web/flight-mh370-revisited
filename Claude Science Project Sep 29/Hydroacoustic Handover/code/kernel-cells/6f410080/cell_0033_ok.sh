python - <<'EOF'
import re,html
def clean(t):
    t=re.sub(r'<(script|style).*?</\1>','',t,flags=re.S|re.I)
    t=html.unescape(re.sub(r'<[^>]+>',' ',t)); return re.sub(r'\s+',' ',t)
t=open('contrail/370loc.html').read()
imgs=[u for u in re.findall(r'(?:src|href)="([^"]+\.(?:png|jpg|gif|jpeg))"',t,re.I)]
print(sorted(set(imgs))[:40])
c=clean(t); i=c.find('Updated Feb 2017'); print(c[i:i+5000])
a=clean(open('contrail/arxiv.html').read()); j=a.find('How to find MH370'); print('\nARXIV',a[j:j+1500])
EOF