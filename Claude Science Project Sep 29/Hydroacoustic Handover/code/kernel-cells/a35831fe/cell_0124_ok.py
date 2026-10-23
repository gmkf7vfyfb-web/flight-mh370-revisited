def env1s(tr,p,fs_,lo=5,hi=40):
    sos=sg.butter(4,[lo,hi],btype='band',fs=fs_,output='sos')
    return tr, np.sqrt(pd.Series(p**2).rolling(int(fs_),center=True).mean().values)
# 1) known event: CMST 2014 Perth Canyon peak ~01:33:42 (CMST Fig. 1: ~222 s after 01:30:00)
o=imos_rec('3315',hms('01:33:42')); tr,p,fs_=o
_,e=env1s(tr,p,fs_); k=(tr>hms('01:32:30'))&(tr<hms('01:34:30'))
print('3315 envelope peak at', fmt(tr[k][np.nanargmax(e[k])]), f"{20*np.log10(np.nanmax(e[k])/np.nanmedian(e[(tr>hms('01:30:00'))&(tr<hms('01:33:00'))])):.1f} dB over median")
# 2) each member detection: level in its own detection band around the detection time vs the rest of the record
members=[('A','3376','00:51:30',(2,5)),('A','3274','01:15:51',(5,10)),('B','3315','00:49:48',(5,40)),('B','3274','01:15:51',(5,10)),
         ('D','3376','00:52:11',(5,40)),('D','3274','01:15:51',(5,10)),('E','3376','00:55:01',(2,5)),('E','3275','01:20:35',(5,40)),
         ('F','3315','01:00:34',(2,5)),('F','3275','01:24:02',(2,5))]
out=[]
for kk,r,t,(lo,hi) in members:
    o=imos_rec(r,hms(t)); tr,p_raw,fs_=o
    # re-read unfiltered from the module reader for band-specific level
    f=[SR.IMOS_ROOT/x.file for _,x in recs[recs.logger==r].iterrows() if _rec_cache.get(str(SR.IMOS_ROOT/x.file),(0,1e9,0))[1]<=hms(t)<=_rec_cache.get(str(SR.IMOS_ROOT/x.file),(0,-1,0))[1]+307][0]
    v=NN.read_volts(f); sos=sg.butter(4,[max(lo,0.5),hi],btype='band',fs=fs_,output='sos'); y=sg.sosfiltfilt(sos,v)
    e1=np.sqrt(pd.Series(y**2).rolling(int(fs_),center=True).mean().values); tt_=tr
    kw=np.abs(tt_-hms(t))<=3; pk=np.nanmax(e1[kw]); allv=e1[np.isfinite(e1)][::600]
    out.append(dict(cand=kk,rx=r,time=t,band=f"{lo}-{hi}",dB_over_record_median=round(20*np.log10(pk/np.median(allv)),1),percentile_in_record=round(100*(allv<pk).mean(),1)))
print(pd.DataFrame(out).to_string())