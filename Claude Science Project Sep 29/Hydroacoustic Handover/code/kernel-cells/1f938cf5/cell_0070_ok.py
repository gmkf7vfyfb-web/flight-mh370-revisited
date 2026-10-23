
cond=[]
for wcol in ('w0','w2'):
    for st in sorted(Lm.stratum.unique()):
        g=Lm[Lm.stratum==st]; WL=g[wcol].sum()
        a=near4[near4.stratum==st]; b=near20[near20.stratum==st]
        pr=(a[wcol]*a.P_rec).sum()/WL; pf=(b[wcol]*b.P_fus).sum()/WL; pi=(a[wcol]*a.in2).sum()/WL
        wr=(a[wcol]*a.P_rec).values; ess=wr.sum()**2/(wr**2).sum() if wr.sum()>0 else 0
        npar=a[a.P_rec>0].groupby('seed_key').parent.nunique().sum()
        cond.append(dict(weighting=wcol,stratum=st,P_rec_given_L=pr,P_fus_given_L=pf,P_impact2km_given_L=pi,ESS_rec_rows=ess,distinct_parents_rec=int(npar),rows_Prec_pos=int((a.P_rec>0).sum())))
COND=pd.DataFrame(cond); print(COND.to_string())
# family / debris composition of rows contributing to P_rec (w0)
a=near4[near4.P_rec>0].copy(); a['c']=a.w0*a.P_rec
fam_lab={0:'?',1:'?'}
print(a.groupby('family').c.sum()/a.c.sum()); print(a.groupby('latent:debris_class').c.sum()/a.c.sum())
print('vh/vd quantiles', wq(a.vh,a.c), wq(a.vd,a.c))
