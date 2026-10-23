def cdx(url,frm='201403',to='201406',lim=3000):
    try:
        r=requests.get('http://web.archive.org/cdx/search/cdx',params={'url':url,'from':frm,'to':to,'output':'json','fl':'original,timestamp,statuscode,mimetype','collapse':'urlkey','limit':lim},timeout=90)
        return r.json()[1:] if r.status_code==200 and r.text.strip() else []
    except Exception as e:
        print(url,e); return []
res={}
for u in ['gistda.or.th/*','www.mot.gov.my/*','mh370.gov.my/*','www.jacc.gov.au/*','www.cas.go.jp/*']:
    rows2=cdx(u); res[u]=rows2
    print(u,len(rows2))
import json
json.dump(res,open('handoff/cdx_misc.json','w'))
for u,rr in res.items():
    for x in rr:
        s=x[0].lower()
        if any(k in s for k in ['mh370','satellite','theos','thaichote','122','debris','objects','media','release','statement','press']) and 'jpg' not in s and 'png' not in s:
            print(u,'|',x)