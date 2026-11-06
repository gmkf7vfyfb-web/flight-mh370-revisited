"""Indicative flaperon-only drift term from stored arc-latitude node tables (no transport).
Inputs (repo branch claude-science-sep29):
  results/drift-runj-2026-10-17/arc-latitude-scan/results/arclat-node-tables.zip            (26-40 S, 18 Oct 2026)
  results/drift-runj-2026-10-17/arc-latitude-scan/north-extension-2026-10-20/arclat-ext-node-tables.zip (20-25 S)
  .../north-extension-2026-10-20/arclat-likelihood-profile-20-40S.csv  (nine-item profile, release-point to arc-latitude map)
  results/evidence-ledger-v32-2026-11-03/ledger-arc-masses-v32.npz      (core and core+drift arc masses, 10 NM bins)
Three proxies, each relative to 37.5 S, mean of the two ocean models in likelihood, mean of 3 release points per latitude:
  cond   = p_flaperon_0 / sum_{s=0..5} p_flaperon_s   (Reunion share of find-coast arrivals before 30 Jun 2016)
  uncond = p_flaperon_0                               (arrival at Reunion, no conditioning on recovery; Davey's form)
  timing = hits_reunion / sum_s p_flaperon_s          (particles inside the Reunion find kernel and window, per find-coast mass)
None is the module's likelihood: no block levels, no reporting delay by period, no per-environment structure."""
import glob, io, subprocess, tomllib, numpy as np, pandas as pd
def show(p): return subprocess.run(["git","-C","repo","show",f"HEAD:Claude Science Project Sep 29/results/{p}"],capture_output=True).stdout
rows=[]
for f in sorted(glob.glob('arclat/*-nodes.csv')+glob.glob('arclat_ext/*-nodes.csv')):
    if 'seedcheck' in f: continue
    d=pd.read_csv(f); S=tomllib.load(open(f.replace('-nodes.csv','-summary.toml'),'rb'))
    d['model']='GlobCurrent' if 'globcurrent' in f else 'GLORYS12'
    d['ppn']=float(S['trajectories'])/float(S['nodes_released']); rows.append(d)
D=pd.concat(rows,ignore_index=True)
D['p_reu']=D.p_flaperon_0; D['p_find']=D[[f'p_flaperon_{i}' for i in range(6)]].sum(1)
D['cond']=D.p_reu/D.p_find; D['h']=D['hits_debris_reunion-right-flaperon']/(D.ppn/3)*1e5
Pf=pd.read_csv(io.BytesIO(show('drift-runj-2026-10-17/arc-latitude-scan/north-extension-2026-10-20/arclat-likelihood-profile-20-40S.csv')))
key=Pf[['node_lat','node_lon','arc_lat']].round(4)
D=D.assign(node_lat=D.lat_deg.round(4),node_lon=D.lon_deg.round(4)).merge(key,on=['node_lat','node_lon'])
g=D.groupby(['arc_lat','node_lat','node_lon'])[['cond','p_reu','h','p_find']].mean().reset_index().groupby('arc_lat').mean(numeric_only=True).reset_index()
prof=Pf.groupby('arc_lat').agg(finds=('finds only','mean'),finds_sd=('finds only_sd','mean'),populated=('populated coast only','mean')).reset_index()
M=prof.merge(g,on='arc_lat'); r=M.loc[M.arc_lat==-37.5].iloc[0]
M['nine_items_ln_rel']=M.finds-r.finds; M['populated_ln_rel']=M.populated-r.populated
M['flap_cond_ln_rel']=np.log(M.cond/r.cond); M['flap_uncond_ln_rel']=np.log(M.p_reu/r.p_reu)
M['flap_timing_ln_rel']=np.log((M.h/M.p_find)/(r.h/r.p_find))
M[['arc_lat','nine_items_ln_rel','finds_sd','populated_ln_rel','flap_cond_ln_rel','flap_uncond_ln_rel','flap_timing_ln_rel','p_reu','cond']].to_csv('flaperon-proxy-by-latitude.csv',index=False,float_format='%.4f')
open('arcm.npz','wb').write(show('evidence-ledger-v32-2026-11-03/ledger-arc-masses-v32.npz')); Z=np.load('arcm.npz')
def st(lat,p):
    ok=np.isfinite(lat)&np.isfinite(p); lat,p=lat[ok],p[ok]/p[ok].sum(); o=np.argsort(lat); c=np.cumsum(p[o])
    return (lat*p).sum(), np.interp(.5,c,lat[o]), np.interp(.95,c,lat[o])
out=[]; o=np.argsort(M.arc_lat.values)
for d in ['D0','D1','D2','D3','D4','D5']:
    lat=Z[f'{d}|lat']; core=np.nan_to_num(Z[f'{d}|core']); u=np.nan_to_num(Z[f'{d}|(uniform along the arc)'])
    m0,md0,h0=st(lat,core)
    terms={'flaperon, conditional on recovery':M.flap_cond_ln_rel,'flaperon, unconditional (Davey form)':M.flap_uncond_ln_rel,'flaperon, kernel and timing proxy':M.flap_timing_ln_rel}
    for n,l in terms.items():
        L=np.nan_to_num(np.exp(np.interp(lat,M.arc_lat.values[o],l.values[o]))); m,md,h=st(lat,core*L)
        out.append(dict(treatment=d,term=n,mean_shift_deg=m-m0,median_shift_NM=60*(md-md0),p95_shift_deg=h-h0,lnR_core_vs_uniform=np.log((core/core.sum()*L).sum()/((u/u.sum())*L).sum())))
    dr=np.nan_to_num(Z[f'{d}|drift']); Ld=np.divide(dr,u,out=np.zeros_like(dr),where=u>0); m,md,h=st(lat,np.nan_to_num(Z[f'{d}|core + drift']))
    out.append(dict(treatment=d,term='nine items, module likelihood (ledger)',mean_shift_deg=m-m0,median_shift_NM=60*(md-md0),p95_shift_deg=h-h0,lnR_core_vs_uniform=np.log((core/core.sum()*Ld).sum()/((u/u.sum())*Ld).sum())))
pd.DataFrame(out).to_csv('flaperon-only-indicative-shifts.csv',index=False,float_format='%.4f')
print(pd.DataFrame(out).query("treatment=='D0'").round(3).to_string(index=False))
