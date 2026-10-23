print(open('kh/h0011/err.log').read()[:300])
b11=np.full(len(M),np.nan); f11=np.full(len(M),np.nan); fuel11=np.full(len(M),np.nan)
for (st,s),idx in M.groupby(['stratum','seed']).indices.items():
    z=np.load(f'kh/h0011/{st}-seed-{s}.npz'); p=M.parent.values[idx].astype(int)
    assert len(z['lat'])==len(Vmap[(st,s)])
    b11[idx]=z['bto11_res'][p]/29.0; f11[idx]=z['bfo11_res'][p]/np.sqrt(z['biasvar'][p]+4.3177**2); fuel11[idx]=z['fuel'][p]
M['z_bto0011']=b11; M['z_bfo0011']=f11; M['fuel_kg_0011']=fuel11
QV2=QV+[('z_bto0011','BTO 00:10:59 resid/sigma'),('z_bfo0011','BFO 00:10:59 resid/sigma (predictive)'),('fuel_kg_0011','fuel at 00:11 kg')]
QV_bak=QV; QV=QV2
CH2=[]
for d in range(6):
    for vn in W.VNAME: CH2.append(characterise(M,f'D{d} total q=0.333 (C2 silent)',vn,f'D{d}xC1'))
QV=QV_bak
# top-1% unweighted summaries
def top_summary(c,df=M):
    t=df.iloc[c['_top']]; o={'key':c['key'].replace(' total q=0.333 (C2 silent)',''),'variant':c['variant'],'n_top':len(t),'top_share_sumwL':c['top1pct_share_of_sumwL']}
    for col,n in QV2: o[n]='/'.join(f'{x:.1f}' for x in np.nanpercentile(t[col],[5,50,95])) if t[col].notna().any() else 'n/a'
    o.update({f'frac_{n}':float(m.values[c['_top']].mean()) for n,m in mech(df).items()}); o['frac_inside_arc']=float((t.bto_arc_us<0).mean())
    o.update({f'frac_{n}':float((t.f4==v).mean()) for v,n in ((1,'A1'),(2,'A2'),(3,'B'))})
    return o
TOP=pd.DataFrame([top_summary(c) for c in CH2])
CHW=pd.DataFrame([{kk:v for kk,v in c.items() if kk!='_top'} for c in CH2]); CHW['key']=CHW.key.str.replace(' total q=0.333 (C2 silent)','')
print(CHW[CHW.variant.isin(['T1.0','C1.0'])][['key','variant','BTO 00:10:59 resid/sigma','BFO 00:10:59 resid/sigma (predictive)','BTO 00:19:29 resid/sigma','BFO 00:19:29 innov/sigma','BFO 00:19:37 innov/sigma','V/S 00:19:37 ft/min','impact speed m/s','flight-path angle deg','tau90 s','along bearing beyond arc crossing km','cross-track km']].map(fmt).to_string())
print(TOP[TOP.variant.isin(['T1.0','C1.0'])][['key','variant','n_top','top_share_sumwL','minutes after 00:19:29','minutes aloft after flame-out','frac_A2','frac_B','frac_unpowered_glide_turns','frac_powered_after_0019a','frac_arrested_dive_after_steep_0019b','frac_inside_arc']].to_string())