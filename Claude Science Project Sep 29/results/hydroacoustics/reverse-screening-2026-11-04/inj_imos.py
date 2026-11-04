"""Section 11 injection tests on real IMOS null records (raw injection, inject_raw formula).
usage: inj_imos.py RS STATION NREP shard N"""
import sys, math, pickle, numpy as np, pandas as pd
from pathlib import Path
from scipy import signal as sps, stats
RS=Path(sys.argv[1]); ST=sys.argv[2]; NREP=int(sys.argv[3]); I,N=int(sys.argv[4]),int(sys.argv[5])
sys.path.insert(0,str(RS/'code'))
import screen_core as SC, reverse_detectors as rd
Z=pickle.load(open(RS/'cache/inj_inputs.pkl','rb'))
POOLS,PCRIT,RECS,LAGS,SHAPES,NPSD=Z['POOLS'],Z['PCRIT'],Z['NULLREC'][ST],Z['LAGS'],Z['SHAPES'],Z['NOISE_PSD']
FS=500.0; BL=50  # samples per 0.1 s envelope block
SNRS=np.arange(-12,13,3)
def pval(key,obs):
    pool=POOLS.get(key)
    if pool is None or not np.isfinite(obs): return np.nan
    return (1+pool.size-np.searchsorted(pool,obs,side='left'))/(1+pool.size)
