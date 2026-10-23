cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-weak-signal
ls; ls templates | head; cat templates/*.json 2>/dev/null | head -c 1500; find . -name "template_build.json" | head -2
python - <<'EOF'
import numpy as np, glob
f=glob.glob('templates/*.npz')[0]; z=np.load(f); print(f, {k:(z[k].shape,str(z[k].dtype)) for k in z.files})
print('fs',float(z['fs']) if 'fs' in z.files else None, 'T', float(z['T']) if 'T' in z.files else None)
h=z['h_2200.0']; print(h.shape, np.abs(h).max(), np.argmax(np.abs(h)))
EOF