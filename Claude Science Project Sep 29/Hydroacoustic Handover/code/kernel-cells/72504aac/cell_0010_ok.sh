X=/Users/pete/Downloads/mh370-exchange
for d in $X/composer/run-j-views-v3*; do echo "== $d"; ls $d | grep -v -E "png|pdf"; done
python - <<'E'
import numpy as np,glob
for f in sorted(glob.glob('/Users/pete/Downloads/mh370-exchange/composer/run-j-views-v3*/maps*.npz')):
    z=np.load(f,allow_pickle=True); print(f, len(z.files)); print([ (k,z[k].shape) for k in z.files][:40])
E
echo == core; ls $X/core/run-j/run-j-waypoints | head; ls $X/core/run-j/run-j-waypoints/* | head -30