b=rstrip['H01W2']; la_,lo_=rx_roy['H01W2']; d=GW.inv(lo_,la_,cd['lon'],cd['lat'])[2]/1000; tt=d/c
seg=b[(b.t_utc_s>=t0+tt-300)&(b.t_utc_s<=t0+tt+300)]; y=seg.psd_db_5_40-seg.psd_db_5_40.median()
w=seg[(seg.t_utc_s>=t0+tt-20)&(seg.t_utc_s<=t0+tt+20)]; yw=w.psd_db_5_40-seg.psd_db_5_40.median()
print('H01W-2 +/-300 s: sd %.2f dB, 95th pct %.2f, max %.2f; in +/-20 s window max %.2f dB'%(y.std(),np.percentile(y,95),y.max(),yw.max()))
print('rank of window max among 40-s windows:', (pd.Series(y.values).rolling(26).max()>=yw.max()).mean().round(2))
SUMc=pd.read_csv('cand/candidates-A-F-summary.csv'); print(SUMc[[c_ for c_ in SUMc.columns if c_.startswith('SNR') or c_ in('cand','E_median_GJ')]].to_string())