SOS={b:rd.bandpass_sos(FS,*bd) for b,bd in SC.RAW_BANDS.items()}
CACHE={}
def rec(i):
    if i not in CACHE:
        f,seg=RECS[i]; x=np.load(f).astype(float)
        env={b:rd.raw_to_envelope(x,FS,band=bd,fs_out=10,mode='max')[1] for b,bd in SC.RAW_BANDS.items()}
        pn={b:np.mean(sps.sosfiltfilt(SOS[b],x)**2) for b in SC.RAW_BANDS}
        nperseg=int(FS*0.25); f_,t_,Zs=sps.stft(x,fs=FS,nperseg=nperseg,noverlap=nperseg//2,boundary=None)
        sel=(f_>=8)&(f_<=100); P=np.abs(Zs[sel])**2; ref=NPSD[seg]
        norm=math.log(2.0)/np.median(P/ref[:,None])
        if len(CACHE)>40: CACHE.clear()
        CACHE[i]=(x,env,pn,ref,norm)
    return CACHE[i]
def s6_local(xc, t_off, ref, norm, targets_t):
    nperseg=int(FS*0.25); f,t,Zs=sps.stft(xc,fs=FS,nperseg=nperseg,noverlap=nperseg//2,boundary=None)
    sel=(f>=8)&(f<=100); P=np.abs(Zs[sel])**2; W=P/ref[:,None]*norm
    dtb,dfb=t[1]-t[0],f[1]-f[0]; C=np.cumsum(np.cumsum(np.pad(W,((1,0),(1,0))),axis=0),axis=1)
    best=np.full(W.shape[1],-np.inf); bD=np.full(W.shape[1],99.0)
    for D in SC.S6_D:
        nt=max(1,int(round(D/dtb)))
        for B in SC.S6_B:
            nf=max(1,int(round(B/dfb)))
            if nt>W.shape[1] or nf>W.shape[0]: continue
            S=C[nf:,nt:]-C[:-nf,nt:]-C[nf:,:-nt]+C[:-nf,:-nt]
            v=SC.gamma_neglog10_sf(S,nf*nt).max(axis=0); u=v>best[:v.size]; best[:v.size][u]=v[u]; bD[:v.size][u]=D
    ts=t-0.125+t_off
    return np.array([np.max(best[(ts>=s0)&(ts+bD<=s0+10)],initial=-np.inf) for s0 in targets_t])
tasks=[(sh,snr,b,k) for sh in SHAPES for snr in SNRS for b in SC.RAW_BANDS for k in range(NREP)]
rng=np.random.default_rng(1000+I)
out=[]
for ti,(sh,snr,band,k) in enumerate(tasks):
    if ti%N!=I: continue
    ri=int(rng.integers(len(RECS))); x0,env0,pn,ref,norm=rec(ri)
    shape=np.asarray(SHAPES[sh],float); dur_s=len(shape)/10
    T=len(x0)/FS; t0=float(rng.uniform(15,T-40))
    # inject_raw formula with precomputed in-band noise power
    n_env=int(len(shape)*FS/10); e=np.interp(np.arange(n_env)/FS,np.arange(len(shape))/10.0,shape)
    s=sps.sosfiltfilt(SOS[band],rng.standard_normal(e.size))*e
    i0=int(round(t0*FS)); n=min(s.size,len(x0)-i0); w=max(1,min(n,int(10*FS)))
    g=math.sqrt(pn[band]*10**(snr/10)/np.mean(s[:w]**2))
    x=x0.copy(); x[i0:i0+n]+=g*s[:n]
    cs=max(0,int(np.floor((t0-15)*10))*BL); ce=min(len(x),int(np.ceil((t0+min(dur_s,200)+15)*10))*BL)
    p0=max(0,cs-int(10*FS)); p1=min(len(x),ce+int(10*FS))
    res=dict(station=ST,shape=sh,snr_db=snr,band_injected=band,rec=ri,t0=t0)
    pm={d:1.0 for d in ('S1','S2','S3','S4','S5','S6')}; s4on=(np.inf,np.nan)
    for b,bd in SC.RAW_BANDS.items():
        y=sps.sosfiltfilt(SOS[b],x[p0:p1]); a=np.abs(sps.hilbert(y))[cs-p0:ce-p0]
        nb=a.size//BL; env=env0[b].copy(); env[cs//BL:cs//BL+nb]=a[:nb*BL].reshape(nb,BL).max(1)
        lag=LAGS[(ST,b)]; p1d={}
        for L in SC.S1_L:
            tg=SC.target_windows(env.size,10.0,L,t0); z=SC.s1_local(env,10.0,L,tg)
            pp=np.array([pval((ST,'raw IMOS','S1',L,b),v) for v in z]); pm['S1']=min(pm['S1'],np.nanmin(pp,initial=1.0)); p1d[L]=(tg,pp)
        for L in SC.S2_L:
            tg=SC.target_windows(env.size,10.0,L,t0); T2=SC.s2_local(env,10.0,L,lag,tg)
            p2=np.array([pval((ST,'raw IMOS','S2',L,b),v) for v in T2]); pm['S2']=min(pm['S2'],np.nanmin(p2,initial=1.0))
            F=rd.fisher_combine(p1d[L][1],p2); p3=np.array([pval((ST,'raw IMOS','S3',L,b),v) for v in F]); pm['S3']=min(pm['S3'],np.nanmin(p3,initial=1.0))
            G=SC.s4_local(env,10.0,L,tg); p4=np.array([pval((ST,'raw IMOS','S4',L,b),v) for v in G])
            pm['S4']=min(pm['S4'],np.nanmin(p4,initial=1.0))
            if np.isfinite(p4).any():
                j=int(np.nanargmin(p4)); 
                if p4[j]<s4on[0]:
                    yy=SC.y_db(env); w_=int(L*10); st_=rd.window_starts(env.size,w_,max(1,int(round(L/4*10))))[tg[j]]
                    s4on=(p4[j],SC.s4_window(yy,10.0,st_,w_)[1]/10.0)
    st5=rd.window_starts(len(x),int(10*FS),int(2.5*FS)); tg5=st5[(st5/FS<=t0+10)&(st5/FS+10>=t0)]
    p5=[pval((ST,'raw IMOS','S5',10.0,'8-100 Hz'),rd.sk_statistic(x[s0:s0+int(10*FS)],FS,nperseg=128,fmin=8,fmax=100)[0]) for s0 in tg5]
    pm['S5']=np.nanmin(p5,initial=1.0)
    a6=max(0,int((t0-12)*FS)); b6=min(len(x),int((t0+22)*FS))
    v6=s6_local(x[a6:b6],a6/FS,ref,norm,tg5/FS); pm['S6']=np.nanmin([pval((ST,'raw IMOS','S6',10.0,'8-100 Hz'),v) for v in v6],initial=1.0)
    for d,v in pm.items(): res['pmin_'+d]=v
    res['onset_err_s']=s4on[1]-t0 if np.isfinite(s4on[1]) else np.nan
    out.append(res)
pd.DataFrame(out).to_csv(RS/f'cache/inj/{ST}_{I}.csv',index=False)
