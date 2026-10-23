rv=open(host.artifact_path('17b39438-4234-4068-a2a0-213cafd12d9c')).read()
for i,l in enumerate(rv.split('\n')):
    if l.startswith('#'): print(i,l)
reg=pd.read_csv(host.artifact_path('e80ab18e-2296-4d13-98b6-7c7ed411df9d')); print(reg.shape, reg.columns.tolist())
vc=[c_ for c_ in reg.columns if 'verdict' in c_.lower() or 'feas' in c_.lower()]; print(vc); 
for c_ in vc: print(reg[c_].value_counts().head(8))
for f,v in [('singles','6061dbb8-4086-46c6-907c-9f4ac39e074e'),('pairs','eda089ea-2ebd-41a8-bcdf-a1c467201259'),('triples','3f2be3fb-d4d2-4c02-b377-fcf6982e3b77')]:
    d=pd.read_csv(host.artifact_path(v)); print(f,d.shape,d.columns.tolist()[:12])
from PIL import Image; print('PIL ok')