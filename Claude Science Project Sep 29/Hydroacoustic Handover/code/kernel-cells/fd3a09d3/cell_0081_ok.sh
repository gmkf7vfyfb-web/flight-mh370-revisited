python - <<'EOF'
import pandas as pd, numpy as np
ev=pd.read_csv('/tmp/tlg_ev_AB/evidence_alone.csv', dtype={'receiver':str}); e=ev[(ev.offset_nm==0)&(ev.eta==1e-4)&(~ev.ridge_source)]
g=e.groupby('receiver').agg(spl_max=('spl_at_E_q50','max'), noise=('noise_median','first')); g['gap_at_2.1e-4']=g.noise-(g.spl_max+10*np.log10(2.1)); print(g.round(1))
s=pd.concat([pd.read_csv(f'/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw/pass{p}/sources.csv') for p in 'AB']); s=s[s.source_id.str.startswith('arc')]
print('rms', s.arc_fit_rms_deg.min().round(3), s.arc_fit_rms_deg.median().round(3), s.arc_fit_rms_deg.max().round(3)); print(s[s.arc_fit_extrapolated][['source_id','arc_fit_rms_deg']].to_string(index=False))
EOF
grep paths /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw/passC.log | tail -1; date -u