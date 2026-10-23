stn={'SSEIR':(-33.51633,70.87617),'SWAMS3':(-42.95883,74.6295),'H01W2':(-34.898071,114.134048)}
cands={'K00:49:58 locus':(-35.87,91.45,'00:26:47'),'MP-69 locus':(-35.71,91.75,'00:26:52.0'),'K00:53:31 locus':(-36.74,90.29,'00:29:13'),'MP-20 locus':(-37.19,89.51,'00:33:31.7'),'MP-31 locus':(-34.21,93.74,'00:27:19.1'),'K00:40:34 locus':(-26.34,100.93,'00:22:47'),'K00:48:55 locus':(-28.80,99.03,'00:31:08'),'K00:52:50 locus':(-32.24,96.08,'00:33:42')}
res=[]
for st,(la,lo) in stn.items():
    bs=band_series(st); dt_=np.median(np.diff(bs.t_utc_s))
    for nm,(L,Lo,ti) in cands.items():
        d=G.inv(Lo,L,lo,la)[2]/1000; tp=hms(ti)+d/1.482
        for off in ([0,16] if st=='H01W2' else [0]):
            w=bs[(bs.t_utc_s>=tp+off-20)&(bs.t_utc_s<=tp+off+20)]; ref=bs[(bs.t_utc_s>=tp-600)&(bs.t_utc_s<=tp+600)]
            if len(w)==0: res.append((st,nm,fmt(tp),off,np.nan,np.nan)); continue
            ex=w.psd_db_5_40.max()-ref.psd_db_5_40.median()
            roll=ref.set_index('t_utc_s').psd_db_5_40.rolling(max(1,int(40/dt_))).max().dropna()-ref.psd_db_5_40.median()
            res.append((st,nm,fmt(tp+off),off,round(ex,1),round((roll>=ex).mean(),2)))
print(f"strip resolution {dt_:.2f} s")
RS=pd.DataFrame(res,columns=['station','candidate','pred_arrival','offset_s','max_excess_dB','frac_windows_as_high']); print(RS.to_string())