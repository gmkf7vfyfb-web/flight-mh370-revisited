for m in re.finditer('MH370',raw):
    s=raw[max(0,m.start()-1500):m.start()+3000]
    print('IMG/LINKS',re.findall(r'(?:src|href)="([^"]+)"',s)[:30])
    print(re.sub(r'\s+',' ',H.unescape(re.sub(r'<[^>]+>',' ',s)))[:3000]); print('=====')