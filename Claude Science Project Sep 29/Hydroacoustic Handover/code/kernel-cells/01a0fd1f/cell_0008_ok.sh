cd rr; python - <<'EOF'
from bs4 import BeautifulSoup
s=BeautifulSoup(open('cocos370.html',encoding='utf-8',errors='ignore'),'html.parser')
a=s.find('article') or s.body
for l in a.find_all('a'):
    h=l.get('href','')
    if h and 'wp-content/uploads' not in h or 'pdf' in h.lower(): print(l.get_text(strip=True)[:60],'|',h)
EOF