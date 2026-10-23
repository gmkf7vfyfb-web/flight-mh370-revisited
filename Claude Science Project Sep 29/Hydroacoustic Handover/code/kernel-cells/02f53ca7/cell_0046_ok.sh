cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
import sys; sys.path.insert(0,'.'); sys.argv=['x']
import tl_recal_block9 as B, numpy as np
pos,_=B.site_pos_heading('air7'); rcv=B.STATIONS['H01W'][0]
for d in [-60,-40,-30,30,40,50,60,80,100]:
    b,R=B.offset_section(pos,rcv,d)
    i=b.elevation_m.idxmax(); 
    # second shallowest region: max in a window away from crest
    m=b.elevation_m.values.copy(); j=i; m[max(0,j-400):j+400]=-9999
    print(d, 'crest', int(b.elevation_m[i]), 'at', round(b.lat[i],2), round(b.lon[i],2), round(b.range_km[i]), '| next', int(m.max()), 'at', round(b.lat[m.argmax()],2), round(b.lon[m.argmax()],2))
EOF
sed -n '/^def env/,/^def kraken_band/p' ram_tl_check.py