mkdir -p red; cd lib; python -c "
from pyproj import Geod; g=Geod(ellps='WGS84'); print(g.inv(114.1426,-34.8903,101.369,-25.732)[0]%360, g.inv(114.1426,-34.8903,101.369,-25.732)[2]/1e3)"
/usr/bin/time -l python reduce_kh.py run-j-waypoints 1 ../red/run-j-waypoints_1.npz 2>&1 | egrep "seed-|maximum resident|real|Error|error" 