from scipy.signal import find_peaks
cd=CANDS_bak; t0=cd['t0']
print('rstrip keys',list(rstrip.keys()), rstrip['SSEIR'].columns.tolist()[:8])
for r in ['SSEIR','SWAMS3','H01W2']:
    b=rstrip[r]; la_,lo_=rx_roy[r]; d=GW.inv(lo_,la_,cd['lon'],cd['lat'])[2]/1000; tt=d/c
    seg=b[(b.t_utc_s>=t0+tt-300)&(b.t_utc_s<=t0+tt+300)].sort_values('t_utc_s')
    dt=np.median(np.diff(seg.t_utc_s)); y=seg.psd_db_5_40.values-seg.psd_db_5_40.median()
    pk,_=find_peaks(y,height=4,distance=max(1,int(5/dt)))
    pt=seg.t_utc_s.values[pk]; iv=np.diff(pt)
    print(f"{r}: bin {dt:.2f} s, {len(pk)} peaks >4 dB in +/-300 s; intervals median {np.median(iv) if len(iv) else np.nan:.2f} s, IQR {np.percentile(iv,25) if len(iv) else 0:.2f}-{np.percentile(iv,75) if len(iv) else 0:.2f}")
shots=pd.read_csv([p for p in __import__('glob').glob('/Users/pete/Downloads/mh370-exchange/hydroacoustics/**/h08s_template_shots.csv',recursive=True)][0])
print(shots.columns.tolist()[:6]); 
tc=[x for x in shots.columns if 't' in x.lower()][0]; st=np.sort(shots[tc].values); print('H08S shot interval median %.2f s IQR %.2f-%.2f'%(np.median(np.diff(st)),*np.percentile(np.diff(st),[25,75])))