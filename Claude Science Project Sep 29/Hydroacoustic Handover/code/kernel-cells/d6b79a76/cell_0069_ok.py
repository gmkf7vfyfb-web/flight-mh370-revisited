from scipy.special import logsumexp
M=R[R.stratum!='joined-v2'].reset_index(drop=True); Jd=R[R.stratum=='joined-v2'].reset_index(drop=True); del R
HK=W.KEYS[:6]
chk=[]
for k in HK:
    for vn in W.VNAME:
        x=(M['lm|'+k]+M['lnL|'+vn]).values; full=A.L(r['acoustic'][k][vn]['all']['l1'] for r in seeds if A.pool_of(r)=='main')
        chk.append((k[:2],vn,np.exp(logsumexp(x[np.isfinite(x)])-full)))
print(pd.DataFrame(chk).pivot(index=0,columns=1,values=2).round(5))
for d in range(5):
    k=f'D{d} joined V2'; x=(Jd['lm|'+k]+Jd['lnL|T1.0']).values; full=A.L(r['acoustic'][k]['T1.0']['all']['l1'] for r in seeds if A.pool_of(r)=='joined'); print(k, np.exp(logsumexp(x[np.isfinite(x)])-full))