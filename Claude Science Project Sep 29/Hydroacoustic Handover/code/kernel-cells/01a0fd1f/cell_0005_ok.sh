cd rr
pip -q install pypdf beautifulsoup4 2>&1 | tail -1
python -c "
import pypdf
r=pypdf.PdfReader('ctbto.pdf')
open('ctbto.txt','w').write('\n'.join(f'=== PAGE {i+1} ===\n'+p.extract_text() for i,p in enumerate(r.pages)))
"
wc -c ctbto.txt
curl -sL -m 60 -o wise_radar.html "http://www.jeffwise.net/2014/11/18/mh370-and-the-mystery-of-indonesian-radar/"; echo "wise $? $(wc -c < wise_radar.html)"
python - <<'EOF'
from bs4 import BeautifulSoup
for f in ['wise_radar.html','cocos370.html']:
    s=BeautifulSoup(open(f,encoding='utf-8',errors='ignore'),'html.parser')
    a=s.find('article') or s.find('div',class_='entry-content') or s.body
    t=a.get_text('\n',strip=True)
    open(f.replace('.html','.txt'),'w').write(t); print(f,len(t))
EOF