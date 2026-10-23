
G="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw/passA"
g=pd.read_csv(f"{G}/tl_grid.csv"); print(g.columns.tolist(), g.shape)
for c in ['receiver','station','fc_hz','src_depth_m','lat','lon','status','branch']:
    if c in g: print(c, sorted(g[c].unique())[:30])
print(g.head(3).to_string())
print(json.load(open(f"{G}/wall.json")))
src=pd.read_csv(f"{G}/sources.csv"); print(src.columns.tolist(), src.shape); print(src.head(3).to_string())
import re
P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/per_impact_lnl.py"
txt=open(P).read().split("\n")
for i,l in enumerate(txt):
    if re.search(r"rho|S_b|band_fraction|peak|T_eff|received|10 \* np.log10|tl_at|def ", l) and 150<i<420: print(i+1, l[:170])
