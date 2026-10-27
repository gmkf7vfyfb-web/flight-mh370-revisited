import numpy as np, glob, json
from obspy import read, read_inventory, UTCDateTime as U
from scipy.signal import butter, sosfiltfilt
inv=read_inventory("verify/raw/inv.xml")
sos=butter(4,[5,40],btype='band',fs=250,output='sos')
res={}; allk={'H01W':[], 'H08S':[]}; rows=[]
for f in sorted(glob.glob("verify/raw/H0*_*.mseed")):
    st0=read(f); stn=f.split('/')[-1][:4]; yr=int(f[-10:-6])
    st0.merge(method=1, fill_value=None)
    for tr in st0.split():
        pass
    for tr in st0:
        tr=tr.copy()
        if np.ma.isMaskedArray(tr.data):
            # handle gaps: process contiguous pieces
            pieces=tr.split()
        else: pieces=[tr]
        for p in pieces:
            p.detrend('demean'); p.taper(0.02)
            p.remove_response(inventory=inv,output="DEF",pre_filt=(2,3,90,110),water_level=None)
            x=sosfiltfilt(sos,p.data.astype(float))
            t0=U(f"{yr}-03-08T00:27:00") if stn=='H01W' else U(f"{yr}-03-08T01:00:00")
            t1=t0+1800 if stn=='H01W' else t0+1200
            n0=int(np.ceil((max(t0,p.stats.starttime+20)-p.stats.starttime)*250)); 
            n1=int(np.floor((min(t1,p.stats.endtime-20)-p.stats.starttime)*250))
            seg=x[n0:n1]; nw=len(seg)//250
            if nw<1: continue
            w=seg[:nw*250].reshape(nw,250)
            pp=w.max(1)-w.min(1); rms=np.sqrt((w**2).mean(1)); k=pp/rms
            allk[stn]+=list(k)
            lvl=20*np.log10(np.median(rms)/1e-6)
            rows.append(dict(id=p.id,yr=yr,n=int(nw),k_med=float(np.median(k)),median_rms_db=float(lvl)))
for r in rows: print(r)
for s in allk: print(s,'pooled median k',np.median(allk[s]),'n',len(allk[s]), 'median of record medians', np.median([r['k_med'] for r in rows if r['id'][3:7]==s]))
json.dump(dict(rows=rows,pooled={s:float(np.median(allk[s])) for s in allk}),open('verify/v1_k.json','w'),indent=1)
