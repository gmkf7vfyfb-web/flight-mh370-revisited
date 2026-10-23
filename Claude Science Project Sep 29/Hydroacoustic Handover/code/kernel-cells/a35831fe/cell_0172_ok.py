import glob
fs_=glob.glob('/Users/pete/Downloads/**/h08s_template_shots.csv',recursive=True)+glob.glob('**/h08s_template_shots.csv',recursive=True)
print(fs_[:3])
for r in ['SSEIR','SWAMS3']:
    b=rstrip[r]; la_,lo_=rx_roy[r]; d=GW.inv(lo_,la_,cd['lon'],cd['lat'])[2]/1000; tt=d/c
    seg=b[(b.t_utc_s>=t0+tt-300)&(b.t_utc_s<=t0+tt+300)].sort_values('t_utc_s')
    out={}
    for col in ['psd_db_5_40','psd_db_10_15','psd_db_2_60']:
        y=seg[col].values-np.nanmedian(seg[col].values); out[col]=y
    pk,_=find_peaks(out['psd_db_5_40'],height=4,distance=3)
    print(r,'at 5-40 Hz peaks: mean excess 5-40 %.1f dB, 10-15 %.1f dB, 2-60 %.1f dB'%tuple(np.nanmean(out[k][pk]) for k in ['psd_db_5_40','psd_db_10_15','psd_db_2_60']))
    y=out['psd_db_5_40']; y=np.nan_to_num(y-np.nanmean(y)); ac=np.correlate(y,y,'full')[len(y)-1:]; ac/=ac[0]
    dt=np.median(np.diff(seg.t_utc_s)); lag=np.arange(len(ac))*dt; sel_=(lag>4)&(lag<30)
    print('   autocorrelation peak at %.2f s (r=%.2f)'%(lag[sel_][ac[sel_].argmax()],ac[sel_].max()))