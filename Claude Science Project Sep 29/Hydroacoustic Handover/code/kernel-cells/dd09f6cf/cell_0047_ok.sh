sed -i '' 's/MULTIOBS_GLO_PHY_MY_015_004/MULTIOBS_GLO_PHY_MYNRT_015_003 (cmems_obs-mob_glo_phy-cur_my_0.25deg_P1D-m)/' lib/surface_drift.py
cp "$(python -c "print('x')" >/dev/null; echo)" /dev/null 2>/dev/null
python - <<'E'
import numpy as np
GLAT0,GLON0,GST,GNX=-46.0,78.0,0.25,136
c=[]
for la in np.arange(-27.0,-24.0,0.25):
    for lo in np.arange(99.5,102.5,0.25):
        c.append(int(np.floor((la+0.01-GLAT0)/GST))*GNX+int(np.floor((lo+0.01-GLON0)/GST)))
np.save('ocean/test_cells.npy',np.array(c))
E
echo ok