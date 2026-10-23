cd rr
for n in 114373 114374 114375 114376 114385; do curl -sL -m 60 -o arch_$n.html -w "$n %{http_code} " "https://archimer.ifremer.fr/doc/01032/$n/"; python -c "
from bs4 import BeautifulSoup;import re
s=BeautifulSoup(open('arch_$n.html',encoding='utf-8',errors='ignore'),'html.parser'); print(s.title.get_text(strip=True)[:150] if s.title else 'no title')
pdfs=set(a['href'] for a in s.find_all('a',href=True) if '.pdf' in a['href'].lower()); print(list(pdfs)[:4])"; done