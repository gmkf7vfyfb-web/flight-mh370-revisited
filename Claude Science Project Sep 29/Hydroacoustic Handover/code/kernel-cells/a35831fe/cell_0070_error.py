def band_series(st):
    fs=sorted(glob.glob(SP+f'appendix_{st.lower()}_{st.lower()}_*_band.csv')); return pd.concat([pd.read_csv(f) for f in fs]).sort_values('t_utc_s')
res=[]
for st,(la,lo) in stn.items():
    bs=band_series(st); dt_=np.median(np.diff(bs.t_utc_s))
    for nm,(L,Lo,ti) in cands.items():
        d=G.inv(Lo,L,lo,la)[2]/1000; tp=hms(ti)+d/1.482
        for off in ([0,16] if st=='H01W2' else [0]):
            w=bs[(bs.t_utc_s>=tp+off-20)&(bs.t_utc_s<=tp+off+20)]; ref=bs[(bs.t_utc_s>=tp-600)&(bs.t_utc_s<=tp+600)]
            if len(w)==0: res.append((st,nm,fmt(tp),off,np.nan,np.nan)); continue
            mad=1.4826*(ref.psd_db_5_40-ref.psd_db_5_40.median()).abs().median()
            # chance: fraction of 40 s windows in ref with max >= observed
            ex=w.psd_db_5_40.max()-ref.psd_db_5_40.median()
            roll=ref.set_index('t_utc_s').psd_db_5_40.rolling(max(1,int(40/dt_))).max().dropna()-ref.psd_db_5_40.median()
            res.append((st,nm,fmt(tp+off),off,round(ex,1),round((roll>=ex).mean(),2)))
print(f"strip resolution {dt_:.2f} s")
print(pd.DataFrame(res,columns=['station','candidate','pred_arrival','offset_s','max_excess_dB','frac_windows_as_high']).to_string())