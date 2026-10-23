Jd['z_bfo19a']=np.nan; Jd['z_bfo19b']=np.nan
CH=[c for c in CH if 'joined' not in c['key']]
for d in range(5):
    for vn in W.VNAME: CH.append(characterise(Jd,f'D{d} joined V2',vn))
ch=pd.DataFrame([{kk:v for kk,v in c.items() if kk!='_top'} for c in CH])
print(ch[ch.variant.isin(['T1.0','C1.0'])][show].map(fmt).to_string())