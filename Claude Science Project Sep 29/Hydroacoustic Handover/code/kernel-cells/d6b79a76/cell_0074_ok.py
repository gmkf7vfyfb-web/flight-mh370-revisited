near=(M.dX_km<=50)&(M.t_after_0019a_min>=13)&(M.t_after_0019a_min<=18)
mm=mech(M)
rows=[]
for n,mk in mm.items():
    s=near&mk
    r_={'mechanism':n,'rows':int(s.sum()),'parents':int(len(set(zip(M.stratum[s],M.seed[s],M.parent[s]))))}
    for d in (0,1,2,3,4,5):
        k=f'lm|D{d} total q=0.333 (C2 silent)'; tot=A.L(r['prior'][k[3:]]['all']['l1'] for r in seeds if A.pool_of(r)=='main')
        x=M[k].values[s.values]; r_[f'D{d}_mass']=float(np.exp(logsumexp(x[np.isfinite(x)])-tot)) if np.isfinite(x).any() else 0.0
    rows.append(r_)
s=near; r_={'mechanism':'ALL (X50, 13-18 min after 00:19:29)','rows':int(s.sum()),'parents':int(len(set(zip(M.stratum[s],M.seed[s],M.parent[s]))))}
for d in range(6):
    k=f'lm|D{d} total q=0.333 (C2 silent)'; tot=A.L(r['prior'][k[3:]]['all']['l1'] for r in seeds if A.pool_of(r)=='main'); x=M[k].values[s.values]; r_[f'D{d}_mass']=float(np.exp(logsumexp(x[np.isfinite(x)])-tot))
rows.append(r_)
feas=pd.DataFrame(rows); print(feas.to_string())
# powered rows near: log-on cause and family
p=near&mm['powered_after_0019a']; print(M[p].groupby('f4').size(), M[p][['fo_min','t_imp_min','vs19a']].describe().round(1))
# whole X50 impact time distribution (unweighted)
print(np.percentile(M[M.dX_km<=50].t_after_0019a_min,[5,25,50,75,95]).round(1))