sh=pd.read_csv(fs_[0]); print(sh.columns.tolist()); print(sh.head(3).to_string())
num=[c_ for c_ in sh.columns if np.issubdtype(sh[c_].dtype,np.number)]
for c_ in num[:3]:
    v=np.sort(sh[c_].dropna().values); dv=np.diff(v)
    print(c_, 'median diff %.2f IQR %.2f-%.2f'%(np.median(dv),*np.percentile(dv,[25,75])))
y=out['psd_db_5_40']; y=np.nan_to_num(y-np.nanmean(y)); ac=np.correlate(y,y,'full')[len(y)-1:]; ac/=ac[0]
for L_ in [9.38,10.94,18.75,20.31]: print('SWAMS3 ac at %.2f s: %.2f'%(L_,ac[int(round(L_/1.5625))]))