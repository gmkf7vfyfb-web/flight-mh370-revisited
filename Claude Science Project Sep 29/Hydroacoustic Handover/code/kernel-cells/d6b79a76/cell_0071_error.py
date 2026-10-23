def wq(x,w,qs=(0.05,0.5,0.95)):
    x=np.asarray(x,float); ok=np.isfinite(x)&(w>0)
    if ok.sum()==0: return [np.nan]*len(qs)
    o=np.argsort(x[ok]); c=np.cumsum(w[ok][o]); c/=c[-1]; return [float(x[ok][o][min(np.searchsorted(c,q),ok.sum()-1)]) for q in qs]
def wshare(mask,w): return float(w[mask].sum()/w.sum()) if w.sum()>0 else np.nan
def mech(df):
    arrested=(df.vs19b<-8000)&(df.t_after_0019a_min>10)
    powered=df.fo_after_0019a|df.powered_at_impact
    glide=~powered
    return {'powered_after_0019a':powered,'unpowered_glide_turns':glide&(df.turns>0),'unpowered_glide_no_turns':glide&(df.turns==0),'arrested_dive_after_steep_0019b':arrested}
QV=[('t_imp_min','impact time, min after 00:00'),('t_after_0019a_min','minutes after 00:19:29'),('fo_min','final flame-out, min after 00:00'),('aloft_after_fo_min','minutes aloft after flame-out'),
    ('turns','turns begun'),('latent:heading_change_deg','heading change deg'),('speed_mps','impact speed m/s'),('flight_path_angle_deg','flight-path angle deg'),('kinetic_energy_j','kinetic energy J'),
    ('tau90_s','tau90 s'),('latent:impact_bank_deg','impact bank deg'),('vs19a','V/S 00:19:29 ft/min'),('vs19b','V/S 00:19:37 ft/min'),('z_bto19a','BTO 00:19:29 resid/sigma'),('z_bto19b','BTO 00:19:37 resid/sigma'),
    ('z_bfo19a','BFO 00:19:29 innov/sigma'),('z_bfo19b','BFO 00:19:37 innov/sigma'),('along_bearing_km','along bearing beyond arc crossing km'),('xt_km','cross-track km'),('bto_arc_us','sea-level BTO minus 18400 us'),('dX_km','distance to arc crossing km'),('latitude_deg','latitude'),('longitude_deg','longitude')]
def characterise(df,k,vn,ck=None):
    lw=(df['lm|'+k]+df['lnL|'+vn]).values; fin=np.isfinite(lw); s=lw[fin].max(); w=np.where(fin,np.exp(lw-s),0.0)
    out={'key':k,'variant':vn,'ess':float(w.sum()**2/(w*w).sum())}
    for c,n in QV: out[n]=wq(df[c].values,w)
    f=df.f4.values; out.update({f'share_{n}':wshare(f==c,w) for c,n in ((1,'A1'),(2,'A2'),(3,'B'))})
    out.update({f'share_{n}':wshare(m.values,w) for n,m in mech(df).items()})
    out['share_inside_arc']=wshare(df.bto_arc_us.values<0,w); out['share_in_strip']=wshare(df.in_strip.values,w)
    out['share_powered_at_impact']=wshare(df.powered_at_impact.values,w)
    if ck is not None and ('lm|'+ck) in df:
        lc=(df['lm|'+ck]+df['lnL|'+vn]).values+np.log(0.75); wc=np.where(np.isfinite(lc),np.exp(lc-s),0.0); out['share_C1']=float(wc.sum()/w.sum())
    # best-fitting set: top 1% (by count) of acoustically compatible rows ranked by w L; and rows carrying 99% of sum wL
    comp=(df['z2|'+vn[0]+'1.0'].values<36)&fin; idx=np.nonzero(comp)[0]; o=idx[np.argsort(-lw[idx])]; ntop=max(1,int(round(0.01*len(idx))))
    out['n_compatible_rows']=int(len(idx)); out['n_top1pct']=ntop; out['top1pct_share_of_sumwL']=float(w[o[:ntop]].sum()/w.sum())
    oo=np.argsort(-w); cw=np.cumsum(w[oo])/w.sum(); out['n_rows_99pct_sumwL']=int(np.searchsorted(cw,0.99)+1)
    out['n_parents_99pct']=int(len(set(zip(df.stratum.values[oo[:out['n_rows_99pct_sumwL']]],df.seed.values[oo[:out['n_rows_99pct_sumwL']]],df.parent.values[oo[:out['n_rows_99pct_sumwL']]]))))
    out['_top']=o[:ntop]
    return out
CH=[]
for d in range(6):
    k=f'D{d} total q=0.333 (C2 silent)'
    for vn in W.VNAME: CH.append(characterise(M,k,vn,f'D{d}xC1'))
for d in range(5):
    for vn in W.VNAME: CH.append(characterise(Jd,f'D{d} joined V2',vn))
ch=pd.DataFrame([{kk:v for kk,v in c.items() if kk!='_top'} for c in CH])
show=['key','variant','ess','impact time, min after 00:00','minutes after 00:19:29','final flame-out, min after 00:00','minutes aloft after flame-out','share_A1','share_A2','share_B','share_C1','share_powered_after_0019a','share_unpowered_glide_turns','share_unpowered_glide_no_turns','share_arrested_dive_after_steep_0019b','share_inside_arc','n_rows_99pct_sumwL','n_parents_99pct']
def fmt(v): return '/'.join(f'{x:.1f}' for x in v) if isinstance(v,list) else (f'{v:.3f}' if isinstance(v,float) else v)
print(ch[ch.variant.isin(['T1.0','C1.0'])][show].map(fmt).to_string())