cd rr
curl -sL -m 60 -o dd.html "https://www.deepdivemh370.com/p/new-hydroacoustic-data"; echo "$? $(wc -c < dd.html)"
python - <<'EOF'
from bs4 import BeautifulSoup
s=BeautifulSoup(open('dd.html',encoding='utf-8',errors='ignore'),'html.parser')
a=s.find('div',class_='available-content') or s.find('article') or s.body
t=a.get_text('\n',strip=True); open('dd.txt','w').write(t); print(len(t))
for l in a.find_all('a'):
    h=l.get('href','')
    if h and 'substack.com/subscribe' not in h: print(l.get_text(strip=True)[:60],'|',h)
for im in a.find_all('img')[:30]: print('IMG', im.get('alt','')[:80], im.get('src','')[:150])
EOF