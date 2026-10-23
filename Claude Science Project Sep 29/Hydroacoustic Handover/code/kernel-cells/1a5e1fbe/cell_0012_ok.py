d2=pymupdf.open('pod/iamsar2025.pdf'); print(d2.page_count)
for i,p in enumerate(d2):
    t=p.get_text()
    for m in re.finditer(r'[^\n]*(correction factor|weather correction|sweep width|ideal|normal search|POD)[^\n]*',t,re.I):
        print(i+1,'|',m.group(0)[:160])