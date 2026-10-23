for f,t in docs.items():
    if f.startswith('gistda') and re.search(r'MH ?370|Malaysia|มาเลเซีย|370',t):
        for m in re.finditer(r'MH ?370|Malaysia|มาเลเซีย',t):
            print(f[-60:],'|',t[max(0,m.start()-300):m.start()+500]); break
res=json.load(open('handoff/cdx_misc.json'))
print([x for x in res['gistda.or.th/*'] if re.search(r'1872|1899|mh|370|news',x[0],re.I)][:30])