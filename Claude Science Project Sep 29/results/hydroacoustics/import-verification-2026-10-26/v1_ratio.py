import numpy as np, glob, json
from obspy import read, read_inventory, UTCDateTime as U
from scipy.signal import butter, sosfiltfilt, sosfilt, resample_poly
inv=read_inventory("verify/raw/inv.xml")
fs=250
S={'zp4':butter(4,[5,40],'band',fs=fs,output='sos'),'zp2':butter(2,[5,40],'band',fs=fs,output='sos'),'c4':butter(4,[5,40],'band',fs=fs,output='sos'),'zp4_2_40':butter(4,[2,40],'band',fs=fs,output='sos')}
out={st:{'k':{v:[] for v in S},'ratio':[],'k80':[], 'rate':[]} for st in ['H01W','H08S']}
def minmax_vertices(x, fs, vps):
    b=2.0/vps; nb=int(len(x)/(b*fs)); edges=(np.arange(nb+1)*b*fs).astype(int)
    v=[];ti=[]
    for i in range(nb):
        seg=x[edges[i]:edges[i+1]]; a=np.argmin(seg); c=np.argmax(seg)
        for j in sorted([a,c]): v.append(seg[j]); ti.append(edges[i]+j)
    return np.array(ti),np.array(v)
for f in sorted(glob.glob("verify/raw/H0*_*.mseed")):
    st0=read(f); stn=f.split('/')[-1][:4]; yr=int(f[-10:-6]); st0.merge(method=1)
    for tr in st0:
        for p in (tr.split() if np.ma.isMaskedArray(tr.data) else [tr]):
            p=p.copy(); p.detrend('demean'); p.taper(0.02)
            p.remove_response(inventory=inv,output="DEF",pre_filt=(1,1.5,90,110))
            t0=U(f"{yr}-03-08T00:27:00") if stn=='H01W' else U(f"{yr}-03-08T01:00:00"); t1=t0+(1800 if stn=='H01W' else 1200)
            n0=int(np.ceil((max(t0,p.stats.starttime+20)-p.stats.starttime)*fs)); n1=int(np.floor((min(t1,p.stats.endtime-20)-p.stats.starttime)*fs))
            nw=(n1-n0)//fs
            if nw<1: continue
            for v,sos in S.items():
                x=(sosfilt(sos,p.data) if v=='c4' else sosfiltfilt(sos,p.data))[n0:n0+nw*fs].reshape(nw,fs)
                out[stn]['k'][v]+=list((x.max(1)-x.min(1))/np.sqrt((x**2).mean(1)))
            x=sosfiltfilt(S['zp4'],p.data)[n0:n0+nw*fs]
            # 80 sps decimation (resample) then PP/RMS where RMS from full rate
            x80=resample_poly(x,8,25); w80=x80[:nw*80].reshape(nw,80); w=x.reshape(nw,fs)
            rms=np.sqrt((w**2).mean(1))
            out[stn]['k80']+=list((w80.max(1)-w80.min(1))/rms)
            ti,vv=minmax_vertices(x,fs,14.5); sec=ti//fs
            for s_ in range(nw):
                m=sec==s_
                if m.sum()>=8: out[stn]['ratio'].append(np.sqrt((vv[m]**2).mean())/rms[s_])
res={}
for stn,o in out.items():
    res[stn]={'k_'+v:float(np.median(o['k'][v])) for v in S}
    res[stn]['k80']=float(np.median(o['k80'])); res[stn]['vrms_ratio_minmax14.5']=float(np.median(o['ratio'])); res[stn]['n_ratio']=len(o['ratio'])
print(json.dumps(res,indent=1)); json.dump(res,open('verify/v1_ratio.json','w'),indent=1)
