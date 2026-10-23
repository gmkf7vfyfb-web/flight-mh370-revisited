for name,T in [('atsb2017',a),('csiro1',' '.join(c1)),('csiro4',' '.join(c4)),('natsar',' '.join(doc[i].get_text() for i in range(0,6)))]:
    T=re.sub(r'\s+',' ',T)
    for m in list(re.finditer(r'[^.]*(Creative Commons|copyright|CC BY)[^.]*\.',T,re.I))[:3]:
        print(name,'||',m.group(0).strip()[:350])