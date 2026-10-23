cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data"
python -c "
import json; v=json.load(open('ram_check/verdicts.json')); print({k:v[k] for k in v if 'wall' in k.lower() or 'time' in k.lower()}); print(list(v.keys()))
import pandas as pd; a=pd.read_csv('air9_ew0112/air9_farfield_array_factor.csv'); print(a.pivot_table(index='fc_hz',columns=['station','across_sign','weights'],values='af_db').round(2).to_string())
"
uptime; python -c "import pyram; print(pyram.__version__ if hasattr(pyram,'__version__') else 'pyram ok')"