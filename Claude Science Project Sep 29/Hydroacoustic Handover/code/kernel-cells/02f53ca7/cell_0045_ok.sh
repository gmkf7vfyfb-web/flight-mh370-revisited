W=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal; tail -4 $W/nx2d.log
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/tl_recal_block9"; python -c "
import pandas as pd; T=pd.read_csv('tl_runs.csv'); off=T[T.tag.str.startswith('air7off')].copy(); off['d']=off.tag.str.extract(r'air7off([+-]\d+)_')[0].astype(float)
print(off.pivot(index='fc_hz',columns='d',values='tl_db').round(1).to_string()); print(off.groupby('d').min_profile_depth_m.first())
a9=T[T.tag=='builder_air9_H01W_a7b'].set_index('fc_hz').tl_db; print(a9.round(1).to_dict())
"