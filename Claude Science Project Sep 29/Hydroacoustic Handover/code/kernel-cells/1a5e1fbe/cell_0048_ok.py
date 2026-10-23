W=pages('icao_wp30.pdf'); print(len(W)); 
for i,t in enumerate(W):
    t=re.sub(r'\s+',' ',t)
    for m in re.finditer(r'[^.]*(weather|sea state|sorties|flight hours|POD|probability|coverage|visib)[^.]*\.',t,re.I):
        print('PDF p',i+1,'||',m.group(0).strip()[:380])