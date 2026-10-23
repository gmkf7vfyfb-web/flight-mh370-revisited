cd "audit/repo/Claude Science Project Sep 29/results/hydroacoustics-audit/scripts"; python3 - <<'EOF'
s=open('paths.py').read()
s=s.replace('shp = (nz, m["nlat"], m["nlon"])','shp = (m["nlat"], m["nlon"], nz)   # file layout [lat][lon][depth] (checked against the shared export)')
s=s.replace('num = np.zeros(a.shape[0]); den = np.zeros(a.shape[0])','num = np.zeros(a.shape[2]); den = np.zeros(a.shape[2])')
s=s.replace('v = a[:, i, j].astype(float)','v = a[i, j, :].astype(float)')
open('paths.py','w').write(s)
EOF
grep -n "shp =\|a.shape\|a\[i, j" paths.py