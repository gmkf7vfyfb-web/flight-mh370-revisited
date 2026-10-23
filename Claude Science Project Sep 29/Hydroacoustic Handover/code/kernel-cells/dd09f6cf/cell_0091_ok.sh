X=/Users/pete/Downloads/mh370-exchange/searched-areas/kadri-haixun-2026-10-18
python lib/pool_terms.py $X/per-seed $X/drift pool-check.csv 2>&1 | head -30; python -c "
import pandas as pd; d=pd.read_csv('pool-check.csv'); print(d[d.option=='D0'][['locality','seabed lnB s05','surface lnB a0.005 csiro']].round(3).to_string())"