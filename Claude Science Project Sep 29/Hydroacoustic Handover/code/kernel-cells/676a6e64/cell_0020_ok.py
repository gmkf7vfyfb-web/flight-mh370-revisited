import subprocess, io, pandas as pd, numpy as np
base='Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data/kadri-figure-extraction/figure9-vector-traces/'
def load(p):
    s=subprocess.run(['git','show',f'FETCH_HEAD:{base}kadri-2024-figure9-panel-{p}.csv'],cwd='repo',capture_output=True,text=True).stdout
    return pd.read_csv(io.StringIO(s))
res={}
for p,t0 in [('a-H01W','00:27'),('b-H01W','00:37'),('c-H01W','00:47')]:
    d=load(p); t=d.plotted_time_s.values; x=d.pressure_pa.values
    fs=1/np.median(np.diff(t)); 
    # resample to uniform grid
    tu=np.arange(t.min(),t.max(),1/fs); xu=np.interp(tu,t,x)
    e=xu**2
    def box(sig,w): 
        k=max(1,int(round(w*fs))); c=np.cumsum(np.insert(sig,0,0)); out=np.full_like(sig,np.nan); out[k-1:]=(c[k:]-c[:-k])/k; return out
    sta=box(e,1.0); lta=np.roll(box(e,20.0),1)  # LTA ending just before STA window start approx
    r=sta/lta; r[:int(21*fs)]=np.nan
    env=np.abs(xu)
    print(f"panel {p} start {t0}: fs~{fs:.1f} Hz, n={len(x)}, rms={np.sqrt(np.mean(xu**2)):.3f} Pa, max|p|={env.max():.3f} Pa at {t0}+{tu[env.argmax()]/60:.2f} min; max STA/LTA {np.nanmax(r):.2f} at +{tu[np.nanargmax(r)]/60:.2f} min")
    res[p]=(tu,xu,r)
# panel a boxes (minutes after 00:27, read from poster)
tu,xu,r=res['a-H01W']; rms_all=np.sqrt(np.mean(xu**2))
for a,b in [(1.2,2.7),(3.4,4.9),(5.5,7.0),(8.4,9.9)]:
    m=(tu>=a*60)&(tu<b*60); 
    print(f"box {a}-{b} min: max STA/LTA {np.nanmax(r[m]):.2f}, rms in box {np.sqrt(np.mean(xu[m]**2)):.3f} Pa ({20*np.log10(np.sqrt(np.mean(xu[m]**2))/rms_all):+.1f} dB vs panel), max|p| {np.abs(xu[m]).max():.3f} Pa")
# outside boxes
mo=np.ones_like(tu,bool)
for a,b in [(1.2,2.7),(3.4,4.9),(5.5,7.0),(8.4,9.9)]: mo&=~((tu>=a*60)&(tu<b*60))
print(f"outside boxes: rms {np.sqrt(np.mean(xu[mo]**2)):.3f} Pa, max STA/LTA {np.nanmax(r[mo]):.2f}")
# panel c boxes for comparison
tu,xu,r=res['c-H01W']
for a,b in [(4.2,5.8),(6.8,8.3)]:
    m=(tu>=a*60)&(tu<b*60); print(f"panel c box {a}-{b}: max STA/LTA {np.nanmax(r[m]):.2f} at +{tu[m][np.nanargmax(r[m])]/60:.2f} min, max|p| {np.abs(xu[m]).max():.3f}")