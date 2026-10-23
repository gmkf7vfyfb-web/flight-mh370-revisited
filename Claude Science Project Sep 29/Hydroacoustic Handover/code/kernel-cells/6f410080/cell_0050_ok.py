f=[x for x in docs if x.endswith('article_1899')][0]
raw=open(f,errors='ignore').read()
i=raw.find('MH370')
seg=raw[i-3000:i+8000]
print(re.findall(r'(?:src|href)="([^"]+)"',seg))
t=docs[f]; j=t.find('ไทยโชต จากเหตุการณ์'); print(t[j-200:j+3000])