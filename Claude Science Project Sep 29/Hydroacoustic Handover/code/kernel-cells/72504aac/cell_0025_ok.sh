X=/Users/pete/Downloads/mh370-exchange
head -30 $X/composer/run-j-views-v3.2/products-v3.csv | cut -c1-300; python -c "
import json;d=json.load(open('$X/composer/run-j-views-v3.2/views-v3-run-j.json'));print(list(d.keys())[:30]); 
for k in ('products','treatments','labels','product_labels','treatment_labels'):
  if k in d: print(k, json.dumps(d[k])[:1500])
"
python -c "
import numpy as np; z=np.load('$X/composer/run-j-views/arc-line.npz'); print({k:z[k].shape for k in z.files}); print({k:z[k][:3] for k in z.files})"
sed -n 60,100p "repo/Claude Science Project Sep 29/results/composer-views-run-j/views_common.py"