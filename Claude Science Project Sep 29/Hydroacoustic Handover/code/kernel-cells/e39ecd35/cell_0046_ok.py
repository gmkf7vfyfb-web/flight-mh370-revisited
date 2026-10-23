
pages = ["https://www.mot.gov.my/en/aviation/reports","https://www.mot.gov.my/en/aviation/safety","https://www.mot.gov.my/en/aviation"]
pdfs=set()
for p in pages:
    try:
        h=get(p)
        for m in re.findall(r'href="([^"]+)"', h):
            if m.lower().endswith(".pdf") or "mh" in m.lower() and "370" in m:
                pdfs.add(urllib.parse.urljoin(p,m))
        print("ok",p,len(h))
    except Exception as e: print("fail",p,type(e).__name__)
for x in sorted(pdfs): print(x)
