cd out && python3 - <<'EOF'
import csv
rows=list(csv.reader(open('ground-truth-cases.csv')))
h=rows[0]; ix={c:i for i,c in enumerate(h)}
for r in rows[1:]:
    cid=r[0]
    if cid.startswith('BLK-AIR'): r[ix['source_depth_m']]='near-surface towed array (depth not extracted)'
    if cid=='HEARD1991': r[ix['source_depth_m']]='not extracted'
    if cid=='PERTH-BERMUDA': r[ix['date_utc']]='1960'; r[ix['source_depth_m']]='not extracted'
    if cid=='TITAN': r[ix['source_depth_m']]='~3300-3700 during descent (approx.; not verified)'; r[ix['source_class']]='implosion during descent'
    if cid=='PRIOR2008': r[ix['event']]='39 kg TNT explosions recorded repeatedly at H11N/H03N (Prior et al., per Brown2026 Table A.4)'
    if cid=='KURSK': r[ix['source_depth_m']]='seafloor, ~100 m water (Bowers & Selby review; approx.)'
csv.writer(open('ground-truth-cases.csv','w',newline='')).writerows(rows)
print(len(rows)-1)
EOF