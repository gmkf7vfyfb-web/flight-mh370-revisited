CC=[]
for d in (0,1,2):
    for vn in ('T1.0','C1.0'): CC.append(characterise(M,f'D{d}xC2 silent',vn))
cc=pd.DataFrame([{kk:v for kk,v in c.items() if kk!='_top'} for c in CC])
print(cc[[c for c in show if c in cc.columns]].map(fmt).to_string())