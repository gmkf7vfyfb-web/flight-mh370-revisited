E=/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run-c; grep -n -i -B2 -A12 "tau" $E/next-c-free/README.md | head -80; ls -la $E/next-c-free/seed-1/; python - <<'EOF'
import numpy as np
z=np.load("/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run-c/next-c-free/seed-1/tau90_v1.npz", allow_pickle=False)
for k in z.files:
    a=z[k]; print(k, a.dtype, a.shape, (a[:5] if a.ndim==1 and a.size>0 else a if a.size<10 else ''))
EOF