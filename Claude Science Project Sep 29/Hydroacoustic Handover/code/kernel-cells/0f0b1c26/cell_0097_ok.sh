cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; python - <<'EOF'
import pandas as pd, numpy as np
st=pd.read_csv('data/stations.csv',comment='#'); print(st.columns.tolist()); print(st.groupby('triad')[['lat','lon']].mean() if 'lat' in st else st.head())
EOF