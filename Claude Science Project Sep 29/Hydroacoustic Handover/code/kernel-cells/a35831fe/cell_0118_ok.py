f_=None
for _,r in recs[recs.logger=='3275'].iterrows():
    f=SR.IMOS_ROOT/r.file; fs_,ts,n=_rec_cache.get(str(f),(None,None,None))
    if ts is not None and ts<=hms('01:20:35')<=ts+n/fs_: f_=f; break
v=NN.read_volts(f_); m3=meta['3275']; g=cal[cal.logger=='3275']; Gd=10*np.log10(np.mean([10**(g[g.band==b].gain_db.iloc[0]/10) for b in ('5-10','10-20','20-40')]))
x=v/np.sqrt(10**((Gd+m3['sens_db'])/10))*1e-6; tt=ts+np.arange(len(x))/fs_
def psd(t0,t1):
    k=(tt>=t0)&(tt<t1); return sg.welch(x[k],fs=fs_,nperseg=int(fs_*2))
fA,PA=psd(hms('01:20:33'),hms('01:20:43')); fB,PB=psd(hms('01:20:00'),hms('01:20:25'))
ex=10*np.log10(PA/PB)
for lo_,hi_ in [(5,10),(10,20),(20,40),(40,80),(80,200),(200,500)]:
    kk=(fA>=lo_)&(fA<hi_); print(f"{lo_}-{hi_} Hz excess {np.mean(ex[kk]):+.1f} dB, max {ex[kk].max():+.1f} at {fA[kk][np.argmax(ex[kk])]:.1f} Hz")
fig,ax=plt.subplots(figsize=(7,3)); ff,tt2,Sxx=sg.spectrogram(x[(tt>=hms('01:20:15'))&(tt<hms('01:21:00'))],fs=fs_,nperseg=6000,noverlap=4500)
ax.pcolormesh(tt2,ff,10*np.log10(Sxx),shading='auto',vmin=np.percentile(10*np.log10(Sxx),5),vmax=np.percentile(10*np.log10(Sxx),99.5)); ax.set_ylim(0,200); fig.savefig('cand/e3275_spec_check.png',dpi=120); plt.close(fig)