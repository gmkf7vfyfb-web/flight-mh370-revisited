char={}
for d in ['D0','D1','D2']:
    for ak,mask in [(None,'strip'),('Tcore',None),('Ccore',None)]:
        df=rows_weighted(d,ak,mask); w=df.w.values
        lab=f'{d}|{ak or "strip"}'
        char[lab]={'ESS_rows':float(1/np.sum(w**2)),'dr_q05_50_95_km':wq(df.dr.values,w,[.05,.5,.95]),'impact_min_after_0000':wq(df.t.values/60,w,[.05,.5,.95]),
            'minutes_flameout_to_impact':wq((df.t.values-df.flame.values)/60,w,[.05,.5,.95]),'impact_speed_mps':wq(df.v.values,w,[.05,.5,.95]),'fpa_deg':wq(df.fpa.values,w,[.05,.5,.95]),
            'fam_A1_A2_B':[float(w[df.fam.values==i].sum()) for i in range(3)],'OI2018_cov_mean':float((w*df['cov'].values).sum()),'strata':df.groupby('st').w.sum().round(4).to_dict()}
        print(lab, {k:(np.round(v,2).tolist() if isinstance(v,list) else (round(v,3) if isinstance(v,float) else v)) for k,v in char[lab].items()})