SP=H+'digitised/royer-2016/spectrograms/'
b=pd.read_csv(SP+'appendix_sseir_sseir_0030-0100_band.csv'); print(b.columns.tolist(), b.shape); print(b.head(3))
stn={'SSEIR':(-33.51633,70.87617),'SWAMS3':(-42.95883,74.6295),'H01W2':(-34.898071,114.134048)}
cands={'K00:49:58 locus':(-35.87,91.45,'00:26:47'),'MP-69 locus':(-35.71,91.75,'00:26:52.0'),'K00:53:31 locus':(-36.74,90.29,'00:29:13'),'MP-20 locus':(-37.19,89.51,'00:33:31.7'),'MP-31 locus':(-34.21,93.74,'00:27:19.1')}
def band_series(st):
    fs=sorted(glob.glob(SP+f'appendix_{st.lower()}_{st.lower()}_*_band.csv')); return pd.concat([pd.read_csv(f) for f in fs])
for st,(la,lo) in stn.items():
    bs=band_series(st); tcol=[c for c in bs.columns if 't_utc_s' in c or c.startswith('t')][0]; vcol=[c for c in bs.columns if '5' in c and '40' in c][0]
    bs=bs.sort_values(tcol)
    for nm,(L,Lo,ti) in cands.items():
        d=G.inv(Lo,L,lo,la)[2]/1000; tp=hms(ti)+d/1.482
        w=bs[(bs[tcol]>=tp-30)&(bs[tcol]<=tp+30)]; ref=bs[(bs[tcol]>=tp-600)&(bs[tcol]<=tp+600)]
        if len(w)==0: print(st,nm,fmt(tp),'no strip'); continue
        z=(w[vcol].max()-ref[vcol].median())/(1.4826*(ref[vcol]-ref[vcol].median()).abs().median())
        print(st,nm,'pred',fmt(tp),f"max in ±30 s: {w[vcol].max()-ref[vcol].median():+.1f} dB over local median, robust z {z:.1f}")