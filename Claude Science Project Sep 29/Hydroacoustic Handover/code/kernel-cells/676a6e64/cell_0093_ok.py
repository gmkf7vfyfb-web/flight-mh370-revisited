from pyproj import Geod
g=Geod(ellps='WGS84')
h01=(-34.892899,114.1539); h08s=None
st=open('hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/stations.csv').read()
import re
rows=[l.split(',') for l in st.splitlines() if l and not l.startswith('#')]
hdr=rows[0]; d={r[1]:(float(r[2]),float(r[3])) for r in rows[1:]}
loc=(-33.6,94.5)
for rx in ['H01W','H08S']:
    la,lo=d[rx]; az,baz,dist=g.inv(lo,la,loc[1],loc[0])
    print(rx, f"bearing receiver->locus {az%360:.1f} deg, range {dist/1e3:.0f} km, travel {dist/1482/60:.1f} min")
la,lo=d['H01W']
for b in (57.0,306.18):
    print('Kadri bearing',b)
p=pd.read_csv(f'{S}/named/table1_verdicts.csv'); print(p.columns.tolist()); print(p.head(25).to_string()[:2500])