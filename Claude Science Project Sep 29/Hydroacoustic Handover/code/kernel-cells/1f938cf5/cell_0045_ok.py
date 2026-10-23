
import time
rng=np.random.default_rng(42)
J4=Lm[Lm.stratum.str.startswith('run-j/')]
# equal weight per stratum (four run J route strata), w0 within stratum
sw=J4.groupby('stratum').w0.transform('sum'); pJ=(J4.w0/sw).values; pJ/=pJ.sum()
def sample_rows(n,rng,df=J4,p=pJ):
    ii=rng.choice(len(df),size=n,p=p); r=df.iloc[ii]
    return r
r=sample_rows(4000,rng)
track=np.degrees(np.arctan2(r.velocity_east_mps.values,r.velocity_north_mps.values))
fam=r['latent:debris_class'].values.astype(int)
for cls in ['recorder-detached','fuselage-section','engine','landing-gear']:
    t1=time.time()
    o=sm.settle(np.full(4000,HX[0]),np.full(4000,HX[1]),T0+r.t_impact_s.values,r.vh.values,track,fam,cls,glorys,wind,rng)
    dx,dy=sm.offsets_km(HX[0],HX[1],o['lat'],o['lon']); D=np.hypot(dx,dy)
    print(cls, 'time',round(time.time()-t1,1),'nan',np.isnan(D).sum(),'D p50/p90/p99',np.round(np.nanpercentile(D,[50,90,99]),2),'depth',np.round(np.nanmedian(o['depth'])),
          'descent min',np.round(np.nanpercentile(o['descent_s'],[5,50,95])/60,1),'floated',o['floated'].mean().round(3),'below m',np.nanmedian(o['below_m']))
