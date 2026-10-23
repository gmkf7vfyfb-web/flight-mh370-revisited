cd src && python3 -c "
import re,html
s=open('tmp.bin',encoding='utf8',errors='ignore').read()
s=re.sub(r'(?is)<(script|style).*?</\1>',' ',s); s=re.sub(r'(?s)<[^>]+>',' ',s)
print(re.sub(r'\s+',' ',html.unescape(s))[:1500])"