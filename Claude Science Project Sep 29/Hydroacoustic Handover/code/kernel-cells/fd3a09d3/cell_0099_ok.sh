OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid
mkdir -p final && cp /tmp/tlg_charts_final/*.png final/ && ls final
python - <<'EOF'
import pandas as pd
OUT='/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid'
tb=pd.read_csv(f'{OUT}/evidence/detectable_by_band.csv', dtype={'receiver':str}); tb=tb[tb.ridge_points=='excluded']
pd.set_option('display.width',200)
print(tb.pivot_table(index=['receiver','eta'],columns='lat_band',values='frac_pd').round(3).to_string())
ev=pd.read_csv(f'{OUT}/evidence/evidence_alone.csv', dtype={'receiver':str})
# offset sensitivity: frac_pd at eta=1e-3 by offset, mean over lat per receiver
e=ev[(ev.eta==1e-3)&(~ev.ridge_source)]; print(e.pivot_table(index='receiver',columns='offset_nm',values='frac_pd').round(3).to_string())
# TL offset sensitivity: 10 Hz H01W/H08S, mean abs difference offset vs 0
t=pd.read_csv(f'{OUT}/tables/ims_tl_kraken_arc.csv'); t=t[(t.src_depth_m==10)]
for st in ['H01W','H08S']:
    p=t[t.station==st].pivot_table(index=['lat','fc_hz'],columns='offset_nm',values='tl_db')
    print(st, {o: round(float((p[o]-p[0.0]).abs().mean()),2) for o in p.columns if o!=0}, 'max', {o: round(float((p[o]-p[0.0]).abs().max()),1) for o in p.columns if o!=0})
EOF