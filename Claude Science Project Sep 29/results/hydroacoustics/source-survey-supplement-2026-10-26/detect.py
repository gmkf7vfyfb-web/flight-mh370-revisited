"""T-phase detector for island/coastal seismometers.
Steps per station-channel: merge day files, demean, taper, divide by the overall sensitivity (StationXML) to
ground velocity (scalar; full deconvolution was rejected because it shifted the GE.CISI time base by -43.5 s), decimate to <= 40 sps, band-pass (Butterworth 4 poles,
zero phase), 1-s RMS envelope e(t). STA = mean of e^2 over 10 s; LTA = median of e^2 over the 600 s that end
20 s before the STA window (delayed, robust). R = STA/LTA (energy ratio); SNR = sqrt(R) (amplitude ratio).
Trigger on SNR >= 2.0, off SNR < 1.4, min duration 8 s, merge triggers less than 10 s apart.
Per detection: onset, end, duration, peak time, peak SNR, peak frequency (peak of the Welch signal / pre-onset
noise spectral ratio, 1 Hz to 0.9 Nyquist), RMS velocity in band (nm/s), HF/LF ratio (RMS 2-8 Hz / RMS 0.5-2 Hz)
relative to the same ratio in the 600 s before onset (a T-phase-likeness index; >1 means relatively rich in
high frequencies)."""
import glob, os, sys, numpy as np, pandas as pd, warnings
from obspy import read, read_inventory, Stream
from scipy.signal import butter, sosfiltfilt, welch
from scipy.ndimage import median_filter
warnings.filterwarnings('ignore')
BANDS={'2-8':(2.,8.),'3-12':(3.,12.)}
STA_S, LTA_S, GAP_S = 10, 600, 20
ON, OFF, MIN_DUR, MERGE = 2.0, 1.4, 8, 10

def load(files, xml, t0=None, t1=None):
    st=Stream()
    for f in files: st+=read(f)
    st.merge(method=1, fill_value=None)
    if t0 is not None: st.trim(t0,t1)
    tr=st[0]
    mask=np.ma.getmaskarray(tr.data) if np.ma.isMaskedArray(tr.data) else np.zeros(tr.stats.npts,bool)
    d=np.ma.filled(tr.data.astype(float), np.nan) if np.ma.isMaskedArray(tr.data) else tr.data.astype(float)
    med=np.nanmedian(d); d=np.where(np.isnan(d),med,d)-med
    tr.data=d
    inv=read_inventory(xml)
    fs=tr.stats.sampling_rate; nyq=fs/2
    tr.taper(0.001)
    tr.remove_sensitivity(inventory=inv)   # scalar only: full deconvolution shifted GE.CISI by about -43.5 s (FIR phase), see note
    tr.data[mask]=0.0
    if fs>40:
        f=int(round(fs/40)); tr.filter('lowpass',freq=16.,corners=8,zerophase=True); tr.data=tr.data[::f]; tr.stats.sampling_rate=fs/f; mask=mask[::f]
    return tr, mask

def rms1(x, fs):
    n=int(fs); m=len(x)//n
    return np.sqrt((x[:m*n].reshape(m,n)**2).mean(1))

def detect(tr, mask, band):
    fs=tr.stats.sampling_rate; lo,hi=BANDS[band]
    if hi>=0.45*fs: return None, None
    sos=butter(4,[lo,hi],btype='band',fs=fs,output='sos')
    y=sosfiltfilt(sos,tr.data)
    e2=rms1(y,fs)**2
    gap=rms1(mask.astype(float),fs)>0  # seconds touching gaps
    n=len(e2)
    sta=np.convolve(e2,np.ones(STA_S)/STA_S,mode='full')[:n]          # trailing mean ending at t
    # median over [t-STA-GAP-LTA, t-STA-GAP): computed on 10-s blocks for speed
    blk=e2[:n//10*10].reshape(-1,10).mean(1)
    lb=median_filter(blk,size=LTA_S//10,origin=(LTA_S//10)//2-1,mode='nearest') if len(blk)>LTA_S//10 else np.full(len(blk),np.median(blk))
    lta=np.repeat(lb,10); lta=np.r_[lta,np.full(n-len(lta),lta[-1])]
    sh=STA_S+GAP_S; lta=np.r_[np.full(sh,lta[0]),lta[:-sh]]
    R=sta/np.maximum(lta,1e-30); snr=np.sqrt(R)
    bad=np.convolve(gap.astype(float),np.ones(LTA_S+sh),mode='full')[:n]>0
    snr[bad]=0; snr[:LTA_S+sh]=0
    on=snr>=ON; dets=[]; i=0
    while i<n:
        if on[i]:
            j=i
            while j<n and snr[j]>=OFF: j+=1
            dets.append([i,j]); i=j
        i+=1
    merged=[]
    for a,b in dets:
        if merged and a-merged[-1][1]<=MERGE: merged[-1][1]=b
        else: merged.append([a,b])
    rows=[]
    t0=tr.stats.starttime
    for a,b in merged:
        a0=max(a-STA_S+1,0)   # STA window starts STA_S-1 s before first trigger second
        dur=b-a0
        if dur<MIN_DUR: continue
        pk=a+int(np.argmax(snr[a:b]))
        seg=tr.data[int(a0*fs):int(b*fs)]
        pre_s=tr.data[int(max(a0-600,0)*fs):int(a0*fs)]
        nps=min(len(seg),int(4*fs))
        f,P=welch(seg,fs=fs,nperseg=nps)
        if len(pre_s)>nps:
            _,Pn=welch(pre_s,fs=fs,nperseg=nps); ratio=P/np.maximum(Pn,1e-40)
        else: ratio=P
        k=(f>=1.0)&(f<=0.9*fs/2); fpk=f[k][np.argmax(ratio[k])]   # peak of signal/pre-noise spectral ratio
        def bandrms(x,l,h):
            s=butter(4,[l,h],btype='band',fs=fs,output='sos'); return np.sqrt(np.mean(sosfiltfilt(s,x)**2))
        pre=tr.data[int(max(a0-600,0)*fs):int(a0*fs)]
        try:
            hl=(bandrms(seg,2,8)/bandrms(seg,0.5,2))/(bandrms(pre,2,8)/bandrms(pre,0.5,2)) if len(pre)>fs*60 else np.nan
        except Exception: hl=np.nan
        rows.append(dict(band=band,onset_utc=str(t0+a0)[:22],end_utc=str(t0+b)[:22],duration_s=dur,peak_utc=str(t0+pk)[:22],
             peak_snr=float(snr[pk]),peak_freq_hz=float(fpk),rms_band_nm_s=float(np.sqrt(e2[a0:b].mean())*1e9),hf_lf_rel=float(hl),
             onset_s=float(t0+a0-t0), t0=str(t0)))
    return pd.DataFrame(rows), (snr, str(t0))
