
s=json.load(open(AUD+'data/air9_audit_summary.json'))
for k in ['M1|z10|H01W|all','M1|z10|H08S|all','M1|z10|H08S|lt12.5','M1|z10|H08S|ge12.5','M1|z10|C2','M3_e0|z10|H01W|all','M3_e0|z10|H08S|all','M4_e0|z10|H01W|all','M4_e0|z10|H08S|all','M2|z10|H01W|all','M2|z10|H08S|all','M1|z9|H01W|all','M1|z12|H08S|all']:
    v=s.get(k); 
    if v: print(k, v['n'], v['f_lo'], v['f_hi'], round(v['level_median'],2), round(v['slope_db_per_oct'],2), round(v['slope_se'],2), round(v['shape_rms'],2), v['verdict'], v['grades'])
ss=json.load(open(AUD+'data/sus_summary.json'))
for k,v in ss.items(): print(k, v['n'], v['f_lo'], v['f_hi'], round(v['level_median'],1), round(v['slope_db_per_oct'],2), round(v['shape_rms'],2), v.get('verdict',''))
sb5=sb[sb.fc_hz==50].dropna(subset=['implied_sl_db']); print(sb5[['shot','station','implied_sl_db']].round(1).to_string())
