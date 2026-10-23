
r=requests.get(tests['dnv.com RP-F107'], timeout=30)
import re
links = sorted(set(re.findall(r'href="([^"]+)"', r.text)))
cand=[l for l in links if re.search(r'pdf|download|F107|standards\.dnv|rules-standards',l,re.I)]
print(len(links)); print('\n'.join(cand[:15]))
print(re.findall(r'<title>(.*?)</title>', r.text)[:1])
