import sys, os, glob, io, numpy as np, pandas as pd, requests
sys.path.insert(0, os.getcwd())
import sigdet as SD, pmap
from score_records import load
from obspy import read, UTCDateTime
from scipy import stats, signal, ndimage
from multiprocessing import Pool
RB='/Users/pete/Downloads/mh370-inputs/hydroacoustics/ims_random_background'
STA={'H01W':(-34.8929,114.1539),'H08S':(-7.6453,72.4744)}
def cat(st):
    fn=f'usgs_{st}.csv'
    if os.path.exists(fn): return pd.read_csv(fn)
    la,lo=STA[st]; out=[]
    for y in range(2015,2026):
        for h in ((f'{y}-01-01',f'{y}-07-01'),(f'{y}-07-01',f'{y+1}-01-01')):
            u=f'https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime={h[0]}&endtime={h[1]}&latitude={la}&longitude={lo}&maxradius=70&minmagnitude=3.5&orderby=time-asc&limit=20000'
            out.append(pd.read_csv(io.StringIO(requests.get(u,timeout=120).text)))
    d=pd.concat(out); d.to_csv(fn,index=False); return d
def gc_km(la1,lo1,la2,lo2):
    p1,p2=np.radians(la1),np.radians(la2); dl=np.radians(lo2-lo1)
    return 6371*np.arccos(np.clip(np.sin(p1)*np.sin(p2)+np.cos(p1)*np.cos(p2)*np.cos(dl),-1,1))
def win30(fn):
    st=os.path.basename(fn)[:4]; s=read(fn,headonly=True); t0=s[0].stats.starttime
    _,x=load(fn,st)
    b,a=signal.butter(4,[5,40],btype='band',fs=SD.FS); xb=signal.filtfilt(b,a,x)
    n=int(30*SD.FS); m=len(xb)//n; E=(xb[:m*n].reshape(m,n)**2).mean(1)
    k=np.array([stats.kurtosis(xb[i*n:(i+1)*n],fisher=False) for i in range(m)])
    ok=np.array([(x[i*n:(i+1)*n]==0).mean()<0.001 for i in range(m)])
    ref=ndimage.median_filter(E,size=21,mode='reflect')
    ok=ndimage.minimum_filter1d(ok.astype(int),size=21,mode='nearest').astype(bool)
    return dict(rec=os.path.basename(fn)[:-6],st=st,t0=str(t0),E_db=10*np.log10(E/ref),kurt=k,ok=ok)
if __name__=='__main__':
    C={st:cat(st) for st in STA}
    for st in STA: print(st,'catalogue events',len(C[st]),'M>=4.5:',(C[st].mag>=4.5).sum())
    with Pool(16) as p: W=p.map(win30,sorted(glob.glob(RB+'/*.mseed')),chunksize=4)
    starts={w['rec']:UTCDateTime(w['t0']) for w in W}
    # ---- noise distribution of 30 s band energy over 10 min running median (dB)
    rows=[]
    for st in STA:
        e=np.concatenate([w['E_db'][w['ok']] for w in W if w['st']==st]); kk=np.concatenate([w['kurt'][w['ok']] for w in W if w['st']==st])
        fin=np.isfinite(e)&np.isfinite(kk); e=e[fin]; kk=kk[fin]
        med=np.median(e); sig=1.4826*np.median(np.abs(e-med))
        u=np.quantile(e,0.95); ex=e[e>u]-u; xi,_,sc=stats.genpareto.fit(ex,floc=0)
        g_theory=10*np.log10(1+1/np.sqrt(35*30))
        rows.append(dict(station=st,n_windows=len(e),median_dB=med,core_sd_dB=sig,gauss_theory_sd_dB=g_theory,
            frac_above_core_3sd=np.mean(e>med+3*sig),gauss_expect_3sd=stats.norm.sf(3),
            q99=np.quantile(e,0.99),q999=np.quantile(e,0.999),max=e.max(),gpd_threshold_dB=u,gpd_shape_xi=xi,gpd_scale_dB=sc,
            kurt_median=np.median(kk),kurt_q95=np.quantile(kk,0.95),kurt_q99=np.quantile(kk,0.99)))
    ND=pd.DataFrame(rows); ND.to_csv('noise_distribution_fit.csv',index=False); print(ND.round(3).T.to_string())
    # ---- earthquake flags on 2 min looks
    B=pd.read_csv('joint_background.csv'); B=B[B.kind=='rnd'].copy(); P=pmap.PMap(pd.read_csv('joint_background.csv'),'rnd')
    for st in STA:
        m=B.st==st; B.loc[m,'COMB']=P.fisher(st,{s:B.loc[m,s].values for s in pmap.COMB})
    B['t_abs']=[float(starts[r]+b0) for r,b0 in zip(B.rec,B.b0)]
    for st in STA:
        d=C[st]; ot=np.array([UTCDateTime(t).timestamp for t in d.time]); D=gc_km(STA[st][0],STA[st][1],d.latitude.values,d.longitude.values)
        lo=ot+D/1.52-30; hi=ot+D/1.45+180; mag=d.mag.values
        for mm,lab in ((3.5,'flag_m35'),(4.5,'flag_m45')):
            sel=mag>=mm; L,Hh=np.sort(lo[sel]),hi[sel][np.argsort(lo[sel])]
            m=B.st==st; ts=B.loc[m,'t_abs'].values
            # look [t, t+120] overlaps any [lo,hi]
            idx=np.searchsorted(L,ts+120); f=np.zeros(len(ts),bool)
            for j,i in enumerate(idx):
                k=np.arange(max(0,i-400),i); f[j]=bool(np.any(Hh[k]>=ts[j])) if len(k) else False
            B.loc[m,lab]=f
    B.to_csv('background_eq_flags.csv',index=False)
    out=[]
    for st,g in B.groupby('st'):
        for s in ['L_d0','S_d1','C_imp','E_pers','COMB']:
            for lab in ('flag_m35','flag_m45'):
                r=dict(station=st,detector=s,catalogue=lab,frac_time_flagged=g[lab].mean())
                for q in (0.95,0.99,0.998):
                    thr=np.nanquantile(g[s],q); top=g[g[s]>=thr]
                    r[f'flagged_in_top_{round((1-q)*100,1)}pct']=top[lab].mean()
                    r[f'thr_q{q}_all']=thr; r[f'thr_q{q}_unflagged']=np.nanquantile(g[~g[lab].astype(bool)][s],q)
                out.append(r)
    T=pd.DataFrame(out); T.to_csv('tail_removal_by_catalogue.csv',index=False)
    pd.set_option('display.width',250); print(T.round(3).to_string())
