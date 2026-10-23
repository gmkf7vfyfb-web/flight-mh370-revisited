t=doc[219].get_text(); print(re.sub(r'\n\s*\n','\n',t)[:3000])
for i,p in enumerate(doc):
    tt=p.get_text()
    for m in re.finditer(r'[^\n]*(debris|wreckage)[^\n]*',tt,re.I):
        if 380<=i<=425 or 'sweep' in tt.lower(): print(i+1,'|',m.group(0)[:150])
import math
print([round(math.erf(math.sqrt(math.pi)/2*c),3) for c in (0.5,1,2)],[round(1-math.exp(-c),3) for c in (0.5,1,2)])