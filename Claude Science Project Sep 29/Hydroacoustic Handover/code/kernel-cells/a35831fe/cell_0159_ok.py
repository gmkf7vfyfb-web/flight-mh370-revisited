print('grid',fs,fw,fst,p2.shape, 'north edge',fs+fst*p2.shape[0],'east edge',fw+fst*p2.shape[1])
def searched_vec(L,Lo):
    i=((L-fs)/fst).astype(int); j=((Lo-fw)/fst).astype(int)
    ok=(i>=0)&(i<p2.shape[0])&(j>=0)&(j<p2.shape[1])
    out=np.zeros(L.shape,bool); ii,jj=i[ok],j[ok]
    out[ok]=(p2[ii,jj]>0.5)|(oi18[ii,jj]>0.5)|(oi25[ii,jj]>0.5)
    return out,ok
srch,okf=searched_vec(la,lo)
print('sample rows outside field grid share (prior wt):', (wi*(~okf)).sum()/wi.sum())
print('check star A old point searched:',cov_at(-35.81,91.578))
rows=[]
for (mdl,var),R in res.items():
    W=R['W']; rows.append(dict(bearing=str(mdl),variant=var,ESS=round(R['ess']),mean=f"{-R['mla']:.2f} S {R['mlo']:.2f} E",
        mass_searched=round(float(W[srch].sum()),3),mass_unsearched=round(float(W[~srch].sum()),3)))
print(pd.DataFrame(rows).to_string())
srG,okG=searched_vec(GLA.ravel(),GLO.ravel()); srG=srG.reshape(GLA.shape)
for mdl,P in AC.items(): print('acoustic only',mdl,'mass searched',P[srG].sum().round(3))
print('prior (arc only) mass searched in box', (wi[srch]).sum()/wi.sum())