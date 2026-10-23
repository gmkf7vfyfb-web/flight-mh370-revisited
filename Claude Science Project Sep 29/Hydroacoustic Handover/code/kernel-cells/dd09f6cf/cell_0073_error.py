def rows_weighted(d, ak=None, mask=None):
    out=[]
    for s in STR:
        K=len(Z[s])
        for z in Z[s]:
            lw=np.log(PF[s]/K)+z[f'rows|logm|{d}']
            if ak: lw=lw+z[f'rows|logLA|{ak}']
            sel=np.ones(lw.size,bool) if mask is None else z[f'rows|mask|{mask}'].astype(bool)
            out.append(pd.DataFrame({'lw':lw[sel],'lat':z['rows|lat'][sel],'lon':z['rows|lon'][sel],'t':z['rows|t'][sel],'v':z['rows|vimp'][sel],'fpa':z['rows|fpa'][sel],
                 'flame':z['rows|flame'][sel],'dr':z['rows|along'][sel]-R7,'cross':z['rows|cross'][sel],'cov':z['rows|covOI18'][sel],'fam':z['rows|fam'][sel],'st':s}))
    df=pd.concat(out); df=df[np.isfinite(df.lw)]; df['w']=np.exp(df.lw-df.lw.max()); df['w']/=df.w.sum(); return df
def wq(x,w,q): o=np.argsort(x); cw=np.cumsum(w[o]); return [float(x[o][np.searchsorted(cw,qq)]) for qq in q]
char={}
for d in ['D0','D1','D2']:
    for ak,mask in [(None,'strip'),('Tcore',None),('Ccore',None)]:
        df=rows_weighted(d,ak,mask); w=df.w.values
        lab=f'{d}|{ak or "strip"}'
        char[lab]={'ESS_rows':float(1/np.sum(w**2)),'dr_q05_50_95_km':wq(df.dr.values,w,[.05,.5,.95]),'impact_min_after_0000':wq(df.t.values/60,w,[.05,.5,.95]),
            'minutes_flameout_to_impact':wq((df.t.values-df.flame.values)/60,w,[.05,.5,.95]),'impact_speed_mps':wq(df.v.values,w,[.05,.5,.95]),'fpa_deg':wq(df.fpa.values,w,[.05,.5,.95]),
            'fam_A1_A2_B':[float(w[df.fam.values==i].sum()) for i in range(3)],'OI2018_cov_mean':float((w*df.cov.values).sum()),'strata':df.groupby('st').w.sum().round(4).to_dict()}
        print(lab, {k:(np.round(v,2).tolist() if isinstance(v,list) else (round(v,3) if isinstance(v,float) else v)) for k,v in char[lab].items()})