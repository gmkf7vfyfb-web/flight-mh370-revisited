import sys, os, glob, numpy as np, pandas as pd
sys.path.insert(0, os.getcwd())
import sigdet as SD
from score_records import load
RB='/Users/pete/Downloads/mh370-inputs/hydroacoustics/ims_random_background'
SEG=720.0
def replay(st,seed):
    rng=np.random.default_rng(seed)
    recs=sorted(os.path.basename(p)[:-6] for p in glob.glob(f'{RB}/{st}1_rnd*.mseed'))
    for _ in range(50):
        k=recs[rng.integers(len(recs))]; t0,x=load(f'{RB}/{k}.mseed',st); T=len(x)/SD.FS
        tc=rng.uniform(SEG/2+5,T-SEG/2-5); i0=int((tc-SEG/2)*SD.FS); seg=x[i0:i0+int(SEG*SD.FS)]
        if (seg==0).mean()>0.001: continue
        break
    R=rng.uniform(1500,4500); fc=np.exp(rng.uniform(np.log(1),np.log(20))); a=rng.uniform(2,4); dec=rng.uniform(3,20); rise=rng.uniform(0.3,2.0)
    rng.standard_normal(int(240*SD.FS)); f0=rng.uniform(2,4)
    return dict(st=st,seed=seed,host=k,range_km=R,corner_Hz=fc,slope=a,decay_s=dec,rise_s=rise,lowcut_Hz=f0)
P=pd.DataFrame([replay('H01W',0),replay('H08S',100000)]); print(P.round(2).to_string())
# median noise spectra per station
NS={}
for st in ('H01W','H08S'):
    fs=sorted(glob.glob(f'{RB}/{st}1_rnd*.mseed'))[::4][:40]; Ns=[]
    for fn in fs:
        _,x=load(fn,st); t,Pp=SD.spec(x); Ns.append(np.median(Pp,1))
    NS[st]=np.median(Ns,0)
f=SD.F; band=(f>=3)&(f<=60)
for st in NS: print(st,'noise PSD dB re 1 uPa^2/Hz at 5/10/20/40 Hz:',[round(10*np.log10(np.interp(v,f,NS[st])*1e12),1) for v in (5,10,20,40)])
pd.DataFrame({'f':f,'H01W':NS['H01W'],'H08S':NS['H08S']}).to_csv('station_noise_median_psd.csv',index=False)
# whitened shape of each replayed case and of one common source at each station's real distance
def shape(fc,a,R,f0,N): return SD.src_shape(f,fc,a)*SD.channel(f,f0=f0,R_km=R)/N
for _,r in P.iterrows():
    w=shape(r.corner_Hz,r.slope,r.range_km,r.lowcut_Hz,NS[r.st]); w=w/w[band].max()
    print(r.st,'case whitened S/N (dB rel peak) at 5/10/20/40 Hz:',[round(10*np.log10(np.interp(v,f,w)),1) for v in (5,10,20,40)],'peak at',round(f[band][np.argmax(w[band])],1),'Hz')
