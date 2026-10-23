cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -i '' 's/grades.append(dict(zs=zs, n=len(fcs), heading=heading, phi_deg=phi, \*\*sc,/grades.append(dict(zs=zs, heading=heading, phi_deg=phi, **sc,/' tl_recal_block9.py
OUT=../results-data/tl_recal_block9; DIG=../results-data/digitised/blackman-2004
python tl_recal_block9.py air1 $OUT $DIG ../results-data/airgun_sites_confirm ../results-data/air9_ew0112
python -c "
import pandas as pd; r=pd.read_csv('$OUT/air1_h08n_check.csv'); print(r[r.zs==10].round(2).to_string(index=False))"