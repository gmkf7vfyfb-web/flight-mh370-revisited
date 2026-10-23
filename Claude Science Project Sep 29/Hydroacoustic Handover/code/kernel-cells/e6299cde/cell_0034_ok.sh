cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/null
python - <<'EOF'
import numpy as np
for l in ('3376','3274','3250'):
    z=np.load(f'null_{l}.npz'); print(l, z['n_files'], {k:(z[k].shape[0], np.round(np.quantile(z[k],[0.5,0.7,0.9,0.95,0.99]),3).tolist()) for k in z.keys() if k!='n_files' and not k.startswith('panel_H08S')})
EOF