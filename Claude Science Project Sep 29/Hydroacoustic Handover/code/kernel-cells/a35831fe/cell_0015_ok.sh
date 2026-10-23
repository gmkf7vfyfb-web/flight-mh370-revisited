cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/graphics-2026-10-22/ranked; ls -la; cat README.txt | head -80; python -c "
import pandas as pd
for f in ['ranked_singles.csv','ranked_pairs.csv','ranked_triples.csv','ranked_multisite.csv']:
    d=pd.read_csv(f); print(f,d.shape); print(list(d.columns))
"