
def p_rest_near(df,cls,M,rng,radius=2.0,ocean=None):
    ocean=ocean or glorys
    rep=np.repeat(np.arange(len(df)),M); r=df.iloc[rep]
    la=r.latitude_deg.values.astype(float); lo=r.longitude_deg.values.astype(float)
    t0=T0+np.nan_to_num(r.t_impact_s.values,nan=1800.)
    tr=np.degrees(np.arctan2(r.velocity_east_mps.values,r.velocity_north_mps.values)); fam=r['latent:debris_class'].values.astype(int)
    out=np.zeros(len(r),bool); B=200000
    for s in range(0,len(r),B):
        o=sm.settle(la[s:s+B],lo[s:s+B],t0[s:s+B],r.vh.values[s:s+B],tr[s:s+B],fam[s:s+B],cls,ocean,wind,rng)
        d=gw.inv(o['lon'],o['lat'],np.full(len(o['lat']),HX[1]),np.full(len(o['lat']),HX[0]))[2]/1e3
        out[s:s+B]=d<=radius
    return out.reshape(len(df),M).mean(1)
t1=time.time()
near4=Lm[Lm.dHX<=4.0].copy(); near20=Lm[Lm.dHX<=20.0].copy()
near4['P_rec']=p_rest_near(near4,'recorder-detached',50,np.random.default_rng(11))
near20['P_fus']=p_rest_near(near20,'fuselage-section',8,np.random.default_rng(12))
print('time',time.time()-t1)
def mass(df,col,wcol='w0'):
    # absolute run J posterior mass (weight column only) per stratum: mean over seeds of sum w0*P
    out={}
    for st,g in df.groupby('stratum'):
        nseed=Lm[Lm.stratum==st].seed_key.nunique()
        out[st]=(g[wcol]*g[col]).groupby(g.seed_key).sum().reindex(Lm[Lm.stratum==st].seed_key.unique(),fill_value=0).mean()
    return out
near4['in2']=(near4.dHX<=2.0).astype(float)
mabs=pd.DataFrame({'P(recorder detached rests <=2 km)':mass(near4,'P_rec'),'P(recorder in aft fuselage rests <=2 km)':mass(near20,'P_fus'),
                   'P(impact point <=2 km, no settling)':mass(near4,'in2')})
# mass of L per stratum (same normalisation) for conditional versions
mL=pd.Series({st:g.groupby('seed_key').w0.sum().mean() for st,g in Lm.groupby('stratum')},name='P(impact in L)')
mabs=mabs.join(mL)
print(mabs.to_string())
