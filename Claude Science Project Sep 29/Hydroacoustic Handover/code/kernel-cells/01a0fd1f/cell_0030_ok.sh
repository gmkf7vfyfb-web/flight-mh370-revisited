cd rr
curl -sL -m 60 -o wise_pm.html "https://www.jeffwise.net/2026/07/19/a-new-clue-from-the-night-mh370-vanished-may-radically-change-the-search-for-the-missing-plane/"; echo "$? $(wc -c < wise_pm.html)"
python - <<'EOF'
from bs4 import BeautifulSoup
s=BeautifulSoup(open('wise_pm.html',encoding='utf-8',errors='ignore'),'html.parser')
a=s.find('article') or s.body
open('wise_pm.txt','w').write(a.get_text('\n',strip=True))
for l in a.find_all('a'):
    h=l.get('href','')
    if any(k in h.lower() for k in ['pdf','royer','drive','dropbox','upload','doi']): print(l.get_text(strip=True)[:60],'|',h)
print(len(a.get_text()))
EOF