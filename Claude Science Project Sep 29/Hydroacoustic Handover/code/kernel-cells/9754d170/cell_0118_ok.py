
a=sb[(sb.shot=='A11sus')&(sb.station=='H01W')].dropna(subset=['implied_sl_db'])
st_=AA.stats(list(a.fc_hz),list(a.implied_sl_db)); print({k:(round(v,2) if isinstance(v,float) else v) for k,v in st_.items()})
v50=sb5.implied_sl_db.values; print(np.median(v50), v50.min(), v50.max(), np.median(v50[sb5.shot!='A11sus']), np.std(v50[sb5.shot!='A11sus']))
