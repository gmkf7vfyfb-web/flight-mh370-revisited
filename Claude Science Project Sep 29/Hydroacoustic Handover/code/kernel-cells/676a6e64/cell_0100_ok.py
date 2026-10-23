import pandas as pd, glob
R='/Users/pete/Downloads/mh370-exchange/hydroacoustics/graphics-2026-10-22/ranked/'
sg=pd.read_csv(R+'ranked_singles.csv'); pr=pd.read_csv(R+'ranked_pairs.csv')
print([c for c in sg.columns if 'eta' in c.lower() or 'rank' in c.lower()][:20])
print(sg.head(3)[[c for c in sg.columns if 'eta' in c.lower() or c in ('receiver','time_utc','rank','ln_lr','lnLR')]].T.to_string()[:2000])
m = glob.glob('repo/**/arrival_window_matrix.csv', recursive=True) or glob.glob('/Users/pete/.claude-science/orgs/*/artifacts/**/*arrival_window_matrix*.csv', recursive=True)
print(m[:2])