sel=[f for f in docs if f.startswith('mot/') and pat.search(docs[f])]
for f in sel:
    t=re.sub(r'\s+',' ',docs[f])
    name=re.sub(r'.*Tahun_202014_','',f)
    if 'Maps' in f: print('#####',name,'\n',t[:3000]); continue
    out=[]
    for m in re.finditer(r'[^.]*?(satellite|imagery|MRSA|Remote Sensing|Thai|Japan|French|Airbus|Chin[ae]s?e? satellite)[^.]*\.',t,re.I):
        s=m.group(0).strip()
        if s not in out: out.append(s)
    print('#####',name); 
    for s in out[:25]: print(' -',s[:500])